"""Program limits and recovery through the installed command in synthetic consumers."""
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time
import unittest

from test_host_adapters import InstalledFixture


class ProgramControl(InstalledFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.control = self.area / 'owner control'
        self.control.mkdir()
        self.policy = self.control / 'policy.json'
        self.store = self.control / 'progress'
        self.plan = {'schema_version': 1, 'program': 'synthetic-run',
                     'approval_reference': 'owner-confirmed-spec', 'playbook': 'autopilot-stack',
                     'duration_seconds': None, 'units': ['PR1', 'PR2'],
                     'limits': {'owners': 1, 'reviewers': 3, 'helpers': 3, 'depth': 3},
                     'workers': [{'id': 'owner1', 'unit': 'PR1', 'role': 'owner',
                                  'parent': 'coordinator', 'timebox_seconds': None},
                                 {'id': 'owner2', 'unit': 'PR2', 'role': 'owner',
                                  'parent': 'coordinator', 'timebox_seconds': None}],
                     'groups': []}
        self.sequence = 0
        self.save_policy()

    def save_policy(self):
        self.policy.write_text(json.dumps(self.plan) + '\n')
        self.policy_sha = hashlib.sha256(self.policy.read_bytes()).hexdigest()

    def event(self, op, **values):
        self.sequence += 1
        event = self.control / 'event.json'
        event.write_text(json.dumps({'id': 'E' + str(self.sequence), 'op': op, **values}) + '\n')
        return self.bound('run-control', '--policy', self.policy, '--policy-sha256', self.policy_sha,
                          '--store', self.store, '--event', event)

    def ok(self, op, **values):
        result = self.event(op, **values)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_reserved_owner_survives_restart_and_blocks_duplicate_dispatch(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        report = self.ok('status')
        self.assertEqual(report['actors']['O1']['liveness'], 'unknown')
        result = self.event('dispatch', worker='owner2', actor='O2', parent='coordinator')
        self.assertEqual(result.returncode, 2)
        self.assertIn('owner limit', result.stderr)
        self.assertIn('O1', self.ok('status')['actors'])

    def process(self, child=False):
        code = ('import subprocess, sys, time; '
                'p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"]); '
                'print(p.pid, flush=True); time.sleep(120)') if child else 'import time; time.sleep(120)'
        proc = subprocess.Popen([sys.executable, '-c', code], start_new_session=True,
                                stdout=subprocess.PIPE, text=True)
        def cleanup():
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            proc.wait(timeout=5)
            proc.stdout.close()
        self.addCleanup(cleanup)
        if child:
            proc.stdout.readline()
        return proc

    def owner(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        proc = self.process()
        self.ok('attach', actor='O1', pid=proc.pid, native_id=None,
                reference='observed local launch')
        return proc

    def test_local_process_identity_tracks_descendants_after_parent_exit(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        proc = self.process(child=True)
        self.ok('attach', actor='O1', pid=proc.pid, native_id=None, reference='observed launch')
        self.assertEqual(self.ok('status')['actors']['O1']['liveness'], 'live')
        proc.terminate()
        proc.wait(timeout=5)
        self.assertEqual(self.ok('status')['actors']['O1']['liveness'], 'live')
        os.killpg(proc.pid, signal.SIGTERM)
        time.sleep(0.1)
        self.assertEqual(self.ok('status')['actors']['O1']['liveness'], 'dead')

    def panel(self):
        for index in range(1, 4):
            self.plan['workers'].append({'id': 'R' + str(index), 'unit': 'PR1',
                'role': 'reviewer', 'parent': 'owner1', 'timebox_seconds': None})
        self.plan['groups'] = [{'id': 'review', 'members': ['R1', 'R2', 'R3']}]
        self.save_policy()

    def test_required_group_is_reserved_whole_and_cannot_be_silently_reduced(self):
        self.panel()
        self.owner()
        self.assertEqual(self.event('dispatch', worker='R1', actor='only-one', parent='O1').returncode, 2)
        result = self.event('dispatch-group', group='review', round='r1', parent='O1', members=['R1'])
        self.assertEqual(result.returncode, 2)
        report = self.ok('dispatch-group', group='review', round='r1', parent='O1')
        self.assertEqual(report['groups']['review:r1'], ['R1:r1', 'R2:r1', 'R3:r1'])
        self.assertEqual(self.event('dispatch-group', group='review', round='r2', parent='O1').returncode, 2)

    def test_insufficient_reviewer_limit_holds_without_partial_dispatch(self):
        self.panel()
        self.plan['limits']['reviewers'] = 2
        self.save_policy()
        self.owner()
        result = self.event('dispatch-group', group='review', round='r1', parent='O1')
        self.assertEqual(result.returncode, 2)
        self.assertIn('reviewer limit', result.stderr)
        self.assertEqual(set(self.ok('status')['actors']), {'coordinator', 'O1'})

    def test_warning_and_high_percentage_do_not_stop_but_owner_stop_survives_restart(self):
        self.ok('init')
        self.ok('allowance', windows=[{'id': 'weekly', 'used_percent': 99,
            'reset_at': time.time() + 3600}], warning='native warning', reference='host capture')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.ok('stop', reference='owner says stop')
        self.assertTrue(self.ok('status')['stopped'])
        self.assertIn('owner stopped', self.event('dispatch', worker='owner2', actor='O2',
                                               parent='coordinator').stderr)
        self.ok('continue', reference='owner explicitly resumes')
        self.assertFalse(self.ok('status')['stopped'])

    def test_checkpoint_preserves_completed_work_and_does_not_certify_proof(self):
        self.ok('init')
        proof = self.control / 'actual-command.log'
        proof.write_text('synthetic command completed\n')
        self.ok('checkpoint', unit='PR1', status='completed', commit='a' * 40,
                proof_refs=[str(proof)], next_action='continue PR2', reference='observed completion')
        report = self.ok('status')
        self.assertEqual(report['progress']['PR1']['status'], 'completed')
        self.assertIn('unverified', report['proof_verdict'])
        self.assertIn('already completed', self.event('dispatch', worker='owner1', actor='O1',
                                                    parent='coordinator').stderr)
        proof.unlink()
        self.assertEqual(self.ok('status')['missing_proof'], [str(proof)])

    def test_orchestrate_preserves_its_time_cutoff_without_applying_it_to_autopilot(self):
        self.plan.update(playbook='orchestrate', duration_seconds=1)
        self.save_policy()
        self.ok('init')
        time.sleep(0.8)
        self.assertIn('planned-time', self.event('dispatch', worker='owner1', actor='O1', parent='coordinator').stderr)

    def test_autopilot_has_no_new_universal_time_cutoff(self):
        self.plan['duration_seconds'] = 1
        self.save_policy()
        self.ok('init')
        time.sleep(0.8)
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')

    def test_nested_usage_is_not_counted_twice_and_resumed_totals_are_monotonic(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        counts = {'uncached_input_tokens': 100, 'output_tokens': 10,
                  'cache_read_tokens': 40, 'cache_write_tokens': 0}
        self.ok('usage', scope='root-session', covers=['root-session', 'owner-session'],
                actors=['coordinator', 'O1'], counts=counts, reference='whole tree capture')
        counts['uncached_input_tokens'] = 130
        report = self.ok('usage', scope='root-session', covers=['root-session', 'owner-session'],
                actors=['coordinator', 'O1'], counts=counts, reference='resumed cumulative capture')
        self.assertEqual(report['usage_totals']['uncached_input_tokens'], 130)
        self.assertEqual(report['usage_coverage'], 'complete')
        self.assertIn('overlapping', self.event('usage', scope='child-session', covers=['owner-session'],
            actors=['O1'], counts=counts, reference='duplicate child capture').stderr)
        counts['uncached_input_tokens'] = 50
        self.assertIn('regressed', self.event('usage', scope='root-session',
            covers=['root-session', 'owner-session'], actors=['coordinator', 'O1'],
            counts=counts, reference='zeroed crash capture').stderr)

    def test_missing_usage_is_unknown_and_partial_counts_remain_visible(self):
        self.ok('init')
        self.assertEqual(self.ok('status')['usage_coverage'], 'unknown')
        report = self.ok('usage', scope='root', covers=['root'], actors=['coordinator'],
            counts={'uncached_input_tokens': 10, 'output_tokens': None,
                    'cache_read_tokens': None, 'cache_write_tokens': None}, reference='partial capture')
        self.assertEqual(report['usage_coverage'], 'partial')
        self.assertIsNone(report['usage_totals']['output_tokens'])
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')

    def test_device_release_requires_dead_process_and_observed_matching_restoration(self):
        proc = self.owner()
        settings = {'font_scale': 1, 'locale': 'en-US'}
        self.ok('device-acquire', device='synthetic-phone', actor='O1',
                settings=settings, reference='observed baseline')
        result = self.event('device-release', device='synthetic-phone', settings=settings,
                            reference='claimed restore', processes_reference='claimed dead')
        self.assertEqual(result.returncode, 2)
        self.assertIn('live', result.stderr)
        proc.terminate()
        proc.wait(timeout=5)
        result = self.event('device-release', device='synthetic-phone',
                            settings={'font_scale': True, 'locale': 'en-US'},
                            reference='wrong restore', processes_reference='observed processes stopped')
        self.assertEqual(result.returncode, 2)
        self.assertIn('settings', result.stderr)
        self.ok('device-release', device='synthetic-phone', settings=settings,
                reference='observed restored settings', processes_reference='observed processes stopped')
        report = self.ok('finish', actor='O1', outcome='interrupted', reference='inspected interrupted effects')
        self.assertFalse(report['devices'])
        self.assertEqual(report['actors']['O1']['status'], 'interrupted')

    def test_device_reservation_survives_a_live_child_in_a_separate_process_group(self):
        self.plan['workers'].append({'id': 'driver', 'unit': 'PR1', 'role': 'helper',
            'parent': 'owner1', 'timebox_seconds': None})
        self.save_policy()
        parent = self.owner()
        self.ok('dispatch', worker='driver', actor='driver1', parent='O1')
        child = self.process()
        self.ok('attach', actor='driver1', pid=child.pid, native_id=None, reference='actual child launch')
        self.ok('device-acquire', device='phone', actor='O1', settings={'locale': 'en'}, reference='baseline')
        parent.terminate()
        parent.wait(timeout=5)
        result = self.event('device-release', device='phone', settings={'locale': 'en'},
                            reference='restore claim', processes_reference='only parent stopped')
        self.assertEqual(result.returncode, 2)
        self.assertIn('live or uncertain', result.stderr)

    def test_remote_unknown_worker_cannot_be_finished_or_replaced(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.ok('attach', actor='O1', pid=None, native_id='actual-host-worker-id', reference='native launch')
        self.ok('observe', actor='O1', status='unknown', reference='fresh host lookup inconclusive')
        self.assertIn('uncertain', self.event('finish', actor='O1', outcome='interrupted',
                                            reference='attempted reconciliation').stderr)
        self.ok('observe', actor='O1', status='dead', reference='fresh native terminal observation')
        self.ok('finish', actor='O1', outcome='interrupted', reference='inspected actual effects')
        self.ok('dispatch', worker='owner1', actor='replacement', parent='coordinator')

    def test_required_participants_cannot_share_one_native_worker_identity(self):
        self.panel()
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.ok('attach', actor='O1', pid=None, native_id='native-owner', reference='actual launch')
        self.ok('dispatch-group', group='review', round='r1', parent='O1')
        self.ok('attach', actor='R1:r1', pid=None, native_id='same-native-worker', reference='reviewer launch')
        self.assertIn('identity already', self.event('attach', actor='R2:r1', pid=None,
            native_id='same-native-worker', reference='reused launch').stderr)

    def test_runtime_wait_blocks_once_until_completion_and_reports_timeout(self):
        proc = self.owner()
        argv = [sys.executable, str(self.helper), 'run-wait', '--binding', str(self.binding),
                '--policy', str(self.policy), '--policy-sha256', self.policy_sha,
                '--store', str(self.store), '--kind', 'actor', '--target', 'O1', '--timeout', '4']
        waiter = subprocess.Popen(argv, cwd=self.consumer, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        def cleanup_waiter():
            if waiter.poll() is None:
                waiter.kill()
            waiter.communicate(timeout=5)
            waiter.stdout.close()
            waiter.stderr.close()
        self.addCleanup(cleanup_waiter)
        time.sleep(0.2)
        self.assertIsNone(waiter.poll())
        proc.terminate()
        proc.wait(timeout=5)
        stdout, stderr = waiter.communicate(timeout=5)
        self.assertEqual(waiter.returncode, 0, stderr)
        self.assertTrue(json.loads(stdout)['wait_satisfied'])
        report = self.ok('status')
        self.assertEqual(report['actors']['O1']['status'], 'running')
        self.assertIn('owner limit', self.event('dispatch', worker='owner2', actor='O2',
            parent='coordinator').stderr)
        self.ok('finish', actor='O1', outcome='completed', reference='actual process exit and result')
        self.ok('dispatch', worker='owner2', actor='O2', parent='coordinator')
        result = self.bound('run-wait', '--policy', self.policy, '--policy-sha256', self.policy_sha,
            '--store', self.store, '--kind', 'actor', '--target', 'O2', '--timeout', '0.1')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)['wait_satisfied'])

    def test_explicit_limit_override_preserves_workers_and_cannot_change_approved_scope(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        previous = self.policy_sha
        self.plan['limits']['owners'] = 2
        self.plan['approval_reference'] = 'owner explicitly authorizes two owners'
        self.save_policy()
        self.ok('approve-limits', previous_policy_sha256=previous)
        self.ok('dispatch', worker='owner2', actor='O2', parent='coordinator')
        previous = self.policy_sha
        self.plan['units'].append('unapproved-new-feature')
        self.save_policy()
        self.assertIn('scope', self.event('approve-limits', previous_policy_sha256=previous).stderr)

    def test_fresh_pickup_requires_new_remote_observation_without_clearing_stop(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.ok('attach', actor='O1', pid=None, native_id='native-worker', reference='launch')
        self.ok('stop', reference='explicit owner stop')
        report = self.ok('pickup')
        self.assertTrue(report['stopped'])
        self.assertEqual(report['actors']['O1']['liveness'], 'unknown')

    def test_checkpoint_corruption_holds_instead_of_reinitializing_or_resetting_progress(self):
        self.ok('init')
        path = self.store / 'state.json'
        body = path.read_text()
        self.assertIn('"stopped": false', body)
        path.write_text(body.replace('"stopped": false', '"stopped": true', 1))
        self.assertIn('integrity', self.event('status').stderr)
        self.assertEqual(self.event('init').returncode, 2)

    def test_event_replay_is_idempotent_and_changed_replay_is_held(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.sequence -= 1
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.sequence -= 1
        self.assertIn('reused', self.event('dispatch', worker='owner2', actor='O2', parent='coordinator').stderr)

    def test_status_does_not_dump_event_history_or_raw_usage_into_model_context(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        self.ok('observe', actor='O1', status='dead', reference='confirmed failed launch')
        self.ok('finish', actor='O1', outcome='completed', reference='observed terminal effects')
        report = self.ok('status')
        self.assertNotIn('events', report)
        self.assertNotIn('usage', report)
        self.assertEqual(report['record'], str(self.store / 'state.json'))
        self.assertNotIn('O1', report['actors'])
        self.assertEqual(report['actor_counts']['completed'], 1)

    def test_concurrent_dispatch_has_one_owner_and_no_lost_checkpoint(self):
        self.ok('init')
        processes = []
        for index in (1, 2):
            event = self.control / ('concurrent' + str(index) + '.json')
            event.write_text(json.dumps({'id': 'C' + str(index), 'op': 'dispatch',
                'worker': 'owner' + str(index), 'actor': 'O' + str(index), 'parent': 'coordinator'}))
            argv = [sys.executable, str(self.helper), 'run-control', '--binding', str(self.binding),
                    '--policy', str(self.policy), '--policy-sha256', self.policy_sha,
                    '--store', str(self.store), '--event', str(event)]
            processes.append(subprocess.Popen(argv, cwd=self.consumer, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, text=True))
        results = []
        for process in processes:
            process.communicate(timeout=5)
            process.stdout.close()
            process.stderr.close()
            results.append(process.returncode)
        self.assertEqual(sorted(results), [0, 2])
        report = self.ok('status')
        self.assertEqual(len([a for a in report['actors'].values() if a['role'] == 'owner']), 1)

    def test_live_store_lock_blocks_and_process_death_releases_only_store_lock(self):
        self.ok('init')
        code = ('import fcntl, sys, time; f=open(sys.argv[1], "r+"); '
                'fcntl.flock(f, fcntl.LOCK_EX); print("locked", flush=True); time.sleep(120)')
        process = subprocess.Popen([sys.executable, '-c', code, str(self.store / 'run.lock')],
            start_new_session=True, stdout=subprocess.PIPE, text=True)
        self.addCleanup(process.stdout.close)
        self.addCleanup(lambda: process.wait(timeout=5))
        self.addCleanup(lambda: process.terminate() if process.poll() is None else None)
        self.assertEqual(process.stdout.readline().strip(), 'locked')
        self.assertIn('live progress-store writer', self.event('status').stderr)
        process.terminate()
        process.wait(timeout=5)
        self.ok('status')

    def test_changed_policy_or_plugin_holds_and_never_rebinds_automatically(self):
        self.ok('init')
        self.policy.write_text(self.policy.read_text() + ' ')
        self.assertIn('policy changed', self.event('status').stderr)
        self.save_policy()
        installed = self.plugin / 'adapters/runtime/control.py'
        installed.write_text(installed.read_text() + '\nchanged\n')
        self.assertIn('unapproved runtime', self.event('status').stderr)

    def test_invalid_policy_versions_and_limits_fail_closed(self):
        original = json.loads(json.dumps(self.plan))
        for key, value in [('schema_version', True), ('schema_version', 2), ('duration_seconds', float('nan'))]:
            with self.subTest(key=key, value=value):
                self.plan = json.loads(json.dumps(original))
                self.plan[key] = value
                self.save_policy()
                self.assertEqual(self.event('init').returncode, 2)
        self.plan = original
        self.plan['limits']['owners'] = True
        self.save_policy()
        self.assertEqual(self.event('init').returncode, 2)

    def test_duplicate_keys_in_policy_are_not_silently_accepted(self):
        self.policy.write_text(self.policy.read_text().replace('"program":', '"program": "forged", "program":'))
        self.policy_sha = hashlib.sha256(self.policy.read_bytes()).hexdigest()
        self.assertIn('duplicate', self.event('init').stderr)

    def test_event_outside_controller_directory_and_symlink_store_are_held(self):
        event = self.consumer / 'untrusted.json'
        event.write_text('{"id":"E1","op":"init"}')
        result = self.bound('run-control', '--policy', self.policy, '--policy-sha256', self.policy_sha,
                           '--store', self.store, '--event', event)
        self.assertEqual(result.returncode, 2)
        self.store.symlink_to(self.consumer, target_is_directory=True)
        self.assertIn('symlink', self.event('init').stderr)

    def test_parent_traversal_cannot_put_progress_in_a_consumer(self):
        self.store = self.control / '..' / self.consumer.name / 'escaped-progress'
        result = self.event('init')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('protected owner control', result.stderr)
        self.assertFalse((self.consumer / 'escaped-progress').exists())

    def test_parent_traversal_cannot_read_an_external_controller_event(self):
        event = self.control / '..' / self.consumer.name / 'untrusted.json'
        event.write_text('{"id":"E1","op":"init"}')
        result = self.bound('run-control', '--policy', self.policy, '--policy-sha256', self.policy_sha,
                           '--store', self.store, '--event', event)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('protected owner control', result.stderr)
        self.assertFalse(self.store.exists())

    def test_wait_cannot_read_progress_through_parent_traversal(self):
        self.ok('init')
        (self.consumer / 'state.json').write_bytes((self.store / 'state.json').read_bytes())
        result = self.bound('run-wait', '--policy', self.policy, '--policy-sha256', self.policy_sha,
            '--store', self.control / '..' / self.consumer.name,
            '--kind', 'device', '--target', 'unreserved-phone', '--timeout', '0')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('protected owner control', result.stderr)

    def test_usage_gap_prevents_complete_claim_and_independent_sessions_aggregate(self):
        self.ok('init')
        counts = {'uncached_input_tokens': 12, 'output_tokens': 3, 'cache_read_tokens': 20, 'cache_write_tokens': 0}
        self.ok('usage', scope='session1', covers=['session1'], actors=['coordinator'], counts=counts, reference='first capture')
        report = self.ok('usage', scope='session2', covers=['session2'], actors=['coordinator'], counts=counts, reference='new session capture')
        self.assertEqual(report['usage_totals']['output_tokens'], 6)
        report = self.ok('usage-gap', scope='session1', covers=['session1'],
            actors=['coordinator'], reference='crash lost final usage')
        self.assertEqual(report['usage_coverage'], 'partial')
        report = self.ok('usage', scope='session3', covers=['session3'], actors=['coordinator'],
            counts=counts, reference='unrelated fresh session')
        self.assertEqual(report['usage_coverage'], 'partial')
        self.assertTrue(report['usage_gaps'])
        counts['output_tokens'] = 4
        report = self.ok('usage', scope='session1', covers=['session1'], actors=['coordinator'],
            counts=counts, reference='recovered full cumulative counter for interrupted session')
        self.assertEqual(report['usage_coverage'], 'complete')
        self.assertFalse(report['usage_gaps'])

    def test_expired_allowance_is_unknown_without_becoming_a_stop(self):
        self.ok('init')
        report = self.ok('allowance', windows=[{'id': 'weekly', 'used_percent': 100,
            'reset_at': time.time() - 1}], warning=None, reference='expired host snapshot')
        self.assertIsNone(report['allowance']['windows'][0]['used_percent'])
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')

    def test_local_live_process_cannot_be_declared_dead_or_finished(self):
        self.owner()
        self.assertIn('contradicts', self.event('observe', actor='O1', status='dead', reference='false claim').stderr)
        self.assertIn('live or uncertain', self.event('finish', actor='O1', outcome='completed', reference='false completion').stderr)

    def test_replaying_initialization_preserves_prior_stop_and_progress(self):
        self.ok('init')
        self.ok('stop', reference='owner stop')
        self.sequence = 0
        self.assertTrue(self.ok('init')['stopped'])
        self.sequence = 100
        self.assertIn('existing program', self.event('init').stderr)

    def test_declared_standalone_helper_limits_and_cycles_are_checked(self):
        self.plan['workers'].append({'id': 'architect', 'unit': 'PR1', 'role': 'helper',
            'parent': 'owner1', 'timebox_seconds': None})
        self.plan['limits']['helpers'] = 1
        self.save_policy()
        self.owner()
        self.ok('dispatch', worker='architect', actor='A1', parent='O1')
        self.assertIn('helper limit', self.event('dispatch', worker='architect', actor='A2', parent='O1').stderr)

    def test_cyclic_policy_is_rejected_before_dispatch(self):
        self.plan['workers'].append({'id': 'loop', 'unit': 'PR1', 'role': 'helper',
            'parent': 'loop', 'timebox_seconds': None})
        self.save_policy()
        self.assertIn('cyclic', self.event('init').stderr)

    def test_new_program_and_pickup_playbooks_reach_shared_controller_guide(self):
        source = Path(__file__).resolve().parents[1]
        for name in ('autopilot-full', 'autopilot-stack', 'orchestrate', 'pause-safely', 'session-pickup'):
            with self.subTest(name=name):
                body = (source / 'plugin/skills/hugues-mode/playbooks' / (name + '.md')).read_text()
                self.assertIn('program-control.md', body)
        self.assertEqual(self.bound('read-workflow', 'adapters/program-control.md').returncode, 0)

    def test_parent_timebox_blocks_child_dispatch_without_stopping_unrelated_rules(self):
        self.panel()
        self.plan['workers'][0]['timebox_seconds'] = 1
        self.save_policy()
        self.owner()
        time.sleep(1)
        self.assertIn('timebox expired', self.event('dispatch-group', group='review', round='r1', parent='O1').stderr)

    def test_missing_process_and_nonisolated_group_cannot_be_attached(self):
        self.ok('init')
        self.ok('dispatch', worker='owner1', actor='O1', parent='coordinator')
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])
        self.addCleanup(lambda: child.wait(timeout=5))
        self.addCleanup(lambda: child.terminate() if child.poll() is None else None)
        self.assertNotEqual(os.getpgid(child.pid), child.pid)
        for pid in (999999999, child.pid):
            with self.subTest(pid=pid):
                self.assertIn('isolated process group', self.event('attach', actor='O1', pid=pid,
                    native_id=None, reference='invalid launch').stderr)
