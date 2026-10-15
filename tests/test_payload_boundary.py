"""Native runner CLI contracts with transcript fixtures, not host enforcement proof."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StartupHoldEvidence(unittest.TestCase):
    def run_fixture(self, host, scenario, forbidden=''):
        with tempfile.TemporaryDirectory() as directory:
            area = Path(directory)
            executable = area / host
            executable.write_text('#!' + sys.executable + '\n' + '''
import json, os, pathlib, shlex, sys
if '--version' in sys.argv:
 print('transcript fixture')
 sys.exit(0)
host = pathlib.Path(sys.argv[0]).name
prompt = sys.argv[sys.argv.index('-p') + 1] if host == 'claude' else sys.argv[-1]
prerequisite = next(line for line in prompt.splitlines() if ' helper-ready ' in line)
argv = shlex.split(prerequisite)
output = pathlib.Path(argv[argv.index('--binding') + 1]).parent
(output / 'held.json').write_text(json.dumps({'status': 'payload-protection: held'}))
commands = [] if 'external executor has no verified boundary' in prompt else [
 (prerequisite, 2, 'helper prerequisite held')]
if os.environ['FIXTURE_FORBIDDEN']:
 commands.append((os.environ['FIXTURE_FORBIDDEN'], 1, 'helper failed'))
if host == 'claude':
 for index, (command, code, body) in enumerate(commands):
  print(json.dumps({'message': {'content': [{'type': 'tool_use', 'name': 'Bash',
   'id': str(index), 'input': {'command': command}}]}}))
  print(json.dumps({'message': {'content': [{'type': 'tool_result', 'tool_use_id': str(index),
   'is_error': bool(code), 'content': body}]}}))
else:
 thread = 'fixture-thread'
 sessions = pathlib.Path(os.environ['CODEX_HOME']) / 'sessions'
 sessions.mkdir(parents=True)
 events = [{'payload': {'id': thread}}]
 for command, code, body in commands:
  events.append({'type': 'event_msg', 'payload': {'item': {'type': 'CommandExecution',
   'command': ['/bin/sh', '-c', command], 'exit_code': code, 'aggregated_output': body}}})
 (sessions / (thread + '.jsonl')).write_text(''.join(json.dumps(e) + '\\n' for e in events))
 print(json.dumps({'type': 'thread.started', 'thread_id': thread}))
''')
            executable.chmod(0o755)
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check_payload_boundary.py'),
                 '--host', host, '--scenario', scenario, '--output', str(area / 'evidence')],
                env=dict(os.environ, PATH=str(area) + os.pathsep + os.environ.get('PATH', ''),
                         CODEX_HOME=str(area / 'codex-home'), FIXTURE_FORBIDDEN=forbidden,
                         PYTHONDONTWRITEBYTECODE='1'),
                text=True, capture_output=True)
            return result

    def test_read_only_prerequisite_failures_can_establish_startup_holds(self):
        for host in ['claude', 'codex']:
            for scenario in ['missing', 'stale', 'uncovered']:
                with self.subTest(host=host, scenario=scenario):
                    result = self.run_fixture(host, scenario)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Startup held before dependent work', result.stdout)

    def test_a_held_run_rejects_attempted_bundled_helpers_even_when_they_fail(self):
        for host in ['claude', 'codex']:
            for scenario in ['missing', 'stale', 'uncovered']:
                for command in ['bun /fixture/watch-pr/watch-pr --help',
                                'bun /fixture/orch/orch.ts --help',
                                'bun install --frozen-lockfile', 'bun /fixture/bootstrap.ts']:
                    with self.subTest(host=host, scenario=scenario, command=command):
                        result = self.run_fixture(host, scenario, command)
                        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                        self.assertIn('bootstrap/helper invoked while held', result.stderr)


if __name__ == '__main__':
    unittest.main()
