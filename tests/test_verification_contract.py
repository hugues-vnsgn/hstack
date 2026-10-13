"""Verification-rule gates through the bound installed adapter and real Git snapshots."""
import json
import re
import shutil
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
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
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
        self.assertIn('-- [ ] Lane 1. Relaunch.', report['diff'])
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
        self.assertTrue(report['missing_baseline'])
        result = self.compare(head, '--ruling', self.approve(report))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['gate'], 'approved')

    def test_unchanged_plan_ignores_working_tree(self):
        head = self.commit(PLAN)
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

    def test_plan_rules_outside_live_blocks_cannot_be_weakened(self):
        before = PLAN.replace('## Search (PR1)', '## Program checklist\n- [ ] Hold unresolved changes.\n## Search (PR1)').replace('## Other (PR2)', '**Merge.**\n- [ ] Root clean verdict required.\n## Other (PR2)')
        self.base = self.commit(before)
        changes = {
            'review gate': before.replace('**Review gate.** Operator reviews.', '**Review gate.** None.'),
            'merge gate': before.replace('Root clean verdict required.', 'Owner may merge directly.'),
            'other PR': before.replace('Unrelated work.', 'Pass with no verification.'),
            'program gate': before.replace('- [ ] Hold unresolved changes.\n', ''),
            'checkbox removal': before.replace('- [ ] Lane 2.', 'Lane 2.'),
        }
        for name, plan in changes.items():
            with self.subTest(change=name):
                result = self.compare(self.commit(plan))
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_evidence_urls_ignore_layout_but_labels_stay_reviewable(self):
        for receipt in ['Evidence. [Run](https://example.invalid/old)',
                        '  Evidence. [Run](https://example.invalid/old)',
                        '- [ ] Keep filters. Evidence. [Run](https://example.invalid/old)']:
            with self.subTest(receipt=receipt):
                before = PLAN.replace('**Verify, perf.**', receipt + '\n**Verify, perf.**')
                self.base = self.commit(before)
                result = self.compare(self.commit(before.replace('/old)', '/new)')))
                self.assertEqual(result.returncode, 0, result.stdout)
                changed = before.replace('[Run]', '[Lane 2 waived: pass when any rows appear]')
                self.assertEqual(self.compare(self.commit(changed)).returncode, 2)

    def test_rejected_ruling_keeps_json_comparison_and_disposition(self):
        head = self.commit(PLAN.replace('100 ms', '120 ms'))
        report = json.loads(self.compare(head).stdout)
        ruling = self.approve(report)
        ruling.write_text(ruling.read_text().replace('approved', 'rejected'))
        result = self.compare(head, '--ruling', ruling)
        self.assertEqual(result.returncode, 2)
        rejected = json.loads(result.stdout)
        self.assertEqual(rejected['gate'], 'hold')
        self.assertEqual(rejected['ruling']['decision'], 'rejected')
        self.assertEqual(rejected['diff'], report['diff'])

    def test_ruling_in_another_consumer_worktree_holds(self):
        head = self.commit(PLAN.replace('100 ms', '120 ms'))
        report = json.loads(self.compare(head).stdout)
        sibling = self.area / 'consumer sibling'
        self.git('worktree', 'add', '--detach', str(sibling), head)
        ruling = sibling / 'ruling.json'
        ruling.write_text(self.approve(report).read_text())
        result = self.compare(head, '--ruling', ruling)
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_baseline_must_match_fetched_main_not_owner_selected_head(self):
        head = self.commit(PLAN.replace('100 ms', '120 ms'))
        result = self.compare(head, '--base-sha', head)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('origin/main', result.stderr)

    def test_main_may_advance_without_being_an_ancestor_of_pr_head(self):
        head = self.commit(PLAN)
        self.git('checkout', '--detach', self.base)
        self.base = self.commit(PLAN.replace('Unrelated work.', 'New main rule.'))
        result = self.compare(head)
        self.assertEqual(result.returncode, 2)
        self.assertIn('New main rule.', json.loads(result.stdout)['before'])

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_real_plan_template_requires_rule_gate_and_compares_review_changes(self):
        source = (self.plugin / 'skills/hugues-mode/playbooks/multi-phase-plan.md').read_text()
        plan = source.split('````markdown\n', 1)[1].split('````', 1)[0]
        plan = plan.replace('<execution playbook>', 'autopilot-full')
        plan = re.sub(r'<[^>\n]+>', 'example', plan)
        path = self.consumer / 'plan.md'
        path.write_text(plan)
        checked = self.bound('plan-check', path)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.base = self.commit(plan)
        head = self.commit(plan.replace('**Review gate.** The operator reviews before merge.',
                                        '**Review gate.** None.'))
        result = self.compare(head, '--section', 'example (example)')
        self.assertEqual(result.returncode, 2, result.stdout)
        without_gate = '\n'.join(line for line in plan.splitlines()
                                 if 'verification-contract.md' not in line and
                                 'verification-contract gate' not in line)
        path.write_text(without_gate)
        checked = self.bound('plan-check', path)
        self.assertEqual(checked.returncode, 1, checked.stdout)
        self.assertIn('verification-contract', checked.stderr)

    def test_attaching_or_removing_receipts_does_not_change_pass_rules(self):
        for receipt in ['Evidence. [Run](https://example.invalid/1)',
                        '  Evidence. [Screenshot](https://example.invalid/1) [Log](https://example.invalid/2)']:
            with self.subTest(receipt=receipt):
                self.base = self.commit(PLAN)
                head = self.commit(PLAN.replace('**Verify, perf.**', receipt + '\n**Verify, perf.**'))
                result = self.compare(head)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.base = head
                self.assertEqual(self.compare(self.commit(PLAN)).returncode, 0)
