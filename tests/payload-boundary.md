# Native read-only payload regression

Run on an authorized Mac with Python 3.11+, authenticated native CLIs and supported
host sandboxing. Each command requires a new external output directory:

```sh
python3 scripts/check_payload_boundary.py --host codex --output /absolute/new/codex-evidence
python3 scripts/check_payload_boundary.py --host claude --output /absolute/new/claude-evidence
```

Use `--plugin /path/to/plugin` for another candidate. `--host codex --shell-only`
checks the sandbox engine without a model session; it does not prove file tools
or delegation. No command configures credentials, installs dependencies or edits
persistent permissions. Existing output directories are refused. Host sessions
use their existing authentication; Claude uses temporary invocation settings and
no MCP, and Codex ignores user configuration and exec-policy rules. Review the
recorded command before reproducing in a different environment.

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
