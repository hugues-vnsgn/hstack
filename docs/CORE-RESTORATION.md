# Source and workflow contracts

The 0.2.0 pinned-core restoration remains a historical release. Version 0.3.0
consolidates its full skill bodies into native entries; see
[native consolidation](NATIVE-CONSOLIDATION.md) for layout, migration and limits.

The upstream archive retains 200 files from pstack 0.15.32 at
`e73df471cd4bd918367e99f3dd9c51bd53ddf5f0`. Git-object snapshots verify its
paths, modes, SHA-1, SHA-256 and sizes. The adapted runtime no longer claims
byte equality. Public native names, workflow phase order, role cardinality,
feature arena, fallback, whole-map maintenance and mobile applicability remain
checked separately from source identity.

The complete installed inventory and permission modes are bound. Skill reads
cannot be disguised as guarded resource reads: the helper refuses every
SKILL.md, and an agent reads a bundled user-only skill's file with the host's
own file-read tool instead.
Missing/empty/malformed
activity, unknown PR state and unsupported inputs retain conservative exit-2
holds; the active/pinned-chat gate is separate and no helper deletes anything.
The bootstrap executes verified source buffers, not bytecode caches.

The current candidate collects 542 tests, including one driver for 50 historical 0.2.0 cases.
Current and historical suite totals are maintained in [test accounting](TEST-COVERAGE.md).
The 0.1.0 archive and its tests are unchanged. The 50 old restoration-contract
cases also run against a hash-bound 0.2.0 archive and are historical only.
Current mutation tests exercise native inventory, names, modes, source mapping,
workflow gates and invocation boundaries. Installed adapter tests exercise real
Python/Node helpers in disposable consumers with synthetic activity only.

The prior 52 Bun tests and strict watch-pr TypeScript result at `37eb703` remain
historical evidence. On October 20, 2026, `bun test ./watch-pr` passed all 65
watch-pr cases with Bun 1.3.14 for the required-context change. The nine new
cases cover argument validation, missing contexts, prefix matching, and polling
in single, stack, and queued modes. This run is separate from the Python suite.
No installation, native host, device, cloud, forge or loop execution is implied.
Source equality and passing static tests do not establish runtime parity.
