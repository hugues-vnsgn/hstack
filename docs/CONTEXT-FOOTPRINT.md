# Progressive disclosure and source footprint

The canonical mode still loads in full. Its native invocation, authority and
routing rules remain mandatory. The shared adapter now requires its worker,
helper, history/integration, TypeScript and publication references only before
their named actions. A small mobile applicability file requires the complete
mobile adapter before any explicit mobile task; non-mobile work stops at the
applicability decision. This uses ordinary file reads, not a new native loader.

Every original host instruction is retained in one of those files, and the mobile
adapter preserves the earlier rules while adding the approved mobile coverage profile. The
[partition receipt](ADAPTER-DISCLOSURE.json) and regression checks account for
every original paragraph, each preserved verbatim or replaced with an explicit,
tested reason. Deferral changes when guidance is read, not whether its
triggered requirements apply. Unknown native invocation for `hugues-mode`,
`setup-hstack` or a consumer or external skill still holds; a reference
never substitutes for that invocation. A bundled user-only skill's SKILL.md is
its sanctioned reach instead, read with the host's own file-read tool per the
host adapter rule; the installed helper never reads it.

## Comparable source scenarios

The table counts UTF-8 source bytes and estimates tokens as Unicode characters
divided by four. These deterministic counts have no runtime sampling noise.
They measure required bundled instruction inventories, not latency, actual
host prompt usage, or a complete executable workflow cost.

The release column uses frozen `509cbec` source. Before disclosure uses frozen
`7db3e80`, the first reviewed native consolidation. After uses current files.
Each column uses the same scenario and counting method. Full paths, hashes,
assumptions and mandatory transitive inputs are in the
[scenario definitions](CONTEXT-SCENARIOS.json) and
[generated inventory](CONTEXT-BUDGET.json). Regenerate with
`python3 scripts/measure_context.py`.

| Scenario | Released 0.2.0, estimated tokens | Before disclosure | After disclosure | Bytes before → after |
|---|---:|---:|---:|---:|
| Declared startup metadata, every frontmatter block (55 after disclosure) | 3,940.25 | 3,700 | 3,716.75 | 14,803 → 14,868 |
| Initial bug-fix routing, full playbook, todos and unslop reply | 11,331.75 | 11,307.75 | 8,544.75 | 45,289 → 34,219 |
| One-function CLI bug fix with cheap regression test | 35,078 | 33,956 | 31,493.25 | 135,888 → 126,043 |
| Three-module TypeScript feature with design and implementation arenas | 37,897.5 | 36,551.25 | 34,476.75 | 146,269 → 137,977 |

The approved-proof candidate adds deferred new-program references separately
from those pinned scenarios. The guide is 7,636 bytes; constructing records also
loads a 6,737-byte format reference. Together they add 14,373 bytes (3,593.25
characters/4 estimated tokens), not a measured host charge. The generated
`new_program_proof` inventory binds both files. Do not describe the original
scenario totals as a complete new-program cost; approval records, host framing
and actual worker reads require their own accounting.

Issue #30 adds a deferred mobile selection guide and risk catalog, totaling
8,493 bytes (2,123.25 estimated tokens). The `mobile_risk_profile` inventory
records both. The mobile-workflows adapter already included in applicable reads
adds the 369-byte profile pointer. These amounts describe source reads, not
observed host tokens; worker briefs include only relevant risk guidance.

Issue #28 adds a deferred controller guide of 10,892 bytes (2,723 estimated
tokens) for program scheduling and recovery. The generated `new_program_control`
inventory records it separately. Controllers read it when that phase applies;
worker briefs carry their own task and limits. These source counts do not measure
actual host loads, waiting cost, cache use or a complete program's usage.

The routing inventory falls about 24.4% from the previous native candidate.
Complete bundled workflow inventories fall less, because worker dispatch,
verification and publication instructions still apply. The bug-fix profile
includes how, why, TDD, source-control investigation and synthesis prompts,
closing skills, specialized agents and applicable principles. The feature
profile includes complex how, architect, arena, swarm, design references,
TypeScript guidance, closing skills and its applicable principles.

The feature profile is a larger bounded workflow within one subsystem. A large
cross-cutting migration, unattended task or standing program follows the mode's
figure-it-out/Orchestrate routing; its designed phases determine a different
closure. Mobile work also loads additional guidance. Neither is hidden inside
the fixed profile or claimed covered by its total.

## What the counts include and leave unknown

Twenty-four canonical skill files remain byte-identical to `7db3e80`: the 24
`principle-*` skills, which never carried the reworded host-contract marker
below. Restoring pstack's router design puts the inherited Cursor
`disable-model-invocation: true` line back on 44 skill bodies, matching most
of that pre-restoration baseline again. The other 26 differ for three
separate reasons: `hugues-mode` and `setup-hstack` diverge from upstream
to stay the only model-invocable skills; architect, arena, how, interrogate,
reflect, swarm and why carry the separate tiered-model-role wiring that
replaced Cursor's rule file with project-local `.hstack/models.md` and
`inherit-parent` defaults; and PR 1 fix round 1's reworded host-contract
marker ("The host contract governs how this skill reaches any sibling
dependency.", replacing wording that read as a blanket override of the scoped
bundled-reference rule) touches every one of the 26 non-principle bodies. PR 1
fix round 2 also reworded part of setup-hstack's (then setup-huguesstack's) own body (item 3's
`create-verification-skill` resolution fix). The router rewrite (issue #22)
edits `hugues-mode` and one line of `setup-hstack`, both already among
the 26, so the 24 byte-identical files are unchanged. The
50 files' combined whole-file size is 191,824 bytes; bodies excluding
frontmatter and delimiters total 177,003 bytes. The mode file is 20,046
bytes, including its 19,769-byte body, about 2,845 words; it was 20,961
bytes and about 3,023 words before the rewrite. The rewrite drops the four
Cursor-only frontmatter fields, moves the model-defaults paragraph into
[the worker reference](../plugin/adapters/host-workers.md#model-defaults-and-role-labels)
and adds the four mobile routes to the Playbooks list. Only `hugues-mode` and
`setup-hstack` are model-invocable now, so only their 352 characters of
description (236 for the router, 116 for setup) enter startup context on Claude Code (362
before the rename shortened the setup description); the
[skill-list measurement](CONTEXT-BUDGET.json) tracks this directly. It
carries two "before" points, both computed by the same function, neither
hardcoded: `native_before`, against the `7db3e80`-pinned bytes every other
measurement on this page compares against (1 model-invocable skill, 280
description characters at that revision), which predates the 0.2.0-to-46-skill
flip this PR undoes and so is not a pre-PR comparison for this measurement
specifically; and `pre_pr_main`, added this round against a minimal,
sha256-pinned `a67df90` fixture (just the 50 SKILL.md frontmatter blocks) --
the actual commit this restoration branched from and the exact revision the
Issue's Problem Statement cites (46 model-invocable skills, 9,844 description
characters, close to but not forced to equal the owner's earlier informally
recorded 9,869, since that number was recorded rather than recomputed from
pinned bytes). The other 48 skills are user-only: the owner types one by
name, and the mode reads it in full as its router reference. The agent never
invokes one natively; the owner still can. [Host validation](skill-list-host-validation.md) observed, at
code commit `ae51493`, that Claude Code's attached skill list grows by exactly
two when the plugin loads (a count; which two skills is inferred), that exactly
two entries from this plugin reach Codex's rendered skills block (which cut the
router's then 312-character description at 243 characters; the owner's reordered
236-character description fits whole, per that receipt's
[addendum](skill-list-host-validation.md#addendum-the-reordered-router-description-on-codex)),
and that `tdd`, a user-only skill, still runs when typed by name. It leaves the router description in
Claude's list and a typed `principle-*` skill unobserved, and it establishes
those claims, not the byte/character counts themselves. A user-only skill's frontmatter still counts toward the all-50
upper bound above regardless, since that bound is deliberately over every
declared skill, not only what a host happens to expose. The reduction comes from avoiding unrelated adapter reads,
not shrinking or omitting the procedures. Reducing the mode further by making
its own mandatory sections optional would change its agreed full-body loading
contract.

The old 9,182-versus-9,111 comparison counted only mode entry plus unconditional
adapters, before a reply or task. That narrower read set is now 25,965 bytes,
about 6,481.75 estimated tokens. At `main` (`a67df90`, pinned in
[the pre-PR baseline](CONTEXT-BASELINE-PRE-PR.json)) it was 25,980 bytes. The
skill-list tiering grew it to 26,724 bytes, 744 more than `main`, through the
longer router description and the scoped bundled-reference rule in the host
adapter. The router rewrite and its fix round take 752 bytes back, which leaves it 8
bytes under `main`. The approved-proof candidate's shorter adapter wording and
deferred pointer save a further seven bytes, leaving it 15 bytes under that
baseline. The fix round restored the scope words the rewrite had
dropped, named `AskUserQuestion` and the registered `hugues-agent` per host in
the adapters, cut the mobile bullet to a pointer at the mobile workflows
adapter, and adopted the owner's 236-character router description, 74 bytes
shorter in the file than the 312-character one (its two quote characters
included). It must not replace the routing-reply row above, which also
includes the selected bug-fix playbook and mandatory unslop dependency.

Startup metadata is unchanged by this phase split. The table counts all declared
frontmatter as an upper bound; actual host exposure, suppression and framing
remain unobserved. Codex policy files add 2,149 source bytes at `7db3e80`
versus 2,148 now, not assumed to enter model context either way. Startup and full-body numbers
overlap and must not be added as though they were independent reads.

The workflow rows count each bundled path once across all participants. Fresh
workers can load it again. The scenarios state five workers for the bug fix,
including one mode worker, and fifteen for the feature, including eight mode
workers. A separately reported mode-worker floor counts the required mode,
agent and applicable shared guidance once per fresh mode worker. It falls from
9,403.5 to 8,312.25 estimated tokens for the bug-fix worker, and from 75,228 to
67,286.0 for the eight feature workers. The model-defaults paragraph and the
per-host `hugues-agent` line now sit in the worker reference that a fresh worker
also reads, and the host adapter points at it, which is why this floor is 252.5
tokens (one worker) above its value before the router rewrite. These partial floors exclude other worker
skills, role inputs and evidence; they are not additive to the unique inventories.

External control and agent-writing instructions, consumer configuration,
source evidence, generated prompts, tool output, retries and native host
overhead have unknown size. The bundled `deslop` skill came after these
scenarios were fixed. The startup row counts its frontmatter, and the scenario
rows leave out its body, though the Opening a PR contract they include runs it.
The released and pre-disclosure columns have no counterpart to compare it with. Every modeled dependency is counted even if its
invocation would hold in a real host. Complete execution totals remain null.
No live session established the intended on-demand behavior or token savings.
The [router eval](hugues-mode-router-eval.md) ran the Issue's five tasks in Claude
Code with `claude-opus-5-5` at high effort. The router fired on the branch for
three of the four tasks it should fire on and on `main` for none, and it stayed
quiet on the casual task on both. Each cell is one sample.
One interactive session on `main` at `0988b56`, recorded in the
[router interactive check](router-interactive-check.md), read the router's
adapters, playbooks and bundled skills as files. It measured no tokens.

## Helper inputs and evidence limits

The [helper input receipt](HELPER-INPUTS.json) records all 20 original mode-helper
files. Nineteen remain installed; the legacy history-scanning audit is preserved
only as provenance. Eighteen remain byte-identical to upstream. The Node plan
validator now accepts bound workflow reads and the approved mobile-risk profile;
current installed Python/Node tests exercise both. Its reviewed digest is recorded
in the helper receipt. The Bun/TypeScript helpers and dependency files did not change
bytes. Their disclosure-pass runtime validation did not run because the harmless
offline sandbox preflight returned `EPERM`. The later review-fix pass ran it on a
scratch install of the candidate: Bun 1.4.2 installed the locked dependencies
through the session proxy, 52 of 52 `bun test orch watch-pr` cases passed and
strict `tsc --noEmit` passed for watch-pr. No result is inferred from prior-layout
trials, and a consumer install on another machine remains unobserved.

Python adapter behavior changed during consolidation and has its own current
tests. This disclosure pass updates its bound inventory/hash constants. Source
identity and old helper passes do not establish current runtime parity. See
[test accounting](TEST-COVERAGE.md) for current versus frozen coverage.
