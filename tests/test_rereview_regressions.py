import json
import runpy
import shlex
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote
import test_host_adapters as fixtures
from test_host_adapters import InstalledFixture
from runtime import activity


class BootstrapBoundary(InstalledFixture, unittest.TestCase):
    def test_runtime_drift_is_rejected_before_any_module_executes(self):
        marker = self.area / 'executed'
        for module in ['__init__.py', 'json_input.py', 'activity.py', 'payload.py']:
            path = self.plugin / 'adapters/runtime' / module
            original = path.read_bytes()
            malicious = "\nfrom pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('executed')\n"
            path.write_bytes(original + malicious.encode())
            with self.subTest(module=module):
                result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(marker.exists(), 'unapproved module executed before rejection')
            path.write_bytes(original)
            marker.unlink(missing_ok=True)

    def test_all_sources_verified_before_compile_and_verified_buffers_are_used(self):
        namespace = runpy.run_path(str(self.helper))
        path = self.plugin / 'adapters/runtime/payload.py'
        original = path.read_bytes()
        path.write_bytes(original + b'\ndrift\n')
        with patch('builtins.compile') as compiler:
            with self.assertRaises(ValueError):
                namespace['load_runtime_sources'](self.binding)
            compiler.assert_not_called()
        path.write_bytes(original)
        original_compile = compile
        def replace_after_verification(body, filename, mode):
            path.write_text('raise RuntimeError("unverified reopened source")\n')
            return original_compile(body, filename, mode)
        with patch('builtins.compile', side_effect=replace_after_verification):
            _, loaded = namespace['load_runtime_sources'](self.binding)
        self.assertTrue(callable(loaded.bind))

    def test_initial_bind_rejects_unapproved_runtime(self):
        path = self.plugin / 'adapters/runtime/payload.py'
        path.write_text(path.read_text() + '\nload_binding = lambda *args: None\n')
        self.assertEqual(self.run_tool('bind').returncode, 2)


class PlanOwnership(InstalledFixture, unittest.TestCase):
    source = 'skills/hugues-mode/playbooks/feature.md'

    def translate(self, text):
        plan = self.consumer / 'plan.md'
        plan.write_text(text)
        return self.bound('translate-plan', plan)

    def test_consumer_owned_paths_revisions_and_prefixes_are_preserved(self):
        for text in ['`pstack/notes/todo.md`', 'cat pstack/notes/todo.md',
                     'git show origin/main:pstack/notes/todo.md',
                     'git show main:docs/feature.md', '`git show HEAD:docs/feature.md`',
                     '`foo-' + self.source + '`', 'foo-' + self.source]:
            with self.subTest(text=text):
                result = self.translate(text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, text)

    def test_plain_and_cat_rereads_remain_guarded_with_spaces(self):
        for text in ['`' + self.source + '`', 'cat "' + self.source + '"']:
            result = self.translate(text)
            self.assertEqual(result.returncode, 0, result.stderr)
            command = result.stdout.strip('`')
            args = shlex.split(command)
            self.assertIn('read-workflow', args)
            read = subprocess.run(args, cwd=self.consumer, capture_output=True, text=True)
            self.assertEqual(read.returncode, 0, read.stderr)
            self.assertEqual(read.stdout, (self.plugin / self.source).read_text())
            self.assertEqual(self.translate(result.stdout).stdout, result.stdout)
        result = self.translate('cat ' + self.source + '\n\ngit show origin/main:' + self.source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count(' read-workflow '), 2)
        result = self.translate("The operator's plan reads `" + self.source + "`.\nOther prose remains.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(' read-workflow ', result.stdout)
        (self.consumer / '--help').write_text('invalid plan\n')
        translated = self.translate('node pstack/skills/poteto-mode/scripts/check-plan.mjs --help')
        self.assertEqual(translated.returncode, 0, translated.stderr)
        helper_args = shlex.split(translated.stdout)
        checked = subprocess.run(helper_args, cwd=self.consumer, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
        helper_args[helper_args.index('--binding') + 1] = str(self.area / 'missing-binding.json')
        checked = subprocess.run(helper_args, cwd=self.consumer, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 2, checked.stdout + checked.stderr)
        path = self.plugin / self.source
        path.write_text(path.read_text() + '\ndrift\n')
        read = subprocess.run(args, cwd=self.consumer, capture_output=True, text=True)
        self.assertEqual(read.returncode, 2)

    def test_unresolved_bundled_shell_shape_holds(self):
        for text in ['cat ' + self.source + ' && echo done',
                     'git show origin/main:' + self.source + ';',
                     'git show origin/main:' + self.source + '|cat',
                     'git show origin/main:' + self.source + ';id',
                     'git show origin/main:' + self.source + '; id',
                     'git show origin/main:' + self.source + '| cat',
                     'node pstack/skills/poteto-mode/scripts/check-plan.mjs; true',
                     'git show HEAD:README.md;cat<' + self.source,
                     'cat pstack/skills/"swarm"/SKILL.md;id',
                     *['node pstack/skills/poteto-mode/scripts/check-plan.mjs ' + operand
                       for operand in ['plan.md;id', 'plan.md|cat', 'plan.md>out',
                                       '"$PLAN"', '*.md', '~/plan.md']],
                     'cat ' + self.source + ' `printf extra`',
                     'cat ' + self.source + ' && echo `date`',
                     'cat ' + chr(92) + '\n' + self.source,
                     'cat <<EOF\n' + self.source + '\nEOF',
                     *['cat ' + quote + '\n' + self.source + '\n' + quote for quote in [chr(39), chr(34)]],
                     'echo "$(\ncat ' + self.source + '\n)"',
                     'echo `\ncat ' + self.source + '\n`',
                     'true &&\ncat ' + self.source,
                     'cat "\n\n' + self.source + '\n\n"',
                     'Narrative\ncat ' + self.source,
                     'Narrative\n\ncat ' + self.source]:
            with self.subTest(text=text):
                result = self.translate(text)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_mobile_authored_template_exists_in_current_payload(self):
        path = self.plugin / 'skills/create-verification-skill/references/project-skill-template.md'
        self.assertTrue(path.is_file())
        self.assertIn('explicitly requested one-journey diagnostic', path.read_text())
        self.assertIn('[mobile workflows](mobile-workflows.md) in full', (self.plugin / 'adapters/mobile.md').read_text())
        self.assertIn('project-skill-template.md', (self.plugin / 'adapters/mobile-workflows.md').read_text())


class ActivityRepresentations(unittest.TestCase):
    setUp = fixtures.SyntheticActivity.setUp
    scan = fixtures.SyntheticActivity.scan
    claude = fixtures.SyntheticActivity.claude

    def test_markdown_shell_and_unicode_delimiters_do_not_hide_activity(self):
        for suffix in ['**', '&&', '|', '*', '#', '=', '(', '\\', '”', '’', '。', '，', '！']:
            with self.subTest(suffix=suffix):
                hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.area / 'unrelated'), message={'content': '**' + str(self.wt) + suffix})])
                self.assertTrue(hits[str(self.wt)] or not complete)

    def test_percent_encoded_paths_do_not_hide_activity(self):
        for path in [quote(str(self.wt)), quote(str(self.wt), safe=''), quote(quote(str(self.wt), safe=''), safe='')]:
            hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.area / 'unrelated'), message={'content': path})])
            self.assertTrue(hits[str(self.wt)] or not complete)

    def test_home_relative_mentions_do_not_establish_idle_coverage(self):
        with patch.object(Path, 'home', return_value=self.area):
            hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.area / 'unrelated'), message={'content': '~/' + self.wt.name})])
        self.assertTrue(hits[str(self.wt)] or not complete)
        home_link = self.area / 'home-link'
        home_link.symlink_to(self.area, target_is_directory=True)
        for home, mention in [(home_link, '~/' + self.wt.name), (self.wt, '~/notes.md')]:
            with self.subTest(home=home, mention=mention), patch.object(Path, 'home', return_value=home):
                hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.area / 'unrelated'), message={'content': mention})])
                self.assertTrue(hits[str(self.wt)] or not complete)
        hits, _, complete = self.scan('claude', [self.claude(cwd=str(self.area / 'unrelated'), message={'content': '~someone/unknown-worktree'})])
        self.assertFalse(complete)


class MetadataSemantics(InstalledFixture, unittest.TestCase):
    git = fixtures.ConsumerAudit.git
    audit = fixtures.ConsumerAudit.audit

    def setUp(self):
        super().setUp()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Synthetic Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.consumer / 'README.md').write_text('fixture\n')
        self.git('add', 'README.md')
        self.git('commit', '-m', 'fixture')
        self.wt = self.area / 'candidate'
        self.git('worktree', 'add', '-b', 'candidate', str(self.wt))
        self.prs = self.area / 'prs.json'
        self.sources = self.area / 'sources.json'
        self.transcript = self.area / 'old.jsonl'
        self.transcript.write_text('{"type":"summary","summary":"old unrelated text","timestamp":"2020-01-01T00:00:00Z"}\n')
        self.manifest = {'schema_version':1, 'coverage':'complete', 'sources':[{'provider':'claude','files':[str(self.transcript)],'authorization':'synthetic','coverage':'complete'}]}

    def test_main_worktree_metadata_not_required_for_candidate_completeness(self):
        self.prs.write_text(json.dumps({'coverage':'complete','states':{'candidate':'NONE'}}))
        result, report = self.audit(self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['worktrees'][0]['metadata_coverage'], 'not-required')
        self.assertEqual(report['worktrees'][1]['metadata_coverage'], 'complete')

    def test_detached_candidate_can_have_explicit_worktree_state(self):
        self.git('worktree', 'add', '--detach', str(self.area / 'detached'))
        self.prs.write_text(json.dumps({'coverage':'complete','states':{'candidate':'NONE','worktree:' + str(self.area / 'detached'):'NONE'}}))
        result, report = self.audit(self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        row = next(row for row in report['worktrees'] if not row['branch'])
        self.assertEqual(row['pr'], 'NONE')
        self.assertEqual(row['metadata_coverage'], 'complete')

    def test_mixed_candidate_metadata_is_explained_per_row(self):
        self.prs.write_text(json.dumps({'coverage':'complete','states':{}}))
        result, report = self.audit(self.manifest)
        self.assertEqual(result.returncode, 2)
        self.assertIn('pr-state-unknown', report['worktrees'][1]['metadata_errors'])
        self.assertEqual(report['audit_status'], 'hold')


if __name__ == '__main__':
    unittest.main()
