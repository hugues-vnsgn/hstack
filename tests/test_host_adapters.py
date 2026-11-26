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
        (self.plugin / 'skills/hugues-mode/scripts/bootstrap.ts').unlink()
        result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
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

    def test_a_draft_that_still_runs_the_plan_checker_is_refused(self):
        # Upstream deleted its plan checker, so hStack no longer binds one. A leftover command
        # is refused with nothing emitted, never rewritten into a verb that does not exist.
        draft = self.consumer / 'draft.md'
        draft.write_text((ROOT / 'tests/fixtures/adapter-plan.md').read_text()
                         + '`node pstack/skills/poteto-mode/scripts/check-plan.mjs plan.md`\n')
        result = self.bound('translate-plan', draft)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(result.stdout, '')
        self.assertIn('unsupported skill-directory command', result.stderr)

    def test_withdrawn_verbs_are_unknown(self):
        for verb in ['payload-policy', 'helper-ready', 'program-check', 'artifact-hash',
                     'decode-design', 'worker-run', 'run-control', 'run-wait', 'plan-compare',
                     'plan-check']:
            with self.subTest(verb=verb):
                result = self.bound(verb)
                self.assertEqual(result.returncode, 2)
                self.assertIn('invalid choice', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_bun_helper_setup_holds_unwritable_installation(self):
        tools = ' '.join((ROOT / 'plugin/adapters/host-helper-setup.md').read_text().split())
        setup = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        for host, directory in [
                ('.claude', '.claude/plugins/cache/hstack/hstack/<loaded-version>/skills/hugues-mode/scripts'),
                ('.codex', '.codex/plugins/cache/hstack/hstack/<loaded-version>/skills/hugues-mode/scripts'),
                ('.cursor', '.cursor/plugins/local/hstack/skills/hugues-mode/scripts')]:
            with self.subTest(host=host):
                self.assertIn(directory, tools)
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
        for name in ['autopilot-full', 'autopilot-stack']:
            self.assertIn('read-workflow', (self.plugin / f'skills/hugues-mode/playbooks/{name}.md').read_text())
        plan = (self.plugin / 'skills/hugues-mode/playbooks/multi-phase-plan.md').read_text()
        self.assertNotIn('plan-check', plan)
        self.assertNotIn('check-plan', plan)
        cleanup = (self.plugin / 'skills/hugues-mode/playbooks/worktree-cleanup.md').read_text()
        self.assertIn('host_tools.py worktree-audit', cleanup)
        self.assertIn('separate active/pinned-chat gate', cleanup)


def claude_current_rows(cwd, stamp):
    base = {'sessionId': 'fixture-session', 'version': '2.1.317', 'entrypoint': 'cli',
            'userType': 'external', 'gitBranch': 'scratch', 'isSidechain': False,
            'cwd': str(cwd), 'timestamp': stamp}
    usage = {'input_tokens': 3, 'output_tokens': 5, 'cache_creation_input_tokens': 7,
             'cache_read_input_tokens': 11,
             'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 7},
             'server_tool_use': {'web_fetch_requests': 0, 'web_search_requests': 0},
             'output_tokens_details': {'thinking_tokens': 2}, 'service_tier': 'standard',
             'speed': 'standard', 'inference_geo': '', 'iterations': [], 'fallback_credit': None}
    assistant = dict(base, type='assistant', uuid='a1', parentUuid='a0', requestId='req',
                     requestRef='ref', requestedModel='model', effort='high', perTurnEffort='high',
                     attributionSkill='skill', attributionPlugin='plugin', apiBlockIndex=0,
                     message={'id': 'msg', 'type': 'message', 'role': 'assistant', 'model': 'model',
                              'stop_reason': 'tool_use', 'stop_sequence': None, 'container': None,
                              'context_management': None, 'diagnostics': {'cache_miss_reason': {'type': 'none'}},
                              'input_transformations': [{'type': 'thinking_dropped', 'path': 'messages.3.content.1', 'reason': 'plain'}],
                              'stop_details': None, 'usage': usage,
                              'content': [{'type': 'thinking', 'thinking': 'plain', 'signature': 'sig'},
                                          {'type': 'tool_use', 'id': 'tu1', 'name': 'Read',
                                           'input': {'file_path': 'README.md'}, 'caller': {'type': 'direct'}}]})
    user = dict(base, type='user', uuid='u1', parentUuid='a1', promptId='prompt', sandboxed=False,
                permissionMode='default', promptSource='user', origin={'kind': 'human'},
                turnPosition={'promptIndex': 0, 'turnIndex': 1}, isVisibleInTranscriptOnly=False,
                permissionDecision={'decision': 'allow', 'source': 'user', 'grantScope': 'once'},
                toolUseResult={'type': 'text', 'file': {'numLines': 1, 'totalLines': 1, 'content': 'plain'}},
                message={'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'tu1',
                                                      'content': 'plain', 'is_error': False}]})
    schema = {'properties': {'file_path': {'type': 'string'}, 'path': {'type': 'string'}}}
    tool = {'name': 'Read', 'description': 'plain', 'defer_loading': False, 'input_schema': schema}
    meta = {'sessionId': 'fixture-session'}
    return [
        dict(meta, type='mode', mode='normal'),
        dict(meta, type='permission-mode', permissionMode='default'),
        dict(meta, type='session-owner', accountUuid='account', organizationUuid='organization'),
        dict(meta, type='atis-latch', atis='latch'),
        dict(meta, type='queue-operation', operation='enqueue', content='plain', timestamp=stamp),
        dict(meta, type='last-prompt', lastPrompt='plain', leafUuid='u1'),
        dict(meta, type='ai-title', aiTitle='plain'),
        dict(meta, type='custom-title', customTitle='plain'),
        dict(meta, type='agent-name', agentName='plain'),
        dict(meta, type='pr-link', prNumber=1, prRepository='owner/repo',
             prUrl='https://example.invalid/pull/1', timestamp=stamp),
        dict(meta, type='tools-used', tools=['Read']),
        dict(meta, type='cost-state', hasUnknownModelCost=False, startTime=1, totalCostUSD=0.5,
             totalDuration=2, totalAPIDuration=1, totalLinesAdded=0, totalLinesRemoved=0,
             modelUsage={'model': {'inputTokens': 3}}),
        dict(base, type='system', subtype='turn_duration', durationMs=5, messageCount=2,
             pendingBackgroundAgentCount=0, isMeta=False, uuid='s1', parentUuid='u1'),
        dict(base, type='system', subtype='local_command', content='plain', level='info', isMeta=False,
             commandRun={'command': 'plain', 'args': 'plain'}, uuid='s2', parentUuid='u1'),
        dict(base, type='attachment', uuid='t1', parentUuid='u1', renderedRole='user',
             rendered=[{'content': 'plain'}], renderedInHumanTurn=[{'content': 'plain'}],
             attachment={'type': 'deferred_tools_delta', 'addedNames': ['Read'], 'loadedNames': [],
                         'toolSearchAbsent': False}),
        dict(base, type='attachment', uuid='t2', parentUuid='u1', renderedRole='user',
             rendered=[{'content': 'plain'}],
             attachment={'type': 'deferred_tools_record', 'entries': [tool]}),
        dict(base, type='attachment', uuid='t3', parentUuid='u1', renderedRole='user',
             rendered=[{'content': 'plain'}],
             attachment={'type': 'file', 'filename': str(Path(cwd) / 'README.md'),
                         'displayPath': 'README.md', 'content': {'type': 'text', 'file': {'content': 'plain'}}}),
        dict(meta, type='api-request-shape', shapeHash='shape', timestamp=stamp, version='2.1.317',
             shape={'system': [{'type': 'text', 'text': 'plain'}], 'tools': [tool]}),
        dict(meta, type='api-request', id='request', base='shape', tail=['blob'], keep=1,
             cacheControl=[{'path': ['messages', 1], 'value': {'type': 'ephemeral', 'ttl': '1h'}}],
             shapeHash='shape',
             requestDigest='digest', querySource='sdk', timestamp=stamp, version='2.1.317',
             params={'model': 'model', 'max_tokens': 1, 'betas': [], 'thinking': {'type': 'adaptive'},
                     'safeguards': [{'type': 'dangerous_tool_use',
                                     'classifier_context': {'live_cwd': str(cwd), 'platform': 'plain',
                                                            'trusted_directories': {'primary': {'path': str(cwd), 'resolved': [str(cwd)]},
                                                                                    'additional': []}}}]}),
        dict(meta, type='api-request-blob', hash='blob',
             message={'role': 'user', 'content': [{'type': 'text', 'text': 'plain'}]}),
        {'type': 'file-history-snapshot', 'messageId': 'u1', 'isSnapshotUpdate': False,
         'snapshot': {'messageId': 'u1', 'timestamp': stamp,
                      'trackedFileBackups': {'README.md': {'backupFileName': None, 'backupTime': stamp,
                                                           'realParentDir': str(cwd), 'version': 1}}}},
        {'type': 'file-history-delta', 'messageId': 'u1', 'snapshotMessageId': 'u1', 'timestamp': stamp,
         'trackingPath': str(Path(cwd) / 'README.md'),
         'backup': {'backupFileName': None, 'backupTime': stamp, 'realParentDir': str(cwd), 'version': 1}},
        assistant,
        user,
    ]


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

    def test_an_undecodable_escape_holds_claude_and_not_cursor(self):
        # The shared matcher decodes percent escapes strictly for Claude Code
        # and Codex, so a record whose text is not valid percent-encoding holds
        # that source's coverage. Only the Cursor path tolerates it, because
        # the owner's real Cursor store carries a git date format.
        text = "the format is --format='%h %ad %s'"
        claude = {'type': 'assistant', 'timestamp': self.stamp, 'cwd': str(self.other),
                  'message': {'content': [{'type': 'text', 'text': text}]}}
        hits, reports, complete = self.scan('claude', [claude])
        self.assertEqual(reports[0]['coverage'], 'unavailable', reports[0])
        self.assertFalse(complete)
        cursor = {'role': 'assistant',
                  'message': {'content': [{'type': 'text', 'text': text}]}}
        hits, reports, complete = self.scan('cursor', [cursor])
        self.assertEqual(reports[0]['coverage'], 'complete', reports[0])
        self.assertFalse(complete)

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

    def test_unsupported_host_is_never_read_and_caps_coverage(self):
        unread = {'provider': 'omp', 'root': '/not-authorized/not-read', 'coverage': 'complete'}
        with patch.object(activity, 'read_selected', side_effect=AssertionError('must not read unsupported host')):
            hits, reports, complete = activity.scan({'coverage': 'complete', 'sources': [unread]}, [self.wt], self.now)
        self.assertFalse(complete)
        self.assertFalse(hits[str(self.wt)])
        self.assertEqual(reports[0]['coverage'], 'unsupported')
        root = self.area / 'authorized empty host'
        root.mkdir()
        supported = {'provider': 'claude', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}
        with patch.object(activity, 'read_selected', side_effect=AssertionError('empty root has no file reads')):
            self.assertFalse(activity.scan({'coverage': 'complete', 'sources': [unread, supported]}, [self.wt], self.now)[2])

    def test_complete_claude_source_with_an_unread_omp_source_is_not_complete(self):
        transcript = self.area / 'claude.jsonl'
        transcript.write_text(json.dumps(self.claude()) + '\n')
        claude = {'provider': 'claude', 'files': [str(transcript)], 'authorization': 'synthetic', 'coverage': 'complete'}
        omp = {'provider': 'omp', 'files': [str(self.area / 'omp.jsonl')], 'authorization': 'synthetic', 'coverage': 'complete'}
        hits, reports, complete = activity.scan({'coverage': 'complete', 'sources': [claude]}, [self.wt], self.now)
        self.assertTrue(complete)
        for sources in ([claude, omp], [omp, claude]):
            with self.subTest(order=[source['provider'] for source in sources]):
                with patch.object(activity, 'read_selected', wraps=activity.read_selected) as read:
                    hits, reports, complete = activity.scan({'coverage': 'complete', 'sources': sources}, [self.wt], self.now)
                self.assertFalse(complete)
                self.assertEqual([call.args[0] for call in read.call_args_list], [transcript])
                self.assertEqual({report['provider']: report['coverage'] for report in reports},
                                 {'claude': 'complete', 'omp': 'unsupported'})
                self.assertTrue(hits[str(self.wt)])

    def test_claude_2_1_31x_transcript_with_activity_is_complete(self):
        rows = claude_current_rows(self.wt, self.stamp)
        hits, reports, complete = self.scan('claude', rows)
        self.assertTrue(complete)
        self.assertEqual(reports[0]['coverage'], 'complete')
        self.assertEqual(reports[0]['files_scanned'], 1)
        self.assertTrue(hits[str(self.wt)][0]['recent'])
        self.assertFalse(hits[str(self.other)])
        for row in rows:
            with self.subTest(row_type=row['type']):
                self.assertTrue(self.scan('claude', [row])[2])

    def test_unknown_claude_metadata_keys_keep_their_activity_visible(self):
        sibling = '../' + self.other.name + '/README.md'
        read_sibling = {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': sibling}}
        for key in ['toolUseResult', 'futureMetadata']:
            with self.subTest(key=key, shape='absolute mention'):
                hits, _, complete = self.scan('claude', [self.claude(**{key: {'detail': str(self.other)}})])
                self.assertTrue(complete)
                self.assertTrue(hits[str(self.other)])
            with self.subTest(key=key, shape='supported tool call'):
                hits, _, complete = self.scan('claude', [self.claude(**{key: [read_sibling]})])
                self.assertTrue(complete)
                self.assertTrue(hits[str(self.other)])
            for shape, value in [('unsupported tool call', [{'type': 'tool_use', 'name': 'Grep', 'input': {'pattern': 'x'}}]),
                                 ('native tool_calls', {'tool_calls': []}),
                                 ('relative path field', {'type': 'file_reference', 'path': sibling}),
                                 ('relative path beside a tool call', {**read_sibling, 'path': sibling}),
                                 ('nested relative path field', [{'detail': {'file_path': 'README.md'}}]),
                                 ('non-string path field', {'path': ['README.md']})]:
                with self.subTest(key=key, shape=shape):
                    self.assertFalse(self.scan('claude', [self.claude(**{key: value})])[2])
        with self.subTest(shape='message metadata'):
            message = {'content': [], 'future_detail': {'path': sibling}}
            self.assertFalse(self.scan('claude', [self.claude(message=message)])[2])
            message = {'content': [], 'input_transformations': [{'type': 'thinking_dropped', 'path': 'messages.3.content.1/../x'}]}
            self.assertFalse(self.scan('claude', [self.claude(message=message)])[2])
            message = {'content': [], 'future_detail': str(self.other)}
            hits, _, complete = self.scan('claude', [self.claude(message=message)])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_unknown_claude_row_types_hold_and_known_metadata_rows_still_see_text(self):
        for kind in ['progress', 'future-row-type']:
            with self.subTest(kind=kind):
                self.assertFalse(self.scan('claude', [{'type': kind, 'sessionId': 'fixture'}])[2])
        attachment = {'type': 'attachment', 'cwd': str(self.wt), 'timestamp': self.stamp,
                      'attachment': {'type': 'file', 'filename': str(self.other / 'README.md')}}
        hits, _, complete = self.scan('claude', [attachment])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])
        call = {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': '../' + self.other.name + '/README.md'}}
        system = {'type': 'system', 'subtype': 'local_command', 'cwd': str(self.wt), 'timestamp': self.stamp}
        hits, _, complete = self.scan('claude', [dict(system, message={'content': [call]})])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])
        for row in [dict(attachment, attachment={'type': 'directory', 'path': '../' + self.other.name}),
                    dict(attachment, attachment={'type': 'hook_success', 'call': dict(call, name='Grep', input={'pattern': 'x'})}),
                    dict(attachment, cwd='relative/directory'),
                    {'type': 'attachment', 'timestamp': 'not-a-time'},
                    {'type': 'mode', 'sessionId': 17}]:
            with self.subTest(row=row):
                self.assertFalse(self.scan('claude', [row])[2])

    def test_claude_2_1_31x_activity_blocks_stay_strict(self):
        call = {'type': 'tool_use', 'id': 'tu1', 'name': 'Read', 'input': {'file_path': 'README.md'}}
        for name, block in [('unreviewed block key', dict(call, unreviewed='field')),
                            ('caller is not an object', dict(call, caller='direct')),
                            ('caller carries a nested value', dict(call, caller={'type': {'path': 'x'}})),
                            ('unsupported tool', dict(call, name='Grep', input={'pattern': 'x'})),
                            ('unknown tool input field', dict(call, input={'file_path': 'README.md', 'unknown': 1}))]:
            with self.subTest(name):
                row = self.claude(message={'content': [block]})
                self.assertFalse(self.scan('claude', [row])[2])
        for name, block in [('unreviewed result key', {'type': 'tool_result', 'tool_use_id': 'tu1', 'content': 'plain', 'unreviewed': 1}),
                            ('opaque result block', {'type': 'tool_result', 'tool_use_id': 'tu1', 'content': [{'type': 'image', 'source': {}}]}),
                            ('unknown block type', {'type': 'server_tool_use', 'name': 'x', 'input': {}})]:
            with self.subTest(name):
                self.assertFalse(self.scan('claude', [self.claude(message={'content': [block]})])[2])
        for name, message in [('usage is not an object', {'content': [], 'usage': 'opaque'}),
                              ('negative count', {'content': [], 'usage': {'input_tokens': -1}}),
                              ('message id is not text', {'content': [], 'id': 17})]:
            with self.subTest(name):
                self.assertFalse(self.scan('claude', [self.claude(message=message)])[2])

    def test_claude_file_history_paths_resolve_from_the_recorded_parent_directory(self):
        def backup(parent):
            entry = {'backupFileName': None, 'backupTime': self.stamp, 'version': 1}
            return entry if parent is None else dict(entry, realParentDir=str(parent))

        def snapshot(backups):
            return {'type': 'file-history-snapshot', 'messageId': 'u1', 'isSnapshotUpdate': False,
                    'snapshot': {'messageId': 'u1', 'timestamp': self.stamp, 'trackedFileBackups': backups}}

        def delta(tracking_path, parent):
            return {'type': 'file-history-delta', 'messageId': 'u1', 'snapshotMessageId': 'u1',
                    'timestamp': self.stamp, 'trackingPath': tracking_path, 'backup': backup(parent)}
        sibling = '../' + self.other.name + '/README.md'
        for name, row in [('snapshot, absolute', snapshot({str(self.other / 'README.md'): backup(self.other)})),
                          ('snapshot, relative name', snapshot({sibling: backup(self.other)})),
                          ('delta, absolute', delta(str(self.other / 'README.md'), self.other)),
                          ('delta, relative name', delta(sibling, self.other)),
                          ('delta, absolute through a symlinked directory', delta(str(self.area / 'link' / 'README.md'), self.other))]:
            with self.subTest(name):
                hits, _, complete = self.scan('claude', [self.claude(), row])
                self.assertTrue(complete)
                self.assertTrue(hits[str(self.other)])
        with self.subTest('the session directory is not the base'):
            hits, _, complete = self.scan('claude', [delta('README.md', self.other)])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])
            self.assertFalse(hits[str(self.wt)])
        with self.subTest('a session that changed directory'):
            old = datetime.fromtimestamp(self.now - 9 * 86400, timezone.utc).isoformat()
            moved = [self.claude(cwd=str(self.wt), timestamp=old), self.claude(cwd=str(self.area), timestamp=old)]
            hits, _, complete = self.scan('claude', moved + [delta('README.md', self.wt)])
            self.assertTrue(complete)
            self.assertTrue(any(hit['recent'] for hit in hits[str(self.wt)]))
            hits, _, complete = self.scan('claude', moved + [delta('README.md', None)])
            self.assertTrue(not complete or any(hit['recent'] for hit in hits[str(self.wt)]))
        for row in [snapshot({}), delta(str(self.wt / 'README.md'), self.wt)]:
            hits, _, complete = self.scan('claude', [row])
            self.assertTrue(complete)
            self.assertEqual(bool(hits[str(self.wt)]), row['type'] == 'file-history-delta')
        for name, row in [('snapshot entry without a parent directory', snapshot({'README.md': backup(None)})),
                          ('snapshot entry is not an object', snapshot({'README.md': 'opaque'})),
                          ('snapshot parent directory is relative', snapshot({'README.md': dict(backup(None), realParentDir='sub')})),
                          ('delta without a parent directory', delta('README.md', None)),
                          ('delta without a backup', {key: value for key, value in delta('README.md', None).items() if key != 'backup'}),
                          ('delta parent directory is not text', dict(delta('README.md', None), backup=dict(backup(None), realParentDir=['x']))),
                          ('delta names a directory', delta('..', self.other)),
                          ('snapshot is not an object', dict(snapshot({}), snapshot='opaque')),
                          ('backups are not an object', snapshot(['README.md'])),
                          ('snapshot is missing', {'type': 'file-history-snapshot', 'messageId': 'u1'}),
                          ('delta lacks a tracking path', {'type': 'file-history-delta', 'messageId': 'u1'}),
                          ('delta tracking path is not text', delta(['README.md'], self.other))]:
            with self.subTest(name):
                self.assertFalse(self.scan('claude', [row])[2])

    def assert_seen_or_held(self, rows):
        hits, _, complete = self.scan('claude', rows)
        self.assertTrue(hits[str(self.other)] or not complete)

    def test_claude_paths_used_as_dict_keys_are_searched(self):
        sibling = str(self.other / 'README.md')
        attachment = {'type': 'attachment', 'cwd': str(self.wt), 'timestamp': self.stamp,
                      'attachment': {'type': 'file', 'filename': str(self.wt / 'README.md'),
                                     'content': {sibling: {'status': 'modified'}}}}
        for name, row in [('user result', self.claude(type='user', message={'content': 'plain'},
                                                      toolUseResult={'files': {sibling: {'status': 'modified'}}})),
                          ('attachment', attachment),
                          ('path in a key of a key', self.claude(type='user', message={'content': 'plain'},
                                                                 toolUseResult={sibling + '/x': {sibling: 1}}))]:
            with self.subTest(name):
                hits, _, complete = self.scan('claude', [row])
                self.assertTrue(complete)
                self.assertTrue(hits[str(self.other)])

    def test_claude_relative_paths_in_path_named_fields_are_seen_or_held(self):
        sibling = '../' + self.other.name + '/README.md'
        unnormalised = str(self.wt) + '/../' + self.other.name + '/README.md'

        def attachment(**fields):
            return {'type': 'attachment', 'cwd': str(self.wt), 'timestamp': self.stamp, 'attachment': fields}

        def result(**fields):
            return self.claude(type='user', message={'content': 'plain'}, toolUseResult=fields)
        for name, row in [('relative filePath in a result', result(type='update', filePath=sibling)),
                          ('unnormalised filePath in a result', result(type='update', filePath=unnormalised)),
                          ('relative filename in an attachment', attachment(type='edited_text_file', filename=sibling, snippet='plain')),
                          ('unnormalised filename in an attachment', attachment(type='edited_text_file', filename=unnormalised, snippet='plain')),
                          ('relative workingDirectory', attachment(type='environment', workingDirectory='../' + self.other.name)),
                          ('relative displayPath alone', attachment(type='file', displayPath=sibling)),
                          ('relative displayPath beside a relative filename', attachment(type='file', displayPath=sibling, filename=sibling)),
                          ('tilde filename', attachment(type='file', filename='~/' + self.other.name))]:
            with self.subTest(name):
                self.assert_seen_or_held([row])
        with self.subTest('displayPath beside its absolute filename'):
            hits, _, complete = self.scan('claude', [attachment(type='file', displayPath=sibling, filename=str(self.other / 'README.md'))])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.other)])

    def test_unobserved_claude_system_subtypes_and_attachment_types_hold(self):
        command = {'command': 'rm', 'args': '-rf ../' + self.other.name}
        system = {'type': 'system', 'cwd': str(self.wt), 'timestamp': self.stamp, 'commandRun': command}
        attachment = {'type': 'attachment', 'cwd': str(self.wt), 'timestamp': self.stamp}
        for name, row in [('unknown subtype', dict(system, subtype='future_subtype')),
                          ('no subtype', system),
                          ('subtype is not text', dict(system, subtype=['local_command'])),
                          ('unknown attachment type', dict(attachment, attachment={'type': 'future_attachment', 'detail': 'plain'})),
                          ('no attachment type', dict(attachment, attachment={'detail': 'plain'})),
                          ('attachment is not an object', dict(attachment, attachment='plain'))]:
            with self.subTest(name):
                self.assertFalse(self.scan('claude', [row])[2])
        for subtype in ['local_command', 'turn_duration', 'stop_hook_summary']:
            with self.subTest(subtype=subtype):
                self.assertTrue(self.scan('claude', [dict(system, subtype=subtype)])[2])

    def test_claude_metadata_path_fields_stay_strings(self):
        sibling = '../' + self.other.name
        attachment = {'type': 'attachment', 'cwd': str(self.wt), 'timestamp': self.stamp}
        for name, fields in [('list', {'type': 'file', 'path': [sibling, 'README.md']}),
                             ('object', {'type': 'file', 'path': {'relative': sibling + '/README.md'}}),
                             ('number', {'type': 'file', 'path': 7}),
                             ('nested list', {'type': 'file', 'detail': {'file_path': [sibling]}})]:
            with self.subTest(name):
                self.assert_seen_or_held([dict(attachment, attachment=fields)])
        with self.subTest('tool schemas and cache markers'):
            schema = {'properties': {'path': {'type': 'string', 'default': str(self.other)}}}
            rows = [dict(attachment, attachment={'type': 'deferred_tools_record', 'entries': [{'name': 'x', 'input_schema': schema}]}),
                    {'type': 'api-request', 'sessionId': 's', 'timestamp': self.stamp,
                     'cacheControl': [{'path': ['messages', 1], 'value': {'type': 'ephemeral'}}]}]
            for row in rows:
                self.assertTrue(self.scan('claude', [row])[2])
            hits, _, complete = self.scan('claude', rows[:1])
            self.assertTrue(hits[str(self.other)])
        with self.subTest('a non-string path outside the schema keys'):
            self.assert_seen_or_held([dict(attachment, attachment={'type': 'file', 'detail': {'path': [sibling]}})])

    def test_claude_tool_calls_outside_the_tool_use_shape_hold(self):
        sibling = '../' + self.other.name + '/README.md'
        meta = {'type': 'api-request-blob', 'sessionId': 's', 'hash': 'h'}

        def blob(block):
            return dict(meta, message={'role': 'assistant', 'content': [block]})
        read = {'type': 'tool_use', 'id': 't', 'name': 'Read', 'input': {'file_path': sibling}}
        hits, _, complete = self.scan('claude', [self.claude(), blob(read)])
        self.assertTrue(complete)
        self.assertTrue(hits[str(self.other)])
        classifier = {'type': 'dangerous_tool_use', 'classifier_context': {'live_cwd': str(self.wt)}}
        request = {'type': 'api-request', 'sessionId': 's', 'timestamp': self.stamp, 'params': {'safeguards': [classifier]}}
        self.assertTrue(self.scan('claude', [request])[2])
        for name, row in [('a call named like the classifier', dict(request, params={'safeguards': [dict(classifier, name='bash', input={})]})),
                          ('mcp_tool_use', blob({'type': 'mcp_tool_use', 'id': 't', 'name': 'write_file', 'server_name': 'fs', 'input': {'file': sibling}})),
                          ('server_tool_use', blob({'type': 'server_tool_use', 'id': 't', 'name': 'bash', 'input': {'command': 'cat ' + sibling}})),
                          ('a call encoded in the blob list',
                           {'type': 'api-request', 'sessionId': 's', 'timestamp': self.stamp,
                            'tail': [json.dumps(read)]})]:
            with self.subTest(name):
                self.assert_seen_or_held([self.claude(), row])

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
                              ('claude', self.claude(message={'content': [], 'usage': {'unknown': {'path': '../sibling'}}}))]:
            self.assertFalse(self.scan(provider, [row])[2])
        for kind in ['progress', 'future-row-type']:
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

    def test_cli_unsupported_host_is_never_read_and_holds_the_audit(self):
        unread = {'provider': 'omp', 'files': ['/not-authorized/not-read.jsonl'], 'coverage': 'complete'}
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [unread]})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['sources'][0]['coverage'], 'unsupported')
        self.assertEqual(report['sources'][0]['files_scanned'], 0)
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')
        root = self.area / 'empty supported history'
        root.mkdir()
        (root / 'old.jsonl').write_text(json.dumps({'type': 'event_msg', 'timestamp': '2020-01-01T00:00:00Z', 'payload': {'type': 'agent_message', 'message': 'old unrelated fixture'}}) + '\n')
        supported = {'provider': 'codex', 'root': str(root), 'authorization': 'synthetic', 'coverage': 'complete'}
        control, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [supported]})
        self.assertEqual(control.returncode, 0)
        result, report = self.audit({'schema_version': 1, 'coverage': 'complete', 'sources': [unread, supported]})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['audit_status'], 'hold')
        self.assertEqual([source['coverage'] for source in report['sources']], ['unsupported', 'complete'])
        self.assertEqual(report['worktrees'][1]['bucket'], 'hold-activity-unavailable')

    def test_cli_reads_a_claude_2_1_31x_transcript(self):
        stamp = datetime.now(timezone.utc).isoformat()
        path = self.area / 'current.jsonl'
        path.write_text(''.join(json.dumps(row) + '\n' for row in claude_current_rows(self.wt, stamp)))
        manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic only', 'coverage': 'complete'}]}
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['audit_status'], 'complete')
        self.assertEqual(report['sources'], [{'provider': 'claude', 'coverage': 'complete', 'files_scanned': 1}])
        row = next(r for r in report['worktrees'] if r['worktree'] == str(self.wt))
        self.assertEqual(row['bucket'], 'verify-recent-chat')
        self.assertEqual(row['evidence'][0]['provider'], 'claude')
        self.assertFalse(row['deletion_authorized'])
        path.write_text(path.read_text() + json.dumps({'type': 'future-row-type', 'sessionId': 'fixture'}) + '\n')
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['sources'][0]['coverage'], 'unavailable')
        self.assertEqual(report['sources'][0]['error'], 'unsupported claude record envelope')

    def test_cli_does_not_report_no_recent_evidence_for_a_worktree_a_claude_row_names_indirectly(self):
        stamp = datetime.now(timezone.utc).isoformat()
        target = str(self.wt / 'README.md')
        attachment = {'type': 'attachment', 'cwd': str(self.consumer), 'timestamp': stamp}
        keyed = {'type': 'user', 'cwd': str(self.consumer), 'timestamp': stamp, 'message': {'role': 'user', 'content': 'plain'},
                 'toolUseResult': {'files': {target: {'status': 'modified'}}}}
        for name, row, recent in [
                ('absolute filename', dict(attachment, attachment={'type': 'edited_text_file', 'filename': target, 'snippet': 'plain'}), True),
                ('path used as a key', keyed, True),
                ('relative filename', dict(attachment, attachment={'type': 'edited_text_file', 'filename': os.path.relpath(target, self.consumer), 'snippet': 'plain'}), False)]:
            with self.subTest(name):
                path = self.area / 'indirect.jsonl'
                path.write_text(json.dumps(row) + '\n')
                manifest = {'schema_version': 1, 'coverage': 'complete', 'sources': [{'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic only', 'coverage': 'complete'}]}
                result, report = self.audit(manifest)
                row = next(r for r in report['worktrees'] if r['worktree'] == str(self.wt))
                self.assertNotEqual(row['activity'], 'no-recent-evidence')
                self.assertEqual(row['activity'] == 'recent', recent)
                self.assertEqual(result.returncode, 0 if recent else 2)

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
    'orca-bot.md': HostPage(listing='ADEs', skip_only=['task DAGs', 'decision gates', 'coordinator loop',
                                                       'automations', 'orca artifacts', 'bot new-chat']),
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
        "The `model:` line in `poteto-agent`'s file":
            'hugues-agent keeps `model: inherit` and the models file picks the role model, so no Cursor slug reaches the API',
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
            for phrase in ['`subagent_type: "general-purpose"`', '`"Explore"`', 'locate or search code',
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
            self.assertEqual(set(shapes), {'true', None})
            for readonly, paths in shapes.items():
                claude = self.row('Subagent fields', f'`readonly: {readonly or "false"}`')[1]
                self.assertIn('`subagent_type: "general-purpose"`', claude, paths)
                if readonly is None:
                    self.assertIn('also for `generalPurpose` without `readonly`', claude, paths)
        with self.subTest('one model rule'):
            claude = self.row('Models', 'A `gemini-*` or other non-Claude slug')[1]
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
            self.assertIn('Resume an existing subagent only when the work needs state that lives in it', router)
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
            for test in ['ORCA_TERMINAL_HANDLE', 'ORCA_PANE_KEY', 'ORCA_TAB_ID', 'ORCA_BOT_TOOLS_TOKEN',
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

    def test_the_orca_bot_page_stamps_every_row_and_carries_the_bot_rules(self):
        page = (ROOT / 'plugin/adapters/hosts/orca-bot.md').read_text()
        rows = {row[0]: row[1] for table in table_rows(page).values() for row in table}
        readme = (ROOT / 'plugin/adapters/hosts/README.md').read_text()
        with self.subTest('every row but the skip line carries an Orca version or says unobserved'):
            for name in HOST_PAGE_ROWS[:-1]:
                self.assertRegex(rows[name], r'1\.4\.\d{3}|unobserved', name)
            self.assertEqual(rows['Load a PR head'], 'unobserved')
        with self.subTest('a guide or a help text is never presented as observed behaviour'):
            for name in ('Send', 'Read', 'Close'):
                self.assertRegex(rows[name], r"Orca's (guide|help)", name)
            self.assertIn('Orca\'s rules block says', rows['Allowed tools'])
        with self.subTest('a chat worker is not said to lack a terminal handle'):
            self.assertNotIn('has no terminal handle and reads no page', page)
        with self.subTest('Detect tests that the token is set and never prints it'):
            self.assertTrue(rows['Detect'].startswith(
                '`ORCA_BOT_TOOLS_TOKEN` is set and `ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID` are all unset.'))
            self.assertIn('A session with the token and any of those three is a pane', rows['Detect'])
            self.assertIn('Test only that the token is set', rows['Detect'])
            self.assertIn('never print, echo or log its value', rows['Detect'])
            self.assertIn('unset in a pane', rows['Detect'])
            self.assertIn('whether a pane a bot started carries the token', rows['Detect'])
        with self.subTest('the index lists the bot page before the Orca page and scopes the shared rule'):
            ades = readme.split('## ADEs\n', 1)[1]
            self.assertLess(ades.index('](orca-bot.md)'), ades.index('](orca.md)'))
            self.assertIn('The Orca bot page is the one exception', readme.split('## Shared ADE rule', 1)[1].split('## Page shape')[0])
            bullet = next(line for line in ades.splitlines() if '](orca-bot.md)' in line)
            self.assertIn('is set and the three Orca variables below are not', bullet)
        carried = {
            'Sessions and worktrees': ['--worktree new-child --repo id:<repo> --base-branch origin/main --name <slug>',
                                       'A bot reads repos and edits none', 'One task, one worker, one worktree',
                                       'Never run `orca repo add` or `orca project setup-update`',
                                       'A group room is unmapped', '--worktree-base-path',
                                       "Orca's source says a worker started as a chat gets `ORCA_TERMINAL_HANDLE` (1.4.271)",
                                       'whether it reads a page is unobserved'],
            'Start': ['orca orchestration worker-start --spec-file <brief> --agent claude --model <id> --effort <level> --item <n> --json',
                      'Read <root>/skills/hugues-mode/worker.md before anything else.', '.hstack/models.md',
                      'never into bot memory', 'tool ban in words', 'mode: terminal', 'anything but `terminal` is a gap',
                      'at most 4 workers per bot', 'an arena pair as 2', 'did not write the code',
                      'the first seat on the `interrogate reviewers` line that names a model rather than `inherit-parent`',
                      "hStack does not enforce a worker's tool deny", 'has no flag for agent arguments (help, 1.4.271)',
                      "Orca strips `--disallowedTools` from a chat's configured arguments (source, 1.4.271)",
                      'whether one reaches a worker pane is unobserved', '(from `ps`, 1.4.269)'],
            'Send': ['orca orchestration send --to dispatch:<id>', '--body-file',
                     'A worker reports with `worker_done`', 'does not tell it to ask',
                     'in the bot\'s transcripts on disk, on 1.4.271: 5 worker `question` messages arrived',
                     'If one arrives, answer it with `orca orchestration reply --id <message_id>'],
            'Read': ['worker-show', 'worker-read --dispatch <id>', 'The evidence folder is the record'],
            'Wait': ["Observed in the bot's transcripts on disk, on 1.4.271: 91 `worker_done`, 1 `escalation` and 5 worker `question`", 'Never poll', '`worker_done` is transport, not done', 'On every wake, before acting',
                     '--retry-of', 'lost worker', 'gh pr checks --watch', 'up to 2 times'],
            'Close': ['worker-release', 'on the owner\'s word', '--delete-branch', 'never `--force`'],
            'Allowed tools': ['orca bot item add`, `set`, `comment`, `done`, `link`, `list` and `show`',
                              'orca bot work list', '--status needs-you', 'a recommended one', 'write the report last',
                              'A bot never merges and never releases', 'Never ask for, accept or type a password or token',
                              'a handoff, a schedule, an event or a webhook holds'],
            'Skip line': ['Orca Runs', 'task DAGs', 'decision gates', 'the coordinator loop', '`bot create`',
                          '`bot new-chat`', 'automations', '`orca artifacts`'],
        }
        for name, phrases in carried.items():
            for phrase in phrases:
                with self.subTest(row=name, phrase=phrase):
                    self.assertIn(phrase, rows[name])
        with self.subTest('the page is an ADE page, never called a host page'):
            self.assertNotIn('host page', page.lower())
        with self.subTest('the intro dates 1.4.271 and cites 1.4.269 only where it was seen'):
            self.assertIn('observed on 2026-11-25 and 2026-11-26 and in the bot\'s transcripts on disk', page)
            self.assertIn('A cell that cites 1.4.269 was seen on that build only', page)
            self.assertNotIn('2026-11-22', page)
            self.assertNotIn('to 2026-11-26', page)

    def test_orca_md_gains_one_clause_for_a_worker_a_bot_dispatched(self):
        page = (ROOT / 'plugin/adapters/hosts/orca.md').read_text()
        clause = 'except that a worker a bot dispatched sends the `worker_done` its dispatch asks for'
        skip = next(row[1] for table in table_rows(page).values() for row in table if row[0] == 'Skip line')
        self.assertIn(clause, skip)
        self.assertTrue(skip.startswith('Skipped in Orca: Orca Runs, Tasks, Dispatches, inboxes, `worker_done`, heartbeats and the `orchestration` skill, ' + clause + '. hStack dispatches'))
        self.assertEqual(page.count(clause), 1)
        # Nothing else on the page knows about a bot, and its version stamps stay.
        self.assertNotIn('ORCA_BOT_TOOLS_TOKEN', page)
        self.assertEqual(page.replace(clause, '').count(' bot '), 0)
        self.assertTrue(page.startswith('# Orca\n\nThis page maps Orca CLI 1.4.241, observed on 2026-10-28. The lost-worker replies and the skip-line refusal also held on 1.4.243.'))

    def test_nothing_prints_the_bot_token(self):
        # ORCA_BOT_TOOLS_TOKEN is a secret. Text may test that it is set and may name it, and a
        # command that would print its value is a leak.
        name = 'ORCA_BOT_TOOLS_TOKEN'
        set_test = re.compile(r'\[ -n "\$\{ORCA_BOT_TOOLS_TOKEN(?::-|-)\}" \]')
        printing = re.compile(r'\b(printenv|echo|printf|export|cat)\b[^`\n]*' + name)
        paths = [*sorted((ROOT / 'plugin/adapters').rglob('*.md')), ROOT / 'plugin/hooks/host-detect.sh',
                 ROOT / 'docs/adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md']
        kit = ROOT / 'docs/orca-bots.md'
        if kit.exists():
            paths.append(kit)
        named = 0
        for path in paths:
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if name not in line or line.lstrip().startswith('#') and path.suffix == '.sh':
                    continue
                named += 1
                with self.subTest(path=path.relative_to(ROOT).as_posix(), line=number):
                    self.assertIsNone(printing.search(line), line)
                    if re.search(r'\$\{' + name, line):
                        self.assertRegex(line, set_test)
        self.assertGreater(named, 5)

        def unsafe_detection(text):
            # A line that names the token as a detection test must carry the safe test and the
            # ban itself, because a session runs it before it reads the page's own rule.
            return [line for line in text.splitlines()
                    if name in line and not (set_test.search(line) and 'never print' in line)]

        index = (ROOT / 'plugin/adapters/hosts/README.md').read_text()
        door = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        page = (ROOT / 'plugin/adapters/hosts/orca-bot.md').read_text()
        for label, text in [('the index', index), ('the written door', door), ('the bot page', page)]:
            with self.subTest(label):
                self.assertTrue(name in text)
                self.assertEqual(unsafe_detection(text), [])
        for label, sample, unsafe in [
                ('the old index line', '- [Orca bot](orca-bot.md): `$ORCA_BOT_TOOLS_TOKEN` is set.', True),
                ('a line with the test and no ban', 'Test it with `[ -n "${ORCA_BOT_TOOLS_TOKEN-}" ]` for `ORCA_BOT_TOOLS_TOKEN`.', True),
                ('a line with the ban and no test', '`$ORCA_BOT_TOOLS_TOKEN` is set, never print it.', True),
                ('a line with both', '`$ORCA_BOT_TOOLS_TOKEN` is set. Test it with `[ -n "${ORCA_BOT_TOOLS_TOKEN-}" ]`, never print it.', False),
                ('a line that does not name it', 'Test it with `[ -n "${ORCA_TAB_ID-}" ]`.', False)]:
            with self.subTest(label):
                self.assertEqual(bool(unsafe_detection(sample)), unsafe)
        for label, sample, leaks in [('a printenv', 'run `printenv ORCA_BOT_TOOLS_TOKEN`', True),
                                     ('an echo', 'run `echo $ORCA_BOT_TOOLS_TOKEN`', True),
                                     ('the set test', 'test `[ -n "${ORCA_BOT_TOOLS_TOKEN-}" ]`', False),
                                     ('the pane door', 'run `printenv ORCA_TERMINAL_HANDLE`; if `ORCA_BOT_TOOLS_TOKEN` is set', False)]:
            with self.subTest(label):
                self.assertEqual(bool(printing.search(sample)), leaks)

    def test_the_bot_kit_carries_the_soul_the_deny_file_and_the_app_settings(self):
        kit_path = ROOT / 'docs/orca-bots.md'
        self.assertTrue(kit_path.is_file())
        kit = kit_path.read_text()
        blocks = re.findall(r'```(\w+)\n(.*?)```', kit, re.S)
        languages = [language for language, _ in blocks]
        self.assertEqual(languages, ['markdown', 'json'])
        soul, deny = blocks[0][1], json.loads(blocks[1][1])
        with self.subTest('the deny file is the four connector prefixes'):
            self.assertEqual(deny, {'permissions': {'deny': [
                'mcp__claude_ai_Gmail', 'mcp__claude_ai_Google_Drive',
                'mcp__claude_ai_Google_Calendar', 'mcp__claude_ai_Slack']}})
            self.assertIn('.claude/settings.local.json', kit)
            self.assertIn('does not reach a worker', kit)
        with self.subTest('the SOUL text carries each rule and no version'):
            for phrase in ['I serve one project', 'edit none of it', 'the mode file that the session start message named',
                           'The evidence folder is the record', 'transport, not proof', '.hstack/models.md',
                           'never into my memory', 'at most 4 workers', 'an arena pair counts as 2', 'never poll',
                           '`orca bot work list`', 'needs you', 'a recommended one',
                           'only when the owner typed the go-ahead in this chat for that job',
                           'a handoff, a schedule, an event or a webhook holds', 'PR title and body',
                           '`orca worktree rm --delete-branch` and never `--force`', '::orca-visual',
                           'never ask for, accept or type a password or token', 'merge a PR or cut a release',
                           'Gmail, Google Drive, Google Calendar or Slack', 'a fresh worker that did not write the code']:
                self.assertIn(phrase, soul, phrase)
            self.assertIsNone(re.search(r'\d+\.\d+\.\d+', soul))
        with self.subTest('the app settings are listed'):
            for setting in ['Model and effort', 'Permission mode', 'Look around', 'Reports']:
                self.assertRegex(kit, r'(?m)^\| ' + setting + r' \|')
            self.assertIn('`judgment and prose`', kit)
        with self.subTest('the kit links the page and the ADR, adds no setup skill and names no private path'):
            for link in ['../plugin/adapters/hosts/orca-bot.md', 'adr/0007-an-orca-bot-uses-supervised-workers-as-transport.md']:
                self.assertIn(f']({link})', kit)
                self.assertTrue((kit_path.parent / link).is_file(), link)
            self.assertIsNone(re.search(r'/Users/|/home/|\S+@\S+\.\w+', kit))
            self.assertNotIn('host page', kit.lower())


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
    # The bot variable observed set in a bot chat on Orca 1.4.271 and unset in a pane. It
    # is a secret, so every value in these tests is made up.
    BOT_VARIABLE = 'ORCA_BOT_TOOLS_TOKEN'
    BOT_SECRET = 'bot-token-canary-3f9c71d2'
    MODE = ROOT / 'plugin/skills/hugues-mode/SKILL.md'

    def run_hook(self, env=None, root=None):
        environment = dict(os.environ)
        for name in (*self.ORCA_VARIABLES, self.BOT_VARIABLE):
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
        for label, env in [('a pane', {'ORCA_TERMINAL_HANDLE': 'probe-value'}),
                           ('a bot chat', {self.BOT_VARIABLE: self.BOT_SECRET})]:
            context = self.context(self.run_hook(env)).replace(str(ROOT / 'plugin'), '')
            for page in ['hosts/orca.md', 'hosts/orca-bot.md', 'hosts/t3-code.md', 'hosts/omp.md']:
                with self.subTest(label=label, page=page):
                    self.assertNotIn(page, context)
            for word in ['must', 'required', 'never', 'shall', 'only', 'always', 'mandatory',
                         'approve', 'permission', 'allow', 'gate', 'block']:
                with self.subTest(label=label, word=word):
                    self.assertNotIn(word, context.lower())

    def test_the_bot_token_alone_triggers_the_door_and_names_two_files(self):
        index = str(ROOT / 'plugin/adapters/hosts/README.md')
        self.assertTrue(self.MODE.is_file())
        with self.subTest('the token alone is a bot chat'):
            result = self.run_hook({self.BOT_VARIABLE: self.BOT_SECRET})
            self.assertEqual(result.returncode, 0, result.stderr)
            context = self.context(result)
            self.assertIn(index, context)
            self.assertIn(str(self.MODE), context)
            self.assertLess(context.index(index), context.index(str(self.MODE)))
            self.assertIn('This is an Orca bot chat.', context)
        for name in self.ORCA_VARIABLES:
            with self.subTest(f'the token beside {name} is a pane'):
                result = self.run_hook({self.BOT_VARIABLE: self.BOT_SECRET, name: 'probe-value'})
                self.assertEqual(result.returncode, 0, result.stderr)
                context = self.context(result)
                self.assertIn(index, context)
                self.assertNotIn(str(self.MODE), context)
                self.assertNotIn('hugues-mode', context)
                self.assertNotIn('bot chat', context)
                self.assertEqual(context, self.context(self.run_hook({name: 'probe-value'})))
        with self.subTest('a pane names the index and not the mode file'):
            context = self.context(self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value'}))
            self.assertIn(index, context)
            self.assertNotIn('hugues-mode', context)
        with self.subTest('an empty token is not a bot chat'):
            result = self.run_hook({self.BOT_VARIABLE: ''})
            self.assertEqual(result.stdout, '')

    def test_the_hook_never_prints_the_bot_token(self):
        # The fake python3 forces the sed fallback, which is the second encoder.
        with tempfile.TemporaryDirectory() as stub_dir:
            stub = Path(stub_dir) / 'python3'
            stub.write_text('#!/bin/sh\nexit 49\n')
            stub.chmod(0o755)
            for encoder, extra in [('python3', {}),
                                   ('the sed fallback', {'PATH': stub_dir + os.pathsep + os.environ['PATH']})]:
                for label, root in [('a plain path', ROOT / 'plugin'),
                                    ('a path holding a quote and a backslash', '/tmp/we"ird\\path')]:
                    with self.subTest(encoder=encoder, path=label):
                        result = self.run_hook({self.BOT_VARIABLE: self.BOT_SECRET, **extra}, root=root)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertNotIn(self.BOT_SECRET, result.stdout)
                        self.assertNotIn(self.BOT_SECRET, result.stderr)
                        context = self.context(result)
                        self.assertIn(f'{root}/skills/hugues-mode/SKILL.md', context)
        with self.subTest('the token beside a pane variable is never printed either'):
            result = self.run_hook({self.BOT_VARIABLE: self.BOT_SECRET, 'ORCA_TAB_ID': 'probe-value'})
            self.assertNotIn(self.BOT_SECRET, result.stdout + result.stderr)
        with self.subTest('the script holds the name only in a set test'):
            for line in self.HOOK.read_text().splitlines():
                if self.BOT_VARIABLE in line and not line.lstrip().startswith('#'):
                    self.assertIn('[ -n "${ORCA_BOT_TOOLS_TOKEN:-}" ]', line)

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
        written = {name for name in (*self.ORCA_VARIABLES, self.BOT_VARIABLE) if name in door}
        self.assertEqual(written, {*self.ORCA_VARIABLES, self.BOT_VARIABLE})
        for name in (*self.ORCA_VARIABLES, self.BOT_VARIABLE):
            with self.subTest(variable=name):
                self.assertIn(name, self.HOOK.read_text())
        with self.subTest('the written door tests the token and prints a pane variable only'):
            self.assertIn('printenv ORCA_TERMINAL_HANDLE ORCA_PANE_KEY ORCA_TAB_ID`', door)
            self.assertNotIn('printenv ' + self.BOT_VARIABLE, door)
            self.assertIn('test it with `[ -n "${ORCA_BOT_TOOLS_TOKEN-}" ]`, never print it', door)

    def test_the_message_survives_a_plugin_path_holding_json_characters(self):
        # The plugin root is a filesystem path, so it may hold a quote or a
        # backslash. A hand-built JSON string breaks the moment it does.
        result = self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value'},
                                root='/tmp/we"ird\\path')
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        context = payload['hookSpecificOutput']['additionalContext']
        self.assertIn('/tmp/we"ird\\path/adapters/hosts/README.md', context)

    def test_a_python3_that_exists_but_cannot_run_falls_back_to_the_encoder_in_shell(self):
        # Windows puts a Microsoft Store stub named python3 on PATH. It passes
        # `command -v`, prints an install prompt and exits 49.
        with tempfile.TemporaryDirectory() as stub_dir:
            stub = Path(stub_dir) / 'python3'
            stub.write_text('#!/bin/sh\necho "Python was not found" >&2\nexit 49\n')
            stub.chmod(0o755)
            result = self.run_hook({'ORCA_TERMINAL_HANDLE': 'probe-value',
                                    'PATH': stub_dir + os.pathsep + os.environ['PATH']})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('/adapters/hosts/README.md', self.context(result))

    def test_the_hook_says_nothing_without_a_plugin_root(self):
        # A relative path would send the session to an index guessed from the
        # working directory, which is worse than no message at all.
        for label, variable, value in [('a pane', 'ORCA_TERMINAL_HANDLE', 'probe-value'),
                                       ('a bot chat', self.BOT_VARIABLE, self.BOT_SECRET)]:
            with self.subTest(label):
                environment = dict(os.environ)
                for name in (*self.ORCA_VARIABLES, self.BOT_VARIABLE):
                    environment[name] = ''
                environment[variable] = value
                environment.pop('CLAUDE_PLUGIN_ROOT', None)
                result = subprocess.run(['bash', str(self.HOOK)], capture_output=True, text=True,
                                        env=environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, '')

    def run_hook_with_only(self, env, script=None):
        """Run the hook with every Orca variable removed, not emptied, then set `env`."""
        environment = dict(os.environ)
        for name in (*self.ORCA_VARIABLES, self.BOT_VARIABLE):
            environment.pop(name, None)
        environment.update(env)
        environment['CLAUDE_PLUGIN_ROOT'] = str(ROOT / 'plugin')
        return subprocess.run(['bash', str(script or self.HOOK)], capture_output=True, text=True,
                              env=environment)

    def test_a_token_missing_from_the_environment_is_not_a_bot_chat(self):
        # An empty variable and a missing one differ: `${NAME:-}` reads both, a bare `$NAME`
        # under `set -u` fails on the missing one. Every case here removes the key.
        index = str(ROOT / 'plugin/adapters/hosts/README.md')
        with self.subTest('no Orca variable at all'):
            result = self.run_hook_with_only({})
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))
        with self.subTest('a pane variable and no token key'):
            result = self.run_hook_with_only({'ORCA_PANE_KEY': 'probe-value'})
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            self.assertIn(index, self.context(result))
            self.assertNotIn('hugues-mode', self.context(result))
        with self.subTest('the token and no pane variable key'):
            result = self.run_hook_with_only({self.BOT_VARIABLE: self.BOT_SECRET})
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            self.assertIn(str(self.MODE), self.context(result))
            self.assertNotIn(self.BOT_SECRET, result.stdout)

    def test_a_bare_reference_to_a_missing_variable_would_fail_under_set_u(self):
        # Proves the case above can fail: the same script with the token read bare dies on an
        # environment that lacks the key, and the real script does not.
        script = self.HOOK.read_text()
        self.assertIn('set -u', script)
        self.assertNotRegex(script, r'\$\{?ORCA_BOT_TOOLS_TOKEN\}?(?![\w:-])')
        bare = '${ORCA_BOT_TOOLS_TOKEN:-}'
        self.assertIn(bare, script)
        with tempfile.TemporaryDirectory() as directory:
            mutant = Path(directory) / 'host-detect.sh'
            mutant.write_text(script.replace(bare, '$ORCA_BOT_TOOLS_TOKEN'))
            for label, env in [('no Orca variable', {}), ('a pane variable', {'ORCA_TAB_ID': 'probe-value'})]:
                with self.subTest(label):
                    broken = self.run_hook_with_only(env, mutant)
                    self.assertNotEqual(broken.returncode, 0, broken.stdout)
                    self.assertIn('unbound variable', broken.stderr)
                    fine = self.run_hook_with_only(env)
                    self.assertEqual(fine.returncode, 0, fine.stderr)

    def test_the_hook_adds_no_always_read_bytes_to_the_host_adapters(self):
        # The hook's message is delivered by the host, not by an adapter every
        # session reads, so neither host.md nor mobile.md grows for it.
        for relative in ('plugin/adapters/host.md', 'plugin/adapters/mobile.md'):
            with self.subTest(path=relative):
                self.assertNotIn('host-detect.sh', (ROOT / relative).read_text())
        # host.md, which every session reads, carries none of the detection.
        self.assertNotIn('ORCA_TERMINAL_HANDLE', (ROOT / 'plugin/adapters/host.md').read_text())
