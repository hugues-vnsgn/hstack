"""Verification-rule gates through the bound installed adapter and real Git snapshots."""
import json
import subprocess
import unittest

from test_host_adapters import InstalledFixture

PLAN = '''# Program
## Search (PR1)
**Verify, unit.** Required.
- [ ] Run search tests.
**Verify, live.** Required.
- [ ] Lane 1. Relaunch. Save `relaunch.png`. Pass when filters persist.
- [ ] Lane 2. Type a search. Save `search.png`. Pass when matching rows appear.
**Verify, perf.** Required.
- [ ] Rule. Latency below 100 ms.
**Review gate.** Operator reviews.
## Other (PR2)
Unrelated work.
'''


class VerificationContract(InstalledFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.base = self.commit(PLAN)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.consumer), *args], text=True).strip()

    def commit(self, plan):
        (self.consumer / 'plan.md').write_text(plan)
        self.git('add', 'plan.md')
        self.git('commit', '-qm', 'Plan snapshot', '--allow-empty')
        return self.git('rev-parse', 'HEAD')

    def compare(self, head, *extra):
        return self.bound('plan-compare', '--repo', self.consumer, '--plan', 'plan.md',
                          '--section', 'Search (PR1)', '--base-sha', self.base,
                          '--head-sha', head, *extra)

    def test_relaunch_rule_change_holds_with_exact_snapshots_and_diff(self):
        head = self.commit(PLAN.replace('filters persist', 'filters reset to defaults'))
        result = self.compare(head)
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['gate'], 'hold')
        self.assertEqual((report['base_sha'], report['head_sha']), (self.base, head))
        self.assertIn('-Lane 1. Relaunch.', report['diff'])
        self.assertIn('filters reset to defaults', report['diff'])
        self.assertTrue(report['verification_required'])

    def test_scenario_removal_and_perf_changes_hold(self):
        for changed in [PLAN.replace('Type a search', 'Use a filter shortcut'),
                        PLAN.replace('- [ ] Lane 2. Type a search. Save `search.png`. Pass when matching rows appear.\n', ''),
                        PLAN.replace('100 ms', '1000 ms')]:
            with self.subTest(plan=changed):
                result = self.compare(self.commit(changed))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(json.loads(result.stdout)['gate'], 'hold')

    def test_checkboxes_and_dedicated_evidence_links_do_not_change_rules(self):
        before = PLAN.replace('**Verify, perf.**', 'Evidence. [Run](https://example.invalid/old)\n**Verify, perf.**')
        self.base = self.commit(before)
        head = self.commit(before.replace('[ ]', '[x]').replace('/old)', '/new)'))
        result = self.compare(head)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['gate'], 'unchanged')

    def approve(self, report):
        ruling = self.area / 'operator-ruling.json'
        ruling.write_text(json.dumps({'comparison_sha256': report['comparison_sha256'],
                                     'decision': 'approved', 'reference': 'operator chat ruling 37'}))
        return ruling

    def test_exact_operator_ruling_allows_gate_but_still_requires_verification(self):
        head = self.commit(PLAN.replace('100 ms', '120 ms'))
        pending = json.loads(self.compare(head).stdout)
        ruling = self.approve(pending)
        result = self.compare(head, '--ruling', ruling)
        self.assertEqual(result.returncode, 0, result.stderr)
        approved = json.loads(result.stdout)
        self.assertEqual(approved['gate'], 'approved')
        self.assertTrue(approved['verification_required'])
        self.assertEqual(approved['ruling']['reference'], 'operator chat ruling 37')
        changed = self.commit(PLAN.replace('100 ms', '150 ms'))
        self.assertEqual(self.compare(changed, '--ruling', ruling).returncode, 2)

    def test_missing_baseline_requires_approved_starting_contract(self):
        self.base = self.commit('# Program\nNo PR section yet.\n')
        head = self.commit(PLAN)
        result = self.compare(head)
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertIsNone(report['before'])
        result = self.compare(head, '--ruling', self.approve(report))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['gate'], 'approved')

    def test_unchanged_rules_ignore_other_sections_and_working_tree(self):
        head = self.commit(PLAN.replace('Unrelated work.', 'New unrelated work.'))
        (self.consumer / 'plan.md').write_text('Uncommitted misleading content')
        result = self.compare(head)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['gate'], 'unchanged')

    def test_untrusted_or_invalid_inputs_hold(self):
        head = self.commit(PLAN.replace('100 ms', '120 ms'))
        report = json.loads(self.compare(head).stdout)
        ruling = self.approve(report)
        local = self.consumer / 'ruling.json'
        local.write_text(ruling.read_text())
        cases = [('--ruling', str(local)), ('--head-sha', 'HEAD'),
                 ('--plan', '../plan.md'), ('--head-sha', '0' * 40)]
        for args in cases:
            with self.subTest(args=args):
                self.assertEqual(self.compare(head, *args).returncode, 2)
        for content in ['{}', '{"decision":"approved","decision":"rejected"}',
                        ruling.read_text().replace('approved', 'rejected')]:
            ruling.write_text(content)
            self.assertEqual(self.compare(head, '--ruling', ruling).returncode, 2)

    def test_bound_checker_drift_is_rejected(self):
        checker = self.plugin / 'skills/hugues-mode/scripts/compare-plan.py'
        checker.write_text('print("approved")\n')
        result = self.compare(self.base)
        self.assertEqual(result.returncode, 2)
        self.assertIn('drift', result.stderr)

    def test_missing_or_ambiguous_head_contract_holds(self):
        for plan in ['# Gone\n', PLAN + PLAN, PLAN.replace('**Verify, live.**', '**Other.**')]:
            with self.subTest(plan=plan):
                self.assertEqual(self.compare(self.commit(plan)).returncode, 2)

    def test_unsupported_markdown_cannot_hide_the_contract(self):
        for changed in [PLAN.replace('**Verify, unit.**', '<!--\n**Verify, unit.**'),
                        PLAN.replace('**Verify, unit.**', '```markdown\n**Verify, unit.**')]:
            with self.subTest(plan=changed):
                self.assertEqual(self.compare(self.commit(changed)).returncode, 2)

    def test_git_replacement_cannot_rewrite_recorded_baseline(self):
        head = self.commit(PLAN.replace('filters persist', 'filters reset to defaults'))
        self.git('replace', self.base, head)
        result = self.compare(head)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('filters persist', json.loads(result.stdout)['before'])
