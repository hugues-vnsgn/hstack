#!/usr/bin/env python3
"""Installed checks and scoped worker execution. No automatic install or cleanup."""
import sys

if __name__ == '__main__' and sys.path:
    del sys.path[0]

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import subprocess

sys.dont_write_bytecode = True
RUNTIME_SHA256 = {
    "__init__.py": "277b071e8e40f0aabb4007e0ae389824708b2bdd5259075623998749da582807",
    "json_input.py": "d162867227d23f2c56b0e391977450ddfb81e1311394646947325581651c5423",
    "activity.py": "5803f97bcc6270bf6d5b5139a68add48a5bb386e05d2d16bed3044a0a223da93",
    "payload.py": "6906fb88bfef6ab9bd3dc55e90c61149fa766911eeb8fd2290164d5d2869569b",
    "program.py": "fe293361d4d5937e9d6246dce476645e1eb8fdde250f64ad0dc33eca3a1ebab9",
    "control.py": "4e116997864db964c1d5007a8bd9d06d63a9b18457e269abcd7403c279347563"
}


def plain_mode(mode):
    # Same rule as runtime.payload.mode_matches for 0o644, which cannot load until verified.
    return not mode & (stat.S_IWOTH | stat.S_IXUSR)


def load_runtime_sources(binding=None):
    directory = Path(__file__).resolve().parent / 'runtime'
    if directory.is_symlink() or {p.name for p in directory.glob('*.py')} != set(RUNTIME_SHA256):
        raise ValueError('unapproved runtime inventory')
    sources = {}
    for filename, expected in RUNTIME_SHA256.items():
        path = directory / filename
        if path.is_symlink() or not path.is_file() or not plain_mode(stat.S_IMODE(path.stat().st_mode)):
            raise ValueError('unsafe runtime file: ' + filename)
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError('unapproved runtime bytes: ' + filename)
        sources[filename] = body
    if binding is not None:
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate binding key')
                result[key] = value
            return result
        recorded = json.loads(binding.read_text(), object_pairs_hook=unique)
        root = directory.parent.parent
        if recorded['plugin_root'] != str(root):
            raise ValueError('approved installation path changed')
        for filename, body in sources.items():
            relative = 'adapters/runtime/' + filename
            if (recorded['adapter_sha256'][relative] != hashlib.sha256(body).hexdigest()
                    or not plain_mode(recorded['adapter_modes'][relative])):
                raise ValueError('bound runtime differs from approved source')
        cli = Path(__file__).resolve()
        if (recorded['adapter_sha256']['adapters/host_tools.py'] != hashlib.sha256(cli.read_bytes()).hexdigest()
                or recorded['adapter_modes']['adapters/host_tools.py'] != stat.S_IMODE(cli.stat().st_mode)):
            raise ValueError('bound bootstrap differs from approved source')
    loaded = {}
    for filename, body in sources.items():
        name = 'runtime' if filename == '__init__.py' else 'runtime.' + Path(filename).stem
        path = directory / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        exec(compile(body, str(path), 'exec'), module.__dict__)
        loaded[name] = module
    return loaded['runtime.activity'], loaded['runtime.payload']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='verb', required=True)
    sub.add_parser('bind', help='Print the installed payload binding for an approved program')
    for verb, operand in [('read-workflow', 'source'), ('plan-check', 'plan'),
                          ('translate-plan', 'plan')]:
        child = sub.add_parser(verb)
        child.add_argument('--binding', type=Path, required=True)
        if verb == 'translate-plan':
            child.add_argument('--markdown', action='store_true',
                               help='Treat text outside inline code as prose, not commands')
        child.add_argument(operand)
    comparison = sub.add_parser('plan-compare')
    comparison.add_argument('--binding', type=Path, required=True)
    for name in ['repo', 'plan', 'section', 'base-sha', 'head-sha']:
        comparison.add_argument('--' + name, required=True)
    comparison.add_argument('--ruling')
    audit = sub.add_parser('worktree-audit')
    audit.add_argument('--binding', type=Path, required=True)
    audit.add_argument('--repo', type=Path, required=True)
    audit.add_argument('--sources', type=Path, required=True)
    audit.add_argument('--pr-snapshot', type=Path)
    audit.add_argument('--base', default='refs/remotes/origin/main')
    proof = sub.add_parser('program-check', help='Check approved requirements and inspected evidence')
    proof.add_argument('--binding', type=Path, required=True)
    proof.add_argument('--approved', type=Path, required=True)
    proof.add_argument('--approval-sha256', required=True)
    proof.add_argument('--candidate', type=Path, required=True)
    proof.add_argument('--record', type=Path, required=True)
    proof.add_argument('--state', type=Path, required=True)
    worker = sub.add_parser('worker-run', help='Execute authorized argv with process write isolation')
    worker.add_argument('--binding', type=Path, required=True)
    worker.add_argument('--approved', type=Path, required=True)
    worker.add_argument('--approval-sha256', required=True)
    worker.add_argument('--writable', type=Path, action='append', required=True)
    worker.add_argument('--protect', type=Path, action='append', default=[])
    worker.add_argument('--cwd', type=Path, required=True)
    worker.add_argument('command', nargs=argparse.REMAINDER)
    for verb in ('artifact-hash', 'decode-design'):
        child = sub.add_parser(verb)
        child.add_argument('--binding', type=Path, required=True)
        child.add_argument('path', type=Path)
    control = sub.add_parser('run-control', help='Check program limits and save controller progress')
    control.add_argument('--binding', type=Path, required=True)
    control.add_argument('--policy', type=Path, required=True)
    control.add_argument('--policy-sha256', required=True)
    control.add_argument('--store', type=Path, required=True)
    control.add_argument('--event', type=Path, required=True)
    waiting = sub.add_parser('run-wait', help='Wait in one process for saved completion or device release')
    waiting.add_argument('--binding', type=Path, required=True)
    waiting.add_argument('--policy', type=Path, required=True)
    waiting.add_argument('--policy-sha256', required=True)
    waiting.add_argument('--store', type=Path, required=True)
    waiting.add_argument('--kind', choices=['actor', 'device'], required=True)
    waiting.add_argument('--target', required=True)
    waiting.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    program = None
    try:
        activity, payload = load_runtime_sources(None if args.verb == 'bind' else args.binding.resolve())
        program = sys.modules['runtime.program']
        if args.verb == 'bind':
            print(json.dumps(payload.bind(root), indent=2))
            return 0
        payload.load_binding(root, args.binding.resolve())
        if args.verb == 'read-workflow':
            sys.stdout.buffer.write(payload.workflow(root, args.source))
        elif args.verb == 'translate-plan':
            print(payload.translate(root, args.binding.resolve(), Path(args.plan).read_text(),
                                    markdown=args.markdown), end='')
        elif args.verb == 'plan-check':
            node = shutil.which('node')
            if not node:
                raise ValueError('Node unavailable; plan validation gate blocked')
            helper = payload.checked_file(root, 'skills/hugues-mode/scripts/check-plan.mjs')
            return subprocess.run([node, str(helper), str(Path(args.plan).resolve())], check=False).returncode
        elif args.verb == 'plan-compare':
            helper = payload.checked_file(root, 'skills/hugues-mode/scripts/compare-plan.py')
            command = [sys.executable, '-I', str(helper)]
            for name in ['repo', 'plan', 'section', 'base-sha', 'head-sha']:
                command.extend(['--' + name, getattr(args, name.replace('-', '_'))])
            if args.ruling:
                command.extend(['--ruling', args.ruling])
            return subprocess.run(command, check=False).returncode
        elif args.verb == 'worktree-audit':
            result = activity.audit(args.repo.resolve(), args.sources, args.pr_snapshot, args.base)
            print(json.dumps(result, indent=2))
            return 0 if result['coverage'] == result['metadata_coverage'] == 'complete' else 2
        elif args.verb == 'program-check':
            result = program.check(args.approved, args.approval_sha256, args.candidate, args.record, args.state)
            print(json.dumps(result, indent=2))
            return 0 if result['ready'] else 2
        elif args.verb == 'worker-run':
            return program.worker(args.approved, args.approval_sha256,
                                  args.writable, args.cwd, args.command, args.protect)
        elif args.verb == 'artifact-hash':
            print(json.dumps({'sha256': program.fingerprint(args.path)}))
        elif args.verb == 'decode-design':
            sys.stdout.write(program.decode_design(args.path))
        elif args.verb == 'run-control':
            result = sys.modules['runtime.control'].control(root, args.binding, args.policy,
                                                          args.policy_sha256, args.store, args.event)
            print(json.dumps(result, indent=2))
        elif args.verb == 'run-wait':
            result = sys.modules['runtime.control'].wait(root, args.binding, args.policy,
                args.policy_sha256, args.store, args.kind, args.target, args.timeout)
            print(json.dumps(result))
            return 0 if result['wait_satisfied'] else 2
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        if args.verb == 'program-check' and program is not None:
            print(json.dumps(program.hold(args.approved, args.record, args.state, exc), indent=2))
        print('host adapter blocked: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
