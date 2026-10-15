"""Owner-reviewable configuration through the bound installed entrypoint."""
import json
from pathlib import Path
import runpy
import tomllib
import unittest

from test_host_adapters import InstalledFixture

ROOT = Path(__file__).resolve().parents[1]


class PayloadPolicy(InstalledFixture, unittest.TestCase):
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
        config = tomllib.loads(result.stdout)
        profile = config['permissions'][config['default_permissions']]
        self.assertEqual(profile['extends'], 'existing-policy')
        self.assertEqual(profile['filesystem'][str(self.plugin)], 'read')
        self.assertEqual(profile['filesystem'][str(self.consumer)], 'write')
        self.assertNotIn('network', profile)

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


if __name__ == '__main__':
    unittest.main()
