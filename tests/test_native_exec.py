import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from test_host_adapters import InstalledFixture


ROOT = Path(__file__).resolve().parents[1]


class NativeExecution(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native helper ')
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name).resolve()
        self.consumer = self.area / 'consumer with spaces'
        self.consumer.mkdir()
        self.plugin = self.area / 'installed plugin'
        shutil.copytree(ROOT / 'plugin', self.plugin, ignore=shutil.ignore_patterns('__pycache__'))
        self.helper = self.plugin / 'adapters/native_exec.py'
        self.store = self.area / 'retained evidence'
        self.bin = self.area / 'tools'
        self.bin.mkdir()

    def tool(self, name, body):
        path = (self.consumer if name == 'gradlew' else self.bin) / name
        path.write_text('#!' + sys.executable + '\n' + body)
        path.chmod(0o755)
        return str(path)

    def request(self, tool='swiftpm', body='', operation='test'):
        executable = self.tool({'swiftpm': 'swift', 'xcodebuild': 'xcodebuild',
                                'gradle': 'gradlew'}[tool], body)
        report = self.consumer / {'swiftpm': 'result.xml', 'xcodebuild': 'result.xcresult',
                                  'gradle': 'app/build/test-results/testDebugUnitTest'}[tool]
        if tool == 'swiftpm':
            argv = [executable, operation, '--disable-swift-testing']
            target = {'package': str(self.consumer)}
            if operation == 'test':
                argv += ['--xunit-output', str(report)]
        elif tool == 'xcodebuild':
            argv = [executable, operation, '-project', 'My App.xcodeproj', '-scheme', 'My App',
                    '-destination', 'id=OWNED-SIM']
            target = {'scheme': 'My App', 'destination': 'id=OWNED-SIM'}
            if operation == 'test':
                argv += ['-resultBundlePath', str(report)]
        else:
            argv = [executable, ':app:testDebugUnitTest' if operation == 'test' else ':app:assembleDebug']
            target = {'task': argv[1], 'report_dir': str(report)}
        return {'argv': argv, 'cwd': str(self.consumer), 'operation': operation,
                'target': target, 'reports': [str(report)] if operation == 'test' else [],
                'env': {'PATH': str(self.bin) + os.pathsep + os.environ['PATH']},
                'timeout_seconds': 10}

    def run_helper(self, tool, request):
        path = self.area / 'request.json'
        path.write_text(json.dumps(request))
        return subprocess.run([sys.executable, str(self.helper), tool, '--request', str(path),
                               '--store', str(self.store)], cwd=self.consumer,
                              capture_output=True, timeout=20)

    def result(self, tool, request, exit_code=0):
        process = self.run_helper(tool, request)
        self.assertEqual(process.returncode, exit_code, process.stderr.decode(errors='replace'))
        self.assertLessEqual(len(process.stdout), 8192)
        value = json.loads(process.stdout)
        attempt = Path(value['attempt'])
        self.assertEqual(json.loads((attempt / 'summary.json').read_text()), value)
        return value, attempt

    @staticmethod
    def xml(tests=1, failed=False, skipped=False):
        cases = ''.join('<testcase classname="AppTests" name="test%d">%s</testcase>' %
                        (i, '<failure message="expected greeting" />' if failed and i == 0
                         else '<skipped />' if skipped and i == tests - 1 else '')
                        for i in range(tests))
        return '<testsuite name="AppTests" tests="%d" failures="%d" errors="0" skipped="%d">%s</testsuite>' % (
            tests, int(failed), int(skipped), cases)

    def xml_child(self, xml, tool='swiftpm'):
        relative = 'app/build/test-results/testDebugUnitTest/TEST-App.xml' if tool == 'gradle' else 'result.xml'
        return ("from pathlib import Path\np = Path(%r)\np.parent.mkdir(parents=True, exist_ok=True)\n"
                "p.write_text(%r)\n" % (relative, xml)
                + ("print('> Task :app:testDebugUnitTest')\n" if tool == 'gradle' else ''))

    def test_exact_argv_context_and_raw_bytes_survive_cleanup(self):
        body = ("import os,sys,json\nfrom pathlib import Path\n"
                "Path('observed.json').write_text(json.dumps({'argv':sys.argv,'cwd':os.getcwd(),'value':os.environ['TASK_VALUE']}))\n"
                "sys.stdout.buffer.write(b'raw \\xff\\x00\\r\\n')\nsys.stderr.buffer.write(b'err \\xfe\\n')\n")
        request = self.request(body=body, operation='build')
        request['argv'] += ['--scratch-path', 'build with spaces', 'literal $HOME `touch bad`']
        request['env']['TASK_VALUE'] = 'unchanged with spaces'
        result, attempt = self.result('swiftpm', request)
        self.assertEqual(json.loads((self.consumer / 'observed.json').read_text()),
                         {'argv': request['argv'], 'cwd': str(self.consumer), 'value': 'unchanged with spaces'})
        invocation = json.loads((attempt / 'invocation.json').read_text())
        self.assertEqual(invocation['argv'], request['argv'])
        self.assertEqual(invocation['cwd'], str(self.consumer))
        self.assertEqual(invocation['env'], request['env'])
        fixed = {key: value for key, value in invocation.items() if key not in {'started_at', 'finished_at'}}
        self.assertEqual(fixed, {'schema_version': 1, 'tool': 'swiftpm', 'argv': request['argv'],
                                'cwd': str(self.consumer), 'operation': 'build', 'target': request['target'],
                                'reports': [], 'env': request['env'], 'timeout_seconds': 10,
                                'environment': 'inherited_with_explicit_overrides'})
        self.assertEqual(result['command_status'], 'exited')
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['interpretation_status'], 'build_only')
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['counts'], {'executed': None, 'failed': None, 'skipped': None})
        shutil.rmtree(self.consumer)
        self.assertEqual((attempt / 'stdout.log').read_bytes(), b'raw \xff\x00\r\n')
        self.assertEqual((attempt / 'stderr.log').read_bytes(), b'err \xfe\n')
        self.assertEqual(result['artifacts'], {'invocation': 'invocation.json', 'stdout': 'stdout.log',
                                             'stderr': 'stderr.log', 'reports': 'reports.json'})

    def test_selected_xml_tests_pass_and_retain_original_report(self):
        for tool in ['swiftpm', 'gradle']:
            with self.subTest(tool=tool):
                request = self.request(tool, self.xml_child(self.xml(3, skipped=True), tool))
                request['argv'] += ['--filter', 'AppTests.test with spaces'] if tool == 'swiftpm' else ['--tests', 'AppTests.test with spaces']
                result, attempt = self.result(tool, request)
                self.assertEqual(result['counts'], {'executed': 2, 'failed': 0, 'skipped': 1})
                self.assertEqual(result['interpretation_status'], 'complete')
                self.assertEqual(result['target_verification'], 'invocation_and_fresh_reports')
                self.assertEqual(result['outcome'], 'passed')
                reports = json.loads((attempt / 'reports.json').read_text())
                self.assertEqual(reports[0]['source'], request['reports'][0])
                retained = attempt / reports[0]['retained']
                native = retained / 'TEST-App.xml' if tool == 'gradle' else retained
                self.assertEqual(native.read_text(), self.xml(3, skipped=True))
                shutil.rmtree(Path(request['reports'][0])) if tool == 'gradle' else Path(request['reports'][0]).unlink()
                self.assertEqual(native.read_text(), self.xml(3, skipped=True))

    def test_zero_tests_never_pass(self):
        result, _ = self.result('swiftpm', self.request(body=self.xml_child(self.xml(0))), 2)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(result['interpretation_status'], 'zero_tests')
        self.assertEqual(result['counts'], {'executed': 0, 'failed': 0, 'skipped': 0})

    def test_all_tools_build_without_claiming_tests(self):
        for tool in ['xcodebuild', 'swiftpm', 'gradle']:
            with self.subTest(tool=tool):
                result, _ = self.result(tool, self.request(tool, operation='build'))
                self.assertEqual(result['interpretation_status'], 'build_only')
                self.assertEqual(result['target_verification'], 'unverified')
                self.assertEqual(result['counts'], {'executed': None, 'failed': None, 'skipped': None})

    def test_nonzero_command_cannot_be_overridden_by_green_xml(self):
        request = self.request(body=self.xml_child(self.xml()) + 'raise SystemExit(7)\n')
        result, _ = self.result('swiftpm', request, 1)
        self.assertEqual(result['exit_code'], 7)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 0, 'skipped': 0})

    def test_inconsistent_aggregate_counts_and_retries_are_incomplete(self):
        for xml in ['<testsuites failures="1">' + self.xml() + '</testsuites>',
                    self.xml().replace('</testcase>', '<rerunFailure message="first attempt" /></testcase>')]:
            with self.subTest(xml=xml):
                result, _ = self.result('swiftpm', self.request(body=self.xml_child(xml)), 2)
                self.assertEqual(result['interpretation_status'], 'incomplete')
                self.assertEqual(result['outcome'], 'incomplete')
                (self.consumer / 'result.xml').unlink()

    def test_xml_failure_outside_leaf_case_cannot_disappear(self):
        for xml, status in [('<testsuites>' + self.xml() + '<testcase name="omitted"><failure message="lost failure"/></testcase></testsuites>', 'unsupported'),
                            (self.xml().replace('</testsuite>', '<error message="runner crashed"/></testsuite>'), 'incomplete')]:
            with self.subTest(xml=xml):
                result, _ = self.result('swiftpm', self.request(body=self.xml_child(xml)), 2)
                self.assertEqual(result['interpretation_status'], status)
                self.assertEqual(result['outcome'], 'incomplete')
                (self.consumer / 'result.xml').unlink()

    def test_swift_action_is_not_an_option_value(self):
        request = self.request(body="print('no tests selected')\n", operation='build')
        request['argv'] = [request['argv'][0], 'test', '--filter', 'build']
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['command_status'], 'not_started')
        self.assertEqual(result['interpretation_status'], 'prerequisite')

    def test_xcode_action_is_not_scheme_and_incremental_test_is_supported(self):
        request = self.request('xcodebuild', operation='build')
        request['argv'][1] = 'clean'
        request['argv'][request['argv'].index('-scheme') + 1] = 'build'
        request['target']['scheme'] = 'build'
        result, _ = self.result('xcodebuild', request, 2)
        self.assertEqual(result['command_status'], 'not_started')
        self.assertEqual(result['interpretation_status'], 'prerequisite')
        request = self.xcode()
        request['argv'][1] = 'test-without-building'
        result, _ = self.result('xcodebuild', request)
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 0, 'skipped': 1})
        self.assertEqual(result['argv'][1], 'test-without-building')
        request = self.request('xcodebuild', operation='build')
        request['argv'][1] = 'build-for-testing'
        result, _ = self.result('xcodebuild', request)
        self.assertEqual(result['interpretation_status'], 'build_only')

    def test_unsupported_xcresult_shapes_still_emit_retained_summary(self):
        for value in [[], {'passedTests': 1, 'failedTests': 0, 'skippedTests': 0,
                           'totalTestCount': 1, 'devicesAndConfigurations': [{'device': {'deviceId': 'OWNED-SIM'}}],
                           'testFailures': ['unknown failure shape']}]:
            with self.subTest(value=value):
                request = self.xcode()
                self.tool('xcrun', 'import json\nprint(json.dumps(%r))\n' % value)
                result, _ = self.result('xcodebuild', request, 2)
                self.assertEqual(result['interpretation_status'], 'unsupported')
                self.assertEqual(result['outcome'], 'incomplete')
                shutil.rmtree(self.consumer / 'result.xcresult')

    def test_symlink_report_is_retained_as_an_explicit_gap(self):
        body = "from pathlib import Path\nPath('private.xml').write_text(%r)\nPath('result.xml').symlink_to('private.xml')\n" % self.xml()
        result, attempt = self.result('swiftpm', self.request(body=body), 2)
        self.assertEqual(result['interpretation_status'], 'unreadable')
        reports = json.loads((attempt / 'reports.json').read_text())
        self.assertEqual(reports[0]['retained'], None)
        self.assertEqual(reports[0]['status'], 'unreadable')

    def test_all_skipped_never_pass(self):
        result, _ = self.result('swiftpm', self.request(body=self.xml_child(self.xml(1, skipped=True))), 2)
        self.assertEqual(result['interpretation_status'], 'zero_tests')
        self.assertEqual(result['counts'], {'executed': 0, 'failed': 0, 'skipped': 1})

    def test_test_failure_survives_green_process_exit(self):
        result, _ = self.result('swiftpm', self.request(body=self.xml_child(self.xml(2, failed=True))), 1)
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 1, 'skipped': 0})
        self.assertIn('AppTests.test0: expected greeting', result['diagnostics'])

    def test_compile_failure_keeps_diagnostic_and_unknown_counts(self):
        request = self.request(body="import sys\nprint('File.swift:4: error: missing actor isolation', file=sys.stderr)\nsys.exit(65)\n")
        result, _ = self.result('swiftpm', request, 1)
        self.assertEqual(result['command_status'], 'exited')
        self.assertEqual(result['exit_code'], 65)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['interpretation_status'], 'missing')
        self.assertEqual(result['counts'], {'executed': None, 'failed': None, 'skipped': None})
        self.assertIn('File.swift:4: error: missing actor isolation', result['diagnostics'])

    def test_missing_malformed_and_unsupported_reports(self):
        for body, status in [('', 'missing'), (self.xml_child('<testsuite>'), 'unreadable'),
                             (self.xml_child('<foreign/>'), 'unsupported')]:
            with self.subTest(status=status):
                result, _ = self.result('swiftpm', self.request(body=body), 2)
                self.assertEqual(result['interpretation_status'], status)
                self.assertEqual(result['outcome'], 'incomplete')
                self.assertIsNone(result['counts']['executed'])
                path = self.consumer / 'result.xml'
                if path.exists():
                    path.unlink()

    def test_unreadable_report_is_explicit(self):
        body = self.xml_child(self.xml()) + "p.chmod(0)\n"
        result, _ = self.result('swiftpm', self.request(body=body), 2)
        self.assertEqual(result['interpretation_status'], 'unreadable')

    def test_stale_report_is_not_attributed_to_retry(self):
        request = self.request(body=self.xml_child(self.xml()))
        Path(request['reports'][0]).write_text(self.xml())
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['interpretation_status'], 'stale')
        self.assertIsNone(result['counts']['executed'])

    def test_suite_mismatch_is_not_passing_evidence(self):
        request = self.request(body=self.xml_child(self.xml()))
        request['target']['suite_pattern'] = '^OtherTests\\.'
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['interpretation_status'], 'target_mismatch')

    def test_invalid_suite_pattern_is_a_retained_prerequisite(self):
        for pattern in ['[', ['not', 'a', 'regex']]:
            with self.subTest(pattern=pattern):
                request = self.request(body=self.xml_child(self.xml()))
                request['target']['suite_pattern'] = pattern
                result, _ = self.result('swiftpm', request, 2)
                self.assertEqual(result['command_status'], 'not_started')
                self.assertEqual(result['interpretation_status'], 'prerequisite')
                self.assertEqual(result['outcome'], 'incomplete')
                self.assertIn('invalid suite_pattern:', result['diagnostics'][0])

    def test_gradle_cached_task_cannot_claim_execution(self):
        body = self.xml_child(self.xml(), 'gradle').replace("print('> Task :app:testDebugUnitTest')", "print('> Task :app:testDebugUnitTest FROM-CACHE')")
        result, _ = self.result('gradle', self.request('gradle', body), 2)
        self.assertEqual(result['interpretation_status'], 'not_executed')
        self.assertIsNone(result['counts']['executed'])

    def test_failed_attempt_and_retry_keep_separate_results(self):
        bad = self.request(body=self.xml_child(self.xml(failed=True)) + 'raise SystemExit(1)\n')
        failure, first = self.result('swiftpm', bad, 1)
        Path(bad['reports'][0]).unlink()
        good = self.request(body=self.xml_child(self.xml()))
        success, second = self.result('swiftpm', good)
        self.assertNotEqual(first, second)
        self.assertEqual(json.loads((first / 'summary.json').read_text())['outcome'], 'failed')
        self.assertEqual(success['outcome'], 'passed')
        self.assertEqual(failure['counts']['failed'], 1)

    def test_large_output_keeps_failure_and_raw_bytes(self):
        body = "import sys\nsys.stdout.buffer.write(b'x'*200000 + b'\\n')\nprint('late error: decisive compiler failure', file=sys.stderr)\nsys.exit(1)\n"
        result, attempt = self.result('swiftpm', self.request(body=body, operation='build'), 1)
        self.assertEqual((attempt / 'stdout.log').read_bytes(), b'x' * 200000 + b'\n')
        self.assertIn('late error: decisive compiler failure', result['diagnostics'])
        self.assertEqual(result['outcome'], 'failed')

    def test_large_command_has_explicit_metadata_pointer(self):
        request = self.request(operation='build')
        request['argv'] += ['x' * 20000]
        result, attempt = self.result('swiftpm', request)
        self.assertEqual(result['argv'], {'omitted': True, 'artifact': 'invocation.json'})
        self.assertEqual(json.loads((attempt / 'invocation.json').read_text())['argv'], request['argv'])

    def test_unavailable_tool_and_denied_execution_are_not_test_results(self):
        request = self.request(operation='build')
        Path(request['argv'][0]).unlink()
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['command_status'], 'unavailable')
        self.assertIsNone(result['exit_code'])
        Path(request['argv'][0]).write_text('not executable')
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['command_status'], 'denied')
        self.assertIsNone(result['counts']['executed'])

    def test_timeout_retains_partial_output(self):
        request = self.request(body="import time\nprint('running', flush=True)\ntime.sleep(30)\n", operation='build')
        request['timeout_seconds'] = 2
        result, attempt = self.result('swiftpm', request, 2)
        self.assertEqual(result['command_status'], 'timed_out')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual((attempt / 'stdout.log').read_bytes(), b'running\n')

    def test_interrupt_retains_attempt(self):
        request = self.request(body="import time\nprint('ready', flush=True)\ntime.sleep(30)\n", operation='build')
        path = self.area / 'request.json'
        path.write_text(json.dumps(request))
        process = subprocess.Popen([sys.executable, str(self.helper), 'swiftpm', '--request', str(path),
                                    '--store', str(self.store)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            logs = list(self.store.glob('*/stdout.log'))
            if logs and logs[0].read_bytes() == b'ready\n':
                break
            time.sleep(0.02)
        else:
            self.fail('child did not reach ready')
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 2, stderr)
        result = json.loads(stdout)
        self.assertEqual(result['command_status'], 'interrupted')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual((Path(result['attempt']) / 'stdout.log').read_bytes(), b'ready\n')

    def xcode(self, device='OWNED-SIM', failed=0):
        self.tool('xcrun', "import json,os,sys\nfrom pathlib import Path\n"
                  "Path('inspector-observed.json').write_text(json.dumps({'argv':sys.argv,'cwd':os.getcwd()}))\n"
                  "print(json.dumps(%r))\n" % {
            'title': 'Test - My App', 'result': 'Failed' if failed else 'Passed',
            'passedTests': 2 - failed, 'failedTests': failed, 'skippedTests': 1,
            'totalTestCount': 3, 'devicesAndConfigurations': [{'device': {'deviceId': device}}],
            'testFailures': [{'failureText': 'Expected greeting'}] if failed else []})
        return self.request('xcodebuild', "from pathlib import Path\nPath('result.xcresult').mkdir()\nPath('result.xcresult/Data').write_bytes(b'native bundle')\n")

    def test_xcode_native_summary_and_bundle_retention(self):
        request = self.xcode()
        result, attempt = self.result('xcodebuild', request)
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 0, 'skipped': 1})
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['target_verification'], 'native_device')
        reports = json.loads((attempt / 'reports.json').read_text())
        inspection_argv = ['xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--path',
                           str(attempt / reports[0]['retained']), '--compact']
        self.assertEqual(json.loads((attempt / 'inspection.json').read_text()),
                         {'argv': inspection_argv, 'cwd': str(self.consumer), 'exit_code': 0})
        self.assertEqual(json.loads((self.consumer / 'inspector-observed.json').read_text()),
                         {'argv': [str(self.bin / 'xcrun'), *inspection_argv[1:]], 'cwd': str(self.consumer)})
        shutil.rmtree(self.consumer)
        self.assertEqual((attempt / reports[0]['retained'] / 'Data').read_bytes(), b'native bundle')

    def test_xcode_wrong_destination_cannot_pass(self):
        result, _ = self.result('xcodebuild', self.xcode('OTHER-SIM'), 2)
        self.assertEqual(result['interpretation_status'], 'target_mismatch')
        self.assertEqual(result['outcome'], 'incomplete')

    def test_xcode_wrong_scheme_and_contradictory_result_cannot_pass(self):
        for title, outcome, status in [('Test - Other App', 'Passed', 'target_mismatch'),
                                       ('Test - My App', 'Failed', 'incomplete')]:
            with self.subTest(title=title, outcome=outcome):
                request = self.xcode()
                self.tool('xcrun', 'import json\nprint(json.dumps(%r))\n' % {
                    'title': title, 'result': outcome, 'passedTests': 2, 'failedTests': 0,
                    'skippedTests': 1, 'totalTestCount': 3,
                    'devicesAndConfigurations': [{'device': {'deviceId': 'OWNED-SIM'}}], 'testFailures': []})
                result, _ = self.result('xcodebuild', request, 2)
                self.assertEqual(result['interpretation_status'], status)
                self.assertEqual(result['outcome'], 'incomplete')
                shutil.rmtree(self.consumer / 'result.xcresult')

    def test_xcode_failure_diagnostic(self):
        result, _ = self.result('xcodebuild', self.xcode(failed=1), 1)
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 1, 'skipped': 1})
        self.assertIn('Expected greeting', result['diagnostics'])

    def test_missing_xcresult_inspector_is_explicit(self):
        request = self.xcode()
        self.tool('xcrun', 'raise SystemExit(69)\n')
        result, _ = self.result('xcodebuild', request, 2)
        self.assertEqual(result['interpretation_status'], 'unsupported')

    def test_conflicting_target_is_prerequisite_and_child_is_unrun(self):
        request = self.request(body="from pathlib import Path\nPath('should-not-run').touch()\n", operation='build')
        request['target']['package'] = str(self.area)
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['command_status'], 'not_started')
        self.assertEqual(result['interpretation_status'], 'prerequisite')
        self.assertFalse((self.consumer / 'should-not-run').exists())

    def test_swift_testing_sibling_is_retained_and_missing_runner_is_incomplete(self):
        body = self.xml_child(self.xml()).replace('result.xml', 'result-swift-testing.xml')
        request = self.request(body=body)
        request['argv'].remove('--disable-swift-testing')
        body += "print('Executed 0 tests, with 0 failures')\n"
        self.tool('swift', body)
        result, _ = self.result('swiftpm', request)
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 0, 'skipped': 0})
        (self.consumer / 'result-swift-testing.xml').unlink()
        self.tool('swift', body.replace("print('Executed 0 tests, with 0 failures')", ''))
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['interpretation_status'], 'incomplete')


class NativeExecutionWiring(InstalledFixture, unittest.TestCase):
    def test_installed_phases_reach_native_execution_contract(self):
        for resource in ['skills/hugues-mode/playbooks/build-doctor.md',
                         'skills/hugues-mode/playbooks/mobile-proof.md',
                         'skills/hugues-mode/playbooks/bug-fix.md',
                         'skills/hugues-mode/references/evidence-guide.md']:
            with self.subTest(resource=resource):
                result = self.bound('read-workflow', resource)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('../../../adapters/native-execution.md', result.stdout)
        contract = self.bound('read-workflow', 'adapters/native-execution.md')
        self.assertEqual(contract.returncode, 0, contract.stderr)
        self.assertIn('8,192 UTF-8 bytes', contract.stdout)
        self.assertIn('native_exec.py', contract.stdout)

    def test_installed_proof_keeps_exception_and_artifact_gates(self):
        resource = 'skills/hugues-mode/references/evidence-guide.md'
        guide = self.bound('read-workflow', resource)
        self.assertEqual(guide.returncode, 0, guide.stderr)
        for requirement in ['executable runtime reproduction', 'without claiming automated RED/GREEN',
                            'stale artifact', 'different target', 'action and resulting',
                            'hierarchy/semantics', 'cleanup, reopen']:
            self.assertIn(requirement, guide.stdout)
        proof = self.bound('read-workflow', 'skills/hugues-mode/playbooks/mobile-proof.md')
        self.assertEqual(proof.returncode, 0, proof.stderr)
        for requirement in ['Run the preflight before planning lanes', 'supported native mechanism',
                            'exact current artifact', 'authorized teardown']:
            self.assertIn(requirement, proof.stdout)


if __name__ == '__main__':
    unittest.main()
