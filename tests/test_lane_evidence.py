"""Static guidance and an independent checker for normalized live host evidence.

This module does not route a prompt or simulate a host. The optional CLI checks
actual observations normalized by a reviewer from saved replies and tool traces.
Withhold fixture `expected` and declaration anchors from hosts. Supply `source_reads` from actual tool
receipts, not a host's assertion. Acceptance covers these cases only, not general
model adherence. Unit tests below exercise checker behavior with concrete inputs.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_wp2_contract import MODE, section, steps

from release_snapshot import release_root
ROOT = release_root()
FIXTURE = ROOT / 'tests/fixtures/rc2-lane-evidence.json'
TARGET_COMPONENTS = ('requested_destination', 'module', 'source_set', 'scheme',
                     'variant', 'device_instance')


def citation_content(case, evidence, source_reads):
    """Resolve only independently available request text or a traced source read."""
    if not isinstance(evidence, dict):
        return None
    reference, quote = evidence.get('reference'), evidence.get('quote')
    content = case['prompt'] if reference == 'request' else None
    if isinstance(reference, str) and reference in case['files'] and reference in source_reads:
        content = case['files'][reference]
    if content is None or not isinstance(quote, str) or not quote.strip() or quote not in content:
        return None
    return content


def source_declaration_quoted(case, reference, quote):
    """Check authored declaration occurrences for these fixtures, not general syntax."""
    if not isinstance(quote, str) or not isinstance(reference, str):
        return False
    declaration = case.get('source_language_declarations', {}).get(reference)
    if not declaration:
        return False
    content = case['files'][reference]
    span, anchor = declaration['span'], declaration['anchor']
    if content.count(span) != 1 or span.count(anchor) != 1:
        return False
    anchor_start = content.index(span) + span.index(anchor)
    anchor_end = anchor_start + len(anchor)
    # A copied comment can repeat an anchor. Its quote must cover the actual
    # declaration occurrence, rather than merely contain the same characters.
    start = content.find(quote)
    while start != -1:
        if start <= anchor_start and start + len(quote) >= anchor_end:
            return True
        start = content.find(quote, start + 1)
    return False


def target_errors(case, observation, source_reads):
    errors = []
    target = observation.get('affected_target')
    evidence = observation.get('affected_target_evidence')
    if not isinstance(target, dict) or set(target) != set(TARGET_COMPONENTS):
        return ['affected_target: require all six independently recorded components']
    if not isinstance(evidence, dict) or set(evidence) != set(TARGET_COMPONENTS):
        return ['affected_target_evidence: require evidence for all six components']
    for component in TARGET_COMPONENTS:
        expected = case['expected']['affected_target'][component]
        value, citation = target[component], evidence[component]
        if value != expected:
            errors.append(f'affected_target.{component}: expected {expected!r}, got {value!r}')
        if value is None:
            if citation is not None:
                errors.append(f'affected_target_evidence.{component}: unresolved component must have null evidence')
        else:
            support = case.get('target_context', {}).get(component)
            if (not support or not isinstance(citation, dict)
                    or citation.get('reference') != support['reference']
                    or citation_content(case, citation, source_reads) is None
                    or support['anchor'] not in citation.get('quote', '')):
                errors.append(f'affected_target_evidence.{component}: known component needs its independent context citation')
    return errors


def observation_errors(case, observation, source_reads=()):
    """Compare a normalized reply with independently authored expected evidence."""
    errors = []
    if not isinstance(source_reads, (list, tuple)) or any(not isinstance(path, str) for path in source_reads):
        errors.append('source reads must be a list of independently recorded paths')
        source_reads = ()
    for field, expected in case['expected'].items():
        if field == 'affected_target':
            continue
        if field not in observation or observation[field] != expected:
            errors.append(f'{field}: expected {expected!r}, got {observation.get(field)!r}')
    errors.extend(target_errors(case, observation, source_reads))
    basis = observation.get('language_basis')
    evidence = observation.get('language_evidence')
    if basis == 'unresolved':
        if 'language_evidence' not in observation or evidence is not None:
            errors.append('unresolved language must have null evidence')
    elif basis in ('request', 'source'):
        if not isinstance(evidence, dict):
            errors.append('language evidence missing')
        else:
            reference, quote = evidence.get('reference'), evidence.get('quote')
            content = case['prompt'] if basis == 'request' and reference == 'request' else None
            if basis == 'source' and isinstance(reference, str) and reference in case['files'] and reference in source_reads:
                content = case['files'][reference]
            if content is None or not isinstance(quote, str) or not quote.strip() or quote not in content:
                errors.append('language citation absent from request or independently recorded source read')
            # A DSL declaration cannot establish app implementation language.
            if basis == 'source' and isinstance(reference, str) and reference.endswith('.gradle.kts'):
                errors.append('build-script DSL is not app-language evidence')
            if basis == 'source' and not source_declaration_quoted(case, reference, quote):
                errors.append('source citation must include the authored language-bearing declaration')
            language = observation.get('implementation_language')
            if basis == 'request' and (not isinstance(language, str) or not isinstance(quote, str) or language not in quote):
                errors.append('request citation must explicitly name the claimed language')
    else:
        errors.append('invalid language basis')
    return errors


def guidance_errors(mode, lanes, routing_cases=()):
    """Check Markdown relationships/gates only; never infer model compliance."""
    errors = []
    numbered = dict(steps(mode))
    first = numbered.get('1', '')
    if 'references/mobile-lanes.md#lane-evidence' not in first or 'Complete this step' not in first:
        errors.append('mode evidence completion gate')
    preview = numbered.get('3', '')
    if 'lane evidence record' not in preview or 'unresolved fields' not in preview:
        errors.append('preview evidence output')
    record = section(lanes, 'Lane evidence')
    dimensions = ('Platform', 'Implementation language', 'Framework or shared ownership', 'Affected target')
    for dimension in dimensions:
        if not any(line.startswith('| ' + dimension + ' |') for line in record.splitlines()):
            errors.append('missing evidence dimension: ' + dimension)
    guards = ('request-derived', 'before execution', 'build.gradle.kts',
              'build-script DSL', 'Android, Gradle or Pixel', 'iOS or Xcode',
              'source evidence', 'language-specific lane or test runner',
              'build-doctor', 'Scoped source evidence takes precedence')
    for guard in guards:
        if guard not in record:
            errors.append('missing lane guard: ' + guard)
    # Relate authored native-language examples to their own explicit prompt,
    # instead of pinning an entire prompt string.
    for row in section(mode, 'Routing examples').splitlines():
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        if len(cells) != 3:
            continue
        request, _, domain = cells
        if 'Swift/iOS' in domain and 'Swift' not in request:
            errors.append('Swift example lacks request language evidence')
        if 'Kotlin/Android' in domain and 'Kotlin' not in request:
            errors.append('Kotlin example lacks request language evidence')
        if 'KMP shared logic' in domain and 'KMP' not in request:
            errors.append('KMP example lacks request ownership evidence')
    for case in routing_cases:
        language = {'Swift/iOS': 'Swift', 'Kotlin/Android': 'Kotlin'}.get(case['expected_domain'])
        if language and language not in case['prompt']:
            errors.append(f"WP2 {case['id']}: {language} example lacks request language evidence")
    return errors


def check_observations(records, complete_suite=False):
    """Partial by default; complete_suite also checks six unique fixture identities."""
    cases = {case['id']: case for case in json.loads(FIXTURE.read_text())['cases']}
    if not isinstance(records, list):
        return [{'case_id': None, 'errors': ['observations must be a list']}]
    results = []
    for record in records:
        if not isinstance(record, dict):
            results.append({'case_id': None, 'errors': ['invalid observation record']})
            continue
        case_id = record.get('case_id')
        if not isinstance(case_id, str) or case_id not in cases:
            errors = ['unknown fixture case']
        elif not isinstance(record.get('observation'), dict):
            errors = ['missing normalized observation']
        else:
            errors = observation_errors(cases[case_id], record['observation'], record.get('source_reads', []))
        results.append({'case_id': case_id, 'errors': errors})
    if complete_suite:
        ids = [record.get('case_id') for record in records if isinstance(record, dict)]
        missing = sorted(set(cases) - {item for item in ids if isinstance(item, str)})
        duplicate = sorted({item for item in ids if isinstance(item, str) and ids.count(item) > 1})
        errors = []
        if missing:
            errors.append('complete suite missing cases: ' + ', '.join(missing))
        if duplicate:
            errors.append('complete suite duplicate cases: ' + ', '.join(duplicate))
        if len(records) != len(cases):
            errors.append(f'complete suite expected {len(cases)} records, got {len(records)}')
        if errors:
            results.append({'case_id': None, 'errors': errors})
    return results


class LaneEvidence(unittest.TestCase):
    def setUp(self):
        self.cases = {case['id']: case for case in json.loads(FIXTURE.read_text())['cases']}
        self.mode = (ROOT / MODE / 'SKILL.md').read_text()
        self.lanes = (ROOT / MODE / 'references/mobile-lanes.md').read_text()

    def observation(self, case_id, reference=None, quote=None):
        # Construct checker inputs, not fabricated host results.
        reply = copy.deepcopy(self.cases[case_id]['expected'])
        context = self.cases[case_id].get('target_context', {})
        reply['affected_target_evidence'] = {
            component: ({'reference': context[component]['reference'],
                         'quote': context[component]['anchor']} if component in context else None)
            for component in TARGET_COMPONENTS}
        reply['language_evidence'] = None if reference is None else {'reference': reference, 'quote': quote}
        return reply

    def test_static_guidance_has_complete_evidence_gate(self):
        cases = json.loads((ROOT / 'tests/fixtures/wp2-routing-prompts.json').read_text())['cases']
        self.assertEqual(guidance_errors(self.mode, self.lanes, cases), [])

    def test_gate_and_each_dimension_mutations_rejected(self):
        self.assertEqual(guidance_errors(self.mode, self.lanes), [])
        mutated = self.mode.replace('references/mobile-lanes.md#lane-evidence', 'references/mobile-lanes.md')
        self.assertIn('mode evidence completion gate', guidance_errors(mutated, self.lanes))
        mutated = self.mode.replace('lane evidence record', 'domain')
        self.assertIn('preview evidence output', guidance_errors(mutated, self.lanes))
        for dimension in ('Platform', 'Implementation language', 'Framework or shared ownership', 'Affected target'):
            with self.subTest(dimension=dimension):
                mutated = self.lanes.replace('| ' + dimension + ' |', '| omitted |')
                self.assertIn('missing evidence dimension: ' + dimension, guidance_errors(self.mode, mutated))

    def test_example_labels_need_evidence_in_their_own_request(self):
        self.assertEqual(guidance_errors(self.mode, self.lanes), [])
        for phrase, replacement, error in [
                ('the Swift article list', 'the article list', 'Swift example lacks request language evidence'),
                ('Kotlin Android topic screen', 'topic screen', 'Kotlin example lacks request language evidence'),
                ('KMP shared code', 'shared code', 'KMP example lacks request ownership evidence')]:
            with self.subTest(example=phrase):
                self.assertIn(error, guidance_errors(self.mode.replace(phrase, replacement), self.lanes))

    def test_platform_only_unresolved_accepted_and_guessed_language_rejected(self):
        for case_id, guessed in [('android-gradle-only', 'Kotlin'), ('ios-xcode-only', 'Swift')]:
            with self.subTest(case=case_id):
                observation = self.observation(case_id)
                self.assertEqual(observation_errors(self.cases[case_id], observation), [])
                observation['implementation_language'] = guessed
                observation['language_basis'] = 'request'
                observation['language_evidence'] = {'reference': 'request', 'quote': self.cases[case_id]['prompt']}
                errors = observation_errors(self.cases[case_id], observation)
                self.assertTrue(any(error.startswith('implementation_language:') for error in errors))
                self.assertIn('request citation must explicitly name the claimed language', errors)

    def test_request_language_accepted_but_not_repository_verified(self):
        case_id = 'explicit-kotlin-request'
        observation = self.observation(case_id, 'request', 'Kotlin Android')
        self.assertEqual(observation_errors(self.cases[case_id], observation), [])
        observation['language_basis'] = 'source'
        self.assertIn('language_basis: expected \'request\', got \'source\'',
                      observation_errors(self.cases[case_id], observation))

    def test_actual_source_read_citation_required_for_positive_controls(self):
        for case_id in ('scoped-kotlin-source', 'scoped-swift-source', 'gradle-kotlin-dsl-java'):
            case = self.cases[case_id]
            reference = next(path for path in case['files'] if not path.endswith('.gradle.kts'))
            observation = self.observation(case_id, reference, case['files'][reference].strip())
            with self.subTest(case=case_id):
                self.assertEqual(observation_errors(case, observation, [reference]), [])
                self.assertIn('language citation absent from request or independently recorded source read',
                              observation_errors(case, observation))
                observation['language_evidence']['quote'] = 'invented source text'
                self.assertIn('language citation absent from request or independently recorded source read',
                              observation_errors(case, observation, [reference]))

    def test_kotlin_DSL_does_not_override_actual_Java_source(self):
        case_id = 'gradle-kotlin-dsl-java'
        case = self.cases[case_id]
        source = 'app/src/main/java/example/MainActivity.java'
        observation = self.observation(case_id, source, 'public class MainActivity')
        self.assertEqual(observation_errors(case, observation, [source]), [])
        observation.update(implementation_language='Kotlin', lane='Kotlin/Android')
        observation['language_evidence'] = {'reference': 'build.gradle.kts', 'quote': 'plugins { id("com.android.application") }'}
        errors = observation_errors(case, observation, ['build.gradle.kts', source])
        self.assertIn('build-script DSL is not app-language evidence', errors)
        self.assertTrue(any(error.startswith('implementation_language:') for error in errors))

    def test_known_platform_does_not_fill_ownership_target_or_runner(self):
        observation = self.observation('android-gradle-only')
        self.assertEqual(observation_errors(self.cases['android-gradle-only'], observation), [])
        for field, guess in [('framework_or_shared_ownership', 'Jetpack Compose'),
                             ('affected_target', 'app:demoDebug'), ('lane', 'Kotlin/Android')]:
            mutated = copy.deepcopy(observation)
            mutated[field] = guess
            self.assertTrue(any(error.startswith(field + ':') for error in
                                observation_errors(self.cases['android-gradle-only'], mutated)))

    def test_reading_build_file_does_not_substitute_source_receipt(self):
        case = self.cases['gradle-kotlin-dsl-java']
        observation = self.observation(case['id'], 'app/src/main/java/example/MainActivity.java', 'public class MainActivity')
        self.assertIn('language citation absent from request or independently recorded source read',
                      observation_errors(case, observation, ['build.gradle.kts']))

    def test_malformed_language_citations_are_rejected(self):
        case = self.cases['explicit-kotlin-request']
        observation = self.observation(case['id'], 'request', 42)
        self.assertIn('request citation must explicitly name the claimed language',
                      observation_errors(case, observation))
        case = self.cases['scoped-kotlin-source']
        observation = self.observation(case['id'], ['not-a-path'], 'fun text(): String')
        self.assertIn('language citation absent from request or independently recorded source read',
                      observation_errors(case, observation))

    def test_self_report_is_not_a_source_read_receipt(self):
        case = self.cases['scoped-kotlin-source']
        reference = 'app/src/main/kotlin/example/Label.kt'
        observation = self.observation(case['id'], reference, 'fun text(): String')
        self.assertIn('source reads must be a list of independently recorded paths',
                      observation_errors(case, observation, reference))
        self.assertIn('language citation absent from request or independently recorded source read',
                      observation_errors(case, observation, reference))
        self.assertEqual(observation_errors(case, observation, [reference]), [])

    def test_review_partial_destination_preserves_unknown_target_components(self):
        case = self.cases['android-gradle-only']
        observation = self.observation(case['id'])
        observation['affected_target'] = {
            'requested_destination': 'Pixel emulator', 'module': None,
            'source_set': None, 'scheme': None, 'variant': None, 'device_instance': None}
        observation['affected_target_evidence'] = {
            key: ({'reference': 'request', 'quote': 'Pixel emulator'}
                  if key == 'requested_destination' else None)
            for key in observation['affected_target']}
        self.assertEqual(observation_errors(case, observation), [])

    def test_review_neutral_source_quotes_do_not_establish_language(self):
        for case_id in ('gradle-kotlin-dsl-java', 'scoped-kotlin-source', 'scoped-swift-source'):
            case = self.cases[case_id]
            reference = next(path for path in case['files'] if not path.endswith('.gradle.kts'))
            for quote in ('demo', '{', 'example'):
                with self.subTest(case=case_id, quote=quote):
                    observation = self.observation(case_id, reference, quote)
                    self.assertTrue(observation_errors(case, observation, [reference]))

    def test_review_WP2_native_examples_have_request_language(self):
        cases = json.loads((ROOT / 'tests/fixtures/wp2-routing-prompts.json').read_text())['cases']
        for case in cases:
            language = {'Swift/iOS': 'Swift', 'Kotlin/Android': 'Kotlin'}.get(case['expected_domain'])
            if language:
                with self.subTest(case=case['id']):
                    self.assertIn(language, case['prompt'])

    def test_WP2_example_language_removal_is_rejected_by_guidance_contract(self):
        cases = json.loads((ROOT / 'tests/fixtures/wp2-routing-prompts.json').read_text())['cases']
        for case_id in ('resume-ios-fix', 'explain-ios-no-changes'):
            mutated = copy.deepcopy(cases)
            case = next(item for item in mutated if item['id'] == case_id)
            case['prompt'] = case['prompt'].replace('Swift ', '')
            self.assertIn(f'WP2 {case_id}: Swift example lacks request language evidence',
                          guidance_errors(self.mode, self.lanes, mutated))

    def test_partial_targets_reject_guessed_identity_and_missing_context(self):
        for case_id in ('android-gradle-only', 'ios-xcode-only'):
            case = self.cases[case_id]
            observation = self.observation(case_id)
            self.assertEqual(observation_errors(case, observation), [])
            for component, guess in [('module', 'app'), ('source_set', 'main'),
                                     ('scheme', 'App'), ('variant', 'demoDebug'),
                                     ('device_instance', 'emulator-5554')]:
                with self.subTest(case=case_id, component=component):
                    mutated = copy.deepcopy(observation)
                    mutated['affected_target'][component] = guess
                    self.assertTrue(any(error.startswith('affected_target.' + component + ':')
                                        for error in observation_errors(case, mutated)))
            for quote in ('Read-only route preview', 'Android', 42):
                mutated = copy.deepcopy(observation)
                mutated['affected_target_evidence']['requested_destination']['quote'] = quote
                self.assertIn('affected_target_evidence.requested_destination: known component needs its independent context citation',
                              observation_errors(case, mutated))
            mutated = copy.deepcopy(observation)
            mutated['affected_target']['requested_destination'] = None
            self.assertTrue(any(error.startswith('affected_target.requested_destination:')
                                for error in observation_errors(case, mutated)))

    def test_unknown_target_components_need_null_evidence_and_complete_record(self):
        case = self.cases['android-gradle-only']
        observation = self.observation(case['id'])
        observation['affected_target_evidence']['variant'] = {'reference': 'request', 'quote': 'Android'}
        self.assertIn('affected_target_evidence.variant: unresolved component must have null evidence',
                      observation_errors(case, observation))
        observation = self.observation(case['id'])
        del observation['affected_target']['device_instance']
        self.assertIn('affected_target: require all six independently recorded components',
                      observation_errors(case, observation))
        observation = self.observation(case['id'])
        del observation['affected_target_evidence']['device_instance']
        self.assertIn('affected_target_evidence: require evidence for all six components',
                      observation_errors(case, observation))

    def test_known_target_source_context_requires_independent_read(self):
        # A fixture-specific supported target declaration demonstrates the
        # same receipt rule; the shipped six-case fixture has no such target.
        case = copy.deepcopy(self.cases['gradle-kotlin-dsl-java'])
        reference = 'settings.gradle.kts'
        case['files'][reference] = 'include(":app")\n'
        case['expected']['affected_target']['module'] = 'app'
        case['target_context']['module'] = {'reference': reference, 'anchor': 'include(":app")'}
        language_source = 'app/src/main/java/example/MainActivity.java'
        observation = self.observation(case['id'], language_source, 'public class MainActivity')
        observation['affected_target']['module'] = 'app'
        observation['affected_target_evidence']['module'] = {'reference': reference, 'quote': 'include(":app")'}
        self.assertEqual(observation_errors(case, observation, [reference, language_source]), [])
        self.assertIn('affected_target_evidence.module: known component needs its independent context citation',
                      observation_errors(case, observation, [language_source]))

    def test_minimal_and_full_actual_declaration_quotes_accepted(self):
        for case_id in ('gradle-kotlin-dsl-java', 'scoped-kotlin-source', 'scoped-swift-source'):
            case = self.cases[case_id]
            reference, declaration = next(iter(case['source_language_declarations'].items()))
            for quote in (declaration['anchor'], declaration['span'], case['files'][reference].strip()):
                with self.subTest(case=case_id, quote=quote):
                    observation = self.observation(case_id, reference, quote)
                    self.assertEqual(observation_errors(case, observation, [reference]), [])

    def test_generic_class_comments_and_path_tokens_are_not_declaration_quotes(self):
        for case_id in ('gradle-kotlin-dsl-java', 'scoped-kotlin-source', 'scoped-swift-source'):
            case = copy.deepcopy(self.cases[case_id])
            reference, declaration = next(iter(case['source_language_declarations'].items()))
            comment = '// ' + declaration['anchor']
            case['files'][reference] += comment + '\n'
            for quote in (comment, reference, 'package example'):
                with self.subTest(case=case_id, quote=quote):
                    observation = self.observation(case_id, reference, quote)
                    self.assertIn('source citation must include the authored language-bearing declaration',
                                  observation_errors(case, observation, [reference]))
        case = self.cases['scoped-kotlin-source']
        reference = 'app/src/main/kotlin/example/Label.kt'
        observation = self.observation(case['id'], reference, 'class Label')
        self.assertIn('source citation must include the authored language-bearing declaration',
                      observation_errors(case, observation, [reference]))

    def all_records(self):
        records = []
        for case_id, case in self.cases.items():
            if case['expected']['language_basis'] == 'source':
                reference, declaration = next(iter(case['source_language_declarations'].items()))
                observation = self.observation(case_id, reference, declaration['anchor'])
            elif case['expected']['language_basis'] == 'request':
                observation = self.observation(case_id, 'request', 'Kotlin Android')
            else:
                observation = self.observation(case_id)
            records.append({'case_id': case_id, 'observation': observation,
                            'source_reads': list(case['files'])})
        return records

    def test_complete_suite_accepts_six_unique_cases_but_not_subset_or_duplicates(self):
        records = self.all_records()
        self.assertFalse(any(result['errors'] for result in check_observations(records, complete_suite=True)))
        # Partial API remains useful for preserved historical single-case probes.
        self.assertFalse(any(result['errors'] for result in check_observations(records[:1])))
        for partial in ([], records[:1], records[:-1], [records[0]] * 6, records + records[:1]):
            with self.subTest(ids=[record['case_id'] for record in partial]):
                self.assertTrue(any(result['errors'] for result in check_observations(partial, complete_suite=True)))

    def test_complete_suite_rejects_malformed_case_identity(self):
        records = self.all_records()
        records[0]['case_id'] = []
        self.assertIn('unknown fixture case', check_observations(records, complete_suite=True)[0]['errors'])
        self.assertEqual(check_observations({'not': 'a-list'}, complete_suite=True),
                         [{'case_id': None, 'errors': ['observations must be a list']}])

    def test_CLI_complete_suite_flag_and_partial_scope(self):
        with tempfile.TemporaryDirectory(prefix='hstack-lane-checker-') as directory:
            records_path = Path(directory) / 'observations.json'
            records = self.all_records()
            argv = [sys.executable, str(Path(__file__).resolve()), '--check-observations', str(records_path)]
            for supplied, complete, expected_exit in [(records, True, 0),
                                                      (records[:1], False, 0),
                                                      (records[:1], True, 1),
                                                      ([records[0]] * 6, True, 1),
                                                      ([], False, 1)]:
                with self.subTest(count=len(supplied), complete=complete):
                    records_path.write_text(json.dumps(supplied))
                    result = subprocess.run(argv + (['--complete-suite'] if complete else []),
                                            text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
                    self.assertIsInstance(json.loads(result.stdout), list)

    def test_checker_unknown_case_and_missing_fields_rejected(self):
        self.assertEqual(check_observations([{'case_id': 'missing', 'observation': {}}]),
                         [{'case_id': 'missing', 'errors': ['unknown fixture case']}])
        observation = self.observation('android-gradle-only')
        del observation['affected_target']
        self.assertIn('affected_target: require all six independently recorded components',
                      check_observations([{'case_id': 'android-gradle-only', 'observation': observation}])[0]['errors'])


if __name__ == '__main__':
    if '--check-observations' in sys.argv:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--check-observations', type=Path, required=True)
        parser.add_argument('--complete-suite', action='store_true',
                            help='Require exactly one record for each fixture case')
        args = parser.parse_args()
        records = json.loads(args.check_observations.read_text())
        results = check_observations(records, complete_suite=args.complete_suite)
        print(json.dumps(results, indent=2))
        sys.exit(1 if not results or any(result['errors'] for result in results) else 0)
    unittest.main()
