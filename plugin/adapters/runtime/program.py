"""Approved program records; consistency checks never substitute for observation."""
import hashlib
import base64
import gzip
import io
import json
from datetime import datetime
from pathlib import Path
import re
import os
import shutil
import struct
import subprocess
import sys
import zlib

from .json_input import load_json


def plain_path(path):
    path = Path(path)
    if not path.is_absolute():
        raise ValueError('absolute record path required')
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise ValueError('symlink in program path')
    return path


def file_bytes(path):
    path = plain_path(path)
    if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('missing or oversized program file: ' + str(path))
    if path.stat().st_nlink != 1:
        raise ValueError('hardlinked program file is not isolated')
    body = path.read_bytes()
    if not body:
        raise ValueError('empty program file: ' + str(path))
    return body


def digest(body):
    return hashlib.sha256(body).hexdigest()


def fingerprint(path):
    """Hash whole builds, including bundle resources; never traverse links."""
    path = plain_path(path)
    entries = [path] if path.is_file() else sorted(path.rglob('*')) if path.is_dir() else []
    receipts, total = [], 0
    if len(entries) > 100000:
        raise ValueError('oversized build inventory')
    for entry in entries:
        plain_path(entry)
        if entry.is_dir():
            continue
        info = entry.stat()
        if not entry.is_file() or info.st_nlink != 1:
            raise ValueError('unsupported or hardlinked build entry')
        total += info.st_size
        if total > 8 * 1024 * 1024 * 1024:
            raise ValueError('oversized build')
        hashed = hashlib.sha256()
        with entry.open('rb') as stream:
            while body := stream.read(1024 * 1024):
                hashed.update(body)
        receipts.append([entry.relative_to(path).as_posix() if path.is_dir() else '',
                         info.st_mode & 0o777, hashed.hexdigest()])
    if not receipts or not total:
        raise ValueError('missing or empty build')
    if path.is_file():
        return receipts[0][2]
    return digest(b'hstack-tree-v1\n' + json.dumps(receipts, separators=(',', ':')).encode())


def decode_design(path):
    """Decode one extracted base64/gzip field to text, without executing it."""
    packed = base64.b64decode(b''.join(file_bytes(path).split()), validate=True)
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        decoded = stream.read(4 * 1024 * 1024 + 1)
    if len(decoded) > 4 * 1024 * 1024:
        raise ValueError('oversized decoded design; inspect a smaller source extract')
    return text(decoded.decode('utf-8'))


def read_record(path):
    return load_json(file_bytes(path).decode('utf-8'))


def fields(row, required, optional=()):
    if (not isinstance(row, dict) or not set(required) <= row.keys()
            or set(row) - set(required) - set(optional)):
        raise ValueError('missing or unknown program fields')


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty program text required')
    return value


def items(value, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError('program list required')
    return value


def sha(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA256 required')


def header(row, required, optional=()):
    fields(row, ['schema_version', 'program', *required], optional)
    if type(row['schema_version']) is not int or row['schema_version'] != 1:
        raise ValueError('unsupported program schema; explicit migration required')
    text(row['program'])


def relative(root, name):
    text(name)
    child = Path(name)
    if child.is_absolute() or '..' in child.parts or '\\' in name:
        raise ValueError('artifact/snapshot must stay within its record directory')
    return root / child


def timestamp(value):
    stamp = datetime.fromisoformat(text(value).replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('timezone required on attempt timestamp')
    return stamp.timestamp()


def source_identity(row):
    fields(row, ['commit', 'dirty_sha256'])
    if not isinstance(row['commit'], str) or not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', row['commit']):
        raise ValueError('source commit required')
    if row['dirty_sha256'] is not None:
        sha(row['dirty_sha256'])


def png(body):
    if not body.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('invalid PNG signature')
    offset, chunks, compressed, expected, stride = 8, [], bytearray(), None, None
    while offset < len(body):
        if len(body) - offset < 12:
            raise ValueError('truncated PNG')
        size = int.from_bytes(body[offset:offset + 4], 'big')
        kind = body[offset + 4:offset + 8]
        end = offset + 12 + size
        if end > len(body):
            raise ValueError('truncated PNG chunk')
        data = body[offset + 8:offset + 8 + size]
        if zlib.crc32(kind + data) != int.from_bytes(body[end - 4:end], 'big'):
            raise ValueError('invalid PNG checksum')
        if kind == b'IHDR':
            if chunks or size != 13:
                raise ValueError('invalid PNG header')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            if not width or not height or width * height > 16000000:
                raise ValueError('unsupported PNG dimensions')
            if depth != 8 or color not in (0, 2, 4, 6) or compression or filtering or interlace:
                raise ValueError('unsupported PNG encoding; inspect/export a supported image')
            stride = 1 + width * {0: 1, 2: 3, 4: 2, 6: 4}[color]
            expected = height * stride
        elif kind == b'IDAT':
            if not chunks or chunks[-1] not in (b'IHDR', b'IDAT', b'PLTE') and b'IDAT' in chunks:
                raise ValueError('invalid PNG image order')
            compressed.extend(data)
        elif kind == b'IEND':
            if size or end != len(body):
                raise ValueError('invalid PNG ending')
        elif kind[0] & 32 == 0 and kind != b'PLTE':
            raise ValueError('unknown critical PNG chunk')
        chunks.append(kind)
        offset = end
    if not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND' or expected is None:
        raise ValueError('incomplete PNG')
    decoder = zlib.decompressobj()
    try:
        pixels = decoder.decompress(bytes(compressed), expected + 1)
    except zlib.error as exc:
        raise ValueError('invalid PNG pixels') from exc
    if len(pixels) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError('incomplete PNG pixels')
    if any(pixels[i] > 4 for i in range(0, expected, stride)):
        raise ValueError('invalid PNG scanline filter')


def artifact_body(body, kind):
    if kind == 'png':
        png(body)
    elif kind in ('text', 'json'):
        decoded = body.decode('utf-8')
        text(decoded)
        if kind == 'json':
            load_json(decoded)
    else:
        raise ValueError('unsupported proof artifact kind')


def approved_record(path, approval_digest):
    sha(approval_digest)
    body = file_bytes(path)
    if digest(body) != approval_digest:
        raise ValueError('approved requirements changed')
    approved = load_json(body.decode('utf-8'))
    header(approved, ['revision', 'approval_reference', 'sources', 'requirements'], ['verification_plan'])
    text(approved['revision'])
    text(approved['approval_reference'])
    source_ids = set()
    has_mobile_plan = False
    for source in items(approved['sources'], True):
        fields(source, ['id', 'snapshot', 'sha256', 'locator'])
        identity = text(source['id'])
        if identity in source_ids:
            raise ValueError('duplicate design source')
        source_ids.add(identity)
        text(source['locator'])
        sha(source['sha256'])
        snapshot = file_bytes(relative(Path(path).parent, source['snapshot']))
        if digest(snapshot) != source['sha256']:
            raise ValueError('approved source snapshot changed')
        if (snapshot.startswith((b'---\n', b'---\r\n'))
                and b'verification_profile' in snapshot.lower()
                and inspect_plan(relative(Path(path).parent, source['snapshot']), '--profile-json')['attempted']):
            has_mobile_plan = True
    requirement_ids, planned = set(), {}
    for requirement in items(approved['requirements'], True):
        fields(requirement, ['id', 'source_ids', 'expected', 'checks'])
        identity = text(requirement['id'])
        if identity in requirement_ids:
            raise ValueError('duplicate requirement')
        requirement_ids.add(identity)
        text(requirement['expected'])
        if not all(text(s) in source_ids for s in items(requirement['source_ids'], True)):
            raise ValueError('unknown requirement source')
        for check in items(requirement['checks'], True):
            fields(check, ['id', 'target', 'actions'])
            identity = text(check['id'])
            if identity in planned:
                raise ValueError('duplicate acceptance check')
            text(check['target'])
            for action in items(check['actions'], True):
                text(action)
            planned[identity] = check
    if has_mobile_plan and 'verification_plan' not in approved:
        raise ValueError('mobile plan requires a verification_plan mapping')
    plan = plan_checks(path, approved, planned) if 'verification_plan' in approved else None
    return approved, planned, plan


def inspect_plan(snapshot, mode):
    """Use the installed parser for profile detection and validated check export."""
    node = shutil.which('node')
    if node is None:
        raise ValueError('Node unavailable; mobile plan proof gate blocked')
    helper = Path(__file__).resolve().parents[2] / 'skills/hugues-mode/scripts/check-plan.mjs'
    result = subprocess.run([node, str(helper), str(snapshot), mode],
                            capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError('invalid verification plan: ' + result.stderr.strip())
    return load_json(result.stdout)


def plan_checks(path, approved, planned):
    """Cross-check the hashed mobile plan using the same installed validator."""
    link = approved['verification_plan']
    fields(link, ['source_id', 'section', 'checks'])
    source = next((s for s in approved['sources'] if s['id'] == text(link['source_id'])), None)
    if source is None:
        raise ValueError('unknown verification plan source')
    manifests = inspect_plan(relative(Path(path).parent, source['snapshot']), '--coverage-json')
    selected = [m for m in manifests if m['section'] == text(link['section'])]
    if len(selected) != 1:
        raise ValueError('verification plan section must exist exactly once')
    checks = {c['id']: c for c in selected[0]['checks']}
    mapping, ids = {}, set()
    for row in items(link['checks']):
        fields(row, ['lane', 'check_id'])
        lane, identity = text(row['lane']), text(row['check_id'])
        if lane in mapping or identity in ids:
            raise ValueError('duplicate plan check mapping')
        mapping[lane] = identity
        ids.add(identity)
    if set(mapping) != set(checks):
        raise ValueError('plan check mapping must include every selected lane')
    for lane, identity in mapping.items():
        declared, accepted = checks[lane], planned.get(identity)
        requirement = next((r for r in approved['requirements']
                            if any(c['id'] == identity for c in r['checks'])), None)
        if (accepted is None or accepted['target'] != declared['target']
                or accepted['actions'] != [declared['action']]
                or requirement['expected'] != declared['expected']
                or link['source_id'] not in requirement['source_ids']):
            raise ValueError('plan check mapping target/actions/pass condition mismatch: ' + lane)
    return {'source_sha256': source['sha256'], 'section': link['section'],
            'live': selected[0]['live'], 'perf': selected[0]['perf'],
            'work_type': selected[0]['workType'], 'checks': link['checks']}


def coordinator_state(path):
    state = read_record(path)
    header(state, ['findings', 'decisions', 'waivers'])
    for rows, required in [(state['findings'], ['id', 'kind', 'description', 'status']),
                           (state['decisions'], ['id', 'question', 'status'])]:
        ids = set()
        for row in items(rows):
            fields(row, required, ['resolution_reference'])
            if text(row['id']) in ids or row['status'] not in ('open', 'resolved'):
                raise ValueError('duplicate or unknown finding/decision')
            ids.add(row['id'])
            for field in required:
                text(row[field])
            if row['status'] == 'resolved':
                text(row.get('resolution_reference'))
    seen = set()
    for waiver in items(state['waivers']):
        fields(waiver, ['check_id', 'approval_reference', 'reason'])
        if text(waiver['check_id']) in seen:
            raise ValueError('duplicate owner waiver')
        seen.add(waiver['check_id'])
        text(waiver['approval_reference'])
        text(waiver['reason'])
    return state


def check(approved_path, approval_digest, candidate_path, record_path, state_path):
    approved, planned_checks, verification_plan = approved_record(approved_path, approval_digest)
    for path in (candidate_path, record_path, state_path):
        if not Path(path).resolve().is_relative_to(Path(approved_path).parent.resolve()):
            raise ValueError('verdict inputs must be inside protected owner control directory')
    candidate = read_record(candidate_path)
    record = read_record(record_path)
    state = coordinator_state(state_path)
    header(candidate, ['requirements', 'source', 'builds'])
    header(record, ['approved_sha256', 'source', 'builder', 'verifier', 'attempts'])
    header(state, ['findings', 'decisions', 'waivers'])
    source_identity(candidate['source'])
    source_identity(record['source'])
    if len({row['program'] for row in (approved, candidate, record, state)}) != 1:
        raise ValueError('program identity mismatch')
    if record['approved_sha256'] != approval_digest:
        raise ValueError('evidence belongs to another approved revision')
    if candidate['requirements'] != approved['requirements']:
        raise ValueError('candidate changed approved requirements')
    if record['source'] != candidate['source']:
        raise ValueError('evidence belongs to another source version')
    if text(record['builder']) == text(record['verifier']):
        raise ValueError('independent verifier required')
    if not isinstance(candidate['builds'], dict):
        raise ValueError('candidate builds required')
    for build in candidate['builds'].values():
        fields(build, ['path', 'sha256'])
        sha(build['sha256'])
        if fingerprint(Path(text(build['path']))) != build['sha256']:
            raise ValueError('candidate build changed')
    seen = set()
    waivers = {}
    for waiver in items(state['waivers']):
        fields(waiver, ['check_id', 'approval_reference', 'reason'])
        if waiver['check_id'] not in planned_checks or waiver['check_id'] in waivers:
            raise ValueError('unknown or duplicate owner waiver')
        text(waiver['approval_reference'])
        text(waiver['reason'])
        waivers[waiver['check_id']] = waiver
    for attempt in items(record['attempts']):
        fields(attempt, ['id', 'check_id', 'target', 'build_sha256', 'started_at', 'finished_at',
                        'actions', 'status', 'actual', 'user_visible', 'artifacts', 'inspection'],
               ['waiver_reference', 'resolution_reference'])
        identity = text(attempt['id'])
        if identity in seen or attempt['check_id'] not in planned_checks:
            raise ValueError('duplicate attempt or unknown acceptance check')
        seen.add(identity)
        start, end = timestamp(attempt['started_at']), timestamp(attempt['finished_at'])
        if start > end:
            raise ValueError('attempt timestamps reversed')
        if attempt['status'] not in ('passed', 'failed', 'untested', 'blocked', 'waived', 'inconclusive'):
            raise ValueError('unknown check outcome')
        if attempt['user_visible'] not in ('works', 'crash', 'error', 'wrong-result', 'unobserved'):
            raise ValueError('unknown user-visible outcome')
        text(attempt['actual'])
        fields(attempt['inspection'], ['reference', 'supports'])
        if type(attempt['inspection']['supports']) is not bool or not isinstance(attempt['inspection']['reference'], str):
            raise ValueError('invalid inspection record')
        if attempt['inspection']['supports']:
            text(attempt['inspection']['reference'])
        for optional in ('resolution_reference', 'waiver_reference'):
            if optional in attempt:
                text(attempt[optional])
        if attempt['status'] in ('untested', 'blocked', 'waived'):
            if (attempt['actions'] or attempt['artifacts'] or attempt['build_sha256'] is not None
                    or attempt['user_visible'] != 'unobserved'):
                raise ValueError('unrun check contains invented execution')
        else:
            sha(attempt['build_sha256'])
            items(attempt['actions'], True)
        if attempt['status'] == 'waived':
            waiver = waivers.get(attempt['check_id'])
            if waiver is None or waiver['approval_reference'] != attempt.get('waiver_reference'):
                raise ValueError('owner waiver missing from coordinator state')
        for artifact in items(attempt['artifacts']):
            fields(artifact, ['path', 'kind', 'sha256', 'attempt_id', 'target', 'build_sha256', 'captured_at'])
            if (artifact['attempt_id'] != identity or artifact['target'] != attempt['target']
                    or artifact['build_sha256'] != attempt['build_sha256']
                    or not start <= timestamp(artifact['captured_at']) <= end):
                raise ValueError('stale or unrelated evidence artifact')
            sha(artifact['sha256'])
            body = file_bytes(relative(Path(record_path).parent, artifact['path']))
            if digest(body) != artifact['sha256']:
                raise ValueError('evidence artifact changed')
            artifact_body(body, artifact['kind'])
    checks = []
    for requirement in approved['requirements']:
        for planned in requirement['checks']:
            attempts = [a for a in record['attempts'] if a['check_id'] == planned['id']]
            if not attempts:
                checks.append({'id': planned['id'], 'requirement_id': requirement['id'],
                               'target': planned['target'], 'expected': requirement['expected'],
                               'status': 'untested', 'actual': 'No attempt recorded',
                               'user_visible': 'unobserved', 'attempts': []})
                continue
            if len({timestamp(a['finished_at']) for a in attempts}) != len(attempts):
                raise ValueError('ambiguous attempt order')
            attempt = max(attempts, key=lambda a: timestamp(a['finished_at']))
            for executed in attempts:
                if executed['target'] != planned['target']:
                    raise ValueError('attempt target/build mismatch')
                if executed['status'] in ('untested', 'blocked', 'waived'):
                    continue
                build = candidate['builds'][planned['target']]
                if executed['build_sha256'] != build['sha256']:
                    raise ValueError('attempt target/build mismatch')
                if executed['actions'] != planned['actions']:
                    raise ValueError('attempt changed the approved actions')
            status = attempt['status']
            if attempt['user_visible'] in ('crash', 'error', 'wrong-result'):
                status = 'failed'
            elif status == 'passed' and (not attempt['artifacts']
                    or attempt['user_visible'] == 'unobserved'
                    or attempt['inspection']['supports'] is not True
                    or not attempt['inspection']['reference']
                    or (any(a['status'] == 'failed' or a['user_visible'] in ('crash', 'error', 'wrong-result')
                            for a in attempts if a is not attempt)
                        and not attempt.get('resolution_reference'))):
                status = 'inconclusive'
            checks.append({'id': planned['id'], 'requirement_id': requirement['id'],
                           'target': planned['target'], 'expected': requirement['expected'],
                           'status': status, 'actual': attempt['actual'],
                           'user_visible': attempt['user_visible'], 'attempts': attempts})
    remaining = [f for f in state['findings'] if f['status'] == 'open']
    decisions = [d for d in state['decisions'] if d['status'] == 'open']
    return {'schema_version': 1, 'program': approved['program'], 'approved_sha256': approval_digest,
            'verification_plan': verification_plan,
            'source': candidate['source'], 'checks': checks, 'remaining_findings': remaining,
            'open_decisions': decisions,
            'missing_proof': [c['id'] for c in checks if c['status'] not in ('passed', 'waived')],
            'ready': bool(checks) and all(c['status'] == 'passed' for c in checks)
                     and not remaining and not decisions,
            'limits': ['Record consistency does not establish artifact meaning or owner approval.']}


def hold(approved_path, record_path, state_path, problem):
    result = {'schema_version': 1, 'ready': False, 'problems': [str(problem)],
              'open_decisions': None, 'remaining_findings': None,
              'reported_outcomes': None, 'missing_proof': None,
              'limits': ['Proof not accepted; reported outcomes are unverified claims. Null lists mean completeness is unknown.']}
    try:
        if not Path(record_path).resolve().is_relative_to(Path(approved_path).parent.resolve()):
            raise ValueError('record outside protected directory')
        record = read_record(record_path)
        rows = items(record.get('attempts'))
        result['reported_outcomes'] = [
            {'check_id': row.get('check_id'), 'target': row.get('target'),
             'actual': row['actual'], 'user_visible': row['user_visible'], 'accepted': False}
            for row in rows if isinstance(row, dict) and isinstance(row.get('actual'), str)
            and row.get('user_visible') in ('works', 'crash', 'error', 'wrong-result', 'unobserved')]
        if len(result['reported_outcomes']) != len(rows):
            result['limits'].append('Some reported outcomes were unreadable; the list is partial.')
    except (ValueError, OSError, KeyError, TypeError):
        pass
    try:
        if not Path(state_path).resolve().is_relative_to(Path(approved_path).parent.resolve()):
            raise ValueError('state outside protected directory')
        state = coordinator_state(state_path)
        for name in ('decisions', 'findings'):
            rows = state[name]
            result['open_decisions' if name == 'decisions' else 'remaining_findings'] = [r for r in rows if r['status'] == 'open']
    except (ValueError, OSError, KeyError, TypeError):
        result['open_decisions'] = result['remaining_findings'] = None
    return result


def worker(approved_path, approval_digest, writable, cwd, command, protected):
    approved_record(approved_path, approval_digest)
    blocked = [Path(approved_path).parent.resolve()]
    blocked.extend(Path(p).resolve(strict=True) for p in protected)
    for path in blocked:
        entries = path.rglob('*') if path.is_dir() else [path]
        if any(p.is_file() and p.stat().st_nlink != 1 for p in entries):
            raise ValueError('hardlinked protected file is not isolated')
    scopes = [Path(p).resolve(strict=True) for p in writable]
    directory = Path(cwd).resolve(strict=True)
    if not scopes or any(not p.is_dir() for p in scopes) or not directory.is_dir():
        raise ValueError('existing writable directories and working directory required')
    if any(p.is_file() and p.stat().st_nlink != 1 for scope in scopes for p in scope.rglob('*')):
        raise ValueError('hardlinked writable file may alias an out-of-scope path')
    if any(p.is_relative_to(b) or b.is_relative_to(p) for p in scopes for b in blocked):
        raise ValueError('writable scope overlaps protected program path')
    if not any(directory.is_relative_to(p) for p in scopes):
        raise ValueError('working directory is outside writable scope')
    argv = list(command)
    if argv and argv[0] == '--':
        argv.pop(0)
    if not argv:
        raise ValueError('worker argv required')
    executable = shutil.which(argv[0])
    if executable is None:
        raise ValueError('worker executable unavailable')
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise ValueError('process write isolation unavailable; use verified native host enforcement')
    profile = '(version 1) (allow default) (deny file-write*)\n'
    for path in scopes:
        profile += '(allow file-write* (subpath ' + json.dumps(str(path)) + '))\n'
    for path in blocked:
        match = 'subpath' if path.is_dir() else 'literal'
        profile += '(deny file-write* (' + match + ' ' + json.dumps(str(path)) + '))\n'
    profile += '(deny file-link)\n'
    return subprocess.run(['/usr/bin/sandbox-exec', '-p', profile, executable, *argv[1:]],
                          cwd=directory, env=dict(os.environ), check=False).returncode
