from pathlib import Path
import shutil
import textwrap
import unittest
ROOT = Path(__file__).resolve().parents[1]
class NativeLayout(unittest.TestCase):
    def test_native_entry_owns_architect_phases_without_runtime_core(self):
        body = (ROOT / 'plugin/skills/architect/SKILL.md').read_text()
        self.assertIn('## Phase A: Ground the problem', body)
        self.assertIn('## Phase E: Scrap when the architecture is wrong', body)
        self.assertFalse((ROOT / 'plugin/core').exists())

    def test_every_reader_of_the_models_file_says_what_to_do_with_the_legacy_file(self):
        # 0.4.0 moved the project model file from `.huguesstack/` to `.hstack/`. A project that
        # has not moved it keeps its roles only if each reader says what to do when the new file
        # is absent: read the legacy file and tell the user to move it.
        legacy = ('If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, '
                  'read the legacy file and tell the user to move it.')
        readers = {p.relative_to(ROOT / 'plugin').as_posix() for p in (ROOT / 'plugin').rglob('*.md')
                   if '.hstack/models.md' in p.read_text()}
        self.assertTrue({'adapters/host-workers.md', 'skills/setup-hstack/SKILL.md', 'skills/hugues-help/SKILL.md',
                         'skills/architect/SKILL.md', 'skills/arena/SKILL.md', 'skills/how/SKILL.md',
                         'skills/interrogate/SKILL.md', 'skills/reflect/SKILL.md', 'skills/swarm/SKILL.md',
                         'skills/why/SKILL.md'} <= readers, sorted(readers))
        for name in sorted(readers):
            text = (ROOT / 'plugin' / name).read_text()
            self.assertIn(legacy, ' '.join(text.split()), name)

    def test_setup_writes_only_the_new_models_folder(self):
        setup = ' '.join((ROOT / 'plugin/skills/setup-hstack/SKILL.md').read_text().split())
        self.assertIn('Write `.hstack/models.md`', setup)
        self.assertIn('Setup writes only `.hstack/`; it never writes or deletes `.huguesstack/`.', setup)
        self.assertIsNone(re.search(r'[Ww]rite `\.huguesstack', setup))

from test_host_adapters import InstalledFixture
class NativeInstalled(InstalledFixture, unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node unavailable; plan gate unrun')
    def test_translated_plan_without_consumer_git_read_passes_bound_gate(self):
        plan = self.consumer / 'plan with spaces.md'
        plan.write_text((ROOT / 'tests/fixtures/adapter-plan.md').read_text().replace(
            '`git show origin/main:PLAN.md`\n', ''))
        self.assertEqual(self.bound('plan-check', plan).returncode, 0)
        translated = self.bound('translate-plan', plan)
        self.assertEqual(translated.returncode, 0, translated.stderr)
        self.assertNotIn('git show origin/main:', translated.stdout)
        plan.write_text(translated.stdout)
        checked = self.bound('plan-check', plan)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        plan.write_text(translated.stdout.replace('read-workflow --binding', 'read-workflow'))
        rejected = self.bound('plan-check', plan)
        self.assertEqual(rejected.returncode, 1)
        self.assertIn('bound read-workflow', rejected.stderr)

    def test_installed_playbook_read_and_native_skill_boundary(self):
        result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Mandatory: no skip-with-reason escape', result.stdout)
        # The helper never reads a skill body. `swarm` is user-only, so an agent reads its
        # SKILL.md with the host's own file-read tool; `read-workflow` refuses it, through
        # its legacy pstack-relative alias too, exactly as it refuses a native-only skill.
        for path in ['skills/swarm/SKILL.md', 'pstack/skills/swarm/SKILL.md']:
            with self.subTest(path=path):
                denied = self.bound('read-workflow', path)
                self.assertEqual(denied.returncode, 2)
                self.assertEqual(denied.stdout, '')
                self.assertIn('native skill invocation', denied.stderr)

    def test_translate_does_not_bypass_native_skill_invocation(self):
        for text in ['`pstack/skills/swarm/SKILL.md`',
                     'cat skills/swarm/SKILL.md',
                     'git show origin/main:skills/swarm/SKILL.md']:
            with self.subTest(text=text):
                plan = self.consumer / 'plan.md'
                plan.write_text(text)
                result = self.bound('translate-plan', plan)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)

    def test_translate_still_refuses_an_unknown_skill_body(self):
        for text in ['`pstack/skills/nope/SKILL.md`', 'cat skills/nope/SKILL.md',
                     'git show origin/main:skills/nope/SKILL.md']:
            with self.subTest(text=text):
                plan = self.consumer / 'plan.md'
                plan.write_text(text)
                result = self.bound('translate-plan', plan)
                self.assertEqual(result.returncode, 2)
                self.assertIn('native skill invocation', result.stderr)

    def test_initial_binding_rejects_adapter_and_native_metadata_drift(self):
        for name in ['adapters/mobile.md', 'skills/swarm/agents/openai.yaml']:
            with self.subTest(name=name):
                path = self.plugin / name
                original = path.read_bytes()
                path.write_bytes(original + b'\nchanged\n')
                self.assertEqual(self.run_tool('bind').returncode, 2)
                path.write_bytes(original)

    def test_legacy_binding_is_not_silently_rebound(self):
        import json
        data = json.loads(self.binding.read_text())
        data['revision'] = 'e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a'
        self.binding.write_text(json.dumps(data))
        result = self.bound('read-workflow', 'skills/hugues-mode/playbooks/feature.md')
        self.assertEqual(result.returncode, 2)

    def test_initial_bind_rejects_trust_anchor_permission_drift(self):
        for name in ['adapters/host_tools.py', 'adapters/runtime/payload.py',
                     'adapters/runtime/payload.json']:
            with self.subTest(name=name):
                path = self.plugin / name
                mode = path.stat().st_mode & 0o777
                path.chmod(0o646)
                self.assertEqual(self.run_tool('bind').returncode, 2)
                path.chmod(mode)


import hashlib
import json
import re
import subprocess
import sys
import tempfile
sys.path.insert(0, str(ROOT / 'scripts'))
import check_core
import measure_context
import native_reach_corpus
import seal_payload


class NativeIntegrity(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='hstack-native-contract-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))

    def rejected(self):
        with self.assertRaises((ValueError, OSError, KeyError, TypeError)):
            check_core.check(self.root)

    def test_current_package_and_public_inventory(self):
        result = check_core.check(self.root)
        self.assertEqual(result['active_skills'], 63)
        self.assertEqual(result['upstream_archive_files'], 200)

    def test_missing_receipt_cannot_disable_integrity(self):
        (self.root / 'docs/upstream/consolidation.json').unlink()
        result = subprocess.run([sys.executable, str(self.root / 'scripts/check_plugin.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_extra_skill_cannot_become_a_second_canonical_declaration(self):
        folder = self.root / 'plugin/skills/extra'
        folder.mkdir()
        (folder / 'SKILL.md').write_text((self.root / 'plugin/skills/arena/SKILL.md').read_text())
        self.rejected()

    def test_removed_required_reference_is_rejected(self):
        (self.root / 'plugin/skills/architect/references/runner-prompt.md').unlink()
        self.rejected()

    def test_extra_file_is_rejected(self):
        (self.root / 'plugin/unapproved.md').write_text('unreviewed')
        self.rejected()

    def test_non_executable_permission_drift_is_rejected(self):
        (self.root / 'plugin/skills/arena/SKILL.md').chmod(0o600)
        self.rejected()

    def test_symlink_shadow_is_rejected(self):
        path = self.root / 'plugin/skills/arena/SKILL.md'
        path.unlink()
        path.symlink_to('../architect/SKILL.md')
        self.rejected()

    def test_corrupt_source_archive_is_rejected(self):
        path = self.root / 'provenance/upstream/pstack-0.15.32.tar.gz'
        path.write_bytes(path.read_bytes() + b'changed')
        self.rejected()

    def test_sealing_does_not_approve_lost_workflow_gates(self):
        path = self.root / 'plugin/skills/architect/SKILL.md'
        path.write_text(path.read_text().replace('at least two structurally distinct candidates', 'one candidate'))
        seal_payload.seal(self.root, accept=['plugin/skills/architect/SKILL.md'])
        self.rejected()

    def test_sealing_does_not_approve_lost_invocation_boundary(self):
        path = self.root / 'plugin/skills/architect/SKILL.md'
        self.assertIn('The host contract governs how this skill reaches any sibling dependency.', path.read_text())
        path.write_text(path.read_text().replace('The host contract governs how this skill reaches any sibling dependency.', 'read any skill body'))
        seal_payload.seal(self.root, accept=['plugin/skills/architect/SKILL.md'])
        self.rejected()

    def test_bundled_cursor_skills_keep_pinned_sources_and_notices(self):
        receipt = json.loads((self.root / 'docs/upstream/consolidation.json').read_text())
        self.assertEqual(set(receipt['external_skills']), {'control-cli', 'control-ui', 'deslop'})
        self.assertEqual(receipt['external_skills'], check_core.EXTERNAL_SKILLS)
        for name, row in check_core.EXTERNAL_SKILLS.items():
            with self.subTest(skill=name):
                self.assertEqual(row['repository'], 'https://github.com/cursor/plugins')
                self.assertEqual(row['license_holder'], 'Copyright (c) 2026 Cursor')
                self.assertEqual([r['source'] for r in receipt['files'] if f'/{name}/' in r['source']], [])
                source = (self.root / row['source_copy']).read_bytes()
                installed = (self.root / row['destination']).read_bytes()
                self.assertEqual(hashlib.sha256(source).hexdigest(), row['source_sha256'])
                self.assertTrue(check_core.native_frontmatter(installed.decode())['disable-model-invocation'])
                self.assertIn(name, check_core.USER_ONLY)
                self.assertEqual((self.root / row['license_copy']).read_bytes(),
                                 (self.root / row['license_destination']).read_bytes())
                self.assertIn(b'Copyright (c) 2026 Cursor', (self.root / row['license_destination']).read_bytes())

    def test_bundled_cursor_skill_bodies_are_editable_but_sources_and_contracts_are_not(self):
        receipt = self.root / 'docs/upstream/consolidation.json'
        for name, row in check_core.EXTERNAL_SKILLS.items():
            skill = self.root / row['destination']
            yaml = skill.parent / 'agents/openai.yaml'
            source = self.root / row['source_copy']
            notice = self.root / row['license_destination']
            installed = skill.read_text()
            def edit_body():
                skill.write_text(installed + '\nChanged procedure.\n')
            def drop_host_contract():
                head, _, rest = installed.partition('## Host invocation contract\n\n')
                skill.write_text(head + rest.split('\n\n', 1)[1])
            def edit_source_copy():
                source.write_text(source.read_text() + '\nChanged procedure.\n')
                edit_body()
            def edit_license_copy():
                notice.write_text('MIT License\n')
            def drop_license_copy():
                notice.unlink()
            def make_model_invocable():
                skill.write_text(installed.replace('disable-model-invocation: true\n', ''))
                yaml.write_text('policy:\n  allow_implicit_invocation: true\n')
            def edit_receipt():
                data = json.loads(receipt.read_text())
                data['external_skills'][name]['revision'] = '0' * 40
                receipt.write_text(json.dumps(data))
            for change, mutate, accepted in [
                    ('body edit', edit_body, True), ('source copy edit', edit_source_copy, False),
                    ('license edit', edit_license_copy, False), ('license removed', drop_license_copy, False),
                    ('model-invocable', make_model_invocable, False), ('receipt edit', edit_receipt, False),
                    ('host contract removed', drop_host_contract, False)]:
                with self.subTest(skill=name, change=change):
                    kept = {p: p.read_bytes() for p in [skill, yaml, receipt, source, notice] if p.exists()}
                    mutate()
                    seal_payload.seal(self.root)
                    if accepted:
                        check_core.check(self.root)
                    else:
                        self.rejected()
                    for path, data in kept.items():
                        path.write_bytes(data)
                    seal_payload.seal(self.root)
                    check_core.check(self.root)

    def test_native_policy_mutation_is_rejected_even_after_sealing(self):
        path = self.root / 'plugin/skills/setup-hstack/agents/openai.yaml'
        path.write_text('policy:\n  allow_implicit_invocation: false\n')
        seal_payload.seal(self.root)
        self.rejected()

    def test_public_name_cannot_change_after_sealing(self):
        path = self.root / 'plugin/skills/hugues-mode/SKILL.md'
        path.write_text(path.read_text().replace('name: hugues-mode', 'name: poteto-mode'))
        seal_payload.seal(self.root, accept=['plugin/skills/hugues-mode/SKILL.md'])
        self.rejected()

    def test_role_prompt_mapping_cannot_change_after_sealing(self):
        path = self.root / 'docs/upstream/consolidation.json'
        data = json.loads(path.read_text())
        data['worker_roles']['reflect-tooling']['prompt'] = 'plugin/skills/reflect/references/judgment-reviewer.md'
        path.write_text(json.dumps(data))
        seal_payload.seal(self.root)
        self.rejected()

    def test_source_identity_cannot_be_swapped_by_resealing(self):
        path = self.root / 'docs/upstream/consolidation.json'
        data = json.loads(path.read_text())
        rows = {row['source']: row for row in data['files']}
        a, b = rows['pstack/skills/bro/SKILL.md'], rows['pstack/skills/benchmark-checklist/SKILL.md']
        a['destination'], b['destination'] = b['destination'], a['destination']
        path.write_text(json.dumps(data))
        seal_payload.seal(self.root, accept=['plugin/skills/bro/SKILL.md', 'plugin/skills/benchmark-checklist/SKILL.md'])
        self.rejected()

    def test_manual_only_cannot_be_removed_from_both_native_metadata_files(self):
        path = self.root / 'plugin/skills/reflect/SKILL.md'
        path.write_text(path.read_text().replace('disable-model-invocation: true\n', ''))
        (path.parent / 'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: true\n')
        seal_payload.seal(self.root, accept=['plugin/skills/reflect/SKILL.md'])
        self.rejected()

    def test_dependency_skill_cannot_become_manual_only(self):
        path = self.root / 'plugin/skills/setup-hstack/SKILL.md'
        path.write_text(path.read_text().replace('\n---\n', '\ndisable-model-invocation: true\n---\n', 1))
        (path.parent / 'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: false\n')
        seal_payload.seal(self.root, accept=['plugin/skills/setup-hstack/SKILL.md'])
        self.rejected()

    def test_verbatim_port_may_only_drop_the_inherited_manual_only_line(self):
        path = self.root / 'plugin/skills/principle-fix-root-causes/SKILL.md'
        path.write_text(path.read_text() + 'Extra rule.\n')
        seal_payload.seal(self.root, accept=['plugin/skills/principle-fix-root-causes/SKILL.md'])
        result = subprocess.run([sys.executable, str(self.root / 'scripts/upstream-diff.py'), 'check',
                                 '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('verbatim destination differs', result.stderr)

    def test_host_invocation_receipt_cannot_add_a_user_only_entry(self):
        path = self.root / 'docs/upstream/consolidation.json'
        data = json.loads(path.read_text())
        data['host_invocation']['user_only'] = sorted(data['host_invocation']['user_only'] + ['architect'])
        path.write_text(json.dumps(data))
        self.rejected()

    def test_manual_only_comment_cannot_override_effective_false(self):
        path = self.root / 'plugin/skills/reflect/SKILL.md'
        path.write_text(path.read_text().replace('disable-model-invocation: true\n',
            'disable-model-invocation: false\n# Previous setting: disable-model-invocation: true\n'))
        seal_payload.seal(self.root, accept=['plugin/skills/reflect/SKILL.md'])
        self.rejected()

    def test_duplicate_native_invocation_field_is_rejected(self):
        path = self.root / 'plugin/skills/reflect/SKILL.md'
        path.write_text(path.read_text().replace('disable-model-invocation: true\n',
            'disable-model-invocation: true\ndisable-model-invocation: false\n'))
        seal_payload.seal(self.root, accept=['plugin/skills/reflect/SKILL.md'])
        self.rejected()

    def test_seal_refuses_unaccepted_canonical_change_before_any_write(self):
        path = self.root / 'plugin/skills/hugues-mode/scripts/check-plan.mjs'
        path.write_text(path.read_text() + '\n// appended\n')
        receipt = (self.root / 'docs/upstream/consolidation.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'check-plan.mjs'):
            seal_payload.seal(self.root)
        self.assertEqual((self.root / 'docs/upstream/consolidation.json').read_bytes(), receipt)
        self.rejected()
        seal_payload.seal(self.root, accept=['plugin/skills/hugues-mode/scripts/check-plan.mjs'])
        self.rejected()

    def test_helper_input_receipt_cannot_go_stale(self):
        path = self.root / 'docs/HELPER-INPUTS.json'
        data = json.loads(path.read_text())
        row = next(r for r in data['files'] if r['installed'] and r['installed'].endswith('/bun.lock'))
        row['same_bytes_as_upstream'] = False
        path.write_text(json.dumps(data))
        self.rejected()

    def test_seal_rejects_escaping_destination_before_any_write(self):
        path = self.root / 'docs/upstream/consolidation.json'
        data = json.loads(path.read_text())
        data['files'][0]['destination'] = '../outside.md'
        path.write_text(json.dumps(data))
        before = {name: (self.root / 'plugin' / name).read_bytes() for name in seal_payload.ANCHORS}
        with self.assertRaises(ValueError):
            seal_payload.seal(self.root)
        self.assertEqual(before, {name: (self.root / 'plugin' / name).read_bytes() for name in before})

    def test_standalone_checker_and_seal_reject_ancestor_symlink(self):
        source = self.root / 'provenance/upstream'
        target = self.root / 'provenance/original'
        source.rename(target)
        source.symlink_to('original', target_is_directory=True)
        self.rejected()
        with self.assertRaises(ValueError):
            seal_payload.seal(self.root)

    def test_native_reach_lint_flags_every_reviewed_contradiction(self):
        # Root cause of PR 1 fix rounds 1 to 4: the rule for reaching a user-only skill was
        # restated across many files, so each round's review found another spelling of the
        # same contradiction. native_reach_corpus holds every spelling found so far. The lint
        # must flag each one however the line is wrapped, listed or embedded.
        def variants(text):
            flat = ' '.join(text.split())
            yield 'as written', text
            yield 'wrapped', textwrap.fill(flat, 36)
            yield 'wrapped inside hyphenated names', textwrap.fill(flat, 23)
            yield 'list item', '- ' + flat
            yield 'embedded in a paragraph', 'An unrelated opening sentence.\n\n' + text + '\n\nAn unrelated closing one.'
        self.assertGreaterEqual(len(native_reach_corpus.CONTRADICTIONS), 45)
        for label, text in native_reach_corpus.CONTRADICTIONS:
            for shape, variant in variants(text):
                with self.subTest(label=label, shape=shape):
                    self.assertTrue(check_core.native_reach_violations(variant))

    def test_native_reach_lint_rejects_a_reintroduced_contradiction_in_the_package(self):
        # The lint must run inside check(): reintroduce one contradiction, reseal so no
        # integrity check fires first, and the failure must come from the lint itself.
        path = self.root / 'plugin/adapters/host-special-skills.md'
        text = path.read_text()
        self.assertIn("by reading automate-me's SKILL.md in\nfull as the scoped bundled reference", text)
        path.write_text(text.replace("by reading automate-me's SKILL.md in\nfull as the scoped bundled reference",
                                     'through the native automate-me entry'))
        seal_payload.seal(self.root)
        with self.assertRaisesRegex(ValueError, 'promised native reach'):
            check_core.check(self.root)

    def test_native_reach_lint_is_quiet_on_correct_text_and_on_the_package(self):
        for label, text in native_reach_corpus.CLEAN:
            with self.subTest(label=label):
                self.assertEqual(check_core.native_reach_violations(text), [])
        self.assertEqual(check_core.native_reach_errors(self.root), [])
        # A skill may name itself, and frontmatter states a tier rather than an instruction.
        self.assertEqual(check_core.native_reach_violations('Invoke tdd natively.', own='tdd'), [])
        skill = self.root / 'plugin/skills/tdd/SKILL.md'
        skill.write_text(skill.read_text().replace('\n---\n', '\ninvoke swarm natively\n---\n', 1))
        self.assertEqual(check_core.native_reach_errors(self.root), [])
        skill.write_text(skill.read_text() + '\nInvoke swarm natively.\n')
        self.assertEqual(len(check_core.native_reach_errors(self.root)), 1)

    def test_native_reach_allowlist_is_one_live_reviewed_sentence(self):
        # The only exemption: the TypeScript route says `paths` auto-load is disabled. An entry
        # that no plugin file carries any more must be deleted, not left behind.
        self.assertEqual(len(check_core.NATIVE_REACH_ALLOWLIST), 1)
        carried = {clause for path in (self.root / 'plugin').rglob('*.md')
                   for clause in check_core.markdown_clauses(path.read_text())}
        self.assertEqual(check_core.NATIVE_REACH_ALLOWLIST - carried, set())

    def test_mode_principles_consultation_cannot_restart_routing(self):
        path = self.root / 'plugin/adapters/host.md'
        path.write_text(path.read_text().replace('never restart task routing', 'restart task routing'))
        seal_payload.seal(self.root)
        self.rejected()

    def test_measured_context_budget_is_current_and_bounded(self):
        import measure_context
        measured = measure_context.measure(self.root)
        self.assertEqual(json.loads((self.root / 'docs/CONTEXT-BUDGET.json').read_text()), measured)
        self.assertEqual(measured['public_skills'], 63)
        self.assertLessEqual(measured['mode_initial_read_set']['candidate']['bytes'], 38000)
        # An upper bound over every declared frontmatter block, user-only skills included. The
        # pstack 0.15.32 merge added four user-only skills, so the bound moved from 16000; the
        # per-turn skill list itself is bounded separately in test_context_disclosure.
        self.assertLessEqual(measured['native_frontmatter']['candidate']['bytes'], 18000)

    def test_context_inventory_lists_skills_added_after_the_release(self):
        # Skills added after 0.2.0 have no historical counterpart, so each is listed by name.
        # A new SKILL.md that is not listed, or a listed one that goes missing, still fails.
        self.assertEqual(sorted(measure_context.ADDED_AFTER_RELEASE),
                         ['plugin/skills/control-cli/SKILL.md', 'plugin/skills/control-ui/SKILL.md',
                          'plugin/skills/create-formal-verification-skill/SKILL.md',
                          'plugin/skills/deslop/SKILL.md', 'plugin/skills/hugues-help/SKILL.md',
                          'plugin/skills/in-your-own-words/SKILL.md', 'plugin/skills/ketchup-video/SKILL.md',
                          'plugin/skills/ketchup/SKILL.md', 'plugin/skills/kotlin-best-practices/SKILL.md',
                          'plugin/skills/maintain-formal-verification-skill/SKILL.md',
                          'plugin/skills/sharpen/SKILL.md', 'plugin/skills/statechart/SKILL.md',
                          'plugin/skills/swift-best-practices/SKILL.md'])
        unlisted = self.root / 'plugin/skills/unlisted/SKILL.md'
        unlisted.parent.mkdir()
        unlisted.write_text((self.root / 'plugin/skills/ketchup/SKILL.md').read_text())
        with self.subTest(change='unlisted new skill'):
            with self.assertRaisesRegex(ValueError, 'context declaration inventory changed'):
                measure_context.measure(self.root)
        shutil.rmtree(unlisted.parent)
        shutil.rmtree(self.root / 'plugin/skills/ketchup')
        with self.subTest(change='listed skill missing'):
            with self.assertRaisesRegex(ValueError, 'context declaration inventory changed'):
                measure_context.measure(self.root)

    def test_router_sections_that_siblings_name_cannot_disappear(self):
        # Six sibling files point at the router by section name. A rename or removal must
        # break loudly, a sibling that stops saying the pointer words must break the table,
        # and a dropped Principles entry must break the index (the only pointer to a
        # user-only principle).
        router = self.root / check_core.ROUTER
        text = router.read_text()
        self.assertEqual(check_core.router_section_errors(self.root), [])
        for name in check_core.ROUTER_SECTIONS:
            with self.subTest(section=name):
                self.assertIn('\n## ' + name + '\n', text)
                router.write_text(text.replace('\n## ' + name + '\n', '\n## ' + name + ' rules\n'))
                self.assertIn('router section missing: ' + name, check_core.router_section_errors(self.root))
        router.write_text(text.replace('\n## Autonomy\n', '\n## Autonomy rules\n'))
        seal_payload.seal(self.root, accept=[check_core.ROUTER])
        with self.assertRaisesRegex(ValueError, 'router sections differ.*Autonomy'):
            check_core.check(self.root)
        router.write_text(text)
        self.assertEqual(check_core.router_section_errors(self.root), [])
        sibling = self.root / 'plugin/skills/figure-it-out/SKILL.md'
        sibling.write_text(sibling.read_text().replace('Principles section', 'principles list'))
        self.assertTrue(any('no longer says' in e for e in check_core.router_section_errors(self.root)))
        sibling.write_text(sibling.read_text().replace('principles list', 'Principles section'))
        # pstack's naming rule: the bold title in kebab case names the leaf, unless the entry
        # gives the name itself.
        for entry, broken, skill in [('- **Prove It Works.** ', '- **Prove It Works** ', 'principle-prove-it-works'),
                                     ('(**principle-sequence-verifiable-units**). ', '(**principle-sequence-verifiable-units**) ',
                                      'principle-sequence-verifiable-units')]:
            self.assertIn(entry, text)
            router.write_text(text.replace(entry, broken))
            self.assertEqual(check_core.router_section_errors(self.root),
                             ['router Principles index lacks a trigger entry for ' + skill])

    def test_dead_cursor_frontmatter_fields_fail_the_plugin_check(self):
        path = self.root / check_core.ROUTER
        text = path.read_text()
        self.assertFalse(check_core.DEAD_FRONTMATTER & check_core.native_frontmatter(text).keys())
        for field, value in [('mode', 'true'), ('icon', 'crown'), ('color', 'yellow'),
                             ('reminder', 'Apply the mode.')]:
            with self.subTest(field=field):
                path.write_text(text.replace('\n---\n', '\n' + field + ': ' + value + '\n---\n', 1))
                seal_payload.seal(self.root, accept=[check_core.ROUTER])
                result = subprocess.run([sys.executable, str(self.root / 'scripts/check_plugin.py')],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('dead frontmatter field: hugues-mode', result.stderr)

    def test_phase_contracts_reject_order_cardinality_and_fallback_mutations(self):
        names = ['architect', 'arena', 'interrogate', 'create-verification-skill',
                 'maintain-verification-skill', 'swarm', 'show-me-your-work', 'setup-pstack', 'poteto-mode', 'tdd']
        bodies = {name: (self.root / 'plugin/skills' / check_core.ALIASES.get(name, name) / 'SKILL.md').read_text()
                  for name in names}
        bodies['feature'] = (self.root / 'plugin/skills/hugues-mode/playbooks/feature.md').read_text()
        self.assertEqual(check_core.behavior_errors(bodies), [])
        for name, before, after in [('arena', '## Phase E: Graft', '## Phase Z: Graft'),
            ('interrogate', '| Reviewer C | `inherit-parent max` |', '| Reviewer C | `opus max` |'),
            ('swarm', 'A gap does not count as a pass', 'A gap counts as a pass'),
            ('tdd', '4. **Run the new test before fixing', '7. **Run the new test before fixing'),
            ('maintain-verification-skill', 'Exercise every feature at least once', 'Exercise one feature'),
            ('poteto-mode', 'Use **figure-it-out** whenever no bundled playbook fits', 'Skip unmatched work')]:
            with self.subTest(name=name):
                self.assertIn(before, bodies[name])
                changed = dict(bodies)
                changed[name] = changed[name].replace(before, after)
                self.assertTrue(check_core.behavior_errors(changed))


class HuguesModeRouter(unittest.TestCase):
    """What an agent reads in the rewritten router and in the files it now points at."""
    def setUp(self):
        self.text = (ROOT / 'plugin/skills/hugues-mode/SKILL.md').read_text()
        self.workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()

    def bullet(self, text, start):
        return next(line for line in text.splitlines() if line.startswith(start))

    def test_frontmatter_title_contract_and_host_tool_names(self):
        self.assertEqual(set(check_core.native_frontmatter(self.text)),
                         {'name', 'description', 'disable-model-invocation'})
        body = self.text.split('---\n', 2)[2]
        self.assertTrue(body.startswith('\n# Hugues mode\n\n## Host invocation contract\n'))
        for marker in ['[host contract](../../adapters/host.md)',
                       '[mobile applicability](../../adapters/mobile.md#applicability)',
                       'The host contract governs how this skill reaches any sibling dependency.']:
            self.assertIn(marker, body.split('## Non-negotiables', 1)[0])
        for stale in ['Poteto mode', 'AskQuestion', 'poteto-agent', 'generalPurpose', '`Task`']:
            self.assertNotIn(stale, self.text)
        # The trigger names no host tool: subagents have no question tool and Codex's is
        # unobserved, so it asks, and interviews only on a call no experiment can settle.
        self.assertNotIn('AskUserQuestion', self.text)
        self.assertIn('- About to ask the user on a "which approach"', self.text)
        self.assertIn('Reserve questions for a genuine product or preference call no experiment can settle, '
                      'and interview the user on it until you reach a shared understanding.', self.text)
        self.assertIn('subagent_type: "hugues-agent"', self.text)
        # The router is user-only, as poteto-mode is upstream, and its description follows
        # poteto-mode's style line. Codex rendered 243 characters of an earlier 312-character
        # description, so the whole description stays under that observed cut.
        fields = check_core.native_frontmatter(self.text)
        self.assertTrue(fields['disable-model-invocation'])
        description = measure_context.description_text(fields['description'])
        self.assertLessEqual(len(description), 243)
        self.assertTrue(description.startswith("hugues's agent style for mobile and engineering work"), description)
        self.assertIn('/hugues-mode, or requests to work in this style.', description)
        # Cursor-only concepts keep their wording; the host adapter translates them.
        for concept in ['Bugbot', '`control-cli`',
                        '`control-ui`', '**create-skill**', 'Cursor restart']:
            self.assertIn(concept, self.text)
        # Bugbot keeps pstack's wording; the publication adapter says what it means here.
        publication = ' '.join((ROOT / 'plugin/adapters/host-publication.md').read_text().split())
        for marker in ['Claude Code Review', 'Claude GitHub Action review workflow',
                       'Codex review (`chatgpt-codex-connector`)', 'Cursor Bugbot',
                       '`bugbot-triage.md` applies to its comments unchanged',
                       'setup installs nothing',
                       '`Bugbot triage done. Not applicable. Reason no review bot.`',
                       'never tick it as if triage happened']:
            self.assertIn(marker, publication)
        # deslop is bundled, so the router names it like its sibling bundled skills.
        self.assertIn('- Before commit → the **deslop** skill (`/deslop`).', self.text)
        self.assertNotIn('cursor-team-kit` plugin (`/deslop`)', self.text)
        for path in re.findall(r'`(playbooks/[\w-]+\.md)`', self.text):
            self.assertTrue((ROOT / 'plugin/skills/hugues-mode' / path).is_file(), path)

    def test_mobile_routes_are_listed_and_the_adapter_keeps_authority(self):
        bullet = self.bullet(check_core.section(self.text, 'Playbooks'), '- **Mobile routes.**')
        for route in ['build-doctor', 'mobile-proof', 'kmp-bridge-change', 'cmp-two-target-change']:
            self.assertIn('`playbooks/' + route + '.md`', bullet)
        self.assertIn('[mobile workflows adapter](../../adapters/mobile-workflows.md) says how one is chosen', bullet)
        self.assertIn('keeps authority', bullet)
        self.assertIn('[mobile applicability](../../adapters/mobile.md#applicability) still gates loading it', bullet)
        # The adapter picks the core action first, and only two routes compose into it:
        # build-doctor and mobile-proof stand alone. The router names the routes and does not
        # restate that rule, so it cannot contradict the adapter.
        for restated in ['compose', 'intent', 'matched core playbook', 'rather than replacing']:
            self.assertNotIn(restated, bullet)
        adapter = (ROOT / 'plugin/adapters/mobile-workflows.md').read_text()
        self.assertIn('select\nthe core action playbook', adapter)
        self.assertIn('Build/toolchain diagnosis uses [build-doctor]', adapter)

    def test_model_defaults_have_one_home_and_setup_reads_its_labels_there(self):
        link = '(../../adapters/host-workers.md#model-defaults-and-role-labels)'
        subagents = check_core.section(self.text, 'Subagents')
        self.assertIn(link, subagents)
        self.assertIn("You own every subagent's work.", subagents)
        self.assertIn('**Fresh subagents by default.**', subagents)
        for moved in ['inherit-parent', 'run_in_background', 'hardest tasks', 'judgment and prose',
                      '`hillclimb`', '`bug-fix`', '`perf-issue`', '`feature, refactoring`']:
            self.assertFalse(moved in self.text, moved)
        defaults = check_core.section(self.workers, 'Model defaults and role labels')
        self.assertEqual(self.workers.count('**Defaults for every agent-tool call.**'), 1)
        for phrase in ['`run_in_background: true`', '`inherit-parent xhigh` for code',
                       '`inherit-parent max` for prose and judgment', 'strongest judgment model',
                       'override these defaults and the model choices in the routed skills',
                       '`feature, refactoring`', '`bug-fix`', '`perf-issue`', '`hillclimb`',
                       '`hardest tasks`', '`judgment and prose`']:
            self.assertIn(phrase, defaults)
        setup = (ROOT / 'plugin/skills/setup-hstack/SKILL.md').read_text()
        self.assertIn(link, setup)
        self.assertNotIn('the same labels hugues-mode uses', setup)

    def test_hugues_agent_registered_name_and_question_tool_have_a_host_home(self):
        host = (ROOT / 'plugin/adapters/host.md').read_text()
        # The router names no question tool. The adapter keys its translation on the Cursor
        # spelling the other skills still use and claims no observed Codex tool name.
        tools = check_core.section(host, 'Tools')
        row = next(line for line in tools.splitlines() if line.startswith('| `AskQuestion` |'))
        cells = [cell.strip() for cell in row.strip('|').split('|')]
        self.assertTrue(cells[1].startswith('`AskUserQuestion`.'))
        self.assertIn('In `-p` mode it is absent', cells[1])
        self.assertIn('plain text in your report and hold the dependent step', cells[1])
        self.assertTrue(cells[2].startswith('unobserved.'))
        self.assertNotIn('Translate AskQuestion', host)
        self.assertIn('Map Cursor `AskQuestion`, todos, filesystem and Git to host tools.', tools)
        grep = next(line for line in tools.splitlines() if line.startswith('| `Grep`, `Glob` |'))
        for phrase in ['`rg`', '`grep` and `find`', 'whichever the session lacks']:
            self.assertIn(phrase, grep)
        # The registered name has one per-host line in host-workers.md. host.md keeps the rename
        # list and sends every worker dispatch to that file through the phase table.
        self.assertIn('`poteto-agent` to `hugues-agent`', host)
        self.assertRegex(host, r'(?m)^\| Worker dispatch[^|]*\| \[Workers and models\]\(host-workers\.md\) \|$')
        line = next(paragraph for paragraph in self.workers.split('\n\n') if paragraph.startswith('**`hugues-agent` by host.**'))
        line = ' '.join(line.split())
        self.assertIn('Claude Code registers it as `hstack:hugues-agent`', line)
        self.assertIn('Codex has no registered name observed here', line)
        self.assertIn('takes the role instructions of `agents/hugues-agent.md`', line)
        self.assertNotIn('A core `poteto-agent` call', self.workers)
        self.assertEqual(self.workers.count('**`hugues-agent` by host.**'), 1)
        manifest = json.loads((ROOT / 'plugin/.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['name'], 'hstack')
        agent = (ROOT / 'plugin/agents/hugues-agent.md').read_text()
        self.assertIn('\n# Hugues subagent\n', agent)
        self.assertNotIn('Poteto', agent)

    def test_hosts_without_todo_tool_keep_a_checklist_in_the_agent_store(self):
        host = (ROOT / 'plugin/adapters/host.md').read_text()
        rules = [line for line in check_core.section(host, 'Tools').splitlines() if 'Markdown checklist' in line]
        self.assertEqual(len(rules), 1)
        rule = rules[0]
        with self.subTest('the rule binds every host, not one table column'):
            self.assertFalse(rule.startswith('|'), rule)
            self.assertTrue(rule.startswith('Without a todo tool, use a Markdown checklist'), rule)
        for phrase in [
                "task's [agent store](host-workflow-tools.md#agent-store-translation)",
                'copied and marked per [Playbooks](../skills/hugues-mode/SKILL.md#playbooks).',
                'Name the file in your reply']:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)
        target = (ROOT / 'plugin/adapters' / re.search(r'\[Playbooks\]\(([^)#]+)#playbooks\)', rule).group(1)).resolve()
        self.assertEqual(target, (ROOT / 'plugin/skills/hugues-mode/SKILL.md').resolve())
        self.assertIn('\n## Playbooks\n', target.read_text())
        store = (ROOT / 'plugin/adapters/host-workflow-tools.md').read_text()
        self.assertIn('## Agent-store translation', store)
        self.assertIn('use the operator-named directory', store)
        self.assertIn('Resume the recorded store', store)
        playbooks = ' '.join(check_core.section(self.text, 'Playbooks').split())
        for phrase in ['A step includes its numbered line and all continuation text. Copy the whole step.',
                       'Mark each item when its step fires, done with an evidence pointer or `skip: <reason>`.',
                       'Never bulk-mark at the end.']:
            self.assertIn(phrase, playbooks)

    def test_codex_native_loading_uses_enabled_catalog_and_complete_skill_read(self):
        host = ' '.join((ROOT / 'plugin/adapters/host.md').read_text().split())
        for phrase in [
                'On Codex, select the enabled skill from the host-provided catalog and read its complete SKILL.md.',
                'No separate Skill tool exists.',
                'Outside that mechanism, never use a file read as an invocation fallback.',
                'Respect manual-only selection, owner-disabled entries and native denials.',
                'For a native-only skill, unavailable, disabled, denied or unknown invocation stops the dependent step.',
                'An available file or a successful binding check establishes no skill permission.',
                'It loads any native-only skill itself through the host-specific mechanism above;',
                "On Claude Code, never call the Skill tool for one."]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, host)
        self.assertNotIn('for those skills, never use a file read as an invocation fallback', host)
        workers = ' '.join(self.workers.split())
        self.assertIn('Full-mode workers load the mode per [host.md](host.md) before work.', workers)
        self.assertIn('On Codex, select its enabled catalog entry and read the complete SKILL.md yourself.', workers)
        self.assertIn("preserve the workflow's own prompt", workers)
        self.assertIn("Carry the loaded mode's absolute path, derived from the current loaded skill, into every fresh worker", workers)
        self.assertIn('without a mode persona', workers)

    def test_mobile_regression_worker_has_only_the_narrow_reading_list(self):
        for path in ['plugin/adapters/mobile-workflows.md',
                     'plugin/skills/hugues-mode/playbooks/bug-fix.md']:
            body = ' '.join((ROOT / path).read_text().split())
            with self.subTest(path=path):
                for phrase in [
                        'general-purpose regression worker',
                        'reads only the `tdd` SKILL.md, the matching language baseline at absolute installed paths, the native execution adapter at its absolute installed path, and the files named in its brief',
                        'Include `<plugin>/adapters/native-execution.md` as an absolute installed path in the brief.',
                        'Any build or test command the regression worker runs goes through the native helper.',
                        'does not load the full mode or principles',
                        "It overrides transitive skill reads and TDD's production-edit steps.",
                        'The production worker is unchanged.']:
                    self.assertIn(phrase, body)
                self.assertRegex(body, r'impractical-test exception|If automated testing is impractical')
        workers = ' '.join(self.workers.split())
        self.assertIn('The mobile regression worker is a general-purpose native worker without a mode persona.', workers)
        self.assertIn('Its reading list is limited by [mobile workflows](mobile-workflows.md).', workers)
        self.assertIn('The mobile regression worker uses the general-purpose exception in', self.text)

    def test_mobile_regression_stalls_keep_the_coordinator_out_of_the_test(self):
        for path in ['plugin/adapters/mobile-workflows.md',
                     'plugin/skills/hugues-mode/playbooks/bug-fix.md']:
            body = ' '.join((ROOT / path).read_text().split())
            with self.subTest(path=path):
                for phrase in [
                        'The coordinator never writes the regression test.',
                        'On a stall, dispatch one fresh replacement with a narrower brief.',
                        'A second stall marks the regression step blocked. State it in the final message.']:
                    self.assertIn(phrase, body)

    def test_forked_context_does_not_satisfy_mobile_worker_freshness(self):
        for path in ['plugin/adapters/mobile-workflows.md', 'plugin/adapters/host-workers.md']:
            body = ' '.join((ROOT / path).read_text().split())
            with self.subTest(path=path):
                self.assertIn('A worker spawned with the coordinator\'s turns, `fork_turns: "all"` or the equivalent, is not fresh for either the regression or production role.', body)

    def test_host_translation_table_covers_control_loop_and_source_attributions(self):
        host = (ROOT / 'plugin/adapters/host.md').read_text()
        section = check_core.section(host, 'Cursor-only features')
        rows = [line for line in section.splitlines() if line.startswith('| ')][1:]
        # The cloud row moved out with the rest of the Cursor-specific prose, so
        # the always-loaded table keeps only the rows every host reads. The
        # Cursor-only rows live in the Cursor page.
        self.assertEqual(len(rows), 5)
        expected = [
            ('Cursor Automations',),
            ('Bugbot', '[Publication](host-publication.md)'),
            ('A built-in PR tool', 'gh pr create'),
            ('"control skill" / "matching control skill"', 'cursor-team-kit', '`control-cli`', '`control-ui`',
             'test-ios', 'test-android', 'native mechanism', 'XCTest or UiAutomator', 'native helper', 'execution gap'),
            ("Cursor's `/loop`", 'current local session', 'never a cloud schedule',
             'active-session waits', 'Between-turn scheduling stays an unsatisfied gap', '#34 item 6'),
        ]
        for row, markers in zip(rows, expected):
            for marker in markers:
                self.assertIn(marker, row)
        for phrase in ["Keep pstack's playbook text.",
                       'gets one plain line, no bullet or bold: `Skipped in <host>: <step>. <reason>.`',
                       'Never ask the user to choose, offer an alternative or retry.',
                       'Independent steps continue; one that needs the skipped output holds, with a named placeholder.',
                       'A skip line never checks a gate: a skipped mandatory gate holds the result.']:
            self.assertIn(phrase, section)
        self.assertNotIn('Never stop', section)
        for row in rows:
            if row.startswith(('| Cursor Automations', '| A built-in PR tool')):
                self.assertTrue(row.rstrip().endswith('| unobserved |'), row)
        # The free-versus-paid rule and the cloud row live in the Cursor page,
        # where a Cursor session reads them.
        page = (ROOT / 'plugin/adapters/hosts/cursor.md').read_text()
        for phrase in ['A free Cursor feature is native in Cursor.',
                       'A feature that needs a paid Cursor plan keeps the skip line',
                       'it is skipped on every host, including Cursor.',
                       'Cursor cloud agents',
                       'A local worktree worker substitutes only where the core permits local execution.']:
            self.assertIn(phrase, page)
        # Claude Code does not print a skip line for cloud agents: the workers
        # adapter maps `environment: "cloud"` to an isolated worktree.
        self.assertNotIn('Cursor cloud agents', section)
        workers = (ROOT / 'plugin/adapters/host-workers.md').read_text()
        self.assertIn('`isolation: "worktree"`, only where the core permits local execution.', workers)
        ui = (ROOT / 'plugin/skills/control-ui/SKILL.md').read_text()
        self.assertIn('may write to the server', ui)
        self.assertIn('get a yes from the user, or from the coordinator', ui)
        self.assertIn('never prints, returns or logs them', ui)
        self.assertIn('ask the user to log in in the browser', ui)
        bug_fix = (ROOT / 'plugin/skills/hugues-mode/playbooks/bug-fix.md').read_text()
        self.assertIn("Drive a long or stubborn hunt with Cursor's `/loop` command.", bug_fix)
        plan = (ROOT / 'plugin/skills/hugues-mode/playbooks/multi-phase-plan.md').read_text()
        self.assertIn('/loop 1h', plan)

    def test_both_native_agents_explicitly_inherit_the_parent_model(self):
        for name in ['hugues-agent', 'hugues-comment-sicko']:
            body = (ROOT / f'plugin/agents/{name}.md').read_text()
            frontmatter = body.split('---', 2)[1]
            with self.subTest(name=name):
                self.assertEqual(re.findall(r'^model: (.+)$', frontmatter, re.M), ['inherit'])

    def test_worker_reply_discloses_requested_actual_and_lowered_effort(self):
        reply = ' '.join(check_core.section(self.text, 'Writing the reply').split())
        for phrase in ['Whenever a run spawned workers, include a Workers line',
                       "each role's requested and actual model and effort",
                       'any fallback or downgrade with its reason']:
            self.assertIn(phrase, reply)
        self.assertIn('Report deliberate effort lowering too, with its reason.', self.workers)

    def test_held_publication_keeps_the_prescribed_local_pr_artifacts(self):
        publication = ' '.join((ROOT / 'plugin/adapters/host-publication.md').read_text().split())
        for phrase in [
                'With publication held or no remote or forge, save local PR title and body separately.',
                'Report paths and hold.',
                "Check Opening a PR's format, section order, Scope and verification.",
                'Skip only forge writes.',
                'Drafts grant no authority.',
                'Missing writing-for-agents is reported as a capability gap, never silently marked performed.',
                'Without a bot, record the plan box "Bugbot triage done." as',
                "The watcher's match on Claude's login, `claude`, is unconfirmed until a Claude review is seen on a PR."]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, publication)

    def test_worker_definition_uses_the_native_names(self):
        agent = (ROOT / 'plugin/agents/hugues-agent.md').read_text()
        description = re.search(r'^description: (.+)$', agent, re.M).group(1)
        for stale in ['poteto', 'generalPurpose']:
            self.assertNotIn(stale, description)
        self.assertIn("Spawn a fresh `hugues-agent` for each new task", description)
        self.assertIn("hugues-mode's Subagents section", description)
        self.assertIn('inline Principles index', description)

    def test_hugues_agent_finds_the_mode_file_itself(self):
        # Issue #48: owners whose brief carried no hugues-mode path never read a bundled
        # skill. pstack's poteto-agent finds its mode file on disk; hugues-agent does the same
        # in Claude Code terms, in this order. Claude Code cannot preload a
        # disable-model-invocation skill, so the user-only mode is never preloaded.
        agent = (ROOT / 'plugin/agents/hugues-agent.md').read_text()
        self.assertNotRegex(agent, r'(?m)^skills:')
        self.assertNotIn('preload', agent)
        flat = ' '.join(agent.split())
        order = ["Read the `hugues-mode` skill's `SKILL.md` in full before doing any work",
                 'the absolute path to the `hugues-mode` SKILL.md that your parent gave you',
                 'search the installed plugins under the Claude config directory',
                 'a file whose path ends in `skills/hugues-mode/SKILL.md`',
                 'stop and tell your parent']
        positions = [flat.find(step) for step in order]
        self.assertNotIn(-1, positions, dict(zip(order, positions)))
        self.assertEqual(positions, sorted(positions))

    def test_bundled_user_only_skills_are_files_never_skill_tool_calls(self):
        # Issue #48: Claude Code's Skill tool refuses a user-only skill and tells the model to
        # take no other route, and five owners stopped there. The rule lives in the adapter and
        # in the agent header, and the playbooks keep their inherited wording.
        for path in ['plugin/adapters/host.md', 'plugin/agents/hugues-agent.md']:
            flat = ' '.join((ROOT / path).read_text().split())
            for phrase in ['On Claude Code, never call the Skill tool for one.',
                           '`/<name>` and "the **<name>** skill" mean reading `../<name>/SKILL.md`',
                           'file-read tool']:
                with self.subTest(path=path, phrase=phrase):
                    self.assertIn(phrase, flat)
        # Native-only skills keep their native route.
        self.assertIn('Reach `setup-hstack` and each consumer or external skill',
                      ' '.join((ROOT / 'plugin/adapters/host.md').read_text().split()))

    def test_playbook_headers_no_longer_hold_a_step_on_invocation(self):
        # Issue #48: pstack's playbooks have no "never a path to read" clause. The three hStack
        # headers keep read-workflow and plan-check (issue #78) and lose the clause.
        for name in ['autopilot-full', 'autopilot-stack', 'multi-phase-plan']:
            text = (ROOT / 'plugin/skills/hugues-mode/playbooks' / (name + '.md')).read_text()
            header = ' '.join(text.split('\n\n', 1)[0].split())
            with self.subTest(playbook=name):
                self.assertNotIn('never a path to read', header)
                self.assertNotIn('Unavailable or denied invocation holds that step', header)
                self.assertIn('bound `read-workflow`', header)
                self.assertIn('`plan-check` for validation', header)
                self.assertIn('reach each skill as [host.md](../../../adapters/host.md) directs.', header)
        tools = ' '.join((ROOT / 'plugin/adapters/host-tools.md').read_text().split())
        self.assertNotIn('never a path to read', tools)
        self.assertIn('a plan names the skill to apply, and the agent resolves the path', tools)
