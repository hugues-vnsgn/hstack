import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tests/fixtures/native-execution'


class NativeExecutionFixture(unittest.TestCase):
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


    def xcode(self, device='OWNED-SIM', failed=0):
        self.tool('xcrun', "import json,os,sys\nfrom pathlib import Path\n"
                  "Path('inspector-observed.json').write_text(json.dumps({'argv':sys.argv,'cwd':os.getcwd()}))\n"
                  "print(json.dumps(%r))\n" % {
            'title': 'Test - My App', 'result': 'Failed' if failed else 'Passed',
            'passedTests': 2 - failed, 'failedTests': failed, 'skippedTests': 1, 'expectedFailures': 0,
            'totalTestCount': 3, 'devicesAndConfigurations': [{'device': {'deviceId': device}}],
            'testFailures': [{'testName': 'testGreeting()', 'failureText': 'Expected greeting'}] if failed else []})
        return self.request('xcodebuild', "from pathlib import Path\nPath('result.xcresult').mkdir()\nPath('result.xcresult/Data').write_bytes(b'native bundle')\n")


    def captured_child(self, name, report=True, log='stdout', tool='swiftpm'):
        body = ''
        if report:
            body += self.xml_child((NATIVE / (name + '.xml')).read_text(), tool)
        path = NATIVE / (name + '.' + log + '.txt')
        if path.exists():
            body += 'import sys\nsys.%s.buffer.write(%r)\n' % (log, path.read_bytes())
        return body


    def instrument_request(self, output):
        executable = self.tool('adb', 'print(%r)\n' % output)
        return {'argv': [executable, '-s', 'emulator-5560', 'shell', 'am', 'instrument', '-w', '-r',
                         'org.u3.drafts.test/androidx.test.runner.AndroidJUnitRunner'],
                'cwd': str(self.consumer), 'operation': 'test',
                'target': {'serial': 'emulator-5560',
                           'runner': 'org.u3.drafts.test/androidx.test.runner.AndroidJUnitRunner'},
                'reports': [], 'env': {}, 'timeout_seconds': 10}
