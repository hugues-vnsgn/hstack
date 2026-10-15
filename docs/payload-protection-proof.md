# Issue 36: native payload protection evidence

The [current approved brief](https://github.com/hugues-vnsgn/huguesStack/issues/36#issuecomment-6184377164)
defines the boundary. These runs cover bounded installed-consumer startup,
prepared helpers and write probes. Full autopilot lifecycle and mobile execution
remain unobserved. [Repeat the regression](../tests/payload-boundary.md).

## Tested identity

- Tested commit: `ebf31800b02ed5a5a75053cff70adf25a18f9e70`.
- Authored plugin Git tree: `e637e82bef481c62cdb7f29c7a262d2648a6b958`.
- Runner SHA256: `aba0bc8af54ec67093e808d760d4510e4f2302db1681be1cd55d17a3af9ad2cc`.
- All eight `identity.json` files record that commit/tree, the source plugin path
  and `source_dirty: false`. They used the default checkout plugin, copied into
  a Git-free installation nested inside a writable consumer with spaces.
- Codex CLI 0.162.1, Claude Code 2.1.300 (`dontAsk`), Bun 1.3.14, Python 3.14.7,
  macOS 27.0.1 arm64. Dependencies were prepared separately in a disposable copy
  before binding and protection; no live installation or persistent policy changed.

The receipt-only follow-up at `a8b8299` changed no plugin or runner bytes. A separate protected
copy does not establish readiness for another bound live root.

## Red and green

On `0050123`, an actual patch context-mismatch error quoting the permission-denial
sentence was misclassified by the evidence parser. `denial-red.log` records that
failing assertion. The complete native-error matcher now rejects it while retaining
paired real denials. The new shell-evidence test rejects absent results, commands
for another probe and mismatched Claude worker parents. Codex proof comes from
successful native command records in each actor's own rollout, excluding forked
parent history. Labels alone establish no actor identity.

`policy-before-python39.log` records the new suite's `tomllib` import failure on
Python 3.9.6. All eight payload-policy cases now pass there and on Python 3.14.7.
Missing, stale and absent-runtime prerequisite cases first failed without the
bound command, then passed with specific diagnostics and unchanged cache bytes.

## Native results

Both prepared runs passed these checks:

- Coordinators read the installed startup/protection guidance. Root and fresh
  native worker each read the payload, ran bound `helper-ready` and prepared
  `watch-pr --help` under protection.
- Each actor attempted native canonical payload edits and received paired native
  permission denials. Claude denied root Write, Edit and alias Edit, plus worker
  Edit, correlated with the host's structured permission-denial IDs. Codex denied
  the canonical root/worker patches. Its generic alias failure supplies no
  independent permission-cause claim.
- Each actor's exact Python child command completed all seven PermissionError
  probes: append, create, rename, delete, chmod, symlink alias and atomic replace.
- Native root/worker consumer and evidence writes succeeded. The root also wrote
  a consumer-local corrective artifact and generated verification skill artifact
  outside the payload; no generated skill invocation is claimed.
- Payload inventory, bytes and modes, including the prepared cache, stayed equal.
  Binding, policy and probe script stayed unchanged. Guarded rereads succeeded.

Each host also passed missing-cache, stale-key and uncovered-writer startup
smokes. Missing/stale cases retained the actual failed read-only helper command;
no helper/bootstrap, app marker or worker dispatch occurred. The uncovered case
held for an external executor without a verified boundary. These are bounded
playbook-gate observations with explicit fixture prerequisites.

## Durable receipts

Private raw evidence lives at
`~/huguesstack-evidence/2026-10-15-pr47-review-fix/` on the authorized Mac.
Each exact subdirectory below retains commands, native logs, binding, policy,
platform/identity records, before/after snapshots and control artifacts. Codex
runs also retain their own coordinator/worker rollouts. Each `SHA256.json` binds
those files; its digest is listed here. All manifest entries were rehashed and
matched. Raw host context is retained privately, outside plugin assets.

| Subdirectory | Result | SHA256 of `SHA256.json` |
|---|---|---|
| `codex-prepared` | probes passed | `434b94712b62db0d81ada0e38d14fd37a3d2b9ff74627c054cbd18960236edf9` |
| `codex-missing` | startup held | `76fa3dd78f870b15c4e4db1613522d0090e8028121a2997117fe72e1812e88c4` |
| `codex-stale` | startup held | `84bf05862e9398e4c0993d67f5df2364be6af23c14fd1bcae44a3c5af402ec86` |
| `codex-uncovered` | startup held | `f4dc9af27469ddfe8d8e5a05227ea267120d4d5457a123c28ea17473b0b33f9e` |
| `claude-prepared` | probes passed | `57fdc12dd7d20184fc132989faf8ae4c57b509d47467b542ceef15c18a080962` |
| `claude-missing` | startup held | `6e72e345bbd1e3511d28bd7e57c1263488074c0341ba2c05d80c62e7dee510ad` |
| `claude-stale` | startup held | `8b4427f24be662601f8dc74fc90db108bad103a9421f85aa2bc9469966783e30` |
| `claude-uncovered` | startup held | `86905f0f3d26a521d310f9629f9034c273e2901d62e95ea737c12eb43dc88ac3` |

## Source checks and limits

All 439 top-level cases pass on Python 3.14.7, including the separate 50-case
frozen restoration execution. Every README maintenance check passes. The full
Python 3.9.6 run has 438 passing top-level cases and one failing frozen 0.2.0
driver: its unchanged nested loader needs newer tar-filter behavior and extraction
modes. The eight current payload-policy cases pass. This is a historical
compatibility gap, not a Python 3.9 full-suite pass. See [test accounting](TEST-COVERAGE.md).

Standards and Spec reviews found no actionable issue in the revision. An ambient
Bun dependency in the test fixture was replaced with a deterministic fake runtime.

Claude print sessions did not perform interactive `/permissions` or `/sandbox`
inspection. Hooks were disabled only for fixture isolation; required Git/safety
hooks in consumer programs still need verified coverage and must not be disabled
to proceed. Complete effective-settings inspection, other permission modes,
Desktop, other operating systems, MCP/REPL/external executors, remote execution,
mobile builds/devices, full queue execution and forge publication remain gaps.
Uncovered writers hold execution. Separate owner-authorized plugin maintenance
keeps its own task and boundary; these consumer probes grant no maintenance scope.

[Earlier observations at 0050123](https://github.com/hugues-vnsgn/huguesStack/blob/0050123e6b06b213fd60b17b418ca4c56769f0f1/docs/payload-protection-proof.md)
remain historical evidence for their original inputs.

## Both-helper startup follow-up

The earlier prepared probe ran watch-pr only. A baseline Codex sandbox run at
`f68236a` passed the existing checks without an orch receipt; requiring that
receipt failed. The baseline receipts originally remained in `/tmp`; the
[PR 54 retrospective](../plans/reports/261015-1645-pr54-retro.md) records their durable
copy, the recovered original assertion and a later repetition. The updated
probe runs both original helpers with `--help` and
requires their outputs for each actor, preserving the existing watch-pr filename.
Codex patch probes use independent literal calls for native denial correlation.

Fresh prepared runs passed on Codex CLI 0.162.1 and Claude Code 2.1.300 on macOS
27.0.1 arm64. Each coordinator and fresh worker ran both helpers under protection,
received native payload-edit and seven child-process write denials, and wrote
consumer/evidence controls. Payload bytes, modes and inventory stayed unchanged.
The original helper bodies, installed policy and workflow contracts were unchanged.

These runs used plugin tree `e637e82bef481c62cdb7f29c7a262d2648a6b958`, shared by
`ebf3180` and `f68236a`, and the modified
runner SHA256 `5cfbe7bc74080aacf14670d06f1834619557aa8771b3162414a3efa1fe9d2967`.
Their identity records deliberately report `source_dirty: true` because the
runner was tested before commit; the recorded runner hash identifies those bytes.
All manifest entries were rehashed successfully. Private durable receipts live at
`~/huguesstack-evidence/2026-10-15-both-helper-startup-e44demak/`:

| Subdirectory | Result | SHA256 of `SHA256.json` |
|---|---|---|
| `codex` | both helpers and probes passed | `70882cda176ba9ca5c393b0a1468940db9f65969eb2b2bdf0f9198dd9007520f` |
| `claude` | both helpers and probes passed | `4f54ef632f6b105c22a4ef60f3563fbbe337a0e7539bbead96fa226567aab110` |

These are prepared-startup observations. Missing/stale/uncovered scenarios retain
their earlier evidence and were not rerun for this extension. The broader gaps
listed above remain gaps; help output proves startup only. These runs did not
exercise orch store writes, watcher or forge behavior. The retrospective records
the later store-write probes separately.
