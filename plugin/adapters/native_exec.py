import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


SUMMARY_BYTES = 8192
UNKNOWN = {'executed': None, 'failed': None, 'skipped': None}
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')


@dataclass(frozen=True)
class XmlReport:
    path: Path
    runner: str


class Diagnostics:
    def __init__(self):
        self.lines = []
        self.omitted = False

    def add(self, value):
        line = ANSI.sub('', str(value)).strip()
        if not line:
            return
        if len(line) > 400:
            line = line[:197] + ' ... ' + line[-198:]
            self.omitted = True
        if line in self.lines:
            return
        self.lines.append(line)
        if len(self.lines) > 6:
            self.lines.pop(3)
            self.omitted = True

    def extend(self, lines):
        for line in lines:
            self.add(line)


def summary_diagnostics(native, logs):
    lines = list(dict.fromkeys(native.lines + logs.lines))
    omitted = native.omitted or logs.omitted or len(lines) > 6
    if len(lines) > 6 and native.lines and logs.lines:
        protected = {lines.index(native.lines[0]), lines.index(native.lines[-1]),
                     lines.index(logs.lines[0]), lines.index(logs.lines[-1])}
        for index in range(len(lines)):
            if len(protected) == 6:
                break
            protected.add(index)
        lines = [line for index, line in enumerate(lines) if index in protected]
    return lines, omitted


@dataclass(frozen=True)
class Invocation:
    tool: str
    argv: list
    cwd: Path
    operation: str
    target: dict
    reports: list
    env: dict
    timeout_seconds: float


class EvidenceError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2) + '\n')
    temporary.replace(path)


def load_request(tool, path):
    value = json.loads(path.read_text())
    allowed = {'argv', 'cwd', 'operation', 'target', 'reports', 'env', 'timeout_seconds'}
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError('request must contain only documented invocation fields')
    argv, target, env = value.get('argv'), value.get('target'), value.get('env', {})
    reports = value.get('reports', [])
    if (not isinstance(argv, list) or not argv or any(not isinstance(a, str) or '\0' in a for a in argv)
            or not isinstance(target, dict) or not target
            or not isinstance(env, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                                or '=' in k or '\0' in k + v for k, v in env.items())
            or not isinstance(reports, list) or any(not isinstance(p, str) for p in reports)):
        raise ValueError('expected argv array, target object, report paths and string environment overrides')
    cwd = Path(value['cwd'])
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError('cwd must be an absolute existing consumer directory')
    operation = value.get('operation')
    timeout = value.get('timeout_seconds', 900)
    if operation not in {'build', 'test'} or type(timeout) not in {int, float} or not 0 < timeout <= 86400:
        raise ValueError('operation must be build or test; timeout_seconds must be in (0, 86400]')
    return Invocation(tool, argv, cwd.resolve(), operation, target, reports, env, timeout)


def absolute(invocation, value):
    path = Path(value)
    return path if path.is_absolute() else invocation.cwd / path


def option(argv, name, default=None):
    values = []
    for index, argument in enumerate(argv):
        if argument == name:
            if index + 1 == len(argv):
                raise EvidenceError('prerequisite', 'missing value for ' + name)
            values.append(argv[index + 1])
        elif argument.startswith(name + '='):
            values.append(argument[len(name) + 1:])
    if len(values) > 1:
        raise EvidenceError('prerequisite', 'one target per attempt; repeated ' + name)
    return values[0] if values else default


def xcode_actions(command):
    actions, index = [], 1
    non_build_modes = {
        '-usage', '-help', '--help', '-h', '-license', '-checkFirstLaunchStatus', '-runFirstLaunch',
        '-downloadAllPlatforms', '-prepareDeviceSupport', '-downloadPlatform', '-importPlatform',
        '-downloadComponent', '-importComponent', '-deleteComponent', '-showComponent', '-showsdks',
        '-showdestinations', '-showTestPlans', '-showBuildSettings', '-showBuildSettingsForIndex',
        '-list', '-convert-project', '-find-executable', '-find-library', '-version', '-exportArchive',
        '-exportNotarizedApp', '-exportLocalizations', '-importLocalizations',
        '-resolvePackageDependencies', '-create-xcframework', '-enumerate-tests', '-dry-run'}
    value_options = {
        '-project', '-workspace', '-scheme', '-target', '-configuration', '-xcconfig', '-arch',
        '-sdk', '-toolchain', '-destination', '-destination-timeout', '-jobs',
        '-maximum-concurrent-test-device-destinations', '-maximum-concurrent-test-simulator-destinations',
        '-parallel-testing-enabled', '-parallel-testing-worker-count', '-maximum-parallel-testing-workers',
        '-convert-project', '-find-executable', '-find-library', '-enableAddressSanitizer',
        '-enableThreadSanitizer', '-enableUndefinedBehaviorSanitizer', '-resultBundlePath',
        '-resultStreamPath', '-resultBundleVersion', '-clonedSourcePackagesDirPath', '-derivedDataPath',
        '-archivePath', '-exportOptionsPlist', '-enableCodeCoverage', '-enableCodesizeProfile',
        '-codesizeProfileOutputDir', '-exportPath', '-importPath', '-localizationPath', '-exportLanguage',
        '-defaultLanguage', '-xctestrun', '-testProductsPath', '-enablePerformanceTestsDiagnostics',
        '-testPlan', '-only-testing', '-skip-testing', '-test-timeouts-enabled',
        '-default-test-execution-time-allowance', '-maximum-test-execution-time-allowance',
        '-test-iterations', '-test-repetition-relaunch-enabled', '-only-test-configuration',
        '-skip-test-configuration', '-collect-test-diagnostics', '-testLanguage', '-testRegion',
        '-test-enumeration-style', '-test-enumeration-format', '-test-enumeration-output-path',
        '-packageCachePath', '-packageAuthorizationProvider', '-defaultPackageRegistryURL',
        '-packageDependencySCMToRegistryTransformation', '-packageFingerprintPolicy',
        '-packageSigningEntityPolicy', '-authenticationKeyPath', '-authenticationKeyID',
        '-authenticationKeyIssuerID', '-scmProvider', '-platform', '-osVersion', '-modelCode',
        '-architecture', '-downloadPlatform', '-importPlatform', '-downloadComponent',
        '-importComponent', '-deleteComponent', '-showComponent'}
    names = {'build', 'build-for-testing', 'test', 'test-without-building', 'clean',
             'analyze', 'archive', 'install', 'installhdrs', 'installsrc'}
    while index < len(command):
        token = command[index]
        if token in non_build_modes:
            raise EvidenceError('prerequisite', 'Xcode command selects a non-build operation: ' + token)
        if token.startswith('-'):
            index += 2 if token in value_options else 1
            continue
        if token in names:
            actions.append(token)
        index += 1
    return actions or ['build']


def validate_target(invocation):
    argv, target = invocation.argv, invocation.target
    command = argv[1:] if Path(argv[0]).name == 'xcrun' else argv
    expected = {'xcodebuild': 'xcodebuild', 'swiftpm': 'swift', 'gradle': 'gradlew'}[invocation.tool]
    if not command or Path(command[0]).name != expected:
        raise EvidenceError('prerequisite', 'expected explicit ' + expected + ' invocation')
    if invocation.tool == 'xcodebuild':
        for field, flag in [('scheme', '-scheme'), ('destination', '-destination')]:
            if not target.get(field) or option(command, flag) != target[field]:
                raise EvidenceError('prerequisite', 'unresolved or conflicting Xcode ' + field)
        containers = [option(command, name) for name in ['-project', '-workspace']]
        if sum(p is not None for p in containers) != 1:
            raise EvidenceError('prerequisite', 'resolve one Xcode project or workspace')
        actions = xcode_actions(command)
        if (invocation.operation == 'test' and not any(a in {'test', 'test-without-building'} for a in actions)
                or invocation.operation == 'build' and any(a not in {'build', 'build-for-testing', 'archive'} for a in actions)):
            raise EvidenceError('prerequisite', 'operation must match Xcode action')
        report = option(command, '-resultBundlePath')
        if invocation.operation == 'test' and not re.search(r'(?:^|,)id=[^,]+', target['destination']):
            raise EvidenceError('prerequisite', 'test destination needs explicit device id')
    elif invocation.tool == 'swiftpm':
        forwarded = False
        for argument in command[1:]:
            if forwarded:
                forwarded = False
            elif argument in {'-Xcc', '-Xcxx', '-Xswiftc', '-Xlinker', '-Xmanifest'}:
                forwarded = True
            elif argument.startswith('-C') or argument == '--chdir' or argument.startswith('--chdir='):
                raise EvidenceError('prerequisite', 'Swift directory redirection is unsupported; set cwd and target.package explicitly')
        if (not target.get('package') or absolute(invocation, option(command, '--package-path', '.')).resolve()
                != absolute(invocation, target['package']).resolve()):
            raise EvidenceError('prerequisite', 'unresolved or conflicting Swift package')
        if len(command) < 2 or invocation.operation != command[1]:
            raise EvidenceError('prerequisite', 'operation must match SwiftPM command')
        report = option(command, '--xunit-output')
    else:
        if any(a.startswith('-p') or a == '--project-dir' or a.startswith('--project-dir=') for a in command[1:]):
            raise EvidenceError('prerequisite', 'Gradle project directory redirection is unsupported; use the consumer cwd')
        task = target.get('task')
        if not isinstance(task, str) or not task.startswith(':') or task not in command[1:]:
            raise EvidenceError('prerequisite', 'resolve explicit fully qualified Gradle task')
        wrapper = absolute(invocation, command[0]).resolve()
        if wrapper != (invocation.cwd / 'gradlew').resolve():
            raise EvidenceError('prerequisite', 'use the consumer root Gradle wrapper')
        report = target.get('report_dir')
    if invocation.operation == 'test':
        if not report or invocation.reports != [report]:
            raise EvidenceError('prerequisite', 'one explicit native report root must match the command or Gradle task mapping')
    if 'suite_pattern' in target:
        try:
            re.compile(target['suite_pattern'])
        except (re.error, TypeError) as error:
            raise EvidenceError('prerequisite', 'invalid suite_pattern: ' + str(error)) from error


def report_sources(invocation):
    sources = [absolute(invocation, p) for p in invocation.reports]
    if invocation.tool == 'swiftpm' and sources:
        sources.append(sources[0].with_name(sources[0].stem + '-swift-testing' + sources[0].suffix))
    return sources


def execute(invocation, attempt, environment):
    status, code, diagnostics = 'not_started', None, []
    process = None
    def stop(signum, frame):
        raise KeyboardInterrupt

    previous = {s: signal.signal(s, stop) for s in [signal.SIGINT, signal.SIGTERM]}
    try:
        with (attempt / 'stdout.log').open('wb') as stdout, (attempt / 'stderr.log').open('wb') as stderr:
            try:
                process = subprocess.Popen(invocation.argv, cwd=invocation.cwd, env=environment,
                                           stdout=stdout, stderr=stderr, start_new_session=True)
                code = process.wait(timeout=invocation.timeout_seconds)
                status = 'signalled' if code < 0 else 'exited'
            except FileNotFoundError as error:
                status, diagnostics = 'unavailable', [str(error)]
            except PermissionError as error:
                status, diagnostics = 'denied', [str(error)]
            except OSError as error:
                status, diagnostics = 'unavailable', [str(error)]
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
                status = 'interrupted' if isinstance(error, KeyboardInterrupt) else 'timed_out'
                diagnostics = ['command ' + status]
                if process is not None:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        code = process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        code = None
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    code = process.wait()
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)
    return status, code, diagnostics


def log_lines(attempt):
    for name in ['stdout.log', 'stderr.log']:
        with (attempt / name).open('rb') as stream:
            while chunk := stream.readline(65536):
                first, last = chunk, chunk
                clipped = not chunk.endswith(b'\n') and len(chunk) == 65536
                if clipped:
                    while last and not last.endswith(b'\n'):
                        following = stream.readline(65536)
                        if not following:
                            break
                        last = following
                    chunk = first[:32768] + b' ... ' + last[-32768:]
                yield ANSI.sub('', chunk.decode('utf-8', errors='replace')).strip(), clipped


def log_diagnostics(attempt, fallback=False):
    errors, tail = Diagnostics(), Diagnostics()
    block = None
    for line, clipped in log_lines(attempt):
        errors.omitted |= clipped
        if not line:
            continue
        if block is not None and line.startswith('* '):
            errors.add('\n'.join(block.lines))
            errors.omitted |= block.omitted
            block = None
        if line == '* What went wrong:':
            block = Diagnostics()
        if block is not None:
            block.add(line)
            continue
        if (re.search(r'\b0 failures?\b', line) and not re.search(r'error:|^e: ', line)
                or line.startswith('|') or re.search(r'^(?:BUILD FAILED|FAILURE: Build failed)', line)
                or re.search(r'^\S+ > .* FAILED$', line)):
            continue
        tail.add(line)
        if re.search(r'error:|fatal|exception|failed|failure|^e:\s', line, re.I):
            errors.add(line)
    if block is not None:
        errors.add('\n'.join(block.lines))
        errors.omitted |= block.omitted
    if not errors.lines and fallback:
        errors.extend(tail.lines[-2:])
        errors.omitted |= tail.omitted
    return errors


def matching_log_lines(attempt, pattern):
    for line, _ in log_lines(attempt):
        match = re.search(pattern, line)
        if match:
            yield match


def xctest_terminals(attempt, identities):
    states, unexpected = {}, False
    for match in matching_log_lines(attempt, r"^Test Case '(.+)' (passed|failed|skipped) \("):
        name, state = match.groups()
        parts = re.fullmatch(r'-\[(.+) (.+)\]', name)
        identity = '.'.join(parts.groups()) if parts else name
        if identity not in identities:
            unexpected = True
        else:
            states[identity] = 'ambiguous' if identity in states else state
    return states, unexpected


def tree_receipt(path):
    paths = sorted(path.rglob('*')) if path.is_dir() else [path]
    result = {}
    for item in paths:
        if item.is_symlink():
            raise EvidenceError('unreadable', 'native report contains symlink: ' + str(item))
        if item.is_file():
            if not item.stat().st_mode & 0o444:
                raise EvidenceError('unreadable', 'native report is unreadable: ' + str(item))
            digest = hashlib.sha256()
            with item.open('rb') as stream:
                for chunk in iter(lambda: stream.read(65536), b''):
                    digest.update(chunk)
            name = str(item.relative_to(path)) if path.is_dir() else path.name
            result[name] = {'sha256': digest.hexdigest(), 'bytes': item.stat().st_size}
    return result


def retain_reports(sources, stale, attempt):
    records, retained = [], []
    for index, source in enumerate(sources):
        row = {'source': str(source), 'retained': None, 'status': 'missing', 'files': {}}
        records.append(row)
        if not source.exists() and not source.is_symlink():
            continue
        try:
            if source.is_symlink():
                raise EvidenceError('unreadable', 'native report root is a symlink')
            before = tree_receipt(source)
            destination = attempt / 'reports' / str(index) / source.name
            destination.parent.mkdir(parents=True)
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            row['retained'] = str(destination.relative_to(attempt))
            row['files'] = tree_receipt(destination)
            if before != row['files'] or before != tree_receipt(source):
                raise EvidenceError('incomplete', 'native report changed during retention')
            row['status'] = 'stale' if source in stale else 'retained'
            retained.append((source, destination))
        except (OSError, EvidenceError) as error:
            row['status'] = error.status if isinstance(error, EvidenceError) else 'unreadable'
            row['diagnostic'] = str(error)
    write_json(attempt / 'reports.json', records)
    return records, retained


def xml_counts(reports, pattern, attempt, diagnostics):
    counts, identities, xctest = {'executed': 0, 'failed': 0, 'skipped': 0}, set(), {}
    if sum(report.path.stat().st_size for report in reports) > 32 * 1024 * 1024:
        raise EvidenceError('unsupported', 'XML report set exceeds 32 MiB interpretation limit')
    for report in reports:
        path = report.path
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError) as error:
            raise EvidenceError('unreadable', 'unreadable native XML: ' + str(error)) from error
        if root.tag not in {'testsuite', 'testsuites'}:
            raise EvidenceError('unsupported', 'unsupported XML report root ' + root.tag)
        parents = {child: parent for parent in root.iter() for child in parent}
        for case in root.iter('testcase'):
            parent = parents[case]
            if parent.tag != 'testsuite' or parent.find('testsuite') is not None:
                raise EvidenceError('unsupported', 'testcase must belong to a leaf testsuite')
        for issue in [*root.iter('failure'), *root.iter('error')]:
            if parents[issue].tag != 'testcase':
                raise EvidenceError('incomplete', 'suite-level native failure: ' + (issue.get('message') or issue.text or 'unknown'))
        for node in root.iter():
            if node.tag not in {'testsuite', 'testsuites'}:
                continue
            cases = list(node.iter('testcase'))
            skipped = sum(case.find('skipped') is not None for case in cases)
            declared = {'tests': len(cases) - (skipped if report.runner == 'swift_testing' else 0),
                        'failures': sum(len(case.findall('failure')) if report.runner == 'swift_testing'
                                        else case.find('failure') is not None for case in cases),
                        'errors': sum(case.find('error') is not None for case in cases),
                        'skipped': skipped}
            for field, actual in declared.items():
                if field in node.attrib and int(node.attrib[field]) != actual:
                    raise EvidenceError('incomplete', 'native XML declared ' + field + ' differs from cases')
        for suite in root.iter('testsuite'):
            cases = list(suite.findall('testcase'))
            if list(suite.findall('testsuite')):
                if cases:
                    raise EvidenceError('unsupported', 'mixed suite nesting')
                continue
            for case in cases:
                identity = case.get('classname', suite.get('name', '')) + '.' + case.get('name', '')
                if identity in identities:
                    raise EvidenceError('incomplete', 'overlapping or retried native test identity: ' + identity)
                identities.add(identity)
                if pattern and not re.search(pattern, identity):
                    raise EvidenceError('target_mismatch', 'unexpected native test identity: ' + identity)
                failures = list(case.findall('failure')) + list(case.findall('error'))
                skipped = case.find('skipped') is not None
                if (skipped and failures or case.find('flakyFailure') is not None
                        or case.find('rerunFailure') is not None):
                    raise EvidenceError('incomplete', 'conflicting or retried native test result: ' + identity)
                counts['skipped' if skipped else 'executed'] += 1
                if report.runner == 'xctest':
                    xctest[identity] = (bool(failures), skipped, 'skipped' in suite.attrib)
                if failures:
                    counts['failed'] += 1
                    for failure in failures:
                        diagnostics.add(identity + ': ' + (failure.get('message') or failure.text or 'test failed'))
    if xctest:
        terminals, uncertain = xctest_terminals(attempt, xctest)
        for identity, (failed, skipped, skip_declared) in xctest.items():
            terminal = terminals.get(identity)
            if terminal is not None and (terminal == 'ambiguous' or (terminal == 'failed') != failed
                                         or skipped and terminal != 'skipped'
                                         or skip_declared and (terminal == 'skipped') != skipped):
                uncertain = True
            if not skip_declared and not skipped and not failed:
                if terminal not in {'passed', 'failed', 'skipped'}:
                    uncertain = True
                elif terminal == 'skipped' and not failed:
                    counts['executed'] -= 1
                    counts['skipped'] += 1
        if uncertain:
            counts.update(executed=None, skipped=None)
            diagnostics.add('XCTest skip counts require matching terminal case results; use swift test --parallel --verbose')
    return counts


def interpret_xcode(invocation, retained, attempt, environment, diagnostics):
    argv = ['xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--schema-version', '0.4.0',
            '--path', str(retained[0][1]), '--compact']
    record = {'argv': argv, 'cwd': str(invocation.cwd), 'exit_code': None}
    try:
        result = subprocess.run(argv, cwd=invocation.cwd, env=environment, capture_output=True,
                                timeout=invocation.timeout_seconds)
        record['exit_code'] = result.returncode
        (attempt / 'inspection.stdout').write_bytes(result.stdout)
        (attempt / 'inspection.stderr').write_bytes(result.stderr)
        if result.returncode:
            raise EvidenceError('unsupported', 'xcresulttool could not interpret retained bundle')
        value = json.loads(result.stdout)
        if not isinstance(value, dict):
            raise EvidenceError('unsupported', 'xcresult summary must be an object')
        fields = [value.get(k) for k in ['passedTests', 'failedTests', 'skippedTests', 'expectedFailures', 'totalTestCount']]
        if any(type(n) is not int or n < 0 for n in fields) or sum(fields[:4]) != fields[4]:
            raise EvidenceError('unsupported', 'unsupported or inconsistent xcresult summary counts')
        expected = re.search(r'(?:^|,)id=([^,]+)', invocation.target['destination']).group(1)
        devices = {row['device']['deviceId'] for row in value['devicesAndConfigurations']}
        if devices != {expected}:
            raise EvidenceError('target_mismatch', 'xcresult destination differs from requested device')
        failures = value.get('testFailures', [])
        if (not isinstance(failures, list) or any(not isinstance(row, dict)
                or not isinstance(row.get('failureText'), str)
                or not isinstance(row.get('testName'), str) for row in failures)):
            raise EvidenceError('unsupported', 'unsupported xcresult failure details')
        if not isinstance(value.get('title'), str) or value.get('result') not in {'Passed', 'Failed', 'Skipped', 'Expected Failure'}:
            raise EvidenceError('unsupported', 'xcresult scheme or result is unavailable')
        if value['title'] != 'Test - ' + invocation.target['scheme']:
            raise EvidenceError('target_mismatch', 'xcresult scheme differs from requested scheme')
        if (value['result'] == 'Failed' and fields[1] == 0
                or value['result'] == 'Skipped' and fields[0] + fields[1] + fields[3] > 0):
            raise EvidenceError('incomplete', 'xcresult outcome contradicts test counts')
        diagnostics.extend(row['testName'] + ': ' + row['failureText'] for row in failures)
        return {'executed': fields[0] + fields[1] + fields[3], 'failed': fields[1], 'skipped': fields[2]}
    except subprocess.TimeoutExpired as error:
        (attempt / 'inspection.stdout').write_bytes(error.output or b'')
        (attempt / 'inspection.stderr').write_bytes(error.stderr or b'')
        raise EvidenceError('unsupported', 'xcresult summary inspection timed out') from error
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise EvidenceError('unsupported', 'xcresult summary unavailable or unsupported: ' + str(error)) from error
    finally:
        write_json(attempt / 'inspection.json', record)


def interpret(invocation, records, retained, attempt, environment, diagnostics):
    if invocation.operation == 'build':
        return 'build_only', dict(UNKNOWN)
    for row in records:
        if row['status'] not in {'retained', 'missing'}:
            raise EvidenceError(row['status'], row.get('diagnostic', 'native report ' + row['status']))
    if not retained:
        raise EvidenceError('missing', 'native report missing for this invocation')
    if invocation.tool == 'xcodebuild':
        counts = interpret_xcode(invocation, retained, attempt, environment, diagnostics)
    else:
        if invocation.tool == 'gradle':
            roles = {source: 'gradle' for source, _ in retained}
            task = re.escape(invocation.target['task'])
            matches = [m.group(1) or '' for m in matching_log_lines(attempt, r'^> Task ' + task + r'(?: (.*))?$')]
            if not matches:
                raise EvidenceError('incomplete', 'Gradle task execution not observed for report mapping')
            if any(re.search(r'UP-TO-DATE|FROM-CACHE|SKIPPED|NO-SOURCE', state) for state in matches):
                raise EvidenceError('not_executed', 'Gradle requested task did not execute fresh tests')
        else:
            xctest_enabled = '--disable-xctest' not in invocation.argv
            swift_enabled = '--disable-swift-testing' not in invocation.argv
            if not xctest_enabled and not swift_enabled:
                raise EvidenceError('incomplete', 'both Swift test runners are disabled')
            primary = records[0]['status'] == 'retained'
            swift_testing = records[1 if xctest_enabled else 0]['status'] == 'retained'
            if xctest_enabled and not primary:
                totals = [m.group(1) for m in matching_log_lines(attempt, r'Executed (\d+) tests?, with')]
                if not totals or int(totals[-1]) != 0:
                    raise EvidenceError('incomplete', 'enabled XCTest report missing without observed zero tests')
            if swift_enabled and not swift_testing:
                totals = [m.group(1) for m in matching_log_lines(attempt, r'Test run with (\d+) tests?')]
                if not totals or int(totals[-1]) != 0:
                    raise EvidenceError('incomplete', 'enabled Swift Testing report missing without observed zero tests')
            sources = report_sources(invocation)
            roles = {sources[0]: 'xctest' if xctest_enabled else 'swift_testing'}
            if xctest_enabled and swift_enabled:
                roles[sources[1]] = 'swift_testing'
        reports = [XmlReport(file, roles[source]) for source, path in retained if source in roles
                   for file in (sorted(path.rglob('*.xml')) if path.is_dir() else [path])]
        if not reports:
            raise EvidenceError('missing', 'native XML report set is empty')
        counts = xml_counts(reports, invocation.target.get('suite_pattern'), attempt, diagnostics)
    return ('incomplete' if counts['executed'] is None else 'zero_tests' if counts['executed'] == 0 else 'complete'), counts


def bounded_summary(summary):
    for field in ['argv', 'cwd', 'target']:
        if len(json.dumps(summary[field]).encode()) > 1600:
            summary[field] = {'omitted': True, 'artifact': 'invocation.json'}
            summary['details_omitted'] = True
    encoded = json.dumps(summary, ensure_ascii=True, separators=(',', ':')) + '\n'
    while len(encoded.encode()) > SUMMARY_BYTES and summary['diagnostics']:
        lines = summary['diagnostics']
        index = max(range(len(lines)), key=lambda i: len(json.dumps(lines[i])))
        if len(lines[index]) > 80:
            size = len(lines[index]) // 4
            lines[index] = lines[index][:size] + ' ... ' + lines[index][-size:]
        else:
            lines.pop(len(lines) // 2)
        summary['details_omitted'] = True
        encoded = json.dumps(summary, ensure_ascii=True, separators=(',', ':')) + '\n'
    if len(encoded.encode()) > SUMMARY_BYTES:
        for field in ['argv', 'cwd', 'target']:
            summary[field] = {'omitted': True, 'artifact': 'invocation.json'}
        summary['details_omitted'] = True
        encoded = json.dumps(summary, ensure_ascii=True, separators=(',', ':')) + '\n'
    if len(encoded.encode()) > SUMMARY_BYTES:
        raise ValueError('evidence path exceeds summary capacity')
    return encoded


def run(invocation, store):
    if not store.is_absolute():
        raise ValueError('store must be absolute and outside consumer and installed plugin')
    store = store.resolve()
    plugin = Path(__file__).resolve().parents[1]
    if store.is_relative_to(invocation.cwd) or store.is_relative_to(plugin):
        raise ValueError('store must be outside consumer and installed plugin')
    store.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix='attempt-', dir=store))
    record = {'schema_version': 1, 'tool': invocation.tool, 'argv': invocation.argv,
              'cwd': str(invocation.cwd), 'operation': invocation.operation, 'target': invocation.target,
              'reports': invocation.reports, 'env': invocation.env, 'environment': 'inherited_with_explicit_overrides',
              'timeout_seconds': invocation.timeout_seconds, 'started_at': datetime.now(timezone.utc).isoformat()}
    write_json(attempt / 'invocation.json', record)
    for name in ['stdout.log', 'stderr.log']:
        (attempt / name).touch()
    counts, diagnostics, interpretation = dict(UNKNOWN), Diagnostics(), 'prerequisite'
    status, code = 'not_started', None
    environment = dict(os.environ, **invocation.env)
    try:
        validate_target(invocation)
        sources = report_sources(invocation)
        stale = {p for p in sources if p.exists() or p.is_symlink()}
        if stale:
            retain_reports(sources, stale, attempt)
            raise EvidenceError('stale', 'native report roots must be absent before execution; prepare a fresh output in the consumer recipe')
        status, code, process_diagnostics = execute(invocation, attempt, environment)
        diagnostics.extend(process_diagnostics)
        records, retained = retain_reports(sources, stale, attempt)
        interpretation, counts = interpret(invocation, records, retained, attempt, environment, diagnostics)
        if invocation.operation == 'build' and status != 'exited':
            interpretation = 'incomplete'
    except (EvidenceError, OSError, ValueError) as error:
        interpretation = error.status if isinstance(error, EvidenceError) else 'unreadable'
        diagnostics.add(str(error))
    if not (attempt / 'reports.json').exists():
        write_json(attempt / 'reports.json', [])
    if status in {'exited', 'signalled'} and code != 0 or counts['failed'] is not None and counts['failed'] > 0:
        outcome = 'failed'
    elif status == 'exited' and code == 0 and interpretation in {'build_only', 'complete'}:
        outcome = 'passed'
    else:
        outcome = 'incomplete'
    diagnostic_lines, omitted = summary_diagnostics(diagnostics, log_diagnostics(attempt, fallback=outcome != 'passed'))
    summary = {'schema_version': 1, 'attempt': str(attempt), 'tool': invocation.tool,
               'operation': invocation.operation, 'argv': invocation.argv, 'cwd': str(invocation.cwd),
               'target': invocation.target, 'command_status': status, 'exit_code': code,
               'interpretation_status': interpretation, 'outcome': outcome, 'counts': counts,
               'target_verification': ('native_device' if invocation.tool == 'xcodebuild'
                                       else 'invocation_and_fresh_reports') if interpretation == 'complete' else 'unverified',
               'diagnostics': diagnostic_lines, 'details_omitted': omitted,
               'artifacts': {'invocation': 'invocation.json', 'stdout': 'stdout.log',
                             'stderr': 'stderr.log', 'reports': 'reports.json'}}
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    write_json(attempt / 'invocation.json', record)
    output = bounded_summary(summary)
    write_json(attempt / 'summary.json', summary)
    sys.stdout.write(output)
    return {'passed': 0, 'failed': 1, 'incomplete': 2}[outcome]


def main():
    parser = argparse.ArgumentParser(description='Execute one consumer-selected native command and retain its evidence.')
    parser.add_argument('tool', choices=['xcodebuild', 'swiftpm', 'gradle'])
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--store', type=Path, required=True)
    arguments = parser.parse_args()
    try:
        return run(load_request(arguments.tool, arguments.request), arguments.store)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('native execution prerequisite: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
