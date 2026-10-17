"""Installed acceptance/proof gates in disposable, synthetic consumers."""
import hashlib
import json
import copy
import shutil
import base64
import gzip
import struct
import zlib
from pathlib import Path
import sys
import unittest

from test_host_adapters import InstalledFixture


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProgramProof(InstalledFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.control = self.area / 'owner control'
        self.control.mkdir()
        source = self.control / 'design.txt'
        source.write_text('Remember filters after reopening.\n')
        self.requirements = [{'id': 'R-001', 'source_ids': ['design'],
                              'expected': 'Remember filters after reopening.',
                              'checks': [{'id': 'C-001', 'target': 'android',
                                          'actions': ['choose AIR', 'close', 'reopen']}]}]
        self.approved = self.control / 'approved.json'
        self.write(self.approved, {'schema_version': 1, 'program': 'filters', 'revision': '1',
                   'approval_reference': 'owner-message-51',
                   'sources': [{'id': 'design', 'snapshot': 'design.txt',
                                'sha256': digest(source), 'locator': 'saved filters'}],
                   'requirements': self.requirements})
        self.approval_digest = digest(self.approved)
        self.build = self.consumer / 'app.bin'
        self.build.write_bytes(b'synthetic build one')
        self.candidate = self.control / 'candidate.json'
        self.source_id = {'commit': 'a' * 40, 'dirty_sha256': None}
        self.write(self.candidate, {'schema_version': 1, 'program': 'filters',
                   'requirements': self.requirements, 'source': self.source_id,
                   'builds': {'android': {'path': str(self.build), 'sha256': digest(self.build)}}})
        self.proof = self.control / 'proof.json'
        self.state = self.control / 'state.json'
        self.state_record = {'schema_version': 1, 'program': 'filters',
                             'findings': [], 'decisions': [], 'waivers': []}
        artifact = self.control / 'attempts/A-001/attempt.log'
        artifact.parent.mkdir(parents=True)
        artifact.write_text('AIR selected; closed; reopened; AIR retained.\n')
        self.record = {'schema_version': 1, 'program': 'filters',
                       'approved_sha256': self.approval_digest, 'source': self.source_id,
                       'builder': 'builder-1', 'verifier': 'verifier-2',
                       'attempts': [{'id': 'A-001', 'check_id': 'C-001', 'target': 'android',
                           'build_sha256': digest(self.build),
                           'started_at': '2026-10-12T10:00:00Z', 'finished_at': '2026-10-12T10:01:00Z',
                           'actions': ['choose AIR', 'close', 'reopen'], 'status': 'passed',
                           'actual': 'AIR retained after reopen', 'user_visible': 'works',
                           'artifacts': [{'path': 'attempts/A-001/attempt.log', 'kind': 'text', 'sha256': digest(artifact),
                               'attempt_id': 'A-001', 'target': 'android', 'build_sha256': digest(self.build),
                               'captured_at': '2026-10-12T10:00:30Z'}],
                           'inspection': {'reference': 'independent-tool-observation-1', 'supports': True}}],
                       }
        self.write(self.proof, self.record)
        self.write(self.state, self.state_record)
        self.artifact = artifact

    def write(self, path, data):
        path.write_text(json.dumps(data, indent=2) + '\n')

    def check(self):
        self.write(self.proof, self.record)
        self.write(self.state, self.state_record)
        return self.bound('program-check', '--approved', self.approved,
                          '--approval-sha256', self.approval_digest,
                          '--candidate', self.candidate, '--record', self.proof, '--state', self.state)

    def test_matching_inspected_proof_passes(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['ready'])
        self.assertEqual(report['checks'][0]['status'], 'passed')
        self.assertEqual(report['checks'][0]['expected'], 'Remember filters after reopening.')
        # A quoted example in a design body is not a plan profile.
        source = self.control / 'design.txt'
        source.write_text('Example\nverification_profile: mobile-risk-v1\n')
        approved = json.loads(self.approved.read_text())
        approved['sources'][0]['sha256'] = digest(source)
        self.write(self.approved, approved)
        self.approval_digest = digest(self.approved)
        self.record['approved_sha256'] = self.approval_digest
        self.assertEqual(self.check().returncode, 0)

    def mobile_records(self):
        from test_mobile_coverage import mobile_plan
        plan = self.control / 'mobile-plan.md'
        plan.write_text(mobile_plan())
        approved = json.loads(self.approved.read_text())
        approved['sources'].append({'id': 'mobile-plan', 'snapshot': plan.name,
                                    'sha256': digest(plan), 'locator': 'PR 1'})
        approved['verification_plan'] = {'source_id': 'mobile-plan', 'section': 'PR 1',
            'checks': [{'lane': str(n), 'check_id': f'C-{n:03}'} for n in range(1, 13)]}
        requirements, attempts = [], []
        builds = {}
        for n in range(1, 13):
            target = 'android-debug' if n % 2 else 'ios-debug'
            action = f'background, kill and reopen route {n}'
            requirements.append({'id': f'R-{n:03}', 'source_ids': ['mobile-plan'],
                'expected': f'route {n} and its back navigation restore',
                'checks': [{'id': f'C-{n:03}', 'target': target, 'actions': [action]}]})
            attempt = copy.deepcopy(self.record['attempts'][0])
            attempt.update(id=f'A-{n:03}', check_id=f'C-{n:03}', target=target, actions=[action])
            attempt['artifacts'][0].update(attempt_id=attempt['id'], target=target)
            attempts.append(attempt)
            builds[target] = {'path': str(self.build), 'sha256': digest(self.build)}
        approved['requirements'] = requirements
        self.write(self.approved, approved)
        self.approval_digest = digest(self.approved)
        self.record.update(approved_sha256=self.approval_digest, attempts=attempts)
        candidate = json.loads(self.candidate.read_text())
        candidate.update(requirements=requirements, builds=builds)
        self.write(self.candidate, candidate)
        return approved, candidate

    def test_mobile_plan_checks_are_bound_to_proof_including_extra_lanes(self):
        approved, candidate = self.mobile_records()
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['checks']), 12)
        # Simulate a controller exporting Android only despite the approved plan.
        approved['requirements'] = [r for r in approved['requirements']
                                    if r['checks'][0]['target'] == 'android-debug']
        approved['verification_plan']['checks'] = [r for r in approved['verification_plan']['checks']
                                                   if int(r['lane']) % 2]
        self.write(self.approved, approved)
        self.approval_digest = digest(self.approved)
        candidate['requirements'] = approved['requirements']
        self.write(self.candidate, candidate)
        self.record['approved_sha256'] = self.approval_digest
        self.record['attempts'] = [a for a in self.record['attempts'] if a['target'] == 'android-debug']
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)['ready'])
        self.assertIn('plan check mapping', result.stderr)

    def test_mobile_plan_cannot_relabel_checks_or_omit_selected_proof(self):
        approved, candidate = self.mobile_records()
        for field, value in [('target', 'android'), ('actions', ['skip reopening'])]:
            with self.subTest(field=field):
                changed = copy.deepcopy(approved)
                changed['requirements'][0]['checks'][0][field] = value
                self.write(self.approved, changed)
                self.approval_digest = digest(self.approved)
                self.record['approved_sha256'] = self.approval_digest
                result = self.check()
                self.assertEqual(result.returncode, 2)
                self.assertIn('mapping target/actions/pass condition mismatch', result.stderr)
        changed = copy.deepcopy(approved)
        changed['requirements'][0]['expected'] = 'ignore saved routes'
        self.write(self.approved, changed)
        self.approval_digest = digest(self.approved)
        self.assertIn('mapping target/actions/pass condition mismatch', self.check().stderr)
        changed = copy.deepcopy(approved)
        del changed['verification_plan']
        self.write(self.approved, changed)
        self.approval_digest = digest(self.approved)
        self.assertIn('requires a verification_plan', self.check().stderr)
        plan = self.control / 'mobile-plan.md'
        original = plan.read_text()
        for profile in ['verification_profile: mobile-risk-v1 ',
                        '"verification_profile": mobile-risk-v1',
                        'Verification_profile: mobile-risk-v1',
                        '\u00a0verification_profile: mobile-risk-v1',
                        '\ufeffverification_profile: mobile-risk-v1',
                        'verification_profile\u00e9: mobile-risk-v1',
                        'verification_profile mobile-risk-v1',
                        'verification_profile: unknown']:
            with self.subTest(profile=profile):
                plan.write_text(original.replace('verification_profile: mobile-risk-v1', profile))
                changed['sources'][-1]['sha256'] = digest(plan)
                self.write(self.approved, changed)
                self.approval_digest = digest(self.approved)
                self.record['approved_sha256'] = self.approval_digest
                result = self.check()
                self.assertEqual(result.returncode, 2)
                self.assertIn('requires a verification_plan', result.stderr)
        plan.write_text(original)
        self.write(self.approved, approved)
        self.approval_digest = digest(self.approved)
        self.record['approved_sha256'] = self.approval_digest
        self.record['attempts'] = self.record['attempts'][:-1]
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertIn('C-012', json.loads(result.stdout)['missing_proof'])

    def test_document_plan_records_non_applicability_without_device_passes(self):
        from test_mobile_coverage import document_plan
        plan = self.control / 'mobile-plan.md'
        plan.write_text(document_plan())
        approved = json.loads(self.approved.read_text())
        approved['sources'].append({'id': 'mobile-plan', 'snapshot': plan.name,
                                    'sha256': digest(plan), 'locator': 'PR 1'})
        approved['verification_plan'] = {'source_id': 'mobile-plan', 'section': 'PR 1', 'checks': []}
        self.write(self.approved, approved)
        self.approval_digest = digest(self.approved)
        self.record['approved_sha256'] = self.approval_digest
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['verification_plan']['live'], False)

    def test_no_attempt_is_untested_with_missing_proof(self):
        self.record['attempts'] = []
        result = self.check()
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report['checks'][0]['status'], 'untested')
        self.assertEqual(report['checks'][0]['user_visible'], 'unobserved')
        self.assertEqual(report['missing_proof'], ['C-001'])

    def test_json_proof_and_dirty_source_have_checked_identities(self):
        self.artifact.write_text('{"result":"AIR retained"}\n')
        self.record['attempts'][0]['artifacts'][0].update(kind='json', sha256=digest(self.artifact))
        self.record['source']['dirty_sha256'] = 'd' * 64
        candidate = json.loads(self.candidate.read_text())
        candidate['source'] = self.record['source']
        self.write(self.candidate, candidate)
        self.assertEqual(self.check().returncode, 0)
        self.artifact.write_text('{"result":')
        self.record['attempts'][0]['artifacts'][0]['sha256'] = digest(self.artifact)
        self.assertEqual(self.check().returncode, 2)
        self.artifact.write_text('{"result":"AIR retained"}\n')
        self.record['attempts'][0]['artifacts'][0].update(kind='unsupported', sha256=digest(self.artifact))
        self.assertEqual(self.check().returncode, 2)
        self.record['attempts'][0]['artifacts'][0]['kind'] = 'json'
        self.record['source']['dirty_sha256'] = 'not a digest'
        self.assertEqual(self.check().returncode, 2)

    def test_rejected_independent_inspection_cannot_pass(self):
        self.record['attempts'][0]['inspection']['supports'] = False
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['checks'][0]['status'], 'inconclusive')

    def test_builder_cannot_self_certify(self):
        self.record['verifier'] = self.record['builder']
        self.assertEqual(self.check().returncode, 2)

    def test_crash_is_named_and_fails_even_when_claimed_passed(self):
        self.record['attempts'][0]['user_visible'] = 'crash'
        self.record['attempts'][0]['actual'] = 'Database preserved; process exited to home screen'
        result = self.check()
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report['checks'][0]['status'], 'failed')
        self.assertEqual(report['checks'][0]['user_visible'], 'crash')

    def test_changed_rules_and_changed_approval_are_rejected(self):
        candidate = json.loads(self.candidate.read_text())
        candidate['requirements'][0]['expected'] = 'Reset filters after reopening.'
        self.write(self.candidate, candidate)
        self.assertIn('changed approved requirements', self.check().stderr)
        self.approved.write_text(self.approved.read_text().replace('Remember', 'Reset'))
        self.assertIn('approved requirements changed', self.check().stderr)

    def test_changed_source_snapshot_is_rejected(self):
        (self.control / 'design.txt').write_text('Reset filters after reopening.\n')
        self.assertEqual(self.check().returncode, 2)

    def test_missing_empty_and_whitespace_artifacts_never_pass(self):
        self.artifact.unlink()
        self.assertEqual(self.check().returncode, 2)
        for body in (b'', b' \n\t'):
            with self.subTest(body=body):
                self.artifact.write_bytes(body)
                self.record['attempts'][0]['artifacts'][0]['sha256'] = digest(self.artifact)
                self.assertEqual(self.check().returncode, 2)

    def test_wrong_platform_build_source_or_approval_never_passes(self):
        original = copy.deepcopy(self.record)
        for field, value in [('target', 'ios'), ('build_sha256', 'b' * 64)]:
            with self.subTest(field=field):
                self.record = copy.deepcopy(original)
                self.record['attempts'][0][field] = value
                self.assertEqual(self.check().returncode, 2)
        self.record = copy.deepcopy(original)
        self.record['source']['commit'] = 'b' * 40
        self.assertEqual(self.check().returncode, 2)
        self.record = copy.deepcopy(original)
        self.record['approved_sha256'] = 'b' * 64
        self.assertEqual(self.check().returncode, 2)

    def test_stale_or_unrelated_artifact_association_is_rejected(self):
        original = copy.deepcopy(self.record)
        for field, value in [('attempt_id', 'old-attempt'), ('target', 'ios'),
                             ('build_sha256', 'b' * 64), ('captured_at', '2026-10-11T10:00:30Z')]:
            with self.subTest(field=field):
                self.record = copy.deepcopy(original)
                self.record['attempts'][0]['artifacts'][0][field] = value
                self.assertEqual(self.check().returncode, 2)

    def test_artifacts_cannot_escape_or_follow_symlinks(self):
        outside = self.control / 'unrelated.log'
        outside.write_text('Unrelated old result\n')
        item = self.record['attempts'][0]['artifacts'][0]
        item.update(path=str(outside), sha256=digest(outside))
        self.assertEqual(self.check().returncode, 2)
        item['path'] = '../owner control/unrelated.log'
        self.assertEqual(self.check().returncode, 2)
        item['path'] = 'alias.log'
        (self.control / 'alias.log').symlink_to(outside)
        self.assertEqual(self.check().returncode, 2)

    def test_invalid_image_is_not_proof_even_with_matching_hash(self):
        self.artifact.write_bytes(b'\x89PNG\r\n\x1a\nnot an image')
        self.record['attempts'][0]['artifacts'][0].update(kind='png', sha256=digest(self.artifact))
        self.assertEqual(self.check().returncode, 2)

    def test_decodable_image_passes_but_invalid_scanline_does_not(self):
        def chunk(kind, body):
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
        for filter_byte, expected in ((0, 0), (5, 2)):
            with self.subTest(filter_byte=filter_byte):
                body = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
                        + chunk(b'IDAT', zlib.compress(bytes([filter_byte, 0, 0, 0]))) + chunk(b'IEND', b''))
                self.artifact.write_bytes(body)
                self.record['attempts'][0]['artifacts'][0].update(kind='png', sha256=digest(self.artifact))
                self.assertEqual(self.check().returncode, expected)

    def test_whole_build_bundle_is_bound_including_resources(self):
        bundle = self.consumer / 'Consumer.app'
        bundle.mkdir()
        (bundle / 'executable').write_bytes(b'synthetic executable')
        (bundle / 'Resources').mkdir()
        resource = bundle / 'Resources/content.json'
        resource.write_text('{"content":"one"}\n')
        result = self.bound('artifact-hash', bundle)
        self.assertEqual(result.returncode, 0, result.stderr)
        identity = json.loads(result.stdout)['sha256']
        candidate = json.loads(self.candidate.read_text())
        candidate['builds']['android'] = {'path': str(bundle), 'sha256': identity}
        self.write(self.candidate, candidate)
        attempt = self.record['attempts'][0]
        attempt['build_sha256'] = attempt['artifacts'][0]['build_sha256'] = identity
        self.assertEqual(self.check().returncode, 0)
        resource.write_text('{"content":"changed"}\n')
        self.assertEqual(self.check().returncode, 2)

    def test_build_fingerprint_rejects_links_and_empty_bundles(self):
        bundle = self.consumer / 'empty.app'
        bundle.mkdir()
        self.assertEqual(self.bound('artifact-hash', bundle).returncode, 2)
        (bundle / 'alias').symlink_to(self.build)
        self.assertEqual(self.bound('artifact-hash', bundle).returncode, 2)

    def test_bundled_design_is_decoded_as_bounded_text_without_execution(self):
        packed = self.control / 'prototype.base64'
        content = '<html><script>throw new Error("do not execute")</script>Remember filters</html>'
        packed.write_bytes(base64.b64encode(gzip.compress(content.encode())))
        result = self.bound('decode-design', packed)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), content)
        packed.write_bytes(base64.b64encode(gzip.compress(b'x' * (4 * 1024 * 1024 + 1))))
        self.assertEqual(self.bound('decode-design', packed).returncode, 2)
        packed.write_text('not a valid base64 gzip bundle!')
        self.assertEqual(self.bound('decode-design', packed).returncode, 2)

    def test_malformed_coordinator_state_does_not_hide_unknown_decisions(self):
        self.state_record['decisions'] = [{'id': 'D-1', 'question': 'Missing receipt', 'status': 'resolved'}]
        self.artifact.unlink()
        report = json.loads(self.check().stdout)
        self.assertIsNone(report['open_decisions'])

    def test_ambiguous_retry_order_cannot_choose_a_pass(self):
        earlier = copy.deepcopy(self.record['attempts'][0])
        earlier.update(id='A-002', status='failed', user_visible='error', actual='Read failed')
        earlier['artifacts'][0]['attempt_id'] = 'A-002'
        self.record['attempts'][0]['resolution_reference'] = 'fixed'
        self.record['attempts'].append(earlier)
        self.assertEqual(self.check().returncode, 2)

    def test_unknown_checks_duplicate_attempts_and_bad_times_hold(self):
        original = copy.deepcopy(self.record)
        for edit in ('unknown-check', 'duplicate', 'bad-time', 'reversed-time'):
            with self.subTest(edit=edit):
                self.record = copy.deepcopy(original)
                attempt = self.record['attempts'][0]
                if edit == 'unknown-check':
                    attempt['check_id'] = 'C-unknown'
                elif edit == 'duplicate':
                    self.record['attempts'].append(copy.deepcopy(attempt))
                elif edit == 'bad-time':
                    attempt['started_at'] = 'yesterday'
                else:
                    attempt['finished_at'] = '2026-10-11T10:01:00Z'
                self.assertEqual(self.check().returncode, 2)

    def test_incomplete_inspection_and_zero_artifacts_are_unproven(self):
        self.record['attempts'][0]['inspection']['reference'] = ''
        self.assertEqual(self.check().returncode, 2)
        self.record['attempts'][0]['inspection']['reference'] = 'observed'
        self.record['attempts'][0]['artifacts'] = []
        self.assertEqual(self.check().returncode, 2)

    def test_malformed_inspection_or_resolution_receipts_cannot_clear_failure(self):
        original = copy.deepcopy(self.record)
        for value in ('   ', True, {'claimed': 'receipt'}):
            with self.subTest(reference=value):
                self.record = copy.deepcopy(original)
                self.record['attempts'][0]['inspection']['reference'] = value
                self.assertEqual(self.check().returncode, 2)
                self.record = copy.deepcopy(original)
                earlier = copy.deepcopy(self.record['attempts'][0])
                earlier.update(id='A-000', status='failed', user_visible='crash',
                               started_at='2026-10-12T09:00:00Z', finished_at='2026-10-12T09:01:00Z')
                earlier['artifacts'][0].update(attempt_id='A-000', captured_at='2026-10-12T09:00:30Z')
                self.record['attempts'].insert(0, earlier)
                self.record['attempts'][1]['resolution_reference'] = value
                self.assertEqual(self.check().returncode, 2)

    def test_open_decisions_and_data_anomalies_survive_failed_retry(self):
        self.state_record['decisions'] = [{'id': 'D-1', 'question': 'Which source wins?', 'status': 'open'}]
        self.state_record['findings'] = [{'id': 'F-1', 'kind': 'data-anomaly', 'description': 'Saved value changed unexpectedly', 'status': 'open'}]
        self.record['attempts'][0]['status'] = 'inconclusive'
        result = self.check()
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report['open_decisions'][0]['id'], 'D-1')
        self.assertEqual(report['remaining_findings'][0]['id'], 'F-1')

    def test_boolean_schema_version_is_not_a_supported_version(self):
        self.record['schema_version'] = True
        self.assertEqual(self.check().returncode, 2)

    def test_unrun_blocked_and_waived_checks_are_distinct(self):
        attempt = self.record['attempts'][0]
        attempt.update(artifacts=[], actions=[], build_sha256=None, user_visible='unobserved',
                       inspection={'reference': '', 'supports': False})
        candidate = json.loads(self.candidate.read_text())
        candidate['builds'] = {}
        self.write(self.candidate, candidate)
        for status in ('untested', 'blocked', 'waived'):
            with self.subTest(status=status):
                attempt['status'] = status
                if status == 'waived':
                    attempt['waiver_reference'] = 'owner-message-99'
                    self.state_record['waivers'] = [{'check_id': 'C-001', 'approval_reference': 'owner-message-99', 'reason': 'Owner accepts missing runtime check'}]
                result = self.check()
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)['checks'][0]['status'], status)

    def test_a_self_declared_waiver_cannot_pass(self):
        self.record['attempts'][0]['status'] = 'waived'
        self.record['attempts'][0]['waiver_reference'] = 'made-up-owner'
        self.assertEqual(self.check().returncode, 2)

    def test_all_open_questions_survive_a_passing_proof(self):
        self.state_record['decisions'] = [{'id': f'D-{n}', 'question': f'Question {n}', 'status': 'open'} for n in range(5)]
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(json.loads(result.stdout)['open_decisions']), 5)

    def test_failed_history_cannot_be_hidden_by_a_green_retry(self):
        earlier = copy.deepcopy(self.record['attempts'][0])
        earlier.update(id='A-000', status='failed', actual='Filters reset', user_visible='wrong-result',
                       started_at='2026-10-12T09:00:00Z', finished_at='2026-10-12T09:01:00Z')
        earlier['artifacts'][0].update(attempt_id='A-000', captured_at='2026-10-12T09:00:30Z')
        self.record['attempts'].insert(0, earlier)
        result = self.check()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(json.loads(result.stdout)['checks'][0]['attempts']), 2)
        self.record['attempts'][1]['resolution_reference'] = 'independent-fixed-regression-proof'
        self.assertEqual(self.check().returncode, 0)

    def test_bound_plugin_drift_holds_program_check(self):
        (self.plugin / 'adapters/host.md').write_text('changed plugin')
        self.assertEqual(self.check().returncode, 2)

    def test_duplicate_json_keys_are_rejected(self):
        self.candidate.write_text(self.candidate.read_text().replace('"program": "filters"', '"program": "filters", "program": "other"'))
        self.assertEqual(self.check().returncode, 2)

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('sandbox-exec'), 'macOS isolation unavailable')
    def test_worker_can_write_only_approved_roots(self):
        output = self.consumer / 'allowed.txt'
        result = self.bound('worker-run', '--approved', self.approved,
                            '--approval-sha256', self.approval_digest,
                            '--writable', self.consumer, '--cwd', self.consumer,
                            '--', sys.executable, '-c', 'from pathlib import Path; Path("allowed.txt").write_text("ok")')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text(), 'ok')
        before = self.approved.read_bytes()
        result = self.bound('worker-run', '--approved', self.approved,
                            '--approval-sha256', self.approval_digest,
                            '--writable', self.consumer, '--cwd', self.consumer,
                            '--', sys.executable, '-c',
                            'import sys; from pathlib import Path; Path(sys.argv[1]).write_text("tampered")', self.approved)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.approved.read_bytes(), before)

    def test_worker_scope_may_cover_the_installed_plugin_but_not_the_control_directory(self):
        with self.subTest(scope='owner control directory'):
            before = self.approved.read_bytes()
            result = self.bound('worker-run', '--approved', self.approved,
                                '--approval-sha256', self.approval_digest,
                                '--writable', self.control, '--cwd', self.control,
                                '--', sys.executable, '-c', 'raise SystemExit(0)')
            self.assertEqual(result.returncode, 2)
            self.assertEqual(self.approved.read_bytes(), before)
        with self.subTest(scope='installed plugin root'):
            if not (sys.platform == 'darwin' and shutil.which('sandbox-exec')):
                self.skipTest('macOS isolation unavailable')
            result = self.bound('worker-run', '--approved', self.approved,
                                '--approval-sha256', self.approval_digest,
                                '--writable', self.plugin, '--cwd', self.plugin,
                                '--', sys.executable, '-c',
                                'from pathlib import Path; Path("worker-note.txt").write_text("ok")')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((self.plugin / 'worker-note.txt').read_text(), 'ok')

    def test_worker_invalid_roots_directory_or_command_never_launches(self):
        cases = [(self.build, self.consumer, [sys.executable, '-c', 'raise SystemExit(0)']),
                 (self.consumer, self.control, [sys.executable, '-c', 'raise SystemExit(0)']),
                 (self.consumer, self.consumer, []),
                 (self.consumer, self.consumer, ['hstack-unavailable-worker-8b05'])]
        for writable, cwd, command in cases:
            with self.subTest(writable=writable, cwd=cwd, command=command):
                result = self.bound('worker-run', '--approved', self.approved,
                                    '--approval-sha256', self.approval_digest,
                                    '--writable', writable, '--cwd', cwd, '--', *command)
                self.assertEqual(result.returncode, 2)

    def test_verdict_records_must_be_in_the_protected_control_directory(self):
        self.proof = self.consumer / 'builder-proof.json'
        shutil.copytree(self.control / 'attempts', self.consumer / 'attempts')
        self.assertEqual(self.check().returncode, 2)

    def test_unobserved_user_outcome_cannot_pass(self):
        self.record['attempts'][0]['user_visible'] = 'unobserved'
        self.assertEqual(self.check().returncode, 2)

    def test_invalid_proof_still_lists_every_open_owner_decision(self):
        self.state_record['decisions'] = [{'id': 'D-1', 'question': 'Resolve design conflict?', 'status': 'open'}]
        self.artifact.unlink()
        result = self.check()
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertFalse(report['ready'])
        self.assertEqual(report['open_decisions'][0]['id'], 'D-1')
        self.assertTrue(report['problems'])

    def test_missing_artifact_does_not_erase_a_reported_crash(self):
        self.record['attempts'][0].update(user_visible='crash', actual='App crashed after reopening')
        self.artifact.unlink()
        report = json.loads(self.check().stdout)
        self.assertFalse(report['ready'])
        self.assertEqual(report['reported_outcomes'][0]['user_visible'], 'crash')
        self.assertEqual(report['reported_outcomes'][0]['actual'], 'App crashed after reopening')
        self.assertFalse(report['reported_outcomes'][0]['accepted'])

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('sandbox-exec'), 'macOS isolation unavailable')
    def test_worker_aliases_and_children_cannot_write_protected_files(self):
        scripts = [
            'import os,sys; os.link(sys.argv[1],"alias"); open("alias","w").write("tampered")',
            'import os,sys; os.symlink(sys.argv[1],"alias"); open("alias","w").write("tampered")',
            'import subprocess,sys; raise SystemExit(subprocess.run([sys.executable,"-c","import sys; open(sys.argv[1],\"w\").write(\"tampered\")",sys.argv[1]]).returncode)',
        ]
        for script in scripts:
            with self.subTest(script=script):
                alias = self.consumer / 'alias'
                if alias.is_symlink() or alias.exists():
                    alias.unlink()
                before = self.approved.read_bytes()
                result = self.bound('worker-run', '--approved', self.approved,
                                    '--approval-sha256', self.approval_digest,
                                    '--writable', self.consumer, '--cwd', self.consumer,
                                    '--', sys.executable, '-c', script, self.approved)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.approved.read_bytes(), before)

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('sandbox-exec'), 'macOS isolation unavailable')
    def test_preexisting_hardlink_is_rejected_before_worker_launch(self):
        import os
        os.link(self.approved, self.consumer / 'old-alias')
        result = self.bound('worker-run', '--approved', self.approved,
                            '--approval-sha256', self.approval_digest,
                            '--writable', self.consumer, '--cwd', self.consumer,
                            '--', sys.executable, '-c', 'raise SystemExit(0)')
        self.assertEqual(result.returncode, 2)

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('sandbox-exec'), 'macOS isolation unavailable')
    def test_existing_writable_alias_cannot_modify_an_out_of_scope_file(self):
        import os
        outside = self.area / 'unapproved.txt'
        outside.write_text('Keep this data')
        os.link(outside, self.consumer / 'old-alias')
        result = self.bound('worker-run', '--approved', self.approved,
                            '--approval-sha256', self.approval_digest,
                            '--writable', self.consumer, '--cwd', self.consumer,
                            '--', sys.executable, '-c', 'open("old-alias","w").write("tampered")')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(outside.read_text(), 'Keep this data')

    def test_withdrawn_payload_protection_verbs_are_unknown(self):
        evidence = self.area / 'evidence'
        evidence.mkdir()
        for argv in (['payload-policy', '--host', 'claude', '--consumer', self.consumer,
                      '--evidence', evidence],
                     ['helper-ready']):
            with self.subTest(verb=argv[0]):
                result = self.bound(*argv)
                self.assertEqual(result.returncode, 2)
                self.assertIn('invalid choice', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_required_program_contract_is_reachable_through_installed_workflows(self):
        for path in ('adapters/host.md', 'adapters/host-workers.md',
                     'skills/hugues-mode/playbooks/multi-phase-plan.md',
                     'skills/hugues-mode/playbooks/autopilot-full.md',
                     'skills/hugues-mode/playbooks/autopilot-stack.md',
                     'skills/hugues-mode/playbooks/mobile-proof.md',
                     'skills/hugues-mode/playbooks/opening-a-pr.md'):
            with self.subTest(path=path):
                result = self.bound('read-workflow', path)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('program-proof.md', result.stdout)
        self.assertEqual(self.bound('read-workflow', 'adapters/program-proof.md').returncode, 0)

    def test_new_runtime_cannot_execute_after_installed_module_drift(self):
        module = self.plugin / 'adapters/runtime/program.py'
        sentinel = self.consumer / 'untrusted-ran'
        module.write_text('from pathlib import Path\nPath(' + repr(str(sentinel)) + ').touch()\n')
        self.assertEqual(self.check().returncode, 2)
        self.assertFalse(sentinel.exists())


if __name__ == '__main__':
    unittest.main()
