# Progressive disclosure and source footprint

The canonical mode still loads in full. Its native invocation, authority and
routing rules remain mandatory. The shared adapter now requires its worker,
helper, history/integration, TypeScript and publication references only before
their named actions. A small mobile applicability file requires the complete
mobile adapter before any explicit mobile task; non-mobile work stops at the
applicability decision. This uses ordinary file reads, not a new native loader.

The [partition receipt](ADAPTER-DISCLOSURE.json) and regression checks account
for every original host paragraph, part by part: each part is preserved
verbatim in one of those files, replaced or removed, and every replacement or
removal carries an explicit, tested reason. The complete mobile adapter is the original mobile file
with each recorded replacement applied. Deferral changes when guidance is read,
not whether its triggered requirements apply. Unknown native invocation for `hugues-mode`,
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
| Declared startup metadata, every frontmatter block (59 in the current candidate) | 3,940.25 | 3,700 | 3,945 | 14,803 → 15,781 |
| Initial bug-fix routing, full playbook, todos and unslop reply | 11,331.75 | 11,307.75 | 9,405.75 | 45,289 → 37,663 |
| One-function CLI bug fix with cheap regression test | 35,078 | 33,956 | 34,851.25 | 135,888 → 139,473 |
| Three-module TypeScript feature with design and implementation arenas | 37,897.5 | 36,551.25 | 37,429.5 | 146,269 → 149,786 |

The routing inventory falls about 16.8% from the previous native candidate.
Complete bundled workflow inventories also count worker dispatch, verification
and publication instructions. The bug-fix profile
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

Ten of the 50 skill files declared at 0.2.0 remain byte-identical to `7db3e80`,
all of them `principle-*` skills, which never carried the reworded host-contract
marker below. The other 40 differ. Fourteen are the principle skills the pstack
0.15.25 re-pin updated. The 26 non-principle files differ for three separate
reasons: `hugues-mode` and `setup-hstack` carry hStack's own router and setup
changes; architect, arena, how, interrogate, reflect, swarm and
why carry the separate tiered-model-role wiring that replaced Cursor's rule file
with project-local `.hstack/models.md` and `inherit-parent` defaults; and PR 1
fix round 1's reworded host-contract marker ("The host contract governs how this
skill reaches any sibling dependency.", replacing wording that read as a blanket
override of the scoped bundled-reference rule) touches every one of the 26. The
nine skills added after the release carry the marker too. All 59 skill files
total 228,298 bytes; bodies excluding frontmatter and delimiters total 212,163
bytes. The mode file is 20,242 bytes, including its 19,965-byte body.

History, not current counts: until the pstack 0.15.25 re-pin, all 24
`principle-*` files matched `7db3e80`. Restoring pstack's router design had put
the inherited Cursor `disable-model-invocation: true` line back on 44 skill
bodies, matching most of that pre-restoration baseline again. PR 1 fix round 2
also reworded part of setup-hstack's (then setup-huguesstack's) own body (item
3's `create-verification-skill` resolution fix). The router rewrite (issue #22)
edited `hugues-mode` and one line of `setup-hstack`, both already among the 26,
so it left the 24 byte-identical files unchanged. At its fix round 1
(`8b7127a`), the 50 files totaled 191,824 bytes, with 177,003 bytes of bodies,
and the mode file was 20,046 bytes, including its 19,769-byte body, about 2,845
words; before the rewrite it was 20,961 bytes and about 3,023 words. The rewrite
dropped the four Cursor-only frontmatter fields, moved the model-defaults
paragraph into
[the worker reference](../plugin/adapters/host-workers.md#model-defaults-and-role-labels)
and added the four mobile routes to the Playbooks list. Issue #83 then put
pstack's own wording back in every rule the rewrite had restated, keeping the
renames, the host translation and the mobile routes, which brought the mode file
to the size given above.

Only `setup-hstack` is model-invocable now, so only its 116 characters of
description enter startup context on Claude Code. Until
[ADR 0003](adr/0003-hugues-mode-is-user-only.md) made the router user-only, it
added 236 more, for 352 (362 before the rename shortened the setup description); the
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
pinned bytes). The other 62 skills are user-only: the owner types one by
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
those claims, not the byte/character counts themselves. A user-only skill's frontmatter still counts toward the all-59
upper bound above regardless, since that bound is deliberately over every
declared skill, not only what a host happens to expose. The reduction comes from avoiding unrelated adapter reads,
not shrinking or omitting the procedures. Reducing the mode further by making
its own mandatory sections optional would change its agreed full-body loading
contract.

The old 9,182-versus-9,111 comparison counted only mode entry plus unconditional
adapters, before a reply or task. That narrower read set is now 27,656 bytes,
about 6,904.5 estimated tokens. The 0.5.7 Cursor work adds 88 bytes to it, all
of them in the host adapter. At `main` (`a67df90`, pinned in
[the pre-PR baseline](CONTEXT-BASELINE-PRE-PR.json)) it was 25,980 bytes. The
skill-list tiering grew it to 26,724 bytes, 744 more than `main`, through the
longer router description and the scoped bundled-reference rule in the host
adapter. The router rewrite and its fix round took 752 bytes back, which left it 8
bytes under `main`. Later adapter edits, including the shorter host-adapter
wording, left it 264 bytes under that baseline, restoring pstack's router
wording (#83) left it 852 bytes under, and the bundled deslop and the #48 reach
rule left it 817 bytes under. The executable-helper resolution rule (#44)
left it 737 bytes under. Bundling the control skills left it 740 bytes under. The Codex loading
clarification left it 822 bytes under. Later host edits left it 723 bytes under.
Issue #109 added 695 bytes for command routing and worker-baseline handoffs,
leaving it 28 bytes under. Issue #110 adds checklist, translation and disclosure
guidance, leaving the current read set 1,625 bytes above that baseline. Its
changed guidance has a separate bounded allowance.

The explicit read-before-tools sentence keeps the previous sentence's byte count.
The fix round restored the scope words the rewrite had
dropped, named `AskUserQuestion` and the registered `hugues-agent` per host in
the adapters, cut the mobile bullet to a pointer at the mobile workflows
adapter, and adopted the owner's 236-character router description, 74 bytes
shorter in the file than the 312-character one (its two quote characters
included). It must not replace the routing-reply row above, which also
includes the selected bug-fix playbook and mandatory unslop dependency.

Startup metadata is unchanged by this phase split. The table counts all declared
frontmatter as an upper bound; actual host exposure, suppression and framing
remain unobserved. Codex policy files add 2,149 source bytes at `7db3e80`
versus 2,535 now across 59 skills, not assumed to enter model context either way. Startup and full-body numbers
overlap and must not be added as though they were independent reads.

The workflow rows count each bundled path once across all participants. Fresh
workers can load it again. The scenarios state five workers for the bug fix,
including one mode worker, and fifteen for the feature, including eight mode
workers. A separately reported mode-worker floor counts the required mode,
agent and applicable shared guidance once per fresh mode worker. It measures
9,803 estimated tokens for the bug-fix worker against 9,403.5 before disclosure,
and 78,424 for the eight feature workers against 75,228 before disclosure. The model-defaults paragraph and the
per-host `hugues-agent` line now sit in the worker reference that a fresh worker
also reads, and the host adapter points at it; that move added 252.5 tokens (one worker)
to this floor at the router rewrite. That historical delta is 8,410.75 minus
8,158.25, from the budget at `8b7127a` and the pre-rewrite budget at
`4b13e5b`; it is not the difference from today's floor. These partial floors exclude other worker
skills, role inputs and evidence; they are not additive to the unique inventories.

External agent-writing instructions, consumer configuration,
source evidence, generated prompts, tool output, retries and native host
overhead have unknown size. The bundled control skills came after these
scenarios. Both enter the declared frontmatter inventory. The two CLI workflow
rows also count the complete `control-cli` file as a candidate-only input.
They do not load `control-ui`. Historical columns stay unchanged because no
bundled counterpart existed then. The bundled `deslop` skill came after these
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

The [helper input receipt](HELPER-INPUTS.json) records all 21 original mode-helper
files. Twenty remain installed (rows with an `installed` path); the legacy
history-scanning audit is preserved only as provenance. Thirteen of the twenty
remain byte-identical to upstream (`same_bytes_as_upstream`). The review-bot
change (issue 34) adapted five watch-pr files, `github.ts`, `policy.ts`, `types.ts`
and two tests, and the plan-checker tests gained one case for its not-applicable
Bugbot box. The Node plan validator accepts bound workflow reads, and current
installed Python/Node tests exercise it. Its reviewed digest is recorded in the
helper receipt. Apart from those six files, the Bun/TypeScript helpers and
dependency files did not change bytes. Their
disclosure-pass runtime validation did not run because the harmless
offline sandbox preflight returned `EPERM`. The later review-fix pass ran it on a
scratch install of the candidate: Bun 1.4.2 installed the locked dependencies
through the session proxy, 52 of 52 `bun test orch watch-pr` cases passed and
strict `tsc --noEmit` passed for watch-pr. No result is inferred from prior-layout
trials, and a consumer install on another machine remains unobserved.

Python adapter behavior changed during consolidation and has its own current
tests. This disclosure pass updates its bound inventory/hash constants. Source
identity and old helper passes do not establish current runtime parity. See
[test accounting](TEST-COVERAGE.md) for current versus frozen coverage.

## Issue #105 mobile guidance inventory

The two authored baselines and six conditional platform references join the
language-selection adapter, mobile review lens and native-forensics reference.
The separate `mobile_guidance` inventory contains 11 files and
26,196 source bytes, about 6,549 estimated tokens.
It measures every new guidance file once. It is neither a task's loading cost
nor observed runtime output or execution cost. Conditional branches load only
when applicable. The generic scenario inventories exclude these skill bodies
and references while counting the short selection pointer in the host adapter.
Issue #109 adds 695 source bytes to these scenarios for command routing and
worker-baseline handoffs. Their measured contributions are bounded separately
at 240 and 560 bytes. Issue #110 counts its changed guidance separately by file.
The allowances are capped at 1,300 bytes for the host table and checklist,
550 for the router, 500 for worker rules, 750 for sandbox guidance, 900 for the
bug-fix continuation, and 15 for each agent's model header. They count those
passages in full, including existing words within changed passages, rather than
claiming an exact net increase. Only files present in each scenario contribute.
After subtracting the measured #109 contributions and #110 allowances, initial
routing and the CLI bug fix remain strictly below their historical inventories.
The TypeScript feature measures 149,786 bytes against 146,269 historical bytes.
Its bound adds those same scoped contributions and the host language-selection
row, which may not exceed 128 bytes. No runtime token saving or execution speedup
follows from these source counts.

Issue #105 adds a conditional native-execution reference of 9,953 source bytes.
It is loaded for native build/test execution and is outside these non-mobile
scenario inventories. Python helper source is not instruction footprint. The
8,192-byte stdout bound is an execution-output contract tested separately; it
is not a measured context or build-time saving.
