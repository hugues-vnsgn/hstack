# Issue 36: native payload protection evidence

This receipt covers the bound configuration helper, disposable installed-consumer
startup and native write probes. It does not claim a full autopilot queue or mobile
execution. The [approved brief](https://github.com/hugues-vnsgn/huguesStack/issues/36#issuecomment-6184377164)
defines the boundary and acceptance criteria. The
[repeatable regression](../tests/payload-boundary.md) documents commands and limits.

## Before

On macOS 27.0.1 with Codex CLI 0.162.1, a disposable bound plugin nested inside a
writable consumer remained writable under the native `:workspace` sandbox.
A Python child changed `adapters/host.md`, exiting 0. The later guarded read
exited 2 with `installed workflow bytes/mode drift`. Detection followed the write.
The separate `red-baseline` receipt retains that command and result.

The first new installed-interface test also failed because `payload-policy` did
not exist. After implementation, the installed CLI generated a Claude JSON
fragment and a Codex TOML fragment, and held unsafe write scopes and unbounded or
missing Codex parents. The denial-evidence tests first failed without their
parser, then passed with paired native-event checks.
Review added a failing printed-denial reproduction; the tightened parser rejects
that fake while retaining the actual native failures. An ordinary editor error
without a structured permission denial also supplies no proof.

## Codex native observation

Tested Codex CLI 0.162.1 on macOS 27.0.1 (arm64), with invocation-only
`huguesstack-program` extending `:workspace`, approval policy `never`, user
configuration/rules ignored, and an installed plugin nested in the writable
consumer. The binding covers a Git-free installed copy.

- The coordinator and fresh delegated worker read the installed autopilot and
  protection reference through the bound helper.
- Each attempted a native patch to the canonical payload and received
  `patch rejected: writing outside of the project; rejected by user approval settings`.
- The coordinator's native alias-path patch failed with `Failed to write file`;
  that generic error is retained separately from the explicit canonical denial.
- Each ran the Python child probe. Append, creation, rename, deletion, chmod,
  symlink-alias writes and atomic replacement all raised `PermissionError`.
- Native positive-control writes succeeded for both coordinator and worker.
- The outer filesystem oracle found unchanged bytes, modes and inventory, and
  the later binding-guarded read succeeded. Root and worker turn contexts record
  the exact payload as read-only, with approval policy `never`.

An initial native run reported a hold for broader untested writer coverage.
The final bounded rerun completed the tested native patch and shell probes with
separate required coordinator/worker shell receipts and unchanged policy, binding
and probe inputs. Neither result establishes coverage of other writers.

## Claude observation

Claude Code 2.1.296 on macOS 27.0.1 (arm64) first stopped before tools with
`authentication_failed` / `Not logged in`. After the owner signed in, the bounded
native regression used the generated invocation policy, no user/project settings,
hooks disabled and no MCP servers. The native inventory contained Task, Bash,
Edit, Read and Write.

- The coordinator read the installed startup and protection reference. Native
  Write and Edit to the canonical payload were denied; an alias Edit was also
  denied. All three errored tool results correlate with the host's structured
  `permission_denials` entries.
- A fresh native general-purpose worker inherited the boundary. Its Edit was
  denied and correlated with its own native tool ID. The root waited for it.
- Coordinator and worker each ran their exact labeled Python child probe once;
  all seven operations raised `PermissionError`. Their native positive-control
  writes succeeded and payload reads remained available.
- The first authenticated run exposed a parser error on a string-valued system
  notice. A regression case now covers that event shape without loosening denial
  matching. The fresh final rerun passed the outer checks: separate shell
  receipts, unchanged policy/binding/probe inputs, unchanged payload bytes/modes/
  inventory and successful guarded rereads.

The print sessions could not open interactive `/permissions` or `/sandbox`, and
the displayed deny list was truncated. This proves the configured boundary for
the tested writers through observed native denials and controls; it is not a
complete interactive effective-settings inspection. The program's policy review
and broader writer-coverage prerequisites remain in force.

## Receipt locations and gaps

Private raw receipts are retained on the authorized Mac in the external
`huguesstack-issue36-*20261015*` evidence directories: baseline results, policy
fragments, bindings, platform/version records, commands, native JSONL streams,
Codex root/worker rollouts, shell results and before/after filesystem inventories.
They contain local paths and host context and are not published as plugin assets.

The regression covers bounded startup and probes. Complete autopilot lifecycle,
Desktop, other operating systems, MCP/REPL/external executors, remote execution,
mobile builds/devices and forge publication remain unobserved. Such uncovered
writers hold the program until verified or removed; they are not inferred safe.
