"""Installed-payload regressions from the PR 17 review: host files, modes and raw skill reads."""
import os
import re
import runpy
import shlex
import unittest
from unittest.mock import patch

from test_host_adapters import InstalledFixture

FEATURE = 'skills/hugues-mode/playbooks/feature.md'


class InstalledTolerance(InstalledFixture, unittest.TestCase):
    def test_bootstrap_dependencies_do_not_block_bound_helpers(self):
        modules = self.plugin / 'skills/hugues-mode/scripts/node_modules'
        (modules / 'commander').mkdir(parents=True)
        (modules / 'commander/package.json').write_text('{}\n')
        (modules / '.bin').mkdir()
        (modules / '.bin/commander').symlink_to('../commander/package.json')
        result = self.bound('read-workflow', FEATURE)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_host_metadata_files_do_not_block_bound_helpers(self):
        for name in ['.DS_Store', 'skills/hugues-mode/.DS_Store']:
            with self.subTest(name=name):
                (self.plugin / name).write_bytes(b'')
                result = self.bound('read-workflow', FEATURE)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_extra_file_beside_bootstrap_dependencies_is_still_rejected(self):
        for name in ['skills/hugues-mode/scripts/extra.md', 'skills/hugues-mode/node_modules/x.js']:
            with self.subTest(name=name):
                path = self.plugin / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('extra\n')
                result = self.bound('read-workflow', FEATURE)
                self.assertEqual(result.returncode, 2)
                self.assertIn('inventory differs', result.stderr)
                path.unlink()

    def test_unreadable_directory_holds_instead_of_shrinking_the_inventory(self):
        # Injected, because chmod 000 does not deny reads when the suite runs as root.
        from runtime import payload
        folder = str(self.plugin / 'skills/hugues-mode/references')
        scandir = os.scandir
        def denied(path='.'):
            if os.fspath(path) == folder:
                raise PermissionError(13, 'Permission denied', folder)
            return scandir(path)
        with patch('os.scandir', denied), self.assertRaises(PermissionError):
            payload.inventory(self.plugin, allow_runtime_cache=True)

    def test_metadata_name_cannot_hide_a_directory_or_symlink(self):
        path = self.plugin / 'skills/.DS_Store'
        path.symlink_to('hugues-mode/SKILL.md')
        result = self.bound('read-workflow', FEATURE)
        self.assertEqual(result.returncode, 2)

    def test_group_writable_install_binds_and_runs(self):
        # umask 002 (user private groups) and git-archive extraction both give 664/775.
        for path in self.plugin.rglob('*'):
            path.chmod(path.stat().st_mode | 0o020)
        bound = self.run_tool('bind')
        self.assertEqual(bound.returncode, 0, bound.stderr)
        self.binding.write_text(bound.stdout)
        result = self.bound('read-workflow', FEATURE)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_world_writable_or_executable_drift_is_still_rejected(self):
        cases = [('adapters/host_tools.py', 0o646), ('adapters/runtime/payload.json', 0o666),
                 ('adapters/runtime/activity.py', 0o646), ('adapters/runtime/payload.py', 0o755),
                 ('skills/hugues-mode/scripts/watch-pr/watch-pr', 0o644), (FEATURE, 0o755),
                 (FEATURE, 0o646)]
        for name, mode in cases:
            with self.subTest(name=name, mode=oct(mode)):
                path = self.plugin / name
                original = path.stat().st_mode & 0o777
                path.chmod(mode)
                self.assertEqual(self.run_tool('bind').returncode, 2)
                path.chmod(original)

    def plan_result(self, text, *, markdown=False):
        plan = self.consumer / 'plan.md'
        plan.write_text(text + '\n')
        return self.bound('translate-plan', *(['--markdown'] if markdown else []), plan)

    def test_translate_refuses_every_spelling_of_a_raw_skill_read(self):
        for text in ['cat /abs/plugin/skills/tdd/SKILL.md',
                     'cat plugin/skills/tdd/SKILL.md',
                     "cat skills/tdd/SK''ILL.md",
                     'cat "skills/tdd/SKILL.md"',
                     "`cat 'plugin/skills/tdd/SKILL.md'`",
                     'Read (plugin/skills/tdd/SKILL.md) first.']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('native skill invocation', result.stderr)
        plan = self.consumer / 'plan.md'
        plan.write_text('Each public skill keeps one SKILL.md body.\n')
        prose = self.bound('translate-plan', plan)
        self.assertEqual((prose.returncode, prose.stdout), (0, plan.read_text()), prose.stderr)

    def test_translate_refuses_a_bundled_skill_body_spelled_exactly(self):
        # PR 1 fix rounds 1 and 2 translated these exact literal spellings of a bundled user-only
        # skill's SKILL.md into a guarded read. Round 3 reverses that: the helper never reads a
        # skill body, so the exact spelling is refused like every other, with nothing emitted
        # that could be run. An agent reads that file with the host's own file-read tool.
        for text in ["cat skills/tdd/SK''ILL.md", 'cat "skills/tdd/SKILL.md"', 'cat skills/tdd/SKILL.md',
                     '`skills/tdd/SKILL.md`', 'skills/tdd/SKILL.md', '`pstack/skills/tdd/SKILL.md`',
                     'git show origin/main:skills/tdd/SKILL.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)
                self.assertNotIn('read-workflow', result.stderr)

    def test_translate_refuses_skill_body_paths_after_normalization(self):
        paths = ['.claude/skills/mine/./SKILL.md', '.claude/skills/x/../mine/SKILL.md',
                 '.claude/skills/mine/SKILL.MD', '.claude/skills/mine/Skill.md',
                 '.claude//skills//mine//SKILL.md', 'mine/SKILL.md']
        forms = ['cat {}', 'sed -n 1,20p {}', 'git show origin/main:{}', 'git show HEAD:{}',
                 'node skills/hugues-mode/scripts/check-plan.mjs {}', '`cat {}`']
        for path in paths:
            for form in forms:
                with self.subTest(line=form.format(path)):
                    result = self.plan_result(form.format(path))
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertIn('native skill invocation', result.stderr)
        for text in ['Each public skill keeps one skill.md body.',
                     'cat .claude/references/notes.md',
                     'cat docs/SKILL.md.bak']:
            with self.subTest(control=text):
                result = self.plan_result(text)
                self.assertEqual((result.returncode, result.stdout), (0, text + '\n'), result.stderr)

    def assert_skill_command_refused(self, command):
        for text, markdown in [(command, False), (f'Run `{command}`.', False),
                               (f'Run `{command}`.', True)]:
            with self.subTest(text=text, markdown=markdown):
                result = self.plan_result(text, markdown=markdown)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')
                self.assertIn('skill', result.stderr)

    def test_translate_refuses_question_mark_skill_expansion(self):
        self.assert_skill_command_refused('cat .claude/skills/mine/SKILL.m?')

    def test_translate_refuses_skill_body_command_substitution(self):
        self.assert_skill_command_refused("cat $(find .claude -iname 'skill.md')")

    def test_translate_refuses_skill_prefix_glob(self):
        self.assert_skill_command_refused('cat .claude/skills/mine/S*')

    def test_translate_refuses_skill_directory_glob(self):
        self.assert_skill_command_refused('cat .claude/skills/mine/*')

    def test_translate_refuses_skill_bracket_glob(self):
        self.assert_skill_command_refused('cat .claude/skills/mine/SKILL.[m]d')

    def test_translate_refuses_skill_brace_expansion(self):
        self.assert_skill_command_refused('cat .claude/skills/mine/SKILL.{md,txt}')

    def test_translate_refuses_skill_variable_expansion(self):
        self.assert_skill_command_refused('f=SKILL.md; cat .claude/skills/mine/$f')

    def test_expansion_after_skill_directory_name_is_refused(self):
        for command in ['suffix=/mine; cat .claude/skills${suffix}/*',
                        'cat .claude/skills`printf /mine/`*',
                        'cat .claude/skills"$(printf /mine/)"*',
                        'cat .claude/skills{,/mine}/*',
                        'cat .claude/skills*/mine/*']:
            for text, markdown in [(command, False), (f'~~~sh\n{command}\n~~~', True)]:
                with self.subTest(text=text, markdown=markdown):
                    result = self.plan_result(text, markdown=markdown)
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertEqual(result.stdout, '')

    def test_translate_limits_skill_directories_to_known_literal_forms(self):
        paths = ['skills/mine/notes.md', '.claude/skills/mine/notes.md',
                 '.agents/skills/mine/notes.md', '~/.claude/skills/mine/notes.md',
                 '/abs/plugin/skills/mine/notes.md', 'other-plugin/skills/mine/notes.md',
                 '.claude//Skills//mine/notes.md', ".claude/sk''ills/mine/notes.md"]
        for path in paths:
            for form in ['{}', 'cat {}', 'head -50 {}', 'git show HEAD:{}',
                         'git show origin/main:{}', '`cat {}`']:
                with self.subTest(text=form.format(path)):
                    result = self.plan_result(form.format(path))
                    self.assertEqual(result.returncode, 2, result.stdout)
                    self.assertEqual(result.stdout, '')

    def test_skill_scope_cannot_escape_through_quotes_or_helper_operands(self):
        for text in ["cat .claude/Skills/mine/* 'unfinished",
                     "cat $(find .claude -iname 'SK''ILL.md')",
                     "cat $(find .claude -iname 'skill.md",
                     'cat .claude/Skills',
                     'find skills -type f -exec cat {} ;',
                     'node skills/hugues-mode/scripts/check-plan.mjs .claude/skills/mine/notes.md',
                     'git show HEAD:skills/hugues-mode/playbooks/feature.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')

    def test_backticks_cannot_hide_a_standalone_skill_command(self):
        for text in ["cat .claude/skills/mine/* # `note`",
                     "cat .claude/skills/mine/`echo '*'`",
                     "cat $(find .claude -iname 'skill.md') # `note`"]:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')

    def test_default_shell_backticks_cannot_hide_skill_name(self):
        for text in ["cat `find .claude -iname 'skill.md'`",
                     "cat `find .agents -iname 'SK''ILL.md'`"]:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')
        text = "cat `find docs -iname 'notes.md'`"
        result = self.plan_result(text)
        self.assertEqual((result.returncode, result.stdout), (0, text + '\n'), result.stderr)

    def test_translation_preserves_unrelated_shell_commands(self):
        for text in [
                'cat docs/*.md', 'cat ~/notes.txt', 'echo "$HOME"',
                'git diff --name-only $(git merge-base HEAD origin/main) origin/main',
                'git fetch origin branch && git checkout abc123',
                'cat docs/skills-guide.md', 'cat my-skills/notes.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, text + '\n')

    def test_markdown_option_preserves_prose_with_or_without_code_spans(self):
        for text in ["The .claude/skills/ folder holds * patterns.",
                     "Discuss * and $variables near SKILL.md; run `git status`.",
                     "The operator's .claude/skills/ folder holds * patterns; run `git status`."]:
            with self.subTest(text=text):
                result = self.plan_result(text, markdown=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, text + '\n')

    def test_markdown_code_blocks_and_malformed_spans_cannot_hide_skill_reads(self):
        for text in ['```sh\ncat .claude/skills/mine/*\n```',
                     '~~~\ncat .claude/skills/mine/* # `note`\n~~~',
                     "```bash\ncat `find .claude -iname 'skill.md'`\n```",
                     '    cat .claude/skills/mine/*',
                     "\tcat $(find .claude -iname 'skill.md')",
                     "    cat `find .claude -iname 'skill.md'`",
                     'Run ``cat .claude/skills/mine/*``.',
                     'Run `cat .claude/skills/mine/*',
                     '```sh\ncat docs/notes.md']:
            with self.subTest(text=text):
                result = self.plan_result(text, markdown=True)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')

    def test_markdown_container_code_blocks_hold(self):
        for text in ['> ~~~sh\n> cat .claude/skills/mine/*\n> ~~~',
                     '> ```sh\n> cat .claude/skills/mine/*\n> ```',
                     '>>~~~sh\n>>cat .claude/skills/mine/*\n>>~~~',
                     '>     cat .claude/skills/mine/*',
                     '- > ~~~sh\n  > cat .claude/skills/mine/*\n  > ~~~',
                     '> ~~~sh\n> git status\n> ~~~']:
            with self.subTest(text=text):
                result = self.plan_result(text, markdown=True)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')

    def test_markdown_code_blocks_keep_safe_commands_and_guard_resource_reads(self):
        guarded = shlex.join(['python3', str(self.helper), 'read-workflow',
                             '--binding', str(self.binding), '--', FEATURE])
        for opener, closer in [('```sh', '```'), ('~~~~', '~~~~')]:
            text = f'Explanation.\n{opener}\ncat {FEATURE}\ngit status\n{closer}\nDone.'
            result = self.plan_result(text, markdown=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, text.replace('cat ' + FEATURE, guarded) + '\n')
            repeated = self.plan_result(result.stdout.rstrip('\n'), markdown=True)
            self.assertEqual(repeated.stdout, result.stdout, repeated.stderr)

    def test_markdown_indented_resource_reads_keep_the_surrounding_prose(self):
        text = f'Explanation.\n\n    cat {FEATURE}\n\nDone.'
        guarded = shlex.join(['python3', str(self.helper), 'read-workflow',
                             '--binding', str(self.binding), '--', FEATURE])
        result = self.plan_result(text, markdown=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, text.replace('cat ' + FEATURE, guarded) + '\n')

    def test_markdown_nested_lists_translate_inline_commands(self):
        guarded = shlex.join(['python3', str(self.helper), 'read-workflow',
                             '--binding', str(self.binding), '--', FEATURE])
        for text in [f'- [ ] Parent\n    - [ ] Read `cat {FEATURE}`.',
                     f'1. Parent\n    1. Read `cat {FEATURE}`.',
                     f'- Parent\n    - Child\n        - Read `cat {FEATURE}`.']:
            with self.subTest(text=text):
                result = self.plan_result(text, markdown=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, text.replace('cat ' + FEATURE, guarded) + '\n')
                repeated = self.plan_result(result.stdout.rstrip('\n'), markdown=True)
                self.assertEqual(repeated.stdout, result.stdout, repeated.stderr)
        for text in ['- Parent\n    - Run `cat .claude/skills/mine/*`.',
                     '- Parent\n\n      cat .claude/skills/mine/*',
                     "- Parent\n\n      cat `find .claude -iname 'skill.md'`",
                     '    - cat .claude/skills/mine/*',
                     '- - -\n\n    cat .claude/skills/mine/*',
                     '* * *\n\n    cat .claude/skills/mine/*',
                     'Heading\n- \n\n    cat .claude/skills/mine/*',
                     'Paragraph\n2. Not a list interruption\n\n    cat .claude/skills/mine/*',
                     f'- Parent\n    Continue with `cat {FEATURE}`.',
                     'Heading\n- \n\n    - ignored; cat .claude/skills/mine/*',
                     'Paragraph\n2. Not a list interruption\n\n    - ignored; cat .claude/skills/mine/*',
                     "Heading\n- \n\n    - ignored; cat `find .claude -iname 'skill.md'`"]:
            with self.subTest(text=text):
                result = self.plan_result(text, markdown=True)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')

    def test_emitted_helpers_retranslate_when_the_install_path_contains_skills(self):
        for folder in ['skills/plugin', 'skills/plugin $literal']:
            destination = self.area / folder
            destination.parent.mkdir(exist_ok=True)
            self.plugin.rename(destination)
            self.plugin = destination
            self.helper = self.plugin / 'adapters/host_tools.py'
            bound = self.run_tool('bind')
            self.assertEqual(bound.returncode, 0, bound.stderr)
            self.binding.write_text(bound.stdout)
            for command in ['cat ' + FEATURE,
                            'node skills/hugues-mode/scripts/check-plan.mjs plan.md']:
                with self.subTest(folder=folder, command=command):
                    translated = self.plan_result(command)
                    self.assertEqual(translated.returncode, 0, translated.stderr)
                    repeated = self.plan_result(translated.stdout.rstrip('\n'))
                    self.assertEqual(repeated.returncode, 0, repeated.stderr)
                    self.assertEqual(repeated.stdout, translated.stdout)

    def test_bundled_plan_templates_keep_their_command_translations(self):
        helper = ['python3', str(self.helper)]
        binding = ['--binding', str(self.binding), '--']
        plan_path = str(self.consumer / 'filled plan.md')
        replacements = {
            'node skills/hugues-mode/scripts/check-plan.mjs ' + shlex.quote(plan_path):
                shlex.join(helper + ['plan-check'] + binding + [plan_path]),
        }
        for playbook in ['autopilot-full', 'autopilot-stack', 'opening-a-pr']:
            source = f'skills/hugues-mode/playbooks/{playbook}.md'
            guarded = shlex.join(helper + ['read-workflow'] + binding + [source])
            replacements[source] = guarded
            replacements['git show origin/main:' + source] = guarded
        commands = {}
        inline = r'(?<!`)`([^`\n]+)`(?!`)'
        for template in ['multi-phase-plan', 'autopilot-full', 'autopilot-stack']:
            for execution in ['autopilot-full', 'autopilot-stack']:
                with self.subTest(template=template, execution=execution):
                    text = (self.plugin / f'skills/hugues-mode/playbooks/{template}.md').read_text()
                    text = text.replace('<execution playbook>', execution)
                    text = text.replace('<plan.md>', shlex.quote(plan_path))
                    expected = text
                    for source, guarded in replacements.items():
                        expected = expected.replace('`' + source + '`', '`' + guarded + '`')
                    result = self.plan_result(text, markdown=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected + '\n')
                    repeated = self.plan_result(result.stdout.rstrip('\n'), markdown=True)
                    self.assertEqual(repeated.returncode, 0, repeated.stderr)
                    self.assertEqual(repeated.stdout, result.stdout.rstrip('\n') + '\n')
                    commands.update(zip(re.findall(inline, text), re.findall(inline, expected)))
        for source, expected in commands.items():
            with self.subTest(command=source):
                result = self.plan_result(source)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected + '\n')

    def test_open_quotes_and_code_spans_cannot_skip_the_skill_body_check(self):
        # An unclosed quote returned the line before any skill-body check ran, and a code span
        # split the path into fragments that each looked harmless.
        for text in ["cat .claude/Skills/mine/SKILL.md 'note", 'cat mine/./SKILL.MD "note',
                     'cat .claude/skills/mine/`SKILL.md`']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('native skill invocation', result.stderr)

    def test_read_workflow_refuses_every_spelling_of_a_skill_body(self):
        for source in ['skills/tdd/SKILL.md', 'skills/tdd//SKILL.md', './skills/tdd/SKILL.md', 'SKILL.md',
                       'skills/tdd/./SKILL.md', 'skills/x/../tdd/SKILL.md', 'skills/tdd/SKILL.MD',
                       'skills/tdd/Skill.md']:
            with self.subTest(source=source):
                result = self.bound('read-workflow', source)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)

    def test_read_workflow_refuses_a_bundled_user_only_skill_body_and_its_alias(self):
        # Reversed in round 3: `tdd` is user-only, and the helper still returns nothing for it.
        for source in ['skills/tdd/SKILL.md', 'pstack/skills/tdd/SKILL.md']:
            with self.subTest(source=source):
                result = self.bound('read-workflow', source)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)

    def test_translate_rejects_a_skill_body_at_any_revision_other_than_origin_main(self):
        # PR 1 fix round 2 security regression: `git show <rev>:<path>/SKILL.md` returned
        # the literal plan text unchanged for every revision other than `origin/main`,
        # skipping the skill-body guard entirely. That held for a consumer path
        # (`.claude/skills/...`) and even for a bundled, approved path
        # (`skills/tdd/SKILL.md`) read at the wrong revision -- both must still require
        # native invocation, exactly as the pre-regression `a67df90` translator did.
        for text in ['git show HEAD:.claude/skills/mine/SKILL.md',
                     'git show HEAD:.agents/skills/mine/SKILL.md',
                     'git show HEAD:skills/tdd/SKILL.md',
                     'git show feature-branch:plugin/skills/other-plugin/SKILL.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('native skill invocation', result.stderr)

    def test_translate_rejects_consumer_and_external_skill_body_paths(self):
        # A consumer's own `.claude/skills/...` or `.agents/skills/...` convention, and an
        # external plugin's skill, are never bundled references: no guarded read ever
        # substitutes for their native invocation. The plan-check helper's operand is the
        # round 3 review's case: it must not translate a consumer skill into a validation run.
        helper = 'skills/hugues-mode/scripts/check-plan.mjs'
        for text in ['cat .claude/skills/mine/SKILL.md',
                     'cat .agents/skills/mine/SKILL.md',
                     '`other-plugin/skills/foo/SKILL.md`',
                     'node ' + helper + ' .claude/skills/mine/SKILL.md',
                     'node ' + helper + ' .agents/skills/mine/SKILL.md',
                     'node ' + helper + ' skills/tdd/SKILL.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)

    def test_translate_refuses_unsupported_shell_forms_on_a_skill_body_as_native_only(self):
        # Round 2 gave `sed`/`head` on a bundled SKILL.md a syntax message ("use a standalone
        # guarded read"). No guarded read of a skill body exists any more, so that advice would
        # point at a command that also fails: the message is the native-invocation one again.
        for text in ['sed -n 1,5p skills/tdd/SKILL.md', 'head skills/tdd/SKILL.md']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('native skill invocation', result.stderr)
                self.assertNotIn('standalone guarded read', result.stderr)

    def test_read_workflow_and_translate_keep_model_invocable_skills_native_only(self):
        # `hugues-mode` and `setup-huguesstack` stay model-invocable and, like every other
        # bundled skill, their SKILL.md is refused by both verbs.
        for source in ['skills/hugues-mode/SKILL.md', 'skills/setup-huguesstack/SKILL.md',
                       'pstack/skills/poteto-mode/SKILL.md', 'pstack/skills/setup-pstack/SKILL.md']:
            with self.subTest(source=source):
                result = self.bound('read-workflow', source)
                self.assertEqual(result.returncode, 2)
                self.assertIn('native skill invocation', result.stderr)
        for text in ['cat skills/hugues-mode/SKILL.md', 'cat skills/setup-huguesstack/SKILL.md',
                     'git show origin/main:skills/hugues-mode/SKILL.md',
                     '`skills/setup-huguesstack/SKILL.md`']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('native skill invocation', result.stderr)

    def test_a_consumer_skill_symlinked_to_a_bundled_body_is_still_refused(self):
        # The refusal is on the spelling, so a consumer skill that happens to link to a bundled
        # file gets no different treatment; and the symlinked file is never read.
        skill = self.consumer / '.claude/skills/mine'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').symlink_to(self.plugin / 'skills/tdd/SKILL.md')
        for text in ['cat .claude/skills/mine/SKILL.md', '`.claude/skills/mine/SKILL.md`']:
            with self.subTest(text=text):
                result = self.plan_result(text)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, '')
                self.assertIn('native skill invocation', result.stderr)


class SkillBodyRejectionMatrix(InstalledFixture, unittest.TestCase):
    """Every way an agent might reach a SKILL.md through the helper, against every skill.

    PR 1 rounds 1 and 2 let the helper read bundled SKILL.md files and each review found
    another branch that slipped past the skill-body guard. Round 3 puts the guard back, and
    this matrix is the proof that it holds for all 54 bundled skills, their legacy aliases,
    a consumer's skill directories and an external plugin. It runs the installed runtime
    in-process (the same verified buffers the CLI runs) so the whole matrix stays fast;
    the tests above exercise the CLI end to end.
    """

    EXTERNAL = ['other-plugin/skills/foo/SKILL.md', 'plugin/skills/other-plugin/SKILL.md',
                '/abs/plugin/skills/tdd/SKILL.md', '.claude/skills/mine/SKILL.md',
                '.agents/skills/mine/SKILL.md', 'node_modules/pkg/skills/foo/SKILL.md']
    PLAN_FORMS = ['`{p}`', '{p}', 'cat {p}', 'cat "{p}"', "cat '{p}'", 'git show origin/main:{p}',
                  'git show HEAD:{p}', 'git show feature-branch:{p}', 'sed -n 1,5p {p}', 'head {p}',
                  'node skills/hugues-mode/scripts/check-plan.mjs {p}',
                  'node pstack/skills/poteto-mode/scripts/check-plan.mjs {p}',
                  '`cat {p}`', 'Read ({p}) first.']

    def setUp(self):
        super().setUp()
        namespace = runpy.run_path(str(self.helper))
        _, self.payload = namespace['load_runtime_sources'](self.binding)
        rows = self.payload.verify(self.plugin)  # integrity is checked once, for real
        self.payload.verify = lambda root: rows  # the same verified tree for every case below
        self.legacy = {old: new for old, new in rows['legacy_paths'].items() if new.endswith('/SKILL.md')}
        self.bundled = sorted(p.name for p in (self.plugin / 'skills').iterdir() if p.is_dir())

    def refused(self, call, *args):
        with self.assertRaises(ValueError) as caught:
            call(*args)
        self.assertIn('native skill invocation', str(caught.exception))
        self.assertNotIn('standalone guarded read', str(caught.exception))

    def test_the_fixture_covers_every_bundled_skill_and_alias(self):
        self.assertEqual(len(self.bundled), 54)
        self.assertEqual(len(self.legacy), 54)
        self.assertEqual(set(self.legacy.values()), {f'skills/{name}/SKILL.md' for name in self.bundled})

    def test_read_workflow_refuses_every_skill_body_spelling(self):
        cases = 0
        for name in self.bundled:
            sources = [f'skills/{name}/SKILL.md', f'skills/{name}//SKILL.md', f'./skills/{name}/SKILL.md',
                       f'skills/{name}/../{name}/SKILL.md', f'skills/../skills/{name}/SKILL.md',
                       *[old for old, new in self.legacy.items() if new == f'skills/{name}/SKILL.md']]
            for source in sources:
                cases += 1
                with self.subTest(source=source):
                    self.refused(self.payload.workflow, self.plugin, source)
        for source in self.EXTERNAL:
            cases += 1
            with self.subTest(source=source):
                self.refused(self.payload.workflow, self.plugin, source)
        self.assertGreaterEqual(cases, 300)

    def test_translate_plan_refuses_every_skill_body_in_every_form(self):
        paths = [f'skills/{name}/SKILL.md' for name in self.bundled] + sorted(self.legacy) + self.EXTERNAL
        cases = 0
        for path in paths:
            for form in self.PLAN_FORMS:
                text = form.format(p=path)
                cases += 1
                with self.subTest(text=text):
                    self.refused(self.payload.translate, self.plugin, self.binding, text + '\n')
        self.assertGreaterEqual(cases, 1400)

    def test_every_skill_body_is_refused_inside_a_larger_plan(self):
        # A refused line fails the whole plan, so a skill body cannot ride along with allowed lines.
        allowed = '`skills/hugues-mode/playbooks/feature.md`'
        for name in self.bundled:
            with self.subTest(name=name):
                text = f'Intro.\n{allowed}\nUse `skills/{name}/SKILL.md` here.\n'
                self.refused(self.payload.translate, self.plugin, self.binding, text)

    def test_ordinary_references_stay_readable_so_the_matrix_is_not_a_blanket_refusal(self):
        checked = 0
        for path in sorted((self.plugin / 'skills').glob('*/references/*.md')):
            relative = path.relative_to(self.plugin).as_posix()
            with self.subTest(relative=relative):
                self.assertEqual(self.payload.workflow(self.plugin, relative), path.read_bytes())
                checked += 1
        self.assertGreaterEqual(checked, 20)
        playbook = 'skills/hugues-mode/playbooks/feature.md'
        translated = self.payload.translate(self.plugin, self.binding, f'`{playbook}`\n')
        self.assertIn('read-workflow', translated)

    def test_a_symlinked_or_traversing_skill_body_is_refused_before_any_read(self):
        outside = self.area / 'outside.md'
        outside.write_text('secret\n')
        target = self.plugin / 'skills/tdd/SKILL.md'
        original = target.read_bytes()
        target.unlink()
        target.symlink_to(outside)
        for source in ['skills/tdd/SKILL.md', 'pstack/skills/tdd/SKILL.md']:
            with self.subTest(source=source):
                result = self.bound('read-workflow', source)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('secret', result.stdout)
        target.unlink()
        target.write_bytes(original)
        for source in ['../outside.md', 'skills/../../outside.md', '/etc/passwd']:
            with self.subTest(source=source):
                result = self.bound('read-workflow', source)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('secret', result.stdout)


if __name__ == '__main__':
    unittest.main()
