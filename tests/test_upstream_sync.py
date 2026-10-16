import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/upstream-diff.py'
SPEC = importlib.util.spec_from_file_location('upstream', SCRIPT)
u = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(u)


class PinnedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history_before = u.load(ROOT / 'docs/upstream/snapshots/pstack-0.15.5.json')
        cls.before = u.load(ROOT / 'docs/upstream/snapshots/pstack-0.15.9.json')
        cls.after = u.load(ROOT / 'docs/upstream/snapshots/pstack-0.15.25.json')
        cls.ledger = u.load(ROOT / 'docs/upstream/hstack-dispositions.json')
        cls.baseline = u.load(ROOT / 'docs/upstream/baseline-dispositions.json')
        cls.history_ledger = u.load(ROOT / 'docs/upstream/history/pstack-0.15.5-dispositions.json')

    def test_exact_appendix_a_paths_and_counts(self):
        # Appendix A is the historical 0.15.5 to 0.15.9 delta; its snapshots stay retained.
        rows = u.changes(u.validate_snapshot(self.history_before), u.validate_snapshot(self.before))
        expected = {
            'pstack/.cursor-plugin/plugin.json', 'pstack/README.md', 'pstack/agents/poteto-agent.md',
            'pstack/docs/guide/08-principles.md', 'pstack/docs/guide/README.md',
            'pstack/skills/architect/SKILL.md', 'pstack/skills/architect/references/design-red-flags.md',
            'pstack/skills/benchmark-checklist/SKILL.md', 'pstack/skills/correct/SKILL.md',
            'pstack/skills/poteto-mode/SKILL.md', 'pstack/skills/poteto-mode/playbooks/autopilot-full.md',
            'pstack/skills/poteto-mode/playbooks/autopilot-stack.md', 'pstack/skills/poteto-mode/playbooks/hillclimb.md',
            'pstack/skills/poteto-mode/playbooks/multi-phase-plan.md', 'pstack/skills/poteto-mode/playbooks/opening-a-pr.md',
            'pstack/skills/poteto-mode/playbooks/perf-issue.md', 'pstack/skills/poteto-mode/scripts/check-plan.mjs',
            'pstack/skills/principle-explain-the-number/SKILL.md', 'pstack/skills/swarm/SKILL.md',
            'pstack/skills/technical-writing/SKILL.md', 'pstack/skills/typescript-best-practices/references/patterns.md'}
        self.assertEqual({r['path'] for r in rows}, expected)
        self.assertEqual([sum(r['change'] == k for r in rows) for k in ('added', 'changed', 'removed')], [3, 18, 0])
        # The maintained delta is 0.15.9 to 0.15.25.
        rows = u.changes(u.validate_snapshot(self.before), u.validate_snapshot(self.after))
        self.assertEqual([sum(r['change'] == k for r in rows) for k in ('added', 'changed', 'removed')], [8, 94, 0])
        self.assertEqual({r['path'] for r in rows if r['change'] == 'added'}, {
            'pstack/plugin.json', 'pstack/skills/in-your-own-words/SKILL.md', 'pstack/skills/ketchup/SKILL.md',
            'pstack/skills/poteto-help/SKILL.md', 'pstack/skills/poteto-help/references/prompting.md',
            'pstack/skills/poteto-help/references/recipes.md',
            'pstack/skills/poteto-mode/scripts/check-plan.test.ts', 'pstack/skills/sharpen/SKILL.md'})

    def test_checked_in_artifacts_and_licenses(self):
        self.assertEqual(u.main(['check']), 0)
        self.assertEqual(len(self.baseline['items']), 161)
        self.assertEqual(len(self.ledger['items']), 169)
        # The retired baselines stay reproducible: the 0.15.5 ledger validates against its snapshot and
        # the 0.15.5 to 0.15.9 delta regenerates byte for byte from the 0.15.9 ledger.
        self.assertEqual(len(self.history_ledger['items']), 158)
        u.validate_ledger(self.history_ledger, u.validate_snapshot(self.history_before))
        u.validate_ledger(self.baseline, u.validate_snapshot(self.before))
        self.assertEqual(u.render_delta(self.history_before, self.before, self.baseline),
                         (ROOT / 'docs/upstream/delta-2eb7ed46-e43c7ee2.md').read_bytes())
        self.assertEqual(sum(r['path'].startswith('pstack/skills/principle-') for r in self.ledger['items']), 24)

    def test_proposal_preserves_unchanged_decisions_and_requires_changed_triage(self):
        saved = copy.deepcopy(self.baseline)
        proposal = u.reconcile(self.baseline, self.before, self.after)
        changed = {r['path'] for r in u.changes(self.before, self.after)}
        self.assertEqual(self.baseline, saved)
        self.assertEqual({r['path'] for r in proposal['items'] if r['disposition'] == 'pending'}, changed)
        self.assertEqual(sum('earlier_proposal' in r for r in proposal['items']), 158)
        # Every changed row that already had a decision keeps it as previous_decision, and rows that
        # already carried a previous decision from an earlier sync keep that too.
        baseline_paths = {r['path'] for r in self.baseline['items']}
        carried = {r['path'] for r in self.baseline['items'] if 'previous_decision' in r}
        self.assertEqual({r['path'] for r in proposal['items'] if 'previous_decision' in r},
                         (changed & baseline_paths) | carried)
        self.assertEqual(sum('previous_decision' in r for r in proposal['items']), 96)
        with self.assertRaisesRegex(ValueError, 'untriaged'):
            u.validate_ledger(proposal, self.after)
        self.assertEqual(u.encode(proposal), u.encode(u.reconcile(saved, self.before, self.after)))

    def test_missing_file_rejected_even_with_adjusted_count(self):
        data = copy.deepcopy(self.after)
        data['files'].pop()
        data['file_count'] -= 1
        with self.assertRaisesRegex(ValueError, 'tree'):
            u.validate_snapshot(data)

    def test_duplicate_path_rejected(self):
        data = copy.deepcopy(self.after)
        data['files'].append(data['files'][-1])
        data['file_count'] += 1
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            u.validate_snapshot(data)

    def test_corrupt_commit_and_tree_rejected(self):
        for key in ('commit_object', 'root_tree_object', 'manifest_object'):
            with self.subTest(key=key):
                data = copy.deepcopy(self.after)
                data[key] = base64.b64encode(base64.b64decode(data[key]) + b'corrupt').decode()
                with self.assertRaises(ValueError):
                    u.validate_snapshot(data)

    def test_wrong_source_version_revision_date_and_count_rejected(self):
        for key, value in [('repository', 'https://example.org/repo'), ('version', '0.15.10'),
                           ('revision', '0' * 40), ('committed_at_utc', '2000-01-01T00:00:00Z'),
                           ('file_count', 160), ('pstack_tree_sha', '1' * 40)]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.after)
                data[key] = value
                with self.assertRaises(ValueError):
                    u.validate_snapshot(data)

    def test_unchanged_blob_cannot_have_conflicting_byte_fingerprints(self):
        for key, value in [('size', 123), ('sha256', '0' * 64)]:
            with self.subTest(key=key):
                after = copy.deepcopy(self.after)
                next(r for r in after['files'] if r['path'] == 'pstack/.gitignore')[key] = value
                with self.assertRaisesRegex(ValueError, 'inconsistent byte'):
                    u.changes(self.before, after)

    def test_unsafe_paths_modes_and_unsorted_inventory_rejected(self):
        for path in ('pstack/../escape', 'pstack//double', 'pstack/pipe|name', 'elsewhere/file', 'pstack/back\\slash'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                u.safe_path(path)
        data = copy.deepcopy(self.after)
        data['files'][0]['mode'] = '120000'
        with self.assertRaisesRegex(ValueError, 'mode'):
            u.validate_snapshot(data)
        data = copy.deepcopy(self.after)
        data['files'].reverse()
        with self.assertRaisesRegex(ValueError, 'sorted'):
            u.validate_snapshot(data)

    def test_stale_incomplete_duplicate_and_untriaged_ledgers_rejected(self):
        for kind in ('fingerprint', 'missing', 'duplicate', 'pending', 'reason', 'principle'):
            with self.subTest(kind=kind):
                ledger = copy.deepcopy(self.ledger)
                if kind == 'fingerprint':
                    ledger['items'][0]['sha256'] = '0' * 64
                elif kind == 'missing':
                    ledger['items'].pop()
                elif kind == 'duplicate':
                    ledger['items'].append(ledger['items'][-1])
                elif kind == 'pending':
                    ledger['items'][0]['disposition'] = 'pending'
                elif kind == 'reason':
                    ledger['items'][0]['reason'] = ''
                else:
                    next(r for r in ledger['items'] if '/principle-' in r['path'])['disposition'] = 'port with adaptation'
                with self.assertRaises(ValueError):
                    u.validate_ledger(ledger, self.after)

    def test_destination_safety(self):
        for path in ('/tmp/file', '../private', 'plugin/../private', 'plugin\\file'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                u.destination_path(path)

    def test_partial_triage_cannot_validate_for_repin(self):
        for key in ('implementation_state', 'release_target'):
            with self.subTest(key=key):
                ledger = copy.deepcopy(self.ledger)
                ledger['items'][0][key] = 'pending'
                with self.assertRaisesRegex(ValueError, 'incomplete triage'):
                    u.validate_ledger(ledger, self.after)
                u.validate_ledger(ledger, self.after, allow_pending=True)

    def test_present_verbatim_mutation_and_receipt_disposition_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            row = next(r for r in self.ledger['items'] if r['path'] == 'pstack/LICENSE')
            destination = root / row['destinations'][0]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'verbatim'):
                u.check_destinations({'items': [row]}, self.after, root)
        ledger = copy.deepcopy(self.ledger)
        row = next(r for r in ledger['items'] if r['path'] == 'pstack/skills/poteto-mode/SKILL.md')
        row['disposition'] = 'ignore with reason'
        with self.assertRaisesRegex(ValueError, 'receipt'):
            u.check_destinations(ledger, self.after, ROOT)

    def test_unknown_receipt_disposition_rejected(self):
        row = next(r for r in self.ledger['items'] if r['path'] == 'pstack/skills/poteto-mode/SKILL.md')
        receipts = u.load(ROOT / 'docs/upstream/wp2-provenance.json')
        receipt = next(r for r in receipts['files'] if r['source'] == row['path'])
        for disposition in ('adpated', 'Verbatim', 'unverified'):
            with self.subTest(disposition=disposition), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                destination = root / row['destinations'][0]
                destination.parent.mkdir(parents=True)
                destination.write_bytes(b'User adaptation.')
                path = root / 'docs/upstream/wp2-provenance.json'
                path.parent.mkdir(parents=True)
                path.write_bytes(u.encode(dict(receipts, files=[dict(receipt, disposition=disposition)])))
                with self.assertRaises(KeyError):
                    u.check_destinations({'items': [row]}, self.after, root)

    def check_wp3_mutation(self, mutate_receipts=None, mutate_ledger=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'package'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
            receipt_path = root / 'docs/wp3-source-receipts.json'
            receipts = u.load(receipt_path)
            ledger = copy.deepcopy(self.ledger)
            if mutate_receipts:
                mutate_receipts(receipts)
                receipt_path.write_bytes(u.encode(receipts))
            if mutate_ledger:
                mutate_ledger(ledger)
            with self.assertRaisesRegex(ValueError, 'WP3 receipt'):
                u.check_destinations(ledger, self.after, root)

    def test_wp3_generator_receipt_fingerprint_mismatch_rejected(self):
        for key, value in (('blob_sha', '0' * 40), ('sha256', '0' * 64)):
            with self.subTest(key=key):
                self.check_wp3_mutation(lambda receipts: receipts['inputs'][0].update({key: value}))

    def test_wp3_generator_receipt_missing_or_duplicate_rejected(self):
        self.check_wp3_mutation(lambda receipts: receipts['inputs'].pop(0))
        self.check_wp3_mutation(lambda receipts: receipts['inputs'].append(copy.deepcopy(receipts['inputs'][0])))

    def test_wp3_generator_receipt_disposition_and_destination_rejected(self):
        self.check_wp3_mutation(lambda receipts: receipts['inputs'][0].update(disposition='integration reference only'))
        self.check_wp3_mutation(lambda receipts: receipts['inputs'][0].update(destinations=[]))

    def test_changed_present_generator_requires_receipt_update(self):
        def change_generator(ledger):
            row = next(r for r in ledger['items'] if r['path'] == 'pstack/skills/create-verification-skill/SKILL.md')
            row.update(blob_sha='1' * 40, sha256='1' * 64)
        self.check_wp3_mutation(mutate_ledger=change_generator)

    def test_shipping_generator_cannot_downgrade_ledger_state(self):
        for state in ('planned', 'deferred'):
            for stale_blob in (False, True):
                with self.subTest(state=state, stale_blob=stale_blob):
                    def downgrade_generator(ledger):
                        row = next(r for r in ledger['items']
                                   if r['path'] == 'pstack/skills/create-verification-skill/SKILL.md')
                        row.update(implementation_state=state, destinations=[])
                        if stale_blob:
                            row.update(blob_sha='1' * 40, sha256='1' * 64)
                    self.check_wp3_mutation(mutate_ledger=downgrade_generator)

    def test_pin_digest_anchors_snapshot_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            pin = u.load(ROOT / 'docs/upstream/pin.json')
            pin['snapshot'] = 'source.json'
            data = u.encode(self.after)
            pin['snapshot_sha256'] = hashlib.sha256(data).hexdigest()
            (directory / 'pin.json').write_bytes(u.encode(pin))
            (directory / 'source.json').write_bytes(data)
            self.assertEqual(u.read_pin(directory / 'pin.json'), self.after)
            (directory / 'source.json').write_bytes(data + b' ')
            with self.assertRaisesRegex(ValueError, 'bytes'):
                u.read_pin(directory / 'pin.json')
            pin['snapshot'] = '../source.json'
            (directory / 'pin.json').write_bytes(u.encode(pin))
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                u.read_pin(directory / 'pin.json')

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            json.loads('{"revision":1,"revision":2}', object_pairs_hook=u.unique)

    def test_reports_escape_markdown_and_html(self):
        ledger = copy.deepcopy(self.ledger)
        ledger['items'][0]['reason'] = '<script>|hello\nnext'
        rendered = u.render_delta(self.before, self.after, ledger).decode()
        self.assertIn('&lt;script>\u0026#124;hello next', rendered)
        self.assertNotIn('<script>', rendered)

    def test_output_is_idempotent_and_never_overwrites_adaptations(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'adapted.md'
            u.write_output(path, b'adapted')
            u.write_output(path, b'adapted')
            u.write_output(path, b'adapted', check=True)
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                u.write_output(path, b'upstream')
            with self.assertRaisesRegex(ValueError, 'differs'):
                u.write_output(path, b'upstream', check=True)
            self.assertEqual(path.read_bytes(), b'adapted')
            link = Path(folder) / 'link'
            link.symlink_to(path)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                u.write_output(link, b'adapted')

    def test_offline_cli_delta_and_reconcile_leave_plugin_and_pin_unchanged(self):
        observed = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'plugin').rglob('*') if p.is_file()}
        pin = (ROOT / 'docs/upstream/pin.json').read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'delta.md'
            args = ['diff', '--from-snapshot', str(ROOT / 'docs/upstream/snapshots/pstack-0.15.9.json'),
                    '--to-snapshot', str(ROOT / 'docs/upstream/snapshots/pstack-0.15.25.json'),
                    '--ledger', str(ROOT / 'docs/upstream/hstack-dispositions.json'), '--output', str(target)]
            subprocess.run([sys.executable, str(SCRIPT), *args], check=True, capture_output=True)
            self.assertEqual(target.read_bytes(), (ROOT / 'docs/upstream/delta-e43c7ee2-6ce45c59.md').read_bytes())
            subprocess.run([sys.executable, str(SCRIPT), *args, '--check'], check=True, capture_output=True)
            proposal = Path(folder) / 'proposal.json'
            subprocess.run([sys.executable, str(SCRIPT), 'reconcile', '--from-snapshot',
                            str(ROOT / 'docs/upstream/snapshots/pstack-0.15.9.json'), '--to-snapshot',
                            str(ROOT / 'docs/upstream/snapshots/pstack-0.15.25.json'), '--ledger',
                            str(ROOT / 'docs/upstream/baseline-dispositions.json'), '--output', str(proposal)],
                           check=True, capture_output=True)
            self.assertEqual(u.load(proposal), u.reconcile(self.baseline, self.before, self.after))
            target.write_bytes(b'user adaptation')
            rejected = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(target.read_bytes(), b'user adaptation')
        self.assertEqual((ROOT / 'docs/upstream/pin.json').read_bytes(), pin)
        self.assertEqual(observed, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in observed})

    def test_csv_cli_validates_source_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'ledger.csv'
            args = [sys.executable, str(SCRIPT), 'csv', '--ledger', str(ROOT / 'docs/upstream/hstack-dispositions.json'),
                    '--snapshot', str(ROOT / 'docs/upstream/snapshots/pstack-0.15.25.json'), '--output', str(output)]
            subprocess.run(args, check=True, capture_output=True)
            self.assertEqual(output.read_bytes(), (ROOT / 'docs/upstream/hstack-dispositions.csv').read_bytes())
            subprocess.run(args + ['--check'], check=True, capture_output=True)
            output.write_bytes(b'curated export')
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), b'curated export')
            bad = Path(folder) / 'bad.csv'
            args[args.index('--output') + 1] = str(bad)
            args[args.index('--snapshot') + 1] = str(ROOT / 'docs/upstream/snapshots/pstack-0.15.9.json')
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertFalse(bad.exists())


class LocalGitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        u.git(self.repo, 'init', '--quiet')
        u.git(self.repo, 'config', 'user.name', 'Fixture')
        u.git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        self.put('pstack/.cursor-plugin/plugin.json', b'{"version":"1.0.0"}')
        self.put('pstack/a.txt', b'a')
        self.put('pstack/nested/z.txt', b'z')
        self.put('unrelated.txt', b'not included')
        self.commit()
        self.before = u.snapshot(self.repo, 'HEAD')

    def put(self, path, data):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def commit(self):
        u.git(self.repo, 'add', '.')
        u.git(self.repo, 'commit', '--quiet', '-m', 'fixture')

    def test_captured_objects_complete_and_deterministic(self):
        self.assertEqual(len(self.before['files']), 3)
        self.assertEqual(u.encode(self.before), u.encode(u.snapshot(self.repo, 'HEAD')))

    def test_content_add_delete_and_mode_delta(self):
        self.put('pstack/a.txt', b'changed')
        (self.repo / 'pstack/nested/z.txt').unlink()
        self.put('pstack/new.txt', b'new')
        self.commit()
        after = u.snapshot(self.repo, 'HEAD')
        self.assertEqual({r['path']: r['change'] for r in u.changes(self.before, after)},
                         {'pstack/a.txt': 'changed', 'pstack/nested/z.txt': 'removed', 'pstack/new.txt': 'added'})
        u.git(self.repo, 'update-index', '--chmod=+x', 'pstack/a.txt')
        u.git(self.repo, 'commit', '--quiet', '-m', 'mode')
        rows = u.changes(after, u.snapshot(self.repo, 'HEAD'))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['before']['blob_sha'], rows[0]['after']['blob_sha'])
        self.assertEqual(rows[0]['change'], 'changed')

    def test_deleted_and_revived_responsibilities_preserve_history(self):
        ledger = {'schema_version': 1, 'repository': u.REPOSITORY, 'revision': self.before['revision'],
                  'items': [dict(r, disposition='ignore with reason', release_target='0.2',
                                 implementation_state='deferred', destinations=[], reason='Fixture scope.')
                            for r in self.before['files']], 'retired_items': []}
        (self.repo / 'pstack/a.txt').unlink()
        self.commit()
        after = u.snapshot(self.repo, 'HEAD')
        proposal = u.reconcile(ledger, self.before, after)
        self.assertEqual(len(proposal['retired_items']), 1)
        self.assertEqual(proposal['retired_items'][0]['removed_at_revision'], after['revision'])
        self.put('pstack/a.txt', b'a')
        self.commit()
        revived = u.reconcile(proposal, after, u.snapshot(self.repo, 'HEAD'))
        self.assertEqual(revived['retired_items'], [])
        row = next(r for r in revived['items'] if r['path'] == 'pstack/a.txt')
        self.assertEqual(row['disposition'], 'pending')
        self.assertEqual(row['previous_decision']['reason'], 'Fixture scope.')

    def test_symlink_git_entry_rejected(self):
        (self.repo / 'pstack/link').symlink_to('a.txt')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            u.snapshot(self.repo, 'HEAD')

    def test_missing_git_blob_rejected(self):
        blob = next(r['blob_sha'] for r in self.before['files'] if r['path'] == 'pstack/a.txt')
        (self.repo / '.git/objects' / blob[:2] / blob[2:]).unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            u.snapshot(self.repo, 'HEAD')

    def test_replace_objects_cannot_change_pinned_evidence(self):
        old = self.before['revision']
        self.put('pstack/a.txt', b'replaced')
        self.commit()
        new = u.git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        u.git(self.repo, 'replace', old, new)
        self.assertEqual(u.snapshot(self.repo, old), self.before)

    def test_snapshot_cli(self):
        output = self.repo / 'snapshot.json'
        result = subprocess.run([sys.executable, str(SCRIPT), 'snapshot', '--repo', str(self.repo),
                                 '--revision', self.before['revision'], '--output', str(output)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(u.load(output), self.before)

    def test_signature_display_config_cannot_change_capture_date(self):
        commit = base64.b64decode(self.before['commit_object'])
        header, message = commit.split(b'\n\n', 1)
        signed = header + b'\ngpgsig -----BEGIN PGP SIGNATURE-----\n fixture\n -----END PGP SIGNATURE-----\n\n' + message
        result = subprocess.run(['git', '-C', str(self.repo), 'hash-object', '-t', 'commit', '-w', '--stdin'],
                                input=signed, capture_output=True, check=True)
        revision = result.stdout.decode().strip()
        u.git(self.repo, 'update-ref', 'HEAD', revision)
        u.git(self.repo, 'config', 'log.showSignature', 'true')
        captured = u.snapshot(self.repo, revision)
        self.assertEqual(captured['committed_at_utc'], self.before['committed_at_utc'])
        self.assertEqual(captured['revision'], revision)


class RetiredPredecessorTests(unittest.TestCase):
    """hstack-alpha (the retired predecessor, GitHub osxsystem/hstack) was deleted on
    2026-10-16. Every file this repository cites from it stays verifiable from the repository."""

    @classmethod
    def setUpClass(cls):
        cls.receipts = u.load(ROOT / 'docs/wp3-source-receipts.json')
        cls.predecessor = cls.receipts['retired_predecessor']
        cls.retained = ROOT / cls.predecessor['retained_at']

    def sha256(self, relative):
        return hashlib.sha256((self.retained / relative).read_bytes()).hexdigest()

    def test_receipt_note_names_the_deletion_and_the_retained_bytes(self):
        self.assertEqual(self.predecessor['repository'], 'https://github.com/osxsystem/hstack')
        self.assertEqual(self.predecessor['revision'], '99cc6129aea3f702ee6cd3b448e4f67700b4353c')
        self.assertEqual(self.predecessor['retained_at'], 'provenance/upstream/hstack-alpha-99cc612/')
        self.assertIn('deleted on 2026-10-16', self.predecessor['note'])
        self.assertIn('hstack-alpha (retired predecessor)', self.predecessor['note'])

    def test_every_cited_predecessor_input_has_a_retained_copy_with_the_receipted_hash(self):
        rows = [row for row in self.receipts['inputs'] if row['repository'] == self.predecessor['repository']]
        self.assertEqual(len(rows), 4)
        for row in rows:
            # The original repository and revision fields stay on each input.
            self.assertEqual(row['revision'], self.predecessor['revision'])
            self.assertEqual(self.sha256(row['source']), row['sha256'], row['source'])

    def test_every_source_line_citation_has_a_retained_copy(self):
        hashes = {row['source']: row['sha256'] for row in self.receipts['inputs']
                  if row['repository'] == self.predecessor['repository']}
        hashes.update(self.predecessor['cited_without_input_row'])
        cited = set()
        for path in sorted((ROOT / 'plugin/skills/hugues-mode').rglob('*.md')):
            for line in path.read_text().splitlines():
                if not (line.startswith('source:') and 'osxsystem/hstack' in line):
                    continue
                self.assertIn(self.predecessor['revision'], line, path.name)
                self.assertIn('hstack-alpha (retired predecessor', line, path.name)
                after = line.split('`' + self.predecessor['revision'] + '`', 1)[1]
                for span in re.findall(r'`([^`]+)`', after):
                    cited.update(item.strip() for item in span.split(',') if item.strip().endswith('.md'))
        self.assertEqual(cited, {
            'packs/mobile/skills/mobile-proof/SKILL.md', 'packs/mobile/references/evidence.md',
            'packs/mobile/references/platforms.md', 'skills/core/hstack/playbooks/build-doctor.md',
            'packs/mobile/references/kmp-compose-pilot.md'})
        for source in sorted(cited):
            self.assertEqual(self.sha256(source), hashes[source], source)

    def test_retained_link_targets_match_their_recorded_hashes(self):
        targets = self.predecessor['retained_link_targets']
        self.assertEqual(len(targets), 13)
        for source, expected in targets.items():
            self.assertEqual(self.sha256(source), expected, source)


if __name__ == '__main__':
    unittest.main()
