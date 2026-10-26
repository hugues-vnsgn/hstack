import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

from test_host_adapters import InstalledFixture

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_core
import seal_payload


class InstalledMobileGuidance(InstalledFixture, unittest.TestCase):
    def read(self, path):
        result = self.bound('read-workflow', path)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_installed_selection_contract_covers_the_nine_source_contexts(self):
        text = self.read('adapters/host-mobile-languages.md')
        rows = [tuple(cell.strip() for cell in line.strip('|').split('|'))
                for line in text.splitlines() if line.startswith('| ')]
        self.assertEqual(rows[2:], [
            ('Swift package, Package.swift targets and Swift declarations, no UI imports',
             'swift-best-practices/SKILL.md', '-'),
            ('SwiftUI app, SwiftUI import and View or App declaration',
             'swift-best-practices/SKILL.md', 'swift-best-practices/references/swiftui.md'),
            ('UIKit app, UIKit import and controller or view declaration',
             'swift-best-practices/SKILL.md', 'swift-best-practices/references/uikit.md'),
            ('Native Android Compose, Android plugin and Compose UI declarations',
             'kotlin-best-practices/SKILL.md', 'kotlin-best-practices/references/android-compose.md'),
            ('Common Kotlin, multiplatform plugin and commonMain or commonTest declarations',
             'kotlin-best-practices/SKILL.md', 'kotlin-best-practices/references/kmp.md'),
            ('Platform Kotlin, multiplatform plugin and iosMain native API declarations',
             'kotlin-best-practices/SKILL.md', 'kotlin-best-practices/references/kmp.md, kotlin-best-practices/references/native-interop.md'),
            ('CMP wrappers, Compose Multiplatform configuration and UIKitView or AndroidView declarations',
             'kotlin-best-practices/SKILL.md', 'kotlin-best-practices/references/kmp.md, kotlin-best-practices/references/cmp.md'),
            ('Kotlin build scripts, build.gradle.kts or settings.gradle.kts without app declarations',
             'kotlin-best-practices/SKILL.md', '-'),
            ('Unrelated non-mobile task, no Swift or Kotlin source read or edited', '-', '-'),
        ])
        for phrase in ['Each fresh worker performs its own reads before the relevant source.',
                       'Read the baseline first', 'Keep unresolved ownership explicit',
                       'Consumer and external skills retain native invocation controls.']:
            self.assertIn(phrase, text)
        host = self.read('adapters/host.md')
        self.assertIn('[Mobile language scope](host-mobile-languages.md)', host)

    def test_installed_baselines_are_user_only_and_helpers_refuse_their_bodies(self):
        for name, expected_paths in [
                ('swift-best-practices', '["**/*.swift"]'),
                ('kotlin-best-practices', '["**/*.kt", "**/*.kts"]')]:
            with self.subTest(name=name):
                path = f'skills/{name}/SKILL.md'
                fields = check_core.native_frontmatter((self.plugin / path).read_text())
                self.assertEqual(fields['name'], name)
                self.assertEqual(fields['disable-model-invocation'], True)
                self.assertEqual(fields['paths'], expected_paths)
                self.assertEqual((self.plugin / f'skills/{name}/agents/openai.yaml').read_text(),
                                 'policy:\n  allow_implicit_invocation: false\n')
                denied = self.bound('read-workflow', path)
                self.assertEqual(denied.returncode, 2)
                self.assertIn('native skill invocation', denied.stderr)

    def test_owned_reference_links_resolve_from_the_installed_owner(self):
        owners = [self.plugin / f'skills/{name}' for name in
                  ['swift-best-practices', 'kotlin-best-practices']]
        reached = set()
        for owner in owners:
            for path in owner.rglob('*.md'):
                for target in re.findall(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)', path.read_text()):
                    if '://' in target:
                        continue
                    resolved = (path.parent / target).resolve()
                    self.assertTrue(resolved.is_file(), (path, target))
                    self.assertTrue(resolved.is_relative_to(self.plugin))
                    if '/references/' in str(resolved):
                        relative = resolved.relative_to(self.plugin).as_posix()
                        self.assertEqual(self.read(relative), resolved.read_text())
                        reached.add(relative)
        self.assertEqual(reached, {
            'skills/swift-best-practices/references/swiftui.md',
            'skills/swift-best-practices/references/uikit.md',
            'skills/kotlin-best-practices/references/android-compose.md',
            'skills/kotlin-best-practices/references/kmp.md',
            'skills/kotlin-best-practices/references/native-interop.md',
            'skills/kotlin-best-practices/references/cmp.md',
        })
        mobile = json.loads((ROOT / 'docs/CONTEXT-BUDGET.json').read_text())['mobile_guidance']
        self.assertEqual(set(mobile), {'scope', 'candidate'})
        self.assertEqual(mobile['candidate']['unique_files'], 11)
        self.assertEqual(set(mobile['candidate']['paths']), {'plugin/' + p for p in reached} | {
            'plugin/skills/swift-best-practices/SKILL.md',
            'plugin/skills/kotlin-best-practices/SKILL.md',
            'plugin/adapters/host-mobile-languages.md',
            'plugin/skills/hugues-mode/references/mobile-review.md',
            'plugin/skills/hugues-mode/references/mobile-forensics.md',
        })
        self.assertEqual(set(mobile['candidate']['inputs']), set(mobile['candidate']['paths']))

    def test_existing_review_and_diagnosis_phases_reach_native_guidance(self):
        workflow = self.read('adapters/mobile-workflows.md')
        self.assertIn("At the selected action's existing review phase", workflow)
        self.assertIn('This adds no phase or review panel.', workflow)
        for phase in ['bug-fix', 'kmp-bridge-change', 'cmp-two-target-change']:
            text = self.read(f'skills/hugues-mode/playbooks/{phase}.md')
            self.assertIn('[mobile review lens](../references/mobile-review.md)', text)
        bug_fix = self.read('skills/hugues-mode/playbooks/bug-fix.md')
        self.assertIn('6. Run **Opening a PR**.', bug_fix)
        self.assertIn('run **interrogate** with the [mobile review lens]', bug_fix)
        self.assertIn('even when you open the PR yourself.', bug_fix)
        self.assertIn('Reuse this review when Opening a PR already requires `interrogate`.', bug_fix)
        opening = self.read('skills/hugues-mode/playbooks/opening-a-pr.md')
        self.assertIn('A subagent that opens a PR runs `interrogate`', opening)
        review = self.read('skills/hugues-mode/references/mobile-review.md')
        for risk in ['Lifecycle and process restoration', 'Main-thread safety', 'Cancellation',
                     'Resource release', 'Offline, error and retry', 'Accessibility and text scaling',
                     'Native-wrapper ownership']:
            self.assertIn('| ' + risk + ' |', review)
        self.assertIn('covered with a linked assertion or observation, or gap with', review)
        forensics = self.read('skills/hugues-mode/playbooks/runtime-forensics.md')
        self.assertIn('[native forensics](../references/mobile-forensics.md) before step 1', forensics)
        native = self.read('skills/hugues-mode/references/mobile-forensics.md')
        for phrase in ['Instruments Time Profiler', 'Xcode Memory Graph', 'Perfetto',
                       'Heap dump', 'same runtime', 'hypothesis as unconfirmed']:
            self.assertIn(phrase, native)

    def test_lane_selection_preserves_ten_lanes_and_optional_supplements(self):
        workflow = self.read('adapters/mobile-workflows.md')
        planning = workflow.split('For mobile multi-phase plans, before step 4', 1)[1]
        planning = planning.split('Read [mobile lanes]', 1)[0]
        self.assertIn('writes\nthe live lanes', planning)
        self.assertIn('[mobile lanes](../skills/hugues-mode/references/mobile-lanes.md)', planning)
        self.assertIn('[mobile review lens](../skills/hugues-mode/references/mobile-review.md)', planning)
        plan = self.read('skills/hugues-mode/playbooks/multi-phase-plan.md')
        self.assertIn('4. Copy the skeleton below into the plan file and fill every placeholder.', plan)
        self.assertIn('Ten lanes at the PR head drive the real surface', plan)
        lanes = self.read('skills/hugues-mode/references/mobile-lanes.md')
        self.assertIn("Preserve the selected multi-phase plan's ten-lane rule.", lanes)
        self.assertIn('An inapplicable risk needs a reason', lanes)
        self.assertIn('an applicable unrun risk remains a gap.', lanes)
        self.assertIn('are optional supplements, reached through native invocation controls.', lanes)
        self.assertNotIn('These skills are external prerequisites', lanes)
        self.assertIn('[Swift baseline](../../swift-best-practices/SKILL.md)', lanes)
        self.assertIn('[Kotlin baseline](../../kotlin-best-practices/SKILL.md)', lanes)


class AuthoredMobileInventory(unittest.TestCase):
    def test_resealing_cannot_admit_missing_inventory_or_wrong_skill_controls(self):
        with tempfile.TemporaryDirectory(prefix='hstack-mobile-inventory-') as temp:
            root = Path(temp) / 'package'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))
            self.assertEqual(check_core.check(root)['active_skills'], 63)
            changes = [
                ('docs/upstream/consolidation.json', lambda text: text.replace('"authored_skills": {', '"unregistered_skills": {'), 'authored skill inventory differs'),
                ('plugin/skills/swift-best-practices/SKILL.md', lambda text: text.replace('disable-model-invocation: true', 'disable-model-invocation: false'), 'host invocation table differs'),
                ('plugin/skills/kotlin-best-practices/SKILL.md', lambda text: text.replace('"**/*.kts"', '"**/*.java"'), 'native path scope differs'),
                ('plugin/skills/kotlin-best-practices/agents/openai.yaml', lambda text: text.replace('false', 'true'), 'native invocation policy differs'),
            ]
            for name, mutate, expected in changes:
                with self.subTest(name=name):
                    path = root / name
                    original = path.read_text()
                    path.write_text(mutate(original))
                    seal_payload.seal(root)
                    with self.assertRaisesRegex(ValueError, expected):
                        check_core.check(root)
                    path.write_text(original)
                    seal_payload.seal(root)
