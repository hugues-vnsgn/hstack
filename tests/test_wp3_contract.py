"""Run the package checker against WP3 leaf/reference mutations.

These observe metadata and link validation, not model or native app behavior.
No consumer files, network, report parser or evidence runtime are required.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from release_snapshot import release_root
ROOT = release_root()
GENERATOR = Path('plugin/skills/create-verification-skill/SKILL.md')


class WP3PackageRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-wp3-check-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.repo,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
        self.valid_package()

    def check(self):
        return subprocess.run(['sh', str(self.repo / 'scripts/check-plugin.sh'), str(self.repo)],
                              cwd=self.temp.name, capture_output=True, text=True)

    def valid_package(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS: manifests,', result.stdout)

    def rejected(self, reason):
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(reason, result.stderr)

    def test_generator_discovered_by_manifest_paths(self):
        manifest = json.loads((self.repo / 'plugin/.claude-plugin/plugin.json').read_text())
        directories = manifest['skills']
        if isinstance(directories, str):
            directories = [directories]
        discovered = set()
        for relative in directories:
            discovered.update((self.repo / 'plugin' / relative).rglob('SKILL.md'))
        self.assertIn(self.repo / GENERATOR, discovered)
        self.valid_package()

    def test_removed_generator_breaks_real_mode_and_authoring_links(self):
        (self.repo / GENERATOR).unlink()
        self.rejected('broken local link')
        result = self.check()
        self.assertIn('plugin/skills/hugues-mode/SKILL.md:', result.stderr)
        self.assertIn('playbooks/authoring-a-skill.md:', result.stderr)

    def test_missing_wp3_references_rejected(self):
        for relative in [
            'plugin/skills/create-verification-skill/references/project-skill-template.md',
            'plugin/skills/hugues-mode/references/evidence-guide.md',
            'plugin/skills/hugues-mode/references/evidence-template.md',
            'plugin/skills/hugues-mode/references/jev-drive.md',
        ]:
            with self.subTest(reference=relative):
                path = self.repo / relative
                original = path.read_bytes()
                path.unlink()
                self.rejected('broken local link')
                path.write_bytes(original)
                self.valid_package()

    def test_generator_missing_frontmatter_rejected(self):
        path = self.repo / GENERATOR
        path.write_text(path.read_text().split('---', 2)[2].lstrip())
        self.rejected('create-verification-skill/SKILL.md: missing frontmatter')

    def test_missing_pr_review_policy_breaks_workflow_links(self):
        path = self.repo / 'plugin/skills/hugues-mode/references/pr-review-policy.md'
        path.unlink()
        self.rejected('broken local link')
        result = self.check()
        self.assertIn('playbooks/opening-a-pr.md:', result.stderr)
        self.assertIn('plugin/skills/interrogate/SKILL.md:', result.stderr)

    def test_generator_wrong_registration_name_rejected(self):
        path = self.repo / GENERATOR
        path.write_text(path.read_text().replace('name: create-verification-skill',
                                                 'name: verify-project'))
        self.rejected('name must match skill folder')

    def test_generator_invalid_invocation_flag_rejected(self):
        path = self.repo / GENERATOR
        path.write_text(path.read_text().replace('disable-model-invocation: true',
                                                 'disable-model-invocation: sometimes'))
        self.rejected('expected boolean disable-model-invocation')

    def test_broken_evidence_anchor_rejected(self):
        path = self.repo / 'plugin/skills/hugues-mode/references/evidence-guide.md'
        path.write_text(path.read_text().replace('mobile-lanes.md#evidence-and-outcomes',
                                                 'mobile-lanes.md#invented-proof'))
        self.rejected('missing heading mobile-lanes.md#invented-proof')

    def test_generator_private_absolute_link_rejected(self):
        path = self.repo / GENERATOR
        path.write_text(path.read_text() + '\n[consumer](/private/consumer/SKILL.md)\n')
        self.rejected('absolute local link /private/consumer/SKILL.md')

    def test_template_loader_example_does_not_register_extra_skill(self):
        before = self.check()
        path = self.repo / 'plugin/skills/create-verification-skill/references/project-skill-template.md'
        path.write_text(path.read_text() + '\n```markdown\n[example](missing-local-file.md)\n```\n')
        after = self.check()
        self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
        self.assertEqual(after.stdout, before.stdout)


class WP3GuidanceContracts(unittest.TestCase):
    def test_mobile_proof_consumes_project_recipe_directly(self):
        body = (ROOT / 'plugin/skills/hugues-mode/playbooks/mobile-proof.md').read_text()
        first = body.split('1. ', 1)[1].split('\n2. ', 1)[0]
        for required in ('verify-<app>/SKILL.md', '.agents/skills', '.claude/skills',
                         'Read that recipe directly', 'current authority'):
            self.assertIn(required, first)

    def test_proof_steps_link_evidence_and_jev(self):
        body = (ROOT / 'plugin/skills/hugues-mode/playbooks/mobile-proof.md').read_text()
        self.assertIn('[durable evidence guide](../references/evidence-guide.md)', body)
        self.assertIn('[jev Drive](../references/jev-drive.md)', body)
        doctor = (ROOT / 'plugin/skills/hugues-mode/playbooks/build-doctor.md').read_text()
        self.assertIn('[evidence guide](../references/evidence-guide.md)', doctor)

    def test_jev_transmission_uses_existing_authority_or_acceptance(self):
        body = (ROOT / 'plugin/skills/hugues-mode/references/jev-drive.md').read_text()
        for required in ("existing explicit authority covers checkpoint screen-text transmission",
                         'Do not ask again', "obtain the owner's acceptance before sending screen text",
                         'keep judged proof blocked', 'permitted local fallback'):
            self.assertIn(required, body)

    def test_generator_honors_repository_layout_and_loader_limits(self):
        body = (ROOT / GENERATOR).read_text()
        for required in ('canonical skill layout first', 'preserve that convention',
                         'Verify the link resolves inside the consumer worktree',
                         'native discovery as unrun', 'compare body hashes',
                         'pstack 0.15.5 at `2eb7ed4613cfc8f098dfe464a23680ea44d84c5e`'):
            self.assertIn(required, body)

    def test_receipts_have_real_destinations_and_operation_provenance(self):
        receipts = json.loads((ROOT / 'docs/wp3-source-receipts.json').read_text())
        operations = set()
        for item in receipts['inputs']:
            for relative in item['destinations']:
                path = Path(relative)
                self.assertFalse(path.is_absolute())
                self.assertNotIn('..', path.parts)
                self.assertTrue((ROOT / path).is_file(), relative)
            if item.get('observed_tool_names'):
                self.assertTrue(item.get('source_sections'), item['source'])
                operations.update(item['observed_tool_names'])
        self.assertEqual(operations, {'start_scenario', 'get_report', 'cancel_run', 'resolve_step'})
        cli = next(item for item in receipts['inputs'] if item['source'] == 'dist/cli.js')
        self.assertEqual(cli['observed_help_exit_code'], 0)
        self.assertEqual(cli['observed_help_version'], 'jev-ios-bridge 1.3.0')
        self.assertTrue(any(usage.startswith('run <script.json>') for usage in cli['observed_help_usage']))
        self.assertIn('report <run-id> [--json]', cli['observed_help_usage'])


if __name__ == '__main__':
    unittest.main()
