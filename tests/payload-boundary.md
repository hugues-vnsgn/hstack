# Native read-only payload regression

Run on an authorized Mac with Python 3.11+, authenticated native CLIs and supported
host sandboxing. Each command requires a new external output directory:

```sh
python3 scripts/check_payload_boundary.py --host codex --prepared-cache /absolute/prepared/node_modules --output /absolute/new/codex-evidence
python3 scripts/check_payload_boundary.py --host claude --prepared-cache /absolute/prepared/node_modules --output /absolute/new/claude-evidence
```

Use `--plugin /path/to/plugin` for another candidate. `--host codex --shell-only`
checks the sandbox engine without a model session; it does not prove file tools
or delegation. No command configures credentials, installs dependencies or edits
persistent permissions. Existing output directories are refused. Host sessions
use their existing authentication; Claude uses temporary invocation settings and
no MCP, and Codex ignores user configuration and exec-policy rules. Review the
recorded command before reproducing in a different environment.

The default `prepared` scenario requires the pinned Bun dependencies and matching
install key, either in that plugin copy or supplied with `--prepared-cache`.
Prepare them separately with installation authority in a disposable copy before
running this check. The runner copies the cache before binding and protection;
it never installs. Each actor's shell probe runs bound `helper-ready`, then prepared
`watch-pr --help` and `orch --help`, retaining their outputs before attempting writes.
The existing `*-helper-help.txt` receipts retain watch-pr output; `*-orch-help.txt`
records orch output. Both are required for each actor. Codex patch probes run as
separate literal tool calls so each native failure has an unambiguous request.
The same actor then runs `orch init` and `orch status` against its own
consumer-local store. The `*-orch-init.json` and `*-orch-status.json` receipts
record successful commands and the empty store state. This exercises store
creation, locking and status writes under protection.

Repeat on each host with `--scenario missing`, `--scenario stale` and
`--scenario uncovered`, each using a new output directory. The first two alter
only the disposable cache before binding and require the native host to run the
read-only prerequisite check, record a startup hold and stop before bootstrap,
application work or delegation. The last supplies an unresolved external-writer
coverage prerequisite and requires the same startup hold. These bounded startup
smokes exercise the playbook gate; they do not attest to arbitrary external tools.
An attempted watch-pr, orch, install or bootstrap command rejects the hold even
when the command fails. The runner CLI tests cover this with transcript fixtures
for both hosts; those fixtures establish parser behavior only.

The check copies the installed plugin inside a writable consumer with spaces in
its path, creates a symlink alias, binds it and prints its native policy. It reads
the installed autopilot startup and protection reference, then runs authorized
negative probes. A Python child process attempts append, creation, rename,
deletion, chmod, alias writes and atomic replacement; each must raise
`PermissionError`. Native file tools also attempt payload edits. One fresh native
worker repeats the native edit and shell probes under the inherited policy.
Consumer writes by the coordinator and worker are positive controls.

The outer check compares every payload path, file hash and mode, checks the shell
results and positive controls, and reruns a binding-guarded read. Full runs require
paired native permission-error results for the coordinator and worker; a model
refusal, final-message claim or missing result is insufficient. Codex also
retains its own root and descendant rollout receipts and checks their effective
payload-read policy and approval mode. The Claude check requires native Write,
Edit, alias and child-worker denial events. Unsupported transcript formats fail
closed and require a reviewed parser update; they do not establish compatibility.

Logs remain outside the source repository, including failed runs. Inspect them
for unexpected tool access, policy changes, retries and any stated holds. A green
filesystem check covers only these probes in that environment. It does not mean
every enabled writer is covered, that a full autopilot program ran, or that the
host's other execution tools are isolated. Keep broader writer gaps as holds.
Desktop, other operating systems, MCP and mobile execution require separate proof.

`identity.json` records the tested checkout commit, plugin tree, source-dirty flag,
runner hash and exact evidence directory. A dirty flag or an alternate `--plugin`
requires separate identity reconciliation; the checkout tree alone cannot identify
those bytes. `SHA256.json` binds the raw logs, commands, binding, policy, snapshots
and control artifacts. Report the manifest hash with the exact durable directory.
Shell labels alone are insufficient: Claude pairs Bash requests and results with
the same worker parent ID; Codex requires successful native CommandExecution
records in each actor's own rollout after its forked history.

## Mobile compatibility and auto-mode limits

The runner first rejects immutable/append-only flags on the disposable payload
and proves an unprotected append and creation succeed, restoring the copy before
binding. `unprotected-control.json` retains that positive control. It never clears
file flags or writes to the source installation.

Use `--prepare-only` to inspect the generated policy and copied fixture without
starting a native host. Preparation is not enforcement evidence. For a Claude
macOS mobile check, add `--macos-mobile`, the selected `--java-home`, repeated
`--allow-write` cache/log directories and `--allow-domain` hosts. Supply a small
fixture with `--mobile-fixture` and repeat `--mobile-command` for each required
gate, such as:

```sh
--mobile-command './gradlew --offline --no-daemon :composeApp:compileDebugKotlinAndroid :composeApp:compileKotlinIosSimulatorArm64'
--mobile-command 'xcrun simctl list devices booted --json'
--mobile-command 'xcrun simctl spawn <selected-booted-device-udid> launchctl getenv HOME'
--mobile-command 'adb devices -l'
--mobile-command 'gh api repos/hugues-vnsgn/hstack --jq .full_name'
```

These are arguments to the runner, not standalone shell commands. It copies the
fixture without Git metadata, build outputs or `.gradle`; the source remains
untouched. Each actor runs the exact selected argv without a shell from the copy
before its denial probes. Logs and exit codes for every requested gate are kept
in that actor's mobile receipts. The copied fixture must have its dependencies
prepared separately; `--offline` cannot fetch missing dependencies. Choose gates
for the actual fixture and require an actual booted-device operation. `simctl list`
can exit zero with unavailable devices; inspect availability or use `getenv` on
the selected booted device. Neither a compile nor these queries proves a device UI test.
Already-running Gradle/adb/Simulator services have their own effects and protection
gaps; these commands alone do not qualify them as isolated writers.

Claude defaults to `--permission-mode dontAsk`, matching the original regression.
Choose `--permission-mode auto` only for an independently authorized diagnostic
run. Its editor receipts do not reliably distinguish classifier refusals from
deny-rule enforcement, so the runner cannot qualify native protection in that
mode even if the other gates pass. Only explicit `dontAsk` qualifies Claude editor
evidence; an omitted or unknown mode also fails closed in the receipt parser.
A classifier refusal, missing worker result or failed mobile gate fails the check;
retain the logs and hold that coverage. The runner never switches modes or retries
outside protection. Full autopilot, forge mutations, MCP isolation and live-root
readiness remain separate verification requirements.

[Issue 53 observed mobile results and limits](../docs/mobile-payload-proof.md) bind
the combined native checks to their actual recipe and source hashes.
