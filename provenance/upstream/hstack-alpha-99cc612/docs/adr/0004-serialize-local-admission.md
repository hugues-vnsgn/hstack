---
status: accepted
---

# Serialize admission within one configured local store

A configured Work Unit store is one capacity domain. Coordinators for different
Runs and projects must use that same store to share a worker limit. Other stores
and terminals launched outside hstack are excluded; this is not a machine-wide
worker budget. `capacity configure` accepts `{"maxWorkers":1}` through `--request`
and `--store`. The allowed integer range is 1 through 32. `capacity status` takes
an empty object and reports the configured limit, occupancy, and FIFO queue.

Keep Work Units authoritative. Count attempts in `admitted`, `active`, and
`orphaned` states by validating every store record. Acceptance, quiet output,
uncertain operations, preserved sessions, and coordinator loss do not release a
slot. Only `not_started` or proven `closed` execution does. Reject corrupt records,
record identity mismatches, and symlink records or policy files conservatively.

Admission, legacy import, and orphan transitions acquire the store capacity lock
before the Work Unit lock. Orphaning can turn a `not_started` attempt back into
potentially live execution, so it also needs the guard. Policy changes use the
same capacity lock. Acquire this lock even before a store is configured so first
configuration cannot race an admission. Other aggregate updates retain their own
Work Unit locks: an atomic closure racing a scan can only overcount capacity.
Never hold either lock across a supplier or provider call.

A full store queues validated admission requests without changing their Work
Units. Persist the FIFO queue in `.capacity-queue`; it records waiting intentions,
not a second registry of active executions. Return exit 75 with `outcome: queued`
and the unchanged `workUnit`. The queue identity is Work Unit plus attempt ID.
Repeating the same pending request is idempotent; changing its fields fails.
An older waiter has priority even when a slot becomes free. Retry the original
request to claim a free slot; there is no background dispatcher. Legacy imports
and orphan transitions that would add occupancy fail when full or behind a
waiter; operators must reconcile the capacity before importing unresolved work.

Publish the admitted Work Unit before removing its queue entry. On subsequent
capacity scans, an existing attempt proves a stale queue entry was already
served and permits its removal, including when that attempt has since closed.
Queue entries that no longer match an admissible assignment remain conservative
blockers: stop coordinators and reconcile those requests before editing the
queue. Reducing the limit below existing occupancy is rejected.

Locks use atomic directory creation and bounded waiting. Locks are never stolen.
After a killed process, establish that no updater is running, inspect Work Units
and queue state, then remove `.capacity-lock` (and a surviving Work Unit lock)
only after reconciliation. Same-directory renames provide process-crash
consistency, not power-loss durability. An unconfigured store retains legacy
unbounded admission behavior.

[ADR 0006](./0006-allow-audited-orphan-retirement.md) qualifies the count for
one explicitly retired orphan. The validated retired attempt is reported
separately and no longer occupies a local slot. Its execution may still exist,
so the configured limit no longer bounds physical processes after retirement.
