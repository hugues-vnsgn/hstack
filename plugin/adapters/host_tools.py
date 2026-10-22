#!/usr/bin/env python3
"""Read-only host mechanics. No network, package bootstrap or deletion actions."""
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
    "payload.py": "7cc5f6fe15ed8ddd1083228cb0805f723d1290cbcedfbb5463add5e8f50aa14c"
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
    audit = sub.add_parser('worktree-audit')
    audit.add_argument('--binding', type=Path, required=True)
    audit.add_argument('--repo', type=Path, required=True)
    audit.add_argument('--sources', type=Path, required=True)
    audit.add_argument('--pr-snapshot', type=Path)
    audit.add_argument('--base', default='refs/remotes/origin/main')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        activity, payload = load_runtime_sources(None if args.verb == 'bind' else args.binding.resolve())
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
            commit = None
            try:
                subprocess.run(['git', '-C', str(root), 'ls-files', '--error-unmatch', str(helper)],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                        check=True, capture_output=True, text=True).stdout.strip()
            except (OSError, subprocess.CalledProcessError):
                pass
            print(json.dumps({'checker_path': str(helper),
                              'checker_sha256': hashlib.sha256(helper.read_bytes()).hexdigest(),
                              'payload_sha256': payload.MANIFEST_SHA256,
                              'plugin_commit': commit}), file=sys.stderr, flush=True)
            return subprocess.run([node, str(helper), str(Path(args.plan).resolve())], check=False).returncode
        elif args.verb == 'worktree-audit':
            result = activity.audit(args.repo.resolve(), args.sources, args.pr_snapshot, args.base)
            print(json.dumps(result, indent=2))
            return 0 if result['coverage'] == result['metadata_coverage'] == 'complete' else 2
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        print('host adapter blocked: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
