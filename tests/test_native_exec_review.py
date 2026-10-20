import json
import os
import re
import unittest
from unittest.mock import patch

from native_exec_fixture import ROOT, NATIVE, NativeExecutionFixture


class NativeExecutionReview(NativeExecutionFixture):
    def test_verbose_native_stacks_keep_every_failure_name_and_message(self):
        for lengths, fill in [([5000] * 10, 'x'), ([30000] + [20] * 9, 'x'), ([1000] * 10, '😀')]:
            with self.subTest(lengths=lengths):
                (self.consumer / 'result.xml').unlink(missing_ok=True)
                cases = ''.join('<testcase classname="Verbose" name="test%d"><failure>expected %d\n%s</failure></testcase>'
                                % (i, i, fill * length) for i, length in enumerate(lengths))
                result, attempt = self.result('swiftpm', self.request(body=self.xml_child('<testsuite>' + cases + '</testsuite>')), 1)
                self.assertEqual(result['counts'], {'executed': 10, 'failed': 10, 'skipped': 0})
                self.assertEqual(len(result['diagnostics']), 10)
                for i in range(10):
                    self.assertTrue(result['diagnostics'][i].startswith('Verbose.test%d: expected %d' % (i, i)))
                self.assertEqual(result['diagnostics_omitted'], 0)
                self.assertEqual(result['details_omitted'], True)
                self.assertEqual((attempt / 'reports/0/result.xml').read_text(), '<testsuite>' + cases + '</testsuite>')
                (self.consumer / 'result.xml').unlink()

    def test_native_duplicate_entries_survive_while_scraped_duplicates_collapse(self):
        request = self.xcode(failed=1)
        self.tool('xcodebuild', "from pathlib import Path\nPath('result.xcresult').mkdir()\nprint('exception duplicate')\nprint('exception duplicate')\n")
        self.tool('xcrun', 'import json\nprint(json.dumps(%r))\n' % {
            'title': 'Test - My App', 'result': 'Failed', 'passedTests': 0, 'failedTests': 2,
            'skippedTests': 0, 'expectedFailures': 0, 'totalTestCount': 2,
            'devicesAndConfigurations': [{'device': {'deviceId': 'OWNED-SIM'}}],
            'testFailures': [{'testName': 'duplicate()', 'failureText': 'expected value'}] * 2})
        result, _ = self.result('xcodebuild', request, 1)
        self.assertEqual(result['diagnostics'], ['duplicate(): expected value',
                                                 'duplicate(): expected value', 'exception duplicate'])
        self.assertEqual(result['diagnostics_omitted'], 0)

    def test_failed_run_filters_named_noise_before_real_error(self):
        for name in ['u3-xcode-noise', 'u3-gradle-noise']:
            with self.subTest(name=name):
                output = (NATIVE / (name + '.txt')).read_text() + '\nerror: actual compiler failure\n'
                result, _ = self.result('swiftpm', self.request(body='print(%r)\nraise SystemExit(1)\n' % output, operation='build'), 1)
                self.assertEqual(result['diagnostics'], ['error: actual compiler failure'])

    def test_passing_run_does_not_scrape_genuine_exception_text(self):
        result, _ = self.result('swiftpm', self.request(body="print('exception in an optional probe')\n", operation='build'))
        self.assertEqual(result['outcome'], 'passed')
        self.assertEqual(result['diagnostics'], [])

    def test_unexpected_summary_is_generic_below_expected_assertion(self):
        output = 'Executed 1 test, with 2 failures (0 unexpected)\nexpected greeting was absent\n'
        result, _ = self.result('swiftpm', self.request(body='print(%r)\nraise SystemExit(1)\n' % output, operation='build'), 1)
        self.assertEqual(result['diagnostics'], ['expected greeting was absent',
                                                 'Executed 1 test, with 2 failures (0 unexpected)'])

    def test_adb_error_terminal_is_failure_even_with_zero_process_exit(self):
        output = (NATIVE / 'adb-pass.txt').read_text().replace('INSTRUMENTATION_STATUS_CODE: 0',
                                                             'INSTRUMENTATION_STATUS_CODE: -1')
        result, _ = self.result('adb-instrument', self.instrument_request(output), 1)
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['outcome'], 'failed')
        self.assertEqual(result['counts'], {'executed': 1, 'failed': 1, 'skipped': 0})

    def test_adb_ignored_and_assumption_states_count_as_skipped(self):
        passed = (NATIVE / 'adb-pass.txt').read_text().replace('numtests=1', 'numtests=2')
        for state in [-3, -4]:
            with self.subTest(state=state):
                fields = ('INSTRUMENTATION_STATUS: class=Review\nINSTRUMENTATION_STATUS: test=skip\n'
                          'INSTRUMENTATION_STATUS: numtests=2\n')
                skipped = (fields + 'INSTRUMENTATION_STATUS_CODE: 1\n' if state == -4 else '')
                skipped += fields + 'INSTRUMENTATION_STATUS_CODE: %d\n' % state
                result, _ = self.result('adb-instrument', self.instrument_request(skipped + passed))
                self.assertEqual(result['interpretation_status'], 'complete')
                self.assertEqual(result['counts'], {'executed': 1, 'failed': 0, 'skipped': 1})

    def test_adb_all_skipped_states_cannot_pass(self):
        passed = (NATIVE / 'adb-pass.txt').read_text()
        for state in [-3, -4]:
            with self.subTest(state=state):
                output = passed.replace('INSTRUMENTATION_STATUS_CODE: 0', 'INSTRUMENTATION_STATUS_CODE: %d' % state)
                if state == -3:
                    output = output[output.index('INSTRUMENTATION_STATUS: class=', 10):]
                result, _ = self.result('adb-instrument', self.instrument_request(output), 2)
                self.assertEqual(result['outcome'], 'incomplete')
                self.assertEqual(result['counts'], {'executed': 0, 'failed': 0, 'skipped': 1})

    def test_adb_missing_device_is_incomplete_and_cannot_be_red(self):
        request = self.instrument_request('')
        self.tool('adb', "import sys\nsys.stderr.write('error: device emulator-5560 not found\\n')\nraise SystemExit(1)\n")
        result, _ = self.result('adb-instrument', request, 2)
        self.assertEqual(result['exit_code'], 1)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(result['counts']['failed'], None)
        self.assertIn('error: device emulator-5560 not found', result['diagnostics'])

    def test_adb_target_regexes_reject_shell_expansion_and_option_serial(self):
        for field, values in [('serial', ['-emulator-5560', 'with space', 'serial;id', 'serial$HOME']),
                              ('runner', ['org.app.test/Runner$Nested', 'org.app.test/Run;id', 'org.app.test/Run name', 'missing-slash'])]:
            for value in values:
                with self.subTest(field=field, value=value):
                    request = self.instrument_request((NATIVE / 'adb-pass.txt').read_text())
                    request['target'][field] = value
                    request['argv'][2 if field == 'serial' else -1] = value
                    result, _ = self.result('adb-instrument', request, 2)
                    self.assertEqual(result['command_status'], 'not_started')
                    self.assertEqual(result['interpretation_status'], 'prerequisite')

    def fake_git(self, status_body):
        self.tool('git', "import json,sys\nfrom pathlib import Path\n"
                  "if sys.argv[1:] == ['rev-parse', 'HEAD']:\n    print('" + 'a' * 40 + "')\n"
                  "else:\n    Path('git-status-argv.json').write_text(json.dumps(sys.argv[1:]))\n" + status_body)

    def test_git_status_disables_optional_locks_and_fsmonitor(self):
        request = self.request(operation='build')
        self.fake_git("    print('?? untracked.txt')\n")
        with patch.dict(os.environ, {'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}):
            _, attempt = self.result('swiftpm', request)
        record = json.loads((attempt / 'invocation.json').read_text())
        self.assertEqual(record['revision'], 'a' * 40)
        self.assertEqual(record['dirty'], True)
        self.assertEqual(json.loads((self.consumer / 'git-status-argv.json').read_text()),
                         ['--no-optional-locks', '-c', 'core.fsmonitor=false', 'status', '--porcelain', '--untracked-files=all'])

    def test_git_status_failure_keeps_revision_and_nonempty_reason(self):
        request = self.request(operation='build')
        self.fake_git('    raise SystemExit(1)\n')
        with patch.dict(os.environ, {'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}):
            _, attempt = self.result('swiftpm', request)
        record = json.loads((attempt / 'invocation.json').read_text())
        self.assertEqual(record['revision'], 'a' * 40)
        self.assertEqual(record['dirty'], None)
        self.assertTrue(record['revision_reason'])

    def test_git_status_timeout_keeps_known_revision(self):
        request = self.request(operation='build')
        self.fake_git('    import time\n    time.sleep(30)\n')
        with patch.dict(os.environ, {'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}):
            _, attempt = self.result('swiftpm', request)
        record = json.loads((attempt / 'invocation.json').read_text())
        self.assertEqual(record['revision'], 'a' * 40)
        self.assertEqual(record['dirty'], None)
        self.assertTrue(record['revision_reason'])


class NativeExecutionAccounting(unittest.TestCase):
    def test_every_current_document_total_matches_collection(self):
        count = unittest.defaultTestLoader.discover(str(ROOT / 'tests')).countTestCases()
        coverage = (ROOT / 'docs/TEST-COVERAGE.md').read_text()
        self.assertEqual(int(re.search(r'\| Total collected \| (\d+) \|', coverage)[1]), count)
        self.assertEqual(int(re.search(r'(\d+) Python cases', coverage)[1]), count)
        self.assertEqual(int(re.search(r'\*\*(\d+) top-level unittest cases', coverage)[1]), count)
        core = (ROOT / 'docs/CORE-RESTORATION.md').read_text()
        self.assertEqual(int(re.search(r'current candidate collects (\d+) tests', core)[1]), count)
