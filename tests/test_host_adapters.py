"""Actual installed entrypoints in external consumer repos; synthetic history only."""
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import NamedTuple
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugin/adapters'))
from runtime import activity


class InstalledFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-consumer-')
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name).resolve()
        self.plugin = self.area / 'installed plugin with spaces'
        shutil.copytree(ROOT / 'plugin', self.plugin, ignore=shutil.ignore_patterns('__pycache__'))
        self.consumer = self.area / 'consumer with spaces'
        self.consumer.mkdir()
        self.helper = self.plugin / 'adapters/host_tools.py'
        self.binding = self.area / 'binding.json'
        bound = self.run_tool('bind')
        self.assertEqual(bound.returncode, 0, bound.stderr)
        self.binding.write_text(bound.stdout)

    def run_tool(self, *args, **kwargs):
        return subprocess.run([sys.executable, str(self.helper), *map(str, args)],
                              cwd=self.consumer, capture_output=True, text=True, **kwargs)

    def bound(self, verb, *args, **kwargs):
        return self.run_tool(verb, '--binding', self.binding, *args, **kwargs)


class InstalledAdapters(InstalledFixture, unittest.TestCase):
    def test_installed_read_outside_plugin_without_git(self):
        source = 'skills/hugues-mode/playbooks/feature.md'
        self.assertFalse((self.plugin / '.git').exists())
        self.assertFalse((self.consumer / 'pstack').exists())
        result = self.bound('read-workflow', source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (self.plugin / source).read_text())

    def test_binding_is_revision_and_adapter_bound(self):
        data = json.loads(self.binding.read_text())
        self.assertEqual(data['revision'], 'hstack-native-v1')
        self.assertIn('adapters/runtime/activity.py', data['adapter_sha256'])
        self.assertEqual(data['plugin_root'], str(self.plugin))

    def test_workflow_drift_blocks_tick(self):
        path = self.plugin / 'skills/hugues-mode/playbooks/feature.md'
        path.write_text(path.read_text() + '\nchanged\n')
        result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
        self.assertEqual(result.returncode, 2)
        self.assertIn('workflow bytes/mode drift', result.stderr)

    def test_adapter_drift_blocks_tick(self):
        path = self.plugin / 'adapters/host.md'
        path.write_text(path.read_text() + '\nchanged\n')
        self.assertIn('drift', self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').stderr)

    def test_mode_drift_blocks_tick(self):
        path = self.plugin / 'skills/show-me-your-work/scripts/log.sh'
        path.chmod(0o644)
        self.assertEqual(self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').returncode, 2)

    def test_missing_installed_helper_blocks_validation(self):
        (self.plugin / 'skills/hugues-mode/scripts/check-plan.mjs').unlink()
        result = self.bound('plan-check', self.consumer / 'plan.md')
        self.assertEqual(result.returncode, 2)
        self.assertIn('missing installed payload', result.stderr)

    def test_manifest_drift_blocks_binding(self):
        (self.plugin / 'adapters/runtime/payload.json').write_text('{}')
        self.assertEqual(self.run_tool('bind').returncode, 2)

    def test_unknown_or_escaping_workflow_rejected(self):
        for path in ['../private.md', '/etc/passwd', 'pstack/skills/nope/SKILL.md', 'pstack/skills/swarm/../../private.md']:
            with self.subTest(path=path):
                self.assertEqual(self.bound('read-workflow', path).returncode, 2)

    def test_binding_does_not_follow_moved_installation(self):
        moved = self.area / 'replacement plugin'
        self.plugin.rename(moved)
        self.helper = moved / 'adapters/host_tools.py'
        self.assertEqual(self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').returncode, 2)

    def test_symlink_payload_rejected(self):
        source = self.plugin / 'skills/hugues-mode/playbooks/feature.md'
        saved = self.area / 'saved.md'
        source.rename(saved)
        source.symlink_to(saved)
        self.assertEqual(self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').returncode, 2)

    def test_translation_executes_bound_workflow_and_keeps_consumer_trunk(self):
        draft = self.consumer / 'draft.md'
        draft.write_text((ROOT / 'tests/fixtures/adapter-plan.md').read_text())
        result = self.bound('translate-plan', draft)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('git show origin/main:PLAN.md', result.stdout)
        self.assertNotIn('git show origin/main:pstack/', result.stdout)
        self.assertNotIn('node pstack/', result.stdout)
        command = next(line for line in result.stdout.splitlines() if 'read-workflow --binding' in line).strip('`')
        reread = subprocess.run(shlex.split(command), cwd=self.consumer, capture_output=True, text=True)
        self.assertEqual(reread.returncode, 0, reread.stderr)
        self.assertEqual(reread.stdout, (self.plugin / 'skills/hugues-mode/playbooks/feature.md').read_text())

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_translated_plan_passes_and_invalid_live_gate_fails(self):
        plan = self.consumer / 'plan with spaces.md'
        plan.write_text((ROOT / 'tests/fixtures/adapter-plan.md').read_text())
        translated = self.bound('translate-plan', plan)
        self.assertEqual(translated.returncode, 0, translated.stderr)
        plan.write_text(translated.stdout)
        valid = self.bound('plan-check', plan)
        self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)
        plan.write_text(plan.read_text().replace('**Verify, live.** Tests alone', '**Verify, live.** Tests suffice. Tests alone'))
        bad = self.bound('plan-check', plan)
        self.assertEqual(bad.returncode, 1)
        self.assertIn('Verify, live. does not open with the rule', bad.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_plan_check_holds_pstack_fixed_ten_lane_rule(self):
        plan = self.consumer / 'plan.md'
        ten = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
        # Frontmatter is skipped, as in pstack: no profile field selects another live rule.
        for text in [ten, '---\nverification_profile: custom\n---\n' + ten]:
            with self.subTest(plan=text[:40]):
                plan.write_text(text)
                result = self.bound('plan-check', plan)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('verify-live=10', result.stdout)
        extra = '- [ ] Lane 11. Extra. Save `lane-11.png`. Pass when visible.\n'
        for text, message in [
                (ten.replace('**Verify, perf.**', extra + '**Verify, perf.**'), 'expected 1 to 10'),
                (ten.replace('Ten lanes on', 'Risk-based lanes on'),
                 'Verify, live lacks "Ten lanes on `<swarm workers model>` at the PR head" with the model filled in')]:
            with self.subTest(message=message):
                plan.write_text(text)
                result = self.bound('plan-check', plan)
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_plan_check_accepts_verdict_without_contract_box(self):
        plan = self.consumer / 'plan.md'
        fixture = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
        self.assertEqual(fixture.count('### Verdict and merge\n### Boot recipe\n'), 1)
        # The Verdict and merge boxes of pstack 0.15.25's plan skeleton, renamed only.
        verdict = ('### Verdict and merge\n'
                   '- [ ] A full swarm runs once, at the code-ready head. Run each full swarm per the '
                   '`swarm` skill. One gates lane. The ten live lanes from the PR\'s **Verify, live** block.\n'
                   '- [ ] Clean only when every lane is `PASS`. Findings go back to the owner.\n'
                   '### Boot recipe\n')
        text = fixture.replace('### Verdict and merge\n### Boot recipe\n', verdict)
        self.assertIn('- [ ] Clean only when every lane is `PASS`.', text)
        for marker in ['verification-contract', 'plan-compare', 'operator ruling']:
            self.assertNotIn(marker, text)
        plan.write_text(text)
        result = self.bound('plan-check', plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('1 PR sections, 0 problems', result.stdout)

    def test_missing_node_is_explicit_block(self):
        result = self.bound('plan-check', self.consumer / 'plan.md', env=dict(os.environ, PATH=''))
        self.assertEqual(result.returncode, 2)
        self.assertIn('Node unavailable', result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_plan_check_identifies_gitless_install_and_ignores_consumer_decoy(self):
        plan = self.consumer / 'plan.md'
        plan.write_text((ROOT / 'tests/fixtures/adapter-plan.md').read_text())
        decoy = self.consumer / 'skills/hugues-mode/scripts/check-plan.mjs'
        decoy.parent.mkdir(parents=True)
        decoy.write_text('console.error("CONSUMER DECOY"); process.exit(99);\n')
        subprocess.run(['git', 'init', '-q', str(self.consumer)], check=True)
        subprocess.run(['git', '-C', str(self.consumer), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.consumer), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'consumer'], check=True)
        result = self.bound('plan-check', plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        identity = json.loads(result.stderr.splitlines()[0])
        self.assertEqual(identity['checker_path'], str(self.plugin / 'skills/hugues-mode/scripts/check-plan.mjs'))
        self.assertEqual(identity['plugin_commit'], None)
        self.assertEqual(identity['payload_sha256'], json.loads(self.binding.read_text())['payload_sha256'])
        self.assertEqual(identity['checker_sha256'], hashlib.sha256(
            (self.plugin / 'skills/hugues-mode/scripts/check-plan.mjs').read_bytes()).hexdigest())
        self.assertIn('1 PR sections, 0 problems', result.stdout)
        self.assertNotIn('CONSUMER DECOY', result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_plan_check_identifies_tracked_plugin_on_failure(self):
        subprocess.run(['git', 'init', '-q', str(self.area)], check=True)
        subprocess.run(['git', '-C', str(self.area), 'add', self.plugin.name], check=True)
        subprocess.run(['git', '-C', str(self.area), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'plugin'], check=True)
        commit = subprocess.check_output(['git', '-C', str(self.area), 'rev-parse', 'HEAD'], text=True).strip()
        plan = self.consumer / 'plan.md'
        plan.write_text('# Invalid plan\n')
        result = self.bound('plan-check', plan)
        self.assertEqual(result.returncode, 1, result.stderr)
        identity = json.loads(result.stderr.splitlines()[0])
        self.assertEqual(identity['plugin_commit'], commit)
        self.assertEqual(identity['checker_path'], str(self.plugin / 'skills/hugues-mode/scripts/check-plan.mjs'))
        self.assertIn('no "## Program checklist" section', result.stderr)

    def test_withdrawn_verbs_are_unknown(self):
        for verb in ['payload-policy', 'helper-ready', 'program-check', 'artifact-hash',
                     'decode-design', 'worker-run', 'run-control', 'run-wait', 'plan-compare']:
            with self.subTest(verb=verb):
                result = self.bound(verb)
                self.assertEqual(result.returncode, 2)
                self.assertIn('invalid choice', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_bun_helper_setup_holds_unwritable_installation(self):
        tools = ' '.join((ROOT / 'plugin/adapters/host-helper-setup.md').read_text().split())
        setup = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        for host in ['.claude', '.codex']:
            self.assertIn(f'{host}/plugins/cache/hstack/hstack/<loaded-version>/skills/hugues-mode/scripts', tools)
        for contract in [
                'cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile',
                'bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help',
                'node_modules/commander/package.json',
                'node_modules/.poteto-mode-tools-install-key',
                'SHA-256 of package.json, a NUL byte, and bun.lock',
                'owner-approved', 'cache is not writable', 'hold the dependent step',
                'Report the exact expanded setup command as the gap',
                'Do not retry the helper or silently skip the step']:
            with self.subTest(contract=contract):
                self.assertIn(contract, tools)
        self.assertIn('[helper setup](host-helper-setup.md) in full', setup)
        workflow = ' '.join((ROOT / 'plugin/adapters/host-workflow-tools.md').read_text().split())
        for contract in [
                '[helper setup](host-helper-setup.md) in full',
                'Missing runtimes, dependencies, cloud workers, forge APIs or loop primitives',
                'hold their operation, preserve its intended gate and report the gap',
                'Native local workers substitute for cloud only where the core permits local execution',
                'Never simulate a race sequentially']:
            with self.subTest(contract=contract):
                self.assertIn(contract, workflow)

    def test_public_bridges_route_actual_adapter(self):
        for name in ['multi-phase-plan', 'autopilot-full', 'autopilot-stack']:
            self.assertIn('read-workflow', (self.plugin / f'skills/hugues-mode/playbooks/{name}.md').read_text())
        cleanup = (self.plugin / 'skills/hugues-mode/playbooks/worktree-cleanup.md').read_text()
        self.assertIn('host_tools.py worktree-audit', cleanup)
        self.assertIn('separate active/pinned-chat gate', cleanup)


class SyntheticActivity(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='hstack-synthetic-history-')
        self.addCleanup(temp.cleanup)
        self.area = Path(temp.name).resolve()
        self.wt = self.area / 'worktree with spaces'
        self.other = Path(str(self.wt) + '-sibling')
        self.now = datetime.now(timezone.utc).timestamp()
        self.stamp = datetime.fromtimestamp(self.now, timezone.utc).isoformat()

    def scan(self, provider, rows, **kwargs):
        source = self.area / (provider + '.jsonl')
        source.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        manifest = {'coverage': 'complete', 'sources': [{'provider': provider, 'files': [str(source)],
                    'authorization': 'task-owned synthetic fixtures only', 'coverage': 'complete'}]}
        manifest.update(kwargs)
        return activity.scan(manifest, [self.wt, self.other], self.now)

    def claude(self, **kwargs):
        row = {'type': 'assistant', 'timestamp': self.stamp, 'cwd': str(self.wt),
               'message': {'content': [{'type': 'tool_use', 'name': 'Read', 'input': {'file_path': 'README.md'}}]}}
        row.update(kwargs)
        return row

    def codex(self, **kwargs):
        row = {'type': 'response_item', 'timestamp': self.stamp,
               'payload': {'type': 'function_call', 'name': 'exec_command',
                           'arguments': json.dumps({'cmd': 'cat README.md', 'workdir': str(self.wt)})}}
        row.update(kwargs)
        return row

    def cursor(self, **kwargs):
        """One Cursor assistant record, in the shape Cursor's own store writes.

        A Cursor record carries no `cwd` and no record-level timestamp, so the
        fixture names an absolute path and the reader's recency comes from the
        transcript file's mtime.
        """
        row = {'role': 'assistant',
               'message': {'content': [{'type': 'tool_use', 'name': 'Read',
                                        'input': {'path': str(self.wt / 'README.md')}}]}}
        row.update(kwargs)
        return row

    def test_claude_native_cwd_and_relative_read(self):
        hits, _, complete = self.scan('claude', [self.claude()])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.wt)][0]['recent'])

    def test_codex_function_arguments_without_session_meta(self):
        hits, _, complete = self.scan('codex', [self.codex()])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.wt)][0]['recent'])

    def test_cursor_absolute_read_is_seen_and_recency_comes_from_file_mtime(self):
        hits, reports, complete = self.scan('cursor', [self.cursor()])
        # The source reads cleanly, so its own coverage is complete, but a
        # Cursor source can never make the scan's coverage complete.
        self.assertEqual(reports[0]['coverage'], 'complete')
        self.assertFalse(complete)
        self.assertTrue(hits[str(self.wt)][0]['recent'])
        self.assertEqual(hits[str(self.wt)][0]['timestamp_basis'], 'file-mtime-conservative')

    def test_cursor_relative_path_without_working_directory_holds(self):
        row = {'role': 'assistant',
               'message': {'content': [{'type': 'tool_use', 'name': 'Read',
                                        'input': {'path': 'README.md'}}]}}
        hits, reports, complete = self.scan('cursor', [row])
        self.assertFalse(complete)
        self.assertEqual(reports[0]['coverage'], 'unavailable')

    def test_a_cursor_shell_command_resolves_its_absolute_paths(self):
        # A relative path resolves against the operation's working directory,
        # and an absolute one resolves on its own. Both are seen, and neither
        # holds the source's coverage.
        cases = [
            (shlex.join(['cat', 'README.md']), str(self.wt)),
            (shlex.join(['cat', str(self.wt / 'README.md')]), str(self.wt)),
        ]
        for command, working_directory in cases:
            with self.subTest(command=command):
                row = {'role': 'assistant',
                       'message': {'content': [{'type': 'tool_use', 'name': 'Shell',
                                                'input': {'command': command,
                                                          'working_directory': working_directory}}]}}
                hits, reports, complete = self.scan('cursor', [row])
                self.assertEqual(reports[0]['coverage'], 'complete')
                self.assertFalse(complete)
                self.assertTrue(hits[str(self.wt)])

    def test_cursor_unreviewed_record_shapes_hold(self):
        cases = [
            {'role': 'assistant', 'message': {'content': [{'type': 'tool_result', 'text': 'plain'}]}},
            {'role': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read'}]}},
            {'role': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read', 'input': {'path': 17}}]}},
            {'role': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read',
                                                           'input': {'path': str(self.wt), 'unknown': 'field'}}]}},
            {'role': 'system', 'message': {'content': [{'type': 'text', 'text': 'plain'}]}},
            {'role': 'assistant', 'message': {'content': []}},
            {'role': 'assistant', 'message': {'content': 'plain'}},
            {'type': 'turn_started', 'status': 'success'},
            {'type': 'turn_ended', 'status': 'unknown'},
            {'type': 'turn_ended', 'status': 'success', 'error': 17},
        ]
        for row in cases:
            with self.subTest(row=row):
                self.assertFalse(self.scan('cursor', [row])[2])

    def test_cursor_turn_markers_and_text_blocks_are_supported(self):
        # A text-only chat reads cleanly, so the source's own coverage is
        # complete. The scan's coverage stays incomplete, because a Cursor
        # source can never claim it.
        rows = [{'role': 'user', 'message': {'content': [{'type': 'text', 'text': 'hello'}]}},
                {'role': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'hi'}]}},
                {'type': 'turn_ended', 'status': 'success'}]
        hits, reports, complete = self.scan('cursor', rows)
        self.assertFalse(complete)
        self.assertEqual(reports[0]['coverage'], 'complete')
        self.assertEqual(reports[0]['limits'],
                         'cursor: no cwd, no tool results, recency is file mtime')

    def test_cursor_missing_tool_result_states_its_limit(self):
        # Cursor's transcript carries no tool result, so the reader cannot see
        # what a tool touched or returned. That limit is stated in the report.
        row = {'role': 'assistant',
               'message': {'content': [{'type': 'tool_use', 'name': 'Read',
                                        'input': {'path': str(self.wt / 'README.md')}}]}}
        hits, reports, complete = self.scan('cursor', [row])
        self.assertFalse(complete)
        self.assertEqual(reports[0]['limits'],
                         'cursor: no cwd, no tool results, recency is file mtime')

    def test_a_cursor_operation_without_an_absolute_path_holds(self):
        # A Cursor record carries no working directory, so an operation that
        # names no absolute path cannot be resolved and holds the coverage.
        cases = [
            ('Shell', {'command': 'ls'}),
            ('Shell', {'command': 'pwd'}),
            ('Grep', {'pattern': 'needle'}),
            ('Glob', {'glob_pattern': '**/*.py'}),
        ]
        for name, args in cases:
            with self.subTest(tool=name, args=args):
                row = {'role': 'assistant',
                       'message': {'content': [{'type': 'tool_use', 'name': name, 'input': args}]}}
                hits, reports, complete = self.scan('cursor', [row])
                self.assertFalse(complete)
                self.assertEqual(reports[0]['coverage'], 'unavailable')

    def test_an_observed_cursor_tool_that_touches_no_file_is_inert(self):
        # These tools are reviewed shapes, so they neither contribute a path
        # nor hold the source's coverage.
        for name, args in [('GetDynamicTools', {'namespace': 'x'}),
                           ('CallDynamicTool', {'namespace': 'x', 'toolName': 'y'}),
                           ('AskQuestion', {'questions': []}),
                           ('ask_question', {'questions': []}),
                           ('AwaitShell', {'namespace': 'x', 'toolName': 'y'}),
                           ('UpdateCurrentStep', {})]:
            with self.subTest(tool=name):
                row = {'role': 'assistant',
                       'message': {'content': [{'type': 'tool_use', 'name': name, 'input': args}]}}
                hits, reports, complete = self.scan('cursor', [row])
                self.assertEqual(reports[0]['coverage'], 'complete', name)
                self.assertFalse(complete, name)

    def test_the_observed_cursor_shell_keys_are_accepted(self):
        for extra in [{'timeout': 30}, {'request_permissions': ['all']},
                      {'request_smart_mode_approval': True,
                       'smart_mode_block_reason': 'because'}]:
            with self.subTest(extra=extra):
                args = {'command': shlex.join(['cat', str(self.wt / 'README.md')]),
                        'working_directory': str(self.wt)}
                args.update(extra)
                row = {'role': 'assistant',
                       'message': {'content': [{'type': 'tool_use', 'name': 'Shell', 'input': args}]}}
                hits, reports, complete = self.scan('cursor', [row])
                self.assertEqual(reports[0]['coverage'], 'complete', extra)
                self.assertTrue(hits[str(self.wt)])

    def test_an_unknown_cursor_provider_is_an_error_not_a_silent_skip(self):
        source = self.area / 'other.jsonl'
        source.write_text(json.dumps(self.cursor()) + '\n')
        manifest = {'coverage': 'complete',
                    'sources': [{'provider': 'other', 'files': [str(source)],
                                 'authorization': 'synthetic only', 'coverage': 'complete'}]}
        hits, reports, complete = activity.scan(manifest, [self.wt], self.now)
        self.assertFalse(complete)
        self.assertEqual(reports[0]['coverage'], 'unavailable')
        self.assertIn('unsupported transcript provider', reports[0]['error'])

    def test_a_record_with_an_undecodable_encoding_is_still_read(self):
        # The owner's real store carries a shell command with a git date format,
        # `--format='%h %ad %s'`. `%ad` is not valid percent-encoding. The raw
        # text is still searched, so the record is read rather than holding the
        # whole source.
        row = {'role': 'assistant',
               'message': {'content': [
                   {'type': 'text', 'text': "the format is --format='%h %ad %s'"},
                   {'type': 'tool_use', 'name': 'Shell',
                    'input': {'command': 'cat ' + str(self.wt / 'README.md'),
                              'description': 'read',
                              'working_directory': str(self.wt)}}]}}
        hits, reports, complete = self.scan('cursor', [row])
        self.assertEqual(reports[0].get('error'), None, reports[0])
        self.assertEqual(reports[0]['coverage'], 'complete', reports[0])

    def test_a_redacted_real_cursor_transcript_reads_without_holding(self):
        # The fixtures are the owner's real chats with every value replaced.
        # A real help chat and a real Shell chat must both read as reviewed
        # records, so a real transcript is not mistaken for an unreadable one.
        for name in ['cursor-help.jsonl', 'cursor-shell.jsonl']:
            with self.subTest(fixture=name):
                source = self.area / name
                source.write_text((ROOT / 'tests/fixtures/cursor' / name).read_text())
                manifest = {'coverage': 'complete',
                            'sources': [{'provider': 'cursor', 'files': [str(source)],
                                         'authorization': 'redacted real transcripts',
                                         'coverage': 'complete'}]}
                hits, reports, complete = activity.scan(manifest, [self.wt], self.now)
                self.assertEqual(reports[0].get('error'), None, reports[0])
                self.assertEqual(reports[0]['coverage'], 'complete', reports[0])
                self.assertFalse(complete, reports[0])

    def test_the_observed_cursor_tool_keys_do_not_hold_a_real_chat(self):
        # The review found that 4 of the owner's 9 real transcripts came back
        # unavailable, because the reader rejected tool arguments Cursor
        # actually writes. The observed keys are accepted, so a real chat
        # reads instead of holding its source. The tool names come from the
        # owner's own store.
        source = self.area / 'real.jsonl'
        source.write_text((ROOT / 'tests/fixtures/cursor/cursor-shell.jsonl').read_text())
        manifest = {'coverage': 'complete',
                    'sources': [{'provider': 'cursor', 'files': [str(source)],
                                 'authorization': 'redacted real transcripts',
                                 'coverage': 'complete'}]}
        hits, reports, complete = activity.scan(manifest, [self.wt], self.now)
        self.assertEqual(reports[0].get('error'), None, reports[0])
        self.assertEqual(reports[0]['files_scanned'], 1)

    def test_codex_session_context_relative_operation(self):
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md'})})
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        hits, _, complete = self.scan('codex', [meta, row])
        self.assertTrue(complete)
        self.assertEqual(len(hits[str(self.wt)]), 2)



    def test_exact_boundary_excludes_sibling_prefix(self):
        hits, _, complete = self.scan('codex', [self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md', 'workdir': str(self.other)})})])
        self.assertTrue(complete)
        self.assertFalse(hits[str(self.wt)])
        self.assertTrue(hits[str(self.other)])

    def test_old_record_not_overridden_by_fresh_file_mtime(self):
        old = datetime.fromtimestamp(self.now - 6 * 86400, timezone.utc).isoformat()
        hits, _, complete = self.scan('claude', [self.claude(timestamp=old)])
        self.assertTrue(complete)
        self.assertFalse(hits[str(self.wt)][0]['recent'])

    def test_future_timestamp_is_conservative_recent(self):
        hits, _, complete = self.scan('claude', [self.claude(timestamp=self.now + 86400)])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.wt)][0]['recent'])

    def test_missing_sources_and_partial_coverage_hold(self):
        self.assertFalse(activity.scan({'coverage': 'complete', 'sources': []}, [self.wt], self.now)[2])
        self.assertFalse(self.scan('claude', [self.claude()], coverage='partial')[2])

    def test_unsupported_envelope_and_bad_timestamp_hold(self):
        for row in [self.claude(type='unknown'), self.claude(timestamp='not-a-time'),
                    self.claude(timestamp=[]), self.claude(cwd=['bad']), self.claude(message='bad')]:
            with self.subTest(row=row):
                self.assertFalse(self.scan('claude', [row])[2])

    def test_relative_operation_without_context_holds(self):
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md'})})
        self.assertFalse(self.scan('codex', [row])[2])
        row = self.claude(cwd=None)
        self.assertFalse(self.scan('claude', [row])[2])
        for cmd in ['pwd', 'ls', 'cat']:
            row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd})})
            self.assertFalse(self.scan('codex', [row])[2])

    def test_malformed_encoded_arguments_hold(self):
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': '{unfinished'})
        self.assertFalse(self.scan('codex', [row])[2])

    def test_supported_hosts_and_nested_subagents_are_scanned(self):
        sources = []
        for provider, row in [('claude', self.claude()), ('codex', self.codex()),
                              ('cursor', self.cursor())]:
            root = self.area / provider
            child = root / 'subagents' / 'nested.jsonl'
            child.parent.mkdir(parents=True)
            child.write_text(json.dumps(row) + '\n')
            sources.append({'provider': provider, 'root': str(root), 'authorization': 'synthetic only', 'coverage': 'complete'})
        hits, reports, complete = activity.scan({'coverage': 'complete', 'sources': sources}, [self.wt], self.now)
        # The Cursor source caps the scan's coverage: its records carry no
        # working directory and no tool results, so it can never make the
        # scan complete on its own.
        self.assertFalse(complete)
        self.assertEqual({r['provider'] for r in hits[str(self.wt)]}, {'claude', 'codex', 'cursor'})
        self.assertEqual(sum(r['files_scanned'] for r in reports), 3)

    def test_empty_and_missing_roots_both_hold(self):
        root = self.area / 'empty'
        root.mkdir()
        manifest = {'coverage': 'complete', 'sources': [{'provider': 'claude', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}]}
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])
        root.rmdir()
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])

    def test_permission_error_and_malformed_json_hold(self):
        with patch.object(activity, 'read_selected', side_effect=PermissionError('synthetic denied')):
            self.assertFalse(self.scan('claude', [self.claude()])[2])
        path = self.area / 'malformed.jsonl'
        path.write_text('{unfinished')
        manifest = {'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])

    def test_symlink_source_cannot_escape_authorized_root(self):
        root = self.area / 'root'
        root.mkdir()
        (root / 'escape.jsonl').symlink_to(self.area / 'outside.jsonl')
        manifest = {'coverage': 'complete', 'sources': [{'provider': 'claude', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}]}
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])

    def test_missing_selected_file_and_partial_source_hold(self):
        manifest = {'coverage': 'complete', 'sources': [{'provider': 'codex', 'files': [str(self.area / 'missing.jsonl')], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])
        root = self.area / 'partial'
        root.mkdir()
        manifest['sources'][0] = {'provider': 'codex', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'partial'}
        self.assertFalse(activity.scan(manifest, [self.wt], self.now)[2])

    def test_absolute_alias_context_is_normalized(self):
        self.wt.mkdir()
        alias = self.area / 'alias'
        alias.symlink_to(self.wt, target_is_directory=True)
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md', 'workdir': str(alias)})})
        hits, _, complete = self.scan('codex', [row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.wt)])

    def test_incomplete_record_after_recent_activity_still_holds(self):
        hits, _, complete = self.scan('claude', [self.claude(), {'type': 'new-unknown-format'}])
        self.assertTrue(hits[str(self.wt)])
        self.assertFalse(complete)
        self.assertEqual(activity.classify('clean', 'NONE', True, complete, True), 'hold-activity-unavailable')

    def test_codex_shell_relative_sibling_path(self):
        cmd = shlex.join(['cat', '../' + self.other.name + '/README.md'])
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
        hits, _, complete = self.scan('codex', [row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_claude_shell_relative_sibling_path(self):
        cmd = shlex.join(['cat', '../' + self.other.name + '/README.md'])
        row = self.claude(message={'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': cmd}}]})
        hits, _, complete = self.scan('claude', [row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_native_patch_relative_sibling_path(self):
        patch_text = '*** Begin Patch\n*** Update File: ../' + self.other.name + '/README.md\n@@\n-old\n+new\n*** End Patch'
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        row = {'type': 'response_item', 'timestamp': self.stamp, 'payload': {'type': 'custom_tool_call', 'name': 'apply_patch', 'input': patch_text}}
        hits, _, complete = self.scan('codex', [meta, row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_missing_or_nonobject_function_arguments_hold_with_session_context(self):
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        for payload in [{'type': 'function_call', 'name': 'exec_command'},
                        {'type': 'function_call', 'name': 'exec_command', 'arguments': '[]'},
                        {'type': 'function_call', 'name': 'exec_command', 'arguments': '{}'}]:
            self.assertFalse(self.scan('codex', [meta, self.codex(payload=payload)])[2])

    def test_opaque_shell_commands_hold(self):
        for cmd in ['cat "$TARGET"', 'cat ../*', 'cat README.md && cat elsewhere', 'python arbitrary.py']:
            row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
            self.assertFalse(self.scan('codex', [row])[2])

    def test_shell_parent_directory_and_attached_git_path(self):
        for cmd in ['ls ..', shlex.join(['git', '-C../' + self.other.name, 'status'])]:
            row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
            hits, _, complete = self.scan('codex', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_malformed_source_members_return_unavailable(self):
        for entry in [[], None, 'invalid', 3]:
            manifest = {'coverage': 'complete', 'sources': [entry]}
            _, reports, complete = activity.scan(manifest, [self.wt], self.now)
            self.assertFalse(complete)
            self.assertIn('source entry must be an object', reports[0]['error'])

    def test_missing_claude_tool_input_holds(self):
        row = self.claude(message={'content': [{'type': 'tool_use', 'name': 'Read'}]})
        self.assertFalse(self.scan('claude', [row])[2])

    def test_unsupported_host_is_ignored_without_reading_or_coverage(self):
        ignored = {'provider': 'omp', 'root': '/not-authorized/not-read', 'coverage': 'complete'}
        with patch.object(activity, 'read_selected', side_effect=AssertionError('must not read unsupported host')):
            hits, reports, complete = activity.scan({'coverage': 'complete', 'sources': [ignored]}, [self.wt], self.now)
        self.assertFalse(complete)
        self.assertFalse(hits[str(self.wt)])
        self.assertEqual(reports[0]['coverage'], 'ignored')
        root = self.area / 'authorized empty host'
        root.mkdir()
        supported = {'provider': 'claude', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}
        with patch.object(activity, 'read_selected', side_effect=AssertionError('empty root has no file reads')):
            self.assertFalse(activity.scan({'coverage': 'complete', 'sources': [ignored, supported]}, [self.wt], self.now)[2])

    def test_nested_progress_and_unknown_claude_blocks_hold(self):
        nested = self.claude(type='progress', data={'type': 'agent_progress', 'message': self.claude()})
        self.assertFalse(self.scan('claude', [nested])[2])
        unknown = self.claude(message={'content': [{'type': 'tool_call', 'name': 'Bash', 'input': {'command': 'cat ../sibling/README.md'}}]})
        self.assertFalse(self.scan('claude', [unknown])[2])

    def test_relative_workdir_and_each_claude_tool_context(self):
        deep = self.area / 'tools/deep'
        relative_target = '../../' + self.other.name + '/README.md'
        meta = {'type': 'session_meta', 'payload': {'cwd': str(self.wt)}, 'timestamp': self.stamp}
        call = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['cat', relative_target]), 'workdir': '../tools/deep'})})
        hits, _, complete = self.scan('codex', [meta, call])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])
        row = self.claude(message={'content': [
            {'type': 'tool_use', 'name': 'Bash', 'input': {'command': shlex.join(['cat', relative_target]), 'cwd': str(deep)}},
            {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': 'README.md', 'cwd': str(self.wt)}}]})
        hits, _, complete = self.scan('claude', [row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_chained_git_directories_use_effective_context(self):
        deep = self.area / 'tools/deep'
        cmd = shlex.join(['git', '-C', str(deep), '-C', '../../' + self.other.name, 'status'])
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
        hits, _, complete = self.scan('codex', [row])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_codex_message_blocks_require_supported_content_schema(self):
        payloads = [
            {'type': 'message', 'role': 'assistant'},
            {'type': 'message', 'role': 'assistant', 'content': 'malformed'},
            {'type': 'message', 'role': 'assistant', 'content': [{'type': 'tool_call', 'path': '../sibling'}]},
            {'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text'}]}]
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        for payload in payloads:
            self.assertFalse(self.scan('codex', [meta, self.codex(payload=payload)])[2])
        row = self.codex(payload={'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': str(self.other)}]})
        self.assertTrue(self.scan('codex', [meta, row])[2])
        self.assertFalse(self.scan('codex', [{'type': 'session_meta', 'payload': {}}])[2])

    def test_claude_file_inputs_require_real_tool_fields_and_types(self):
        cases = [('Read', {'path': str(self.wt)}), ('Read', {'file_path': str(self.wt), 'offset': 'bad'}),
                 ('Glob', {'path': str(self.wt), 'pattern': 123}), ('Write', {'file_path': str(self.wt), 'content': 123}),
                 ('Edit', {'file_path': str(self.wt)}), ('Read', {'file_path': str(self.wt), 'extra': 'unknown'})]
        for name, args in cases:
            row = self.claude(message={'content': [{'type': 'tool_use', 'name': name, 'input': args}]})
            self.assertFalse(self.scan('claude', [row])[2])
        self.assertFalse(self.scan('claude', [self.claude(message={'content': [{'type': 'text'}]})])[2])

    def test_embedded_sed_program_is_opaque_and_holds(self):
        cmd = shlex.join(['sed', '-n', '1r ../' + self.other.name + '/README.md', 'README.md'])
        row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
        self.assertFalse(self.scan('codex', [row])[2])

    def test_claude_nested_tool_results_require_text_leaf_schema(self):
        cases = [[17], [{'type': 'text'}], [{'type': 'text', 'text': 42}],
                 [{'type': 'file_reference', 'path': '../sibling/README.md'}],
                 [{'type': 'image', 'source': {'type': 'base64', 'data': 'synthetic'}}],
                 [{'type': 'tool_result', 'tool_use_id': 'nested', 'content': []}],
                 [{'type': 'text', 'text': 'plain', 'unknown': '../sibling'}]]
        for content in cases:
            with self.subTest(content=content):
                row = self.claude(message={'content': [{'type': 'tool_result', 'tool_use_id': 'fixture', 'content': content}]})
                _, reports, complete = self.scan('claude', [row])
                self.assertFalse(complete)
                self.assertEqual(reports[0]['coverage'], 'unavailable')
                self.assertEqual(activity.classify('clean', 'NONE', True, complete, False), 'hold-activity-unavailable')

    def test_claude_tool_result_strings_and_text_leaves_preserve_evidence(self):
        for content in [str(self.other), [{'type': 'text', 'text': str(self.other)}]]:
            row = self.claude(message={'content': [{'type': 'tool_result', 'tool_use_id': 'fixture', 'content': content}]})
            hits, _, complete = self.scan('claude', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_codex_outputs_require_identified_string_content(self):
        for kind in ['function_call_output', 'custom_tool_call_output']:
            cases = [{'type': kind, 'call_id': 'fixture'},
                     {'type': kind, 'call_id': 'fixture', 'output': 17},
                     {'type': kind, 'call_id': 'fixture', 'output': [{'type': 'file_reference', 'path': '../sibling'}]},
                     {'type': kind, 'output': 'plain'},
                     {'type': kind, 'call_id': '', 'output': 'plain'},
                     {'type': kind, 'call_id': 'fixture', 'output': 'plain', 'unknown': '../sibling'}]
            for payload in cases:
                with self.subTest(payload=payload):
                    self.assertFalse(self.scan('codex', [self.codex(payload=payload)])[2])

    def test_codex_string_outputs_preserve_sibling_activity(self):
        for kind in ['function_call_output', 'custom_tool_call_output']:
            row = self.codex(payload={'type': kind, 'call_id': 'fixture', 'output': str(self.other)})
            hits, _, complete = self.scan('codex', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_nonoperative_envelopes_require_reviewed_text_schemas(self):
        for provider, row in [('claude', self.claude(unknown={'type': 'file_reference', 'path': '../sibling'})),
                              ('codex', self.codex(unknown={'type': 'file_reference', 'path': '../sibling'})),
                              ('claude', self.claude(message={'content': [], 'usage': {'unknown': '../sibling'}}))]:
            self.assertFalse(self.scan(provider, [row])[2])
        for kind in ['system', 'file-history-snapshot', 'queue-operation']:
            self.assertFalse(self.scan('claude', [self.claude(type=kind)])[2])
        for row in [self.claude(type='summary', summary=17),
                    {'type': 'summary', 'summary': 'plain', 'unknown': {'type': 'file_reference', 'path': '../sibling'}},
                    self.claude(message={'content': [{'type': 'redacted_thinking', 'data': 'opaque'}]}),
                    self.claude(message={'content': [{'type': 'tool_result', 'tool_use_id': 'fixture', 'content': 'plain', 'is_error': 17}]}),
                    self.claude(message={'content': [{'type': 'text', 'text': 'plain', 'unknown': '../sibling'}]})]:
            self.assertFalse(self.scan('claude', [row])[2])
        for kind in ['session_meta', 'turn_context']:
            for extra in [{'unknown': {'type': 'file_reference', 'path': '../sibling'}},
                          {'instructions': [17]}, {'git': {'unknown': '../sibling'}}]:
                row = {'type': kind, 'payload': dict(extra, cwd=str(self.wt))}
                self.assertFalse(self.scan('codex', [row])[2])
        for payload in [{'type': 'reasoning'}, {'type': 'reasoning', 'summary': [17]},
                        {'type': 'reasoning', 'summary': [{'type': 'summary_text'}]},
                        {'type': 'reasoning', 'summary': [], 'encrypted_content': 'opaque'},
                        {'type': 'reasoning', 'summary': [], 'content': [{'type': 'unknown'}]},
                        {'type': 'web_search_call'}]:
            self.assertFalse(self.scan('codex', [self.codex(payload=payload)])[2])
        for payload in [{'type': 'agent_message'}, {'type': 'agent_reasoning', 'text': 17},
                        {'type': 'user_message', 'message': 'plain', 'images': ['opaque']},
                        {'type': 'token_count'}, {'type': 'task_started'}]:
            row = {'type': 'event_msg', 'timestamp': self.stamp, 'payload': payload}
            self.assertFalse(self.scan('codex', [row])[2])

    def test_reviewed_text_summaries_reasoning_and_events_preserve_evidence(self):
        row = self.claude(uuid='fixture', isSidechain=False, message={'role': 'assistant', 'content': [{'type': 'text', 'text': str(self.other)}], 'usage': {'input_tokens': 0, 'output_tokens': 1}})
        self.assertTrue(self.scan('claude', [row])[0][str(self.other)])
        row = {'type': 'summary', 'timestamp': self.stamp, 'summary': str(self.other)}
        self.assertTrue(self.scan('claude', [row])[0][str(self.other)])
        row = self.codex(payload={'type': 'reasoning', 'summary': [{'type': 'summary_text', 'text': str(self.other)}], 'content': [{'type': 'reasoning_text', 'text': 'plain'}], 'encrypted_content': None})
        self.assertTrue(self.scan('codex', [row])[0][str(self.other)])
        for payload in [{'type': 'agent_message', 'message': str(self.other)},
                        {'type': 'agent_reasoning', 'text': str(self.other)},
                        {'type': 'user_message', 'message': str(self.other), 'images': [], 'local_images': []}]:
            row = {'type': 'event_msg', 'timestamp': self.stamp, 'payload': payload}
            hits, _, complete = self.scan('codex', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_patch_grammar_holds_unconsumed_directives_and_retains_known_paths(self):
        target = '../' + self.other.name + '/README.md'
        invalid = [
            '*** Add File: harmless\n*** UnsupportedOperation: ' + target,
            '*** Update File: ' + target + '\n@@\n-old\n+new\n*** UnsupportedOperation: elsewhere',
            '*** Add File: ' + target + '\nunprefixed content',
            '*** Delete File: ' + target + '\n+unexpected body',
            '*** Update File: ' + target + '\n@@',
            '*** Move to: ' + target,
            '*** Update File: ' + target + '\n*** Move to: moved\n*** Move to: duplicate\n@@\n-old\n+new']
        for body in invalid:
            row = self.codex(payload={'type': 'custom_tool_call', 'name': 'apply_patch', 'cwd': str(self.wt), 'input': '*** Begin Patch\n' + body + '\n*** End Patch'})
            self.assertFalse(self.scan('codex', [row])[2])
        row['payload']['input'] = '*** Begin Patch\n*** Update File: ' + target + '\n@@\n-old\n+new\n*** UnsupportedOperation: elsewhere\n*** End Patch'
        hits, _, complete = self.scan('codex', [row])
        self.assertFalse(complete)
        self.assertEqual(hits[str(self.other)][0]['evidence_basis'], 'unparsed-path-hint')
        for body in ['*** Add File: ' + target + '\n+fixture',
                     '*** Delete File: ' + target,
                     '*** Update File: ' + target + '\n*** Move to: renamed\n@@\n-old\n+new\n*** End of File']:
            row['payload']['input'] = '*** Begin Patch\n' + body + '\n*** End Patch'
            self.assertTrue(self.scan('codex', [row])[2])

    def test_codex_operation_cwd_never_changes_persistent_session_context(self):
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        call = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['cat', '../' + self.other.name + '/README.md'])})})
        operations = [
            self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'cwd': str(self.area / 'tools/deep'), 'arguments': json.dumps({'cmd': 'pwd'})}),
            self.codex(payload={'type': 'function_call_output', 'call_id': 'fixture', 'cwd': str(self.area / 'tools/deep'), 'output': 'plain'})]
        hits, _, complete = self.scan('codex', [meta, *operations, call])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])
        turn = {'type': 'turn_context', 'timestamp': self.stamp, 'payload': {'cwd': str(self.other)}}
        plain = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md'})})
        hits, _, complete = self.scan('codex', [meta, turn, *operations, plain])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])

    def test_unknown_before_valid_and_mixed_blocks_retain_hints_under_hold(self):
        unknown = {'type': 'unknown', 'timestamp': self.stamp}
        valid = self.claude(cwd=str(self.other))
        for rows in [[unknown, valid], [valid, unknown]]:
            hits, reports, complete = self.scan('claude', rows)
            self.assertFalse(complete)
            self.assertEqual(reports[0]['coverage'], 'unavailable')
            self.assertTrue(hits[str(self.other)])
            self.assertEqual(hits[str(self.other)][0]['evidence_basis'], 'validated-record')
        mixed = self.claude(message={'content': [{'type': 'text', 'text': str(self.other)}, {'type': 'unknown'}]})
        hits, _, complete = self.scan('claude', [mixed])
        self.assertFalse(complete)
        self.assertEqual(hits[str(self.other)][0]['evidence_basis'], 'unparsed-path-hint')

    def test_unavailable_file_does_not_suppress_other_authorized_file_hints(self):
        missing, valid = self.area / 'missing.jsonl', self.area / 'valid.jsonl'
        valid.write_text(json.dumps(self.claude(cwd=str(self.other))) + '\n')
        manifest = {'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(missing), str(valid)], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        hits, reports, complete = activity.scan(manifest, [self.other], self.now)
        self.assertFalse(complete)
        self.assertEqual(reports[0]['files_scanned'], 1)
        self.assertTrue(hits[str(self.other)])

    def test_opaque_record_invalidates_relative_context_until_reviewed_context_resets(self):
        meta = {'type': 'session_meta', 'timestamp': self.stamp, 'payload': {'cwd': str(self.wt)}}
        unknown = {'type': 'event_msg', 'payload': {'type': 'unknown'}}
        call = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['cat', '../' + self.other.name + '/README.md'])})})
        hits, _, complete = self.scan('codex', [meta, unknown, call])
        self.assertFalse(complete)
        self.assertFalse(hits[str(self.other)])
        hits, _, complete = self.scan('codex', [meta, unknown, meta, call])
        self.assertFalse(complete)
        self.assertEqual(hits[str(self.other)][0]['evidence_basis'], 'validated-record')

    def test_literal_shell_forms_hold_opaque_options_and_nonstandard_program_paths(self):
        for cmd in ['rg --pre arbitrary-script token README.md', 'rg --pre=arbitrary-script token README.md',
                    '/unreviewed/bin/cat README.md', 'head --unknown README.md', 'head -n bad README.md']:
            row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
            self.assertFalse(self.scan('codex', [row])[2])
        for cmd in [shlex.join(['/bin/cat', '--', '../' + self.other.name + '/README.md']),
                    shlex.join(['head', '-n', '2', '../' + self.other.name + '/README.md']),
                    shlex.join(['rg', '-n', 'token', '../' + self.other.name + '/README.md'])]:
            row = self.codex(payload={'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.wt)})})
            hits, _, complete = self.scan('codex', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])



    def test_no_recent_evidence_is_distinct_from_unavailable(self):
        hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.other))])
        self.assertTrue(complete)
        self.assertFalse(hits[str(self.wt)])

    def test_classification_retains_wip_pr_and_active_pinned_gates(self):
        expected = [
            ('wip:1', 'NONE', True, True, False, 'hold-wip'),
            ('clean', 'OPEN', True, True, False, 'hold-open-pr'),
            ('clean', 'NONE', True, False, False, 'hold-activity-unavailable'),
            ('clean', 'NONE', True, True, True, 'verify-recent-chat'),
            ('clean', 'NONE', True, True, False, 'verify-active-pinned'),
            ('clean', 'UNKNOWN', True, True, False, 'hold-metadata-unavailable'),
            ('clean', 'NONE', None, True, False, 'hold-metadata-unavailable'),
            ('scratch:1', 'NONE', True, True, False, 'review-scratch')]
        for *args, bucket in expected:
            self.assertEqual(activity.classify(*args), bucket)


class ConsumerAudit(InstalledFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Synthetic Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.consumer / 'README.md').write_text('fixture\n')
        self.git('add', 'README.md')
        self.git('commit', '-m', 'fixture')
        self.wt = self.area / 'scratch worktree with spaces'
        self.git('worktree', 'add', '-b', 'scratch', str(self.wt))
        self.sources = self.area / 'sources.json'
        self.prs = self.area / 'prs.json'
        self.prs.write_text(json.dumps({'coverage': 'complete', 'states': {'main': 'NONE', 'scratch': 'NONE'}}))

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.consumer), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def audit(self, manifest, *args):
        self.sources.write_text(json.dumps(manifest))
        result = self.bound('worktree-audit', '--repo', self.consumer, '--sources', self.sources,
                            '--pr-snapshot', self.prs, '--base', 'main', *args)
        return result, json.loads(result.stdout)

    def test_cli_missing_source_holds_clean_merged_worktree(self):
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': []})
        self.assertEqual(result.returncode, 2)
        row = next(r for r in report['worktrees'] if r['worktree'] == str(self.wt))
        self.assertEqual(row['bucket'], 'hold-activity-unavailable')
        self.assertFalse(row['deletion_authorized'])

    def test_cli_each_native_provider_recent_activity(self):
        stamp = datetime.now(timezone.utc).isoformat()
        rows = {'claude': {'type': 'assistant', 'timestamp': stamp, 'cwd': str(self.wt), 'message': {'content': []}},
                'codex': {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': 'cat README.md', 'workdir': str(self.wt)})}}}
        for provider, record in rows.items():
            with self.subTest(provider=provider):
                path = self.area / (provider + '.jsonl')
                path.write_text(json.dumps(record) + '\n')
                manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': provider, 'files': [str(path)], 'authorization': 'synthetic only', 'coverage': 'complete'}]}
                result, report = self.audit(manifest)
                self.assertEqual(result.returncode, 0, result.stderr)
                row = next(r for r in report['worktrees'] if r['worktree'] == str(self.wt))
                self.assertEqual(row['bucket'], 'verify-recent-chat')
                self.assertEqual(row['evidence'][0]['provider'], provider)
                self.assertFalse(report['network_used'])
                self.assertFalse(report['deletion_performed'])
                self.assertTrue(self.wt.exists())

    def test_cli_empty_activity_holds_before_pinned_gate(self):
        root = self.area / 'empty transcripts'
        root.mkdir()
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'root': str(root), 'authorization': 'synthetic empty root', 'coverage': 'complete'}]})
        self.assertEqual(result.returncode, 2)
        row = next(r for r in report['worktrees'] if r['worktree'] == str(self.wt))
        self.assertEqual(row['activity'], 'unavailable')
        self.assertEqual(row['bucket'], 'hold-activity-unavailable')
        self.assertEqual(row['active_pinned_gate'], 'required-separately')
        self.assertFalse(row['deletion_authorized'])

    def test_cli_relative_sibling_shell_and_patch_activity(self):
        stamp = datetime.now(timezone.utc).isoformat()
        cmd = shlex.join(['cat', '../' + self.wt.name + '/README.md'])
        patch_text = '*** Begin Patch\n*** Update File: ../' + self.wt.name + '/README.md\n@@\n-fixture\n+fixture\n*** End Patch'
        cases = [
            ('claude', [{'type': 'assistant', 'timestamp': stamp, 'cwd': str(self.consumer), 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': cmd}}]}}]),
            ('codex', [{'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': cmd, 'workdir': str(self.consumer)})}}]),
            ('codex', [{'type': 'session_meta', 'timestamp': stamp, 'payload': {'cwd': str(self.consumer)}},
                       {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'custom_tool_call', 'name': 'apply_patch', 'input': patch_text}}])]
        for provider, records in cases:
            path = self.area / 'relative.jsonl'
            path.write_text('\n'.join(json.dumps(row) for row in records) + '\n')
            result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': provider, 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report['worktrees'][1]['bucket'], 'verify-recent-chat')
            self.assertTrue(self.wt.exists())

    def test_cli_malformed_source_and_function_arguments_hold(self):
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [[]]})
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
        path = self.area / 'missing-arguments.jsonl'
        stamp = datetime.now(timezone.utc).isoformat()
        rows = [{'type': 'session_meta', 'timestamp': stamp, 'payload': {'cwd': str(self.consumer)}},
                {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command'}}]
        path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'codex', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')

    def test_cli_untracked_scratch_and_tracked_wip_are_retained(self):
        root = self.area / 'empty transcripts'
        root.mkdir()
        (root / 'old.jsonl').write_text(json.dumps({'type': 'summary', 'summary': 'old unrelated fixture', 'timestamp': '2020-01-01T00:00:00Z'}) + '\n')
        manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}]}
        (self.wt / 'scratch.txt').write_text('untracked')
        _, report = self.audit(manifest)
        self.assertEqual(report['worktrees'][1]['bucket'], 'review-scratch')
        (self.wt / 'README.md').write_text('tracked edit')
        _, report = self.audit(manifest)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-wip')

    def test_cli_unsupported_host_is_ignored_and_cannot_supply_supported_host_coverage(self):
        ignored = {'provider': 'omp', 'files': ['/not-authorized/not-read.jsonl'], 'coverage': 'complete'}
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [ignored]})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['sources'][0]['coverage'], 'ignored')
        self.assertEqual(report['sources'][0]['files_scanned'], 0)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
        root = self.area / 'empty supported history'
        root.mkdir()
        (root / 'old.jsonl').write_text(json.dumps({'type': 'event_msg', 'timestamp': '2020-01-01T00:00:00Z', 'payload': {'type': 'agent_message', 'message': 'old unrelated fixture'}}) + '\n')
        supported = {'provider': 'codex', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [ignored, supported]})
        self.assertEqual(result.returncode, 0)
        self.assertFalse(report['worktrees'][1]['evidence'])

    def test_cli_supported_host_contexts_and_nested_progress_hold(self):
        stamp = datetime.now(timezone.utc).isoformat()
        deep = self.area / 'tools/deep'
        relative_target = '../../' + self.wt.name + '/README.md'
        calls = [
            {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['cat', relative_target]), 'workdir': '../tools/deep'})},
            {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['git', '-C', str(deep), '-C', '../../' + self.wt.name, 'status']), 'workdir': str(self.consumer)})}]
        path = self.area / 'context.jsonl'
        for payload in calls:
            rows = [{'type': 'session_meta', 'timestamp': stamp, 'payload': {'cwd': str(self.consumer)}},
                    {'type': 'response_item', 'timestamp': stamp, 'payload': payload}]
            path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
            result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'codex', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report['worktrees'][1]['bucket'], 'verify-recent-chat')
        nested = {'type': 'progress', 'timestamp': stamp, 'cwd': str(self.consumer), 'data': {'type': 'agent_progress', 'message': {'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': shlex.join(['cat', '../' + self.wt.name + '/README.md'])}}]}}}}
        path.write_text(json.dumps(nested) + '\n')
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')

    def test_cli_malformed_native_messages_files_and_sed_hold(self):
        stamp = datetime.now(timezone.utc).isoformat()
        cases = [
            ('codex', [{'type': 'session_meta', 'timestamp': stamp, 'payload': {'cwd': str(self.consumer)}},
                       {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'message', 'role': 'assistant', 'content': [{'type': 'unknown_operation', 'command': 'cat ../sibling/README.md'}]}}]),
            ('claude', [{'type': 'assistant', 'timestamp': stamp, 'cwd': str(self.consumer), 'message': {'content': [{'type': 'tool_use', 'name': 'Read', 'input': {'path': str(self.consumer)}}]}}]),
            ('codex', [{'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['sed', '-n', '1r ../' + self.wt.name + '/README.md', 'README.md']), 'workdir': str(self.consumer)})}}])]
        path = self.area / 'invalid-native-inputs.jsonl'
        for provider, rows in cases:
            path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
            result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': provider, 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]})
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(report['coverage'], 'unavailable')
            self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')

    def test_cli_nested_claude_tool_result_schema_holds_and_valid_text_detects_sibling(self):
        path = self.area / 'nested-tool-result.jsonl'
        stamp = datetime.now(timezone.utc).isoformat()
        cases = [[42], [{'type': 'text'}], [{'type': 'unknown', 'path': '../' + self.wt.name}],
                 [{'type': 'image', 'source': {'data': 'synthetic'}}]]
        manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        for content in cases:
            row = {'type': 'user', 'timestamp': stamp, 'cwd': str(self.consumer), 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'fixture', 'content': content}]}}
            path.write_text(json.dumps(row) + '\n')
            result, report = self.audit(manifest)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(report['coverage'], 'unavailable')
            self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
            self.assertFalse(report['worktrees'][1]['deletion_authorized'])
        row['message']['content'][0]['content'] = [{'type': 'text', 'text': str(self.wt / 'README.md')}]
        path.write_text(json.dumps(row) + '\n')
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['worktrees'][1]['bucket'], 'verify-recent-chat')
        self.assertFalse(report['worktrees'][1]['deletion_authorized'])

    def test_cli_codex_output_and_nonoperative_schemas_hold_with_valid_text_control(self):
        stamp = datetime.now(timezone.utc).isoformat()
        path = self.area / 'tool-outputs.jsonl'
        manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'codex', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        cases = [
            {'type': 'response_item', 'payload': {'type': 'function_call_output', 'call_id': 'fixture'}},
            {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'call_id': 'fixture', 'output': 17}},
            {'type': 'response_item', 'payload': {'type': 'function_call_output', 'call_id': 'fixture', 'output': [{'type': 'file_reference', 'path': '../' + self.wt.name}]}},
            {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [], 'encrypted_content': 'opaque'}},
            {'type': 'event_msg', 'payload': {'type': 'agent_message'}}]
        for row in cases:
            path.write_text(json.dumps(dict(row, timestamp=stamp)) + '\n')
            result, report = self.audit(manifest)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(report['coverage'], 'unavailable')
            self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
            self.assertFalse(report['worktrees'][1]['deletion_authorized'])
        for kind in ['function_call_output', 'custom_tool_call_output']:
            row = {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': kind, 'call_id': 'fixture', 'output': str(self.wt / 'README.md')}}
            path.write_text(json.dumps(row) + '\n')
            result, report = self.audit(manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report['worktrees'][1]['bucket'], 'verify-recent-chat')

    def test_cli_session_scope_and_partial_patch_hints_never_promote_coverage(self):
        stamp = datetime.now(timezone.utc).isoformat()
        path = self.area / 'scope-and-patch.jsonl'
        manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'codex', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]}
        meta = {'type': 'session_meta', 'timestamp': stamp, 'payload': {'cwd': str(self.consumer)}}
        unrelated = {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command', 'cwd': str(self.area / 'tools/deep'), 'arguments': json.dumps({'cmd': 'pwd'})}}
        call = {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call', 'name': 'exec_command', 'arguments': json.dumps({'cmd': shlex.join(['cat', '../' + self.wt.name + '/README.md'])})}}
        path.write_text('\n'.join(json.dumps(row) for row in [meta, unrelated, call]) + '\n')
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['worktrees'][1]['bucket'], 'verify-recent-chat')
        patch = {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'custom_tool_call', 'name': 'apply_patch', 'cwd': str(self.consumer), 'input': '*** Begin Patch\n*** Add File: ../' + self.wt.name + '/fixture.txt\n+fixture\n*** UnsupportedOperation: elsewhere\n*** End Patch'}}
        valid = {'type': 'response_item', 'timestamp': stamp, 'payload': {'type': 'function_call_output', 'call_id': 'fixture', 'output': str(self.wt)}}
        path.write_text('\n'.join(json.dumps(row) for row in [patch, valid]) + '\n')
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(report['coverage'], 'unavailable')
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
        self.assertEqual({row['evidence_basis'] for row in report['worktrees'][1]['evidence']}, {'unparsed-path-hint', 'validated-record'})
        self.assertFalse(report['worktrees'][1]['deletion_authorized'])


HOST_PAGE_ROWS = ['Detect', 'Sessions and worktrees', 'Start', 'Send', 'Read', 'Wait', 'Close',
                  'Load a PR head', 'Allowed tools', 'Skip line']
SKIP_LINE = re.compile(r'Skipped in .+: .+\. .+\.')
HostPage = NamedTuple('HostPage', [('listing', str), ('skip_only', list)])
HOST_PAGES = {
    'orca.md': HostPage(listing='ADEs', skip_only=['worker_done', 'orchestration']),
    'cursor.md': HostPage(listing='Agents', skip_only=[]),
}
HARNESS_MEMBER = 'pstack/docs/harness/claude-code.md'

# Upstream first-column cells that hStack states elsewhere or does not need, keyed by the upstream
# table that holds them so a cell dropped in one table cannot hide the same cell in another.
DROPPED = {
    'Tools': {
        '`Task`': 'host-workers.md opens with the Task to native agent tool translation',
        'Run another pstack skill (`/name` or "the **name** skill")':
            'host.md Loading and routing owns the read-by-path rule and bars the Skill tool for user-only skills',
    },
    'Subagent fields': {
        '`subagent_type: generalPurpose`':
            'the readonly rows map a generalPurpose worker by its readonly flag, the false row also with no readonly field',
        '`poteto-agent`, `comment-sicko`': 'host-workers.md names hstack:hugues-agent and hugues-comment-sicko',
    },
    'Models': {
        '`auto` or `inherit-parent`': 'host-workers.md Model defaults omit model for an inherit-parent role',
        'The `pstack-models.mdc` rule, `~/.cursor/rules/pstack-models.mdc`': 'setup-hstack writes project-local .hstack/models.md',
        'A role value `<model> <effort>`, such as `opus high`':
            'the Models row maps a role value such as claude-opus-5-5 xhigh, and host-workers.md passes the effort token',
    },
    'Paths': {
        '`.cursor/skills/`, `~/.cursor/skills/`': 'host-special-skills.md Project skill paths',
        '`~/.cursor/plugins/`, `.cursor-plugin/plugin.json`':
            'host-special-skills.md:31-32 maps skill paths to the actual host, and hStack ships native manifests',
        '`.cursor/rules/*.mdc`, always-applied rules': 'no hStack body reads .mdc rules',
        '`https://github.com/cursor/plugins/blob/main/pstack/<path>`': 'no hStack body links Cursor\'s repository',
        'Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/`':
            'plugin/skills/recall/SKILL.md states the Cursor transcript path and both slug forms, '
            'and plugin/adapters/runtime/activity.py reads that provider',
    },
    'Cursor-only features': {
        'Cursor cloud agents':
            'the Subagent fields row for environment "cloud" maps it, and a step that needs the agent itself is Cursor-only',
    },
}
# Upstream rows hStack leaves open, each with the reason it cannot be closed here.
GAPS = {}


def table_rows(text):
    tables, heading, rows = {}, None, None
    for line in text.splitlines() + ['']:
        if line.startswith('#'):
            heading = line.lstrip('#').strip()
        if line.startswith('|'):
            if rows is None:
                rows = []
            rows.append([cell.strip() for cell in line.strip().strip('|').split('|')])
        elif rows is not None:
            tables.setdefault(heading, []).extend(rows[2:])
            rows = None
    return tables


def markdown_tables(text):
    return {name: [row[0] for row in rows] for name, rows in table_rows(text).items()}


def unmapped_upstream_rows(upstream, adapters, dropped, gaps):
    mine = {}
    for text in adapters:
        for name, cells in markdown_tables(text).items():
            mine.setdefault(name, set()).update(cells)
    return [f'{name}: {cell}' for name, cells in markdown_tables(upstream).items() for cell in cells
            if cell not in mine.get(name, set()) and cell not in dropped.get(name, {}) and cell not in gaps.get(name, {})]


def with_extra_row(text, heading, row):
    separator = '| --- | --- |\n'
    at = text.index(separator, text.index(f'## {heading}\n')) + len(separator)
    return text[:at] + row + '\n' + text[at:]


def host_page_errors(text, skip_only=()):
    cells = [row for rows in table_rows(text).values() for row in rows]
    rows = [row[0] for row in cells]
    errors = [] if rows == HOST_PAGE_ROWS else [f'rows {rows} are not {HOST_PAGE_ROWS}']
    if not SKIP_LINE.search(text):
        errors.append('no skip line')
    skip = ' '.join(row[1] for row in cells if row[0] == 'Skip line')
    for word in skip_only:
        if word not in skip or word in text.replace(skip, ''):
            errors.append(f'{word} is not only in the skip line')
    return errors


def host_index_errors(readme, pages):
    lists = readme.split('## Agents', 1)[1]
    listed = set(re.findall(r'^- \[[^\]]+\]\(([^)/]+\.md)\)', lists, re.M))
    return sorted([*('listed but missing: ' + name for name in listed - set(pages)),
                   *('missing from the index: ' + name for name in set(pages) - listed)])


class HostAdapterShape(unittest.TestCase):
    def pinned_harness_doc(self, archive=None):
        pin = json.loads((ROOT / 'docs/upstream/pin.json').read_text())
        archive = archive or ROOT / f"provenance/upstream/pstack-{pin['version']}.tar.gz"
        with tarfile.open(archive) as tar:
            return tar.extractfile(HARNESS_MEMBER).read().decode()

    def adapters(self):
        return [(ROOT / f'plugin/adapters/{name}').read_text() for name in ('host.md', 'host-workers.md')]

    def row(self, table, first):
        rows = [row for text in self.adapters() for row in table_rows(text).get(table, []) if row[0] == first]
        self.assertEqual(len(rows), 1, f'{table}: {first}')
        return rows[0]

    def test_upstream_harness_rows_are_mapped(self):
        upstream = self.pinned_harness_doc()
        with self.subTest('every upstream row is mapped, dropped or a recorded gap'):
            self.assertEqual(unmapped_upstream_rows(upstream, self.adapters(), DROPPED, GAPS), [])
        cells = markdown_tables(upstream)
        for table, reasons in [*DROPPED.items(), *GAPS.items()]:
            self.assertEqual(set(reasons) - set(cells.get(table, [])), set(), f'{table} lists a cell upstream lacks')
            self.assertTrue(all(reasons.values()))
        with tempfile.TemporaryDirectory(prefix='hstack-harness-') as directory:
            for label, heading, row, expected in [
                    ('extra upstream row', 'Subagent fields', '| `brand_new_field: <x>` | `brand_new_value` |',
                     'Subagent fields: `brand_new_field: <x>`'),
                    ('a row dropped in another table', 'Cursor-only features', '| `Task` | `Agent` |',
                     'Cursor-only features: `Task`'),
                    ('a gap in another table', 'Tools', '| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | x |',
                     'Tools: Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/`')]:
                changed = with_extra_row(upstream, heading, row)
                self.assertNotEqual(changed, upstream)
                archive = Path(directory) / 'pstack.tar.gz'
                with tarfile.open(archive, 'w:gz') as tar:
                    info = tarfile.TarInfo(HARNESS_MEMBER)
                    info.size = len(changed.encode())
                    tar.addfile(info, io.BytesIO(changed.encode()))
                with self.subTest(label):
                    errors = unmapped_upstream_rows(self.pinned_harness_doc(archive), self.adapters(), DROPPED, GAPS)
                    self.assertEqual(errors, [expected])

        workers = ' '.join(self.adapters()[1].split())
        with self.subTest('readonly precedence'):
            claude = self.row('Subagent fields', '`readonly: true`')[1]
            for phrase in ['`subagent_type: "general-purpose"`', '`"Explore"`', 'locate or search code', '`how` explorer',
                           '"do not edit files"', "`git status` in the worker's checkout"]:
                self.assertIn(phrase, claude)
            self.assertLess(claude.index('general-purpose'), claude.index('Explore'))
            self.assertTrue(self.row('Subagent fields', '`readonly: false`')[1].startswith('`subagent_type: "general-purpose"`'))
        with self.subTest('every generalPurpose call in the skills has a row'):
            shapes = {}
            for path in sorted((ROOT / 'plugin/skills').rglob('*.md')):
                for line in path.read_text().splitlines():
                    if 'generalPurpose`' in line:
                        readonly = next((value for value in ('true', 'false') if f'`readonly: {value}`' in line), None)
                        shapes.setdefault(readonly, []).append(path.relative_to(ROOT).as_posix())
            self.assertEqual(set(shapes), {'true', 'false', None})
            for readonly, paths in shapes.items():
                claude = self.row('Subagent fields', f'`readonly: {readonly or "false"}`')[1]
                self.assertIn('`subagent_type: "general-purpose"`', claude, paths)
                if readonly is None:
                    self.assertIn('also for `generalPurpose` without `readonly`', claude, paths)
        with self.subTest('one model rule'):
            claude = self.row('Models', 'A `grok-*`, `gpt-*`, or other non-Claude slug')[1]
            self.assertIn('the ` or ` rule above applies', claude)
            self.assertIn('the Workers line names the model that ran', claude)
            self.assertNotIn('Omit `model`', claude)
            self.assertIn("setup-hstack's ` or ` rule picks first: the first alternative the native tool accepts, "
                          "else `inherit-parent` at the first alternative's effort. A skill's own fallback to its default "
                          'applies only if the tool then rejects the value that rule picked.', workers)
            self.assertNotIn("Preserve each core skill's fallback sequence", workers)
            self.assertIn('The Workers line records the requested and actual family/model/effort.', workers)
            self.assertIn('A seat needs a family only when its workflow requires one and no alternative on its line is '
                          'accepted: mark the seat blocked', workers)
            self.assertNotIn('If no allowed equivalent is exposed', workers)
            self.assertNotIn('If a seat needs a family the host cannot', workers)
        with self.subTest('the Claude model row is the starting value'):
            claude = self.row('Models', '`claude-<family>-<version>-<effort>[-fast]`, such as `claude-opus-5-5-xhigh`')[1]
            for phrase in ['`model: "opus"` while the Agent tool takes only aliases', '`effort: "xhigh"` to start',
                           '"Match the model to the job" may lower with a reported reason',
                           'So does a role value `claude-opus-5-5 xhigh`.', 'Drop `-fast`.']:
                self.assertIn(phrase, claude)
            setup = ' '.join((ROOT / 'plugin/skills/setup-hstack/SKILL.md').read_text().split())
            self.assertIn("When Claude Code's Agent tool accepts only aliases for `model`, pass the ID's alias", setup)
            self.assertIn('**Match the model to the job.**', workers)
        with self.subTest('a generalPurpose worker maps by its readonly flag'):
            self.assertNotIn("Cursor's `generalPurpose` maps to", workers)
            self.assertNotIn('preserve `generalPurpose`', workers)
            self.assertIn("preserve the workflow's own prompt, readonly/agent-mode requirement", workers)
            self.assertIn("Do not replace these workers with `hugues-agent`. Codex uses a fresh native worker with the "
                          "workflow's prompt.", workers)
        with self.subTest('resume sends the result text'):
            row = self.row('Subagent fields', '`resume`')
            self.assertIn("the earlier result's text pasted whole into its brief", row[1])
            self.assertIn('`SendMessage` in the cases `hugues-mode/SKILL.md` allows', row[1])
            self.assertTrue(row[2].startswith('Same; '), row[2])
            self.assertIn('its message tool is unobserved', row[2])
            router = (ROOT / 'plugin/skills/hugues-mode/SKILL.md').read_text()
            self.assertIn('Resume, message, or queue a follow-up on an existing subagent only when', router)
        with self.subTest('the drop rule spares the fields the Agent tool lists'):
            self.assertIn('If a Cursor-only field has no row, drop it and say so.', workers)
            for field in ['subagent_type', 'model', 'effort', 'run_in_background', 'isolation']:
                self.assertIn(f'`{field}`', workers.split('Never drop ', 1)[1].split('. ', 1)[0])
            self.assertEqual(self.row('Subagent fields', '`run_in_background: true`')[1], 'Pass it.')
            self.assertIn('no such field', self.row('Subagent fields', '`environment: "local"`')[1])
        with self.subTest('cloud keeps the local-execution limit and the worktree location'):
            claude = self.row('Subagent fields', '`environment: "cloud"`')[1]
            for phrase in ['`isolation: "worktree"`', 'only where the core permits local execution',
                           "AGENTS.md sets a worktree location, the coordinator creates the worktree there before dispatch "
                           'and omits `isolation`', 'The brief names the branch.']:
                self.assertIn(phrase, claude)
            tools = ' '.join((ROOT / 'plugin/adapters/host-workflow-tools.md').read_text().split())
            self.assertIn('Native local workers substitute for cloud only where the core permits local execution', tools)

    def test_host_pages_follow_the_page_shape_and_the_index_lists_them(self):
        directory = ROOT / 'plugin/adapters/hosts'
        readme = (directory / 'README.md').read_text()
        self.assertLessEqual(len(readme.encode()), 1750)
        self.assertIn(', '.join(HOST_PAGE_ROWS), readme)
        pages = sorted(path.name for path in directory.glob('*.md') if path.name != 'README.md')
        self.assertEqual(host_index_errors(readme, pages), [])
        for name in pages:
            with self.subTest(page=name):
                self.assertIn(name, HOST_PAGES)
                host_page = HOST_PAGES[name]
                self.assertEqual(host_page_errors((directory / name).read_text(), host_page.skip_only), [])
                section = readme.split(f'## {host_page.listing}\n', 1)[1].split('\n## ', 1)[0]
                self.assertIn(f']({name}):', section)
        with self.subTest('the ADE rule is stated once, and the door names the tests the README repeats'):
            adr = (ROOT / 'docs/adr/0004-adapters-for-ades-and-agents.md').read_text()
            sentence = 'A page never creates or reads the ADE'
            self.assertEqual(readme.count(sentence), 1)
            self.assertEqual(adr.count(sentence), 0)
            self.assertIn('hosts/README.md#shared-ade-rule', adr)
            self.assertIn('settlement receipts', readme)
            workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()
            door = next(line for line in workers.splitlines() if '(hosts/README.md)' in line)
            for test in ['ORCA_TERMINAL_HANDLE', 'ORCA_PANE_KEY', 'ORCA_TAB_ID',
                         '`t3-code` tools', 'omp']:
                self.assertIn(test, door)
                self.assertIn(test, readme)
            self.assertIn('[host-workers.md](../host-workers.md) sends you here', readme)
        with self.subTest('the index and the ADR name what the door reads and where it can miss'):
            for limit in ['Unobserved: omp matches at dispatch, not its first tool call',
                          "Codex's `shell_environment_policy` may strip `ORCA_TERMINAL_HANDLE` in Orca",
                          'Every process an Orca pane starts inherits it.']:
                self.assertIn(limit, readme)
            self.assertIn('reads at most the index, never a page', adr)
            self.assertIn('host.md, which every session reads, carries none of it', adr)
            self.assertNotIn('gets one row in its phase table', adr)
            self.assertNotIn('never reads a file under', adr)
        def page(rows, skip='Skipped in Example: step. Reason.'):
            return '# Example\n\n| Row | Mechanics |\n|---|---|\n' + ''.join(
                f'| {row} | {skip if row == "Skip line" else "x"} |\n' for row in rows)

        swapped = [*HOST_PAGE_ROWS[:2], HOST_PAGE_ROWS[3], HOST_PAGE_ROWS[2], *HOST_PAGE_ROWS[4:]]
        listing = '## Agents\n\n- [One](one.md): test\n\n## ADEs\n\n- [Two](two.md): test\n'
        for label, errors, expected in [
                ('a complete page', host_page_errors(page(HOST_PAGE_ROWS)), []),
                ('a missing row', host_page_errors(page(HOST_PAGE_ROWS[:6] + HOST_PAGE_ROWS[7:])), ['rows ']),
                ('rows out of order', host_page_errors(page(swapped)), ['rows ']),
                ('no skip line', host_page_errors(page(HOST_PAGE_ROWS, skip='none')), ['no skip line']),
                ('a skip-only word in the skip line', host_page_errors(page(HOST_PAGE_ROWS), ['step']), []),
                ('a skip-only word outside the skip line',
                 host_page_errors(page(HOST_PAGE_ROWS) + 'Use step.\n', ['step']), ['step is not only']),
                ('a skip-only word missing', host_page_errors(page(HOST_PAGE_ROWS), ['inbox']), ['inbox is not only']),
                ('an exact index', host_index_errors(listing, ['one.md', 'two.md']), []),
                ('a page the index omits', host_index_errors(listing, ['one.md', 'two.md', 'three.md']),
                 ['missing from the index: three.md']),
                ('a listed page that is missing', host_index_errors(listing, ['one.md']), ['listed but missing: two.md'])]:
            with self.subTest(label):
                self.assertEqual(len(errors), len(expected), errors)
                for error, prefix in zip(errors, expected):
                    self.assertTrue(error.startswith(prefix), error)


class HostDetectionHook(unittest.TestCase):
    """The SessionStart hook that detects an ADE, and the written check it backs up.

    Prose could not make the door reliable: across rounds 2 to 4 of PR 142 a
    session read the index in 2 of 6 Orca runs, and the runs that skipped it never
    mentioned Orca at all. The hook does the test where the session cannot miss
    it. The written check stays, because Codex and omp load no plugin hook.
    """
    HOOK = ROOT / 'plugin/hooks/host-detect.sh'
    MANIFEST = ROOT / 'plugin/hooks/hooks.json'
    # The three Orca variables observed set in a real pane on Orca 1.4.241.
    ORCA_VARIABLES = ('ORCA_TERMINAL_HANDLE', 'ORCA_PANE_KEY', 'ORCA_TAB_ID')

    def run_hook(self, env=None, root=None):
        environment = dict(os.environ)
        for name in self.ORCA_VARIABLES:
            environment[name] = ''
        environment.update(env or {})
        environment['CLAUDE_PLUGIN_ROOT'] = str(root or ROOT / 'plugin')
        return subprocess.run([str(self.HOOK)], capture_output=True, text=True,
                              env=environment)

    def context(self, result):
        return json.loads(result.stdout)['hookSpecificOutput']['additionalContext']

    def test_the_manifest_declares_one_session_start_command_hook(self):
        manifest = json.loads(self.MANIFEST.read_text())
        self.assertIn('SessionStart', manifest['hooks'])
        entries = manifest['hooks']['SessionStart']
        self.assertEqual(len(entries), 1)
        hooks = entries[0]['hooks']
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0]['type'], 'command')
        self.assertIn('host-detect.sh', hooks[0]['command'])
        self.assertIn('${CLAUDE_PLUGIN_ROOT}', hooks[0]['command'])
        # The command runs the script directly, so the executable bit is
        # load-bearing. A `bash` wrapper would make the mode a dead pin.
        self.assertNotIn('bash', hooks[0]['command'])
        self.assertGreaterEqual(hooks[0]['timeout'], 1)

    def test_the_hook_script_is_sealed_and_executable(self):
        receipt = json.loads((ROOT / 'docs/upstream/consolidation.json').read_text())
        for relative in ('hooks/hooks.json', 'hooks/host-detect.sh'):
            with self.subTest(path=relative):
                self.assertIn(relative, receipt['installed_files'])
        mode = receipt['installed_files']['hooks/host-detect.sh']['mode']
        self.assertEqual(mode, 0o755, 'the hook script must be executable')
        self.assertEqual(receipt['installed_files']['hooks/hooks.json']['mode'], 0o644)
        self.assertTrue((ROOT / 'plugin/hooks/host-detect.sh').is_file())

    def test_a_plain_session_gets_no_output_and_no_bytes(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, '')

    def test_each_orca_variable_alone_triggers_the_door(self):
        for name in self.ORCA_VARIABLES:
            with self.subTest(variable=name):
                result = self.run_hook({name: 'probe-value'})
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload['hookSpecificOutput']['hookEventName'], 'SessionStart')
                context = payload['hookSpecificOutput']['additionalContext']
                self.assertIn('/adapters/hosts/README.md', context)
                self.assertIn('Before your first dispatch', context)

    def test_the_door_names_the_index_of_the_loaded_plugin(self):
        result = self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value'}, root=ROOT / 'plugin')
        self.assertIn(str(ROOT / 'plugin' / 'adapters' / 'hosts' / 'README.md'),
                      self.context(result))

    def test_the_hook_names_the_index_only_and_grants_no_authority(self):
        result = self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value'})
        context = self.context(result).replace(str(ROOT / 'plugin'), '')
        for page in ['hosts/orca.md', 'hosts/t3-code.md', 'hosts/omp.md']:
            with self.subTest(page=page):
                self.assertNotIn(page, context)
        for word in ['must', 'required', 'never', 'shall', 'only', 'always', 'mandatory',
                     'approve', 'permission', 'allow', 'gate', 'block']:
            with self.subTest(word=word):
                self.assertNotIn(word, context.lower())

    def test_the_written_check_stays_for_the_hosts_that_load_no_hook(self):
        workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        door = next(line for line in workers.splitlines() if '(hosts/README.md)' in line)
        for test in ['`t3-code` tools', 'omp']:
            with self.subTest(test=test):
                self.assertIn(test, door)

    def test_the_hook_and_the_written_check_test_the_same_variables(self):
        # A session that meets the hook's test must also meet the written one, so
        # the two doors carry the same set of variables. A variable in one and not
        # the other opens a session that reads the index and one that does not.
        workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        door = next(line for line in workers.splitlines() if '(hosts/README.md)' in line)
        written = {name for name in self.ORCA_VARIABLES if name in door}
        self.assertEqual(written, set(self.ORCA_VARIABLES))
        for name in self.ORCA_VARIABLES:
            with self.subTest(variable=name):
                self.assertIn(name, self.HOOK.read_text())

    def test_the_message_survives_a_plugin_path_holding_json_characters(self):
        # The plugin root is a filesystem path, so it may hold a quote or a
        # backslash. A hand-built JSON string breaks the moment it does.
        result = self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value'},
                                root='/tmp/we"ird\\path')
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload['hookSpecificOutput']['additionalContext']
        self.assertIn('/tmp/we"ird\\path/adapters/hosts/README.md', context)

    def test_the_hook_says_nothing_without_a_plugin_root(self):
        # A relative path would send the session to an index guessed from the
        # working directory, which is worse than no message at all.
        environment = dict(os.environ)
        for name in self.ORCA_VARIABLES:
            environment[name] = ''
        environment['ORCA_TERMINAL_HANDLE'] = 'probe-value'
        environment.pop('CLAUDE_PLUGIN_ROOT', None)
        result = subprocess.run(['bash', str(self.HOOK)], capture_output=True, text=True,
                                env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_the_hook_adds_no_always_read_bytes_to_the_host_adapters(self):
        # The hook's message is delivered by the host, not by an adapter every
        # session reads, so neither host.md nor mobile.md grows for it.
        for relative in ('plugin/adapters/host.md', 'plugin/adapters/mobile.md'):
            with self.subTest(path=relative):
                self.assertNotIn('host-detect.sh', (ROOT / relative).read_text())
        # host.md, which every session reads, carries none of the detection.
        self.assertNotIn('ORCA_TERMINAL_HANDLE', (ROOT / 'plugin/adapters/host.md').read_text())
