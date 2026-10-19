import hashlib
import json
from pathlib import Path
import tarfile

import check_core

ROOT = Path(__file__).resolve().parents[1]

# Skills added to the product after the frozen 0.2.0 release (tests/fixtures/release-0.2.0.tar.gz)
# and after the pinned native baseline. They have no historical counterpart, so every historical
# comparison (published 0.2.0, native_before) covers only the originally declared skills while the
# candidate covers all of them. Each addition is listed here by name: a new SKILL.md that is not
# listed, or a listed one that appears in the release, still fails the inventory check below.
ADDED_AFTER_RELEASE = (
    'plugin/skills/control-cli/SKILL.md',
    'plugin/skills/control-ui/SKILL.md',
    'plugin/skills/deslop/SKILL.md',
    'plugin/skills/hugues-help/SKILL.md',
    'plugin/skills/in-your-own-words/SKILL.md',
    'plugin/skills/ketchup/SKILL.md',
    'plugin/skills/sharpen/SKILL.md',
)

# Skills renamed after the frozen archives were cut. The archive bytes stay as published; only
# the loaded path keys take today's name, so every historical comparison finds the renamed skill.
RENAMED_AFTER_ARCHIVE = {'plugin/skills/setup-huguesstack/': 'plugin/skills/setup-hstack/'}


def current_names(texts):
    renamed = {}
    for name, text in texts.items():
        for old, new in RENAMED_AFTER_ARCHIVE.items():
            if name.startswith(old):
                name = new + name[len(old):]
                break
        renamed[name] = text
    if len(renamed) != len(texts):
        raise ValueError('context archive rename collides with a current path')
    return renamed


def metrics(texts):
    chars = sum(len(s) for s in texts)
    return {'bytes': sum(len(s.encode()) for s in texts), 'characters': chars,
            'estimated_tokens_characters_divided_by_4': round(chars / 4, 2)}


def archive_texts(path):
    with tarfile.open(path) as archive:
        members = [m for m in archive.getmembers() if m.isfile() and
                   (m.name.endswith('.md') or m.name.endswith('/agents/openai.yaml'))]
        if len({m.name for m in members}) != len(members):
            raise ValueError('duplicate context archive path')
        return {m.name: archive.extractfile(m).read().decode() for m in members}


def native_baseline(root):
    receipt = json.loads((root / 'docs/CONTEXT-BASELINE.json').read_text())
    path = root / receipt['archive']
    if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['archive_sha256']:
        raise ValueError('context baseline archive drift')
    texts = archive_texts(path)
    if set(texts) != set(receipt['files']):
        raise ValueError('context baseline inventory drift')
    for name, text in texts.items():
        if hashlib.sha256(text.encode()).hexdigest() != receipt['files'][name]['sha256']:
            raise ValueError('context baseline bytes drift: ' + name)
    return texts, receipt['revision']


def pre_pr_main_baseline(root):
    """The actual pre-PR point this restoration branched from (`a67df90`, the revision
    the Issue's Problem Statement measures): just the 50 SKILL.md frontmatter blocks,
    sha256-pinned, following the CONTEXT-BASELINE.json fixture pattern but holding only
    what skill_list_metrics needs. `native_before` (pinned `7db3e80`) is a different,
    earlier point that predates the 0.2.0-to-46-skill flip this PR undoes -- it is not a
    pre-PR comparison for the skill-list budget, only for the other measurements on this
    page that it was already pinned for."""
    receipt = json.loads((root / 'docs/CONTEXT-BASELINE-PRE-PR.json').read_text())
    return pinned_texts(root, receipt, 'pre-PR baseline'), receipt['revision']


def pre_pr_main_mode_read_set(root):
    """The router's initial read set as `main` (`a67df90`) had it: the full router body plus
    the two unconditional adapters, sha256-pinned in the same receipt as the frontmatter
    fixture above. The frontmatter fixture holds only frontmatter blocks, so it cannot
    answer how large the router's initial read was before the router rewrite."""
    receipt = json.loads((root / 'docs/CONTEXT-BASELINE-PRE-PR.json').read_text())
    return pinned_texts(root, receipt['mode_read_set'], 'pre-PR mode read set'), receipt['revision']


def pinned_texts(root, receipt, label):
    path = root / receipt['archive']
    if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['archive_sha256']:
        raise ValueError(label + ' archive drift')
    texts = archive_texts(path)
    if set(texts) != set(receipt['files']):
        raise ValueError(label + ' inventory drift')
    for name, text in texts.items():
        if hashlib.sha256(text.encode()).hexdigest() != receipt['files'][name]['sha256']:
            raise ValueError(label + ' bytes drift: ' + name)
    return texts


def description_text(raw):
    """Unwrap a frontmatter description scalar the way a YAML-parsing host sees it:
    a quoted scalar's surrounding quotes are not part of the displayed string."""
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def skill_list_metrics(texts, paths):
    """Description characters of every skill without `disable-model-invocation: true`,
    over one caller-supplied, already-pinned set of skill texts."""
    selected = sorted(p for p in paths
                      if not check_core.native_frontmatter(texts[p])['disable-model-invocation'])
    descriptions = [description_text(check_core.native_frontmatter(texts[p])['description']) for p in selected]
    return {'model_invocable_skills': len(selected), 'paths': selected, **metrics(descriptions)}


def inventory(texts, paths):
    paths = sorted(set(paths))
    if any(path not in texts for path in paths):
        raise ValueError('missing modeled context input')
    return {'paths': paths, 'unique_files': len(paths), **metrics([texts[p] for p in paths]),
            'inputs': {p: {'bytes': len(texts[p].encode()),
                          'sha256': hashlib.sha256(texts[p].encode()).hexdigest()} for p in paths}}


def measure(root=ROOT):
    release = current_names(archive_texts(root / 'tests/fixtures/release-0.2.0.tar.gz'))
    before, before_revision = native_baseline(root)
    before = current_names(before)
    pre_pr_main, pre_pr_main_revision = pre_pr_main_baseline(root)
    pre_pr_main = current_names(pre_pr_main)
    pre_pr_mode, _ = pre_pr_main_mode_read_set(root)
    pre_pr_mode = current_names(pre_pr_mode)
    current = {p.relative_to(root).as_posix(): p.read_text()
               for p in (root / 'plugin').rglob('*') if p.is_file() and
               (p.suffix == '.md' or p.name == 'openai.yaml')}
    declaration_paths = sorted(p for p in current if p.startswith('plugin/skills/') and p.endswith('/SKILL.md'))
    original_declarations = sorted(p for p in release if p.startswith('plugin/skills/') and p.endswith('/SKILL.md'))
    added_declarations = sorted(ADDED_AFTER_RELEASE)
    if (len(original_declarations) != 50 or set(added_declarations) & set(original_declarations)
            or len(added_declarations) != len(ADDED_AFTER_RELEASE)
            or declaration_paths != sorted(original_declarations + added_declarations)):
        raise ValueError('context declaration inventory changed')
    receipt = json.loads((root / 'docs/upstream/consolidation.json').read_text())
    source_by_destination = {r['destination']: r['source'] for r in receipt['files'] if r['destination']}

    def release_paths(paths):
        selected = set()
        for path in paths:
            source = source_by_destination.get(path)
            core = 'plugin/core/' + source if source else None
            if core in release:
                if (path.endswith('/SKILL.md') and '/principle-' not in path) or path.startswith('plugin/agents/'):
                    selected.add(path)
                selected.add(path if '/principle-' in path else core)
            elif path in release:
                selected.add(path)
            else:
                raise ValueError('missing historical context mapping: ' + path)
        return selected

    always = {'plugin/adapters/host.md', 'plugin/adapters/mobile.md'}
    spec = json.loads((root / 'docs/CONTEXT-SCENARIOS.json').read_text())
    scenarios = {}
    for name, profile in spec['profiles'].items():
        required = {row['path'] for row in profile['required']}
        if len(required) != len(profile['required']) or not {
                'plugin/skills/hugues-mode/SKILL.md', 'plugin/skills/unslop/SKILL.md'} <= required:
            raise ValueError('incomplete or duplicate routing/reply inputs')
        phases = {'plugin/adapters/' + p for p in profile['phase_guidance']}
        for phase in phases:
            if '(' + Path(phase).name + ')' not in current['plugin/adapters/host.md']:
                raise ValueError('phase reference not reachable from mandatory host guidance')
        candidate_required = {row['path'] for row in profile.get('candidate_required', [])}
        if len(candidate_required) != len(profile.get('candidate_required', [])):
            raise ValueError('duplicate candidate-only input')
        paths = required | always
        mode_workers = sum(row['count'] for row in profile['workers'] if row['mode_context'])
        worker_floor = {'plugin/skills/hugues-mode/SKILL.md', 'plugin/agents/hugues-agent.md', *always}
        worker_after = worker_floor | {'plugin/adapters/host-workers.md'}
        floor = {}
        for version, texts, names in [('published_0_2', release, release_paths(worker_floor)),
                                     ('native_before', before, worker_floor),
                                     ('candidate', current, worker_after)]:
            item = inventory(texts, names)
            floor[version] = {**item, 'mode_workers': mode_workers,
                'repeated_bytes_floor': item['bytes'] * mode_workers,
                'repeated_estimated_tokens_floor': item['estimated_tokens_characters_divided_by_4'] * mode_workers}
        scenarios[name] = {'scenario': profile['scenario'],
            'published_0_2': inventory(release, release_paths(paths)),
            'native_before': inventory(before, paths),
            'candidate': inventory(current, paths | phases | candidate_required),
            'workers': profile['workers'], 'fresh_mode_worker_floor': floor,
            'complete_execution_tokens': None,
            'unknown_inputs': spec['unknown_inputs']}

    old_paths = ['plugin/skills/hugues-mode/SKILL.md', 'plugin/adapters/host.md',
                 'plugin/adapters/mobile.md', 'plugin/core/pstack/skills/poteto-mode/SKILL.md']
    new_paths = old_paths[:3]
    frontmatter = lambda texts, paths: metrics([texts[p].split('---', 2)[1] for p in paths])
    return {'method': 'UTF-8 bytes; Unicode characters; characters/4 estimate. Deterministic source accounting, not runtime latency or observed host context.',
        'baseline_revision': '509cbec0486c23bb76a943ffec1ea7c7fb553c0f',
        'native_before_revision': before_revision,
        'pre_pr_main_revision': pre_pr_main_revision,
        'mode_initial_read_set': {'scope': 'Mode entry and unconditional adapters only, before reply or task-dependent reads. See initial_mode_routing for the route announcement closure.',
            'baseline_paths': old_paths, 'candidate_paths': new_paths,
            'baseline': metrics([release[p] for p in old_paths]),
            'native_before': metrics([before[p] for p in new_paths]),
            'pre_pr_main': metrics([pre_pr_mode[p] for p in new_paths]),
            'candidate': metrics([current[p] for p in new_paths])},
        'native_frontmatter': {'scope': f'All {len(declaration_paths)} declared frontmatter blocks, an upper bound; actual native startup exposure is unknown. '
                f'baseline and native_before cover the {len(original_declarations)} skills declared at 0.2.0; '
                f'candidate adds the {len(added_declarations)} listed in added_after_release, which have no historical counterpart.',
            'baseline': frontmatter(release, original_declarations),
            'native_before': frontmatter(before, original_declarations),
            'candidate': frontmatter(current, declaration_paths),
            'candidate_original_skills': frontmatter(current, original_declarations),
            'added_after_release': added_declarations,
            'paths': declaration_paths},
        'codex_policy_metadata': {'scope': 'Additional policy-file bytes, not a claim these files enter model context.',
            'native_before': inventory(before, [p for p in before if p.endswith('/agents/openai.yaml')]),
            'candidate': inventory(current, [p for p in current if p.endswith('/agents/openai.yaml')])},
        'skill_list': {'scope': "Description characters of every skill without `disable-model-invocation: true`, "
                "the description value as a YAML-parsing host sees it (surrounding quotes excluded); "
                "Claude Code documents this text as entering its per-turn skill list, budgeted at 1% of the "
                "context window (Codex: 2%), both with an 8000-character fallback. Not a runtime observation. "
                "native_before (pinned 7db3e80) predates the 0.2.0-to-46-skill flip this PR undoes and is not a "
                "pre-PR comparison point for this measurement; pre_pr_main (pinned a67df90, the revision this "
                "restoration branched from and the Issue's Problem Statement measures) is the real one.",
            'native_before': skill_list_metrics(before, original_declarations),
            'pre_pr_main': skill_list_metrics(pre_pr_main, sorted(pre_pr_main)),
            'candidate': skill_list_metrics(current, declaration_paths)},
        'canonical_skill_bodies': {'scope': 'Whole native SKILL.md files, metadata included; separate from invocation closure.',
            'native_before': inventory(before, original_declarations), 'candidate': inventory(current, declaration_paths),
            'workflow_body_only_before': metrics([before[p].split('---', 2)[2] for p in original_declarations]),
            'workflow_body_only_candidate': metrics([current[p].split('---', 2)[2] for p in declaration_paths]),
            'mode_full_file': inventory(current, ['plugin/skills/hugues-mode/SKILL.md']),
            'mode_workflow_body_only': metrics([current['plugin/skills/hugues-mode/SKILL.md'].split('---', 2)[2]]),
            'unchanged_files': sum(before[p] == current[p] for p in original_declarations)},
        'scenarios': scenarios, 'worker_accounting': spec['worker_accounting'],
        'public_skills': len(declaration_paths),
        'limits': ['No runtime host, tokenizer, prompt framing, cache or native invocation observation.',
                   'Required transitive bundled reads are included for the stated scenarios even if invocation would hold.',
                   'External skills, consumer inputs and generated evidence have unknown size; no complete workflow token total is claimed.',
                   'Unique inventories do not count repeated loads in fresh workers; the separate floor is partial and not additive.',
                   'Mobile, investigation categories, retries and task-designed large programs require different closures.',
                   'Static scenario accounting needs review when instructions or assumptions change.']}


if __name__ == '__main__':
    print(json.dumps(measure(), indent=2))
