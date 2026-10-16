"""Exercise real packaging and ledger rejection for the retained verification leaves.

These are static framework proofs, not mobile executions or prompt adherence tests.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from release_snapshot import release_root
ROOT = release_root()
NAMES = ('tdd', 'blast-radius', 'maintain-verification-skill', 'correct')
RECEIPT = Path('docs/upstream/retained-verification-provenance.json')
spec = importlib.util.spec_from_file_location('retained_upstream', ROOT / 'scripts/upstream-diff.py')
UPSTREAM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(UPSTREAM)


class RetainedVerificationAccounting(unittest.TestCase):
    def test_pinned_source_destination_ledger_relations(self):
        source = UPSTREAM.read_pin(ROOT / 'docs/upstream/pin.json')
        ledger = UPSTREAM.validate_ledger(UPSTREAM.load(ROOT / 'docs/upstream/huguesStack-dispositions.json'), source)
        receipts = UPSTREAM.load(ROOT / RECEIPT)
        self.assertEqual((receipts['repository'], receipts['revision'], receipts['upstream_version']),
                         (source['repository'], source['revision'], source['version']))
        self.assertEqual(receipts['package'], 'verification')
        indexed = {row['path']: row for row in ledger['items']}
        destinations = set()
        for item in receipts['files']:
            row = indexed[item['source']]
            self.assertEqual(item['disposition'], 'adapted')
            self.assertEqual(row['disposition'], 'port with adaptation')
            self.assertEqual(row['implementation_state'], 'present')
            self.assertIn(item['destination'], row['destinations'])
            for key in ('blob_sha', 'sha256', 'mode'):
                self.assertEqual(item[key], row[key])
            body = (ROOT / item['destination']).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(), item['destination_sha256'])
            self.assertNotEqual(hashlib.sha256(body).hexdigest(), item['sha256'])
            self.assertTrue(item['retained_contracts'])
            self.assertTrue(item['deviations'])
            destinations.add(item['destination'])
        self.assertEqual(destinations, {f'plugin/skills/{name}/SKILL.md' for name in NAMES})
        self.assertEqual(len(receipts['files']), len(destinations))


class RetainedVerificationPackageMutations(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-retained-verification-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))

    def check(self):
        return subprocess.run(['sh', str(self.repo / 'scripts/check-plugin.sh'), str(self.repo)],
                              cwd=self.temp.name, capture_output=True, text=True)

    def test_registered_leaf_names_and_integrated_links(self):
        manifest = json.loads((self.repo / 'plugin/.claude-plugin/plugin.json').read_text())
        roots = manifest['skills']
        if isinstance(roots, str):
            roots = [roots]
        discovered = {path for relative in roots for path in (self.repo / 'plugin' / relative).rglob('SKILL.md')}
        for name in NAMES:
            self.assertIn(self.repo / f'plugin/skills/{name}/SKILL.md', discovered)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS: manifests,', result.stdout)

    def test_frontmatter_mutation_rejected_with_actionable_file(self):
        for name in NAMES:
            with self.subTest(skill=name):
                path = self.repo / f'plugin/skills/{name}/SKILL.md'
                original = path.read_text()
                path.write_text(original.replace(f'name: {name}', 'name: wrong-registration', 1))
                result = self.check()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f'{name}/SKILL.md: name must match skill folder', result.stderr)
                path.write_text(original)

    def test_required_proof_reference_removal_rejected(self):
        path = self.repo / 'plugin/skills/hugues-mode/references/evidence-guide.md'
        path.unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        for name in NAMES:
            self.assertIn(f'plugin/skills/{name}/SKILL.md:', result.stderr)
        self.assertIn('broken local link', result.stderr)

    def test_arena_dependency_removal_rejected_at_blast_radius(self):
        path = self.repo / 'plugin/skills/arena/SKILL.md'
        if path.exists():
            path.unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('plugin/skills/blast-radius/SKILL.md:', result.stderr)
        self.assertIn('../arena/SKILL.md', result.stderr)

    def test_false_verbatim_tdd_or_correct_claim_rejected(self):
        for name in ('tdd', 'correct'):
            with self.subTest(skill=name):
                ledger = UPSTREAM.load(self.repo / 'docs/upstream/huguesStack-dispositions.json')
                row = next(row for row in ledger['items'] if row['path'] == f'pstack/skills/{name}/SKILL.md')
                row['disposition'] = 'port verbatim'
                with self.assertRaisesRegex(ValueError, f'verbatim destination differs: plugin/skills/{name}/SKILL.md'):
                    UPSTREAM.check_destinations(ledger, UPSTREAM.read_pin(self.repo / 'docs/upstream/pin.json'), self.repo)


if __name__ == '__main__':
    unittest.main()
