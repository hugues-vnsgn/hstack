# Read-only installed payload

Before either autopilot starts write-capable work, establish native host protection
for the canonical `plugin_root` in the approved binding. Keep the payload readable
and the authorized consumer/evidence directories writable. Hash checks detect
drift; host permissions must reject the write itself.

## Prepare the boundary

Complete any separately authorized dependency bootstrap before binding and
protecting the installation. Before selecting a bundled Bun helper, run the bound
read-only prerequisite check:

```sh
python3 "<plugin>/adapters/host_tools.py" helper-ready --binding "<program>/plugin-binding.json"
```

Missing Bun, missing dependencies or a stale package/lock install key holds that
operation **before** running the helper or its bootstrap. Obtain separate owner
authorization for preparation, then bind and protect the prepared installation.
Prepared helpers remain available under protection. Generated caches do not get
a writable exception in the payload; `prepared` reports prerequisites only.

1. Resolve the loaded installation and create its binding as
   [host tools](host-tools.md) directs. Record its manifest digest, plugin version
   from `.claude-plugin/plugin.json`, host version, platform and canonical root in
   the program evidence. If it is a Git installation, record the containing
   repository's `git rev-parse HEAD` as the installed checkout commit, separately
   from the upstream pin. Check that Git actually tracks this payload; a cache
   nested in a consumer Git repository is not a Git installation. Git-free caches
   use the version and bound digest. Dirt outside the payload is not a blocker.
2. Inventory every enabled writer: native file tools, shell/child processes,
   delegated workers, MCP, REPL, external executors and remote/computer-use tools.
   Include host hooks and background commands, plugin monitors, language servers,
   status-line commands and credential helpers. Claude runs several of these
   outside its Bash sandbox. Preserve required Git and safety hooks; verify their
   independent boundary or hold the program rather than disabling them to proceed.
   For each, establish effective enforcement on this root or remove that
   capability from this program. An unverified writer holds dependent execution.
   A tool annotation or an agent's promise is not enforcement.
3. Print an owner-reviewable fragment through the bound installed helper:

   ```sh
   python3 "<plugin>/adapters/host_tools.py" payload-policy --binding "<program>/plugin-binding.json" --host claude --consumer "<consumer>" --evidence "<evidence>"
   python3 "<plugin>/adapters/host_tools.py" payload-policy --binding "<program>/plugin-binding.json" --host codex --consumer "<consumer>" --evidence "<evidence>" --parent "<active-permission-profile>"
   ```

   Use the command for the actual host. The helper prints configuration and
   applies nothing; success is not a protection verdict. Use existing operator
   authorization for the shown scope. Show and obtain authorization for any new
   settings change. Keep persistent profiles and installations unchanged unless
   their changes are explicitly authorized. Consumer/evidence paths must name
   already-authorized directories, never a subtree of the protected payload.
4. Merge only the reviewed additions with the current effective settings. Keep
   unrelated rules, stricter restrictions, native invocation controls, existing
   topology/publication permissions and network policy. Resolve conflicting or
   unsupported settings with the owner before work; do not replace their policy
   with a generated fragment. Record the effective result and writer coverage.

## Claude Code

The JSON fragment combines an absolute `Edit` deny for all built-in file editors
with sandbox filesystem `denyWrite` for the canonical root. It requires sandbox
availability, filesystem isolation and no unsandboxed retries. Absolute file-tool
rules use `//path`; sandbox paths use `/path`. Keep existing deny/ask entries when
merging. `Write(path)` is not a supported replacement for `Edit(path)`.

Pass the reviewed merged file with native invocation settings:

```sh
claude --settings /absolute/owner-approved/program-settings.json
```

Inspect `/permissions` and `/sandbox` in that invocation. Require sandbox enabled,
`failIfUnavailable: true`, `allowUnsandboxedCommands: false`, filesystem isolation
enabled and the canonical payload deny. Check **all effective settings sources**
for excluded commands, weaker sandbox modes, unrestricted sockets, Apple Events
and other external writers. Empty arrays in a fragment do not clear merged
exceptions. Remove uncovered capabilities under the existing authorization or
hold. Preserve invocation controls from [host.md](host.md). Preserve the parent's
boundary in each native Agent call; a worker must not request bypass permissions.

## Codex

The TOML fragment creates `hstack-program`, extending the active bounded
permission profile and carving out the exact payload as `read` inside authorized
writable directories. Name the actual parent; use `:workspace` only when that is
the approved baseline. Retain its narrower restrictions. An existing profile
with this generated name needs an owner-reviewed merge, including any narrower
write grants beneath the payload. Permission profiles and legacy sandbox settings
must not be mixed for this invocation.

Use the reviewed layer through Codex's supported named configuration profile
(`-p <name>`, loading `<active CODEX_HOME>/<name>.config.toml`) or equivalent native
`-c` overrides for `default_permissions` and `permissions.hstack-program`.
Show the exact launch configuration. Do not set unrestricted sandbox mode or
permit escalated retries. With approval policy `never`, a denial is returned to
the worker; otherwise preserve stricter existing approval requirements and hold
any escalation that would bypass this boundary. Verify native patch tools as
well as local commands. MCP, REPL, remote and external writers need their own
verified boundary or removal. Fresh native workers retain the effective profile;
verify it again when dispatch creates a different execution environment.

## Prove startup and preserve the boundary

Readiness belongs to the canonical root in this program's binding. Record the
binding digest, exact root, effective policy sources, writer inventory and native
results together. A protected disposable copy proves only its own configuration;
it cannot establish readiness for a different live root. For the bound live
installation, inspect effective native policy without modifying it and establish
that every enabled writer enforces that exact root. If this inspection or the
mapping from evidence to the bound root is unavailable, hold. Never probe a live
payload with a write merely to fill the gap.

Before application writes, inspect effective policy and retain native evidence
of a denied disposable payload edit, a successful payload read and an authorized
consumer/evidence write in the same execution environment. Use a disposable
installation for negative probes, never mutate the live installation to test it.
The maintainer's opt-in native regression is `scripts/check_payload_boundary.py`
in the source repository; it is not an installed consumer command. Its receipt
and limits are linked from the issue. Missing host support, a failed positive
control, unobserved writer coverage or missing worker inheritance holds work.
Record `payload-protection: held` with the uncovered capability and prerequisite;
start only after the evidence supports `payload-protection: ready` for the root
and every write-capable worker. Recheck on fresh dispatch, restart, tool/policy
changes and each audit tick. Keep policy and binding evidence available to workers.

On a denied plugin edit, retain the exact attempted action and native denial and
confirm the payload is unchanged. Hold dependent work and report the defect to
the plugin tracker under existing publication authority, or retain an issue draft
for the owner. Plugin maintenance belongs to a separate owner-authorized task.
Keep the boundary: no alternate writer, unsandboxed retry, policy weakening,
reseal/rebind, plugin-maintenance worktree or cross-repository PR inside the
consumer program. Bound drift or relocation also holds rereads until explicit
owner reconciliation. Neither a valid binding nor a configuration fragment proves
host enforcement, and neither grants publication or landing authority.

## References

- [Issue 36 and its current approved brief](https://github.com/hugues-vnsgn/hstack/issues/36#issuecomment-6184377164)
- [Claude file permissions](https://code.claude.com/docs/en/permissions)
- [Claude sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Codex permission profiles](https://learn.chatgpt.com/docs/permissions)
