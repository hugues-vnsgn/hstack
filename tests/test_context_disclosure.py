from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_core
import measure_context
from test_host_adapters import InstalledFixture

TRUNK = 'ae7cec396976abddfe27ca701e9fe782bc7db6f7'
# The revision before Cursor became a native host, which is the 0.5.6 release.
# It is the baseline for the Cursor adapter allowance, and it is pinned rather
# than read from `origin/main` so the allowance does not collapse when that
# branch starts carrying the Cursor commit itself.
PRE_CURSOR = '4f64103ea6e7463ecc5e1d2b531e75ceb99c0d10'
# The Cursor-only features section grew when Cursor became a native host. After the review
# moved the per-feature Cursor actions, the subagent and model meanings, the transcript store,
# the foreground-delegate gap and the one-source rule out to plugin/adapters/hosts/cursor.md,
# the section's Cursor-specific content is the door sentence that points a Cursor session at
# that page, which sits here because the table below is where a Cursor session reads its
# instructions. The value is the section's live size over the trunk section it replaced
# (267 = 1452 - 1185); it is net-zero for the caps, which subtract the trunk guidance, and it
# records the section's real growth so a later edit to the section shows up here rather than
# passing unnoticed.
CURSOR_ONLY_SECTION_GROWTH_OVER_TRUNK = 267


def issue_110_guidance(read, host_guidance):
    mode = read('plugin/skills/hugues-mode/SKILL.md')
    workers = read('plugin/adapters/host-workers.md')
    bug = read('plugin/skills/hugues-mode/playbooks/bug-fix.md')
    sentences = {
        'plugin/skills/hugues-mode/SKILL.md': ['The mobile regression worker uses the general-purpose exception in [workers and models](../../adapters/host-workers.md).'],
        'plugin/adapters/host-workers.md': ['Report deliberate effort lowering too, with its reason.',
                                            'Full-mode workers load the mode per [host.md](host.md) before work.'],
    }
    texts = {
        'plugin/adapters/host.md': host_guidance(read('plugin/adapters/host.md')),
        'plugin/skills/hugues-mode/SKILL.md': (
            mode[mode.index('A step includes'):mode.index('\n\nA large or cross-cutting')]
            + next(line for line in mode.splitlines() if line.startswith('- Whenever a run spawned workers'))),
        'plugin/adapters/host-workers.md': workers[workers.index('The mobile regression worker is'):workers.index('\nAgent mode preserves')],
        'plugin/adapters/host-workflow-tools.md': check_core.section(read('plugin/adapters/host-workflow-tools.md'), 'Codex sandbox'),
        'plugin/skills/hugues-mode/playbooks/bug-fix.md': bug[bug.index('   Use a fresh general-purpose regression worker.'):bug.index('   Run the same selected regression')],
        'plugin/agents/hugues-agent.md': 'model: inherit\n',
        'plugin/agents/hugues-comment-sicko.md': 'model: inherit\n',
    }
    for path, extra in sentences.items():
        missing = [sentence for sentence in extra if ' '.join(sentence.split()) not in ' '.join(read(path).split())]
        assert not missing, (path, missing)
        texts[path] += ''.join(extra)
    return {path: len(text.encode()) for path, text in texts.items()}


def trunk_host_guidance(host):
    return (check_core.section(host, 'Inherited wording translations')
            + host[host.index('A step includes'):host.index('Name the file in your reply.')])


def at_trunk(path):
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{TRUNK}:{path}'],
                          capture_output=True, text=True, check=True).stdout


def at_pre_cursor(path):
    """The bytes a file had before Cursor became a native host.

    The Cursor adapter allowance measures what the third host costs, so its
    baseline has to be the revision before the Cursor work landed. Measuring
    against `origin/main` breaks the moment that branch carries the Cursor
    commit: the growth collapses to zero while the always-loaded content has
    not shrunk, and the bound fails on a release that changed no adapter.
    """
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{PRE_CURSOR}:{path}'],
                          capture_output=True, text=True, check=True).stdout


class ContextDisclosure(unittest.TestCase):
    def issue_110_guidance_bytes(self):
        trunk = issue_110_guidance(at_trunk, trunk_host_guidance)
        head = issue_110_guidance(lambda path: (ROOT / path).read_text(),
                                  lambda host: check_core.section(host, 'Cursor-only features'))
        host = 'plugin/adapters/host.md'
        self.assertEqual(head.pop(host) - trunk[host], CURSOR_ONLY_SECTION_GROWTH_OVER_TRUNK)
        self.assertEqual(head, {path: size for path, size in trunk.items() if path != host})
        for (path, size), limit in zip(trunk.items(), [1300, 550, 500, 750, 900, 15, 15]):
            self.assertLessEqual(size, limit, path)
        return trunk

    def test_initial_adapters_do_not_eagerly_load_unrelated_phase_guidance(self):
        host = (ROOT / 'plugin/adapters/host.md').read_text()
        mobile = (ROOT / 'plugin/adapters/mobile.md').read_text()
        native_row = next(line for line in host.splitlines(keepends=True)
                          if '[Native execution](native-execution.md)' in line)
        scope = 'Plain JVM or server Gradle projects stay out of scope.\n\n'
        self.assertIn(scope, host)
        native_growth = len((native_row + scope).encode())
        self.assertLessEqual(native_growth, 240)
        self.assertIn('\nRead this file once per session, and again after compaction.', host)
        self.assertIn('Apply this adapter and [mobile applicability](mobile.md#applicability) before the canonical workflow.', host)
        workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        with self.subTest('the door runs a test before the first dispatch'):
            self.assertTrue(check_core.DOOR.startswith('Before your first dispatch, run `printenv ORCA_TERMINAL_HANDLE ORCA_PANE_KEY ORCA_TAB_ID`;'))
            for test in ['if it prints a value', '`t3-code` tools are listed', 'the agent is omp']:
                self.assertIn(test, check_core.DOOR)
            self.assertTrue(workers.startswith('## Native workers and role models\n\n' + check_core.DOOR + '\n\n'))
        with self.subTest('a session that meets no door test reads nothing under hosts/'):
            hosts = ROOT / 'plugin/adapters/hosts'
            references = [(path.relative_to(ROOT).as_posix(), line)
                          for path in sorted((ROOT / 'plugin').rglob('*.md')) if hosts not in path.parents
                          for line in path.read_text().splitlines() if 'hosts/' in line]
            # The Orca door stays the only dispatch-time door in the workers adapter. The
            # Cursor page is a host door: host.md names it for a Cursor session, and the
            # workers adapter names it for the Cursor agent and field meanings. A session
            # on another host reads the line and nothing under hosts/.
            self.assertEqual([path for path, _ in references],
                             ['plugin/adapters/host-workers.md',
                              'plugin/adapters/host-workers.md',
                              'plugin/adapters/host-workers.md',
                              'plugin/adapters/host.md'])
            self.assertEqual([line for path, line in references if path == 'plugin/adapters/host-workers.md'],
                             [check_core.DOOR,
                              'takes the role instructions of `agents/hugues-agent.md`. In Cursor, read [hosts/cursor.md](hosts/cursor.md) for the agent registration.',
                              'In Cursor, read [hosts/cursor.md](hosts/cursor.md) for the field meanings.'])
            self.assertEqual([line for path, line in references if path == 'plugin/adapters/host.md'],
                             ['In Cursor, read [hosts/cursor.md](hosts/cursor.md) before the first tool call.'])
            measured = measure_context.measure(ROOT)
            for name, profile in measured['scenarios'].items():
                self.assertEqual([p for p in profile['candidate']['paths'] if '/hosts/' in p], [], name)
        with self.subTest('the opener and the phase reference reread rule agree with the skills'):
            self.assertIn('Retain loaded guidance and reread after compaction when needed.', host)
            self.assertIn('A skill\'s "read the host contract" is that read.', host)
        translated_guidance = self.issue_110_guidance_bytes()['plugin/adapters/host.md']
        # The always-loaded adapters' budget. It was 6000 when the guidance was
        # deferred, and the Cursor host moved it to 6100: a third host costs the
        # door sentence that points a Cursor session at its page (78 bytes) plus
        # the 8 bytes that name it in the adapter title. The restored trunk text
        # is the other half of the move, and the review that asked for it
        # required that restoration verbatim. The budget is a project-set
        # context budget, not a host limit, and it has moved before.
        self.assertLess(len(host.encode()) + len(mobile.encode()) - native_growth - translated_guidance, 6100)
        # The native-only set is named once, in host.md itself: hugues-mode and
        # setup-hstack are reached only by native invocation, with denials respected, and
        # a file read is no substitute. The user-only read is stated once too, beside the tier.
        self.assertEqual(host.count("only through the host's supported native mechanism"), 1)
        self.assertIn('Reach `setup-hstack` and each consumer or external skill', host)
        self.assertIn('owner-disabled entries and native denials', host)
        self.assertIn('never use a file read as an invocation fallback', host)
        self.assertIn("reads its SKILL.md in full as the scoped bundled reference, with the host's own", host)
        self.assertIn('never read a skill body', host)
        # The two halves of the user-only read, each stated once and only in host.md: a native
        # denial does not stop the read, and "invocation stops the step" is scoped to the
        # native-only skills. A fresh worker's read covers user-only skills, never the
        # native-only two.
        self.assertEqual(host.count("A native denial on such a skill does not stop the host's file read"), 1)
        self.assertEqual(host.count('For a native-only skill, unavailable, disabled, denied or unknown invocation stops'), 1)
        self.assertNotIn('\nUnavailable, disabled, denied or unknown invocation stops', host)
        self.assertIn('A fresh worker reads any bundled user-only skill itself.', host)
        self.assertNotIn('reads any bundled skill', host)
        tools = (ROOT / 'plugin/adapters/host-tools.md').read_text()
        self.assertNotIn('native denial', tools)
        self.assertNotIn('enabling or disabling the plugin', tools)
        self.assertIn('the reach and denial rules are in [host.md](host.md)', tools)
        self.assertNotIn('supersedes the native-only', host)
        self.assertNotIn('The native-only rule above governs', host)
        self.assertIn('never restart task routing', host)
        self.assertIn('No translation grants new authority', host)
        self.assertIn('For all other work, follow the pinned core unchanged', mobile)

    def test_adapter_partition_preserves_every_original_rule(self):
        baseline, _ = measure_context.native_baseline(ROOT)
        receipt = json.loads((ROOT / 'docs/ADAPTER-DISCLOSURE.json').read_text())
        paragraphs = baseline[receipt['host_source']].strip().split('\n\n')
        restored = {}
        replaced = []
        for row in receipt['host_fragments']:
            fragment = paragraphs[row['paragraph']]
            if row['slice']:
                fragment = fragment[slice(*row['slice'])].rstrip()
            self.assertEqual(hashlib.sha256(fragment.encode()).hexdigest(), row['sha256'])
            destination_text = (ROOT / row['destination']).read_text()
            disposition = row.get('disposition', 'original')
            if disposition == 'original':
                self.assertEqual(destination_text.count(fragment), 1)
            elif disposition == 'replaced':
                # An intentional edit: the receipt still pins the original baseline fragment's
                # hash (so drift in what was replaced is caught), but the destination now carries
                # the recorded replacement text instead of the original wording verbatim.
                self.assertTrue(row.get('reason'), 'a replaced fragment needs a reason')
                self.assertEqual(destination_text.count(row['replacement']), 1)
                self.assertEqual(destination_text.count(fragment), 0)
                replaced.append(fragment)
            elif disposition == 'removed':
                # An intentional deletion: the receipt pins the original fragment's hash and the
                # reason, and the destination no longer carries it.
                self.assertTrue(row.get('reason'), 'a removed fragment needs a reason')
                self.assertNotIn('replacement', row)
                self.assertEqual(destination_text.count(fragment), 0)
                replaced.append(fragment)
            else:
                self.fail('unknown disposition: ' + disposition)
            restored.setdefault(row['paragraph'], []).append(fragment)
        self.assertEqual(set(restored), set(range(len(paragraphs))))
        with self.subTest('the baseline Git translation sentence keeps its Git mapping'):
            rows = [row for row in receipt['host_fragments']
                    if 'filesystem and Git operations' in paragraphs[row['paragraph']][slice(*(row['slice'] or [None]))]]
            self.assertEqual(len(rows), 1)
            self.assertIn('filesystem and Git to host tools', (ROOT / rows[0]['destination']).read_text())
        for index, pieces in restored.items():
            self.assertEqual(' '.join(' '.join(pieces).split()), ' '.join(paragraphs[index].split()))
        # The blanket pre-fix sentences are gone from the live adapter, not merely shadowed by a
        # later paragraph: a model-invocable-only reading of host.md no longer contradicts the
        # scoped bundled-reference rule.
        host_text = (ROOT / 'plugin/adapters/host.md').read_text()
        for fragment in replaced:
            self.assertNotIn(fragment, host_text)
        self.assertNotIn('Invoke each bundled, consumer or external skill', host_text)
        self.assertNotIn('This contract overrides inherited raw sibling-read wording.', host_text)
        # mobile_sha256 pins the baseline file; the destination is that baseline with every
        # recorded replacement applied and nothing else changed.
        original_mobile = baseline[receipt['mobile_source']]
        self.assertEqual(hashlib.sha256(original_mobile.encode()).hexdigest(), receipt['mobile_sha256'])
        expected_mobile, cursor = [], 0
        for row in receipt['mobile_fragments']:
            start, end = row['slice']
            fragment = original_mobile[start:end]
            self.assertGreaterEqual(start, cursor)
            self.assertEqual(hashlib.sha256(fragment.encode()).hexdigest(), row['sha256'])
            self.assertEqual(row['disposition'], 'replaced')
            self.assertTrue(row.get('reason'), 'a replaced fragment needs a reason')
            expected_mobile += [original_mobile[cursor:start], row['replacement']]
            cursor = end
        expected_mobile.append(original_mobile[cursor:])
        mobile = (ROOT / receipt['mobile_destination']).read_bytes()
        self.assertEqual(mobile, ''.join(expected_mobile).encode())
        self.assertNotIn(b'native invocation for skills', mobile)

    def adapter_texts(self):
        return {p: (ROOT / p).read_text() for p in
                [*check_core.ADAPTERS, *check_core.ADAPTER_RESOURCES]}

    def test_each_phase_reference_is_a_required_prerequisite(self):
        original = self.adapter_texts()
        self.assertEqual(check_core.adapter_errors(original), [])
        for name in check_core.PHASE_GUIDANCE:
            with self.subTest(name=name):
                changed = dict(original)
                changed[check_core.ADAPTERS[0]] = changed[check_core.ADAPTERS[0]].replace('(' + name + ')', '(missing.md)')
                self.assertTrue(check_core.adapter_errors(changed))
        workers = 'plugin/adapters/host-workers.md'
        for old in ['(hosts/README.md)', '`printenv ORCA_TERMINAL_HANDLE ORCA_PANE_KEY ORCA_TAB_ID`']:
            with self.subTest(door=old):
                changed = dict(original)
                changed[workers] = changed[workers].replace(old, '(missing.md)')
                self.assertEqual(check_core.adapter_errors(changed), ['missing door: hosts/README.md'])

    def test_mobile_and_worker_rules_cannot_disappear_after_deferral(self):
        original = self.adapter_texts()
        for name, marker in [('plugin/adapters/mobile.md', '[mobile workflows](mobile-workflows.md) in full'),
                             ('plugin/adapters/mobile-workflows.md', 'separate\nfresh production worker'),
                             ('plugin/adapters/host-workers.md', 'List length sets'),
                             ('plugin/adapters/host.md', 'Reach `setup-hstack` and each consumer or external skill'),
                             ('plugin/adapters/host.md', "only through the host's supported native mechanism")]:
            with self.subTest(name=name):
                changed = dict(original)
                self.assertIn(marker, changed[name])
                changed[name] = changed[name].replace(marker, 'omitted')
                self.assertTrue(check_core.adapter_errors(changed))

    def test_scenarios_count_required_dependencies_and_expose_unknown_totals(self):
        scenarios = measure_context.measure(ROOT)['scenarios']
        expected = {
            'initial_mode_routing': ['plugin/skills/unslop/SKILL.md',
                                    'plugin/skills/hugues-mode/playbooks/bug-fix.md'],
            'bug_fix': ['plugin/skills/control-cli/SKILL.md', 'plugin/skills/tdd/SKILL.md', 'plugin/skills/why/references/epistemics.md',
                        'plugin/skills/why/references/sources/code-archaeology.md',
                        'plugin/agents/hugues-comment-sicko.md', 'plugin/adapters/host-workers.md',
                        'plugin/skills/principle-subtract-before-you-add/SKILL.md'],
            'larger_feature': ['plugin/skills/control-cli/SKILL.md', 'plugin/skills/architect/references/design-red-flags.md',
                               'plugin/skills/arena/SKILL.md', 'plugin/skills/swarm/SKILL.md',
                               'plugin/skills/typescript-best-practices/references/patterns.md',
                               'plugin/adapters/host-typescript.md',
                               'plugin/skills/principle-subtract-before-you-add/SKILL.md'],
        }
        for name, paths in expected.items():
            profile = scenarios[name]
            self.assertTrue(set(paths) <= set(profile['candidate']['paths']))
            self.assertIsNone(profile['complete_execution_tokens'])
            self.assertTrue(profile['unknown_inputs'])
            self.assertNotIn('plugin/adapters/mobile-workflows.md', profile['candidate']['paths'])
        self.assertEqual(scenarios['bug_fix']['fresh_mode_worker_floor']['candidate']['mode_workers'], 1)
        self.assertEqual(scenarios['larger_feature']['fresh_mode_worker_floor']['candidate']['mode_workers'], 8)

    def cursor_adapter_growth(self, adapters=None):
        """The bytes the adapters add over the trunk hStack inherited.

        Measured from the adapters' own bytes against the revision before
        Cursor landed, so the figure is exactly the Cursor host's cost: the
        door sentence that points a Cursor session at its page, the 8 bytes
        that name it in the adapter title, the Cursor sentence in the tools
        adapter and the two page doors in the workers adapter. The trunk text
        the review asked to restore is not part of this figure, because it is
        not the Cursor host's cost.
        """
        if adapters is None:
            adapters = ['plugin/adapters/host.md', 'plugin/adapters/mobile.md',
                        'plugin/adapters/host-workers.md', 'plugin/adapters/host-workflow-tools.md']
        growth = 0
        for path in adapters:
            inherited = at_pre_cursor(path)
            growth += len((ROOT / path).read_bytes()) - len(inherited.encode())
        return growth

    def test_source_budgets_recompute_and_bound_unchanged_bodies(self):
        measured = measure_context.measure(ROOT)
        self.assertEqual(measured, json.loads((ROOT / 'docs/CONTEXT-BUDGET.json').read_text()))
        # Restoring pstack's router design puts the inherited manual-only line back on 44 more
        # skill bodies, matching most of the pre-restoration baseline again. PR 1 fix round 1's
        # reworded host-contract marker (now scoped to the bundled-reference rule rather than a
        # blanket override) touches the same sentence in all 26 non-principle bodies, 24 of which
        # were otherwise unchanged; the other two (hugues-mode, setup-hstack) already
        # differed. architect, arena, how, interrogate, reflect, swarm and why also still carry
        # the separate tiered-model-role wiring change. 50 - 26 = 24 bodies were byte-identical
        # to the pre-restoration baseline (the 24 principle-* skills, which never carried that
        # marker). The pstack 0.15.25 merge then ported upstream's rewrites of 14 of those 24
        # principle bodies, so 10 remained identical. The four skills it added (hugues-help,
        # in-your-own-words, ketchup, sharpen) have no baseline body and are not compared. The
        # pstack 0.15.32 merge ported upstream's rewrites of three more of those 10, leaving 7;
        # its four new skills have no baseline body either. The list is recomputed here from the
        # files, so only principle-* bodies can be counted.
        baseline, _ = measure_context.native_baseline(ROOT)
        baseline = measure_context.current_names(baseline)
        identical = sorted(p for p in baseline if p.startswith('plugin/skills/') and p.endswith('/SKILL.md')
                           and baseline[p] == (ROOT / p).read_text())
        self.assertEqual(len(identical), 7)
        self.assertTrue(all(p.startswith('plugin/skills/principle-') for p in identical))
        self.assertEqual(measured['canonical_skill_bodies']['unchanged_files'], len(identical))
        self.assertLess(measured['native_frontmatter']['candidate_original_skills']['bytes'],
                        measured['native_frontmatter']['native_before']['bytes'])
        host = (ROOT / 'plugin/adapters/host.md').read_text()
        native_row = next(line for line in host.splitlines(keepends=True)
                          if '[Native execution](native-execution.md)' in line)
        scope = 'Plain JVM or server Gradle projects stay out of scope.\n\n'
        self.assertIn(scope, host)
        native_growth = len((native_row + scope).encode())
        self.assertLessEqual(native_growth, 240)
        mode = (ROOT / 'plugin/skills/hugues-mode/SKILL.md').read_text()
        brief = mode.split('## Subagents\n\n', 1)[1].split('\n\n', 1)[0] + '\n\n'
        self.assertIn('absolute installed baseline paths', brief)
        brief_growth = len(brief.encode())
        self.assertLessEqual(brief_growth, 560)
        required_growth = native_growth + brief_growth
        issue_110 = self.issue_110_guidance_bytes()
        # The bound is on hStack-authored growth. A file whose bytes equal its pinned upstream
        # source grows only when pstack does, so the last re-pin's growth in those files is
        # allowed (0.15.32 rewrote two principles that bug_fix reads).
        receipt = json.loads((ROOT / 'docs/upstream/consolidation.json').read_text())
        verbatim = {r['destination']: r['source'] for r in receipt['files']
                    if r['destination'] and r['destination_sha256'] == r['source_sha256']}

        def sizes(pin):
            pin = json.loads((ROOT / 'docs/upstream' / pin).read_text())
            snapshot = json.loads((ROOT / 'docs/upstream' / pin['snapshot']).read_text())
            return {f['path']: f['size'] for f in snapshot['files']}
        pinned, previous = sizes('pin.json'), sizes('baseline-pin.json')
        for name in ['initial_mode_routing', 'bug_fix']:
            profile = measured['scenarios'][name]
            guidance = sum(size for path, size in issue_110.items() if path in profile['candidate']['paths'])
            upstream_growth = sum(pinned[verbatim[path]] - previous.get(verbatim[path], 0)
                                  for path in profile['candidate']['paths'] if path in verbatim)
            self.assertLess(profile['candidate']['bytes'] - required_growth - guidance - upstream_growth,
                            profile['native_before']['bytes'])
        selection_row = next(line for line in host.splitlines(keepends=True)
                             if '[Mobile language scope](host-mobile-languages.md)' in line)
        selection_growth = len(selection_row.encode())
        self.assertLessEqual(selection_growth, 128)
        # Cursor is the third host, so the adapters name it and point a Cursor
        # session at its page. That is the whole hStack-authored growth the
        # bound has to absorb on top of the trunk guidance, and it is measured
        # from the adapters' own diff against trunk rather than guessed.
        cursor_adapter_growth = self.cursor_adapter_growth()
        self.assertLessEqual(cursor_adapter_growth, 400)
        feature = measured['scenarios']['larger_feature']
        feature_guidance = sum(size for path, size in issue_110.items() if path in feature['candidate']['paths'])
        self.assertLessEqual(feature['candidate']['bytes'],
                             feature['native_before']['bytes'] + selection_growth + required_growth
                             + feature_guidance + cursor_adapter_growth)
        routing = measured['scenarios']['initial_mode_routing']
        routing_guidance = sum(size for path, size in issue_110.items() if path in routing['candidate']['paths'])
        self.assertLess(routing['candidate']['bytes'] - routing_guidance, routing['native_before']['bytes'] * .8)

    def test_skill_list_budget_is_at_most_2500_characters(self):
        measured = measure_context.measure(ROOT)
        skill_list = measured['skill_list']
        self.assertLessEqual(skill_list['candidate']['characters'], 2500)
        self.assertEqual(skill_list['candidate']['model_invocable_skills'], 1)
        self.assertEqual(set(skill_list['candidate']['paths']), {'plugin/skills/setup-hstack/SKILL.md'})
        # No hardcoded baseline here: native_before is recomputed, by the same function, over
        # the same pinned CONTEXT-BASELINE.json bytes every other measurement in this module
        # already compares against (measured['native_before_revision'] names the exact
        # revision). Recompute it independently of measure_context.skill_list_metrics itself,
        # so this proves the counting rule, not just the wiring.
        baseline, _ = measure_context.native_baseline(ROOT)
        baseline = measure_context.current_names(baseline)
        declaration_paths = sorted(p for p in baseline
                                   if p.startswith('plugin/skills/') and p.endswith('/SKILL.md'))
        expected_invocable = [p for p in declaration_paths
                              if not check_core.native_frontmatter(baseline[p])['disable-model-invocation']]
        self.assertEqual(skill_list['native_before']['model_invocable_skills'], len(expected_invocable))
        self.assertEqual(set(skill_list['native_before']['paths']), set(expected_invocable))
        expected_characters = sum(len(measure_context.description_text(
            check_core.native_frontmatter(baseline[p])['description'])) for p in expected_invocable)
        self.assertEqual(skill_list['native_before']['characters'], expected_characters)
        # native_before (7db3e80) predates the 0.2.0-to-46-skill flip this PR undoes, so it
        # is 1 skill, not a pre-PR comparison point. pre_pr_main (a67df90, where this
        # restoration branched from, and the exact revision the Issue's Problem Statement
        # measures) is the real one: recomputed here too, from its own minimal fixture
        # (just the 50 SKILL.md frontmatter blocks), by the same unmodified function.
        self.assertEqual(measured['pre_pr_main_revision'], 'a67df901162cc2add4aabb9e2a3843134696c490')
        pre_pr_main, _ = measure_context.pre_pr_main_baseline(ROOT)
        pre_pr_main = measure_context.current_names(pre_pr_main)
        pre_pr_paths = sorted(pre_pr_main)
        self.assertEqual(len(pre_pr_paths), 50)
        pre_pr_invocable = [p for p in pre_pr_paths
                           if not check_core.native_frontmatter(pre_pr_main[p])['disable-model-invocation']]
        self.assertEqual(skill_list['pre_pr_main']['model_invocable_skills'], len(pre_pr_invocable))
        self.assertEqual(skill_list['pre_pr_main']['model_invocable_skills'], 46)
        self.assertEqual(set(skill_list['pre_pr_main']['paths']), set(pre_pr_invocable))
        pre_pr_characters = sum(len(measure_context.description_text(
            check_core.native_frontmatter(pre_pr_main[p])['description'])) for p in pre_pr_invocable)
        self.assertEqual(skill_list['pre_pr_main']['characters'], pre_pr_characters)
        # Close to, but not forced to equal, the owner's informally recorded 9,869: that
        # figure was "recorded rather than recomputed from pinned bytes" (NATIVE-CONSOLIDATION.md).
        # This is the first reproducible, hash-pinned recomputation of the Issue's own baseline.
        self.assertGreater(skill_list['pre_pr_main']['characters'], 9500)

    def test_pre_pr_main_baseline_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='pre-pr-baseline-') as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            receipt = ROOT / 'docs/CONTEXT-BASELINE-PRE-PR.json'
            shutil.copyfile(receipt, root / 'docs/CONTEXT-BASELINE-PRE-PR.json')
            name = json.loads(receipt.read_text())['archive']
            (root / name).parent.mkdir(parents=True)
            (root / name).write_bytes((ROOT / name).read_bytes() + b'drift')
            with self.assertRaisesRegex(ValueError, 'pre-PR baseline archive drift'):
                measure_context.pre_pr_main_baseline(root)

    def test_router_initial_read_set_is_smaller_than_main(self):
        # `main` is a67df90: the fixture pins its router body and both unconditional adapters.
        # The candidate side is recomputed here from the files, not read back from the record.
        measured = measure_context.measure(ROOT)
        read_set = measured['mode_initial_read_set']
        main, revision = measure_context.pre_pr_main_mode_read_set(ROOT)
        self.assertEqual(revision, 'a67df901162cc2add4aabb9e2a3843134696c490')
        self.assertEqual(set(main), set(read_set['candidate_paths']))
        candidate = sum((ROOT / path).stat().st_size for path in read_set['candidate_paths'])
        before = sum(len(text.encode()) for text in main.values())
        self.assertEqual(read_set['candidate']['bytes'], candidate)
        self.assertEqual(read_set['pre_pr_main']['bytes'], before)
        guidance = sum(size for path, size in self.issue_110_guidance_bytes().items()
                       if path in read_set['candidate_paths'])
        # The router's initial read set carries the always-loaded adapters, so
        # it moves with them: the Cursor door sentence and the title that names
        # the third host. The bound absorbs that growth explicitly rather than
        # leaving it to the guidance allowance, which is anchored to older
        # frozen revisions that predate both.
        router_growth = self.cursor_adapter_growth(['plugin/adapters/host.md',
                                                    'plugin/adapters/mobile.md'])
        self.assertLess(candidate - guidance - router_growth, before + 15)
        router = 'plugin/skills/hugues-mode/SKILL.md'
        self.assertLess((ROOT / router).stat().st_size, len(main[router].encode()))

    def test_pre_pr_mode_read_set_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='pre-pr-mode-read-set-') as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            receipt = ROOT / 'docs/CONTEXT-BASELINE-PRE-PR.json'
            shutil.copyfile(receipt, root / 'docs/CONTEXT-BASELINE-PRE-PR.json')
            name = json.loads(receipt.read_text())['mode_read_set']['archive']
            (root / name).parent.mkdir(parents=True)
            (root / name).write_bytes((ROOT / name).read_bytes() + b'drift')
            with self.assertRaisesRegex(ValueError, 'pre-PR mode read set archive drift'):
                measure_context.pre_pr_main_mode_read_set(root)

    def test_skill_list_description_excludes_yaml_quoting(self):
        # A host that YAML-parses the frontmatter never sees the surrounding quote
        # characters themselves; the measured character count must not either.
        self.assertEqual(measure_context.description_text('Plain, unquoted text.'), 'Plain, unquoted text.')
        self.assertEqual(measure_context.description_text('"Quoted, with an escaped \\" mark."'),
                         'Quoted, with an escaped " mark.')
        self.assertEqual(measure_context.description_text("'Single-quoted, with a doubled '' mark.'"),
                         "Single-quoted, with a doubled ' mark.")

    def test_context_baseline_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='context-baseline-') as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            receipt = ROOT / 'docs/CONTEXT-BASELINE.json'
            shutil.copyfile(receipt, root / 'docs/CONTEXT-BASELINE.json')
            name = json.loads(receipt.read_text())['archive']
            (root / name).parent.mkdir(parents=True)
            (root / name).write_bytes((ROOT / name).read_bytes() + b'drift')
            with self.assertRaisesRegex(ValueError, 'baseline archive drift'):
                measure_context.native_baseline(root)


class InstalledPhaseGuidance(InstalledFixture, unittest.TestCase):
    def test_native_project_skill_paths_cover_discovery_updates_and_feature_maps(self):
        result = self.bound('read-workflow', 'adapters/host-special-skills.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        body = ' '.join(result.stdout.split())
        for required in (
            "consumer's existing supported layout",
            '`.claude/skills` on Claude Code and `.agents/skills` on Codex',
            'Preserve categories and user edits',
            'Updates keep the exact existing skill target',
            "automate-me's recursive mode discovery and categorized output",
            "create-verification-skill's generated `verify-<app>/SKILL.md`",
            '`features/README.md` plus its feature files',
            "maintain-verification-skill's target lookup",
            'multiple-candidate and missing-target gates',
            'Personal/global placement or configuration needs explicit scope',
            "Reflect's divergent, tooling and judgment reviewers",
            'A path on disk alone is not evidence of use',
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_native_agent_store_preserves_existing_programs_and_helper_arguments(self):
        result = self.bound('read-workflow', 'adapters/host-workflow-tools.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        body = ' '.join(result.stdout.split())
        for required in (
            "operator-named directory or the existing program's recorded directory",
            'explicit `--store` or `ORCH_STORE` binding',
            'existing flag/environment precedence',
            '`~/hstack-evidence/<date>-<task>/`',
            'Resolve that choice once to an absolute path',
            'Resume the recorded store rather than creating a new dated directory',
            'plans under `docs/`, programs under `orchestrate/<project-slug>/`',
            'Explicit plan and log targets still win',
            'preserving a bound program path without appending another program subdirectory',
            'complete log-file path to `log.sh`',
            'Keep all state outside the installed plugin',
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_codex_sandbox_guidance_preserves_the_store_and_direct_commands(self):
        result = self.bound('read-workflow', 'adapters/host-workflow-tools.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        body = ' '.join(check_core.section(result.stdout, 'Codex sandbox').split())
        for required in [
                'codex --add-dir <evidence store> --add-dir <worktree root>',
                "chief's 2026-10-20 observation", 'sandbox still on',
                'Otherwise request per-command escalation.',
                '`adb`', '`xcrun simctl`', 'CoreSimulator', 'Gradle wrapper',
                '`swift build` / `swift test`', 'ModuleCache', '`git` index writes in a linked worktree',
                'A `/tmp` fallback is allowed only when the final message names it.',
                'Run commands directly. Never use a wrapper script that runs arbitrary arguments.']:
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_deferred_guidance_is_readable_and_integrity_bound(self):
        for relative in check_core.ADAPTER_RESOURCES:
            name = relative.removeprefix('plugin/')
            with self.subTest(name=name):
                result = self.bound('read-workflow', name)
                self.assertEqual(result.returncode, 0, result.stderr)
                path = self.plugin / name
                original = path.read_bytes()
                self.assertEqual(result.stdout, original.decode())
                path.write_bytes(original + b'\ndrift\n')
                self.assertEqual(self.bound('read-workflow', name).returncode, 2)
                path.write_bytes(original)
