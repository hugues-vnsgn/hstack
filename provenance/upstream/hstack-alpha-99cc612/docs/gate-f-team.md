# Gate F: supervised Codex teams

The first slice adds a configured-store worker budget and required independent
review of captured code and evidence. It keeps the serial implementer → reviewer
workflow. Python 3 is required for the `team` commands and acceptance of reviewed
v4 Work Units; ordinary v2/v3 work retains the shell/jq interfaces.

## Capacity domain

Configure one local store before submitting work:

```text
hstack capacity configure --store DIR --request capacity.json
```

The request is `{"maxWorkers":1}`. Use the resolved setup configuration's
`concurrency.maxWorkers` value when constructing it. All Runs/projects managed
through that store share this budget. Different stores and external user
terminals are outside the domain; this is not a machine-wide process limit.
An unconfigured store retains the older admission behavior.

All Work Unit admission, unresolved import, and occupancy-increasing orphan
transitions use the same capacity lock before the Work Unit lock. Capacity is
derived from validated Work Units. Admitted, active, and orphaned attempts occupy
slots. A completed turn or accepted result does not release one. An attempt must
be proven not started or authoritatively closed.

When capacity or FIFO priority prevents admission, execution and Codex launch
return `outcome: queued`, with no provider launch. Low-level Work Unit admission
returns the same outcome with exit code 75. The waiting request is durable;
repeat the original request after capacity becomes available. This serial
workflow has no background process draining the queue. Do not treat an uncertain
mutation as a queued request or retry it.

`hstack capacity status --store DIR --request empty.json` reports occupancy and
the FIFO queue. A stale lock or invalid queued identity requires operator
inspection. Verify the writer stopped before removing its exact lock. A queued
identity cannot be replaced with different admission parameters. To withdraw a
waiting request, use `capacity cancel` with its exact `workUnitId` and `attemptId`.
This removes only the queue entry; it never releases an admitted worker's slot.
An explicit later submission joins the queue again. See
[ADR 0004](./adr/0004-serialize-local-admission.md).

## Bind the review requirement before work

Create distinct implementation and reviewer Work Units using the ordinary
`work-unit create` command. The implementation declares its expected checks plus
`{"checkId":"independent_review","evidenceRef":"review.json"}`. The reviewer
declares that review evidence check in its own assignment.

Before the implementation's first attempt, call `work-unit review-bind` with:

```json
{
  "workUnitId": "implementation",
  "expectedRevision": 1,
  "reviewerWorkUnitId": "reviewer",
  "baseCommit": "FULL_40_CHARACTER_COMMIT_SHA",
  "writableFiles": ["app/src/main/Example.kt", "app/src/test/ExampleTest.kt"]
}
```

This one-time binding upgrades only the implementation record to v4. Existing
v2/v3 creation and schemas are unchanged. The reviewer, base, and permitted files
cannot be silently changed after execution starts. Codex session observation
preserves the v4 requirement.

Before publishing v4, `review-bind` verifies that the reviewer is a distinct,
existing Work Unit and declares `independent_review` with `review.json` evidence.

## Serial execution recipe

1. Create an isolated Orca implementation checkout at the bound base. Give Codex
   a standalone brief with permitted files, exact test commands, evidence paths,
   and result destination. Use the existing `codex launch/send/status` interfaces.
2. Independently check the implementation result and declared evidence. It must
   contain the expected checks except `independent_review`; do not accept the
   implementation yet. Confirm provider, shell, and terminal shutdown.
3. Capture work with `team snapshot`. Its request contains `workUnitId`,
   `checkout`, `baseCommit`, `resultPath`, and `evidenceRoot`. The command verifies
   the closed implementation attempt, actual diff, permitted files, reported
   changed files, and passing check evidence. HEAD must still equal the bound base.
4. Create a separate clean Orca reviewer checkout at that base. Call `team export`
   with `snapshotRef` and `destination`. It copies captured changes and exposes
   the diff, result, and test evidence under `.hstack/review-materials/`.
5. Give a fresh Codex reviewer the returned standalone review brief. It must
   inspect the actual code/evidence and write a verdict naming the snapshot hash.
   It may run checks but must not edit the implementation. Validate the reviewer's
   normal result/evidence, accept its Work Unit, and confirm its shutdown.
6. Call `team accept` with `workUnitId` and `snapshotRef`. The command combines
   captured checks with review evidence and invokes protected Work Unit acceptance.
Missing, blocking, incorrect, or stale review evidence prevents acceptance.

Snapshot scope is explicit: it fingerprints tracked changes, ordinary untracked
files, and explicitly permitted ignored source files. It excludes runtime
metadata under `.hstack`, `.agents`, or `.gradle`, and generated paths named
`build`; capture those as declared evidence instead. It does not claim to
fingerprint arbitrary ignored filesystem content. A private Git index creates
the exported diff, so snapshotting never modifies the user's index.

Every team command uses `--store DIR --request FILE`. The review verdict is:

```json
{
  "schemaVersion": 1,
  "implementationWorkUnitId": "implementation",
  "reviewerWorkUnitId": "reviewer",
  "snapshotSha256": "SNAPSHOT_SHA256",
  "verdict": "pass",
  "findings": []
}
```

Use `changes_requested` when corrections are required. Findings contain
`severity` (`blocking` or `nonblocking`), `message`, and a relative `file` path.
A `pass` label cannot override a blocking finding. The reviewer must have a
different Work Unit, terminal binding, and physical checkout. Observed provider
sessions must differ when both are available.

## Evidence and recovery limits

Snapshots retain changed file bytes/modes, base identity, diff, result, and test
evidence. The protected `work-unit accept` path independently verifies the review;
calling it directly cannot bypass the requirement. Changed implementation code
or evidence invalidates the review. Acceptance names the immutable captured
artifact, not an atomic promise about a mutable checkout afterward. Landing needs
its own fresh check. See [ADR 0005](./adr/0005-bind-review-to-captured-work.md).

No command implicitly commits, merges, deletes a checkout, selects another
provider, or bypasses Codex permissions. Gate D's supervised readiness/input
handling and uncertain-operation rules still apply. Quota exhaustion is not
completion; keep the attempt and its capacity accounted for until recovery or
confirmed shutdown.

## Android pilot

The [disposable Android fixture](../packs/mobile/references/android-pilot.md)
provides the first mobile check. Its exact-threshold bug must fail both a new unit
test and the emulator check before the fix. Compilation alone cannot close this
pilot. Gate E integrations remain deferred.

## KMP and Compose pilot

The [F4 fixture](../packs/mobile/references/kmp-compose-pilot.md) extends the
proof to shared Kotlin logic and Compose UI on Android and a thin SwiftUI iOS
host. Its live worker added the same boundary regression on both targets, fixed
the shared predicate, and passed all three UI cases on both installed apps. A
distinct reviewer reran the tests/builds and accepted the captured snapshot.
See the [verification report](../plans/260905-2042-f4-kmp-pilot/reports/tester-final.md).
This local debug-artifact proof does not certify production applications,
release signing, physical devices, or all mobile toolchains.
