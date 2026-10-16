"""Static integration contracts on shipped files; no simulated host/mobile execution.

Mutation tests exercise real manifest discovery, numbered-step handoffs and the
existing package checker. Passing proves these Markdown relationships only.
"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from test_wp2_contract import MODE, PLAYBOOKS, routes, section, steps

from release_snapshot import release_root
ROOT = release_root()
RETAINED = {'how', 'why', 'architect', 'arena', 'tdd', 'blast-radius',
            'maintain-verification-skill', 'correct'}
DEFERRED = {'swarm', 'show-me-your-work', 'setup-huguesstack'}
RC1 = '21a82942019292f7212ff1185e9ef187ac96e86d'
RC2_HOST = 'e2ff899f226184e6109029e5bdb3ac19838b80e4'
RC2_LANE = 'dba645fa3adc024487c1137486a81b31e12ec832'
# These contracts relate call sites to shipped tools, not tool-body wording.
CALLS = {
    ('investigation', 1): {'how', 'why'},
    ('bug-fix', 2): {'how', 'why'},
    ('bug-fix', 3): {'architect', 'tdd'},
    ('bug-fix', 5): {'tdd'},
    ('feature', 1): {'how'},
    ('feature', 2): {'architect', 'arena'},
    ('feature', 4): {'arena'},
    ('prototype', 2): {'architect', 'arena'},
    ('refactoring', 1): {'how'},
    ('refactoring', 3): {'architect', 'blast-radius'},
    ('opening-a-pr', 1): {'blast-radius'},
    ('authoring-a-skill', 1): {'create-verification-skill', 'maintain-verification-skill', 'correct'},
    ('kmp-bridge-change', 2): {'tdd'},
    ('kmp-bridge-change', 3): {'how', 'architect', 'blast-radius'},
    ('cmp-two-target-change', 2): {'tdd'},
    ('cmp-two-target-change', 3): {'how', 'architect', 'blast-radius'},
}


def discovered(root):
    manifest = json.loads((root / 'plugin/.claude-plugin/plugin.json').read_text())
    paths = manifest['skills']
    if isinstance(paths, str):
        paths = [paths]
    return {p.resolve() for directory in paths
            for p in (root / 'plugin' / directory).rglob('SKILL.md')}


def integration_errors(root):
    errors = []
    found = discovered(root)
    expected = {root / 'plugin/skills' / name / 'SKILL.md' for name in RETAINED}
    if not {p.resolve() for p in expected} <= found:
        errors.append('retained manifest discovery')
    mode = (root / MODE / 'SKILL.md').read_text()
    # Mode index and call sites must reach files actually discovered by the manifest.
    guidance = section(mode, 'Available guidance')
    for name in RETAINED:
        if f'../{name}/SKILL.md' not in guidance:
            errors.append(f'mode index: {name}')
    table = routes(mode)
    if set(table) != PLAYBOOKS | {'interrogate'}:
        errors.append('existing routes')
    for (route, number), dependencies in CALLS.items():
        path = root / MODE / table[route][1]
        numbered = dict(steps(path.read_text()))
        body = numbered.get(str(number), '')
        linked = { (path.parent / target).resolve()
                  for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', body) }
        for name in dependencies:
            target = (root / 'plugin/skills' / name / 'SKILL.md').resolve()
            if target not in linked or target not in found:
                errors.append(f'{route} step {number}: {name}')
        if 'in full' not in body:
            # Reuse is valid after an earlier mandatory complete read in this checklist.
            for name in dependencies:
                earlier = [text for n, text in numbered.items() if int(n) < number]
                if not any(f'../../{name}/SKILL.md' in text and 'in full' in text for text in earlier):
                    errors.append(f'{route} step {number}: complete read')
    # Observe order inside the actual step copied into the host checklist.
    bug = dict(steps((root / MODE / 'playbooks/bug-fix.md').read_text()))
    gate = bug['3']
    sequence = ['fresh scoped regression-test worker', 'independently run',
                'unfixed production code', 'observed RED',
                'separate fresh production implementation subagent']
    positions = [gate.find(item) for item in sequence]
    if min(positions) < 0 or positions != sorted(positions):
        errors.append('bug regression before production')
    if 'impractical seam' not in gate or 'original runtime failing observation' not in gate:
        errors.append('bug runtime fallback')
    if 'RED evidence from step 3' not in bug['5'] or 'same regression' not in bug['5']:
        errors.append('same-check GREEN handoff')
    for route in ('kmp-bridge-change', 'cmp-two-target-change'):
        numbered = dict(steps((root / MODE / f'playbooks/{route}.md').read_text()))
        body = numbered['2']
        sequence = ['fresh scoped regression-test worker', 'independently run',
                    'unfixed production code', 'observed RED', 'separate fresh production worker in step 3']
        positions = [body.find(item) for item in sequence]
        if min(positions) < 0 or positions != sorted(positions) or 'impractical-seam reason' not in body:
            errors.append(f'{route}: RED before production')
    author = dict(steps((root / MODE / 'playbooks/authoring-a-skill.md').read_text()))
    handoff = author['1']
    required = ['new consumer-local', 'existing bounded recipe', 'hand off to its numbered steps',
                'this playbook ends at that handoff', 'source wave', 'coordinator-owned live proof',
                'clean/changed/blocked', 'clean or blocked produces no PR']
    if not all(part in handoff for part in required) or 'fresh implementation subagent' not in author['2']:
        errors.append('maintenance before generic worker')
    if 'at least two occurrences per class' not in handoff:
        errors.append('recurring class evidence')
    generator = (root / 'plugin/skills/create-verification-skill/SKILL.md').read_text()
    if '../maintain-verification-skill/SKILL.md' not in generator or 'existing bounded recipe' not in generator:
        errors.append('existing generator maintenance handoff')
    # Analysis can delegate or run checks: preview must defer it to execution.
    mode_steps = dict(steps(mode))
    if 'execute that analysis only in step 4' not in mode_steps['2'] or 'reads and plans only' not in mode_steps['2']:
        errors.append('wide preview stop')
    if 'execute the selected blast-radius analysis only here' not in mode_steps['4']:
        errors.append('wide analysis execution scope')
    return errors


def host_binding_errors(root):
    errors = []
    receipt = (root / 'docs/rc-validation.md').read_text()
    intro = receipt.split('Recorded **6 October', 1)[0]
    if RC1 not in intro or '54 plugin-file fingerprints' not in intro:
        errors.append('historical RC1 fingerprint binding')
    if 'no RC2 loading, routing, delegation' not in intro:
        errors.append('RC2 coverage boundary')
    support = (root / 'docs/support.md').read_text()
    # New observations have their own revision-bound receipt. The historical
    # RC1 packet cannot cover them, and bounded observations cannot promote
    # the full workflow/mobile acceptance cell.
    rows = [tuple(part.strip() for part in row.strip('|').split('|'))
            for row in support.splitlines()
            if row.startswith(('| RC2', '| Historical RC2'))]
    by_cell = {row[0]: row[1:] for row in rows if len(row) == 3}
    if len(by_cell) != len(rows):
        errors.append('RC2 unique evidence cells')
    full = by_cell.get('RC2 full eight-workflow adherence', ())
    if (len(full) != 2 or full[0] != 'blocked' or not all(item in full[1] for item in
            ('Bounded native Swift and Kotlin work is now observed',
             'full eight-workflow adherence', 'native todo integration',
             'four-domain task completeness remain unproven'))):
        errors.append('RC2 full workflow acceptance blocked')
    observed_cells = {'RC2 host loading and route previews',
                      'RC2 bounded retained workflow observations',
                      'Historical RC2 static recipe/cold pickup',
                      'RC2 native Swift S1 feature', 'RC2 native Kotlin K1 feature logic',
                      'RC2 K1 native UI/recipe/maintenance',
                      'RC2 native project recipe discovery'}
    actual_observed = {row[0] for row in rows if len(row) == 3 and row[1] == 'observed-pass'}
    optional_observed = {'RC2 repaired lane previews'}
    if not observed_cells <= actual_observed <= observed_cells | optional_observed:
        errors.append('RC2 bounded observation scope')
    loading = by_cell.get('RC2 host loading and route previews', ())
    if (len(loading) != 2 or loading[0] != 'observed-pass' or
            f'`{RC2_HOST[:7]}`' not in loading[1] or
            '(rc2-host-validation.md)' not in loading[1] or
            not all(item in loading[1] for item in ('35 skills', '16 routes', '87 steps',
                                                   'unsupported Kotlin'))):
        errors.append('RC2 loading receipt binding')
    bounded = by_cell.get('RC2 bounded retained workflow observations', ())
    if (len(bounded) != 2 or bounded[0] != 'observed-pass' or
            '(rc2-host-validation.md#bounded-workflow-observations)' not in bounded[1] or
            'runtime unrun' not in bounded[1]):
        errors.append('RC2 bounded workflow receipt binding')
    pickup = by_cell.get('Historical RC2 static recipe/cold pickup', ())
    if (len(pickup) != 2 or pickup[0] != 'observed-pass' or
            '(rc2-host-validation.md#bounded-workflow-observations)' not in pickup[1] or
            not all(item in pickup[1] for item in
                    ('static Kotlin recipe', 'read-only Codex pickup',
                     'No mobile cycle, actual pause/compaction or resumed GREEN'))):
        errors.append('RC2 static recipe pickup limits')
    lane = by_cell.get('RC2 lane evidence', ())
    if (len(lane) != 2 or lane[0] != 'observed-fail' or
            f'`{RC2_LANE[:7]}`' not in lane[1] or
            'strict fixture comparisons FAIL' not in lane[1] or 'No full fixture PASS' not in lane[1]):
        errors.append('RC2 strict lane failures retained')
    host_receipt = (root / 'docs/rc2-host-validation.md').read_text()
    binding = host_receipt.split('## Original RC2 loading and routing', 1)[0]
    if (RC2_HOST not in binding or RC2_LANE not in binding or RC1 in binding or
            '79 plugin files' not in binding or 'distinct snapshots' not in binding):
        errors.append('separate RC2 revision binding')
    historical = ' '.join(section(host_receipt, 'Bounded workflow observations').split())
    gaps = ' '.join(section(host_receipt, 'Remaining acceptance gaps').split())
    if (not all(item in historical for item in
                ('Native Codex recipe invocation and a mobile recipe cycle remain unproven',
                 'The fixture lacks an app, native toolchain and device',
                 'In that initial synthetic snapshot',
                 'actual pause, compaction, resumed GREEN and persistent native todos remain unrun')) or
            not all(item in gaps for item in
                ('Full adherence of all eight retained workflows',
                 'complete maintenance/source-wave/live/cleanup cycle remain unproven',
                 'Later S1 Swift RED/GREEN/native assertion phases and K1 Kotlin unit/build work',
                 '(rc2-native-feature-proof.md)', 'K1 device/recipe/maintenance proof',
                 'full four-domain task coverage', 'compaction/native persistent todos',
                 'full clean generated-recipe cycle remain unproven')) or
            'no full six-case fixture PASS is claimed' not in host_receipt):
        errors.append('RC2 receipt acceptance limits')
    repaired = by_cell.get('RC2 repaired lane previews')
    if repaired is not None:
        # A later small sample can pass independently without rewriting the
        # earlier strict failures. Require its own scoped receipt and limits;
        # it supplies no full-workflow/native-mobile acceptance evidence.
        if ('(rc2-host-validation.md#repaired-schema-probes)' not in repaired[1] or
                not any(limit in repaired[1].lower() for limit in
                        ('no clean-head invocation or full workflow adherence claim',
                         'full workflow and native mobile execution unproven'))):
            errors.append('RC2 repaired preview scope')
        repaired_receipt = ' '.join(section(host_receipt, 'Repaired schema probes').split())
        if (not re.search(r'\b[0-9a-f]{40}\b', repaired_receipt) or
                RC1 in repaired_receipt or
                'six' not in repaired_receipt.lower() or
                not any(limit in repaired_receipt.lower() for limit in
                        ('full workflow adherence remains unproven; no consumer execution occurred',
                         'full workflow and native mobile execution remain unproven'))):
            errors.append('RC2 repaired preview receipt binding')
    errors.extend(native_binding_errors(root, by_cell))
    return errors


def native_binding_errors(root, by_cell):
    """Check current cells against their own bounded native receipt, not old runs."""
    errors = []
    support_contracts = {
        'RC2 native Swift S1 feature': ('observed-pass', 'S1 bounded native proof', (
            'Seven-case RED: two passes/five intended missing-command failures',
            'actual pause/fresh pickup', 'separate production change',
            '12 method identities/14 invocations', 'zero fail/skip',
            'UIKit/synthetic delegate selector dispatch only', '(rc2-native-feature-proof.md)')),
        'RC2 S1 complete maintenance/clean cycle': ('blocked', 'S1 clean cycle blocked', (
            'Source/live checkpoint coverage 4/4', 'cleanup proved',
            'Original simulator boot-state restoration unsupported',
            'original data continuity unproven', 'content changed during approved startup',
            'No full clean-cycle PASS')),
        'RC2 native Kotlin K1 feature logic': ('observed-pass', 'K1 bounded logic proof', (
            '15-case RED with three intended failures', 'actual pause/fresh pickup',
            'separate ViewModel normalization fix, 15/15 GREEN',
            'one retained compile failure and one corrected retry', '(rc2-native-feature-proof.md)')),
        'Historical RC2 K1 native readiness': ('blocked', 'K1 historical readiness blocked', (
            'Original readiness snapshot',
            'Six selectors/four checkpoints have source coverage',
            'all new native, recipe and maintenance runs unrun', 'blocked readiness',
            'no task-owned target/package started or unrelated device targeted')),
        'RC2 K1 native UI/recipe/maintenance': ('observed-pass', 'K1 bounded live proof', (
            'GREEN, recipe and maintenance each: six exact cases PASS, zero fail/skip/unrun',
            'four reopened, decoded, coordinator-viewed native images',
            'Android 16 / SDK 36 / full SDK 36.1', 'same retained APK',
            'bounded feature host/fakes only', 'Owned cleanup and evidence survival verified',
            'Original STOP/failures retained', 'no Room/full-app/hardware Enter/analytics proof',
            '(rc2-native-feature-proof.md#k1-private-continuation)')),
        'RC2 native project recipe discovery': ('observed-pass', 'native recipe fallback only', (
            'Both hosts actually read full S1/K1 recipe Markdown',
            'Claude catalog omitted these recipes',
            'Codex native discovery is self-reported without raw catalog proof',
            'Direct read establishes fallback only',
            '(rc2-native-feature-proof.md#recipe-discovery-and-preservation)')),
    }
    for cell, (state, error, required) in support_contracts.items():
        row = by_cell.get(cell, ())
        if len(row) != 2 or row[0] != state or not all(item in row[1] for item in required):
            errors.append(error)

    receipt_path = root / 'docs/rc2-native-feature-proof.md'
    if not receipt_path.is_file():
        return errors + ['native receipt missing']
    receipt = receipt_path.read_text()
    rows = [tuple(part.strip() for part in line.strip('|').split('|'))
            for line in receipt.splitlines() if line.startswith('| ')]
    by_target = {row[0]: ' '.join(' '.join(row[1:]).split())
                 for row in rows if len(row) == 3}
    native_contracts = {
        'Codex-coordinated S1, Swift/UIKit, NetNewsWire Debug arm64 on Xcode 27/iOS 26.4.1 simulator': (
            'S1 RED pickup receipt', ('seven cases, two passes/five literal missing',
            'UIKeyCommand', 'Test-only pause checkpoint', 'fresh checkpoint-only pickup',
            'before separate production work', 'Actual pause/pickup',
            'no compaction or native persistent-todo proof')),
        'Codex-coordinated K1, Kotlin/Compose, Now in Android search ViewModel/unit target': (
            'K1 RED GREEN receipt', ('RED: 15 cases, three intended failures',
            'Test-only pause checkpoint', 'fresh pickup', 'Separate ViewModel trim fix: 15/15 GREEN',
            'zero errors/skips', 'Feature logic with screen fakes',
            'no Room persistence/full-app proof')),
        'S1 guarded Shift-Return behavior': ('S1 bounded native receipt', (
            'positive result count and selection above one',
            '12 method identities/14 invocations, zero failures/skips',
            'Native UIKit bar and synthetic delegate', 'UIApplication.sendAction',
            'no physical hardware keyboard or full article Find journey')),
        'S1 generated recipe phase': ('S1 bounded recipe receipt', (
            '12 method identities/14 invocations, zero failures/skips',
            'four native rendered bar PNGs independently inspected',
            'Same bounded assertion surface', 'counts not added as unique tests')),
        'S1 maintenance phase': ('S1 clean cycle receipt blocked', (
            'Complete 4/4 source and live checkpoints',
            '12 method identities/14 invocations, zero failures/skips',
            'Overall maintenance remains blocked by original boot-state restoration',
            'no full clean-cycle PASS')),
        'K1 offline demo Debug UI-test APK': ('K1 built artifact is not live proof', (
            'Initial missing compile API failure retained', 'one retry built the APK',
            'Historical assembly snapshot',
            'BUILT, with no installation or driven result')),
        'Historical K1 native readiness': ('K1 historical receipt blocked', (
            'Original readiness snapshot',
            'Six selectors/four checkpoint images covered in source',
            'all new live phases BLOCKED/UNRUN', 'failed empty-inventory readiness',
            'No task device/package created or unrelated device targeted')),
        'Current K1 native UI, recipe and maintenance': ('K1 bounded live receipt', (
            'GREEN, recipe and maintenance each: six exact cases PASS, zero fail/skip/unrun',
            'four 1080 × 2400 native PNGs per phase reopened, decoded and viewed by the coordinator',
            'Android 16 / SDK 36 / full SDK 36.1', 'retained APK installed on the exact owned target',
            'Feature host/fake repositories only', 'owned cleanup and evidence survival verified',
            '(#k1-private-continuation)')),
    }
    for target, (error, required) in native_contracts.items():
        if not all(item in by_target.get(target, '') for item in required):
            errors.append(error)

    continuation = ' '.join(section(receipt, 'K1 private continuation').split())
    if not all(item in continuation for item in (
            'attempt 1 retained its STOP', 'unsupported SDK-minor validation',
            'defunct-process cleanup failure', 'successful guarded cleanup',
            'attempt 2 reached PREPARED', 'Android 16 / SDK 36 / full SDK 36.1',
            'Positive exact-package absence', 'APK installation Success',
            'GREEN, recipe and maintenance each ran six exact cases once',
            'six PASS, zero fail/skip/unrun, with no protocol errors',
            'all twelve were reopened and decoded after cleanup',
            'individually viewed by the coordinator', 'not eighteen unique tests',
            'No new assertion or build retry', 'no fresh build or unit-test execution claim',
            'No Room persistence/deduplication, full-app journey, hardware Enter',
            'analytics behavior or whole-OS network proof',
            'whitespace come from native assertions, not pixels alone',
            'Checkpoint 04 captures the cleared editor after whitespace assertions',
            'native Autofill bubble', 'Exact-package absence and exact owned-process absence',
            'Known preexisting Codex config drift remains unattributed and untouched',
            'post-cleanup inventory is an observation, not an accepted future baseline',
            'Attempt 3 was unclaimed and is unavailable after PREPARED',
            'PASS_BOUNDED_NATIVE_CYCLE_AND_REOPENED_EVIDENCE', 'checker exit 0')):
        errors.append('K1 continuation scope and closure')
    # Bind the current result to its own opaque final receipt, never the APK
    # hash or a historical native/host packet standing in for runtime proof.
    final_binding = re.search(r'checker exit 0\. SHA-256: `([0-9a-f]{64})`', continuation)
    index = (root / 'docs/evidence-index.md').read_text()
    current_index = next((line for line in index.splitlines()
                          if line.startswith('| RC2 S1/K1 feature continuation |')), '')
    if (not final_binding or final_binding[1] not in current_index or
            final_binding[1] in section(receipt, 'Public artifact identities')):
        errors.append('K1 final receipt binding')

    preservation = ' '.join(section(receipt, 'Recipe discovery and preservation').split())
    if not all(item in preservation for item in (
            'probes prove the direct-read fallback, with no native-loader success claim',
            'Original old-container continuity remains UNPROVEN',
            'Identity preservation does not mean unchanged content',
            'Safe restoration to the original Shutdown state remains unsupported',
            'residue prevents a full clean-cycle claim',
            'global Claude settings hash changed', 'attribution remains UNPROVEN',
            'No all-global-settings- unchanged claim is supported')):
        errors.append('native preservation limits')
    current = ' '.join(section(receipt, 'Public artifact identities').split())
    if not all(item in current for item in (
            'Historical Swift five-method/seven-invocation and Kotlin nine-unit/five-UI slices remain historical',
            'they supply no K1 new UI proof', 'Full eight-workflow adherence',
            'four-domain feature completeness', 'native Codex install/invocation',
            'compaction and general persistence remain unproven')):
        errors.append('historical native slices cannot prove current coverage')
    return errors


class RetainedIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-retained-integration-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))

    def test_real_registered_call_sites_and_order(self):
        self.assertEqual(integration_errors(self.root), [])
        self.assertEqual(len(discovered(self.root)), 35)

    def test_manifest_removal_excludes_real_call_targets(self):
        path = self.root / 'plugin/.claude-plugin/plugin.json'
        manifest = json.loads(path.read_text())
        manifest['skills'] = ['./skills/hugues-mode']
        path.write_text(json.dumps(manifest))
        errors = integration_errors(self.root)
        self.assertIn('retained manifest discovery', errors)
        self.assertIn('feature step 2: architect', errors)

    def test_every_leaf_link_required_in_numbered_steps(self):
        for (route, number), dependencies in CALLS.items():
            path = self.root / MODE / f'playbooks/{route}.md'
            original = path.read_text()
            numbered = dict(steps(original))
            for name in dependencies:
                with self.subTest(route=route, step=number, dependency=name):
                    changed = numbered[str(number)].replace(f'../../{name}/SKILL.md', '../../interrogate/SKILL.md')
                    self.assertNotEqual(changed, numbered[str(number)])
                    path.write_text(original.replace(numbered[str(number)], changed))
                    self.assertIn(f'{route} step {number}: {name}', integration_errors(self.root))
                    path.write_text(original)

    def test_prose_link_outside_numbered_step_cannot_replace_handoff(self):
        path = self.root / MODE / 'playbooks/feature.md'
        original = path.read_text()
        step = dict(steps(original))['2']
        path.write_text(original.replace(step, step.replace('../../architect/SKILL.md', '../../interrogate/SKILL.md'))
                        + '\nRead [architect](../../architect/SKILL.md) in full.\n')
        self.assertIn('feature step 2: architect', integration_errors(self.root))

    def test_missing_actual_leaf_rejected_by_package_checker(self):
        (self.root / 'plugin/skills/tdd/SKILL.md').unlink()
        result = subprocess.run(['sh', str(self.root / 'scripts/check-plugin.sh'), str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('playbooks/bug-fix.md: broken local link', result.stderr)
        self.assertIn('../../tdd/SKILL.md', result.stderr)

    def test_RED_moved_after_production_worker_rejected(self):
        path = self.root / MODE / 'playbooks/bug-fix.md'
        text = path.read_text()
        path.write_text(text.replace('observed RED', 'a planned check', 1)
                        .replace('separate fresh production implementation subagent.',
                                 'separate fresh production implementation subagent, then observe observed RED.', 1))
        self.assertIn('bug regression before production', integration_errors(self.root))

    def test_shared_bug_RED_missing_rejected(self):
        for route in ('kmp-bridge-change', 'cmp-two-target-change'):
            path = self.root / MODE / f'playbooks/{route}.md'
            original = path.read_text()
            with self.subTest(route=route):
                path.write_text(original.replace('observed RED', 'planned RED'))
                self.assertIn(f'{route}: RED before production', integration_errors(self.root))
                path.write_text(original)

    def test_maintenance_moved_after_generic_worker_rejected(self):
        path = self.root / MODE / 'playbooks/authoring-a-skill.md'
        text = path.read_text()
        first = dict(steps(text))['1']
        maintenance = re.search(r'For auditing.*?produces no PR\.', first)[0]
        path.write_text(text.replace(maintenance, '') + '\n' + maintenance + '\n')
        self.assertIn('maintenance before generic worker', integration_errors(self.root))

    def test_recurring_single_mistake_is_not_correct_workflow(self):
        path = self.root / MODE / 'playbooks/authoring-a-skill.md'
        path.write_text(path.read_text().replace('at least two occurrences per class', 'one observed mistake'))
        self.assertIn('recurring class evidence', integration_errors(self.root))

    def test_wide_preview_analysis_execution_rejected(self):
        path = self.root / MODE / 'SKILL.md'
        path.write_text(path.read_text().replace('execute that analysis only in step 4', 'execute the analysis now'))
        self.assertIn('wide preview stop', integration_errors(self.root))

    def test_approved_deferred_files_are_absent_and_ledger_preserves_scope(self):
        ledger = json.loads((self.root / 'docs/upstream/huguesStack-dispositions.json').read_text())
        deferred_rows = [row for row in ledger['items']
                         if row['path'].split('/')[2:3] and row['path'].split('/')[2] in
                         {'swarm', 'show-me-your-work', 'setup-pstack'}]
        self.assertTrue(deferred_rows)
        for row in deferred_rows:
            self.assertEqual((row['disposition'], row['implementation_state'], row['destinations']),
                             ('ignore with reason', 'deferred', []), row['path'])
        for name in DEFERRED:
            self.assertFalse((self.root / 'plugin/skills' / name).exists())
        # A deferred directory cannot masquerade as one of the retained tools.
        self.assertTrue(RETAINED.isdisjoint(DEFERRED))

    def test_release_versions_match_without_native_execution_claim(self):
        plugin = json.loads((self.root / 'plugin/.claude-plugin/plugin.json').read_text())
        market = json.loads((self.root / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(plugin['version'], '0.1.0')
        self.assertEqual(market['plugins'][0]['version'], plugin['version'])
        self.assertEqual(market['plugins'][0]['source'], './plugin')
        self.assertEqual(plugin['skills'], ['./skills'])

    def test_historical_host_evidence_stays_separate_from_RC2(self):
        self.assertEqual(host_binding_errors(self.root), [])

    def test_historical_fingerprints_cannot_be_promoted_to_RC2(self):
        path = self.root / 'docs/rc-validation.md'
        path.write_text(path.read_text().replace(RC1, 'f126656d2718084de8292cda0cb40b81333e4d6e'))
        self.assertIn('historical RC1 fingerprint binding', host_binding_errors(self.root))

    def test_full_workflow_mobile_cell_cannot_be_promoted_by_bounded_observations(self):
        path = self.root / 'docs/support.md'
        text = path.read_text()
        row = next(line for line in text.splitlines()
                   if line.startswith('| RC2 full eight-workflow adherence |'))
        path.write_text(text.replace(row, row.replace('| blocked |', '| observed-pass |')))
        errors = host_binding_errors(self.root)
        self.assertIn('RC2 full workflow acceptance blocked', errors)
        self.assertIn('RC2 bounded observation scope', errors)

    def test_RC2_observations_require_separate_revision_bound_receipt(self):
        path = self.root / 'docs/rc2-host-validation.md'
        original = path.read_text()
        for revision in (RC2_HOST, RC2_LANE):
            with self.subTest(revision=revision):
                path.write_text(original.replace(revision, RC1))
                self.assertIn('separate RC2 revision binding', host_binding_errors(self.root))
        path.write_text(original)
        path = self.root / 'docs/support.md'
        original = path.read_text()
        for old, new, error in (
                (f'`{RC2_HOST[:7]}`', f'`{RC1[:7]}`', 'RC2 loading receipt binding'),
                ('(rc2-host-validation.md)', '(rc-validation.md)', 'RC2 loading receipt binding'),
                ('(rc2-host-validation.md#bounded-workflow-observations)',
                 '(rc-validation.md)', 'RC2 bounded workflow receipt binding'),
                ('No mobile cycle, actual pause/compaction or resumed GREEN',
                 'Mobile cycle and resumed GREEN passed', 'RC2 static recipe pickup limits')):
            with self.subTest(binding=old):
                self.assertIn(old, original)
                path.write_text(original.replace(old, new))
                self.assertIn(error, host_binding_errors(self.root))

    def test_semantic_lane_observations_cannot_hide_strict_fixture_failures(self):
        path = self.root / 'docs/support.md'
        original = path.read_text()
        row = next(line for line in original.splitlines() if line.startswith('| RC2 lane evidence |'))
        path.write_text(original.replace(row, row.replace('| observed-fail |', '| observed-pass |')))
        self.assertIn('RC2 strict lane failures retained', host_binding_errors(self.root))

    def assert_boundary_mutation(self, document, old, new, error):
        path = self.root / 'docs' / document
        original = path.read_text()
        self.assertIn(old, original)
        self.assertNotEqual(old, new)
        try:
            path.write_text(original.replace(old, new, 1))
            self.assertIn(error, host_binding_errors(self.root))
        finally:
            path.write_text(original)

    def test_current_native_observations_require_their_own_receipt(self):
        (self.root / 'docs/rc2-native-feature-proof.md').unlink()
        self.assertIn('native receipt missing', host_binding_errors(self.root))

    def test_completed_native_RED_GREEN_and_pickup_cannot_be_erased_as_unrun(self):
        for document, old, new, error in (
                ('support.md', 'actual pause/fresh pickup', 'pause/pickup unrun',
                 'S1 bounded native proof'),
                ('rc2-native-feature-proof.md', 'Actual pause/pickup, with no compaction',
                 'Pause/pickup unrun, with no compaction', 'S1 RED pickup receipt'),
                ('rc2-native-feature-proof.md', 'Separate ViewModel trim fix: 15/15 GREEN',
                 'ViewModel fix and GREEN unrun', 'K1 RED GREEN receipt'),
                ('rc2-host-validation.md',
                 'Later S1 Swift RED/GREEN/native assertion phases and K1 Kotlin unit/build work',
                 'All native Swift and Kotlin work remains unrun', 'RC2 receipt acceptance limits')):
            with self.subTest(document=document, evidence=old):
                self.assert_boundary_mutation(document, old, new, error)

    def test_S1_bounded_dispatch_cannot_promote_full_native_journey(self):
        for document, old, new, error in (
                ('support.md', 'UIKit/synthetic delegate selector dispatch only',
                 'Full native hardware keyboard and article Find journey proved', 'S1 bounded native proof'),
                ('rc2-native-feature-proof.md',
                 'no physical hardware keyboard or full article Find journey',
                 'physical hardware keyboard and full article Find journey passed',
                 'S1 bounded native receipt'),
                ('rc2-native-feature-proof.md',
                 'Same bounded assertion surface; separate phase, counts not added as unique tests',
                 'Full app coverage; separate phase, counts added as unique tests',
                 'S1 bounded recipe receipt')):
            with self.subTest(document=document, evidence=old):
                self.assert_boundary_mutation(document, old, new, error)

    def test_S1_live_checkpoints_cannot_promote_maintenance_clean_cycle(self):
        for document, old, new, error in (
                ('support.md', '| RC2 S1 complete maintenance/clean cycle | blocked |',
                 '| RC2 S1 complete maintenance/clean cycle | observed-pass |', 'S1 clean cycle blocked'),
                ('support.md', 'Original simulator boot-state restoration unsupported',
                 'Original simulator boot-state restoration proved', 'S1 clean cycle blocked'),
                ('rc2-native-feature-proof.md',
                 'Overall maintenance remains blocked by original boot-state restoration; no full clean-cycle PASS',
                 'Overall maintenance and full clean-cycle PASS; unrelated K1 work remains unproven',
                 'S1 clean cycle receipt blocked'),
                ('rc2-native-feature-proof.md', 'Complete 4/4 source and live checkpoints',
                 'Complete 4/4 source checkpoints only', 'S1 clean cycle receipt blocked'),
                ('rc2-native-feature-proof.md', 'Identity preservation does not mean\nunchanged content',
                 'Identity preservation proves unchanged content', 'native preservation limits'),
                ('rc2-native-feature-proof.md', 'Original old-container\ncontinuity remains UNPROVEN',
                 'Original old-container continuity proved', 'native preservation limits')):
            with self.subTest(document=document, evidence=old):
                self.assert_boundary_mutation(document, old, new, error)

    def test_K1_source_coverage_build_and_historical_UI_cannot_promote_live_phases(self):
        for document, old, new, error in (
                ('support.md', '| Historical RC2 K1 native readiness | blocked |',
                 '| Historical RC2 K1 native readiness | observed-pass |', 'K1 historical readiness blocked'),
                ('support.md', 'all new native, recipe and maintenance runs unrun',
                 'all new native, recipe and maintenance runs passed', 'K1 historical readiness blocked'),
                ('rc2-native-feature-proof.md', 'all new live phases BLOCKED/UNRUN',
                 'all new live phases PASS; unrelated compaction remains unproven', 'K1 historical receipt blocked'),
                ('rc2-native-feature-proof.md', 'BUILT, with no installation or driven result',
                 'BUILT, installed and driven successfully', 'K1 built artifact is not live proof'),
                ('support.md', 'six exact cases PASS, zero fail/skip/unrun',
                 'source selectors and historical five-UI proof only', 'K1 bounded live proof'),
                ('support.md', '(rc2-native-feature-proof.md#k1-private-continuation)',
                 '(rc2-host-validation.md)', 'K1 bounded live proof'),
                ('rc2-native-feature-proof.md',
                 'six exact cases PASS, zero fail/skip/unrun', 'APK assembly PASS only',
                 'K1 bounded live receipt'),
                ('rc2-native-feature-proof.md',
                 'all twelve were reopened and decoded after\ncleanup',
                 'all twelve were covered only in source', 'K1 continuation scope and closure'),
                ('rc2-native-feature-proof.md',
                 'No new\nassertion or build retry', 'Fresh assertion and build retries passed',
                 'K1 continuation scope and closure'),
                ('rc2-native-feature-proof.md',
                 'No Room persistence/deduplication, full-app journey, hardware Enter',
                 'Room persistence and full-app hardware Enter proved',
                 'K1 continuation scope and closure'),
                ('rc2-native-feature-proof.md',
                 'Checkpoint 04 captures the cleared editor\nafter whitespace assertions',
                 'Checkpoint 04 pixels prove exact whitespace', 'K1 continuation scope and closure'),
                ('rc2-native-feature-proof.md',
                 'post-cleanup inventory is an observation, not an accepted future\nbaseline',
                 'post-cleanup inventory is the accepted future baseline',
                 'K1 continuation scope and closure'),
                ('rc2-native-feature-proof.md',
                 'checker exit 0. SHA-256:', 'historical build SHA-256:',
                 'K1 final receipt binding'),
                ('rc2-native-feature-proof.md', 'they supply no K1 new UI proof',
                 'they establish K1 new UI proof', 'historical native slices cannot prove current coverage')):
            with self.subTest(document=document, evidence=old):
                self.assert_boundary_mutation(document, old, new, error)

    def test_historical_recipe_and_cold_pickup_limits_stay_in_their_snapshot(self):
        self.assert_boundary_mutation('support.md',
            '| Historical RC2 static recipe/cold pickup |', '| RC2 static recipe/cold pickup |',
            'RC2 static recipe pickup limits')
        self.assert_boundary_mutation('rc2-host-validation.md',
            'In that initial synthetic snapshot', 'In the current native packet',
            'RC2 receipt acceptance limits')
        path = self.root / 'docs/rc2-host-validation.md'
        original = path.read_text()
        historical = section(original, 'Bounded workflow observations')
        limit = 'actual pause, compaction, resumed GREEN and persistent native todos\nremain unrun'
        self.assertIn(limit, historical)
        # The same words elsewhere cannot supply this snapshot's missing boundary.
        path.write_text(original.replace(limit, 'full native persistence proved', 1) + '\n' + limit + '\n')
        self.assertIn('RC2 receipt acceptance limits', host_binding_errors(self.root))

    def test_recipe_direct_reads_and_settings_disclosure_cannot_be_promoted(self):
        for document, old, new, error in (
                ('support.md', 'Direct read establishes fallback only',
                 'Direct read proves native loader invocation', 'native recipe fallback only'),
                ('rc2-native-feature-proof.md',
                 'These probes prove the direct-read fallback, with no native-loader success claim',
                 'These probes prove native-loader success', 'native preservation limits'),
                ('rc2-native-feature-proof.md', 'A global Claude settings hash changed',
                 'All global settings hashes matched', 'native preservation limits')):
            with self.subTest(document=document, evidence=old):
                self.assert_boundary_mutation(document, old, new, error)

    def test_unrelated_unproven_marker_cannot_supply_full_workflow_boundary(self):
        self.assert_boundary_mutation('support.md',
            'four-domain task completeness remain unproven',
            'four-domain task completeness passed; unrelated design work remains unproven',
            'RC2 full workflow acceptance blocked')
        path = self.root / 'docs/support.md'
        path.write_text(path.read_text() + '\n| RC2 universal native acceptance | observed-pass | unrelated scope unproven |\n')
        self.assertIn('RC2 bounded observation scope', host_binding_errors(self.root))

    def test_later_bounded_previews_need_their_own_receipt_and_preserve_full_gate(self):
        support = self.root / 'docs/support.md'
        receipt = self.root / 'docs/rc2-host-validation.md'
        support_text = support.read_text()
        receipt_text = receipt.read_text()
        # Isolate the optional cell whether or not a later packet is present.
        support_text = '\n'.join(line for line in support_text.splitlines()
                                 if not line.startswith('| RC2 repaired lane previews |'))
        receipt_text = re.sub(r'^## Repaired schema probes\s*\n.*?(?=^## |\Z)', '',
                              receipt_text, flags=re.M | re.S)
        row = ('| RC2 repaired lane previews | observed-pass | Six scoped read-only cases. '
               '[Receipt](rc2-host-validation.md#repaired-schema-probes); '
               'full workflow and native mobile execution unproven |\n')
        support.write_text(support_text + '\n' + row)
        receipt.write_text(receipt_text)
        self.assertIn('RC2 repaired preview receipt binding', host_binding_errors(self.root))
        scoped = ('\n## Repaired schema probes\n\n'
                  'Six scoped cases bind revision `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`. '
                  'Full workflow and native mobile execution remain unproven.\n')
        receipt.write_text(receipt_text + scoped)
        self.assertEqual(host_binding_errors(self.root), [])
        receipt.write_text(receipt_text + scoped.replace('a' * 40, RC1))
        self.assertIn('RC2 repaired preview receipt binding', host_binding_errors(self.root))
        receipt.write_text(receipt_text + scoped.replace(
            'Full workflow and native mobile execution remain unproven',
            'Full workflow and native mobile execution passed; unrelated design remains unproven'))
        self.assertIn('RC2 repaired preview receipt binding', host_binding_errors(self.root))
        receipt.write_text(receipt_text + scoped)
        support.write_text(support_text + '\n' + row.replace('#repaired-schema-probes', ''))
        self.assertIn('RC2 repaired preview scope', host_binding_errors(self.root))
        support.write_text(support_text + '\n' + row.replace('execution unproven', 'execution passed'))
        self.assertIn('RC2 repaired preview scope', host_binding_errors(self.root))


if __name__ == '__main__':
    unittest.main()
