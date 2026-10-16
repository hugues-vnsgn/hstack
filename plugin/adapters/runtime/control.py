"""Controller-owned program scheduling and durable recovery; no native tool dispatch."""
from contextlib import contextmanager
import json
import math
import os
import re
import stat
import subprocess
from pathlib import Path
import tempfile
import time

try:
    import fcntl
except ImportError:
    fcntl = None

from .program import digest, fields, file_bytes, items, plain_path, read_record, sha, text
from .payload import load_binding

COUNTS = ('uncached_input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens')


def encode(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError('invalid program limit/count')
    return value


def policy(path, expected):
    sha(expected)
    if digest(file_bytes(path)) != expected:
        raise ValueError('approved run policy changed')
    row = read_record(path)
    fields(row, ['schema_version', 'program', 'approval_reference', 'playbook',
                 'duration_seconds', 'units', 'limits', 'workers', 'groups'])
    if type(row['schema_version']) is not int or row['schema_version'] != 1:
        raise ValueError('unsupported run policy schema')
    text(row['program'])
    text(row['approval_reference'])
    if row['playbook'] not in ('autopilot-full', 'autopilot-stack', 'orchestrate'):
        raise ValueError('unsupported program playbook')
    fields(row['limits'], ['owners', 'reviewers', 'helpers', 'depth'])
    for key, limit in row['limits'].items():
        integer(limit, 1 if key in ('owners', 'depth') else 0)
    if row['duration_seconds'] is not None:
        integer(row['duration_seconds'], 1)
    if row['playbook'] == 'orchestrate' and row['duration_seconds'] is None:
        raise ValueError('orchestrate needs its planned duration')
    if row['playbook'] == 'orchestrate' and row['limits']['depth'] > 3:
        raise ValueError('orchestrate preserves its three-level nesting limit')
    units = items(row['units'], True)
    if len(set(map(text, units))) != len(units):
        raise ValueError('duplicate approved unit')
    workers = {}
    for worker in items(row['workers']):
        fields(worker, ['id', 'unit', 'role', 'parent', 'timebox_seconds'])
        name = text(worker['id'])
        if name == 'coordinator' or name in workers or worker['unit'] not in units:
            raise ValueError('duplicate or unapproved worker/unit')
        if worker['role'] not in ('owner', 'reviewer', 'helper'):
            raise ValueError('unknown worker role')
        text(worker['parent'])
        if worker['timebox_seconds'] is not None:
            integer(worker['timebox_seconds'], 1)
        workers[name] = worker
    grouped = set()
    groups = {}
    for group in items(row['groups']):
        fields(group, ['id', 'members'])
        name = text(group['id'])
        members = items(group['members'], True)
        if name in groups or len(set(map(text, members))) != len(members):
            raise ValueError('duplicate required group')
        if any(m not in workers or workers[m]['role'] == 'owner' or m in grouped for m in members):
            raise ValueError('invalid required group member')
        if len({(workers[m]['parent'], workers[m]['unit']) for m in members}) != 1:
            raise ValueError('required group must share parent and unit')
        grouped.update(members)
        groups[name] = group
    for worker in workers.values():
        parent = worker['parent']
        if worker['role'] == 'owner' and parent != 'coordinator':
            raise ValueError('owner must belong to coordinator')
        if parent != 'coordinator' and (parent not in workers or workers[parent]['unit'] != worker['unit']):
            raise ValueError('missing or cross-unit parent')
        seen, cursor = set(), worker['id']
        while cursor != 'coordinator':
            if cursor in seen:
                raise ValueError('cyclic worker tree')
            seen.add(cursor)
            cursor = workers[cursor]['parent']
        if len(seen) >= row['limits']['depth']:
            raise ValueError('worker exceeds approved nesting depth')
        if worker['role'] == 'reviewer' and worker['id'] not in grouped:
            raise ValueError('reviewer must belong to a complete group')
    return row, workers, groups, grouped


@contextmanager
def transaction(store):
    if fcntl is None:
        raise ValueError('process-safe store locking unavailable')
    plain_path(store)
    store.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = plain_path(store / 'run.lock')
    descriptor = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode) or os.fstat(descriptor).st_nlink != 1:
            raise ValueError('hardlinked store lock')
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('live progress-store writer; retry through runtime waiting') from exc
        yield
    finally:
        os.close(descriptor)


def save(path, state):
    plain_path(path)
    if path.exists():
        file_bytes(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.checkpoint-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(encode({'state': state, 'sha256': digest(encode(state))}))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def active(actor):
    return actor['status'] in ('reserved', 'running')


def read_state(path):
    record = read_record(path)
    fields(record, ['state', 'sha256'])
    if digest(encode(record['state'])) != record['sha256']:
        raise ValueError('checkpoint integrity mismatch; preserve damaged record for review')
    state = record['state']
    if type(state['schema_version']) is not int or state['schema_version'] != 1 or type(state['stopped']) is not bool:
        raise ValueError('invalid checkpoint schema/state')
    return state


def policy_shape(plan):
    return digest(encode({key: value for key, value in plan.items()
                          if key not in ('limits', 'duration_seconds', 'approval_reference')}))


def process_birth(pid):
    result = subprocess.run(['/bin/ps', '-p', str(pid), '-o', 'lstart='],
                            capture_output=True, text=True, timeout=5)
    return result.stdout.strip() if result.returncode == 0 else None


def liveness(actor):
    identity = actor.get('process')
    if identity is None:
        return actor.get('observation', {}).get('status', 'unknown')
    try:
        result = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid=,stat='],
                                capture_output=True, text=True, timeout=5)
        if result.returncode:
            return 'unknown'
        live = []
        for line in result.stdout.splitlines():
            pid, group, status = line.split()
            if int(group) == identity['pid'] and not status.startswith('Z'):
                live.append(int(pid))
        if not live:
            return 'dead'
        birth = process_birth(identity['pid'])
        if birth is not None and birth != identity['birth']:
            return 'unknown'
        return 'live'
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return 'unknown'


def device_liveness(state, owner):
    relevant = {owner}
    while True:
        children = {name for name, actor in state['actors'].items()
                    if active(actor) and actor['parent'] in relevant}
        if children <= relevant:
            break
        relevant.update(children)
    statuses = {liveness(state['actors'][name]) for name in relevant}
    return 'live' if 'live' in statuses else 'unknown' if 'unknown' in statuses else 'dead'


def report(state, focus=None):
    result = json.loads(encode(state))
    for key in ('events', 'usage', 'restoration', 'policy_shape', 'approvals'):
        result.pop(key, None)
    result['actor_counts'] = {status: sum(a['status'] == status for a in state['actors'].values())
                              for status in ('reserved', 'running', 'completed', 'interrupted')}
    result['actors'] = {name: actor for name, actor in result['actors'].items() if active(actor) or name == focus}
    result['groups'] = {name: members for name, members in result['groups'].items()
                        if any(active(state['actors'][member]) for member in members)}
    for actor in result['actors'].values():
        actor['liveness'] = liveness(actor)
    result['proof_verdict'] = 'unverified; use program-check for proof'
    covered = {a for row in state['usage'].values() for a in row['actors']}
    result['usage_missing_actors'] = sorted(set(state['actors']) - covered)
    result['usage_totals'] = {key: (sum(row['counts'][key] for row in state['usage'].values())
        if state['usage'] and all(row['counts'][key] is not None for row in state['usage'].values()) else None)
        for key in COUNTS}
    result['usage_coverage'] = ('unknown' if not state['usage'] else 'partial'
        if result['usage_missing_actors'] or state.get('usage_gaps')
        or any(value is None for value in result['usage_totals'].values()) else 'complete')
    result['usage_basis'] = 'recorded snapshots; not current account allowance or verified cost'
    result['missing_proof'] = []
    for progress in state['progress'].values():
        for reference in progress['proof_refs']:
            try:
                file_bytes(reference)
            except (ValueError, OSError):
                result['missing_proof'].append(reference)
    if result['allowance'] is not None:
        for window in result['allowance']['windows']:
            if window['reset_at'] is not None and window['reset_at'] <= time.time():
                window['used_percent'] = None
    result['allowance_basis'] = 'captured host snapshot, unknown if absent; no quota forecast'
    return result


def counts(row):
    fields(row, COUNTS)
    for value in row.values():
        if value is not None:
            integer(value)


def record_usage(state, event):
    fields(event, ['id', 'op', 'scope', 'covers', 'actors', 'counts', 'reference'])
    scope = text(event['scope'])
    text(event['reference'])
    covers = items(event['covers'], True)
    actors = items(event['actors'], True)
    if len(set(map(text, covers))) != len(covers) or len(set(map(text, actors))) != len(actors):
        raise ValueError('duplicate usage coverage')
    if any(actor not in state['actors'] for actor in actors):
        raise ValueError('unregistered actor in usage')
    counts(event['counts'])
    for other, row in state['usage'].items():
        if other != scope and set(covers) & set(row['covers']):
            raise ValueError('overlapping usage; choose one authoritative tree or disjoint sessions')
    previous = state['usage'].get(scope)
    if previous:
        if not set(previous['covers']) <= set(covers) or not set(previous['actors']) <= set(actors):
            raise ValueError('usage coverage regressed')
        for key, old in previous['counts'].items():
            if old is not None and (event['counts'][key] is None or event['counts'][key] < old):
                raise ValueError('cumulative usage regressed; keep prior counts and report the gap')
    state['usage'][scope] = {key: event[key] for key in ('covers', 'actors', 'counts', 'reference')}
    if all(value is not None for value in event['counts'].values()):
        for name, gap in list(state.get('usage_gaps', {}).items()):
            if gap['scope'] == scope and set(gap['covers']) <= set(covers) and set(gap['actors']) <= set(actors):
                del state['usage_gaps'][name]


def dispatch(plan, workers, state, worker_id, name, parent_id):
    worker = workers[worker_id]
    text(name)
    parent = state['actors'][parent_id]
    if state['stopped']:
        raise ValueError('owner stopped program')
    if name in state['actors'] or parent['worker'] != worker['parent']:
        raise ValueError('duplicate actor or wrong parent')
    if not active(parent) or (parent_id != 'coordinator' and liveness(parent) != 'live'):
        raise ValueError('parent state uncertain or inactive')
    if state['progress'].get(worker['unit'], {}).get('status') == 'completed':
        raise ValueError('unit already completed; inspect saved progress')
    if worker['role'] == 'owner' and any(state['actors'][lease['actor']]['unit'] == worker['unit']
                                        for lease in state['devices'].values()):
        raise ValueError('unit device needs restoration before further dispatch')
    count = sum(active(a) and a['role'] == worker['role'] for a in state['actors'].values())
    key = {'owner': 'owners', 'reviewer': 'reviewers', 'helper': 'helpers'}[worker['role']]
    if count >= plan['limits'][key]:
        raise ValueError(worker['role'] + ' limit reached')
    if worker['role'] == 'owner' and any(active(a) and a['unit'] == worker['unit'] for a in state['actors'].values()):
        raise ValueError('unit has unreconciled workers; avoid duplicate work')
    now = time.time()
    if plan['playbook'] == 'orchestrate' and now - state['started_at'] >= 0.7 * plan['duration_seconds']:
        raise ValueError('orchestrate planned-time spawn cutoff reached')
    ancestor = parent_id
    while ancestor != 'coordinator':
        actor = state['actors'][ancestor]
        limit = workers[actor['worker']]['timebox_seconds']
        if limit is not None and now - actor['reserved_at'] >= limit:
            raise ValueError('parent timebox expired; return partial findings')
        ancestor = actor['parent']
    state['actors'][name] = {'worker': worker_id, 'unit': worker['unit'], 'role': worker['role'],
                            'status': 'reserved', 'parent': parent_id, 'reserved_at': now}


def apply(plan, workers, groups, grouped, state, event):
    op = event['op']
    if op == 'status':
        fields(event, ['id', 'op'])
        return
    if op == 'pickup':
        fields(event, ['id', 'op'])
        for actor in state['actors'].values():
            if active(actor) and actor.get('process') is None:
                actor['observation'] = {'status': 'unknown', 'reference': 'fresh native lookup required after pickup'}
        return
    if op == 'approve-limits':
        fields(event, ['id', 'op', 'previous_policy_sha256'])
        sha(event['previous_policy_sha256'])
        if event['previous_policy_sha256'] != state['policy_sha256']:
            raise ValueError('override does not name the current approved policy')
        if policy_shape(plan) != state['policy_shape']:
            raise ValueError('limit override cannot change approved scope, workers or groups')
        state.setdefault('approvals', []).append({'previous_policy_sha256': state['policy_sha256'],
                                                 'reference': plan['approval_reference']})
        return
    if op == 'observe':
        fields(event, ['id', 'op', 'actor', 'status', 'reference'])
        text(event['reference'])
        if event['status'] not in ('live', 'dead', 'unknown'):
            raise ValueError('unsupported native liveness observation')
        actor = state['actors'][event['actor']]
        if actor.get('process') is not None and liveness(actor) != event['status']:
            raise ValueError('observation contradicts local process state')
        actor['observation'] = {'status': event['status'], 'reference': event['reference']}
        return
    if op == 'finish':
        fields(event, ['id', 'op', 'actor', 'outcome', 'reference'])
        text(event['reference'])
        actor = state['actors'][event['actor']]
        if event['actor'] == 'coordinator' or event['outcome'] not in ('completed', 'interrupted'):
            raise ValueError('invalid worker completion')
        if not active(actor) or liveness(actor) != 'dead':
            raise ValueError('worker is live or uncertain; reconcile actual effects first')
        if any(lease['actor'] == event['actor'] for lease in state['devices'].values()):
            raise ValueError('restore and release owned device first')
        if any(active(child) and child['parent'] == event['actor'] for child in state['actors'].values()):
            raise ValueError('worker still has unaccounted children')
        actor.update(status=event['outcome'], completion_reference=event['reference'])
        return
    if op == 'device-acquire':
        fields(event, ['id', 'op', 'device', 'actor', 'settings', 'reference'])
        device = text(event['device'])
        text(event['reference'])
        actor = state['actors'][event['actor']]
        if device in state['devices']:
            raise ValueError('device already reserved')
        if not active(actor) or liveness(actor) != 'live':
            raise ValueError('device owner state uncertain or inactive')
        if not isinstance(event['settings'], dict) or not event['settings']:
            raise ValueError('observed device test settings required')
        state['devices'][device] = {'actor': event['actor'], 'settings': event['settings'],
                                   'baseline_reference': event['reference']}
        return
    if op == 'device-release':
        fields(event, ['id', 'op', 'device', 'settings', 'reference', 'processes_reference'])
        text(event['reference'])
        text(event['processes_reference'])
        lease = state['devices'][event['device']]
        if device_liveness(state, lease['actor']) != 'dead':
            raise ValueError('device process is live or uncertain; keep reservation')
        if encode(lease['settings']) != encode(event['settings']):
            raise ValueError('device test settings not restored; preserve reservation')
        state.setdefault('restoration', []).append({'device': event['device'], **event})
        del state['devices'][event['device']]
        return
    if op in ('stop', 'continue'):
        fields(event, ['id', 'op', 'reference'])
        text(event['reference'])
        state['stopped'] = op == 'stop'
        state['owner_decision'] = event['reference']
        return
    if op == 'allowance':
        fields(event, ['id', 'op', 'windows', 'warning', 'reference'])
        text(event['reference'])
        windows = items(event['windows'])
        ids = set()
        for window in windows:
            fields(window, ['id', 'used_percent', 'reset_at'])
            name = text(window['id'])
            if name in ids:
                raise ValueError('duplicate allowance window')
            ids.add(name)
            for key in ('used_percent', 'reset_at'):
                value = window[key]
                if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                    raise ValueError('invalid allowance observation')
        if event['warning'] is not None:
            text(event['warning'])
        state['allowance'] = {'windows': windows, 'warning': event['warning'],
                              'reference': event['reference'], 'recorded_at': time.time()}
        return
    if op == 'usage':
        record_usage(state, event)
        return
    if op == 'usage-gap':
        fields(event, ['id', 'op', 'scope', 'covers', 'actors', 'reference'])
        text(event['scope'])
        text(event['reference'])
        covers = items(event['covers'], True)
        actors = items(event['actors'], True)
        if len(set(map(text, covers))) != len(covers) or len(set(map(text, actors))) != len(actors):
            raise ValueError('duplicate usage gap coverage')
        for actor in actors:
            if actor not in state['actors']:
                raise ValueError('unregistered actor in usage gap')
        state.setdefault('usage_gaps', {})[event['id']] = {
            key: event[key] for key in ('scope', 'covers', 'actors', 'reference')}
        return
    if op == 'checkpoint':
        fields(event, ['id', 'op', 'unit', 'status', 'commit', 'proof_refs', 'next_action', 'reference'])
        text(event['reference'])
        text(event['next_action'])
        if event['unit'] not in plan['units'] or event['status'] not in ('pending', 'interrupted', 'completed'):
            raise ValueError('unknown checkpoint unit/state')
        if event['commit'] is not None and not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', text(event['commit'])):
            raise ValueError('invalid checkpoint commit')
        if event['status'] == 'completed' and any(active(a) and a['unit'] == event['unit']
                                                 for a in state['actors'].values()):
            raise ValueError('unit has unaccounted workers')
        previous = state['progress'].get(event['unit'])
        if previous and previous['status'] == 'completed':
            raise ValueError('completed progress is frozen; do not redo it')
        for reference in items(event['proof_refs']):
            file_bytes(reference)
        state['progress'][event['unit']] = {key: event[key] for key in
            ('status', 'commit', 'proof_refs', 'next_action', 'reference')}
        return
    if op == 'attach':
        fields(event, ['id', 'op', 'actor', 'pid', 'native_id', 'reference'])
        text(event['reference'])
        actor = state['actors'][event['actor']]
        if actor['status'] != 'reserved':
            raise ValueError('actor identity already attached or terminal')
        if event['pid'] is not None:
            pid = integer(event['pid'], 1)
            birth = process_birth(pid)
            if birth is None or os.getpgid(pid) != pid:
                raise ValueError('local worker needs an observed isolated process group')
            actor['process'] = {'pid': pid, 'birth': birth}
        else:
            text(event['native_id'])
        if event['native_id'] is not None:
            text(event['native_id'])
        for name, other in state['actors'].items():
            if name != event['actor'] and active(other) and (
                    (event['native_id'] is not None and other.get('native_id') == event['native_id'])
                    or (actor.get('process') is not None and other.get('process') == actor['process'])):
                raise ValueError('worker identity already attached to another active participant')
        actor.update(status='running', native_id=event['native_id'],
                     observation={'status': 'live', 'reference': event['reference']})
        return
    if op == 'dispatch':
        fields(event, ['id', 'op', 'worker', 'actor', 'parent'])
        if event['worker'] in grouped:
            raise ValueError('dispatch the complete required group')
        dispatch(plan, workers, state, event['worker'], event['actor'], event['parent'])
        return
    if op == 'dispatch-group':
        fields(event, ['id', 'op', 'group', 'round', 'parent'])
        suffix = text(event['round'])
        group = groups[event['group']]
        name = event['group'] + ':' + suffix
        if name in state['groups'] or any(active(state['actors'][m])
                                        for members in state['groups'].values() for m in members):
            raise ValueError('required group already active or round duplicated')
        members = []
        for member in group['members']:
            actor = member + ':' + suffix
            dispatch(plan, workers, state, member, actor, event['parent'])
            members.append(actor)
        state['groups'][name] = members
        return
    raise ValueError('unsupported controller event')


def protected_paths(root, policy_path, store, event_path=None):
    policy_path = plain_path(policy_path).resolve()
    store = plain_path(store).resolve()
    if not store.is_relative_to(policy_path.parent) or store.is_relative_to(root):
        raise ValueError('progress must stay in the protected owner control directory outside plugin')
    if event_path is not None:
        event_path = plain_path(event_path).resolve()
        if not event_path.is_relative_to(policy_path.parent):
            raise ValueError('controller event must stay in protected owner control directory')
    return policy_path, store, event_path


def control(root, binding, policy_path, expected, store, event_path):
    policy_path, store, event_path = protected_paths(root, policy_path, store, event_path)
    plan, workers, groups, grouped = policy(policy_path, expected)
    event = read_record(event_path)
    text(event['id'])
    text(event['op'])
    event_digest = digest(encode(event))
    binding_digest = digest(file_bytes(binding))
    with transaction(store):
        path = store / 'state.json'
        if path.exists():
            state = read_state(path)
            if state['binding_sha256'] != binding_digest or (
                    state['policy_sha256'] != expected and event['op'] != 'approve-limits'):
                raise ValueError('checkpoint policy or installation changed')
        elif event['op'] == 'init':
            fields(event, ['id', 'op'])
            state = {'schema_version': 1, 'program': plan['program'], 'policy_sha256': expected,
                     'binding_sha256': binding_digest, 'policy_shape': policy_shape(plan), 'started_at': time.time(),
                     'stopped': False, 'actors': {'coordinator': {'worker': 'coordinator',
                         'role': 'coordinator', 'status': 'running', 'unit': None, 'parent': None}},
                     'groups': {}, 'devices': {}, 'progress': {}, 'usage': {}, 'allowance': None, 'events': {}}
        else:
            raise ValueError('initialize approved program before dispatch')
        if event['id'] in state['events']:
            if state['events'][event['id']] != event_digest:
                raise ValueError('event ID reused with different content')
            return {**report(state, event.get('actor')), 'record': str(path)}
        if event['op'] == 'init' and state['events']:
            raise ValueError('existing program; use status/pickup instead of reinitializing')
        if event['op'] != 'init':
            apply(plan, workers, groups, grouped, state, event)
        if event['op'] == 'approve-limits':
            state['policy_sha256'] = expected
        if event['op'] != 'status':
            state['events'][event['id']] = event_digest
            save(path, state)
        return {**report(state, event.get('actor')), 'record': str(path)}


def wait(root, binding, policy_path, expected, store, kind, target, timeout):
    if not math.isfinite(timeout) or timeout < 0:
        raise ValueError('finite nonnegative wait timeout required')
    deadline = time.monotonic() + timeout
    policy_path, store, _ = protected_paths(root, policy_path, store)
    while True:
        load_binding(root, binding.resolve())
        policy(policy_path, expected)
        plain_path(store)
        state = read_state(store / 'state.json')
        if state['policy_sha256'] != expected or state['binding_sha256'] != digest(file_bytes(binding)):
            raise ValueError('checkpoint policy or installation changed')
        if kind == 'actor':
            actor = state['actors'][target]
            satisfied = not active(actor) or (actor.get('process') is not None and liveness(actor) == 'dead')
        else:
            satisfied = target not in state['devices']
        if satisfied or time.monotonic() >= deadline:
            return {'wait_satisfied': satisfied, 'kind': kind, 'target': target,
                    'basis': 'saved state or observed local process exit; reconcile effects and resource ownership'}
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))
