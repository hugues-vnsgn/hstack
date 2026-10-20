import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import unittest

from test_host_adapters import InstalledFixture


from native_exec_fixture import NATIVE, NativeExecutionFixture


class NativeExecution(NativeExecutionFixture):


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
        fixed = {key: value for key, value in invocation.items() if key not in {'started_at', 'finished_at', 'revision', 'dirty', 'revision_reason'}}
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
                self.assertEqual(result['outcome'], 'passed')
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
        self.assertEqual(result['interpretation_status'], 'incomplete')
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
        self.assertEqual(result['interpretation_status'], 'incomplete')
        self.assertEqual((Path(result['attempt']) / 'stdout.log').read_bytes(), b'ready\n')


    def test_xcode_native_summary_and_bundle_retention(self):
        request = self.xcode()
        result, attempt = self.result('xcodebuild', request)
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 0, 'skipped': 1})
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['target_verification'], 'native_device')
        reports = json.loads((attempt / 'reports.json').read_text())
        inspection_argv = ['xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--schema-version', '0.4.0', '--path',
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
                    'skippedTests': 1, 'expectedFailures': 0, 'totalTestCount': 3,
                    'devicesAndConfigurations': [{'device': {'deviceId': 'OWNED-SIM'}}], 'testFailures': []})
                result, _ = self.result('xcodebuild', request, 2)
                self.assertEqual(result['interpretation_status'], status)
                self.assertEqual(result['outcome'], 'incomplete')
                shutil.rmtree(self.consumer / 'result.xcresult')

    def test_xcode_failure_diagnostic(self):
        result, _ = self.result('xcodebuild', self.xcode(failed=1), 1)
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 1, 'skipped': 1})
        self.assertIn('testGreeting(): Expected greeting', result['diagnostics'])

    def test_missing_xcresult_inspector_is_explicit(self):
        request = self.xcode()
        self.tool('xcrun', 'raise SystemExit(69)\n')
        result, _ = self.result('xcodebuild', request, 2)
        self.assertEqual(result['interpretation_status'], 'unsupported')

    def test_xcode_timing_flag_does_not_consume_test_action(self):
        for flag in ['-showBuildTimingSummary', '-parallelizeTargets', '-json']:
            with self.subTest(flag=flag):
                request = self.xcode()
                request['argv'].remove('test')
                request['argv'] += [flag, 'test']
                result, _ = self.result('xcodebuild', request)
                self.assertEqual(result['outcome'], 'passed')
                self.assertEqual(result['interpretation_status'], 'complete')
                shutil.rmtree(self.consumer / 'result.xcresult')

    def test_xcode_switches_cannot_hide_clean_or_option_values_become_actions(self):
        request = self.request('xcodebuild', operation='build')
        request['argv'].remove('build')
        request['argv'] += ['-json', 'clean']
        result, _ = self.result('xcodebuild', request, 2)
        self.assertEqual(result['command_status'], 'not_started')
        self.assertEqual(result['interpretation_status'], 'prerequisite')
        for flag in ['-configuration', '-testPlan', '-target']:
            with self.subTest(flag=flag):
                request = self.xcode()
                request['argv'].remove('test')
                request['argv'] += [flag, 'test']
                result, _ = self.result('xcodebuild', request, 2)
                self.assertEqual(result['command_status'], 'not_started')
                self.assertEqual(result['interpretation_status'], 'prerequisite')

    def test_forwarded_clang_directory_spelling_preserves_exact_argv(self):
        body = "import json,sys\nfrom pathlib import Path\nPath('observed.json').write_text(json.dumps(sys.argv))\n"
        request = self.request(body=body, operation='build')
        request['argv'] += ['-Xcc', '-C', '-Xcc', '-E']
        result, _ = self.result('swiftpm', request)
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(json.loads((self.consumer / 'observed.json').read_text()), request['argv'])

    def test_xcode_non_build_modes_never_satisfy_build(self):
        for flag in ['-showBuildSettings', '-list', '-version', '-resolvePackageDependencies', '-enumerate-tests']:
            with self.subTest(flag=flag):
                request = self.request('xcodebuild', "from pathlib import Path\nPath('should-not-run').touch()\n", 'build')
                request['argv'].remove('build')
                request['argv'].append(flag)
                result, _ = self.result('xcodebuild', request, 2)
                self.assertEqual(result['command_status'], 'not_started')
                self.assertEqual(result['interpretation_status'], 'prerequisite')
                self.assertEqual(result['outcome'], 'incomplete')
                self.assertFalse((self.consumer / 'should-not-run').exists())

    def test_target_directory_redirection_is_rejected_before_execution(self):
        for tool, flag in [('swiftpm', '-C'), ('swiftpm', '--chdir'),
                           ('swiftpm', '-Celsewhere'), ('swiftpm', '--chdir=elsewhere'),
                           ('gradle', '-p'), ('gradle', '--project-dir'),
                           ('gradle', '-pelsewhere'), ('gradle', '--project-dir=elsewhere')]:
            with self.subTest(tool=tool, flag=flag):
                request = self.request(tool, "from pathlib import Path\nPath('should-not-run').touch()\n", 'build')
                request['argv'] += [flag] + (['elsewhere'] if flag in {'-C', '--chdir', '-p', '--project-dir'} else [])
                result, _ = self.result(tool, request, 2)
                self.assertEqual(result['command_status'], 'not_started')
                self.assertEqual(result['interpretation_status'], 'prerequisite')
                self.assertEqual(result['outcome'], 'incomplete')
                self.assertFalse((self.consumer / 'should-not-run').exists())

    def test_gradle_failure_xml_is_decisive_with_green_process(self):
        request = self.request('gradle', self.xml_child(self.xml(2, failed=True), 'gradle'))
        result, _ = self.result('gradle', request, 1)
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 2, 'failed': 1, 'skipped': 0})
        self.assertIn('AppTests.test0: expected greeting', result['diagnostics'])

    def test_gradle_report_needs_observed_task_and_matching_report_dir(self):
        request = self.request('gradle', self.xml_child(self.xml(), 'gradle').replace("print('> Task :app:testDebugUnitTest')", ''))
        result, _ = self.result('gradle', request, 2)
        self.assertEqual(result['interpretation_status'], 'incomplete')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertIn('Gradle task execution not observed for report mapping', result['diagnostics'])
        shutil.rmtree(request['reports'][0])
        request['target']['report_dir'] = 'different/reports'
        result, _ = self.result('gradle', request, 2)
        self.assertEqual(result['command_status'], 'not_started')
        self.assertEqual(result['interpretation_status'], 'prerequisite')
        self.assertEqual(result['outcome'], 'incomplete')

    def test_xml_report_set_has_an_aggregate_parse_limit(self):
        body = ("from pathlib import Path\np = Path('app/build/test-results/testDebugUnitTest')\n"
                "p.mkdir(parents=True)\n"
                "for name in ['first', 'second']:\n"
                "    (p / (name + '.xml')).write_text('<testsuite>' + ' ' * (17 * 1024 * 1024) + '</testsuite>')\n"
                "print('> Task :app:testDebugUnitTest')\n")
        result, attempt = self.result('gradle', self.request('gradle', body), 2)
        self.assertEqual(result['interpretation_status'], 'unsupported')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertIn('XML report set exceeds 32 MiB interpretation limit', result['diagnostics'])
        reports = json.loads((attempt / 'reports.json').read_text())
        self.assertEqual(set(reports[0]['files']), {'first.xml', 'second.xml'})

    def test_ten_native_failures_all_fit_without_omission(self):
        cases = ''.join('<testcase classname="Failures" name="test%d"><failure message="failure %d"/></testcase>' % (i, i)
                        for i in range(10))
        result, _ = self.result('swiftpm', self.request(body=self.xml_child('<testsuite tests="10" failures="10">' + cases + '</testsuite>')), 1)
        self.assertEqual(result['counts'], {'executed': 10, 'failed': 10, 'skipped': 0})
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['details_omitted'], False)
        self.assertEqual(result['diagnostics_omitted'], 0)
        self.assertEqual(len(result['diagnostics']), 10)
        self.assertIn('Failures.test0: failure 0', result['diagnostics'])
        self.assertIn('Failures.test9: failure 9', result['diagnostics'])

    def test_passing_run_diagnostics_exclude_zero_failure_noise(self):
        body = self.xml_child(self.xml()) + "print('Executed 1 test, with 0 failures (0 unexpected) in 0.001 seconds')\n"
        result, _ = self.result('swiftpm', self.request(body=body))
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['diagnostics'], [])


    def test_real_parallel_xctest_skip_reconciles_terminal_case_result(self):
        body = self.captured_child('xctest-skipped-verbose')
        request = self.request(body=body)
        request['argv'] += ['--parallel', '--verbose']
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['interpretation_status'], 'zero_tests')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(result['counts'], {'executed': 0, 'failed': 0, 'skipped': 1})

    def test_real_parallel_xctest_without_skip_visibility_stays_incomplete(self):
        request = self.request(body=self.captured_child('xctest-skipped'))
        request['argv'] += ['--parallel']
        result, _ = self.result('swiftpm', request, 2)
        self.assertEqual(result['interpretation_status'], 'incomplete')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(result['counts'], {'executed': None, 'failed': 0, 'skipped': None})
        self.assertIn('XCTest skip counts require matching terminal case results; use swift test --parallel --verbose', result['diagnostics'])

    def test_xctest_terminal_results_must_match_identity_and_xml(self):
        original = (NATIVE / 'xctest-skipped-verbose.stdout.txt').read_text()
        for output in [original.replace('NativeCaptureTests.NativeCaptureTests testSkipped', 'OtherTests testSkipped'),
                       original.replace("skipped (0.001 seconds)", "failed (0.001 seconds)"),
                       original + "Test Case '-[NativeCaptureTests.NativeCaptureTests testSkipped]' passed (0.001 seconds).\n"]:
            with self.subTest(output=output[-100:]):
                body = self.xml_child((NATIVE / 'xctest-skipped-verbose.xml').read_text())
                body += 'print(%r)\n' % output
                result, _ = self.result('swiftpm', self.request(body=body), 2)
                self.assertEqual(result['interpretation_status'], 'incomplete')
                self.assertEqual(result['outcome'], 'incomplete')
                (self.consumer / 'result.xml').unlink()

    def test_real_parallel_xctest_pass_and_manifest_literal(self):
        request = self.request(body=self.captured_child('xctest-passed-verbose'))
        request['argv'] += ['--parallel', '--verbose']
        result, attempt = self.result('swiftpm', request)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 0, 'skipped': 0})
        reports = json.loads((attempt / 'reports.json').read_text())
        self.assertEqual(reports, [
            {'source': str(self.consumer / 'result.xml'), 'retained': 'reports/0/result.xml', 'status': 'retained',
             'files': {'result.xml': {'sha256': 'b2aec561e9857bff5d38e4386954f963404d1bf1965e59ca84f2f958028badf9', 'bytes': 274}}},
            {'source': str(self.consumer / 'result-swift-testing.xml'), 'retained': None, 'status': 'missing', 'files': {}}])
        shutil.rmtree(self.consumer)
        self.assertEqual((attempt / 'reports/0/result.xml').read_bytes(), (NATIVE / 'xctest-passed-verbose.xml').read_bytes())

    def test_real_swift_testing_primary_path_and_disabled_count_convention(self):
        for name, status, counts, code in [
                ('swift-testing-primary', 'complete', {'executed': 1, 'failed': 0, 'skipped': 0}, 0),
                ('swift-testing-disabled', 'zero_tests', {'executed': 0, 'failed': 0, 'skipped': 1}, 2)]:
            with self.subTest(name=name):
                request = self.request(body=self.captured_child(name))
                request['argv'].remove('--disable-swift-testing')
                request['argv'] += ['--disable-xctest']
                result, _ = self.result('swiftpm', request, code)
                self.assertEqual(result['interpretation_status'], status)
                self.assertEqual(result['outcome'], 'passed' if code == 0 else 'incomplete')
                self.assertEqual(result['counts'], counts)
                (self.consumer / 'result.xml').unlink()

    def test_both_swift_runners_keep_separate_count_conventions(self):
        body = self.captured_child('xctest-passed-verbose')
        body += "from pathlib import Path\nPath('result-swift-testing.xml').write_text(%r)\n" % (NATIVE / 'swift-testing-disabled.xml').read_text()
        request = self.request(body=body)
        request['argv'].remove('--disable-swift-testing')
        result, _ = self.result('swiftpm', request)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 0, 'skipped': 1})

    def test_swift_testing_skip_convention_does_not_weaken_gradle_counts(self):
        request = self.request('gradle', self.xml_child((NATIVE / 'swift-testing-disabled.xml').read_text(), 'gradle'))
        result, _ = self.result('gradle', request, 2)
        self.assertEqual(result['interpretation_status'], 'incomplete')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertIn('native XML declared tests differs from cases', result['diagnostics'])

    def test_real_swift_testing_multiple_issues_are_one_failed_test(self):
        request = self.request(body=self.xml_child((NATIVE / 'swift-testing-multiple-issues.xml').read_text()))
        request['argv'].remove('--disable-swift-testing')
        request['argv'] += ['--disable-xctest']
        result, _ = self.result('swiftpm', request, 1)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 1, 'skipped': 0})
        self.assertIn('ReviewTests.multipleIssues(): Expectation failed: 1 == 2 (error)', result['diagnostics'])
        self.assertIn('ReviewTests.multipleIssues(): Expectation failed: 3 == 4 (error)', result['diagnostics'])

    def test_real_xcresult_expected_failures_and_test_name(self):
        request = self.xcode()
        request['argv'][request['argv'].index('-scheme') + 1] = 'SetupProof'
        request['argv'][request['argv'].index('-destination') + 1] = 'id=2FA5430F-801F-41A4-A0F8-EE459354F82C'
        request['target'] = {'scheme': 'SetupProof', 'destination': 'id=2FA5430F-801F-41A4-A0F8-EE459354F82C'}
        self.tool('xcrun', 'import sys\nsys.stdout.buffer.write(%r)\n' % (NATIVE / 'xcresult-expected-failure.json').read_bytes())
        result, _ = self.result('xcodebuild', request, 1)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 3, 'failed': 1, 'skipped': 0})
        self.assertIn('testFailure(): XCTAssertEqual failed: ("1") is not equal to ("2") - captured failure diagnostic', result['diagnostics'])

    def test_real_gradle_failure_xml_keeps_all_failures(self):
        request = self.request('gradle', self.captured_child('gradle-jvm-failure', tool='gradle'))
        result, _ = self.result('gradle', request, 1)
        self.assertEqual(result['interpretation_status'], 'complete')
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 10, 'failed': 10, 'skipped': 0})
        self.assertEqual(result['details_omitted'], False)
        self.assertEqual(result['diagnostics_omitted'], 0)
        self.assertEqual(sum(line.startswith('NativeFailureTest.') for line in result['diagnostics'][:10]), 10)
        self.assertIn('NativeFailureTest.testFailure10: java.lang.AssertionError: native failure 10 expected:<1> but was:<2>', result['diagnostics'])
        self.assertIn('NativeFailureTest.testFailure9: java.lang.AssertionError: native failure 9 expected:<1> but was:<2>', result['diagnostics'])

    def test_real_kotlin_error_and_gradle_offline_cause_survive(self):
        for name, expected in [
                ('gradle-kotlin-error', "Unresolved reference 'missingNativeSymbol'."),
                ('gradle-offline-missing-dependency', 'No cached version of org.hstack.capture:offline-only-missing:1.0 available for offline mode.')]:
            with self.subTest(name=name):
                body = self.captured_child(name, report=False, log='stderr', tool='gradle') + 'raise SystemExit(1)\n'
                result, _ = self.result('gradle', self.request('gradle', body, 'build'), 1)
                self.assertEqual(result['outcome'], 'failed')
                self.assertTrue(any(expected in line for line in result['diagnostics']), result['diagnostics'])

    def test_real_multi_error_logs_keep_first_error_and_strip_ansi(self):
        for name, log in [('swift-build-five-errors', 'stderr'), ('swift-build-five-errors-color', 'pty')]:
            with self.subTest(name=name):
                content = (NATIVE / (name + '.' + log + '.txt')).read_bytes()
                body = 'import sys\nsys.stderr.buffer.write(%r)\nraise SystemExit(1)\n' % content
                result, attempt = self.result('swiftpm', self.request(body=body, operation='build'), 1)
                self.assertEqual(result['outcome'], 'failed')
                self.assertEqual(result['details_omitted'], False)
                self.assertTrue(any('NativeCapture.swift:1:26:' in line for line in result['diagnostics']), result['diagnostics'])
                self.assertTrue(any('NativeCapture.swift:5:26:' in line for line in result['diagnostics']), result['diagnostics'])
                self.assertNotIn('\x1b', ''.join(result['diagnostics']))
                self.assertEqual((attempt / 'stderr.log').read_bytes(), content)

    def test_styled_diagnostic_clipping_and_metadata_omissions_are_explicit(self):
        content = '\x1b[31me: Native.kt:1: ' + 'x' * 12000 + ' Unresolved reference\x1b[0m\n'
        request = self.request('gradle', 'import sys\nsys.stderr.write(%r)\nraise SystemExit(1)\n' % content, 'build')
        result, attempt = self.result('gradle', request, 1)
        self.assertEqual(result['details_omitted'], True)
        self.assertNotIn('\x1b', ''.join(result['diagnostics']))
        self.assertTrue(result['diagnostics'][0].startswith('e: Native.kt:1: '))
        self.assertIn('Unresolved reference', result['diagnostics'][0])
        self.assertEqual((attempt / 'stderr.log').read_text(), content)
        request = self.request(operation='build')
        request['argv'] += ['x' * 20000]
        result, _ = self.result('swiftpm', request)
        self.assertEqual(result['details_omitted'], True)

    def test_xcresult_inspection_timeout_uses_request_timeout_and_keeps_partial_output(self):
        request = self.xcode()
        request['timeout_seconds'] = 0.5
        self.tool('xcrun', "import time\nprint('partial inspector output', flush=True)\ntime.sleep(30)\n")
        result, attempt = self.result('xcodebuild', request, 2)
        self.assertEqual(result['command_status'], 'exited')
        self.assertEqual(result['interpretation_status'], 'unsupported')
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual((attempt / 'inspection.stdout').read_bytes(), b'partial inspector output\n')

    def test_unicode_diagnostics_converge_under_byte_budget_with_large_metadata(self):
        output = ''.join('error: %d ' % i + '\U0001f600' * 90 + '\n' for i in range(6))
        body = 'import sys\nsys.stderr.write(%r)\nraise SystemExit(1)\n' % output
        request = self.request(body=body, operation='build')
        request['argv'].append('a' * 1300)
        request['target']['context'] = 'b' * 1200
        result, attempt = self.result('swiftpm', request, 1)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['details_omitted'], True)
        self.assertEqual(len(result['diagnostics']) + result['diagnostics_omitted'], 6)
        self.assertGreater(result['diagnostics_omitted'], 0)
        self.assertTrue(result['diagnostics'][0].startswith('error: 0 '))
        self.assertEqual((attempt / 'stderr.log').read_text(), output)

    def test_u3_decisive_assertion_survives_ranked_summary(self):
        output = (NATIVE / 'u3-ios-red.txt').read_text()
        request = self.request(body='print(%r)\nraise SystemExit(1)\n' % output, operation='build')
        result, _ = self.result('swiftpm', request, 1)
        self.assertTrue(any('("Home notes") is not equal to ("Work notes")' in line
                            for line in result['diagnostics']), result['diagnostics'])
        self.assertFalse(any('RegisterExecutionPolicyException' in line for line in result['diagnostics']))

    def test_u3_passing_builds_have_no_scraped_diagnostics(self):
        for name in ['u3-swiftpm-noise', 'u3-xcode-noise', 'u3-gradle-noise']:
            with self.subTest(name=name):
                output = (NATIVE / (name + '.txt')).read_text()
                result, _ = self.result('swiftpm', self.request(body='print(%r)\n' % output, operation='build'))
                self.assertEqual(result['outcome'], 'passed')
                self.assertEqual(result['diagnostics'], [])

    def test_every_xcresult_failure_precedes_scraped_logs(self):
        request = self.xcode(failed=1)
        failures = [{'testName': 'case%d' % i, 'failureText': 'native %d' % i} for i in range(20)]
        self.tool('xcrun', 'import json\nprint(json.dumps(%r))\n' % {
            'title': 'Test - My App', 'result': 'Failed', 'passedTests': 0, 'failedTests': 20,
            'skippedTests': 0, 'expectedFailures': 0, 'totalTestCount': 20,
            'devicesAndConfigurations': [{'device': {'deviceId': 'OWNED-SIM'}}], 'testFailures': failures})
        result, _ = self.result('xcodebuild', request, 1)
        self.assertEqual(result['diagnostics'], ['case%d: native %d' % (i, i) for i in range(20)])
        self.assertEqual(result['diagnostics_omitted'], 0)

    def test_budget_reports_exact_number_of_excluded_lines(self):
        output = ''.join('error: line %03d %s\n' % (i, 'x' * 100) for i in range(200))
        request = self.request(body='print(%r)\nraise SystemExit(1)\n' % output, operation='build')
        result, _ = self.result('swiftpm', request, 1)
        self.assertEqual(len(result['diagnostics']) + result['diagnostics_omitted'], 200)
        self.assertGreater(result['diagnostics_omitted'], 100)
        self.assertTrue(result['diagnostics'][0].startswith('error: line 000 '))
        self.assertEqual(result['details_omitted'], True)

    def test_native_failures_fill_budget_before_assertions_and_generic_logs(self):
        xml = '<testsuite>' + ''.join('<testcase name="test%d"><failure message="native %d"/></testcase>'
                                     % (i, i) for i in range(25)) + '</testsuite>'
        body = self.xml_child(xml) + "print('exception generic')\nprint('error: expected assertion')\n"
        result, _ = self.result('swiftpm', self.request(body=body), 1)
        self.assertEqual(result['diagnostics'][:25], ['.test%d: native %d' % (i, i) for i in range(25)])
        self.assertEqual(result['diagnostics'][25:], ['error: expected assertion', 'exception generic'])
        self.assertEqual(result['diagnostics_omitted'], 0)

    def test_git_revision_clean_dirty_and_non_repository(self):
        request = self.request(operation='build')
        result, attempt = self.result('swiftpm', request)
        record = json.loads((attempt / 'invocation.json').read_text())
        self.assertEqual(record['revision'], None)
        self.assertEqual(record['dirty'], None)
        self.assertTrue(record['revision_reason'])
        (self.consumer / 'tracked.txt').write_text('baseline')
        subprocess.run(['git', 'init', '-q', str(self.consumer)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(self.consumer), 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(self.consumer), '-c', 'user.name=Fixture', '-c',
                        'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], check=True, capture_output=True)
        revision = subprocess.check_output(['git', '-C', str(self.consumer), 'rev-parse', 'HEAD']).decode().strip()
        subprocess.run(['git', '-C', str(self.consumer), 'config', 'status.showUntrackedFiles', 'no'],
                       check=True, capture_output=True)
        for dirty in [False, True]:
            if dirty:
                (self.consumer / 'dirty.txt').write_text('changed')
            _, attempt = self.result('swiftpm', request)
            record = json.loads((attempt / 'invocation.json').read_text())
            self.assertEqual(record['revision'], revision)
            self.assertEqual(record['dirty'], dirty)
            self.assertEqual(record['revision_reason'], None)


    def test_captured_adb_raw_pass_and_assertion_failure(self):
        for name, code, counts in [('adb-pass', 0, {'executed': 1, 'failed': 0, 'skipped': 0}),
                                   ('adb-failure', 1, {'executed': 1, 'failed': 1, 'skipped': 0})]:
            with self.subTest(name=name):
                output = (NATIVE / (name + '.txt')).read_text()
                result, attempt = self.result('adb-instrument', self.instrument_request(output), code)
                self.assertEqual(result['exit_code'], 0)
                self.assertEqual(result['counts'], counts)
                self.assertEqual(result['outcome'], 'passed' if code == 0 else 'failed')
                self.assertEqual((attempt / 'stdout.log').read_text(), output + '\n')

    def test_adb_crash_zero_and_truncated_output_never_pass(self):
        for output in [(NATIVE / 'adb-crash.txt').read_text(),
                       (NATIVE / 'adb-zero.txt').read_text(),
                       'INSTRUMENTATION_STATUS_CODE: 1']:
            with self.subTest(output=output):
                result, _ = self.result('adb-instrument', self.instrument_request(output), 2)
                self.assertEqual(result['outcome'], 'incomplete')

    def test_adb_duplicate_missing_and_conflicting_terminals_never_pass(self):
        passed = (NATIVE / 'adb-pass.txt').read_text()
        for output in [passed.replace('INSTRUMENTATION_CODE: -1', ''),
                       passed.replace('INSTRUMENTATION_STATUS_CODE: 0', 'INSTRUMENTATION_STATUS_CODE: 2'),
                       passed + passed,
                       passed.replace('numtests=1', 'numtests=2'),
                       passed.replace('INSTRUMENTATION_STATUS_CODE: 1', 'INSTRUMENTATION_STATUS_CODE: 0'),
                       passed + 'INSTRUMENTATION_RESULT: shortMsg=Process crashed.\n']:
            with self.subTest(output=output[-120:]):
                result, _ = self.result('adb-instrument', self.instrument_request(output), 2)
                self.assertEqual(result['outcome'], 'incomplete')

    def test_adb_observed_failure_survives_duplicate_passing_terminal(self):
        passed = (NATIVE / 'adb-pass.txt').read_text()
        terminal = passed[passed.index('INSTRUMENTATION_STATUS: class=', 10):passed.index('INSTRUMENTATION_RESULT:')]
        output = passed.replace('INSTRUMENTATION_STATUS_CODE: 0',
                                'INSTRUMENTATION_STATUS_CODE: -2') + terminal
        result, _ = self.result('adb-instrument', self.instrument_request(output), 1)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts']['failed'], 1)
        self.assertEqual(result['interpretation_status'], 'incomplete')

    def test_adb_malformed_and_out_of_order_protocol_never_pass(self):
        passed = (NATIVE / 'adb-pass.txt').read_text()
        for output in [passed.replace('INSTRUMENTATION_CODE: -1', 'INSTRUMENTATION_STATUS_CODE: nonsense\nINSTRUMENTATION_CODE: -1'),
                       'INSTRUMENTATION_CODE: -1\n' + passed.replace('INSTRUMENTATION_CODE: -1', '')]:
            with self.subTest(output=output[-150:]):
                result, _ = self.result('adb-instrument', self.instrument_request(output), 2)
                self.assertEqual(result['outcome'], 'incomplete')

    def test_adb_rejects_other_commands_and_unresolved_targets(self):
        for change in ['command', 'serial', 'runner', 'build', 'reports']:
            with self.subTest(change=change):
                request = self.instrument_request((NATIVE / 'adb-pass.txt').read_text())
                if change == 'command':
                    request['argv'] = [request['argv'][0], 'install', 'app.apk']
                elif change in {'serial', 'runner'}:
                    request['target'][change] = 'different'
                elif change == 'build':
                    request['operation'] = 'build'
                else:
                    request['reports'] = ['invented.xml']
                result, _ = self.result('adb-instrument', request, 2)
                self.assertEqual(result['command_status'], 'not_started')
                self.assertEqual(result['interpretation_status'], 'prerequisite')

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
