"""Drive the fixture with XCUITest on an owned simulator and retain proof."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parent
    evidence_root = Path(os.environ['ISSUE35_EVIDENCE_ROOT']).resolve()
    evidence_root.mkdir(parents=True, exist_ok=True)
    evidence = Path(tempfile.mkdtemp(prefix='proof-', dir=evidence_root))
    commands = []

    def run(*argv):
        result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=600)
        commands.append({'argv': list(argv), 'exit': result.returncode,
                         'stdout': result.stdout, 'stderr': result.stderr})
        (evidence / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        result.check_returncode()
        return result.stdout.strip()

    runtimes = json.loads(run('xcrun', 'simctl', 'list', 'runtimes', '-j'))['runtimes']
    compatible = [r for r in runtimes if r['isAvailable'] and '.iOS-' in r['identifier']
                  and int(r['version'].split('.')[0]) >= 17]
    if not compatible:
        raise RuntimeError('An available iOS 17+ simulator runtime is required')
    runtime = compatible[0]
    device_type = next(t['identifier'] for t in runtime['supportedDeviceTypes'] if t['productFamily'] == 'iPhone')
    udid = run('xcrun', 'simctl', 'create', 'huguesstack-issue35', device_type, runtime['identifier'])
    receipt = {'device': udid, 'runtime': runtime['identifier'], 'status': 'failed'}
    try:
        bundle = 'org.huguesstack.setup-proof'
        spec = {'name': 'SetupProof', 'options': {'deploymentTarget': {'iOS': '17.0'}},
                'targets': {
                    'SetupProof': {'type': 'application', 'platform': 'iOS',
                        'sources': [str(root / 'App.swift')],
                        'settings': {'PRODUCT_BUNDLE_IDENTIFIER': bundle},
                        'info': {'path': 'Info.plist', 'properties': {
                            'UILaunchScreen': {}, 'UIApplicationSceneManifest': {
                                'UIApplicationSupportsMultipleScenes': False,
                                'UISceneConfigurations': {'UIWindowSceneSessionRoleApplication': [{
                                    'UISceneConfigurationName': 'Default',
                                    'UISceneDelegateClassName': 'SceneDelegate'}]}}}}},
                    'GreetingTests': {'type': 'bundle.ui-testing', 'platform': 'iOS',
                        'sources': [str(root / 'GreetingTests.swift')],
                        'settings': {'GENERATE_INFOPLIST_FILE': 'YES'},
                        'dependencies': [{'target': 'SetupProof'}]}},
                'schemes': {'SetupProof': {'build': {'targets': {'SetupProof': 'all'}},
                                         'test': {'targets': ['GreetingTests']}}}}
        project = evidence / 'project.json'
        project.write_text(json.dumps(spec, indent=2) + '\n')
        run('xcodegen', 'generate', '--spec', str(project), '--project', str(evidence))
        run('xcrun', 'simctl', 'boot', udid)
        run('xcrun', 'simctl', 'bootstatus', udid, '-b')
        results = evidence / 'Greeting.xcresult'
        run('xcodebuild', 'test', '-project', str(evidence / 'SetupProof.xcodeproj'),
            '-scheme', 'SetupProof', '-destination', 'id=' + udid,
            '-parallel-testing-enabled', 'NO', '-derivedDataPath', str(evidence / 'build'),
            '-resultBundlePath', str(results), 'CODE_SIGNING_ALLOWED=NO')
        summary = json.loads(run('xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--path', str(results)))
        (evidence / 'test-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        assert summary['passedTests'] == 1 and summary['failedTests'] == 0 and summary['skippedTests'] == 0
        attachments = evidence / 'attachments'
        run('xcrun', 'xcresulttool', 'export', 'attachments', '--path', str(results), '--output-path', str(attachments))
        manifest = json.loads((attachments / 'manifest.json').read_text())
        images = [a for test in manifest for a in test['attachments'] if a['suggestedHumanReadableName'].startswith('greeting')]
        assert len(images) == 1, 'expected the greeting screenshot attachment'
        shutil.copyfile(attachments / images[0]['exportedFileName'], evidence / 'greeting.png')
        container = Path(run('xcrun', 'simctl', 'get_app_container', udid, bundle, 'data'))
        greeting = (container / 'Documents/greeting.txt').read_text()
        assert greeting == 'Hello, Codex!', 'greeting did not persist'
        (evidence / 'greeting.txt').write_text(greeting)
        receipt['status'] = 'passed'
    except Exception as error:
        receipt['error'] = str(error)
        raise
    finally:
        cleanup_errors = []
        try:
            devices = json.loads(run('xcrun', 'simctl', 'list', 'devices', '-j'))['devices']
            device = next(d for rows in devices.values() for d in rows if d['udid'] == udid)
            if device['state'] == 'Booted':
                run('xcrun', 'simctl', 'shutdown', udid)
        except Exception as error:
            cleanup_errors.append(str(error))
        try:
            run('xcrun', 'simctl', 'delete', udid)
        except Exception as error:
            cleanup_errors.append(str(error))
        receipt['cleanup'] = 'failed' if cleanup_errors else 'deleted-owned-simulator'
        receipt['cleanup_errors'] = cleanup_errors
        (evidence / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if cleanup_errors:
            raise RuntimeError('Cleanup failed; inspect ' + str(evidence / 'result.json'))
    assert (evidence / 'greeting.png').stat().st_size > 0
    assert (evidence / 'greeting.txt').read_text() == 'Hello, Codex!'
    print(evidence)


if __name__ == '__main__':
    main()
