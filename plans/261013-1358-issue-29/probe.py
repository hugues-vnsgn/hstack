"""Observe documented proof-index scope; this does not drive a native handoff."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--evidence', type=Path, required=True)
args = parser.parse_args()
sys.dont_write_bytecode = True
sys.path.insert(0, str(args.source / 'tests'))
from test_program_proof import ProgramProof, digest

args.evidence.mkdir(parents=True, exist_ok=True)
test = ProgramProof(methodName='test_matching_inspected_proof_passes')
test.setUp()
started = time.monotonic()
try:
    rule = 'Before a push starts a round, run: python3 required_project_check.py\n'
    (test.consumer / 'AGENTS.md').write_text(rule)
    command = test.consumer / 'required_project_check.py'
    command.write_text('import sys\nprint("required project check failed")\nsys.exit(7)\n')
    observed = subprocess.run([sys.executable, str(command)], cwd=test.consumer,
                              capture_output=True, text=True)
    (args.evidence / 'required-project-check.log').write_text(observed.stdout + observed.stderr)
    assert observed.returncode == 7, observed

    # Preserve the project instruction as approved source data, without inventing
    # an acceptance entry for it. The API checks indexed requirements, not prose.
    snapshot = test.control / 'project-rules.txt'
    snapshot.write_text(rule)
    approved = json.loads(test.approved.read_text())
    approved['sources'].append({'id': 'project-rules', 'snapshot': snapshot.name,
        'sha256': digest(snapshot), 'locator': 'consumer AGENTS.md required pre-review check'})
    test.write(test.approved, approved)
    test.approval_digest = digest(test.approved)
    test.record['approved_sha256'] = test.approval_digest

    def capture(name):
        result = test.check()
        (args.evidence / (name + '.stdout.json')).write_text(result.stdout)
        (args.evidence / (name + '.stderr.log')).write_text(result.stderr)
        return {'exit_code': result.returncode, 'verdict': json.loads(result.stdout)}

    omitted = capture('01-omitted-project-check')
    assert omitted['exit_code'] == 0 and omitted['verdict']['ready'] is True

    # One data change: explicitly carry the same project requirement into the
    # approved acceptance plan. The existing checker must now detect omission.
    approved['requirements'].append({'id': 'R-PRE', 'source_ids': ['project-rules'],
        'expected': 'Required project pre-review check succeeds on the committed head.',
        'checks': [{'id': 'C-PRE', 'target': 'android',
                    'actions': ['python3 required_project_check.py']}]})
    test.write(test.approved, approved)
    test.approval_digest = digest(test.approved)
    test.record['approved_sha256'] = test.approval_digest
    candidate = json.loads(test.candidate.read_text())
    candidate['requirements'] = approved['requirements']
    test.write(test.candidate, candidate)
    listed = capture('02-listed-unrun-project-check')
    assert listed['exit_code'] == 2 and listed['verdict']['ready'] is False
    assert listed['verdict']['missing_proof'] == ['C-PRE']

    failure = copy.deepcopy(test.record['attempts'][0])
    artifact = test.control / 'attempts/PRE/project-check.log'
    artifact.parent.mkdir(parents=True)
    artifact.write_text(observed.stdout + observed.stderr)
    failure.update(id='PRE', check_id='C-PRE', actions=['python3 required_project_check.py'],
        status='failed', actual='Required project check exited 7.', user_visible='error')
    failure['artifacts'] = [{'path': 'attempts/PRE/project-check.log', 'kind': 'text',
        'sha256': digest(artifact), 'attempt_id': 'PRE', 'target': 'android',
        'build_sha256': digest(test.build), 'captured_at': '2026-10-12T10:00:30Z'}]
    failure['inspection'] = {'reference': 'diagnostic actual command exit 7', 'supports': True}
    test.record['attempts'].append(failure)
    failed = capture('03-listed-failed-project-check')
    assert failed['exit_code'] == 2 and failed['verdict']['ready'] is False

    summary = {'source_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=args.source,
        capture_output=True, text=True, check=True).stdout.strip(),
        'project_check_exit': observed.returncode, 'omitted_check': omitted,
        'listed_unrun_check': listed, 'listed_failed_check': failed,
        'duration_seconds': round(time.monotonic() - started, 3),
        'limits': ['Synthetic evidence-index fixture, not a native agent trial.',
                  'ready describes approved proof only; documented other playbook gates still apply.',
                  'Does not demonstrate lost requirement transfer, invalid handoff acceptance or merge approval.']}
    (args.evidence / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.evidence / 'binding.json').write_bytes(test.binding.read_bytes())
    (args.evidence / 'tested-source-sha256.json').write_text(json.dumps({
        str(p.relative_to(args.source)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [args.source / 'plugin/adapters/runtime/program.py',
                  args.source / 'plugin/adapters/host_tools.py',
                  args.source / 'plugin/adapters/program-proof.md']}, indent=2) + '\n')
    print(json.dumps({'project_check_exit': observed.returncode,
        'omitted_check_ready': omitted['verdict']['ready'],
        'listed_unrun_check_ready': listed['verdict']['ready'],
        'listed_failed_check_ready': failed['verdict']['ready'],
        'duration_seconds': summary['duration_seconds'], 'evidence': str(args.evidence)}))
finally:
    test.doCleanups()
