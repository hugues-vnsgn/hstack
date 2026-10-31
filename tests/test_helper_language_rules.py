from pathlib import Path
import re
import unittest

from test_host_adapters import InstalledFixture


class HelperLanguageRules(InstalledFixture, unittest.TestCase):
    def read(self, path):
        result = self.bound('read-workflow', path)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_command_routing_reaches_native_execution_without_mobile_gate(self):
        host = self.read('adapters/host.md')
        self.assertIn(
            '| Running `xcodebuild`, `swift build` / `swift test`, or Gradle in an Android/KMP/CMP project | [Native execution](native-execution.md) |',
            host)
        self.assertEqual(
            (self.plugin / 'adapters/native-execution.md').resolve(),
            (self.plugin / 'adapters' / re.search(
                r'\[Native execution\]\(([^)]+)\)', host).group(1)).resolve())
        self.assertIn('## Run one selected check', self.read('adapters/native-execution.md'))
        self.assertIn('Plain JVM or server Gradle projects stay out of scope.', host)
        mobile = self.read('adapters/mobile.md')
        self.assertIn('Apply mobile guidance only to an explicitly selected mobile task (Swift/iOS,', mobile)

    def test_required_helper_section_limits_each_exception_and_reports_gaps(self):
        text = self.read('adapters/native-execution.md')
        self.assertTrue(text.startswith(
            '# Native build and test execution\n\n## When the helper is required\n'))
        section = ' '.join(text.split('## When the helper is required\n', 1)[1].split('\n## ', 1)[0].split())
        for phrase in [
                'Every build or test command using `xcodebuild`, `swift build` / `swift test`, or Gradle in an Android/KMP/CMP project must go through the helper.',
                'Allow an exception for one command at a time, only when:',
                "The helper does not support that command.",
                'The helper returns a prerequisite error that the agent cannot resolve.',
                'Run the excepted command and retain its raw logs in the task evidence store.',
                'List each excepted command and its reason under Gaps in the final message.',
                'An unsupported test step never excuses a build step or any other supported step.',
                'The existing impractical-test exception is unchanged.']:
            self.assertIn(phrase, section)
        self.assertEqual(re.findall(r'^\d+\. (.+)$', text.split('\n## Run one selected check', 1)[0], re.M), [
            'The helper does not support that command.',
            'The helper returns a prerequisite error that the agent cannot resolve.',
        ])

    def test_adversary_brief_requires_language_baseline_before_source(self):
        skill = (self.plugin / 'skills/interrogate/SKILL.md').read_text()
        text = ' '.join(skill.split())
        self.assertIn('Add the language baselines to each brief', text)
        self.assertIn('matching the languages in the scope, or `none`, each read in full before the first source read', text)
        self.assertLess(skill.index('Break this change.'), skill.index('Add the language baselines'))
        self.assertLess(skill.index('Add the language baselines'), skill.index('## Verify'))
        for name in ['swift-best-practices', 'kotlin-best-practices']:
            self.assertIn(f'<plugin>/skills/{name}/SKILL.md', skill)
            self.assertIn(f'name: {name}', (self.plugin / f'skills/{name}/SKILL.md').read_text())

    def test_worker_briefs_carry_absolute_baselines_on_both_hosts(self):
        mode = (self.plugin / 'skills/hugues-mode/SKILL.md').read_text()
        section = ' '.join(mode.split('## Subagents\n', 1)[1].split('\n## ', 1)[0].split())
        for phrase in [
                'On both Claude Code and Codex, every worker brief that reaches Swift or Kotlin source must carry the absolute installed baseline paths',
                'read each baseline in full before the first source read',
                'Resolve `<plugin>` from the loaded mode path',
                'include both paths for mixed-language work']:
            self.assertIn(phrase, section)
        for name in ['swift-best-practices', 'kotlin-best-practices']:
            token = f'<plugin>/skills/{name}/SKILL.md'
            self.assertIn(token, section)
            resolved = Path(token.replace('<plugin>', str(self.plugin)))
            self.assertTrue(resolved.is_absolute())
            self.assertIn(f'name: {name}', resolved.read_text())

    def test_pasted_mobile_lens_resolves_links_from_installed_owner(self):
        text = self.read('skills/hugues-mode/references/mobile-review.md')
        self.assertIn(
            "Before pasting this lens into a prompt or the evidence store, resolve its relative links to absolute installed paths from this file's directory.",
            ' '.join(text.split()))
        target = re.search(r'\[mobile language scope\]\(([^)]+)\)', text).group(1)
        resolved = (self.plugin / 'skills/hugues-mode/references' / target).resolve()
        self.assertEqual(resolved, self.plugin / 'adapters/host-mobile-languages.md')
        self.assertIn('# Swift and Kotlin scope', resolved.read_text())
