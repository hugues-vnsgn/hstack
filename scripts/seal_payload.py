import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = {'adapters/runtime/payload.json', 'adapters/runtime/payload.py', 'adapters/host_tools.py'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + '\n'


def seal(root=ROOT, accept=()):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('unsafe repository root')
    root = root.resolve()
    if any(p.is_symlink() for p in root.rglob('*') if '.git' not in p.parts):
        raise ValueError('unsafe repository symlink')
    plugin = root / 'plugin'
    receipt_path = root / 'docs/upstream/consolidation.json'
    receipt = json.loads(receipt_path.read_text())
    for row in receipt['files']:
        name = row['destination']
        if name is None:
            continue
        relative = PurePosixPath(name)
        if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
                or str(relative) != name or not (root / name).is_file()
                or not (root / name).resolve().is_relative_to(root)):
            raise ValueError('unsafe canonical destination')
    # Resealing must not silently approve a changed canonical body: name each reviewed change.
    changed = {row['destination'] for row in receipt['files'] if row['destination']
               and digest(root / row['destination']) != row['destination_sha256']}
    if changed - set(accept):
        raise ValueError('canonical destination changed; review it, then pass --accept: '
                         + ', '.join(sorted(changed - set(accept))))
    for name in ANCHORS | {'adapters/runtime/__init__.py', 'adapters/runtime/json_input.py',
                           'adapters/runtime/activity.py', 'adapters/runtime/program.py'}:
        if stat.S_IMODE((plugin / name).stat().st_mode) != 0o644:
            raise ValueError('unsafe trust anchor/runtime mode: ' + name)
    files = []
    for p in sorted(plugin.rglob('*')):
        name = p.relative_to(plugin).as_posix()
        if '__pycache__' in p.parts:
            continue
        if p.is_symlink() or not (p.is_file() or p.is_dir()):
            raise ValueError('unsafe installed entry: ' + name)
        if p.is_file() and name not in ANCHORS:
            files.append({'path': name, 'sha256': digest(p),
                          'mode': '100' + format(stat.S_IMODE(p.stat().st_mode), '03o')})
    legacy = {r['source']: r['destination'].removeprefix('plugin/') for r in receipt['files']
              if r['destination'] and r['destination'].startswith('plugin/')}
    manifest = plugin / 'adapters/runtime/payload.json'
    manifest.write_text(encode({'schema_version': 2, 'revision': 'hstack-native-v1',
        'upstream_revision': receipt['upstream_revision'], 'legacy_paths': legacy, 'files': files}))
    payload = plugin / 'adapters/runtime/payload.py'
    payload.write_text(re.sub(r"MANIFEST_SHA256 = '[^']+'", "MANIFEST_SHA256 = '" + digest(manifest) + "'", payload.read_text()))
    bootstrap = plugin / 'adapters/host_tools.py'
    hashes = {name: digest(plugin / 'adapters/runtime' / name)
              for name in ['__init__.py', 'json_input.py', 'activity.py', 'payload.py', 'program.py']}
    bootstrap.write_text(re.sub(r'RUNTIME_SHA256 = \{.*?\n\}', 'RUNTIME_SHA256 = ' + json.dumps(hashes, indent=4), bootstrap.read_text(), flags=re.S))
    for row in receipt['files']:
        if row['destination']:
            row['destination_sha256'] = digest(root / row['destination'])
    receipt['installed_files'] = {p.relative_to(plugin).as_posix():
        {'sha256': digest(p), 'mode': stat.S_IMODE(p.stat().st_mode)}
        for p in sorted(plugin.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    receipt_path.write_text(encode(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seal the installed payload manifest and receipts.')
    parser.add_argument('--accept', action='append', default=[], metavar='DESTINATION',
                        help='repository path of a reviewed canonical change; repeat per file')
    seal(accept=parser.parse_args().accept)
