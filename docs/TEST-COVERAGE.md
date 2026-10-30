# Python test roots and evidence limits

The current candidate collects **584 top-level unittest cases**. One is a driver that
separately executes **50 frozen 0.2.0 restoration cases**. Do not add the driver
and its children as independent coverage, or describe historical passes as current
native workflow proof. Subtests are not added to case totals.

| Group | Collected cases | Evidence |
|---|---:|---|
| Historical 0.1.0 contracts | 131 | Unchanged SHA256-bound release archive |
| Current checker, historical 0.1.0 fixtures | 44 | Explicit historical validation mode, package mutations, and the Cursor manifest rules, each with its own negative case |
| Historical 0.2.0 restoration driver | 1 | Executes 50 cases inside a separate hash-bound archive |
| Current source/provenance checks | 48 | test_upstream_sync (37), test_retained_provenance (11) |
| Current installed adapters and regressions | 129 | test_host_adapters (104), test_review_regressions (12), test_rereview_regressions (13) |
| Current native-layout contracts | 63 | test_native_layout; canonical source, permissions, host invocation table, seal acceptance, helper receipt, the three bundled non-pstack Cursor skills (their pinned sources and notices, the user-only and host-contract requirements, one body edit that resealing approves, and 18 drift mutations that resealing cannot approve), budgets (including the explicit list of skills added after 0.2.0 that have no historical context counterpart) and the native-reach lint (a corpus of 49 reviewed contradictions in five line shapes each, 17 correct sentences, the package wiring and a one-entry allowlist), plus the router rewrite: router section pointers and the Principles index, the four dead Cursor frontmatter fields through the plugin check, and five read-only cases on the router and the files it points at (title, host tool names and description, mobile routes, single-source model defaults, the registered `hugues-agent` name and question tool per host, worker definition), and three source-wording cases for issue #48 (the agent finds its own mode file, the Skill-tool rule, the playbook headers) |
| Current progressive-disclosure contracts | 16 | test_context_disclosure; retained rules, mandatory phase reads, complete declared source inventories, the skill-list budget (including its pinned pre-PR `a67df90` point), YAML-description quoting, the router's initial read set against `main`'s pinned read set and bound resources |
| Current installed-tolerance regressions | 45 | test_installed_tolerance; bootstrap dependencies, host metadata, unreadable folders, umask modes, every spelling of a raw skill read, normalized paths (`.`, `..`, letter case, repeated slashes), open quotes and split code spans, every revision/syntax a skill-body guard must still check, the plan-check helper's operand, and a rejection matrix of 2,220 cases (379 `read-workflow`, 1,778 `translate-plan` and 63 in-plan cases) over all 63 bundled skills, the legacy aliases of the 58 that have one, consumer and external paths, with symlink and traversal cases and positive controls |
| Current setup-to-proof contracts | 9 | test_setup_proof; mobile recipe requirement, native holds and non-mobile harnesses, host handoffs, model tiers, and installed mobile-proof reads from an external consumer with a decoy path. Includes rejection of absent, failed or text-only screenshot reads in native evidence. These nine cases check source/commands and evidence parsing, not host or device execution. |
| Current bundled mobile guidance | 6 | test_mobile_guidance; installed nine-context selection contract, scoped skill controls, reference resolution, review and native-forensics hooks, ten-lane preservation and authored inventory mutations. These are delivered-source contracts, not device journeys. |
| Current helper and language rules | 5 | test_helper_language_rules; command routing and resolved helper link, per-command exceptions and Gaps, reviewer baseline template, both-host worker briefs and portable lens links. Delivered-source contracts only. |
| Current native execution helpers | 86 | test_native_exec and test_native_exec_review; 83 controlled installed CLI cases, two installed workflow/evidence contracts and one collection/accounting guard. Native project observations run separately. |
| Total collected | 584 | Current, mixed and historical scopes remain distinct |

The [native setup-to-proof check](../tests/setup-proof.md) runs separately on an
authorized Mac. Its real iOS UI tests and Claude sessions are not included in the
584 Python cases. The opt-in CI workflow requires a provisioned native runner.
The source maintenance workflow runs the README's five commands on pull requests
and pushes to main; it does not run native host or device probes.

The 131 historical modules are test_wp2_contract (45), test_wp3_contract (15),
test_retained_design (7), test_retained_research (8), test_retained_verification (6),
test_retained_integration (26) and test_lane_evidence (24). Their root is
`release_root()`. No frozen archive was modified to make a current test pass.
The newly retained 0.2.0 archive is the original `509cbec` Git tree, not the
0.3.0 layout. Its 50 restored-contract cases remain historical evidence.
Main collected 349 cases. Moving those 50 behind one driver and adding 29
native-layout plus eight disclosure cases gives 337, without dropping the frozen
50 executions or counting them twice. The preceding native candidate had 329.
The review-fix pass adds five native-layout and nine installed-tolerance cases,
giving 351. The historical driver now also fails when any nested case is skipped.
Restoring pstack's router design adds one skill-list budget disclosure case,
giving 352. PR 1 fix round 1 adds one native-layout case (an unknown skill body
still refuses translation), one disclosure case (YAML-description quoting) and
two installed-tolerance cases (a bundled skill's exact SKILL.md path now
translates and reads; round 3 reversed both), giving 356. PR 1 fix round 2 adds two native-layout
cases (the native-reach lint rejects a reintroduced contradiction, and passes
the reviewed auto-load-disabled sentence), one disclosure case (the pinned
`a67df90` pre-PR skill-list point recomputes to 46 skills and the Issue's
cited character count) and four installed-tolerance cases (a skill-body guard
still fires at every Git revision and unsupported shell form, and
`hugues-mode`/`setup-hstack` stay native-only for both `read-workflow`
and `translate-plan`), giving 363. PR 1 fix round 3 takes the helper relaxation
back out: the cases that translated and read a bundled SKILL.md become
refusals, and seven installed-tolerance cases are added (the six-case
rejection matrix over every bundled skill, alias, consumer and external path
and plan form, and a consumer-symlink case) with two native-layout cases (the
reworked native-reach lint now has a reviewed-contradiction corpus, a
package-wiring case, a correct-sentence case and an allowlist case, replacing
two), giving 372. PR 1 fix round 4 adds no case: it adds ten contradictions
and four correct sentences to the lint corpus (the mobile-workflows sentence,
the fresh-worker read of "any bundled skill", and host-loading spellings), widens
the lint to catch them and records its limits in the corpus file, and extends
the adapter-partition case to the mobile adapter's recorded replacement, so the
total stays 372. The router rewrite (issue #22) adds seven native-layout cases
(the router-section and Principles-index check with its mutations, the four dead
frontmatter fields run through the plugin check, and five read-only cases on the
rewritten router and the files it points at) and two disclosure cases (the
router's initial read set recomputes smaller than `main`'s, and drift in the
pinned `a67df90` read-set fixture is rejected), giving 381. Its fix round adds two
more read-only router cases (the scope words that positive rewrites had dropped, and
the per-host registered `hugues-agent` name and question tool), giving 383.
The skill-path normalization fix adds two installed-tolerance cases (normalized
paths, and open quotes or split code spans), giving 385. The 0.3.0 release adds
no case, so the total stays 385. Issue #26 adds seventeen installed-tolerance cases:
seven shell-expansion bypasses, the skill-directory allow-list, quote and helper
operand checks, backtick-comment bypasses, unrelated-shell controls, explicit
Markdown prose, safe and rejected fenced/indented-code, malformed spans, emitted helpers
under skill-directory installation paths, and translation of all three
bundled Markdown plan templates with both execution-playbook choices, plus
every inline fragment translated separately as command input, giving 402.
The PR #41 review adds four installed-tolerance cases for expansions immediately
after a skill-directory name, shell backticks around a skill-name token, rejected
Markdown container code blocks, and nested checklist translation with indented-code
controls. That brought the total to 406. The existing 1,840-case rejection matrix remains intact.

The approved-proof candidate adds 42 installed-command cases.
MacOS write tests observe actual process/child/alias denial; other platforms skip
those cases and do not acquire observed support. Proof cases validate protected
record consistency and readable artifact bytes, not authenticated approval,
independent process identity or semantic truth of images. Native worker journeys
and mobile observations remain separate gaps.

Current adapter cases execute the public installed Python entrypoint in disposable
external consumer directories, including Node plan validation when available.
Bindings cover canonical files, metadata, adapters, runtime code and permission
modes. Tests reject missing/extra files, symlinks, world-writable files,
changed executable bits, bootstrap execution before verification, poisoned
bytecode caches, consumer path ownership errors and unsupported shell shapes.
No SKILL.md is returned by `read-workflow` or translated by `translate-plan`:
every spelling (a bundled skill's exact path or legacy alias, a wrong prefix,
an absolute path, a consumer, external or model-invocable skill, at any Git
revision or shell form) is rejected, so no helper read can stand in for a
native invocation or for the agent's own file read of a user-only skill.
Tests do not simulate a successful host permission decision.

The unchanged activity parser is exercised with synthetic Claude/Codex records,
relative contexts, malformed/unsupported inputs, empty sources, duplicate/deep
JSON and unknown PR metadata. Candidate-specific holds and exit 2 remain required.
The active/pinned-chat gate stays separate. No real transcript was read and no
real worktree was deleted.

Native-layout cases compare all 63 public names (58 from pstack, three from Cursor's `cursor-team-kit` and two hStack-authored language baselines) and modes, archive/source identity,
canonical mapping, workflow phase/cardinality/fallback constraints, the
reviewed host invocation table, consumer boundaries and a measured source-context budget.
Hash resealing cannot approve a lost phase gate or changed invocation policy.
Invocation metadata checks use effective fields, rejecting duplicate fields and
comment decoys. Plans containing only bound workflow reads pass the plan gate
without an incidental consumer Git read; missing binding markers still fail.
The budget uses bytes and characters/4; it is not measured host context.

Complete persisted-transcript compatibility, completed worker dispatch, Codex
invocation, mobile device journeys and forge/cloud/loop execution remain
unverified. Claude Code discovery and the router's firing were observed in the
[skill-list host validation](skill-list-host-validation.md), the
[router eval](hugues-mode-router-eval.md) and the
[router interactive check](router-interactive-check.md), each bound to its own
commit. Earlier native observations are bound to their original revisions.
Historical Bun/TypeScript helper results remain separate from any new
run recorded in the implementation evidence.
The required-context change adapts the watch-pr sources and adds nine Bun
cases. On October 20, 2026, `bun test ./watch-pr` passed all 65 watch-pr cases
with Bun 1.3.14. These cases are separate from the Python totals above. The
dependency inputs remain unchanged. The Node plan checker also changed and
has current Python/Node integration coverage. The disclosure-pass
Bun/TypeScript run was blocked before execution by sandbox preflight `EPERM`. The
review-fix pass ran it on a scratch install of the candidate: Bun 1.4.2,
`bun install --frozen-lockfile` through the session proxy, 52 of 52 `bun test orch
watch-pr` cases and strict `tsc --noEmit` for watch-pr passed. That run is outside
the Python suite and is not counted above. See the
[helper input receipt](HELPER-INPUTS.json) and [context report](CONTEXT-FOOTPRINT.md).

Issue #37 adds nineteen installed verification-contract cases, bringing the then-current
total to 425. Eight review regressions cover whole-plan changes, receipt labels,
rejected rulings, sibling worktrees, fetched-main identity, divergent main, and the
real plan template through both installed helpers, plus attaching and removing
receipts without triggering approval. Ruling authentication and owner write isolation remain workflow
requirements; these synthetic Git fixtures do not prove either in a live host.

Issue #36 and its review fixes add eight payload-policy and evidence-parser cases, bringing the total
to 439. Its [opt-in native regression](https://github.com/hugues-vnsgn/hstack/blob/v0.4.0/tests/payload-boundary.md) runs separately;
the [observed receipt](https://github.com/hugues-vnsgn/hstack/blob/v0.4.0/docs/payload-protection-proof.md) distinguishes native probe
results from unobserved writers and full-program execution.

The PR 54 retrospective adds two runner CLI cases, bringing the current total to
441. Their 30 subtests include six valid holds and 24 forbidden helper attempts.
Before the fix, all six orch-attempt subtests incorrectly passed the runner's
hold validation. The other helper attempts were already rejected.

The pstack 0.15.25 merge adds one native-layout case, bringing the current total
to 442: the context inventory lists the four skills added after the 0.2.0
release (`hugues-help`, `in-your-own-words`, `ketchup`, `sharpen`) by name, and an
unlisted new skill or a missing listed one still fails the measurement. It also
rebinds existing cases to the new pin: the upstream-sync and retained-provenance
fixtures follow the 0.15.9 to 0.15.25 delta, while the 0.15.5 snapshot and
ledger (`docs/upstream/history/`) still back the Appendix A path list and the
regenerated historical delta, and the
installed-tolerance rejection matrix grows with the four new bundled skills and
their `pstack/skills/...` aliases from 1,840 to 1,980 cases.

The hStack rename (0.4.0) adds two native-layout cases, bringing the current total
to 444: every plugin file that names `.hstack/models.md` must also say to read a
legacy `.huguesstack/models.md` when the new file is absent, and setup writes only
`.hstack/`. It also moves the existing assertions to the new names (`setup-hstack`,
`.hstack/`, `hstack-native-v1`, `hstack-program`, `hstack-dispositions`). The seven
historical modules keep the old names where they read the frozen 0.1.0 tree, and the
context measurement renames the setup skill's path in the frozen 0.2.0 and baseline
archives without editing them.

The same release adds four source/provenance cases, bringing the current total to 448.
They bind the retained bytes of hstack-alpha (retired predecessor, a different project whose
GitHub repository was deleted on 2026-10-16): the receipt note names the deletion and the
retained location, each cited input hashes to its retained copy, every `source:` line in
`hugues-mode` cites a file that is retained with the receipted hash, and the thirteen
files those retained Markdown files link to match their recorded hashes. The copied
KMP/CMP practice app under `tests/fixtures/kmp-compose-ios-pilot/` is data for later
mobile work and is not run by any case.

The PR 47 review-fix check ran all 439 cases on Python 3.14.7 successfully.
On macOS's Python 3.9.6, the eight payload-policy cases pass and the full run has
438 passing top-level cases plus one failing historical 0.2.0 driver. Its frozen
nested loader requires tar extraction-filter behavior absent from that stdlib;
its older extraction modes also fail frozen integrity checks. The current outer
loaders support hash-verified extraction on 3.9, but the frozen archive and its
assertions remain unchanged. This is a historical compatibility gap, not a
Python 3.9 full-suite pass.

Issue #53 adds three public-interface cases, bringing the current total to 451:
the optional Claude macOS mobile recipe preserves the payload denial, preparation
proves the disposable copy writable without claiming enforcement, and mobile
preparation copies the fixture and records exact gate argv. The unsafe-request
matrix also covers unsupported hosts, absent opt-in, invalid JDKs, payload write
roots and malformed domains. PR #55 review adds three more cases, bringing the
current total to 454 with 14 payload-policy cases: broad explicit tool roots and aliases, inward JDK links,
and Claude permission-mode ambiguity. The invalid-domain matrix also rejects
wildcards, ports, malformed labels and non-ASCII names. Legacy consumer/evidence
behavior remains covered. These remain source/CLI checks.
Native mobile observations and remaining gaps are recorded in the
[issue 53 receipt](https://github.com/hugues-vnsgn/hstack/blob/262397d513bc69545fb1cc27535860aa8202e516/docs/mobile-payload-proof.md).

The issue-28 candidate adds 38 installed-command cases. These observe
local process groups, kernel locks and blocking command waits with synthetic
consumer records. Native dispatch enforcement, complete host usage delivery,
mobile restoration and real fresh-session pickup remain deferred trial gaps.

Issue #30 adds nineteen installed mobile-coverage cases and three plan/proof
integration cases. Matrix
subtests are not added to this total. Real host/mobile trials remain deferred.

On 2026-10-17, issue #77 withdraws payload protection. The fourteen
policy-fragment and helper-readiness cases go with the two host-tool verbs they
covered, and one installed-command case checks that the bound CLI now rejects
both as unknown verbs. The two runner CLI cases go with the native
payload-boundary regression script they checked, bringing the current total to
541. The `worker-run` overlap case now accepts a writable scope over the
installed plugin root and still rejects one over the owner control directory,
and the approved-roots case no longer lists the plugin file or the binding as
protected. The binding, guarded-read and drift cases are unchanged.

On 2026-10-17, issue #80 removes approved proof, the `worker-run` sandbox and
program control. The 46 approved-proof cases, including issue #30's three
plan/proof integration cases, and the 38 program scheduling/recovery cases go
with the `program-check`, `artifact-hash`, `decode-design`, `worker-run`,
`run-control` and `run-wait` verbs they covered. Issue #77's case that rejects the
withdrawn payload-protection verbs moves to test_host_adapters and now also
checks that the bound CLI rejects the six removed verbs as unknown, bringing the
current total to 458. Remaining runtime drift, bytecode and binding cases still
cover the four runtime modules that stay.

On 2026-10-17, issue #81 removes risk-based mobile coverage and returns plan
validation to pstack's fixed rule of ten live lanes. The nineteen risk-coverage
cases go with the validator, risk catalog and selection guide they covered. One
new installed-command case in test_host_adapters checks that the bound
`plan-check` accepts a ten-lane plan, with or without frontmatter, and rejects an
eleventh lane or a risk-based live heading, bringing the current total to 440.

On 2026-10-17, issue #82 removes the verification-contract gate. The nineteen
verification-contract cases go with the `plan-compare` verb, its comparison
helper and the contract reference they covered. The test_host_adapters case that
rejects withdrawn verbs now also checks that the bound CLI rejects `plan-compare`
as unknown. One new installed-command case checks that the bound `plan-check`
accepts a plan whose Verdict and merge section holds pstack's own boxes and no
verification-contract box, bringing the current total to 422.

On 2026-10-17, issue #83 removes the Claude stack-permission preflight and the
Astra High PR review policy, and puts pstack 0.15.25's wording back in the
router. The two router cases that pinned the rewrite's own wording, autonomy
placement and the scope of restated obligations, go with it, bringing the
current total to 420. The Principles index case now checks pstack's naming
rule, a bold title in kebab case or a given name. The installed-binding drift
cases no longer list the deleted policy file.

The bundled `deslop` skill is a copy of Cursor's `cursor-team-kit` skill, not a
pstack skill, and adds two native-layout cases. One binds the installed skill to
its pinned Cursor source, the license notice and the two allowed additions. The
other changes the installed body, the retained source copy, the shipped notice,
the user-only metadata and the receipt in turn, reseals after each change and
expects the core check to reject it. The existing cases now expect 55 public
skills, list `deslop` among the skills added after 0.2.0 and compare the
startup-metadata budget with `native_before` over the 50 skills both declare.
The installed-tolerance rejection matrix grows from 1,980 to 2,000 subtests with
the new skill, which has no legacy `pstack/skills/...` path. These are source
checks of files and wiring. They do not show that a host lists, loads or runs
`/deslop`.

Issue #48 adds three native-layout cases.
One checks that `hugues-agent` keeps its preload and finds `hugues-mode/SKILL.md`
in order: the parent's path, the base directory Claude Code shows, then a search
of the installed plugins. One checks that `host.md` and the agent header both say a
bundled user-only skill is never a Skill-tool call and that `/<name>` means reading
`../<name>/SKILL.md`. One checks that the three playbook headers lose the clause
that held a step on denied invocation while keeping `read-workflow` and
`plan-check`. The native-reach corpus gains two contradictions (a Skill-tool call on
`no-comments`, and on each bundled skill) and two correct sentences (the rule as
`host.md` and the agent header word it). These are source checks of wording. They
do not show how Claude Code behaves with it.

Merging `main` into the #78 branch brings in the deslop cases and the three #48 cases
above, so the total at that merge was 425.

Issue #44 adds two installed plan-check cases. They verify checker identity from a
Gitless install with a consumer decoy and a real consumer commit, and from a tracked
plugin checkout on validation failure. The collected total is 427.

Issue #75 adds three installed procedure-contract cases, bringing the collected
total to 430 after the #44 merge. They read the bound mobile workflows and references through the
public helper and check preflight ordering and records, both host-baseline
branches, tool examples and reached-step evidence. These check installed
instructions, not host or device behavior.

Issue #34 decisions 2 and 3 add two installed phase-guidance contracts, bringing
the collected total to 432. They check native skill-default and existing-target
placement across the named workflows, plus durable store precedence and retained
helper arguments. These validate delivered instructions, not native skill discovery
or coordinator recovery behavior.

The control-skill bundling keeps the 432 collected cases. The two existing
Cursor integrity cases now cover `control-cli`, `control-ui` and `deslop`,
including six mutations per skill. The current installed-tolerance matrix has
2,040 subtests. Both control skills enter the declared metadata inventory; the
CLI scenarios also count the complete `control-cli` body as a candidate-only
input, with historical columns unchanged.

The release 0.5.0 pretest fix adds one native-layout source-contract case for Codex catalog selection and complete skill-file reads while preserving native-only holds and worker-role boundaries. The collected total is 434. This checks delivered instructions, not fresh-host behavior.

The release 0.5.0 pretest fix adds one native-layout source-contract case for the required local PR title and body under a publication hold or absent remote or forge. The collected total is 434. This checks delivered instructions, not fresh-host behavior.

The F3 helper-setup source contract adds one installed-adapter case. Collection on the rebased branch gives 435 top-level cases, with 78 in test_host_adapters and 56 in test_native_layout. The setup case also retains gap reporting, operation and gate holds, permitted native local substitution for cloud, and real race execution. These are source checks, not fresh-host proof.

The F4 no-todo-tool translation adds one native-layout source-contract case. Collection on the rebased branch gives 436 top-level cases, with 57 in test_native_layout and 78 in test_host_adapters. It checks the conditional Markdown checklist, agent-store rule, verbatim steps before step one, ongoing done or skip records, and the filename in the reply. These are delivered-instruction checks. Fresh-host adoption remains unobserved.

Issue #105 adds six installed mobile-guidance and inventory cases. Collection
gives 442 top-level cases. The nine selection contexts are instruction contracts
through an installed plugin in an external consumer, not observations of native
host loading. Reseal mutations reject missing authored inventory, model-invocable
metadata, changed path scopes and implicit invocation. The current tolerance
matrix covers 59 skills and 2,080 subtests. Frozen archives remain unchanged.
The disclosure test keeps initial routing and the CLI bug fix strictly below
their historical source inventories. The TypeScript feature is bounded by its
historical inventory plus the measured host selection row, at most 128 bytes.
Installed contracts also check that mobile plans load lane scenarios and the
review lens before step 4 writes live lanes, and that bug-fix step 6 supplies the
lens to Opening a PR's interrogate review, including top-level PR authors. Historical measurements and test
counts remain unchanged.

Issue #105's native execution helpers add 35 cases. Collection on this branch
reports 477 top-level cases before round 2. The public installed CLI cases pin exact argv,
cwd and environment overrides, raw output bytes, process states, literal test
counts, failure diagnostics, zero/all-skipped results, report gaps and target
mismatches, independent retry attempts, bounded output, native inspection and
post-cleanup retention. Two installed resource contracts check workflow wiring,
artifact identity and the impractical-test exception. These contracts do not
observe a host following those instructions.

Separate local observations exercised SwiftPM with one passing test, Xcode with
one passing iOS UI test and the KMP fixture's Gradle task with three passing
native tests. The owned simulator was deleted and retained reports reopened
after scratch cleanup. These are helper observations, not fresh Claude Code or
Codex consumer journeys. The host/domain matrix and an observed consumer
impractical-test journey remain gaps for the later #105 phase.

Issue #105 round 2 adds 25 installed public CLI cases. Collection on main's
merged language-guidance base reports 502 top-level cases, including 60 native
helper cases. Captured native XML, JSON and logs pin XCTest skip visibility,
Swift Testing primary/disabled/multiple-issue counts, expected xcresult failures,
compiler and Gradle causes, explicit omission flags and report manifests. Other
cases cover argument ownership, Xcode actions and metadata modes, XML aggregate
limits, interrupted builds and Unicode output-budget convergence. These are helper-boundary tests. Fresh native
host/domain workflow evidence remains deferred.

Issue #109 adds five installed wording contracts for helper routing and portable
language-baseline handoffs. Collection gives 507 top-level cases. The context
bounds account separately for the command routing row and scope sentence, capped
at 240 bytes, and the worker-baseline brief paragraph, capped at 560 bytes. The
existing budgets still bind all other source. These contracts do not establish
Claude Code or Codex compliance with the revised text.

Issue #110 adds six native-layout wording cases and one installed sandbox-guidance
case. Collection gives 514 top-level cases, including 63 native-layout and 16
progressive-disclosure cases. Existing checklist assertions now require complete
continuation text and evidence at each reached step. The new cases cover narrow
regression reads, coordinator exclusion and stall replacement, fork isolation,
every host translation row, both agent model headers, worker disclosure and
Codex sandbox guidance. Scoped source allowances count the changed #110 guidance
while preserving the bounds on unrelated text. These check delivered instructions.
Claude Code inheritance and post-merge U3 behavior remain unobserved here.

Chief review of #113 extends the existing narrow-reading-list case to require
the native execution adapter at its absolute installed path and helper use for
regression-worker build/test commands. Recollection remains 514 top-level cases.

Issue #109's helper PR contributes 26 cases, including 14 chief-review regression
and accounting cases. Collection after the PR #113 rebase gives 540 total cases
and 86 native execution cases. Current totals above are checked against discovery;
the earlier 507-case wording-contract paragraph remains historical. Verbose native
failure previews, ERROR/skip states, device errors, shell-sensitive target input,
failed-run noise filtering, pass silence and Git status failure/timeout behavior
are verified at the helper boundary. A device `@Ignore` observation remains a gap.

Issue #124 stops comparing the installed `control-cli`, `control-ui` and `deslop`
bodies to their Cursor source. The two Cursor integrity cases are renamed and keep
540 top-level cases. The mutation case now has seven subtests per skill: a body
edit that a reseal approves, and six that it cannot, including a removed host
contract. The paragraphs above describing the two allowed additions and six
mutations are historical.

The pstack 0.15.32 merge adds no case and keeps 540 top-level cases. It rebinds
existing cases to the new pin: the upstream-sync fixtures follow the 0.15.25 to
0.15.32 delta, and the 0.15.9 and 0.15.5 snapshots and ledgers still back the
two historical deltas, which regenerate byte for byte. The skill counts move
from 59 to 63, and the list of skills added after 0.2.0 names the four new
skills. The rejection matrix grows from 2,080 to 2,220 subtests with them and
their `pstack/skills/...` aliases. Three principle bodies that were still
byte-identical to the pre-restoration baseline took upstream's rewrites, so 7
remain identical. The all-frontmatter upper bound moves from 16,000 to 18,000
bytes for the four user-only skills; the per-turn skill-list budget is
unchanged. The bug-fix context bound now allows growth in files that are
byte-identical to their pinned upstream source between the baseline pin and
the current pin, which covers the two principles upstream rewrote.

The host.md harness-shape change (issue #136, multi-host P2) adds two cases. `test_upstream_harness_rows_are_mapped` reads
`pstack/docs/harness/claude-code.md` from the archive the pin names and checks that each
first-column cell of each upstream table is a cell of the same-named table in `host.md` or
`host-workers.md`, a key of that table's entry in the test's `DROPPED` map with its reason,
or a key of its entry in `GAPS`, the rows hStack leaves open. Subtests build an archive with
one extra row and expect the case to name it, add `Task` to upstream's Cursor-only features
table, which `DROPPED` lists only under Tools, and add the transcripts row, which `GAPS`
lists only under Paths. Further subtests pin the five coordinator rulings in the
`host-workers.md` cells: the `readonly` precedence, the one model rule, `resume` with the
result's text, the drop rule and the cloud row. Fix round 3 adds subtests for the model
precedence (setup-hstack's ` or ` rule first, a skill's fallback only for a rejected value), the
blocked-seat definition, the Claude Models row as the alias-while-alias-only starting value,
the removed `generalPurpose` mapping and the coordinator creating the worktree. Fix round 4
adds subtests that every `generalPurpose` call in the skills, with `readonly: true`, `false`
or no `readonly`, reaches a `general-purpose` row, and that the Claude Models row maps a role
value such as `claude-opus-5-5 xhigh`.
`test_host_pages_follow_the_page_shape_and_the_index_lists_them` checks each page under
`plugin/adapters/hosts/` for the ten rows in order and a skip line, and checks that the
index lists exactly the pages that exist. `orca.md` is the first page. The test's
`HOST_PAGES` table gives each page its index list and the words only its skip line may use,
and the index stays at most 1,750 bytes, a cap the owner raised from 1,500 on 2026-10-28.
Synthetic pages prove each page and index check can fail. A subtest checks that the shared ADE rule is stated once, in the README, and that the
README repeats the three tests the door names and points back to `host-workers.md`. Another checks that the README names the
door's unobserved limits and that ADR 0004 lets a session outside every listed ADE and agent
read at most the index. Both cases are source checks of wiring and
observe no session. Four existing cases moved a pinned phrase with its
rule: the `AskQuestion`, `poteto-agent` and worker-pointer assertions, the todo-checklist
section name and phrases, the translation-table rows and skip-line sentences, and the
guidance-byte accounting in `test_context_disclosure`. The accounting computes each issue
110 exemption from `ae7cec3` with `git show` and exempts exactly those bytes. The `Cursor-only
features` section that replaced issue 110's `host.md` text is 1,372 bytes against 1,185 at
`ae7cec3`. Its 187-byte growth is pinned and counts against every bound, so no exemption rose
and the host.md cap stays 1,300. The worker allowance stays 500 bytes and the new `Subagent
fields and models` tables are not exempt. Since fix round 4 the door is one sentence at the top of
`host-workers.md`, and `check_core.py` reports a missing door. A subtest checks that it is
the only line in a `plugin/` Markdown file outside the index that names `hosts/`, and that no
measured scenario reads a file there. The same case asserts that the `host.md` opener links
mobile applicability. The
Git-translation subtest is keyed to the hash-pinned baseline sentence, not to a reason's
wording. The todo-checklist case checks that the checklist rule sits under the Tools
table, not in one host's column, and resolves its Playbooks link to the router. The
`poteto-agent` mapping sentence in `hugues-agent` by host went, with its assertion in
`test_native_layout`, because the rename list and the per-host line state the mapping. The
checklist's three step-fidelity sentences went from `host.md` to the router's Playbooks
section, which already carries them and is already asserted.

The P2 fix round 5 host-detection hook adds eleven cases. The Cursor host work adds
seven more in `test_host_adapters`, and the review-1 fix round adds seven more
there and seventeen in `test_check_plugin`. A later merge of two near-identical
Cursor path tests removes one, so the Cursor work nets thirteen in
`test_host_adapters` (91 to 104) and seventeen in `test_check_plugin` (27 to 44).
This release's fix round adds the shared matcher regression, so 105 sit in
`test_host_adapters` and 584 top-level cases collect.
The `test_host_adapters` additions cover the Cursor activity reader's honest
coverage: a Cursor operation that names no absolute path holds, the observed
tools that touch no file are inert, the observed Shell argument keys are
accepted, an unknown provider is an error rather than a silent skip, the
turn marker accepts only the observed shape, and two fixtures built from the
owner's real chats, with every value replaced, read as reviewed records.
The `test_check_plugin` additions give each Cursor manifest rule its own
negative case, so a rule nothing exercised cannot rot unnoticed.
`test_host_adapters.HostDetectionHook` reads the hook's manifest and script: one
`SessionStart` command hook that resolves `${CLAUDE_PLUGIN_ROOT}` and runs the script
directly, so the executable bit is load-bearing, the three Orca variables the script tests
(`ORCA_TERMINAL_HANDLE`, `ORCA_PANE_KEY` and `ORCA_TAB_ID`, all observed set in a real
Orca 1.4.241 pane), the index the message names, no page, and no gate or authority in the
message. It runs the script: a plain session gets no output and no bytes, each Orca
variable alone produces the `SessionStart` context naming the loaded plugin's index, a
plugin path holding a quote and a backslash still yields valid JSON, and a session with
no plugin root gets no message rather than a path guessed from the working directory. It
checks the script is sealed executable and the manifest sealed read-only, that the written
check in `host-workers.md` stays for the hosts that load no plugin hook, and that the
written check and the hook test the same set of variables, so a session that meets one
meets the other. `scripts/check_core.py` holds the same wiring, the two modes and the
emitted output, run through both encoders the script has, so a reseal cannot approve a
broken, non-executable or wrongly-escaping hook. These are source and wiring checks. The
hook firing in a live Claude Code session was observed on 2026-10-28 with Claude Code
2.1.311, and the Orca variables were observed in a live Orca 1.4.241 pane. A session
reading the index because of the hook was not observed.
