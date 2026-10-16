---
status: accepted
---

# Allow audited retirement of an orphan's accounting slot

An Orca restart can leave a launched Execution Attempt without an identity that
hstack can use to prove shutdown. ADR 0002 keeps such an orphan unresolved, and
ADR 0004 counts it against the local worker limit. The user chose to allow an
explicit, audited accounting exception so unrelated queued work can continue.

An operator may retire one bound, launched Orphaned Attempt with its exact Work
Unit revision, attempt ID, decision ID, identity, reason, authority reference,
and acknowledgement that execution may still be running. The operator fields
are audit assertions within the existing local filesystem trust boundary; they
do not authenticate the caller or prove shutdown.

Retirement upgrades that Work Unit to record version 5 and appends one matching
event. It retains the orphan's state, binding, checkout reference, operations,
and earlier journal entries. Acceptance stays blocked. The Work Unit becomes
immutable; another Work Unit and checkout are required for replacement work.
The accounting scan excludes only that validated retired attempt and reports
it separately. A queued admission still has to retry under the normal FIFO
rule. No automatic expiry or inferred closure is introduced.

This qualifies ADR 0002's unresolved-execution rule and ADR 0004's closure-only
capacity rule for the local count. It does not establish a bound on physical
processes: the retired attempt may still be running. Preserve its checkout and
evidence until its actual lifecycle is resolved through a separately reviewed
procedure.
