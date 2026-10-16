import sys
"""Mutate isolated package copies to exercise the static safety boundaries."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main()
