"""Opt-in native Claude + iOS setup-to-proof check; requires Xcode and Claude auth."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def screenshot_reads(events):
    requests = {}
    inspected = set()
    for event in events:
        for block in event.get('message', {}).get('content', []):
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use' and block.get('name') == 'Read':
                requests[block['id']] = block.get('input', {}).get('file_path')
            if block.get('type') == 'tool_result' and not block.get('is_error'):
                content = block.get('content', [])
                if isinstance(content, list) and any(part.get('type') == 'image' for part in content if isinstance(part, dict)):
                    path = requests.get(block.get('tool_use_id'))
                    if path:
                        inspected.add(Path(path).resolve())
    return inspected


def verify_proofs(paths, events, response):
    assert paths, 'no mobile proof was produced'
    assert response.get('structured_output') == {
        'observed_greeting': 'Hello, Codex!', 'visual_verified': True}, 'visual verification did not pass'
    expected_images = {(path.parent / 'greeting.png').resolve() for path in paths}
    assert expected_images <= screenshot_reads(events), 'host did not inspect every proof screenshot'
    for path in paths:
        receipt = json.loads(path.read_text())
        assert receipt['status'] == 'passed' and receipt['cleanup'] == 'deleted-owned-simulator'
        assert (path.parent / 'greeting.txt').read_text() == 'Hello, Codex!'
        assert (path.parent / 'greeting.png').stat().st_size > 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new external evidence directory')
    parser.add_argument('--plugin', type=Path, default=ROOT / 'plugin')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        parser.error('--output must be a new directory outside the repository')
    for executable in ('claude', 'xcrun', 'xcodegen'):
        if not shutil.which(executable):
            parser.error(executable + ' is required; this check was not run')
    output.mkdir(parents=True)
    plugin = output / 'installed plugin'
    shutil.copytree(args.plugin.resolve(), plugin, ignore=shutil.ignore_patterns('__pycache__'))
    consumer = output / 'consumer'
    shutil.copytree(ROOT / 'tests/fixtures/setup-proof-ios', consumer,
                    ignore=shutil.ignore_patterns('__pycache__'))
    env = dict(os.environ, ISSUE35_EVIDENCE_ROOT=str(output / 'proof'))
    (output / 'claude-version.txt').write_text(subprocess.check_output(['claude', '--version'], text=True))
    (output / 'xcode-version.txt').write_text(subprocess.check_output(['xcodebuild', '-version'], text=True))

    def session(name, prompt, schema=None):
        argv = ['claude', '-p', prompt, '--plugin-dir', str(plugin), '--setting-sources', 'project',
                '--settings', '{"disableAllHooks":true}', '--strict-mcp-config',
                '--mcp-config', '{"mcpServers":{}}', '--tools', 'Read,Write,Edit,Glob,Grep,Bash',
                '--allowedTools', 'Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash(python3 proof.py)',
                '--max-turns', '40', '--no-session-persistence', '--output-format', 'stream-json', '--verbose']
        if schema:
            argv += ['--json-schema', json.dumps(schema)]
        (output / (name + '-command.json')).write_text(json.dumps(argv, indent=2) + '\n')
        with (output / (name + '.jsonl')).open('w') as log:
            result = subprocess.run(argv, cwd=consumer, env=env, stdout=log,
                                    stderr=subprocess.PIPE, text=True, timeout=900)
        (output / (name + '.stderr')).write_text(result.stderr)
        result.check_returncode()
        events = [json.loads(line) for line in (output / (name + '.jsonl')).read_text().splitlines()]
        final = next(event for event in reversed(events) if event.get('type') == 'result')
        if final.get('is_error') or final.get('subtype') != 'success':
            raise RuntimeError(name + ' did not finish successfully; inspect its transcript')
        if final.get('permission_denials'):
            raise RuntimeError(name + ' encountered a permission denial; inspect its transcript')
        return events, final

    schema = {'type': 'object', 'properties': {
        'generation_offered': {'type': 'boolean'}, 'mobile_proof_held': {'type': 'boolean'}},
        'required': ['generation_offered', 'mobile_proof_held'], 'additionalProperties': False}
    _, setup = session('setup', '/hugues-stack:setup-huguesstack '
        'This is an isolated integration consumer. Read its README. Complete model setup with '
        'budget small and inherit-parent medium for every seat, retaining panel cardinalities; '
        'I accept those choices now. Follow step 7 normally, but stop before any offered generation. '
        'Do not drive the app yet. Return whether you offered generation and whether mobile proof '
        'is held, based on your actual actions and the mobile-proof prerequisite.', schema)
    assert (consumer / '.huguesstack/models.md').is_file(), 'setup did not write model config'
    assert not list(consumer.glob('.claude/skills/*/SKILL.md')), 'setup generated before acceptance'
    assert setup.get('structured_output') == {
        'generation_offered': True, 'mobile_proof_held': True}, 'setup skipped the required mobile recipe offer'

    visual_schema = {'type': 'object', 'properties': {
        'observed_greeting': {'type': 'string'}, 'visual_verified': {'type': 'boolean'}},
        'required': ['observed_greeting', 'visual_verified'], 'additionalProperties': False}
    generation_events, generation = session('generate', '/hugues-stack:setup-huguesstack '
        'Continue setup in this isolated consumer. Keep the accepted model choices. '
        'Yes to the verification-skill offer: generate the project recipe using the existing harness '
        'and prove it once under the generator contract. You may write only within this consumer '
        'and ISSUE35_EVIDENCE_ROOT, and may run python3 proof.py. That harness creates and deletes '
        'only its own simulator. Keep the harness and app sources unchanged. Read the README '
        'and inspect the screenshot with Read. Use .claude/skills/ for the recipe. '
        'Do not publish, install dependencies, change settings or use other devices. '
        'Return the text you observed in the screenshot and whether you verified it visually.', visual_schema)
    recipes = list(consumer.glob('.claude/skills/verify-*/SKILL.md'))
    assert len(recipes) == 1, 'expected exactly one project verification recipe'
    match = re.search(r'^name:\s*(verify-[a-z0-9-]+)\s*$', recipes[0].read_text(), re.M)
    assert match, 'generated recipe lacks a native name'
    recipe = match.group(1)
    before = set((output / 'proof').glob('*/result.json'))
    verify_proofs(before, generation_events, generation)
    events, verification = session('verify', '/' + recipe + ' '
        'If this skill is not registered, stop; never read its body as an invocation fallback. '
        'Run the greeting feature once using python3 proof.py, inspect greeting.txt and greeting.png '
        'after cleanup, and report actual results. Authority is limited to this disposable consumer, '
        'ISSUE35_EVIDENCE_ROOT and the harness-owned simulator. Keep app and harness unchanged. '
        'Return the text you observed in the screenshot and whether you verified it visually.', visual_schema)
    init = next(e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init')
    assert recipe in init.get('slash_commands', []), 'fresh host did not discover the project skill'
    after = set((output / 'proof').glob('*/result.json'))
    assert after - before, 'native recipe invocation produced no new proof'
    verify_proofs(after - before, events, verification)
    for filename in ('App.swift', 'GreetingTests.swift', 'proof.py'):
        assert (consumer / filename).read_bytes() == (ROOT / 'tests/fixtures/setup-proof-ios' / filename).read_bytes()
    (output / 'PASS.json').write_text(json.dumps({'recipe': recipe, 'proof_runs': len(after),
        'scope': 'Claude setup, recipe generation, fresh native invocation, iOS greeting proof'}, indent=2) + '\n')
    print('PASS: native setup-to-proof; evidence at', output)


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, RuntimeError, subprocess.SubprocessError) as error:
        print('FAIL:', error, file=sys.stderr)
        sys.exit(1)
