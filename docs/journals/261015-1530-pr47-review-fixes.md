---
date: 2026-10-15
session: PR 47 review fixes
---

# Journal: 2026-10-15 — PR 47 review fixes

## Context

Judge the external review before changing the installed-payload boundary. The
owner authorized confirmed fixes, a push and another Claude review, without merge.

## What Happened

- Reproduced a context-mismatch error misclassified as a native denial and a
  Python 3.9 discovery failure. Tightened denial matching and removed the ordinary
  suite's dependency on tomllib.
- Added a bound, read-only helper prerequisite check matching the pinned Bun
  bootstrap's package/NUL/lock key. Kept upstream helper bytes unchanged.
- Required shell proof from the actor's native command/result, exact-root policy
  evidence, and coverage of hooks and background writers.
- Added prepared-helper and missing/stale/uncovered startup smoke scenarios,
  durable evidence identity and hash manifests.

## Reflection

Private receipts supported the original observations, but their labels and
locations made independent verification harder. The revision binds evidence to
exact program bytes and actors while preserving explicit host-coverage gaps.

## Decisions Made

| Decision | Rationale | Impact |
|---|---|---|
| Prepare dependencies in disposable copies | Protection must include generated caches | No bootstrap exception inside consumer programs |
| Keep pinned playbooks and helpers | The defect concerns host mechanics and proof | pstack topology and landing rules stay intact |

## Next Steps

- All eight clean-commit native scenarios passed. The receipt records exact
  identities and hashes. All 439 tests pass on Python 3.14; the frozen Python 3.9
  historical driver gap remains documented.
- Push and request Claude rereview of the exact head. Keep the PR open for the owner.
