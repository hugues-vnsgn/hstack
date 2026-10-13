"""Compare verification contracts at immutable Git commits; never certify behavior."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


def git(repo, *args):
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(repo), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or 'Git read failed')
    return result.stdout


def snapshot(repo, sha, plan):
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', sha):
        raise ValueError('use a full immutable commit SHA')
    if git(repo, 'cat-file', '-t', sha).strip() != 'commit':
        raise ValueError('snapshot must be a commit')
    entry = git(repo, 'ls-tree', sha, '--', plan).strip()
    if not entry:
        return None
    if not entry.startswith(('100644 blob ', '100755 blob ')):
        raise ValueError('plan must be a regular Git blob')
    return git(repo, 'show', sha + ':' + plan)


def contract(text, section):
    if text is None:
        return None
    if re.search(r'<!--|^[ \t]*(?:```|~~~)', text, re.M):
        raise ValueError('fenced code and HTML comments require manual contract review')
    sections = re.split(r'^## ', text, flags=re.M)[1:]
    matches = [part.split('\n', 1)[1] for part in sections
               if part.split('\n', 1)[0].strip() == section and '\n' in part]
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError('ambiguous PR section')
    lines = matches[0].splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith('**Verify, unit.**')]
    ends = [i for i, line in enumerate(lines) if line.startswith('**Review gate.**')]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise ValueError('expected one unit/live/perf contract before Review gate')
    selected = lines[starts[0]:ends[0]]
    for name in ['unit', 'live', 'perf']:
        if sum(line.startswith('**Verify, ' + name + '.**') for line in selected) != 1:
            raise ValueError('missing or duplicate verification block')
    selected = [line for line in selected if not re.fullmatch(
        r'Evidence\. (?:\[[^\]\n]+\]\([^()\s]+\) ?)+', line)]
    return '\n'.join(re.sub(r'^(\s*)- \[[ xX]\] ', r'\1', line).rstrip()
                     for line in selected if line.strip())


def compare(args):
    path = PurePosixPath(args.plan)
    if path.is_absolute() or '..' in path.parts or str(path) != args.plan or ':' in args.plan:
        raise ValueError('plan must be a normalized repository-relative path')
    before = contract(snapshot(args.repo, args.base_sha, args.plan), args.section)
    after = contract(snapshot(args.repo, args.head_sha, args.plan), args.section)
    if after is None:
        raise ValueError('PR head has no verification contract')
    diff = '\n'.join(difflib.unified_diff((before or '').splitlines(), after.splitlines(),
                                         fromfile='main contract', tofile='head contract', lineterm=''))
    result = {'base_sha': args.base_sha, 'head_sha': args.head_sha,
            'plan': args.plan, 'section': args.section, 'before': before, 'after': after,
            'diff': diff, 'gate': 'hold' if before is None or diff else 'unchanged',
            'verification_required': True}
    result['comparison_sha256'] = hashlib.sha256(
        json.dumps(result, sort_keys=True).encode()).hexdigest()
    result['ruling'] = None
    if args.ruling:
        ruling_path = Path(args.ruling).resolve()
        if ruling_path.is_relative_to(Path(args.repo).resolve()):
            raise ValueError('operator ruling must be supplied outside the consumer worktree')
        ruling = json.loads(ruling_path.read_text(), object_pairs_hook=unique_keys)
        if (not isinstance(ruling, dict)
                or set(ruling) != {'comparison_sha256', 'decision', 'reference'}
                or ruling['comparison_sha256'] != result['comparison_sha256']
                or ruling['decision'] != 'approved'
                or not isinstance(ruling['reference'], str) or not ruling['reference'].strip()):
            raise ValueError('ruling must approve this exact comparison with an operator reference')
        result['ruling'] = ruling
        if result['gate'] == 'hold':
            result['gate'] = 'approved'
    return result


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate ruling key')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['repo', 'plan', 'section', 'base-sha', 'head-sha']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--ruling')
    args = parser.parse_args()
    try:
        result = compare(args)
        print(json.dumps(result, indent=2))
        return 2 if result['gate'] == 'hold' else 0
    except (ValueError, OSError) as exc:
        print('verification contract blocked: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
