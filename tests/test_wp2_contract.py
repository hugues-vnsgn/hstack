"""Static package contracts, not a simulation or observation of model routing.

The literal hashes below were computed from the independently verified pstack
0.15.9 input. Tests need no network access or private/local upstream checkout.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from release_snapshot import release_root
ROOT = release_root()
PIN = 'e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a'
MODE = Path('plugin/skills/hugues-mode')
PLAYBOOKS = {
    'investigation', 'bug-fix', 'feature', 'prototype', 'refactoring',
    'visual-parity', 'authoring-a-skill', 'session-pickup', 'pause-safely',
    'opening-a-pr', 'build-doctor', 'mobile-proof', 'kmp-bridge-change',
    'cmp-two-target-change',
}
ADAPTED_PLAYBOOKS = PLAYBOOKS - {
    'build-doctor', 'mobile-proof', 'kmp-bridge-change', 'cmp-two-target-change',
}
PRINCIPLE_SHA256 = {'principle-attack-the-premise': 'c87bd7536f772f8a403ad8155535ee17a1bbec9a353156693eb3bb1520c87ae3',
 'principle-boundary-discipline': '62ac2862c2caa22dd14531f51c9c6bb445ceb198ca98a687e25b4d47c1f10a28',
 'principle-build-the-lever': '458b269eab8e95a1573276955312f7d2a13ae8599879a9efc748248f6bc34b56',
 'principle-encode-lessons-in-structure': '77044c83a9ac6df78fc643887ea5f1f11f082adaf14b717c060cdaed03cce863',
 'principle-exhaust-the-design-space': '8583310d7297b7823d75494faa57b003564d436807febecdecbd8321abe5cf6e',
 'principle-experience-first': '58903529d733b1c1a7c9ccf127d45ef3c7d0d9f0b81164a4dc6b80efe6f2912b',
 'principle-explain-the-number': '5aac99e7ce0bb1b37e2579acf4fe88c32a1456d9d46afd4a57cfe1df9092e89c',
 'principle-fix-root-causes': 'ba4cd38da1dcc8fe5432feb64457cba95594736a9b21b2ebf8f8c52aee068707',
 'principle-foundational-thinking': '864b827e8199d946ce58beca0f89c4ed4099ed6e426fb698a3aaa45de2a9eea2',
 'principle-guard-the-context-window': 'd2cef147862576e3d709b7afc149d85196245e8338b9c7eef337c95fba412b3e',
 'principle-laziness-protocol': '9006579e9e3f33955d17569733db688ae65f22577dc3b21803d219a5a8445aff',
 'principle-make-operations-idempotent': '540738217c3da7bf513b9886924ad6a2bc77e58be867f5bd2e1831c74bf2ce70',
 'principle-migrate-callers-then-delete-legacy-apis': '09978915a4a11990cf0a9a02d9c08cc59e0b7a04c5c24b83aa560fbe4146f75b',
 'principle-minimize-reader-load': '42551c5dc74cd578163c148da552db3ff67d29b78600ef216bfd311fb828fe69',
 'principle-model-the-domain': 'bbadbb9a723fac3f76e782ae45665eb94058ec10993e4bae36d4dc6b0e4eac07',
 'principle-never-block-on-the-human': 'f2764bb9338cbfc788c903cf4b9cd0a5f4042d3a04dd6d59cbd525d9beaadd0a',
 'principle-outcome-oriented-execution': '10eb91633aa570355ba4bb37088fcade2b22e498df7a58edc749e65bc5a78e2d',
 'principle-prove-it-works': 'ec79a15025bac8d33d62011c54f3b612733fd2a024e623b531b3637aa75070e2',
 'principle-redesign-from-first-principles': 'a1c7fd0a96b40e12a74bceb0e6bb20a9666dd844dcabfb624acb27da23b929fe',
 'principle-separate-before-serializing-shared-state': '05294b40448e927c5da1c7b6f5c6b9fed3744637e3833d2d948b9154a9dd00bb',
 'principle-sequence-verifiable-units': '2ccbbacc56ace5afdfb8670cef19d7bd009fb2a0033b9a741cbdf2b6baf72187',
 'principle-subtract-before-you-add': 'a983a50e732c1ed315eba7aaf47a61329e31c4794eb1ab9d25d9945265b31e03',
 'principle-test-behavior-not-implementation': '87e40efe4e486f7ea639d2ed1fc0abe6c93b8fd0e89a81218086909d2470a52e',
 'principle-type-system-discipline': 'c83da8031ffb4c86410030d3e261f659598fca2b7d8158fd9dc269d70a3a025e'}


INTERROGATE_REFERENCE_SHA256 = {
    'code-quality-review.md': '79162fda183eafd40d51661fbb5e151c7ba250f89e506ba17f5bd135dcbd50a8',
    'lead-judgment.md': '6e5bdf5670eb34017692e9b6c546f36ac7552e6bb9f3f2f3429164fcc46a9361',
    'reviewer-prompt.md': 'e0598e254792b56de39bb16b1e6db559b03a522fdc54b98f942d254090920ae6',
    'rubric.md': 'a85aa801abbaf14434f00579440abc0d8e2723227ba8bf57de7cca8d6e7d2f25',
}
# Literal expected answers, independent of the routing instructions under test.
ACCEPTANCE_ROUTES = {
    'ios-badge-bug': 'bug-fix',
    'android-action-feature': 'feature',
    'kmp-boundary-bug': 'kmp-bridge-change',
    'other-host-review': 'interrogate',
    'swift-refactor': 'refactoring',
    'cmp-prototype': 'prototype',
    'pause-kmp-fix': 'pause-safely',
    'resume-ios-fix': 'session-pickup',
    'explain-ios-no-changes': 'investigation',
    'open-pr-cmp-change': 'opening-a-pr',
    'verify-kmp-only': 'mobile-proof',
}


def section(text, heading):
    match = re.search(r'^## ' + re.escape(heading) + r'\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return match[1] if match else ''


def steps(text):
    return re.findall(r'^(\d+)\. (\S.*)$', section(text, 'Steps'), re.M)


def routes(text):
    result = {}
    for line in section(text, 'Routing table').splitlines():
        cells = [part.strip() for part in line.split('|')[1:-1]]
        if len(cells) != 3 or cells[0] in {'Route', '---'}:
            continue
        link = re.fullmatch(r'\[[^]]+\]\(([^)]+)\)', cells[2])
        if link:
            result[cells[0]] = (cells[1], link[1])
    return result


def assert_playbooks(case, root):
    paths = {p.stem: p for p in (root / MODE / 'playbooks').glob('*.md')}
    case.assertEqual(set(paths), PLAYBOOKS, 'WP2 exact playbook set')
    for name, path in paths.items():
        numbered = steps(path.read_text())
        case.assertTrue(numbered, f'{name}: missing nonempty numbered Steps')
        case.assertEqual([int(n) for n, _ in numbered], list(range(1, len(numbered) + 1)),
                         f'{name}: nonconsecutive Steps')


def assert_routes(case, root):
    table = routes((root / MODE / 'SKILL.md').read_text())
    expected = {name: 'playbooks/' + name + '.md' for name in PLAYBOOKS}
    expected['interrogate'] = '../interrogate/SKILL.md'
    case.assertEqual(set(table), set(expected), 'WP2 exact route set')
    for name, file in expected.items():
        case.assertEqual(table[name][1], file, f'{name}: incorrect route file')
        case.assertTrue(table[name][0], f'{name}: missing route trigger')
        case.assertTrue((root / MODE / file).is_file(), f'{name}: route file missing')
    fixtures = json.loads((root / 'tests/fixtures/wp2-routing-prompts.json').read_text())
    case.assertEqual({item['id']: item['expected_route'] for item in fixtures['cases']},
                     ACCEPTANCE_ROUTES, 'literal route acceptance answers')
    case.assertEqual(len(fixtures['cases']), len(ACCEPTANCE_ROUTES),
                     'unique literal route acceptance prompts')
    for item in fixtures['cases']:
        case.assertEqual(table[item['expected_route']][1], item['expected_file'],
                         f"{item['id']}: acceptance file differs from route table")
        case.assertTrue(item['prompt'] and item['expected_domain'] and item['expected_proof'])


def assert_intent_precedence(case, root):
    precedence = section((root / MODE / 'SKILL.md').read_text(), 'Routing precedence')
    # Inspect the authored order only; model selection is established by a host probe.
    bullets = [line for line in precedence.splitlines() if line.startswith('- ')]
    first = {}
    for position, bullet in enumerate(bullets):
        for route in re.findall(r'`([^`]+)`', bullet):
            first.setdefault(route, position)
    intent_routes = {'pause-safely', 'session-pickup', 'opening-a-pr', 'investigation',
                     'mobile-proof', 'visual-parity', 'authoring-a-skill', 'prototype',
                     'refactoring', 'interrogate', 'build-doctor'}
    implementation_routes = {'cmp-two-target-change', 'kmp-bridge-change', 'bug-fix', 'feature'}
    case.assertTrue(intent_routes | implementation_routes <= set(first),
                    'explicit intent and implementation precedence rules required')
    for intent in intent_routes:
        for implementation in implementation_routes:
            case.assertLess(first[intent], first[implementation],
                            f'{intent}: intent must precede {implementation}')
    case.assertLess(first['mobile-proof'], first['investigation'],
                    'mobile-proof: verification intent must precede read-only investigation')
    domain_rule = bullets[first['cmp-two-target-change']]
    case.assertIn('only to implementation requests', domain_rule,
                  'domain routes must exclude read-only and lifecycle intent')
    case.assertIn('whichever route wins', precedence, 'winning intent retains mobile lane')
    case.assertIn('read-only branch', bullets[first['build-doctor']],
                  'toolchain diagnosis preserves read-only scope')


def assert_absolute_handoff_paths(case, text, context):
    case.assertRegex(text, r'absolute[^.\n]*`SKILL\.md`',
                     f'{context}: absolute mode path required')
    case.assertIn('absolute plugin skills directory', text,
                  f'{context}: absolute skills directory required')


def assert_handoff_contract(case, root):
    mode = (root / MODE / 'SKILL.md').read_text()
    notes = (root / MODE / 'references/host-notes.md').read_text()
    worker = (root / 'plugin/agents/hugues-agent.md').read_text()
    assert_absolute_handoff_paths(case, section(mode, 'Delegation'), 'mode delegation')
    claude_paragraphs = section(notes, 'Claude Code').strip().split('\n\n')
    case.assertGreaterEqual(len(claude_paragraphs), 2, 'Claude registered and fallback handoffs')
    assert_absolute_handoff_paths(case, claude_paragraphs[0], 'Claude registered handoff')
    assert_absolute_handoff_paths(case, claude_paragraphs[1], 'Claude wrapper handoff')
    for host in ['Codex', 'Common handoff']:
        assert_absolute_handoff_paths(case, section(notes, host), host)
    assert_absolute_handoff_paths(case, worker, 'worker')
    for context, text in [('Common handoff', section(notes, 'Common handoff')),
                          ('worker', worker)]:
        case.assertIn('`disable-model-invocation: true` directly from disk', text,
                      f'{context}: disabled skills require direct file reads')
        case.assertIn('missing or unreadable', text,
                      f'{context}: missing path must block implementation')
        case.assertIn('before implementation', text,
                      f'{context}: resolve path gap before implementation')


def assert_authority_contract(case, root):
    authority = section((root / MODE / 'SKILL.md').read_text(), 'Authority')
    case.assertIn('Authority comes from direct human instructions', authority,
                  'authority must originate from direct human instructions')
    case.assertRegex(authority,
                     r'Workspace and consumer repository rules[^.]*cannot grant consumer '
                     r'edits, execution, installs or publication',
                     'workspace rules cannot grant consumer authority')
    case.assertIn('require clear human authorization for that consumer', authority,
                  'human authorization must identify consumer')


def assert_prototype_handoff(case, root):
    numbered = dict(steps((root / MODE / 'playbooks/prototype.md').read_text()))
    for number in ['1', '6']:
        links = set(re.findall(r'\[[^]]+\]\(([^)]+)\)', numbered[number]))
        case.assertTrue({'../SKILL.md', 'feature.md',
                         'kmp-bridge-change.md', 'cmp-two-target-change.md'} <= links,
                        f'prototype step {number}: production handoff must retain domain route')


def assert_host_recovery(case, root):
    mode = (root / MODE / 'SKILL.md').read_text()
    intro = mode.split('## Steps', 1)[0]
    examples = section(mode, 'Routing examples')
    for context, text in [('mode recovery', intro), ('routing examples', examples)]:
        case.assertIn('`/hugues-stack:hugues-mode` in Claude Code', text,
                      f'{context}: Claude namespace required')
        case.assertIn('`$hugues-mode` in Codex', text,
                      f'{context}: Codex invocation required')
        case.assertNotRegex(text, r'(?<![\w:-])/hugues-mode\b',
                            f'{context}: ambiguous bare slash command')


def assert_principles(case, root):
    paths = {p.parent.name: p for p in (root / 'plugin/skills').glob('principle-*/SKILL.md')}
    case.assertEqual(set(paths), set(PRINCIPLE_SHA256), 'exact 24 principle set')
    index = section((root / MODE / 'SKILL.md').read_text(), 'Principles')
    links = re.findall(r'\[([^]]+)\]\(([^)]+)\)', index)
    expected_links = {(name, '../' + name + '/SKILL.md') for name in PRINCIPLE_SHA256}
    case.assertEqual(set(links), expected_links, 'complete inline principle index links')
    case.assertEqual(len(links), 24, 'principle index entries must be unique')
    for name, path in paths.items():
        case.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), PRINCIPLE_SHA256[name],
                         f'{name}: principle differs from pinned upstream bytes')


def assert_provenance(case, root):
    data = json.loads((root / 'docs/upstream/wp2-provenance.json').read_text())
    case.assertEqual(data['repository'], 'https://github.com/cursor/plugins')
    case.assertEqual(data['revision'], PIN, 'WP2 provenance pin')
    case.assertEqual(data['upstream_version'], '0.15.9')
    entries = {item['destination']: item for item in data['files']}
    case.assertEqual(len(entries), len(data['files']), 'provenance destination uniqueness')
    for name, sha in PRINCIPLE_SHA256.items():
        destination = f'plugin/skills/{name}/SKILL.md'
        case.assertIn(destination, entries, f'{name}: missing principle provenance')
        item = entries[destination]
        case.assertEqual(item['source'], f'pstack/skills/{name}/SKILL.md')
        case.assertEqual(item['disposition'], 'verbatim')
        case.assertEqual(item['sha256'], sha, f'{name}: incorrect pinned principle hash')
    for name, sha in INTERROGATE_REFERENCE_SHA256.items():
        destination = f'plugin/skills/interrogate/references/{name}'
        case.assertIn(destination, entries, f'{name}: missing reference provenance')
        item = entries[destination]
        case.assertEqual(item['source'], f'pstack/skills/interrogate/references/{name}')
        case.assertEqual(item['disposition'], 'verbatim')
        case.assertEqual(item['sha256'], sha, f'{name}: incorrect pinned reference hash')
    adapted = {
        'plugin/skills/hugues-mode/SKILL.md': 'pstack/skills/poteto-mode/SKILL.md',
        'plugin/agents/hugues-agent.md': 'pstack/agents/poteto-agent.md',
        'plugin/skills/interrogate/SKILL.md': 'pstack/skills/interrogate/SKILL.md',
    }
    adapted.update({str(MODE / 'playbooks' / (name + '.md')):
                    'pstack/skills/poteto-mode/playbooks/' + name + '.md'
                    for name in ADAPTED_PLAYBOOKS})
    for destination, source in adapted.items():
        case.assertIn(destination, entries, f'{destination}: missing adapted source mapping')
        case.assertEqual(entries[destination]['source'], source,
                         f'{destination}: incorrect adapted source mapping')
        case.assertEqual(entries[destination]['disposition'], 'adapted')
    for item in data['files']:
        case.assertTrue((root / item['destination']).is_file(), 'provenance destination missing')
        case.assertRegex(item['blob_sha'], r'^[a-f0-9]{40}$', 'invalid upstream blob SHA')
        case.assertRegex(item['sha256'], r'^[a-f0-9]{64}$', 'invalid upstream SHA-256')
        if item['disposition'] == 'verbatim':
            case.assertEqual(hashlib.sha256((root / item['destination']).read_bytes()).hexdigest(),
                             item['sha256'],
                             f"{item['destination']}: verbatim destination differs from receipt")



def assert_lanes_and_safeguards(case, root):
    lane_text = (root / MODE / 'references/mobile-lanes.md').read_text()
    lane_rows = {}
    for line in section(lane_text, 'Required lanes').splitlines():
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) == 4 and cells[0] not in {'Domain', '---'}:
            lane_rows[cells[0]] = ' '.join(cells[1:]).casefold().replace('-', ' ')
    fixtures = json.loads((root / 'tests/fixtures/wp2-routing-prompts.json').read_text())
    case.assertEqual(set(lane_rows), {'Swift/iOS', 'Kotlin/Android', 'KMP shared logic', 'CMP shared UI'},
                     'all four required mobile lanes')
    case.assertEqual({item['domain'] for item in fixtures['lanes']}, set(lane_rows),
                     'four independent lane acceptance cases')
    for item in fixtures['lanes']:
        for requirement in item['required']:
            case.assertIn(requirement.casefold().replace('-', ' '), lane_rows[item['domain']],
                          f"{item['domain']}: missing required lane proof {requirement}")
    outcomes = section(lane_text, 'Evidence and outcomes')
    for phrase in ['A skipped assertion is skipped, never passed',
                   'a retried or flaky assertion is flaky, never a clean pass',
                   'a wrong-target result is invalid for the requested target',
                   'zero relevant assertions is incomplete',
                   'A later pass does not erase a failed attempt']:
        case.assertIn(phrase, outcomes, 'mobile result classification safeguard')
    for requirement in ['argv array', 'exit code', 'Plugin SHA', 'consumer repo and SHA',
                        'outside the repository', 'artifact hash']:
        case.assertIn(requirement, outcomes, 'mobile evidence provenance requirement')
    authority = section(lane_text, 'Authority and discovery')
    case.assertIn('grants no consumer edit, copy, build, install or runtime authority', authority,
                  'consumer execution requires clear authority')
    case.assertIn('outside the plugin', authority, 'consumer source stays separate')
    case.assertIn('blockers', authority, 'system changes require separate authority')
    case.assertIn('no judged verdict', section(lane_text, 'Missing capabilities'),
                  'fallback must disclose missing judged proof')


def assert_worker_contract(case, root):
    worker = (root / 'plugin/agents/hugues-agent.md').read_text()
    metadata = re.match(r'\A---\n(.*?)\n---\n', worker, re.S)
    case.assertIsNotNone(metadata, 'worker frontmatter required')
    case.assertRegex(metadata[1], r'(?m)^name: hugues-agent$', 'worker identity')
    case.assertRegex(metadata[1], r'(?m)^description: \S.+$', 'worker description required')
    case.assertIn('../skills/hugues-mode/SKILL.md', worker, 'worker reads exact mode')
    case.assertIn('including its Principles index', worker, 'worker reads principles index')
    case.assertIn('Do not recursively delegate the same assignment.', worker,
                  'bounded worker must not self-delegate')
    mode = (root / MODE / 'SKILL.md').read_text()
    case.assertIn('When executing as an assigned scoped worker', section(mode, 'Delegation'),
                  'worker role must be distinguished from coordinator')
    case.assertIn('perform the assignment directly', section(mode, 'Delegation'))
    case.assertIn('A new task, retry or fix round normally gets a fresh worker', section(mode, 'Delegation'),
                  'fresh worker for each new work round')
    case.assertIn('It authorizes no delegate, edit, build, device drive or consumer command', section(mode, 'Steps'),
                  'route preview stops before execution')
    case.assertIn('require explicit authority', section(mode, 'Authority'),
                  'external actions require explicit authority')
    manifest = json.loads((root / 'plugin/.claude-plugin/plugin.json').read_text())
    case.assertIn('./agents/hugues-agent.md', manifest['agents'], 'worker registered in manifest')


class WP2StaticContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hstack-wp2-contract-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns('.git', '__pycache__', 'planning'))

    def test_exact_playbook_set_and_ordered_steps(self):
        assert_playbooks(self, self.repo)

    def test_route_table_covers_literal_acceptance_files(self):
        assert_routes(self, self.repo)

    def test_verbatim_principles_and_full_inline_index(self):
        assert_principles(self, self.repo)

    def test_pinned_principle_and_adapted_source_provenance(self):
        assert_provenance(self, self.repo)

    def test_changed_interrogate_reference_rejected(self):
        assert_provenance(self, self.repo)
        path = self.repo / 'plugin/skills/interrogate/references/rubric.md'
        path.write_bytes(path.read_bytes() + b'\nChanged review lens.\n')
        with self.assertRaisesRegex(AssertionError, 'verbatim destination differs from receipt'):
            assert_provenance(self, self.repo)

    def test_changed_reference_and_receipt_cannot_repin_upstream(self):
        assert_provenance(self, self.repo)
        path = self.repo / 'plugin/skills/interrogate/references/reviewer-prompt.md'
        path.write_bytes(path.read_bytes() + b'\nChanged review prompt.\n')
        def change(data):
            for row in data['files']:
                if row['destination'].endswith('/references/reviewer-prompt.md'):
                    row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.change_receipt(change)
        with self.assertRaisesRegex(AssertionError, 'incorrect pinned reference hash'):
            assert_provenance(self, self.repo)

    def test_domain_route_cannot_replace_literal_intent_answer(self):
        assert_routes(self, self.repo)
        path = self.repo / 'tests/fixtures/wp2-routing-prompts.json'
        data = json.loads(path.read_text())
        for item in data['cases']:
            if item['id'] == 'pause-kmp-fix':
                item.update(expected_route='kmp-bridge-change',
                            expected_file='playbooks/kmp-bridge-change.md')
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, 'literal route acceptance answers'):
            assert_routes(self, self.repo)

    def test_action_intent_precedes_domain_implementation(self):
        assert_intent_precedence(self, self.repo)

    def test_removed_lifecycle_precedence_rejected(self):
        assert_intent_precedence(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        text = path.read_text()
        precedence = section(text, 'Routing precedence')
        changed = '\n'.join(line for line in precedence.splitlines()
                            if '`pause-safely`' not in line)
        path.write_text(text.replace(precedence, changed + '\n'))
        with self.assertRaisesRegex(AssertionError, 'explicit intent and implementation precedence'):
            assert_intent_precedence(self, self.repo)

    def test_domain_before_pause_regression_rejected(self):
        assert_intent_precedence(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        text = path.read_text()
        precedence = section(text, 'Routing precedence')
        lines = precedence.splitlines()
        pause = next(line for line in lines if line.startswith('- ') and '`pause-safely`' in line)
        lines.remove(pause)
        lines.append(pause)
        path.write_text(text.replace(precedence, '\n'.join(lines) + '\n'))
        with self.assertRaisesRegex(AssertionError, 'pause-safely: intent must precede'):
            assert_intent_precedence(self, self.repo)

    def test_investigation_before_verification_regression_rejected(self):
        assert_intent_precedence(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        text = path.read_text()
        precedence = section(text, 'Routing precedence')
        lines = precedence.splitlines()
        proof = next(i for i, line in enumerate(lines)
                     if line.startswith('- ') and '`mobile-proof`' in line)
        investigation = next(i for i, line in enumerate(lines)
                             if line.startswith('- ') and '`investigation`' in line)
        lines[proof], lines[investigation] = lines[investigation], lines[proof]
        path.write_text(text.replace(precedence, '\n'.join(lines) + '\n'))
        with self.assertRaisesRegex(AssertionError, 'verification intent must precede'):
            assert_intent_precedence(self, self.repo)

    def test_domain_routes_require_implementation_intent(self):
        assert_intent_precedence(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        path.write_text(path.read_text().replace('only to implementation requests', 'to any request'))
        with self.assertRaisesRegex(AssertionError, 'domain routes must exclude'):
            assert_intent_precedence(self, self.repo)

    def test_absolute_paths_in_all_host_and_worker_handoffs(self):
        assert_handoff_contract(self, self.repo)

    def test_claude_registered_handoff_missing_mode_path_rejected(self):
        assert_handoff_contract(self, self.repo)
        path = self.repo / MODE / 'references/host-notes.md'
        text = path.read_text()
        claude = section(text, 'Claude Code')
        changed = claude.replace("absolute path to this mode's `SKILL.md`", 'relative mode-file link', 1)
        path.write_text(text.replace(claude, changed))
        with self.assertRaisesRegex(AssertionError, 'Claude registered handoff: absolute mode path'):
            assert_handoff_contract(self, self.repo)

    def test_claude_wrapper_handoff_missing_skills_directory_rejected(self):
        assert_handoff_contract(self, self.repo)
        path = self.repo / MODE / 'references/host-notes.md'
        text = path.read_text()
        claude = section(text, 'Claude Code')
        paragraphs = claude.strip().split('\n\n')
        paragraphs[1] = paragraphs[1].replace('absolute plugin skills directory', 'consumer directory')
        path.write_text(text.replace(claude, '\n\n'.join(paragraphs) + '\n\n'))
        with self.assertRaisesRegex(AssertionError, 'Claude wrapper handoff: absolute skills directory'):
            assert_handoff_contract(self, self.repo)

    def test_common_handoff_missing_absolute_paths_rejected(self):
        assert_handoff_contract(self, self.repo)
        path = self.repo / MODE / 'references/host-notes.md'
        text = path.read_text()
        common = section(text, 'Common handoff')
        changed = common.replace("absolute path to this mode's `SKILL.md`", 'relative mode-file link')
        path.write_text(text.replace(common, changed))
        with self.assertRaisesRegex(AssertionError, 'Common handoff: absolute mode path'):
            assert_handoff_contract(self, self.repo)

    def test_workspace_rules_cannot_grant_consumer_authority(self):
        assert_authority_contract(self, self.repo)

    def test_workspace_authority_escalation_rejected(self):
        assert_authority_contract(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        path.write_text(path.read_text().replace('cannot grant consumer edits, execution, installs or publication',
                                                'can grant consumer edits, execution, installs or publication'))
        with self.assertRaisesRegex(AssertionError, 'workspace rules cannot grant consumer authority'):
            assert_authority_contract(self, self.repo)

    def test_prototype_transitions_preserve_production_domain(self):
        assert_prototype_handoff(self, self.repo)

    def test_prototype_native_only_transition_rejected(self):
        path = self.repo / MODE / 'playbooks/prototype.md'
        original = path.read_text()
        for number, route in [('1', 'cmp-two-target-change'), ('6', 'kmp-bridge-change')]:
            with self.subTest(step=number, route=route):
                path.write_text(original)
                assert_prototype_handoff(self, self.repo)
                step = dict(steps(original))[number]
                changed = step.replace(f'[{route}]({route}.md)', 'feature')
                path.write_text(original.replace(step, changed))
                with self.assertRaisesRegex(AssertionError, f'prototype step {number}: production handoff'):
                    assert_prototype_handoff(self, self.repo)

    def test_recovery_and_examples_use_each_host_invocation(self):
        assert_host_recovery(self, self.repo)

    def test_ambiguous_recovery_command_rejected(self):
        assert_host_recovery(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        path.write_text(path.read_text().replace('/hugues-stack:hugues-mode', '/hugues-mode', 1))
        with self.assertRaisesRegex(AssertionError, 'mode recovery: Claude namespace required'):
            assert_host_recovery(self, self.repo)

    def test_missing_playbook_rejected_from_valid_fixture(self):
        assert_playbooks(self, self.repo)
        (self.repo / MODE / 'playbooks/feature.md').unlink()
        with self.assertRaisesRegex(AssertionError, 'WP2 exact playbook set'):
            assert_playbooks(self, self.repo)

    def test_unordered_steps_rejected_from_valid_fixture(self):
        assert_playbooks(self, self.repo)
        path = self.repo / MODE / 'playbooks/bug-fix.md'
        path.write_text(path.read_text().replace('1. ', '2. ', 1))
        with self.assertRaisesRegex(AssertionError, 'bug-fix: nonconsecutive Steps'):
            assert_playbooks(self, self.repo)

    def test_empty_steps_rejected_from_valid_fixture(self):
        assert_playbooks(self, self.repo)
        path = self.repo / MODE / 'playbooks/mobile-proof.md'
        text = path.read_text()
        path.write_text(text.replace(section(text, 'Steps'), '\n'))
        with self.assertRaisesRegex(AssertionError, 'mobile-proof: missing nonempty numbered Steps'):
            assert_playbooks(self, self.repo)

    def test_wrong_route_file_rejected_from_valid_fixture(self):
        assert_routes(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        path.write_text(path.read_text().replace('[feature](playbooks/feature.md)',
                                                '[feature](playbooks/bug-fix.md)'))
        with self.assertRaisesRegex(AssertionError, 'feature: incorrect route file'):
            assert_routes(self, self.repo)

    def test_changed_principle_rejected_from_valid_fixture(self):
        assert_principles(self, self.repo)
        path = self.repo / 'plugin/skills/principle-prove-it-works/SKILL.md'
        path.write_bytes(path.read_bytes() + b'\nChanged upstream instruction.\n')
        with self.assertRaisesRegex(AssertionError, 'principle differs from pinned upstream bytes'):
            assert_principles(self, self.repo)

    def test_removed_index_entry_rejected_from_valid_fixture(self):
        assert_principles(self, self.repo)
        path = self.repo / MODE / 'SKILL.md'
        text = path.read_text()
        index = section(text, 'Principles')
        index = '\n'.join(line for line in index.splitlines() if '../principle-prove-it-works/SKILL.md' not in line)
        path.write_text(text.replace(section(text, 'Principles'), index + '\n'))
        with self.assertRaisesRegex(AssertionError, 'complete inline principle index links'):
            assert_principles(self, self.repo)

    def test_wrong_provenance_pin_rejected_from_valid_fixture(self):
        assert_provenance(self, self.repo)
        path = self.repo / 'docs/upstream/wp2-provenance.json'
        data = json.loads(path.read_text())
        data['revision'] = '0' * 40
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, 'WP2 provenance pin'):
            assert_provenance(self, self.repo)

    def test_missing_adaptation_mapping_rejected_from_valid_fixture(self):
        assert_provenance(self, self.repo)
        path = self.repo / 'docs/upstream/wp2-provenance.json'
        data = json.loads(path.read_text())
        data['files'] = [item for item in data['files']
                         if item['destination'] != 'plugin/agents/hugues-agent.md']
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, 'missing adapted source mapping'):
            assert_provenance(self, self.repo)


    def test_four_mobile_lanes_proof_and_authority_safeguards(self):
        assert_lanes_and_safeguards(self, self.repo)

    def test_worker_metadata_scope_and_nonrecursive_delegation(self):
        assert_worker_contract(self, self.repo)

    def test_removed_mobile_target_requirement_rejected(self):
        assert_lanes_and_safeguards(self, self.repo)
        path = self.repo / MODE / 'references/mobile-lanes.md'
        text = path.read_text()
        path.write_text('\n'.join(line for line in text.splitlines()
                                 if not line.startswith('| KMP shared logic |')))
        with self.assertRaisesRegex(AssertionError, 'all four required mobile lanes'):
            assert_lanes_and_safeguards(self, self.repo)

    def test_missing_result_classification_guard_rejected(self):
        assert_lanes_and_safeguards(self, self.repo)
        path = self.repo / MODE / 'references/mobile-lanes.md'
        path.write_text(path.read_text().replace('A skipped assertion is skipped, never passed',
                                                'A skipped assertion may be counted as passed'))
        with self.assertRaisesRegex(AssertionError, 'mobile result classification safeguard'):
            assert_lanes_and_safeguards(self, self.repo)

    def test_recursive_worker_regression_rejected(self):
        assert_worker_contract(self, self.repo)
        path = self.repo / 'plugin/agents/hugues-agent.md'
        path.write_text(path.read_text().replace('Do not recursively delegate the same assignment.',
                                                'Recursively delegate the same assignment.'))
        with self.assertRaisesRegex(AssertionError, 'bounded worker must not self-delegate'):
            assert_worker_contract(self, self.repo)

    def package_check(self):
        return subprocess.run(['sh', str(self.repo / 'scripts/check-plugin.sh'), str(self.repo)],
                              text=True, capture_output=True)

    def valid_package_check(self):
        result = self.package_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('DEFERRED:', result.stdout, 'known upstream helper gap must be visible')
        return result

    def rejected_package_check(self, diagnostic):
        result = self.package_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def change_receipt(self, change):
        path = self.repo / 'docs/upstream/wp2-provenance.json'
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_known_deferred_link_is_explicitly_reported(self):
        self.valid_package_check()

    def test_altered_deferred_source_cannot_use_exception(self):
        self.valid_package_check()
        path = self.repo / 'plugin/skills/principle-explain-the-number/SKILL.md'
        path.write_bytes(path.read_bytes() + b'\nAn altered source.\n')
        self.rejected_package_check('source bytes differ from pinned upstream')

    def test_altered_source_and_receipt_cannot_repin_exception(self):
        self.valid_package_check()
        path = self.repo / 'plugin/skills/principle-explain-the-number/SKILL.md'
        path.write_bytes(path.read_bytes() + b'\nAn altered source.\n')
        new_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        def change(data):
            data['deferred_links'][0]['source_sha256'] = new_hash
            for row in data['files']:
                if row['destination'] == 'plugin/skills/principle-explain-the-number/SKILL.md':
                    row['sha256'] = new_hash
        self.change_receipt(change)
        self.rejected_package_check('invalid source, target, hash or reason')

    def test_different_broken_link_still_fails(self):
        self.valid_package_check()
        (self.repo / 'UNRELATED.md').write_text('[not deferred](missing-other-leaf.md)\n')
        self.rejected_package_check('UNRELATED.md: broken local link')

    def test_wrong_deferred_target_rejected(self):
        self.valid_package_check()
        self.change_receipt(lambda data: data['deferred_links'][0].update(target='../other/SKILL.md'))
        self.rejected_package_check('invalid source, target, hash or reason')

    def test_excess_deferred_rows_rejected(self):
        self.valid_package_check()
        self.change_receipt(lambda data: data['deferred_links'].append(dict(data['deferred_links'][0])))
        self.rejected_package_check('expected exactly one bounded receipt')

    def test_malformed_deferred_receipt_rejected(self):
        self.valid_package_check()
        self.change_receipt(lambda data: data.update(deferred_links={'source': 'anything'}))
        self.rejected_package_check('expected exactly one bounded receipt')

    def test_missing_verbatim_provenance_rejected(self):
        self.valid_package_check()
        def change(data):
            for row in data['files']:
                if row['destination'] == 'plugin/skills/principle-explain-the-number/SKILL.md':
                    row['disposition'] = 'adapted'
        self.change_receipt(change)
        self.rejected_package_check('missing matching verbatim provenance')

    def test_changed_deferred_upstream_pin_rejected(self):
        self.valid_package_check()
        self.change_receipt(lambda data: data.update(revision='f' * 40))
        self.rejected_package_check('upstream pin mismatch')

    def test_newly_present_helper_rejects_stale_deferral(self):
        self.valid_package_check()
        path = self.repo / 'plugin/skills/benchmark-checklist'
        path.mkdir()
        (path / 'SKILL.md').write_text('---\nname: benchmark-checklist\ndescription: Unique test helper metadata\n---\n')
        self.rejected_package_check('target is present; remove stale deferral')


if __name__ == '__main__':
    unittest.main()
