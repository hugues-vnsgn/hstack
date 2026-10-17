"""Claude review regressions; task-owned synthetic inputs only."""
import json
import os
import py_compile
from pathlib import Path
import stat
import unittest
from unittest.mock import patch

import test_host_adapters as fixtures
from test_host_adapters import InstalledFixture
from runtime import activity
from runtime.json_input import load_json


class PayloadReview(InstalledFixture, unittest.TestCase):
    def test_cli_ignores_poisoned_valid_runtime_bytecode(self):
        for name in ['__init__.py', 'json_input.py', 'activity.py', 'payload.py']:
            path = self.plugin / 'adapters/runtime' / name
            body, metadata = path.read_bytes(), path.stat()
            poison = b'raise RuntimeError\n'
            self.assertGreaterEqual(len(body), len(poison))
            path.write_bytes(poison + b' ' * (len(body) - len(poison)))
            os.utime(path, ns=(metadata.st_atime_ns, metadata.st_mtime_ns))
            cache = py_compile.compile(str(path), doraise=True,
                                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
            path.write_bytes(body)
            os.utime(path, ns=(metadata.st_atime_ns, metadata.st_mtime_ns))
            self.assertTrue(Path(cache).is_file())
        result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (self.plugin / 'skills/hugues-mode/playbooks/feature.md').read_text())
        self.assertEqual(self.run_tool('bind').stdout, self.binding.read_text())

    def test_every_effective_adapter_and_bridge_is_bound(self):
        for name in ['adapters/mobile.md', 'skills/hugues-mode/SKILL.md',
                     'skills/hugues-mode/playbooks/multi-phase-plan.md']:
            with self.subTest(name=name):
                path = self.plugin / name
                original = path.read_bytes()
                path.write_bytes(original + b'\ndrift\n')
                self.assertEqual(self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').returncode, 2)
                path.write_bytes(original)

    def test_extra_core_file_and_non_executable_permission_changes_hold(self):
        extra = self.plugin / 'skills/hugues-mode/unapproved.md'
        extra.write_text('not pinned')
        self.assertEqual(self.run_tool('bind').returncode, 2)
        extra.unlink()
        cache = self.plugin / 'skills/hugues-mode/__pycache__'
        cache.mkdir()
        (cache / 'extra.pyc').write_bytes(b'not pinned')
        self.assertEqual(self.run_tool('bind').returncode, 2)
        (cache / 'extra.pyc').unlink()
        cache.rmdir()
        for name in ['skills/hugues-mode/playbooks/feature.md', 'skills/hugues-mode/SKILL.md']:
            path = self.plugin / name
            mode = stat.S_IMODE(path.stat().st_mode)
            path.chmod(0o600)
            self.assertEqual(self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md').returncode, 2)
            path.chmod(mode)

    def test_plain_plan_paths_resolve_to_installed_sources(self):
        source = 'skills/hugues-mode/playbooks/feature.md'
        plan = self.consumer / 'plan.md'
        plan.write_text(f'Read `{source}`.\n`git show origin/main:{source}`\nConsumer git show origin/main:PLAN.md\n')
        result = self.bound('translate-plan', plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(self.plugin / source), result.stdout)
        self.assertIn('read-workflow --binding', result.stdout)
        self.assertIn('git show origin/main:PLAN.md', result.stdout)


class ActivityReview(unittest.TestCase):
    def test_duplicate_keys_and_deep_json_hold(self):
        for text in ['{"content":"retained","content":"lost"}', '[' * 10000 + '0' + ']' * 10000,
                     '[' * 65 + '0' + ']' * 65]:
            with self.assertRaises(ValueError):
                load_json(text)

    def test_unknown_pr_or_merge_precedes_scratch_and_recent_advice(self):
        for pr, merged in [('UNKNOWN', True), ('NONE', None)]:
            for recent in [False, True]:
                self.assertEqual(activity.classify('scratch:1', pr, merged, True, recent), 'hold-metadata-unavailable')


class ActivityFixtureReview(unittest.TestCase):
    setUp = fixtures.SyntheticActivity.setUp
    scan = fixtures.SyntheticActivity.scan
    claude = fixtures.SyntheticActivity.claude

    def test_punctuation_and_xml_mentions_are_recent(self):
        for text in [str(self.wt) + suffix for suffix in ['.', '?', '!', '<', '>']] + [f'<path>{self.wt}</path>']:
            row = self.claude(cwd=str(self.area), message={'content': text})
            hits, _, complete = self.scan('claude', [row])
            self.assertTrue(complete)
            self.assertTrue(hits[str(self.wt)], text)

    def test_case_variants_use_filesystem_identity(self):
        self.wt.mkdir()
        alias = Path(str(self.wt).upper())
        self.assertTrue(activity.contains_worktree(self.wt.parent, self.wt))
        same = alias.exists() and alias.samefile(self.wt)
        self.assertEqual(activity.mentions_worktree(str(alias), self.wt), same)
        self.assertEqual(activity.contains_worktree(alias, self.wt), same)
        with patch.object(Path, 'samefile', return_value=False):
            self.assertFalse(activity.mentions_worktree(str(alias), self.wt))
        with patch.object(Path, 'samefile', return_value=True):
            self.assertTrue(activity.mentions_worktree(str(alias), self.wt))

    def test_empty_file_list_empty_and_whitespace_transcripts_hold(self):
        source = self.area / 'empty.jsonl'
        for files, text in [([], ''), ([str(source)], ''), ([str(source)], ' \n\t')]:
            source.write_text(text)
            _, _, complete = activity.scan({'coverage': 'complete', 'sources': [
                {'provider': 'claude', 'files': files, 'authorization': 'synthetic', 'coverage': 'complete'}]}, [self.wt], self.now)
            self.assertFalse(complete)

    def test_duplicate_record_keys_cannot_hide_a_mention(self):
        source = self.area / 'ambiguous.jsonl'
        source.write_text('{"type":"assistant","message":{"content":' + json.dumps(str(self.wt)) + ',"content":"elsewhere"}}\n')
        _, reports, complete = activity.scan({'coverage': 'complete', 'sources': [
            {'provider': 'claude', 'files': [str(source)], 'authorization': 'synthetic', 'coverage': 'complete'}]}, [self.wt], self.now)
        self.assertFalse(complete)
        self.assertIn('duplicate JSON key', reports[0]['error'])


class AuditReview(InstalledFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.consumer / "README.md").write_text("fixture\n")
        self.git("add", "README.md")
        self.git("commit", "-m", "fixture")
        self.wt = self.area / "scratch worktree with spaces"
        self.git("worktree", "add", "-b", "scratch", str(self.wt))
        self.sources = self.area / "sources.json"
        self.prs = self.area / "prs.json"
        self.prs.write_text(json.dumps({"coverage": "complete", "states": {"main": "NONE", "scratch": "NONE"}}))

    git = fixtures.ConsumerAudit.git
    audit = fixtures.ConsumerAudit.audit

    def valid_sources(self):
        path = self.area / 'old.jsonl'
        path.write_text(json.dumps({'type': 'summary', 'summary': 'old unrelated record', 'timestamp': '2020-01-01T00:00:00Z'}) + '\n')
        return {'schema_version': 1, 'coverage': 'complete', 'sources': [
            {'provider': 'claude', 'files': [str(path)], 'authorization': 'synthetic', 'coverage': 'complete'}]}

    def test_unreadable_missing_invalid_pr_metadata_exits_two_for_scratch(self):
        (self.wt / 'scratch.txt').write_text('retained')
        for body in [None, '{', '{}', '{"coverage":"complete","states":{"scratch":[]}}',
                     '[' * 2000 + '0' + ']' * 2000]:
            if body is None:
                self.prs.unlink(missing_ok=True)
            else:
                self.prs.write_text(body)
            result, report = self.audit(self.valid_sources())
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(report['coverage'], 'complete')
            self.assertEqual(report['metadata_coverage'], 'unavailable')
            self.assertEqual(report['worktrees'][1]['bucket'], 'hold-metadata-unavailable')

    def test_deep_transcript_and_sources_exit_two(self):
        manifest = self.valid_sources()
        Path(manifest['sources'][0]['files'][0]).write_text(
            '{"type":"assistant","message":{"content":[{"type":"tool_use",'
            '"name":"Bash","input":{"command":' + '[' * 2000 + '0' + ']' * 2000 + '}}]}}')
        result, report = self.audit(manifest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(report['coverage'], 'unavailable')
        self.sources.write_text('[' * 2000 + '0' + ']' * 2000)
        result = self.bound('worktree-audit', '--repo', self.consumer, '--sources', self.sources, '--pr-snapshot', self.prs, '--base', 'main')
        self.assertEqual(result.returncode, 2, result.stderr)


if __name__ == '__main__':
    unittest.main()
