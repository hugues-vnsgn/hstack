# Program record format, schema 1

Use UTF-8 JSON with unique keys. Keep all five records and source/artifact
snapshots in the protected owner control directory from [program proof](program-proof.md).
Use absolute CLI paths. Snapshot/artifact paths are relative to their record's
directory, with no `..`, symlinks or hardlinks. Unknown fields hold. Retain
original command/tool arguments, responses and device details in linked receipts;
the small index below does not replace that capture trail.

## Approved checklist

```json
{
  "schema_version": 1, "program": "filters", "revision": "1",
  "approval_reference": "actual-owner-message-reference",
  "sources": [{"id": "design", "snapshot": "design.txt", "sha256": "<64-hex-sha256>", "locator": "section: saved filters"}],
  "requirements": [{
    "id": "R-001", "source_ids": ["design"],
    "expected": "Remember filters after reopening.",
    "checks": [{"id": "C-001", "target": "android", "actions": ["choose AIR", "close", "reopen"]}]
  }]
}
```

Make every source, requirement and check ID unique. Use separate checks for
different targets. Include design conflict decisions among the hashed sources.
Obtain approval before building. Retain the approved file's digest in trusted
controller state, not in a worker-replaceable approval file.

For `mobile-risk-v1`, retain the committed plan as another hashed source. Add
this field to the approved checklist before its existing owner approval:

```json
"verification_plan": {
  "source_id": "mobile-plan", "section": "PR 1",
  "checks": [{"lane": "1", "check_id": "C-001"}, {"lane": "2", "check_id": "C-002"}]
}
```

Map every live lane once, including extra checks. Each mapped requirement names
the plan source and uses the lane's exact pass-condition text as `expected`.
Its check uses the exact target ID and `["<exact Action text>"]`. Omit grammar
delimiters and receipt attachments from these values. Other unit/performance
checks may coexist. A documentation/workflow plan has an empty live mapping and
still needs its approved executable checks and their actual evidence.
The derived verdict includes plan digest, section, work type, mapping and explicit
live/performance applicability. Non-applicability is not a device pass. Records
without a mobile plan retain their previous format; migration needs approval.
The checker cannot discover an omitted plan or authenticate an owner's approval.

## Candidate

```json
{
  "schema_version": 1, "program": "filters",
  "requirements": ["<copy the exact approved requirement objects>"],
  "source": {"commit": "<40-or-64-hex-commit>", "dirty_sha256": null},
  "builds": {"android": {"path": "/absolute/frozen/app.apk", "sha256": "<artifact-hash-result>"}}
}
```

Replace the placeholder array with the approved objects, not strings. For a
dirty build, use the digest of the retained diff/untracked receipt instead of
null. Capture that identity from the actual worktree. Use exact target keys from
the checklist. A blocked/unrun target can have no build entry. Hash whole `.app`
directories with `artifact-hash`; do not hash only the executable.

## Inspected proof

```json
{
  "schema_version": 1, "program": "filters", "approved_sha256": "<trusted-digest>",
  "source": {"commit": "<same-candidate-commit>", "dirty_sha256": null},
  "builder": "actual-builder-id", "verifier": "actual-independent-verifier-id",
  "attempts": [{
    "id": "A-001", "check_id": "C-001", "target": "android",
    "build_sha256": "<same-build-digest>",
    "started_at": "2026-10-12T10:00:00Z", "finished_at": "2026-10-12T10:01:00Z",
    "actions": ["choose AIR", "close", "reopen"], "status": "passed",
    "actual": "AIR retained after reopening", "user_visible": "works",
    "artifacts": [{
      "path": "attempts/A-001/attempt.log", "kind": "text", "sha256": "<file-sha256>",
      "attempt_id": "A-001", "target": "android", "build_sha256": "<same-build-digest>",
      "captured_at": "2026-10-12T10:00:30Z"
    }],
    "inspection": {"reference": "actual-independent-inspection-receipt", "supports": true}
  }]
}
```

Use actual timezone-aware timestamps. Attempts need unique IDs and distinct
finish times per check so retry order is unambiguous. Executed actions must
match the approved sequence; retain exact argv/tool calls in the artifact trail.
Artifact kinds are `text`, `json`, `png`. Use file SHA256 for their original bytes.
The inspection receipt must establish meaning, freshness and target association.
Do not invent it from the JSON index.

| Field | Allowed values/rule |
|---|---|
| `status` | `passed`, `failed`, `untested`, `blocked`, `waived`, `inconclusive` |
| `user_visible` | `works`, `crash`, `error`, `wrong-result`, `unobserved` |
| Unrun/blocked/waived attempt | Empty actions/artifacts, null build digest, unobserved outcome; describe the reason in `actual` |
| Optional `waiver_reference` | Must match the actual approval in coordinator state |
| Optional `resolution_reference` | Independent explanation and proof resolving earlier failures; a passing retry alone is insufficient |

Keep all attempts for the current build. Archive previous build rounds rather
than relabeling their artifacts. A crash/error/wrong result always produces a
failed row even if its declared status says passed.

## Coordinator state

```json
{
  "schema_version": 1, "program": "filters",
  "findings": [{"id": "F-1", "kind": "data-anomaly", "description": "Saved value changed unexpectedly", "status": "open"}],
  "decisions": [{"id": "D-1", "question": "Which design source wins?", "status": "open"}],
  "waivers": [{"check_id": "C-001", "approval_reference": "actual-owner-waiver-reference", "reason": "Owner accepts the named missing check"}]
}
```

Use empty lists only when the controller's complete current state has none.
Findings and decisions have unique IDs within each list, status `open` or
`resolved`; resolved rows require a nonempty `resolution_reference`. Do not
resolve a defect by filing it elsewhere. A waiver does not remove a finding or
owner decision. Keep these lists independent of the verifier's proposed proof.

## Derived verdict

Retain the checker output as `verdict.json`; do not author it by hand. A valid
report includes the expected/actual result and attempts per check, remaining
findings, open decisions, missing proof and `ready`. Only all-passed checks with
no open findings/decisions yield `ready: true`. A malformed input yields a hold
with problems; null state lists mean completeness could not be established.
On a hold, readable reported outcomes remain in `reported_outcomes` with
`accepted: false`; these are unverified claims, so a missing artifact cannot
erase a reported crash. Null outcomes mean the record could not be read.
