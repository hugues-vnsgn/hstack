---
status: accepted
---

# Bind required review to captured work

Gate F requires an independent review that cannot be skipped through the
lower-level acceptance command. Work Unit remains the acceptance authority.
Bind a reviewer Work Unit, base commit, and permitted files before the first
attempt. Binding rejects an absent reviewer, the implementation Work Unit itself,
or a reviewer that does not declare `independent_review` with `review.json`
evidence. Only these records upgrade to v4; published v2/v3 schemas stay unchanged.

Capture the implementation's diff, changed file bytes and modes, result, and
check evidence in one immutable snapshot. The reviewer works in a separate
checkout or snapshot and names the captured snapshot hash in its verdict. The
reviewer's own Work Unit must be independently accepted and closed. A blocking
finding, missing result, wrong reviewer, or stale implementation rejects acceptance.

The snapshot covers tracked changes, ordinary untracked files, and explicitly
permitted ignored source files. It deliberately excludes runtime metadata and
generated build output. A private Git index produces the patch so capture never
rewrites the user's index.

The protected Work Unit acceptance path verifies the snapshot, reviewer evidence,
and current implementation fingerprint before recording acceptance. Acceptance
means acceptance of the named captured artifact. A Work Unit lock does not stop
an unrelated process from editing a checkout afterward; no atomic acceptance of
arbitrary mutable checkout bytes is claimed. Landing requires its own fresh check.

The team commands coordinate existing Work Units and copy review artifacts. They
do not own a second progress registry, merge code, or launch untracked providers.
The serial first slice uses the ordinary Codex and capacity interfaces. Supervised
input, uncertain operations, and explicit cleanup retain the Gate D rules.
