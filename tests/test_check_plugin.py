import sys
"""Mutate isolated package copies to exercise the static safety boundaries."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import seal_payload

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / 'scripts/check-plugin.sh'


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-check-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'package'
        from release_snapshot import release_root
        shutil.copytree(release_root(), self.repo, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
        shutil.copytree(ROOT / 'scripts', self.repo / 'scripts', dirs_exist_ok=True)
        self.mode_body = (self.repo / 'plugin/skills/hugues-mode/SKILL.md').read_text().split('---\n', 2)[2]

    def run_check(self):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_plugin.py'), str(self.repo), '--historical-release-0.1.0'], text=True, capture_output=True)

    def assert_rejected(self, diagnostic):
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def manifest(self, change):
        file = self.repo / 'plugin/.claude-plugin/plugin.json'
        data = json.loads(file.read_text())
        change(data)
        file.write_text(json.dumps(data))

    def skill(self, text):
        # Mutate loader metadata without removing real headings linked by other skills.
        (self.repo / 'plugin/skills/hugues-mode/SKILL.md').write_text(text + self.mode_body)

    def test_valid_package_and_cwd_independence(self):
        result = subprocess.run([sys.executable, str(self.repo / 'scripts/check_plugin.py'), '--historical-release-0.1.0'], cwd=self.temp.name, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.run_check().returncode, 0)

    def test_invalid_json(self):
        (self.repo / 'plugin/.claude-plugin/plugin.json').write_text('{')
        self.assert_rejected('plugin/.claude-plugin/plugin.json')

    def test_duplicate_json_keys(self):
        (self.repo / 'plugin/.claude-plugin/plugin.json').write_text('{"name":"first","name":"second"}')
        self.assert_rejected('duplicate JSON key')

    def test_marketplace_wrong_name(self):
        file = self.repo / '.claude-plugin/marketplace.json'
        data = json.loads(file.read_text())
        data['plugins'][0]['name'] = 'different'
        file.write_text(json.dumps(data))
        self.assert_rejected('plugin name mismatch')

    def test_marketplace_escape(self):
        file = self.repo / '.claude-plugin/marketplace.json'
        data = json.loads(file.read_text())
        data['plugins'][0]['source'] = '../outside'
        file.write_text(json.dumps(data))
        self.assert_rejected('expected source ./plugin')

    def test_manifest_path_boundaries(self):
        for path in ['/tmp', '../outside', './skills/../../outside', './skills\\outside', './%2e%2e/outside', '${ROOT}/skills', './missing']:
            with self.subTest(path=path):
                self.manifest(lambda m: m.update(skills=[path]))
                self.assert_rejected('skills:')

    def test_agent_directory_is_not_file(self):
        self.manifest(lambda m: m.update(agents=['./skills']))
        self.assert_rejected('agents: expected Markdown file')

    def test_unknown_runtime_fields(self):
        self.manifest(lambda m: m.update(hooks={'unsafe': True}))
        self.assert_rejected('unsupported WP1 fields')

    def test_symlink_escape_and_dangling_link(self):
        for name, target in [('outside', self.repo.parent), ('dangling', self.repo.parent / 'missing')]:
            with self.subTest(name=name):
                path = self.repo / name
                path.symlink_to(target, target_is_directory=True)
                self.assert_rejected('symlinks are forbidden')
                path.unlink()

    def test_planning_symlink_is_rejected(self):
        folder = self.repo / 'docs/planning'
        folder.mkdir()
        (folder / 'escape.md').symlink_to('/tmp/missing-hstack-planning')
        self.assert_rejected('symlinks are forbidden')

    def test_missing_and_malformed_frontmatter(self):
        for text in ['# No metadata\n', '---\nname: hugues-mode\ndescription: |\n  multiline\n---\n']:
            with self.subTest(text=text):
                self.skill(text)
                self.assert_rejected('frontmatter' if text.startswith('#') else 'unsupported scalar')

    def test_frontmatter_blank_line_accepted(self):
        for line in ['', '   ', '\t']:
            with self.subTest(line=line):
                self.skill(f'---\nname: hugues-mode\n{line}\ndescription: probe\n---\n')
                result = self.run_check()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_frontmatter_comment_line_accepted(self):
        for line in ['# Loader metadata', '   # Loader metadata']:
            with self.subTest(line=line):
                self.skill(f'---\n{line}\nname: hugues-mode\ndescription: probe\n---\n')
                result = self.run_check()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_frontmatter_allowed_tools_list_rejected(self):
        self.skill('---\nname: hugues-mode\ndescription: probe\nallowed-tools:\n  - Read\n---\n')
        self.assert_rejected('unsupported frontmatter line; WP1 accepts single-line "key: value" scalars')

    def test_frontmatter_duplicate_key_rejected(self):
        self.skill('---\nname: hugues-mode\nname: hugues-mode\ndescription: probe\n---\n')
        self.assert_rejected('invalid or duplicate frontmatter field')

    def test_invalid_skill_name_and_description_types(self):
        for name, description in [('wrong-folder', 'probe'), ('hugues-mode', 'null'), ('hugues-mode', 'true'), ('hugues-mode', '123'), ('hugues-mode', '""')]:
            with self.subTest(name=name, description=description):
                self.skill(f'---\nname: {name}\ndescription: {description}\n---\n')
                self.assert_rejected('name must match' if name == 'wrong-folder' else 'invalid description')

    def test_unterminated_single_quoted_scalars(self):
        for scalar in ["'", "'unterminated quote", "'unterminated escaped quote''"]:
            with self.subTest(scalar=scalar):
                self.skill(f'---\nname: hugues-mode\ndescription: {scalar}\n---\n')
                self.assert_rejected('invalid quoted scalar')

    def test_unescaped_single_quotes_and_trailing_content(self):
        for scalar in ["'can't parse this'", "'closed' trailing", "'closed' 'again'"]:
            with self.subTest(scalar=scalar):
                self.skill(f'---\nname: hugues-mode\ndescription: {scalar}\n---\n')
                self.assert_rejected('invalid quoted scalar')

    def test_valid_single_quoted_scalar_escaping(self):
        for scalar in ["'Review O''Brien: loader # evidence'", "'A trailing apostrophe'''",
                       "'A literal \\n stays on one line'"]:
            with self.subTest(scalar=scalar):
                self.skill(f"---\nname: 'hugues-mode'\ndescription: {scalar}\ndisable-model-invocation: true\n---\n")
                result = self.run_check()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_single_quoted_scalars_decode_only_doubled_apostrophes(self):
        folder = self.repo / 'plugin/skills/other-probe'
        folder.mkdir()
        for quoted, decoded in [("'Review O''Brien'", "Review O'Brien"),
                                ("'A literal \\n stays on one line'", r'A literal \n stays on one line')]:
            with self.subTest(quoted=quoted):
                self.skill(f'---\nname: hugues-mode\ndescription: {quoted}\n---\n')
                (folder / 'SKILL.md').write_text(
                    f'---\nname: other-probe\ndescription: {json.dumps(decoded)}\n---\n')
                self.assert_rejected('duplicate skill description')

    def test_duplicate_skill_name(self):
        folder = self.repo / 'plugin/skills/nested/hugues-mode'
        folder.mkdir(parents=True)
        shutil.copyfile(self.repo / 'plugin/skills/hugues-mode/SKILL.md', folder / 'SKILL.md')
        self.assert_rejected('duplicate skill name')

    def test_duplicate_skill_description(self):
        folder = self.repo / 'plugin/skills/other-probe'
        folder.mkdir()
        text = (self.repo / 'plugin/skills/hugues-mode/SKILL.md').read_text().replace('name: hugues-mode', 'name: other-probe')
        (folder / 'SKILL.md').write_text(text)
        self.assert_rejected('duplicate skill description')

    def test_missing_skill_directory(self):
        shutil.rmtree(self.repo / 'plugin/skills')
        self.assert_rejected('no skills found')

    def test_link_missing_file_and_heading(self):
        for link in ['missing.md', 'README.md#missing-heading']:
            with self.subTest(link=link):
                (self.repo / 'BAD.md').write_text(f'[broken]({link})\n')
                self.assert_rejected('broken local link' if link == 'missing.md' else 'missing heading')

    def test_link_escape_absolute_and_encoded(self):
        for link in ['../outside.md', '%2e%2e/outside.md', '/tmp/outside.md', 'file:///tmp/outside.md', '//outside.example/test.md']:
            with self.subTest(link=link):
                (self.repo / 'BAD.md').write_text(f'[bad]({link})\n')
                result = self.run_check()
                self.assertEqual(result.returncode, 1)
                self.assertRegex(result.stderr, 'escapes root|absolute local|unsupported link')

    def test_reference_links_are_checked(self):
        (self.repo / 'BAD.md').write_text('[broken][target]\n\n[target]: missing.md\n')
        self.assert_rejected('broken local link')
        (self.repo / 'BAD.md').write_text('[broken][unresolved]\n')
        self.assert_rejected('undefined link reference')

    def test_valid_links_code_examples_and_planning_boundary(self):
        (self.repo / 'docs/planning').mkdir()
        (self.repo / 'docs/planning/old.md').write_text('[archived](missing.md)\n')
        (self.repo / 'LINKS.md').write_text('''# Code `heading`

[local](README.md) [heading](#code-heading) [license][notice]
[notice]: LICENSE

```md
[example](missing.md)
```

`[example](missing.md)`
''')
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_plugin_description_must_not_be_empty(self):
        for description in ['', '   ', None]:
            with self.subTest(description=description):
                self.manifest(lambda m: m.update(description=description))
                self.assert_rejected('plugin: missing description')

    def test_marketplace_entry_shape_failure_does_not_traceback(self):
        file = self.repo / '.claude-plugin/marketplace.json'
        data = json.loads(file.read_text())
        data['plugins'] = []
        file.write_text(json.dumps(data))
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertIn('marketplace: expected one plugin entry', result.stderr)


class CursorManifestChecks(unittest.TestCase):
    """The Cursor manifests have their own rules, and each one needs a
    negative test, because a rule nothing exercises is a rule that rots."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='hstack-cursor-manifest-')
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name) / 'package'
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))

    def run_check(self):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_plugin.py'), str(self.repo)],
                              text=True, capture_output=True)

    def assert_rejected(self, diagnostic):
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def write(self, relative, data):
        file = self.repo / relative
        file.write_text(json.dumps(data, indent=2))
        return data

    def cursor_market(self, change):
        file = self.repo / '.cursor-plugin/marketplace.json'
        data = json.loads(file.read_text())
        change(data)
        self.write('.cursor-plugin/marketplace.json', data)

    def cursor_plugin(self, change):
        file = self.repo / 'plugin/.cursor-plugin/plugin.json'
        data = json.loads(file.read_text())
        change(data)
        self.write('plugin/.cursor-plugin/plugin.json', data)

    def test_the_current_cursor_manifests_pass(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_cursor_name_mismatch_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(name='other'))
        self.assert_rejected('cursor plugin: name differs from the Claude manifest')

    def test_a_cursor_version_mismatch_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(version='9.9.9'))
        self.assert_rejected('cursor plugin: version differs from the Claude manifest')

    def test_a_cursor_description_mismatch_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(description='another description'))
        self.assert_rejected('cursor plugin: description differs from the Claude manifest')

    def test_a_cursor_license_mismatch_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(license='Apache-2.0'))
        self.assert_rejected('cursor plugin: license differs from the Claude manifest')

    def test_a_cursor_keyword_mismatch_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(keywords=['mobile']))
        self.assert_rejected('cursor plugin: keywords differ from the Claude manifest')

    def test_an_invalid_cursor_version_string_is_rejected(self):
        self.cursor_plugin(lambda m: m.update(version='not-a-version'))
        self.assert_rejected('cursor plugin: invalid version')

    def test_a_cursor_marketplace_metadata_version_mismatch_is_rejected(self):
        self.cursor_market(lambda m: m['metadata'].update(version='9.9.9'))
        self.assert_rejected('cursor marketplace: metadata version differs from the plugin manifest')

    def test_an_invalid_cursor_marketplace_metadata_version_is_rejected(self):
        self.cursor_market(lambda m: m['metadata'].update(version='v1'))
        self.assert_rejected('cursor marketplace: invalid metadata version')

    def test_a_missing_cursor_marketplace_description_is_rejected(self):
        self.cursor_market(lambda m: m['metadata'].pop('description'))
        self.assert_rejected('cursor marketplace: missing metadata description')

    def test_a_cursor_marketplace_owner_mismatch_is_rejected(self):
        self.cursor_market(lambda m: m.update(owner={'name': 'someone-else'}))
        self.assert_rejected('cursor marketplace: owner differs from the Claude marketplace')

    def test_a_cursor_marketplace_source_outside_the_repository_is_rejected(self):
        self.cursor_market(lambda m: m['plugins'][0].update(source='../outside'))
        self.assert_rejected('cursor marketplace:')

    def test_a_cursor_marketplace_entry_version_mismatch_is_rejected(self):
        self.cursor_market(lambda m: m['plugins'][0].update(version='9.9.9'))
        self.assert_rejected('cursor marketplace entry 0: version differs from the plugin manifest')

    def test_a_cursor_marketplace_entry_shape_failure_does_not_traceback(self):
        self.cursor_market(lambda m: m.update(plugins=[]))
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertIn('cursor marketplace: expected one plugin entry', result.stderr)

    def test_the_cursor_models_reference_is_present(self):
        # The setup skill points at the Cursor model reference. A missing file
        # would break the setup step on Cursor only.
        reference = self.repo / 'plugin/skills/setup-hstack/references/cursor-models.md'
        self.assertTrue(reference.is_file())
        setup = (self.repo / 'plugin/skills/setup-hstack/SKILL.md').read_text()
        self.assertIn('cursor-models.md', setup)
        # The checker's link rule is what catches a missing reference. Removing
        # the file and resealing the payload makes the link the only defect.
        reference.unlink()
        seal_payload.seal(self.repo, accept=['plugin/skills/setup-hstack/references/cursor-models.md'])
        self.assert_rejected('broken local link')


if __name__ == '__main__':
    unittest.main()
