# Approved requirements and proof

Implementation scope: issues #31, #36, #37 and #38. Keep pstack's public names,
phase order, worker roles and historical archives. New programs use an approved
requirements record and the installed `program-check` gate at the existing
verification step. Existing programs keep their pinned installation until an
explicit migration; old reports are not silently certified by the new gate.

## Acceptance

| Case | Required result |
|---|---|
| Builder replaces persistence with reset | Gate holds against the approved original |
| Approved file or source snapshot changes | Trusted approval digest holds |
| Installed plugin changes | Existing binding holds |
| Worker writes approved records | Process isolation denies the write |
| Missing, empty, unreadable or unrelated proof | No supported pass |
| Wrong build, platform or approved revision | No automatic evidence reuse |
| Independent inspection rejects a claim | No supported pass |
| Crash, unresolved defect or data anomaly | Plain outcome and unresolved finding remain visible |
| Unrun, blocked or owner-waived check | Separate result, never a fabricated pass |
| Open owner questions | Every unresolved question appears in the verdict |
| Matching inspected evidence | Gate accepts the requirement |

Tests exercise installed commands in disposable external consumers. The owner
authorized implementation of fixes 1 and 2 in the conversation.
OS-isolated subprocess observations are separate from native host/mobile proof.

## Implementation sequence

1. Add one installed record checker with negative tests through its CLI.
2. Add a restricted subprocess launcher and observe protected-write rejection.
3. Wire one disclosed reference into existing planning, verification and report
   steps; retain the original gates and canonical public names.
4. Run all maintenance checks, update current test counts and receipts, and
   review against the approved scope. Preserve unobserved host checks as gaps.

## Authority

The coordinator retains the owner's real approval reference and digest outside
worker write access. A digest or a JSON approval field cannot authenticate an
owner. Artifacts are independently inspected; the checker validates identities
and consistency, not the semantic truth of screenshots or tool recollections.
Filesystem isolation is enforced by the process host, not by a Markdown rule.
External tools and MCP servers need their own equivalent write restrictions.
