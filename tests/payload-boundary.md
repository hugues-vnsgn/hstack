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
it never installs. Each actor's shell probe runs bound `helper-ready` and the
prepared `watch-pr --help`, retaining their outputs, before attempting writes.

Repeat on each host with `--scenario missing`, `--scenario stale` and
`--scenario uncovered`, each using a new output directory. The first two alter
only the disposable cache before binding and require the native host to run the
read-only prerequisite check, record a startup hold and stop before bootstrap,
application work or delegation. The last supplies an unresolved external-writer
coverage prerequisite and requires the same startup hold. These bounded startup
smokes exercise the playbook gate; they do not attest to arbitrary external tools.

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
