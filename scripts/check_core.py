"""Verify actual pinned bytes, active workflow wiring and bounded policy overrides."""
import hashlib
import ast
import importlib.util
import json
from pathlib import Path
import re
import stat
import sys

import tarfile

ROOT = Path(__file__).resolve().parents[1]
PIN = 'e73df471cd4bd918367e99f3dd9c51bd53ddf5f0'
TREE = '880564357e051d7c7802da1cb5d8df1d0b008299'
EXCLUDED = set()
ALIASES = {'poteto-mode': 'hugues-mode', 'setup-pstack': 'setup-hstack', 'poteto-help': 'hugues-help'}
# Reviewed host invocation table. pstack's router read every other skill as a file;
# hStack restores that design. Only `setup-hstack` stays model-invocable, so its
# description is the only one paid for in the host's per-turn skill list. The router,
# `hugues-mode`, is user-only as `poteto-mode` is upstream. Every other bundled skill is user-only:
# the owner can still type it by name, and the mode reaches it by reading its
# SKILL.md in full (the scoped host adapter rule), never by native invocation.
USER_ONLY = {
    'architect', 'arena', 'automate-me', 'benchmark-checklist', 'blast-radius', 'bro',
    'control-cli', 'control-ui', 'correct', 'create-formal-verification-skill', 'create-verification-skill', 'deslop', 'figure-it-out', 'how', 'hugues-help', 'hugues-mode',
    'in-your-own-words', 'interrogate', 'ketchup', 'ketchup-video',
    'maintain-formal-verification-skill', 'maintain-verification-skill', 'make-bot-ui', 'no-comments',
    'principle-attack-the-premise', 'principle-boundary-discipline', 'principle-build-the-lever',
    'principle-encode-lessons-in-structure', 'principle-exhaust-the-design-space',
    'principle-experience-first', 'principle-explain-the-number', 'principle-fix-root-causes',
    'principle-foundational-thinking', 'principle-guard-the-context-window',
    'principle-laziness-protocol', 'principle-make-operations-idempotent',
    'principle-migrate-callers-then-delete-legacy-apis', 'principle-minimize-reader-load',
    'principle-model-the-domain', 'principle-never-block-on-the-human',
    'principle-outcome-oriented-execution', 'principle-prove-it-works',
    'principle-redesign-from-first-principles', 'principle-separate-before-serializing-shared-state',
    'principle-sequence-verifiable-units', 'principle-subtract-before-you-add',
    'principle-test-behavior-not-implementation', 'principle-type-system-discipline',
    'recall', 'reflect', 'sharpen', 'show-me-your-work', 'statechart', 'swarm', 'tdd', 'teach',
    'technical-writing',
    'swift-best-practices', 'kotlin-best-practices',
    'typescript-best-practices', 'unslop', 'why',
}
# Skills hStack bundles from a source other than pstack. The pstack archive and the upstream
# ledger have no row for them, so each is bound here instead: to the exact file and commit it
# was copied from and to the MIT notice that came with it (see external_skill_errors). The
# installed body is hStack-maintained and may be edited; the pinned source copy records its
# origin. consolidation.json carries the same table as a reviewable receipt, and the two must agree.
EXTERNAL_SKILLS = {
    'control-cli': {
        'repository': 'https://github.com/cursor/plugins',
        'revision': 'ccb5507cec1546dc88135c1139c811e6c59115ba',
        'source': 'cursor-team-kit/skills/control-cli/SKILL.md',
        'source_blob_sha': '69289ac517e8a28380c8eca5c6692e8a601fa62c',
        'source_sha256': '13ac93e595bbda2000849bdb815d5f2ca03f7c2ca63788c8335f9212b9b422a2',
        'source_copy': 'provenance/upstream/cursor-team-kit-ccb5507/skills/control-cli/SKILL.md',
        'license': 'MIT',
        'license_holder': 'Copyright (c) 2026 Cursor',
        'license_source': 'cursor-team-kit/LICENSE',
        'license_blob_sha': 'ca2bba771cd39dbef6acf96b52481133983451f3',
        'license_sha256': '702f5f331b56aff0e33d8c7826df5202559f894145eb70355c6477b55b5bb8a0',
        'license_copy': 'provenance/upstream/cursor-team-kit-ccb5507/LICENSE',
        'destination': 'plugin/skills/control-cli/SKILL.md',
        'license_destination': 'plugin/skills/control-cli/LICENSE',
    },
    'control-ui': {
        'repository': 'https://github.com/cursor/plugins',
        'revision': 'ccb5507cec1546dc88135c1139c811e6c59115ba',
        'source': 'cursor-team-kit/skills/control-ui/SKILL.md',
        'source_blob_sha': '68484fd5418cc893a6bf40e0db45b3001dcf5947',
        'source_sha256': '410cae25bdb1e5d2323b126abc5047b0213be7fdb0195710213fa8de8a751871',
        'source_copy': 'provenance/upstream/cursor-team-kit-ccb5507/skills/control-ui/SKILL.md',
        'license': 'MIT',
        'license_holder': 'Copyright (c) 2026 Cursor',
        'license_source': 'cursor-team-kit/LICENSE',
        'license_blob_sha': 'ca2bba771cd39dbef6acf96b52481133983451f3',
        'license_sha256': '702f5f331b56aff0e33d8c7826df5202559f894145eb70355c6477b55b5bb8a0',
        'license_copy': 'provenance/upstream/cursor-team-kit-ccb5507/LICENSE',
        'destination': 'plugin/skills/control-ui/SKILL.md',
        'license_destination': 'plugin/skills/control-ui/LICENSE',
    },
    'deslop': {
        'repository': 'https://github.com/cursor/plugins',
        'revision': 'ccb5507cec1546dc88135c1139c811e6c59115ba',
        'source': 'cursor-team-kit/skills/deslop/SKILL.md',
        'source_blob_sha': '1b3827c7f991182149a7abda696af43ff8f17a12',
        'source_sha256': '2f7b7def74af7ed11f5b44b4d32f0f91fca8c5d1f92bf2171e8d12fd33a0f810',
        'source_copy': 'provenance/upstream/cursor-team-kit-ccb5507/skills/deslop/SKILL.md',
        'license': 'MIT',
        'license_holder': 'Copyright (c) 2026 Cursor',
        'license_source': 'cursor-team-kit/LICENSE',
        'license_blob_sha': 'ca2bba771cd39dbef6acf96b52481133983451f3',
        'license_sha256': '702f5f331b56aff0e33d8c7826df5202559f894145eb70355c6477b55b5bb8a0',
        'license_copy': 'provenance/upstream/cursor-team-kit-ccb5507/LICENSE',
        'destination': 'plugin/skills/deslop/SKILL.md',
        'license_destination': 'plugin/skills/deslop/LICENSE',
    },
}
AUTHORED_SKILLS = {
    'swift-best-practices': {'paths': '["**/*.swift"]'},
    'kotlin-best-practices': {'paths': '["**/*.kt", "**/*.kts"]'},
}
# Cursor fields that neither Claude Code nor Codex reads from a skill's frontmatter.
# The router carried them until the router rewrite; no skill may bring them back.
DEAD_FRONTMATTER = {'mode', 'icon', 'color', 'reminder'}
ROUTER = 'plugin/skills/hugues-mode/SKILL.md'
# Router sections that sibling files point at by name. Each row is the file, the router
# section it names, and the words it names it with. A rename or removal of a section, or a
# sibling that stops saying these words, fails the check, so the table cannot rot silently.
ROUTER_SECTION_POINTERS = (
    ('plugin/skills/figure-it-out/SKILL.md', 'Principles', 'Principles section of the **hugues-mode** skill'),
    ('plugin/agents/hugues-agent.md', 'Subagents', "hugues-mode's Subagents section"),
    ('plugin/agents/hugues-agent.md', 'Principles', 'inline Principles index'),
    ('plugin/skills/hugues-mode/playbooks/multi-phase-plan.md', 'Subagents', 'per the Subagents section'),
    ('plugin/skills/hugues-mode/playbooks/bug-fix.md', 'Non-negotiables', '(Non-negotiables)'),
    ('plugin/skills/hugues-mode/playbooks/investigation.md', 'Autonomy', '(see Autonomy)'),
    ('plugin/skills/hugues-mode/playbooks/worktree-cleanup.md', 'Autonomy', 'Per Autonomy,'),
)
# Every section of the router that is kept by name, whether or not a sibling points at it.
ROUTER_SECTIONS = ('Non-negotiables', 'Principles', 'Autonomy', 'Subagents',
                   'Writing the reply', 'Comments', 'Playbooks')
AGENTS = {
    'poteto-agent': {'source': 'pstack/agents/poteto-agent.md',
                     'entrypoint': 'plugin/agents/hugues-agent.md'},
    'Comment Sicko': {'source': 'pstack/agents/comment-sicko.md',
                      'entrypoint': 'plugin/agents/hugues-comment-sicko.md'},
}
WORKER_ROLES = {
    'how-explorer': ('how', 'generalPurpose', 'references/explorer-prompt.md'),
    'how-explainer': ('how', 'generalPurpose', 'references/explainer-prompt.md'),
    'why-investigator': ('why', 'generalPurpose', 'references/investigator-prompt.md'),
    'why-synthesizer': ('why', 'generalPurpose', 'references/synthesizer-prompt.md'),
    'reflect-judgment': ('reflect', 'generalPurpose', 'references/judgment-reviewer.md'),
    'reflect-tooling': ('reflect', 'generalPurpose', 'references/tooling-reviewer.md'),
    'reflect-divergent': ('reflect', 'generalPurpose', 'references/divergent-reviewer.md'),
    'reflect-synthesizer': ('reflect', 'generalPurpose', 'references/synthesizer.md'),
    'interrogate-reviewer': ('interrogate', 'generalPurpose', 'references/reviewer-prompt.md'),
    'architect-runner': ('architect', 'core', 'references/runner-prompt.md'),
    'arena-runner': ('arena', 'core', 'SKILL.md'),
    'arena-cross-judge': ('arena', 'core', 'SKILL.md'),
    'swarm-worker': ('swarm', 'generalPurpose', 'SKILL.md'),
    'automate-me-history-miner': ('automate-me', 'core', 'SKILL.md'),
    'show-me-your-work-auditor': ('show-me-your-work', 'core', 'SKILL.md'),
}


def worker_roles():
    return {name: {'skill': skill, 'dispatch': dispatch,
                   'prompt': f'pstack/skills/{skill}/{prompt}'}
            for name, (skill, dispatch, prompt) in WORKER_ROLES.items()}


ADAPTERS = ['plugin/adapters/host.md', 'plugin/adapters/mobile.md']
PHASE_GUIDANCE = {
    'host-workers.md': 'Worker dispatch, worker execution, role selection or setup-hstack',
    'host-workflow-tools.md': 'Installed planning or audit commands, workflow ticks, other installed helpers, Bun bootstrap, cloud/loop/forge operations',
    'host-special-skills.md': 'Transcript-dependent skills, optional integrations or consumer skill placement',
    'host-mobile-languages.md': 'Reading or editing Swift or Kotlin files',
    'host-typescript.md': 'Reading or editing TypeScript files',
    'host-publication.md': 'Skill authoring, commits, review, Bugbot triage or its plan box, PR preparation/publication or missing control/writing capability reports',
}
ADAPTER_RESOURCES = ['plugin/adapters/' + name for name in PHASE_GUIDANCE] + ['plugin/adapters/mobile-workflows.md']


def require(value, message):
    if not value:
        raise ValueError(message)


def native_frontmatter(text):
    header = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    require(header, 'missing native frontmatter')
    fields = {}
    description_block = False
    for line in header[1].splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if description_block and line[0].isspace():
            continue
        pair = re.fullmatch(r'([a-z][a-z-]*):\s+(.+)', line)
        require(pair, 'unsupported native frontmatter scalar')
        key, value = pair.groups()
        require(key not in fields, 'duplicate native frontmatter field: ' + key)
        fields[key] = value
        description_block = key == 'description' and value in {'>', '>-', '>+', '|', '|-', '|+'}
    manual = fields.get('disable-model-invocation', 'false')
    require(manual in {'true', 'false'}, 'invalid native invocation boolean')
    fields['disable-model-invocation'] = manual == 'true'
    return fields


def section(text, heading):
    match = re.search(r'^## ' + re.escape(heading) + r'\n(.*?)(?=^## |\Z)',
                      text, re.M | re.S)
    return match.group(1) if match else ''


def ordered(text, markers):
    positions = [text.find(marker) for marker in markers]
    return all(p >= 0 for p in positions) and positions == sorted(set(positions))


def behavior_errors(bodies):
    """Check phase-local obligations independently of the source fingerprints."""
    errors = []
    def expect(name, value):
        if not value:
            errors.append(name)
    for name, headings in {
        'architect': ['Ground the problem', 'Sketch', 'Agree (opt-in)',
                      'Implement against the sketch', 'Scrap when the architecture is wrong'],
        'arena': ['Frame', 'Fan out', 'Cross-judge', 'Pick a base', 'Graft', 'Verify'],
        'swarm': ['Frame', 'Fan out', 'Aggregate', 'Report'],
    }.items():
        actual = re.findall(r'^## Phase [A-F]: (.+)$', bodies[name], re.M)
        expect(name + '-phase-order', actual == headings)
    expect('architect-two-shapes', 'at least two structurally distinct candidates' in
           section(bodies['architect'], 'Phase B: Sketch'))
    expect('mandatory-feature-arena', 'Mandatory: no skip-with-reason escape' in bodies['feature']
           and ordered(bodies['feature'], ['1. `how`', '2. `architect`',
                                          '3. Write the throughput', '4. Delegate code-writing',
                                          '5. Verify', '6. Rebase', '7. If the design', '8. Run']))
    expect('three-seat-interrogate', re.findall(
        r'\| Reviewer [ABC] \| `([^`]+)` \|', bodies['interrogate']) == ['inherit-parent max'] * 3)
    expect('interrogate-adjudication', ordered(bodies['interrogate'],
        ['## Step 1,', '## Step 2,', '## Step 3,', '## Step 4,', '## Step 5,'])
        and 'Do NOT auto-apply changes' in bodies['interrogate'])
    expect('generator-feature-map', 'aim for the top 3-5' in
        section(bodies['create-verification-skill'], '3. Seed the feature map')
        and 'features/README.md' in bodies['create-verification-skill'])
    expect('generator-proof-after-map', ordered(bodies['create-verification-skill'],
        ['## 1.', '## 2.', '## 3.', '## 4.', '## 5.'])
        and 'drive ONE mapped feature' in section(bodies['create-verification-skill'],
                                                '4. Prove the generated skill before handing it over')
        and 'evidence still exists' in bodies['create-verification-skill'])
    maintenance = section(bodies['maintain-verification-skill'], 'Pass')
    expect('maintenance-whole-map', ordered(maintenance, ['0. **Locate', '1. **Index',
        '2. **Source', '3. **Reconcile', '4. **Live', '5. **Triage', '6. **Ship'])
        and 'Exercise every feature at least once' in maintenance
        and 'retry once' in maintenance and 'source path' in maintenance)
    expect('tdd-red-before-fix', ordered(section(bodies['tdd'], 'Workflow'),
        ['3. **Write', '4. **Run the new test before fixing', '5. **Fix', '6. **Rerun']))
    expect('swarm-coverage-and-dropouts', all(marker in section(bodies['swarm'], 'Phase C: Aggregate')
        for marker in ['SHAs and method', 'respawn that worker once',
                       'A gap does not count as a pass', 'every required slice']))
    expect('trail-append-only', all(marker in bodies['show-me-your-work'] for marker in
        ['Append-only', 'ts', 'phase', 'decision', 'why', 'evidence', 'result',
         'phase `start`', 'Cross-model review', 'Audit the log against the transcript']))
    expect('setup-panel-cardinality', all(marker in bodies['setup-pstack'] for marker in
        ['one subagent runs per entry', 'list length sets the count',
         'Never write a real slug you have not confirmed', 'Every real slug written',
         'unlimited — keep max', 'large — xhigh reasoning',
         'medium — high reasoning', 'small — medium reasoning']))
    mode = bodies['poteto-mode']
    expect('mode-fallback-and-trail', all(marker in mode for marker in
        ['Use **figure-it-out** whenever no bundled playbook fits',
         'routes to **Orchestrate** instead', '**show-me-your-work**',
         '**swarm**', '**benchmark-checklist**', '**no-comments**', '**technical-writing**']))
    return errors


def external_skill_errors(root, receipt, upstream):
    """Pin the source copy and license notice of each skill hStack bundles from outside pstack.
    The installed body is hStack-maintained; the user-only and host-contract requirements on it
    come from the per-skill loop in check."""
    errors = []
    if receipt.get('external_skills') != EXTERNAL_SKILLS:
        errors.append('external skill receipt differs')
    def read(relative):
        path = root / relative
        if not (path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root)):
            errors.append('missing/unsafe external skill file: ' + relative)
            return None
        return path.read_bytes()
    for name, row in EXTERNAL_SKILLS.items():
        source = read(row['source_copy'])
        notice = read(row['license_copy'])
        installed = read(row['destination'])
        shipped_notice = read(row['license_destination'])
        if None in (source, notice, installed, shipped_notice):
            continue
        if (hashlib.sha256(source).hexdigest() != row['source_sha256']
                or upstream.oid('blob', source) != row['source_blob_sha']):
            errors.append('external skill source copy differs from its pinned commit: ' + name)
        if (hashlib.sha256(notice).hexdigest() != row['license_sha256']
                or upstream.oid('blob', notice) != row['license_blob_sha']
                or row['license_holder'].encode() not in notice):
            errors.append('external skill license copy differs from its pinned commit: ' + name)
        if shipped_notice != notice:
            errors.append('installed external skill license differs from the pinned notice: ' + name)
    return errors


def adapter_errors(texts):
    errors = []
    host = texts[ADAPTERS[0]]
    for name, trigger in PHASE_GUIDANCE.items():
        if not re.search(r'^\| ' + re.escape(trigger) + r' \| \[[^\]]+\]\(' + re.escape(name) + r'\) \|$', host, re.M):
            errors.append('missing phase prerequisite: ' + name)
    for marker in ['Before the triggering action, read its complete reference',
                   'never use a file read as an invocation fallback', 'never restart task routing',
                   'Reach `setup-hstack` and each consumer or external skill',
                   "only through the host's supported native mechanism",
                   'owner-disabled entries and native denials',
                   'No translation grants new authority', 'A constraint\ncan block execution',
                   'copy its ordered todos verbatim']:
        if marker.casefold() not in host.casefold():
            errors.append('lost always-loaded boundary: ' + marker)
    mobile = texts[ADAPTERS[1]]
    if not all(marker in mobile for marker in ['explicitly selected mobile task',
               '[mobile workflows](mobile-workflows.md) in full', 'before selecting the route or executing a phase',
               'For all other work, follow the pinned core unchanged']):
        errors.append('lost mobile applicability prerequisite')
    effective = dict(texts)
    effective[ADAPTERS[0]] = '\n'.join([host, *(texts['plugin/adapters/' + name] for name in PHASE_GUIDANCE)])
    effective[ADAPTERS[1]] = mobile + '\n' + texts['plugin/adapters/mobile-workflows.md']
    obligations = {
        ADAPTERS[0]: ['canonical skill owns workflow', 'never use a file read as an invocation fallback',
                     'never restart task routing', 'consumer or external skill', 'List length sets', 'never an implicit replacement', 'effort setting',
                     'project-local `.hstack/models.md`', 'No translation grants new authority',
                     'mark the seat blocked', 'Do not execute it without installation authority',
                     'Supply absolute paths',
                     '`Comment Sicko` to `hugues-comment-sicko`',
                     'Do not substitute a generic worker without those rules',
                     'All 59 top-level skills are registered',
                     'preserve `generalPurpose`', 'Do not replace these workers with `hugues-agent`',
                     'Registration grants no permission to process personal transcripts',
                     'TypeScript paths remain `**/*.ts` and `**/*.tsx`',
                     'automate-me history mining remains blocked',
                     'Reflect retains the pinned current-session digest fallback',
                     'Preserve Recall\'s\nexplicit state-capsule shortcut'],
        ADAPTERS[1]: ['For all other work, follow the pinned core unchanged', 'For mobile bug fixes',
                     'For mobile arena work', 'Intent before domain', 'Large, cross-cutting, unmatched',
                     'First select\nthe core action playbook',
                     'they never replace core todos or implementation gates',
                     'observe RED against unfixed production', 'separate\nfresh production worker',
                     'same\nregression', 'Keep the rubric', 'block blind judging',
                     'top 3–5', 'Maintenance covers the whole map',
                     'cannot replace or satisfy the core', 'One target does not prove'],
    }
    for path, markers in obligations.items():
        for marker in markers:
            if marker.casefold() not in effective[path].casefold():
                errors.append(path + ': lost override boundary: ' + marker)
    return errors


# Native-reach lint. A user-only skill cannot be invoked by a model, so agent-facing text
# must never tell an agent to reach one natively or through the host; the agent reads its
# SKILL.md instead (host.md states that rule once). Reviews of PR 1 found the same
# contradiction in rounds one to four, each time in a spelling the previous lint missed, so
# the lint works on whole clauses and on these kinds of evidence, each independent of the
# others:
#   * a skill named in the USER_ONLY table (the only list; never a second copy);
#   * a class word that stands for user-only skills ("principles", "bundled", "dependency");
#   * a phrase that promises native reach without naming any skill ("native context");
#   * a reach word aimed at skills with no class named at all ("native invocation for
#     skills"), where a "consumer" elsewhere in the clause qualifies something else;
#   * a read told to cover any bundled skill, which includes the two native-only ones.
# Known limit, pinned in tests/native_reach_corpus.py: a prohibition that names no skill and
# no class ("never substitute direct body reads") is not caught, because the same words are
# correct in host.md's "for those skills" form and in a consumer project-skill template.
NATIVE_REACH_TRIGGER = re.compile(
    r'\binvo[ck]\w*|\bnatively\b|\bauto-?load\w*|\bskill tool\b'
    r'|\bnative[\s-]+(?:invo\w*|skill|context|host|mechanism|entry)\b'
    r'|\bnative\s+\S+\s+(?:skill|entry)\b'
    # Reach left to the host: "let the host load X", "host loading", "loaded by the host".
    r'|\b(?:host|harness)(?:\'s)?[\s-]+(?:auto-?)?(?:load|inject|attach|activat|surfac)\w*'
    r'|\b(?:load|inject|attach|activat|surfac)\w*\s+(?:\w+\s+){0,3}?(?:by|through|via)\s+the\s+(?:host|harness)\b'
    r'|\b(?:host|harness)\s+(?:to\s+)?(?:load|inject|attach|activate|surface)\b', re.I)
# Names of a tier or a policy field state a property, never an instruction to invoke.
NATIVE_REACH_PROPERTY = re.compile(
    r'(?:disable-)?model-invoc\w*|allow_implicit_invocation|implicit[\s-]+invoc\w*', re.I)
NATIVE_REACH_UNSCOPED = re.compile(r'\bnative[\s-]+(?:skill|context)\b|\bskill invocations?\b', re.I)
# "bundled" and the principle family are always user-only, so no qualifier excuses them.
NATIVE_REACH_STRONG_CLASS = re.compile(
    r'\bprinciples?\b|\bprinciple-\*|\bbundled\b|\buser-only\b', re.I)
# The object of a reach word is "skills" and nothing narrows it: no consumer, external,
# project, native-only or "those" in front. Only determiners may sit between, so this is
# independent of a "consumer" that appears elsewhere in the clause.
NATIVE_REACH_BARE_SKILLS = re.compile(
    r'\b(?:invocation|invoke|invoking|invokes|natively|load|loading|loads)\s+(?:(?:of|for)\s+)?'
    r'(?:(?:all|any|every|each|the|other|these|your)\s+)*skills?\b', re.I)
# A read told to cover "any bundled skill" also covers the two native-only bundled skills.
NATIVE_REACH_OVERBROAD_READ = re.compile(
    r'\bread(?:s|ing)?\s+(?:(?:any|every|each|all)\s+(?:other\s+)?)bundled\s+skills?\b', re.I)
# These also describe consumer and external skills, so a clause that scopes itself to
# "consumer" or "external" skills (the native-only tier) is excused.
NATIVE_REACH_WEAK_CLASS = re.compile(
    r'\b(?:public|other)\s+leaf\b|\bleaf\s+(?:skill|principle)s?\b|\bleaves\b|\bpublic skills?\b'
    r'|\bdependenc(?:y|ies)\b|\bsibling\s+(?:skills?|bodies|body)\b', re.I)
NATIVE_REACH_SCOPE = re.compile(r'\b(?:consumer|external)\b', re.I)
# Skill names that are also ordinary English words count only when formatted as a name
# (`code`, **bold**, /slash, [link]), followed by "skill", or placed directly beside the
# invocation word ("invoke swarm", "swarm natively"); every other name matches bare.
PLAIN_WORD_SKILLS = {'architect', 'arena', 'bro', 'correct', 'how', 'interrogate', 'recall',
                     'reflect', 'swarm', 'teach', 'why'}
# Clauses reviewed and confirmed NOT to instruct native reach, though a trigger and a user-only
# name both land in them: each one says native reach is disabled, never that an agent should
# rely on it. Whitespace-normalized exact match on one clause.
NATIVE_REACH_ALLOWLIST = {
    "`disable-model-invocation: true` disables typescript-best-practices' preserved `paths` "
    "auto-load, so reading or editing those files reads its SKILL.md in full first, as the "
    "scoped bundled reference, then principle-type-system-discipline's the same way.",
}
MARKDOWN_BLOCK_START = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s|^\s*#|^\s*\||^\s*```')
SENTENCE_BREAK = re.compile(r'(?<=[.!?])\s+')
FRONTMATTER = re.compile(r'\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)', re.S)


def markdown_clauses(text):
    """Yield each clause of authored prose: one Markdown block (paragraph, list item, table
    row, heading or code line) at a time, wrapped lines rejoined, then one sentence at a
    time, then split at semicolons. A hyphen at a line end joins to the next word."""
    blocks, current = [], []
    for line in text.splitlines():
        if not line.strip() or MARKDOWN_BLOCK_START.match(line):
            if current:
                blocks.append(current)
            current = []
        if line.strip():
            current.append(line.strip())
    if current:
        blocks.append(current)
    for block in blocks:
        joined = re.sub(r'(?<=\w)-\s+(?=\w)', '-', ' '.join(block))
        for sentence in SENTENCE_BREAK.split(' '.join(joined.split())):
            for clause in sentence.split(';'):
                if clause.strip():
                    yield clause.strip()


def skill_name_pattern(name):
    escaped = re.escape(name)
    if name in PLAIN_WORD_SKILLS:
        article = r'(?:(?:the|each|every|any|a|an)\s+)?'
        return (r'`/?' + escaped + r'`|\*\*' + escaped + r'\*\*|(?<![\w-])/' + escaped
                + r'(?![\w-])|\[' + escaped + r'\]|(?<![\w-])' + escaped + r' skills?\b|\bskill '
                + escaped + r'\b'
                + r'|\binvo[ck]\w*\s+' + article + escaped + r'(?![\w-])'
                + r'|(?<![\w-])' + escaped + r'\s+natively\b'
                + r'|\bnative(?:ly)?[\s-]+' + article + escaped + r'(?![\w-])')
    return r'(?<![\w-])' + escaped + r'(?![\w-])'


def native_reach_violations(text, own=None):
    """Return the clauses of `text` that tell an agent to reach a user-only skill natively.
    `own` is the skill whose files hold the text: a skill may name itself. The unit is one
    clause, so a reach word and a skill (or class word) split across clauses are not tied
    together; that is why host.md states the rule once and the corpus in
    tests/native_reach_corpus.py pins every spelling reviewers have found so far."""
    names = sorted((n for n in USER_ONLY if n != own), key=len, reverse=True)
    found = []
    for clause in markdown_clauses(text):
        stated = NATIVE_REACH_PROPERTY.sub(' ', clause)
        if clause in NATIVE_REACH_ALLOWLIST:
            continue
        if NATIVE_REACH_OVERBROAD_READ.search(stated):
            found.append(clause)
            continue
        if not NATIVE_REACH_TRIGGER.search(stated):
            continue
        if NATIVE_REACH_BARE_SKILLS.search(stated):
            found.append(clause)
            continue
        scoped = bool(NATIVE_REACH_SCOPE.search(stated))
        named = any(re.search(skill_name_pattern(n), stated) for n in names)
        if (named or NATIVE_REACH_STRONG_CLASS.search(stated)
                or (not scoped and (NATIVE_REACH_WEAK_CLASS.search(stated)
                                    or NATIVE_REACH_UNSCOPED.search(stated)))):
            found.append(clause)
    return found


def native_reach_errors(root):
    """Fail when agent-facing text under plugin/ instructs reaching a USER_ONLY skill through
    native invocation, native context or auto-load. Frontmatter is metadata, not an
    instruction, so it is skipped; the tier it declares is checked against USER_ONLY elsewhere."""
    errors = []
    skills = root / 'plugin/skills'
    for path in sorted((root / 'plugin').rglob('*.md')):
        text = FRONTMATTER.sub('', path.read_text(), count=1)
        own = path.relative_to(skills).parts[0] if path.is_relative_to(skills) else None
        for clause in native_reach_violations(text, own):
            errors.append(path.relative_to(root).as_posix() + ': ' + clause)
    return errors


def router_section_errors(root):
    """The router keeps every section a sibling points at, and its Principles index keeps
    one entry per principle skill: after the skill-list tiering that index is the only
    pointer to the 24 user-only principles."""
    router = (root / ROUTER).read_text()
    headings = set(re.findall(r'^## (.+?)\s*$', router, re.M))
    errors = ['router section missing: ' + name for name in ROUTER_SECTIONS if name not in headings]
    for path, name, words in ROUTER_SECTION_POINTERS:
        if words not in ' '.join((root / path).read_text().split()):
            errors.append(path + ' no longer says "' + words + '"; update ROUTER_SECTION_POINTERS')
        elif name not in headings:
            errors.append(path + ' points at router section "' + name + '", which is missing')
    named = principle_entry_names(section(router, 'Principles'))
    for skill in sorted(p.name for p in (root / 'plugin/skills').glob('principle-*')):
        if skill not in named:
            errors.append('router Principles index lacks a trigger entry for ' + skill)
    return errors


def principle_entry_names(index):
    """pstack's naming rule: an entry's leaf is **principle-<title>**, the bold title in kebab
    case with hyphens kept and other punctuation dropped, unless the entry gives its name."""
    names = set()
    for title, given in re.findall(r'^- \*\*([^*]+?)(?:\.\*\*|\*\* \(\*\*(principle-[a-z0-9-]+)\*\*\)\.) \S',
                                   index, re.M):
        names.add(given or 'principle-' + re.sub(r'[^a-z0-9 -]', '', title.lower()).replace(' ', '-'))
    return names


def current_document_errors(texts):
    errors = []
    plan = texts['docs/PLAN.md']
    guide = texts['docs/upstream/README.md'].split('# Upstream sync', 1)[0]
    for name, text, count in [('docs/PLAN.md', plan, 50), ('docs/upstream/README.md', guide, 54)]:
        if not all(marker in text for marker in [f'all {count} top-level skills', 'both upstream agents']):
            errors.append(name + ': incomplete current inventory')
        if re.search(r'(?:47|three excluded|families inactive)', text, re.I):
            errors.append(name + ': stale current exclusions')
    if '9 October, GMT+7' not in plan:
        errors.append('docs/PLAN.md: changed original deadline')
    return errors


def mobile_route_errors(texts):
    errors = []
    for name, text in texts.items():
        before_steps = text.split('## Steps', 1)[0]
        if not all(marker in before_steps for marker in
                   ['selected core action playbook', 'ordered todos verbatim',
                    'Do not execute this extension in place of the core procedure']):
            errors.append(name + '-core-composition')
        match = re.search(r'^3\. (.*?)(?=^4\. |\Z)', text, re.M | re.S)
        implementation = match.group(1) if match else ''
        if not all(marker in implementation for marker in
                   ['selected core implementation gate', 'configured role models',
                    '[arena](../../arena/SKILL.md) in full', 'complete the implementation arena',
                    'Mandatory: no skip-with-reason escape',
                    'Design-only synthesis cannot satisfy this implementation gate',
                    'even within one function', 'core scoped-worker exception']):
            errors.append(name + '-implementation-arena')
    return errors


def check(root=ROOT):
    require(not root.is_symlink(), 'unsafe repository root')
    root = root.resolve()
    require(not any(p.is_symlink() for p in root.rglob('*') if '.git' not in p.parts),
            'unsafe repository symlink')
    spec = importlib.util.spec_from_file_location('native_upstream', root / 'scripts/upstream-diff.py')
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    snapshot = upstream.read_pin(root / 'docs/upstream/pin.json')
    require(snapshot['revision'] == PIN and snapshot['file_count'] == 200, 'upstream pin differs')
    receipt = upstream.load(root / 'docs/upstream/consolidation.json')
    require(receipt['schema_version'] == 1 and receipt['upstream_revision'] == PIN,
            'consolidation pin differs')
    require(not (root / 'plugin/core').exists() and not (root / 'plugin/core-bindings.json').exists(),
            'retired runtime core or registry present')
    archive = root / 'provenance/upstream/pstack-0.15.32.tar.gz'
    require(receipt['archive'] == archive.relative_to(root).as_posix() and not archive.is_symlink()
            and hashlib.sha256(archive.read_bytes()).hexdigest() == receipt['archive_sha256'],
            'upstream archive differs')
    expected = {r['path']: r for r in snapshot['files']}
    original_bodies = {}
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        require(len(members) == len(expected) and {m.name for m in members} == set(expected),
                'upstream archive inventory differs')
        for member in members:
            require(member.isfile(), 'unsafe upstream archive entry')
            body = tar.extractfile(member).read()
            original_bodies[member.name] = body
            row = expected[member.name]
            require(member.mode == int(row['mode'][-3:], 8) and len(body) == row['size']
                    and hashlib.sha256(body).hexdigest() == row['sha256']
                    and upstream.oid('blob', body) == row['blob_sha'], 'upstream archive bytes/mode differ')
    rows = receipt['files']
    require(len(rows) == len(expected) and {r['source'] for r in rows} == set(expected),
            'consolidation source coverage differs')
    destinations = [r['destination'] for r in rows if r['destination']]
    require(len(destinations) == len(set(destinations)), 'duplicate canonical destination')
    for row in rows:
        original = expected[row['source']]
        source = row['source'].removeprefix('pstack/')
        if source.startswith('skills/'):
            parts = source.split('/')
            parts[1] = ALIASES.get(parts[1], parts[1])
            destination = 'plugin/' + '/'.join(parts)
            if source.endswith('/scripts/worktree-audit.sh'):
                destination = None
        elif source.startswith('agents/'):
            destination = next(v['entrypoint'] for v in AGENTS.values() if v['source'] == row['source'])
        elif source.startswith('docs/harness/'):
            # pstack's adapter for running a Cursor-first plugin in Claude Code; hStack is native there.
            destination = None
        elif source.startswith('docs/'):
            destination = 'docs/pstack/' + source.removeprefix('docs/')
        elif source == 'LICENSE':
            destination = 'plugin/PSTACK-LICENSE'
        else:
            destination = None
        require(row['destination'] == destination and row['disposition'] ==
                ('canonical' if destination else 'provenance-only'), 'canonical source identity differs')
        require(row['source_sha256'] == original['sha256']
                and row['source_mode'] == int(original['mode'][-3:], 8), 'source provenance differs')
        if row['destination']:
            path = root / upstream.destination_path(row['destination'])
            require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root),
                    'missing/unsafe canonical destination')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row['destination_sha256'],
                    'canonical destination bytes differ: ' + row['destination'])
            require(stat.S_IMODE(path.stat().st_mode) == row['source_mode'], 'canonical source mode differs')
    names = {ALIASES.get(Path(name).parts[2], Path(name).parts[2]) for name in expected
             if len(Path(name).parts) == 4 and name.endswith('/SKILL.md')}
    require(len(names) == 58 and not names & set(EXTERNAL_SKILLS), 'pstack skill inventory differs')
    names |= set(EXTERNAL_SKILLS) | set(AUTHORED_SKILLS)
    require(receipt.get('authored_skills') == AUTHORED_SKILLS, 'authored skill inventory differs')
    require(set(receipt['public_skills']) == names, 'public skill inventory differs')
    external_errors = external_skill_errors(root, receipt, upstream)
    require(not external_errors, '; '.join(external_errors))
    require(receipt.get('host_invocation', {}).get('user_only') == sorted(USER_ONLY),
            'host invocation receipt differs')
    declarations = list((root / 'plugin').rglob('SKILL.md'))
    require({p.relative_to(root).as_posix() for p in declarations} ==
            {f'plugin/skills/{name}/SKILL.md' for name in names}, 'registered skill inventory differs')
    for path in declarations:
        text = path.read_text()
        name = path.parent.name
        fields = native_frontmatter(text)
        require(fields.get('name') == name, 'native name differs: ' + name)
        manual = fields['disable-model-invocation']
        require(not DEAD_FRONTMATTER & fields.keys(), 'dead frontmatter field: ' + name)
        upstream_name = next((old for old, new in ALIASES.items() if new == name), name)
        if name in AUTHORED_SKILLS:
            original_fields = AUTHORED_SKILLS[name]
        elif name in EXTERNAL_SKILLS:
            original_fields = {}
        else:
            original_fields = native_frontmatter(
                original_bodies[f'pstack/skills/{upstream_name}/SKILL.md'].decode())
        require(manual == (name in USER_ONLY), 'host invocation table differs: ' + name)
        require(fields.get('paths') == original_fields.get('paths'), 'native path scope differs: ' + name)
        require((path.parent / 'agents/openai.yaml').read_text() ==
                'policy:\n  allow_implicit_invocation: ' + str(not manual).lower() + '\n',
                'native invocation policy differs: ' + name)
        if not name.startswith('principle-'):
            require('The host contract governs how this skill reaches any sibling dependency.' in text
                    and '[host contract](../../adapters/host.md)' in text,
                    'native dependency boundary missing: ' + name)
    for relative in ['skills/hugues-mode/playbooks/mobile-proof.md',
                     'skills/hugues-mode/references/mobile-lanes.md',
                     'skills/hugues-mode/references/jev-drive.md']:
        text = (root / 'plugin' / relative).read_text()
        require(not re.search(r'(?:read|Read)[^\n]*directly[^\n]*(?:invocation|disabled)', text),
                'consumer skill invocation bypass: ' + relative)
    manifest = upstream.load(root / 'plugin/.claude-plugin/plugin.json')
    require(manifest['skills'] == ['./skills'] and manifest['agents'] ==
            ['./agents/hugues-agent.md', './agents/hugues-comment-sicko.md'], 'manifest wiring differs')
    require({p.name for p in (root / 'plugin/agents').glob('*.md')} ==
            {'hugues-agent.md', 'hugues-comment-sicko.md'}, 'registered agent inventory differs')
    require(receipt['agents'] == AGENTS, 'specialized agent binding differs')
    source_map = {r['source']: r['destination'] for r in rows}
    require(receipt['worker_roles'] == {role: {**row, 'prompt': source_map[row['prompt']]}
            for role, row in worker_roles().items()}, 'worker role wiring differs')
    playbooks = {p.stem for p in (root / 'plugin/skills/hugues-mode/playbooks').glob('*.md')}
    original_playbooks = {Path(p).stem for p in expected
                         if p.startswith('pstack/skills/poteto-mode/playbooks/')}
    require(playbooks == original_playbooks | {'build-doctor', 'mobile-proof', 'kmp-bridge-change',
                                              'cmp-two-target-change'}, 'playbook inventory differs')
    bodies = {name: (root / 'plugin/skills' / ALIASES.get(name, name) / 'SKILL.md').read_text()
              for name in ['architect', 'arena', 'interrogate', 'create-verification-skill',
                           'maintain-verification-skill', 'swarm', 'show-me-your-work',
                           'setup-pstack', 'poteto-mode', 'tdd']}
    bodies['feature'] = (root / 'plugin/skills/hugues-mode/playbooks/feature.md').read_text()
    require(not behavior_errors(bodies), 'workflow behavior differs: ' + ', '.join(behavior_errors(bodies)))
    router_errors = router_section_errors(root)
    require(not router_errors, 'router sections differ: ' + '; '.join(router_errors))
    cursor_models = sorted(p.relative_to(root).as_posix() for p in (root / 'plugin').rglob('*.md')
                           if re.search(r'pstack-models\.mdc|\.cursor/rules|grok-\d|claude-opus-\d-\d-max|gpt-\d\.\d-sol-max',
                                        p.read_text()))
    require(not cursor_models, 'Cursor model wiring in installed skills: ' + ', '.join(cursor_models))
    texts = {p: (root / p).read_text() for p in [*ADAPTERS, *ADAPTER_RESOURCES]}
    require(not adapter_errors(texts), 'adapter behavior differs: ' + '; '.join(adapter_errors(texts)))
    reach_errors = native_reach_errors(root)
    require(not reach_errors, 'user-only skill promised native reach: ' + '; '.join(reach_errors))
    mobile = {name: (root / f'plugin/skills/hugues-mode/playbooks/{name}.md').read_text()
              for name in ['kmp-bridge-change', 'cmp-two-target-change']}
    require(not mobile_route_errors(mobile), 'mobile workflow gates differ')
    installed = {}
    for path in (root / 'plugin').rglob('*'):
        relative = path.relative_to(root / 'plugin').as_posix()
        if relative.startswith('adapters/runtime/__pycache__/') and path.suffix == '.pyc' and not path.is_symlink():
            continue
        require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'unsafe installed path')
        if path.is_file():
            installed[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'mode': stat.S_IMODE(path.stat().st_mode)}
    require(installed == receipt['installed_files'], 'installed inventory/bytes/mode differs')
    helpers = upstream.load(root / 'docs/HELPER-INPUTS.json')
    require(helpers['source_revision'] == PIN and {r['source'] for r in helpers['files']} ==
            {p for p in expected if p.startswith('pstack/skills/poteto-mode/scripts/')},
            'helper input coverage differs')
    for row in helpers['files']:
        require(row['source_sha256'] == expected[row['source']]['sha256'], 'helper source differs: ' + row['source'])
        if row['installed'] is None:
            require(row['candidate_sha256'] is None and source_map[row['source']] is None,
                    'provenance-only helper differs: ' + row['source'])
            continue
        require(row['installed'] == source_map[row['source']], 'helper destination differs: ' + row['source'])
        actual = installed[row['installed'].removeprefix('plugin/')]['sha256']
        require(actual == row['candidate_sha256'] and row['same_bytes_as_upstream'] ==
                (actual == row['source_sha256']), 'helper input receipt is stale: ' + row['installed'])
    bootstrap = ast.parse((root / 'plugin/adapters/host_tools.py').read_text())
    anchor = next(ast.literal_eval(n.value) for n in bootstrap.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'RUNTIME_SHA256' for t in n.targets))
    require(anchor == {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (root / 'plugin/adapters/runtime').glob('*.py')}, 'runtime anchor differs')
    payload_path = root / 'plugin/adapters/runtime/payload.json'
    payload = upstream.load(payload_path)
    anchors = {'adapters/runtime/payload.json', 'adapters/runtime/payload.py', 'adapters/host_tools.py'}
    require(payload == {'schema_version': 2, 'revision': 'hstack-native-v1',
        'upstream_revision': PIN,
        'legacy_paths': {s: d.removeprefix('plugin/') for s, d in source_map.items() if d and d.startswith('plugin/')},
        'files': [{'path': p, 'sha256': row['sha256'], 'mode': '100'+format(row['mode'], '03o')}
                  for p, row in sorted(installed.items()) if p not in anchors]}, 'installed payload manifest differs')
    require("MANIFEST_SHA256 = '" + hashlib.sha256(payload_path.read_bytes()).hexdigest() + "'" in
            (root / 'plugin/adapters/runtime/payload.py').read_text(), 'payload anchor differs')
    return {'upstream_archive_files': 200, 'active_skills': len(names), 'core_playbooks': 23,
            'mobile_playbooks': 4, 'core_agents': 2, 'worker_roles': 15}


if __name__ == '__main__':
    try:
        print('PASS: source provenance + canonical workflows + installed integrity',
              check(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT))
    except (ValueError, OSError, KeyError, TypeError, tarfile.TarError) as exc:
        print('native distribution rejected: ' + str(exc), file=sys.stderr)
        sys.exit(1)
