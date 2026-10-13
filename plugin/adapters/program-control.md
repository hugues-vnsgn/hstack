# Program limits, checkpoints and pickup

For a new autopilot-full, autopilot-stack or orchestrate program, the controller
reads this guide before dispatch. Preserve [program proof](program-proof.md),
native invocation, phase order, required participants, configured model roles,
host permission decisions and publication authority. Scheduling defaults to one
PR owner and one complete arena/review group at a time. These owner-approved
limits override inherited unlimited parallel-owner scheduling, not required
parallelism inside an arena or review group.

## Establish the controller record

Keep the approved policy, event inputs and progress store in a permanent owner
control directory outside the plugin and outside worker-writable roots. Protect
this whole directory and the installed binding with the same actual write
enforcement as the approved proof records. Never let builders write their own
limits, completion list, dispatch receipts or checkpoints. Hold dependent work
when that enforcement is unavailable.

Use the installed `adapters/host_tools.py`, an absolute payload binding, and an
owner-held SHA256 of the approved policy. These commands check/save records;
they do not spawn a native worker, authorize a tool, authenticate an owner
message or prove the meaning of a receipt. The trusted controller checks actual
tool results before recording them. Every program spawn, including a helper's
request, must pass the controller gate. Where the host cannot route or restrict
unmediated helper dispatch, hold that dispatch and report the enforcement gap.

```sh
python3 <installed-plugin>/adapters/host_tools.py run-control \
  --binding <absolute-binding.json> --policy <absolute-policy.json> \
  --policy-sha256 <owner-held-sha256> --store <absolute-control-dir>/progress \
  --event <absolute-control-dir>/event.json
```

Policy schema 1 lists the approved work and complete required groups. Example:

```json
{
  "schema_version": 1,
  "program": "approved-program",
  "approval_reference": "actual-owner-plan-decision",
  "playbook": "autopilot-stack",
  "duration_seconds": null,
  "units": ["PR1"],
  "limits": {"owners": 1, "reviewers": 3, "helpers": 0, "depth": 3},
  "workers": [
    {"id":"owner1","unit":"PR1","role":"owner","parent":"coordinator","timebox_seconds":null},
    {"id":"R1","unit":"PR1","role":"reviewer","parent":"coordinator","timebox_seconds":null},
    {"id":"R2","unit":"PR1","role":"reviewer","parent":"coordinator","timebox_seconds":null},
    {"id":"R3","unit":"PR1","role":"reviewer","parent":"coordinator","timebox_seconds":null}
  ],
  "groups": [{"id":"review","members":["R1","R2","R3"]}]
}
```

Use the actual configured participant count, not this example's three. Declare
standalone helpers, required nested groups and nesting depth in the approved
plan; preserve the selected playbook's existing nesting constraints. Depth
counts the coordinator. Orchestrate requires its planned duration in seconds;
its existing approximately 70% planned-time spawn cutoff still applies.
Worker timeboxes preserve the brief's runtime bounds. No new universal time
limit, numerical token ceiling, 80% subscription cutoff, model downgrade or
automatic quota-warning pause is introduced.

## Reserve before dispatch; attach the observed identity

Write a fresh event ID for each action. Replaying identical events is safe;
reusing an ID for different content holds. The controller saves a reservation
before the actual native tool call and then attaches its observed identity. If
interrupted between these actions, an unknown reservation remains counted; a
fresh session must reconcile it before starting replacements.

Every event contains `id` and `op`, plus the fields below:

| Operation | Additional fields and behavior |
|---|---|
| `init` | Initialize once. Replaying the same event preserves state; a new initialization cannot reset an existing program. |
| `dispatch` | `worker`, unique `actor`, `parent`. Reserve a declared standalone worker within limits. |
| `dispatch-group` | `group`, unique `round`, `parent`. Reserve every configured member atomically as `<member>:<round>`; preserve required parallel dispatch. Never send a reduced member list. |
| `attach` | `actor`, `pid`, `native_id`, `reference`. For a local worker, use a genuinely isolated process-group leader PID; its birth identity is captured. For a native remote worker, use `pid:null` and the actual native ID. |
| `observe` | `actor`, `status` (`live`, `dead`, `unknown`), `reference`. Inspect native status; do not resume a worker merely to probe it. A claim cannot override live local processes. |
| `finish` | `actor`, `outcome` (`completed`, `interrupted`), `reference`. Account for actual effects and children; owned devices must already be restored/released. Unknown or live workers cannot be silently replaced. |
| `checkpoint` | `unit`, `status` (`pending`, `interrupted`, `completed`), `commit` or null, `proof_refs` (absolute file paths), `next_action`, `reference`. Save progress before long actions and after meaningful boundaries. Completion records are not proof verdicts. |
| `status` | Read current actors/groups, terminal counts and progress. Full worker history, event journals and raw usage stay on disk rather than entering every model turn. |
| `pickup` | Begin fresh-session reconciliation. Clear saved remote liveness claims to unknown; inspect actual status again. Preserve owner stops, completed progress and reservations. |
| `stop`, `continue` | `reference` to the actual owner's instruction. Only an explicit continuation clears an owner stop. |
| `approve-limits` | `previous_policy_sha256`, with a separately approved policy and its new owner-held digest. Adjust limits/duration only; workers, required groups and approved work stay fixed. Preserve all progress and reservations. |

Give workers small briefs containing their own scope, required reads, applicable
limits, parent/group identities and accessible proof references. Keep standing
orders intact. The controller records every actual helper dispatch; a worker
cannot authorize extra helpers itself. Counters and group limits hold missing
or oversized dispatches without turning omitted checks into success.

## Record usage without guessing subscription allowance

`usage` events contain `scope`, `covers`, `actors`, `counts`, `reference`. Scope
identifies one cumulative provider counter across resume. Covers lists the
actual underlying session/counter identities included; actors names registered
participants. Use either a whole-tree counter or disjoint child-session counters.
Overlapping coverage holds; never count a child twice. New independent sessions
use new scopes. Preserve monotonically increasing totals, including after crashes.

Counts contains `uncached_input_tokens`, `output_tokens`, `cache_read_tokens`,
`cache_write_tokens`, each a nonnegative integer or null. Normalize only from
documented provider fields: for Codex's inclusive input total, subtract its
reported cached input to obtain uncached input; do not subtract again from a
provider field already exclusive of cache. Missing channels remain null.
`usage-gap` takes `scope`, `covers`, `actors` and `reference` when final data is
missing. Resolve it only with complete cumulative counts for that same scope,
covering every missing counter and actor. An unrelated session leaves the gap
visible. Report
complete/partial/unknown recorded coverage separately from verified host delivery.
No count is an exact subscription allowance or monetary bill.

`allowance` takes `windows` (each with `id`, `used_percent`, `reset_at`), `warning`
or null, and `reference`. Use actual host captures; expired windows become unknown.
Show capture age/reference rather than claiming an old snapshot is current.
Log/report genuine warnings without adding an automatic pause. If the host
rejects usage, preserve the earlier checkpoint and bounded retry/pickup behavior.
Do not spend repeated model turns retrying a quota failure.

The native metadata route must be discovered in the actual host. Codex documents
quota reads and thread usage; Claude documents eligible statusline quota fields
and SDK whole-tree counters. None was observed flowing into this plugin here.
If unavailable, record unknown/partial coverage and use the approved limits.

## Wait in the runtime; restore before releasing a device

Prefer native completion notification. Otherwise use one blocking command:

```sh
python3 <installed-plugin>/adapters/host_tools.py run-wait \
  --binding <absolute-binding.json> --policy <absolute-policy.json> \
  --policy-sha256 <owner-held-sha256> --store <absolute-control-dir>/progress \
  --kind actor --target <actor-id> --timeout 30
```

`--kind device` waits for that program's recorded reservation to be released.
This does not establish global device availability or remove independent host
checks. Actor waiting also wakes on observed local process-group exit; its saved
status stays active until effects are reconciled with `finish`. Device reservations
stay held. Timeout exits 2 with `wait_satisfied:false`; wait through a host event
or another runtime wait, never a chain of model turns polling status. Without
either capability, save a durable handoff and report the blockage. Required
program audits remain in force.

Before altering test settings, `device-acquire` records `device`, `actor`,
`settings` (the observed baseline object), `reference`. The actor must be live.
On recovery inspect the worker and its device-using processes. The local check
tracks children remaining in its process group after the leader dies, plus
registered active descendants in separate groups. Register device-using processes
that escape the original group separately; unaccounted ownership holds release.
For native remote workers, inspect fresh host/process observations; unknown holds.

After processes stop, restore only recorded test settings and inspect the result.
Then `device-release` takes `device`, observed restored `settings`, `reference`
and `processes_reference`. Local live/unknown groups block release. Restored
settings must match the baseline, including value types. Receipt strings do not
prove these observations; the trusted controller must inspect their actual
tool captures. Never wipe app data or proof to clean up a device.

The progress-store kernel lock protects short writes, survives process death
without deleting a live lock, and is separate from device reservations. Atomic,
fsynced checkpoints include an integrity checksum; corruption holds for review,
not reinitialization. Checksums detect accidental corruption, not owner identity.

After pickup, reconcile actual source/commits, logs, children and pending effects.
Reuse completed work; recheck proof with `program-check` for the actual approved
build. A missing, stale or wrong-target receipt remains missing or blocked.
