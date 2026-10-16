"""Exercise retained-source acceptance through the real upstream checker CLI."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('retained_upstream', ROOT / 'scripts/upstream-diff.py')
u = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(u)


class RetainedProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
        self.directory = self.root / 'docs/upstream'
        self.ledger = u.load(self.directory / 'huguesStack-dispositions.json')
        self.source = u.read_pin(self.directory / 'pin.json')
        # Keep this fixture independent of which retained packages are integrated.
        # Replace retained leaves only inside the temporary copied checkout.
        for receipt in self.directory.glob('retained-*-provenance.json'):
            receipt.unlink()
        for family in u.RETAINED_SKILLS:
            directory = self.root / 'plugin/skills' / family
            if directory.exists():
                shutil.rmtree(directory)
        for row in self.ledger['items']:
            parts = Path(row['path']).parts
            if len(parts) >= 4 and parts[1] == 'skills' and parts[2] in u.RETAINED_SKILLS:
                row['implementation_state'] = 'planned'
        self.receipt_path = self.directory / 'retained-fixture-provenance.json'
        self.receipt = dict(repository=self.source['repository'], revision=self.source['revision'],
                            upstream_version=self.source['version'], package='fixture', files=[])
        # These tiny adaptations exist only in temporary fixtures. The fingerprints
        # still refer to the real pinned how source, not a synthetic snapshot.
        for source in ('pstack/skills/how/SKILL.md', 'pstack/skills/how/references/explorer-prompt.md'):
            row = next(row for row in self.ledger['items'] if row['path'] == source)
            destination = 'plugin/' + source[len('pstack/'):]
            row.update(implementation_state='present', disposition='port with adaptation',
                       destinations=[destination])
            target = self.root / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'Synthetic retained how adaptation for checker tests.\n')
            self.receipt['files'].append(dict(source=source, destination=destination, disposition='adapted',
                blob_sha=row['blob_sha'], sha256=row['sha256'], mode=row['mode'],
                destination_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                retained_contracts=['Test-only source explanation contract.'],
                deviations=['Synthetic test fixture; never shipped.']))
        self.save()

    def save(self):
        self.receipt_path.write_bytes(u.encode(self.receipt))
        (self.directory / 'huguesStack-dispositions.json').write_bytes(u.encode(self.ledger))
        (self.directory / 'huguesStack-dispositions.csv').write_bytes(u.render_csv(self.ledger))
        before = u.read_pin(self.directory / 'baseline-pin.json')
        name = f"delta-{before['revision'][:8]}-{self.source['revision'][:8]}.md"
        (self.directory / name).write_bytes(u.render_delta(before, self.source, self.ledger))

    def run_check(self, error=None):
        result = subprocess.run([sys.executable, str(self.root / 'scripts/upstream-diff.py'),
                                 'check', '--root', str(self.root)], capture_output=True, text=True)
        if error is None:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Verified pstack 0.15.25', result.stdout)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(error, result.stderr)

    def test_accepts_complete_receipt_and_rejects_missing_file_receipt(self):
        self.run_check()
        self.receipt['files'].pop()
        self.save()
        self.run_check('coverage missing')

    def test_shipping_files_require_receipt_even_when_ledger_is_downgraded(self):
        self.run_check()
        self.receipt_path.unlink()
        for row in self.ledger['items']:
            if row['path'].startswith('pstack/skills/how/'):
                row.update(implementation_state='planned', destinations=[])
        self.save()
        self.receipt_path.unlink()
        self.run_check('coverage missing')

    def test_duplicate_sources_and_destinations_rejected(self):
        for field in ('source', 'destination'):
            with self.subTest(field=field):
                saved = copy.deepcopy(self.receipt)
                self.receipt['files'][1][field] = self.receipt['files'][0][field]
                self.save()
                self.run_check('duplicate retained')
                self.receipt = saved

    def test_duplicate_receipts_across_packages_rejected(self):
        self.run_check()
        second = dict(self.receipt, package='second')
        (self.directory / 'retained-second-provenance.json').write_bytes(u.encode(second))
        self.run_check('duplicate retained')

    def test_unsafe_source_and_destination_rejected(self):
        for field, value in (('source', 'pstack/../escape'), ('destination', '../escape'),
                             ('destination', '/tmp/escape'), ('destination', 'plugin//double')):
            with self.subTest(field=field, value=value):
                saved = copy.deepcopy(self.receipt)
                self.receipt['files'][0][field] = value
                self.save()
                self.run_check('unsafe')
                self.receipt = saved

    def test_pin_fingerprints_modes_and_destination_digest_rejected(self):
        for key, value in (('repository', 'https://example.invalid/source'), ('revision', '0' * 40),
                           ('upstream_version', '0.15.10'), ('blob_sha', '0' * 40),
                           ('sha256', '0' * 64), ('mode', '100755'), ('destination_sha256', '0' * 64)):
            with self.subTest(key=key):
                saved = copy.deepcopy(self.receipt)
                target = self.receipt if key in self.receipt else self.receipt['files'][0]
                target[key] = value
                self.save()
                error = 'match pin' if key in self.receipt else 'bytes differ' if key == 'destination_sha256' else 'fingerprint/mode'
                self.run_check(error)
                self.receipt = saved

    def test_malformed_receipts_rejected(self):
        self.run_check()
        valid = copy.deepcopy(self.receipt)
        for mutate, error in (
                (lambda r: r.pop('repository'), 'malformed retained receipt header'),
                (lambda r: r.update(package='mismatch'), 'package does not match filename'),
                (lambda r: r.update(files=[]), 'needs files'),
                (lambda r: r['files'][0].pop('mode'), 'malformed retained file receipt'),
                (lambda r: r['files'][0].update(disposition='adpated'), 'invalid retained receipt disposition'),
                (lambda r: r['files'][0].update(retained_contracts=[]), 'contract evidence'),
                (lambda r: r['files'][0].update(deviations='unstructured'), 'malformed retained receipt deviations')):
            with self.subTest(error=error):
                self.receipt = copy.deepcopy(valid)
                mutate(self.receipt)
                self.save()
                self.run_check(error)
        self.receipt_path.write_text('{"package":"fixture","package":"fixture"}')
        self.run_check('duplicate JSON key')

    def test_disposition_state_and_destination_must_agree_with_ledger(self):
        self.run_check()
        row = next(row for row in self.ledger['items'] if row['path'] == self.receipt['files'][0]['source'])
        for updates in (dict(implementation_state='deferred'), dict(destinations=[]),
                        dict(destinations=['plugin/skills/how/elsewhere.md']), dict(disposition='ignore with reason')):
            with self.subTest(updates=updates):
                saved = copy.deepcopy(row)
                row.update(updates)
                self.save()
                # A present row with no/absent destination is rejected by existing
                # ledger/destination guards before reaching retained receipts.
                error = 'needs a destination' if updates == dict(destinations=[]) else 'missing/unsafe' if 'destinations' in updates else 'present ledger'
                self.run_check(error)
                row.clear()
                row.update(saved)

    def test_modified_adapted_bytes_and_unsafe_file_rejected(self):
        self.run_check()
        target = self.root / self.receipt['files'][0]['destination']
        target.write_bytes(b'Modified after the receipt was produced.\n')
        self.run_check('bytes differ')
        target.unlink()
        target.symlink_to(self.root / self.receipt['files'][1]['destination'])
        self.run_check('missing/unsafe present destination')

    def test_verbatim_claim_requires_actual_pinned_git_blob(self):
        self.run_check()
        entry = self.receipt['files'][0]
        entry['disposition'] = 'verbatim'
        row = next(row for row in self.ledger['items'] if row['path'] == entry['source'])
        row['disposition'] = 'port verbatim'
        self.save()
        self.run_check('verbatim destination differs')

    def test_unreceipted_reference_rejected_and_missing_destination_rejected(self):
        self.run_check()
        reference = self.root / 'plugin/skills/how/references/unreceipted.md'
        reference.write_bytes(b'Unreceipted reference.\n')
        self.run_check('coverage missing')
        reference.unlink()
        (self.root / self.receipt['files'][1]['destination']).unlink()
        self.run_check('missing/unsafe present destination')


if __name__ == '__main__':
    unittest.main()
