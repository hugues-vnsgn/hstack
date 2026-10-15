"""Owner-reviewable configuration through the bound installed entrypoint."""
import json
import hashlib
import os
from pathlib import Path
import runpy
import unittest

from test_host_adapters import InstalledFixture

ROOT = Path(__file__).resolve().parents[1]


class PayloadPolicy(InstalledFixture, unittest.TestCase):
    def fake_bun(self):
        directory = self.area / 'bin'
        directory.mkdir()
        runtime = directory / 'bun'
        runtime.write_text('#!/bin/sh\nexit 99\n')
        runtime.chmod(0o755)
        return str(directory)

    def test_helper_readiness_holds_missing_stale_and_absent_runtime_without_bootstrap(self):
        cache = self.plugin / 'skills/hugues-mode/scripts/node_modules'
        runtime = self.fake_bun()
        for state in ['missing', 'stale', 'runtime']:
            with self.subTest(state=state):
                if state != 'missing':
                    (cache / 'commander').mkdir(parents=True, exist_ok=True)
                    (cache / 'commander/package.json').write_text('{}')
                    (cache / '.poteto-mode-tools-install-key').write_text('stale')
                env = dict(os.environ, PATH='' if state == 'runtime' else runtime)
                before = {str(p): p.read_bytes() for p in cache.rglob('*') if p.is_file()}
                result = self.bound('helper-ready', env=env)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('helper prerequisite held', result.stderr)
                self.assertIn({'missing': 'dependencies missing', 'stale': 'dependencies stale',
                               'runtime': 'Bun unavailable'}[state], result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertEqual(before, {str(p): p.read_bytes() for p in cache.rglob('*') if p.is_file()})

    def test_prepared_helper_readiness_is_bound_and_read_only(self):
        scripts = self.plugin / 'skills/hugues-mode/scripts'
        cache = scripts / 'node_modules'
        (cache / 'commander').mkdir(parents=True)
        (cache / 'commander/package.json').write_text('{}')
        key = hashlib.sha256((scripts / 'package.json').read_bytes() + b'\0' +
                             (scripts / 'bun.lock').read_bytes()).hexdigest()
        (cache / '.poteto-mode-tools-install-key').write_text(key + '\n')
        # Presence is checked, never execution: no runtime is required in the suite.
        result = self.bound('helper-ready', env=dict(os.environ, PATH=self.fake_bun()))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['install_key'], key)
        (scripts / 'package.json').write_text('{}')
        self.assertEqual(self.bound('helper-ready').returncode, 2)

    def test_claude_fragment_protects_payload_and_keeps_consumer_writable(self):
        result = self.bound('payload-policy', '--host', 'claude',
                            '--consumer', self.consumer, '--evidence', self.area)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertIn('Edit(/' + str(self.plugin) + '/**)', config['permissions']['deny'])
        sandbox = config['sandbox']
        self.assertTrue(sandbox['enabled'])
        self.assertTrue(sandbox['failIfUnavailable'])
        self.assertFalse(sandbox['allowUnsandboxedCommands'])
        self.assertEqual(sandbox['filesystem']['denyWrite'], [str(self.plugin)])
        self.assertIn(str(self.consumer), sandbox['filesystem']['allowWrite'])
        self.assertNotIn('allow', config['permissions'])

    def test_codex_fragment_extends_the_selected_policy_with_an_exact_carveout(self):
        result = self.bound('payload-policy', '--host', 'codex', '--parent', 'existing-policy',
                            '--consumer', self.consumer, '--evidence', self.area)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('default_permissions = "huguesstack-program"\n', result.stdout)
        self.assertIn('[permissions.huguesstack-program]\nextends = "existing-policy"\n', result.stdout)
        self.assertIn('[permissions.huguesstack-program.filesystem]\n', result.stdout)
        self.assertIn(json.dumps(str(self.plugin)) + ' = "read"\n', result.stdout)
        self.assertIn(json.dumps(str(self.consumer)) + ' = "write"\n', result.stdout)
        self.assertNotIn('network', result.stdout)

    def test_unsafe_policy_requests_hold_without_printing_configuration(self):
        for extra in [('--host', 'codex'),
                      ('--host', 'codex', '--parent', ':danger-full-access'),
                      ('--host', 'claude', '--consumer', self.plugin),
                      ('--host', 'claude', '--evidence', self.plugin / 'adapters')]:
            with self.subTest(extra=extra):
                result = self.bound('payload-policy', '--consumer', self.consumer,
                                    '--evidence', self.area, *extra)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, '')


class NativeDenialEvidence(unittest.TestCase):
    def test_shell_results_must_belong_to_the_actor_that_ran_the_exact_probe(self):
        inspect = runpy.run_path(str(ROOT / 'scripts/check_payload_boundary.py'))['shell_probes']
        results = dict.fromkeys(['append', 'create', 'rename', 'delete', 'chmod', 'alias', 'replace'], 'denied')
        request = {'parent_tool_use_id': 'worker-1', 'message': {'content': [
            {'type': 'tool_use', 'name': 'Bash', 'id': 'shell-1', 'input': {'command': 'python probe worker'}}]}}
        response = {'parent_tool_use_id': 'worker-1', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 'shell-1', 'content': json.dumps(results)}]}}
        self.assertEqual(inspect([request, response], 'claude', 'python probe worker'), {'worker-1'})
        for events in ([request], [response], [request, dict(response, parent_tool_use_id=None)]):
            self.assertEqual(inspect(events, 'claude', 'python probe worker'), set())
        self.assertEqual(inspect([request, response], 'claude', 'python probe coordinator'), set())
        execution = {'type': 'event_msg', 'payload': {'type': 'item_completed', 'item': {
            'type': 'CommandExecution', 'command': ['/bin/zsh', '-lc', 'python probe worker'],
            'status': 'completed', 'exit_code': 0, 'aggregated_output': json.dumps(results)}}}
        self.assertEqual(inspect([execution], 'codex', 'python probe worker'), {None})
        execution['payload']['item']['exit_code'] = 1
        self.assertEqual(inspect([execution], 'codex', 'python probe worker'), set())

    def test_model_claims_and_unpaired_results_are_not_native_denials(self):
        inspect = runpy.run_path(str(ROOT / 'scripts/check_payload_boundary.py'))['denied_edits']
        request = {'message': {'content': [{'type': 'tool_use', 'id': 'write-1',
                    'name': 'Write', 'input': {'file_path': '/fixture/plugin/file'}}]}}
        response = {'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'write-1',
                    'is_error': True, 'content': 'Permission denied'}]}}
        result = {'type': 'result', 'permission_denials': [{'tool_use_id': 'write-1',
                  'tool_name': 'Write', 'tool_input': {'file_path': '/fixture/plugin/file'}}]}
        self.assertEqual(inspect([request, response, result], 'claude'), {('/fixture/plugin/file', 'Write', None)})
        for events in ([request], [response], [request, response],
                       [{'type': 'assistant', 'text': 'Write was denied'}]):
            self.assertEqual(inspect(events, 'claude'), set())
        editor_error = {'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'write-1',
                        'is_error': True, 'content': 'String permission was not found in the file'}]}}
        self.assertEqual(inspect([request, editor_error], 'claude'), set())
        native_error = {'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'write-1',
                        'is_error': True, 'content': '<tool_use_error>File is in a directory that is denied by your permission settings.</tool_use_error>'}]}}
        notice = {'type': 'system', 'message': 'Permission to edit the fixture has been denied.'}
        self.assertEqual(inspect([notice, request, native_error, result], 'claude'),
                         {('/fixture/plugin/file', 'Write', None)})

    def test_codex_denial_requires_a_matching_native_patch_failure(self):
        inspect = runpy.run_path(str(ROOT / 'scripts/check_payload_boundary.py'))['denied_edits']
        request = {'payload': {'type': 'custom_tool_call', 'name': 'exec', 'call_id': 'patch-1',
                   'input': 'text(await tools.apply_patch("*** Update File: /fixture/plugin/file\\n"));'}}
        response = {'payload': {'type': 'custom_tool_call_output', 'call_id': 'patch-1',
                    'output': [{'type': 'input_text', 'text': 'Script error: patch rejected: writing outside of the project; rejected by user approval settings'}]}}
        self.assertEqual(inspect([request, response], 'codex'), {('/fixture/plugin/file', 'apply_patch', None)})
        for events in ([request], [response], [{'payload': {'type': 'message', 'text': 'patch rejected'}}]):
            self.assertEqual(inspect(events, 'codex'), set())
        printed = {'payload': dict(request['payload'], input=(
            'const sample = `tools.apply_patch(\\n*** Update File: /fixture/plugin/file\\n`; '
            'text("patch rejected: writing outside of the project; rejected by user approval settings");'))}
        self.assertEqual(inspect([printed, response], 'codex'), set())
        mismatch = {'payload': dict(response['payload'], output=[{'type': 'input_text',
                    'text': 'Script error: apply_patch verification failed: Failed to find expected lines:\n'
                            'patch rejected: writing outside of the project; rejected by user approval settings'}])}
        self.assertEqual(inspect([request, mismatch], 'codex'), set())


if __name__ == '__main__':
    unittest.main()
