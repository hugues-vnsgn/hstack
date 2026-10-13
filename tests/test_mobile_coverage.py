"""Risk coverage through the installed public CLI, outside the plugin checkout."""
from pathlib import Path
import json
import subprocess
import unittest

from test_host_adapters import InstalledFixture, ROOT


def mobile_plan():
    plan = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
    coverage = '''**Coverage.**
- Work type. mobile-behavior.
- Platforms. android, ios.
- Areas. navigation.
- Source. Fixture navigation change and supported-target declarations.
- Target android-debug. Platform android. Identity debug APK on fixture emulator.
- Target ios-debug. Platform ios. Identity debug app on fixture simulator.
- Risk process-death. applicable. Checks 1, 2. Reason saved navigation changes.
- Risk background-reopen. applicable. Checks 1, 2. Reason return path changes.
- Risk restored-navigation. applicable. Checks 1, 2. Reason saved route changes.
- Risk rotation. not-applicable. Checks none. Reason rotation ownership is unchanged. Approval owner fixture ruling.
- Risk navigation-gestures. not-applicable. Checks none. Reason gesture handling is unchanged. Approval owner fixture ruling.
- Live. applicable.
- Performance. applicable.
'''
    plan = '---\nverification_profile: mobile-risk-v1\n---\n' + plan
    plan = plan.replace('**Files.**', coverage + '**Files.**')
    start = plan.index('- [ ] Lane 1.')
    end = plan.index('**Verify, perf.**', start)
    lanes = []
    for n in range(1, 13):
        target = 'android-debug' if n % 2 else 'ios-debug'
        lanes.append(f'- [ ] Lane {n}. Restore route {n}. Risks `process-death, background-reopen, restored-navigation`. '
                     f'Target `{target}`. Reason route {n} has a distinct saved state. '
                     f'Action background, kill and reopen route {n}. Save `lane-{n}.png`. '
                     f'Pass when route {n} and its back navigation restore.')
    return plan[:start].replace('Ten lanes on', 'Risk-based lanes on') + '\n'.join(lanes) + '\n' + plan[end:]


def document_plan(work_type='documentation'):
    plan = mobile_plan()
    start = plan.index('**Coverage.**')
    end = plan.index('**Files.**', start)
    area = 'documentation' if work_type == 'documentation' else 'workflow'
    coverage = f'''**Coverage.**
- Work type. {work_type}.
- Platforms. none.
- Areas. {area}.
- Source. Fixture diff changes {area} only.
- Live. not-applicable. Reason no app behavior changed. Approval owner fixture ruling.
- Performance. not-applicable. Reason no runtime changed. Approval owner fixture ruling.
'''
    plan = plan[:start] + coverage + plan[end:]
    start = plan.index('**Verify, live.**')
    end = plan.index('**Review gate.**', start)
    rule = 'Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.'
    plan = plan[:start] + f'**Verify, live.** {rule} Not applicable.\n**Verify, perf.** {rule} Not applicable.\n' + plan[end:]
    return plan.replace('Regression passes.', 'Run `python3 check-docs.py`.')


def area_plan(area, risks):
    plan = mobile_plan().replace('Areas. navigation.', f'Areas. {area}.')
    start = plan.index('- Risk process-death.')
    end = plan.index('- Live.', start)
    rows = ''.join(f'- Risk {risk}. applicable. Checks 1, 2. Reason {area} changes.\n' for risk in risks)
    plan = plan[:start] + rows + plan[end:]
    return plan.replace('Risks `process-death, background-reopen, restored-navigation`',
                        'Risks `' + ', '.join(risks) + '`')


class MobileCoverage(InstalledFixture, unittest.TestCase):
    def check(self, text):
        path = self.consumer / 'plan.md'
        path.write_text(text)
        return self.bound('plan-check', path)

    def test_twelve_justified_mobile_checks_are_accepted(self):
        result = self.check(mobile_plan())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('verify-live=12', result.stdout)
        self.assertIn('0 problems', result.stdout)

    def test_navigation_plan_cannot_omit_process_death(self):
        plan = mobile_plan().replace('- Risk process-death. applicable. Checks 1, 2. Reason saved navigation changes.\n', '')
        result = self.check(plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('process-death', result.stderr)

    def test_risk_requires_check_on_every_affected_target(self):
        result = self.check(mobile_plan().replace('Risk process-death. applicable. Checks 1, 2.',
                                                 'Risk process-death. applicable. Checks 1.'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('process-death', result.stderr)
        self.assertIn('ios-debug', result.stderr)

    def test_storage_coverage_is_accepted_and_corruption_is_required(self):
        plan = mobile_plan().replace('Areas. navigation.', 'Areas. navigation, persistence.')
        rows = ''.join(f'- Risk {risk}. applicable. Checks 1, 2. Reason storage changes.\n'
                       for risk in ['read-write-failure', 'corruption', 'interrupted-write', 'existing-data'])
        plan = plan.replace('- Live. applicable.', rows + '- Live. applicable.')
        plan = plan.replace('Risks `process-death, background-reopen, restored-navigation`',
                            'Risks `process-death, background-reopen, restored-navigation, read-write-failure, corruption, interrupted-write, existing-data`')
        result = self.check(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.check(plan.replace('- Risk corruption. applicable. Checks 1, 2. Reason storage changes.\n', ''))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing risk corruption', result.stderr)

    def test_documentation_can_justify_zero_device_checks(self):
        result = self.check(document_plan())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('verify-live=0', result.stdout)

    def test_workflow_change_needs_an_executable_check(self):
        plan = document_plan('tooling-workflow').replace('check-docs.py', 'check-workflow.py')
        result = self.check(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.check(plan.replace('Run `python3 check-workflow.py`.', 'Read the instructions.'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('command check', result.stderr)

    def test_unknown_or_duplicate_profile_is_rejected(self):
        legacy = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
        for plan in ['---\nverification_profile: other\n---\n' + legacy,
                     mobile_plan().replace('verification_profile: mobile-risk-v1',
                                           'verification_profile: mobile-risk-v1\nverification_profile: mobile-risk-v1')]:
            with self.subTest(plan=plan[:120]):
                result = self.check(plan)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('verification_profile', result.stderr)

    def test_other_mobile_areas_have_declared_risk_coverage(self):
        for area, risks in [('layout', ['small-layout', 'large-text', 'keyboard-input']),
                            ('native-views', ['memory-retention', 'view-cleanup']),
                            ('launch', ['oldest-os', 'release-build', 'content-readiness']),
                            ('network', ['offline', 'failure-recovery'])]:
            with self.subTest(area=area):
                result = self.check(area_plan(area, risks))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_incomplete_or_conflicting_check_declarations_hold(self):
        plan = mobile_plan()
        changes = [('Reason route 1 has a distinct saved state. ', ''),
                   ('Action background, kill and reopen route 1. ', ''),
                   ('Save `lane-1.png`. ', ''),
                   ('Pass when route 1 and its back navigation restore.', 'Pass when <>.'),
                   ('Target `ios-debug`', 'Target `missing-device`'),
                   ('Platforms. android, ios.', 'Platforms. android.'),
                   ('Risk process-death. applicable. Checks 1, 2.', 'Risk process-death. applicable. Checks 999.'),
                   ('Risk process-death. applicable. Checks 1, 2.', 'Risk process-death. applicable. Checks 1, 1.'),
                   ('Risk background-reopen. applicable.', 'Risk background-reopen. unresolved.'),
                   ('. Approval owner fixture ruling', ''),
                   ('- Source. Fixture navigation change and supported-target declarations.\n', ''),
                   ('- Work type. mobile-behavior.', '- Work type. unknown.')]
        for before, after in changes:
            with self.subTest(before=before):
                self.assertNotEqual(self.check(plan.replace(before, after)).returncode, 0)

    def test_legacy_plans_still_require_exactly_ten(self):
        legacy = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
        self.assertEqual(self.check(legacy).returncode, 0)
        extra = '- [ ] Lane 11. Extra. Save `extra.png`. Pass when visible.\n'
        result = self.check(legacy.replace('**Verify, perf.**', extra + '**Verify, perf.**'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('expected 1 to 10', result.stderr)

    def test_installed_catalog_and_validator_drift_stop_the_check(self):
        for name in ['references/mobile-risks.json', 'scripts/mobile-coverage.mjs']:
            with self.subTest(file=name):
                file = self.plugin / 'skills/hugues-mode' / name
                original = file.read_bytes()
                file.write_bytes(original + b'\nchanged\n')
                result = self.check(mobile_plan())
                self.assertEqual(result.returncode, 2)
                self.assertIn('drift', result.stderr)
                file.write_bytes(original)

    def test_profile_and_risk_changes_require_exact_operator_ruling(self):
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.consumer), *args], text=True).strip()
        git('init', '-q'); git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
        path = self.consumer / 'plan.md'
        path.write_text(mobile_plan()); git('add', 'plan.md'); git('commit', '-qm', 'Approved mobile plan')
        base = git('rev-parse', 'HEAD'); git('update-ref', 'refs/remotes/origin/main', base)
        path.write_text(mobile_plan().replace('Reason saved navigation changes.', 'Reason builder proposes removing coverage.'))
        git('commit', '-qam', 'Proposed coverage change'); head = git('rev-parse', 'HEAD')
        args = ('--repo', self.consumer, '--plan', 'plan.md', '--section', 'PR 1', '--base-sha', base, '--head-sha', head)
        pending = self.bound('plan-compare', *args)
        self.assertEqual(pending.returncode, 2)
        report = json.loads(pending.stdout)
        self.assertIn('builder proposes', report['diff'])
        ruling = self.area / 'ruling.json'
        ruling.write_text(json.dumps({'comparison_sha256': report['comparison_sha256'],
                                     'decision': 'approved', 'reference': 'actual fixture owner ruling'}))
        approved = self.bound('plan-compare', *args, '--ruling', ruling)
        self.assertEqual(approved.returncode, 0, approved.stderr)
        self.assertTrue(json.loads(approved.stdout)['verification_required'])

    def test_unknown_area_rejects_with_diagnostic_without_crashing(self):
        result = self.check(mobile_plan().replace('Areas. navigation.', 'Areas. constructor.'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unknown changed area constructor', result.stderr)
        self.assertNotIn('TypeError', result.stderr)

    def test_malformed_profile_declarations_do_not_fall_back(self):
        legacy = (ROOT / 'tests/fixtures/adapter-plan.md').read_text()
        for field in ['"verification_profile": mobile-risk-v1',
                      "'verification_profile': mobile-risk-v1",
                      'verification_profile mobile-risk-v1']:
            with self.subTest(field=field):
                result = self.check('---\n' + field + '\n---\n' + legacy)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('verification_profile', result.stderr)

    def test_unresolved_fields_cannot_hide_behind_whitespace(self):
        plan = mobile_plan()
        for before, after in [('Identity debug APK on fixture emulator.', 'Identity unknown .'),
                              ('Source. Fixture navigation change and supported-target declarations.', 'Source. unresolved .'),
                              ('Reason saved navigation changes.', 'Reason unknown .')]:
            with self.subTest(field=before):
                self.assertNotEqual(self.check(plan.replace(before, after)).returncode, 0)
