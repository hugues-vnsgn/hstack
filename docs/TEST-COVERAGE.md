# Python test roots and evidence limits

The current candidate collects **546 top-level unittest cases**. One is a driver that
separately executes **50 frozen 0.2.0 restoration cases**. Do not add the driver
and its children as independent coverage, or describe historical passes as current
native workflow proof. Subtests are not added to case totals.

| Group | Collected cases | Evidence |
|---|---:|---|
| Historical 0.1.0 contracts | 131 | Unchanged SHA256-bound release archive |
| Current checker, historical 0.1.0 fixtures | 27 | Explicit historical validation mode and package mutations |
| Historical 0.2.0 restoration driver | 1 | Executes 50 cases inside a separate hash-bound archive |
| Current source/provenance checks | 48 | test_upstream_sync (37), test_retained_provenance (11) |
| Current installed adapters and regressions | 97 | test_host_adapters (72), test_review_regressions (12), test_rereview_regressions (13) |
| Current native-layout contracts | 56 | test_native_layout; canonical source, permissions, host invocation table, seal acceptance, helper receipt, the bundled non-pstack `deslop` skill (its pinned Cursor source, notice and two allowed additions, and six drift mutations that resealing cannot approve), budgets (including the explicit list of skills added after 0.2.0 that have no historical context counterpart) and the native-reach lint (a corpus of 47 reviewed contradictions in five line shapes each, 18 correct sentences, the package wiring and a one-entry allowlist), plus the router rewrite: router section pointers and the Principles index, the four dead Cursor frontmatter fields through the plugin check, and seven read-only cases on the router and the files it points at (title, host tool names and description, mobile routes, autonomy placement, single-source model defaults, the scope of restated obligations, the registered `hugues-agent` name and question tool per host, worker definition), and three source-wording cases for issue #48 (the agent finds its own mode file, the Skill-tool rule, the playbook headers) |
| Current progressive-disclosure contracts | 13 | test_context_disclosure; retained rules, mandatory phase reads, complete declared source inventories, the skill-list budget (including its pinned pre-PR `a67df90` point), YAML-description quoting, the router's initial read set against `main`'s pinned read set and bound resources |
| Current installed-tolerance regressions | 45 | test_installed_tolerance; bootstrap dependencies, host metadata, unreadable folders, umask modes, every spelling of a raw skill read, normalized paths (`.`, `..`, letter case, repeated slashes), open quotes and split code spans, every revision/syntax a skill-body guard must still check, the plan-check helper's operand, and a rejection matrix of 2,000 cases (335 `read-workflow`, 1,610 `translate-plan` and 55 in-plan cases) over all 55 bundled skills, the legacy aliases of the 54 that have one, consumer and external paths, with symlink and traversal cases and positive controls |
| Current verification-contract gate | 19 | test_verification_contract; installed bound comparison of committed plans, both field regressions, exact rulings, absent baselines, receipt-only edits, malformed inputs and checker drift; no host isolation or mobile proof |
| Current setup-to-proof contracts | 6 | test_setup_proof; mobile recipe requirement, native holds and non-mobile harnesses, host handoffs, model tiers, and installed mobile-proof reads from an external consumer with a decoy path. Includes rejection of absent, failed or text-only screenshot reads in native evidence. These six cases check source/commands and evidence parsing, not host or device execution. |
| Current approved requirements/proof | 46 | test_program_proof; installed JSON checks, artifact/build identities, safe design decoding, workflow reach, macOS process write isolation and rejection of the two withdrawn host-tool verbs |
| Current program scheduling/recovery | 38 | test_program_control; installed policy gates, whole-group dispatch, saved progress, usage coverage, process groups, device receipts, concurrent writers and runtime waiting |
| Current mobile coverage | 19 | test_mobile_coverage; installed risk coverage, exemptions, profile/default compatibility, operator rulings and integrity drift; synthetic plan fixtures, no native/mobile behavior claim |
| Total collected | 546 | Current, mixed and historical scopes remain distinct |

The [native setup-to-proof check](../tests/setup-proof.md) runs separately on an
authorized Mac. Its real iOS UI tests and Claude sessions are not included in the
546 Python cases. The opt-in CI workflow requires a provisioned native runner.
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
Bindings cover canonical files, metadata, adapters, policies, runtime code and
permission modes. Tests reject missing/extra files, symlinks, world-writable files,
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

Native-layout cases compare all 55 public names (54 from pstack and `deslop`) and modes, archive/source identity,
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
Their source and dependency inputs remain unchanged; the Node plan checker did
change and has current Python/Node integration coverage. The disclosure-pass
Bun/TypeScript run was blocked before execution by sandbox preflight `EPERM`. The
review-fix pass ran it on a scratch install of the candidate: Bun 1.4.2,
`bun install --frozen-lockfile` through the session proxy, 52 of 52 `bun test orch
watch-pr` cases and strict `tsc --noEmit` for watch-pr passed. That run is outside
the Python suite and is not counted above. See the
[helper input receipt](HELPER-INPUTS.json) and [context report](CONTEXT-FOOTPRINT.md).

Issue #37 adds nineteen installed verification-contract cases, bringing the current
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

Issue #48 adds three native-layout cases, bringing the current total to 546.
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
