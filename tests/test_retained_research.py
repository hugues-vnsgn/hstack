"""Check retained research package artifacts through shipped checker CLIs.

These tests observe discovery, broken references and provenance acceptance.
Contract mutations exercise receipt binding; they do not execute a model or app
and make no claim that static checks can judge the instruction's semantics.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from release_snapshot import release_root
ROOT = release_root()
RECEIPT = Path('docs/upstream/retained-research-provenance.json')


class RetainedResearchPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-research-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.root,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
        self.package_check()
        self.upstream_check()

    def run_check(self, argv, error=None):
        result = subprocess.run(argv, capture_output=True, text=True)
        if error is None:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(error, result.stderr)
        return result

    def package_check(self, error=None):
        return self.run_check(['sh', str(self.root / 'scripts/check-plugin.sh'),
                               str(self.root)], error)

    def upstream_check(self, error=None):
        return self.run_check([sys.executable, str(self.root / 'scripts/upstream-diff.py'),
                               'check', '--root', str(self.root)], error)

    def test_both_skills_discovered_from_manifest_paths(self):
        manifest = json.loads((self.root / 'plugin/.claude-plugin/plugin.json').read_text())
        directories = manifest['skills']
        if isinstance(directories, str):
            directories = [directories]
        discovered = set()
        for relative in directories:
            discovered.update(path.relative_to(self.root).as_posix()
                              for path in (self.root / 'plugin' / relative).rglob('SKILL.md'))
        self.assertTrue({'plugin/skills/how/SKILL.md', 'plugin/skills/why/SKILL.md'} <= discovered)
        self.assertIn('PASS: manifests,', self.package_check().stdout)

    def test_missing_complex_explorer_reference_rejected(self):
        (self.root / 'plugin/skills/how/references/explorer-prompt.md').unlink()
        result = self.package_check('broken local link')
        self.assertIn('plugin/skills/how/SKILL.md:', result.stderr)
        self.upstream_check('missing/unsafe present destination')

    def test_missing_epistemics_breaks_skill_and_indexed_output(self):
        (self.root / 'plugin/skills/why/references/epistemics.md').unlink()
        result = self.package_check('broken local link')
        self.assertIn('plugin/skills/why/SKILL.md:', result.stderr)
        self.upstream_check('missing/unsafe present destination')

    def test_missing_defensive_incident_reference_rejected(self):
        (self.root / 'plugin/skills/why/references/sources/incident-postmortem.md').unlink()
        result = self.package_check('broken local link')
        self.assertIn('plugin/skills/why/references/source-playbook.md:', result.stderr)

    def test_invalid_direct_read_invocation_metadata_rejected(self):
        path = self.root / 'plugin/skills/how/SKILL.md'
        path.write_text(path.read_text().replace('disable-model-invocation: true',
                                                 'disable-model-invocation: sometimes'))
        self.package_check('expected boolean disable-model-invocation')

    def test_changed_research_contract_requires_new_destination_receipt(self):
        path = self.root / 'plugin/skills/how/SKILL.md'
        original = path.read_text()
        changed = original.replace('Spawn zero explorers', 'Spawn three explorers')
        self.assertNotEqual(changed, original)
        path.write_text(changed)
        self.package_check()
        self.upstream_check('retained destination bytes differ: plugin/skills/how/SKILL.md')

    def test_verbatim_epistemics_cannot_be_rewritten_with_only_new_destination_hash(self):
        path = self.root / 'plugin/skills/why/references/epistemics.md'
        original = path.read_text()
        # Change an actual causal-confidence rule while retaining its links.
        changed = original.replace('Cite the source.', 'Omit the source.')
        self.assertNotEqual(changed, original)
        path.write_text(changed)
        receipt = json.loads((self.root / RECEIPT).read_text())
        entry = next(item for item in receipt['files'] if item['destination'] == path.relative_to(self.root).as_posix())
        entry['destination_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.root / RECEIPT).write_text(json.dumps(receipt))
        self.upstream_check('verbatim destination differs')

    def test_removed_research_reference_receipt_rejected(self):
        path = self.root / RECEIPT
        receipt = json.loads(path.read_text())
        receipt['files'] = [entry for entry in receipt['files']
                            if entry['destination'] != 'plugin/skills/why/references/investigator-prompt.md']
        path.write_text(json.dumps(receipt))
        self.package_check()
        self.upstream_check('coverage missing')


if __name__ == '__main__':
    unittest.main()
