> These receipts describe the released 0.1.0 bytes and their recorded revisions. They do not validate the restored development core; see [current validation](CORE-RESTORATION.md).

# Support evidence

Status snapshot: **6 October 2026**, package version **`0.1.0`**.
Combined [PR #13](https://github.com/hugues-vnsgn/huguesStack/pull/13) merged
into main at `18c73d183f19ed9b401f4b58c6743705a6bfc3da`.
Consult [GitHub Releases](https://github.com/hugues-vnsgn/huguesStack/releases)
for publication and final-check receipts. The [evidence index](evidence-index.md) records historical revisions,
receipts, failed attempts and limits. Read [WORKFLOW](WORKFLOW.md) to start a task
and the [release notes](RELEASE-0.1.0.md) for the review scope.

Use per-cell states **authored**, **static-tested**, **observed-pass**,
**observed-fail**, **blocked** and **deferred**. Separately record run outcomes
**pass**, **fail**, **flaky**, **skipped** or **incomplete**. Review completion
and verdict are separate facts. A blocked test is unrun; a skip is an excluded
assertion. A successful same-artifact retry retains its flaky outcome.

| Cell | State | Evidence and limits |
|---|---|---|
| Historical RC1 package, 27 skills and local contracts | static-tested | Initial RC1 `5af676e7486291fbfac1fb81263c2aecec629476`: fresh 120 framework tests and seven checks PASS; independent Astra High CLEAN. This row binds the historical initial RC1 head and covers no RC2 edit. Historical merged-main receipt remains separate |
| RC2 retained tools and wiring | static-tested | 35 skills / 79 plugin files. Routing candidate `68cb710`, tree `41dcde6fbe6330aec21ec6570fe70b107ba69da9`: 194 framework tests/seven checks PASS, independent same-host Astra High CLEAN. These checks cover that candidate; later documentation heads require their own checks/review. [Integration](retained-integration.md) |
| RC2 host loading and route previews | observed-pass | At `e2ff899`, Claude native session-local loading registered 35 skills and the worker; Codex used manual project skills and separately discovered the uninstalled marketplace. Each host matched 16 routes and 87 steps. Both inferred unsupported Kotlin in the Android/Gradle-only case; [RC2 receipt](rc2-host-validation.md) separates the gap |
| RC2 lane evidence | observed-fail | At `dba645f` plugin bytes, both candidate hosts made supported language/lane choices across six scoped cases and copied 36 steps exactly. Initial historical snapshot: all four baseline/candidate strict fixture comparisons FAIL on target formatting and/or lane fields. Adjudication accepted checker false positives and required target-component evidence/declaration anchors; raw failures remain. No full fixture PASS for that snapshot. [Receipt](rc2-host-validation.md#lane-evidence-probes) |
| RC2 repaired lane previews | observed-pass | Each host passed six unique cases and 36 copied steps using uncommitted corrected plugin bytes, planning-only. All 79 fingerprints subsequently match committed `68cb710`; no clean-head invocation or full workflow adherence claim. [Receipt](rc2-host-validation.md#repaired-schema-probes) |
| RC2 bounded retained workflow observations | observed-pass | Native Claude simple `how`, separate test-before-fix `tdd`, narrow `blast-radius`: six tests, two intended RED failures before production, six GREEN passes; fourteen overlapping outer checks. Managed Codex design-only `architect`/`arena` guardrails observed; synthesis inspected, runtime unrun. [Limits](rc2-host-validation.md#bounded-workflow-observations) |
| RC2 full eight-workflow adherence | blocked | Bounded native Swift and Kotlin work is now observed below; full eight-workflow adherence, native todo integration and four-domain task completeness remain unproven |
| Upstream inventory | static-tested | pstack 0.15.32 at upstream `main` `e73df471`, released in 0.5.5 and kept in 0.5.7; 200 responsibilities reconciled; delta from 0.15.25: 31 added / 43 changed / 0 removed. [Sync procedure](upstream/README.md); exact upstream benchmark link remains deferred |
| Claude historical cold load | observed-pass | WP1 fresh-session probe on its historical body |
| Claude project recipe invocation | observed-pass | Read-only native Skill invocation passed; two earlier unknown-skill probes retained |
| Claude verification generator invocation | observed-pass | Complete private candidate authored; this invocation wrote no consumer guide or ran a cycle |
| Claude historical RC1 read-only routing | observed-pass | Claude Code 2.1.290 / actual `claude-opus-5-5`: session-local native plugin load, 16 cases/15 routes (fourteen playbooks plus `interrogate`), 87 exact numbered steps. Original eleven fixture domain/proof decisions matched; supplemental Android-only language inference was over-specific. No execution proof |
| Codex marketplace discovery/manual path | observed-pass | Historical discovery without installation, manual project-skill probes and direct-read fallback; WP2 planning preview: 11 routes/61 steps on its recorded head |
| Codex native install/invocation | blocked | Unrun; global installation outside recorded probe authority |
| Codex historical RC1 read-only routing | observed-pass | Codex 0.160.1 manual project-skill/direct-read fallback: 16 cases/15 routes, 87 exact numbered steps; original eleven fixture domain/proof decisions matched. Android-only implementation language correctly unresolved. Actual served model unconfirmed; no native install claim |
| Historical RC1 plugin/settings preservation | observed-pass | All 54 plugin fingerprints and both user-settings hashes unchanged before/after; exact RC1 plugin bytes at `21a82942019292f7212ff1185e9ef187ac96e86d` match. [Receipt and binding limits](rc-validation.md) |
| Native todo integration | blocked | CLI previews lacked native todo tools and displayed checklists. Managed design adapter exposed a plan tool but did not preload every design phase; full native todo adherence remains unproven |
| Claude historical RC1 synthetic delegation/artifact review | observed-pass | Fresh registered `hugues-stack:hugues-agent` wrote one scratch function; fresh native Explore reviewer read actual source and found no behavior defects. Parented mode/principle/target reads retained; same-host process independence only. Initial ineffective Write rule/denial retained as setup failure, not a platform automatic-review rejection |
| Historical RC1 synthetic artifact behavior | observed-pass | Same artifact: 22 outer-worker assertions PASS and 14 independent coordinator literal checks PASS. Separate overlapping sets, not 36 unique tests or additions to 120 framework tests. No native-session commands/tests ran. [Binding and limits](rc-validation.md) |
| Historical RC2 static recipe/cold pickup | observed-pass | Native Claude generated and freshly loaded a static Kotlin recipe; Codex read its Markdown directly. Fresh read-only Codex pickup reopened actual Git state and preserved two RED failures, with outer hash checks. No mobile cycle, actual pause/compaction or resumed GREEN. [Receipt](rc2-host-validation.md#bounded-workflow-observations) |
| Full mode execution/multi-turn persistence | authored | Actual S1/K1 pause, checkpoint-only fresh pickup and resumed GREEN now observed. End-to-end mode execution, compaction and native persistent todo remain unproven |
| Applied generated-recipe cycle | blocked | Later approved guide body applied; 12 Android/eight iOS tests and five local journeys passed with retained failed attempts/fallback. Final iOS boot-state preservation unresolved; revised guide native invocation unrun. No full clean-cycle pass |
| Historical KMP shared navigation/header task | observed-pass | Android/iOS logic and native callers observed on bounded artifacts; older 11-test snapshot remains distinct from later 12-test reports |
| Historical CMP journey/header task | observed-pass | Android and two iOS runtime journeys, normal/enlarged text within recorded scope; successful attempts followed retained failures. Native Android enlarged text/forced ellipsis unrun; iOS bottom-tab clipping remains outside header scope |
| Android Jev labels | observed-pass | One approved run: 3/3 checkpoints, six claims, probabilities 0.98 to 0.99. Labels only; no new transmission or renewed authority |
| iOS Jev judgment | blocked | MobileBuildMCP driver conflicts with consumer's XcodeBuildMCP rule; local screen evidence remains separate |
| Native Swift build and selected Swift Testing tests | observed-pass | NetNewsWire at `626f08c3e5bf542a37f2bd59c65e13ffe0417bdf`: five methods/seven invocations PASS, zero failures/skips, Xcode 26.4.1/iOS 26.4.1. Historical; not rerun on Xcode 27. Approved hosted startup created default account/feed containers, retained |
| RC2 native Swift S1 feature | observed-pass | Seven-case RED: two passes/five intended missing-command failures; actual pause/fresh pickup; separate production change. GREEN, recipe and maintenance each: 12 method identities/14 invocations, zero fail/skip and four inspected native bar images on Xcode 27/iOS 26.4.1. UIKit/synthetic delegate selector dispatch only. [Proof and limits](rc2-native-feature-proof.md) |
| RC2 S1 complete maintenance/clean cycle | blocked | Source/live checkpoint coverage 4/4 and owned app/daemon/socket-parent/window cleanup proved. Original simulator boot-state restoration unsupported; original data continuity unproven. Current accepted baseline identities preserved, content changed during approved startup. No full clean-cycle PASS |
| Native Kotlin demo build and selected unit tests | observed-pass | Now in Android at `a49ed253d75e61a2b6ab80a8da677b57437b08eb`: offline demo build and nine SearchViewModel tests PASS, zero failures/errors/skips. Unit results historical and not rerun in Espresso 3.7 round |
| Native Kotlin selected UI tests | observed-pass | Five existing non-image search methods PASS in one Espresso 3.7 instrumentation attempt; zero fail/skip/unrun, Android 16/SDK 36 with empty minor field. Strict core/idling 3.7 dependency change limited to isolated AndroidTest configuration. Original Espresso 3.5 five initialization failures retained; changed APK/conditions are not a flaky retry |
| RC2 native Kotlin K1 feature logic | observed-pass | 15-case RED with three intended failures; actual pause/fresh pickup; separate ViewModel normalization fix, 15/15 GREEN. Offline UI-test APK built after one retained compile failure and one corrected retry. [Proof](rc2-native-feature-proof.md) |
| Historical RC2 K1 native readiness | blocked | Original readiness snapshot: Six selectors/four checkpoints have source coverage; all new native, recipe and maintenance runs unrun. Connected phone/existing emulator blocked readiness; no task-owned target/package started or unrelated device targeted. Later results have their own receipt below |
| RC2 K1 native UI/recipe/maintenance | observed-pass | GREEN, recipe and maintenance each: six exact cases PASS, zero fail/skip/unrun and four reopened, decoded, coordinator-viewed native images. Android 16 / SDK 36 / full SDK 36.1; same retained APK, bounded feature host/fakes only. Owned cleanup and evidence survival verified. Original STOP/failures retained; no Room/full-app/hardware Enter/analytics proof. [Receipt and image limits](rc2-native-feature-proof.md#k1-private-continuation) |
| RC2 native project recipe discovery | observed-pass | Both hosts actually read full S1/K1 recipe Markdown. Claude catalog omitted these recipes; Codex native discovery is self-reported without raw catalog proof. Direct read establishes fallback only. [Limits](rc2-native-feature-proof.md#recipe-discovery-and-preservation) |
| Layer 2, feature maps and CLI-first addition | deferred | Managed-worker runtime outside Layer 1; draft PR #2 remains post-first-release work |

PRs [#1](https://github.com/hugues-vnsgn/huguesStack/pull/1),
[#3](https://github.com/hugues-vnsgn/huguesStack/pull/3),
[#4](https://github.com/hugues-vnsgn/huguesStack/pull/4),
[#5](https://github.com/hugues-vnsgn/huguesStack/pull/5),
[#6](https://github.com/hugues-vnsgn/huguesStack/pull/6) and
[#7](https://github.com/hugues-vnsgn/huguesStack/pull/7) and
combined [#13](https://github.com/hugues-vnsgn/huguesStack/pull/13) are merged.
[#2](https://github.com/hugues-vnsgn/huguesStack/pull/2) remains an open deferred
draft. Historical Opus/Fable and Astra reviews keep their original scope.
Same-host review provides process independence, not cross-host proof.

Historical RC2 host bindings retain their exact bytes. The 0.1.0 change alters
the plugin manifest version while preserving skill, playbook and worker bodies;
no fresh host load of that manifest has been observed.

The owner approved eight retained leaves for 0.1.0 on 6 October 2026:
`how`, `why`, `architect`, `arena`, `tdd`, `blast-radius`,
`maintain-verification-skill` and `correct`. All eight are authored and
static-tested, with direct playbook handoffs in RC2. The same approval defers
`swarm`, `show-me-your-work` and `setup-huguesstack` to 0.2. Feature maps,
CLI-first verification and Layer 2 retain their existing deferred scope.
Bounded synthetic observations cover parts of `how`, `tdd`, `blast-radius`,
`architect` and `arena`; they do not establish full adherence of any eight-tool
workflow set. The later [native proof](rc2-native-feature-proof.md) adds bounded
Swift execution and Kotlin unit/build and bounded native cycle evidence without
establishing that set.

Swift and Kotlin RED/GREEN work and checkpoint-only fresh pickup are observed.
Bounded K1 device/recipe/maintenance proof is observed. Four-domain feature-task coverage, complete mode execution,
compaction/native persistent todos and a full clean generated cycle remain incomplete. The revised [plan](PLAN.md) permits an owner checkpoint with labelled
gaps; those gaps never become observed support. Target remains
**9 October 2026, end of day GMT+7**.

Historical [WP1](wp1-validation.md), [WP2](wp2-validation.md),
[WP3](wp3-validation.md) and [verification continuation](verification-continuation.md)
snapshots are preserved. Raw native artifacts stay outside the public repository.
