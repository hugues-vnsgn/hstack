## Native workers and role models

Translate Cursor Task to the current host's native agent tool. Each new work
round gets a fresh worker. Preserve the core's narrow resume exceptions and the
scoped-worker direct implementation exception; do not recursively delegate the
same assignment. Supply absolute paths
to the public mode, plugin skills directory and the host adapter and applicable mobile adapter,
the exact base/head, writable scope, success predicate and evidence destination.
Carry the loaded mode's absolute path into every fresh worker, including
general-purpose helpers; see [workflow tools](host-workflow-tools.md).
Full-mode workers load the mode per [host.md](host.md) before work. On Codex, select its enabled
catalog entry and read the complete SKILL.md yourself. Read each applicable
principle's SKILL.md in full as the scoped bundled reference below.
If the host cannot preserve required context isolation or parallelism, mark
that phase blocked.

**`hugues-agent` by host.** Claude Code registers it as `hstack:hugues-agent`, the
`subagent_type` to pass. Codex has no registered name observed here: the fresh worker
takes the role instructions of `agents/hugues-agent.md`.

For routed research/review calls, preserve `generalPurpose` and the workflow's
own prompt, readonly/agent-mode requirement, model, cardinality and handoff order.
Do not replace these workers with `hugues-agent`.
Cursor's `generalPurpose` maps to Claude Code's native `general-purpose` agent;
Codex uses a fresh native worker with that role's prompt.
Each owning skill names its complete worker prompts alongside its workflow.
Read the selected role's ordinary prompt reference, fill its named placeholders,
and preserve the owning workflow's order, cardinality and context isolation.
For simple how, omit explorer findings exactly as directed. Why retains its
category playbooks; reflect synthesis receives all three full outputs. Architect
passes its runner brief through arena. Read arena's SKILL.md in full as the
scoped bundled reference; never substitute a consumer or external fallback for
it. Inline briefs remain with their owner.
General-purpose native workers receive absolute source,
adapter and fixture paths, scope and success predicate, without a mode persona.
The mobile regression worker is a general-purpose native worker without a mode persona.
Its reading list is limited by [mobile workflows](mobile-workflows.md).
A worker spawned with the coordinator's turns, `fork_turns: "all"` or the equivalent,
is not fresh for either the regression or production role.
Agent mode preserves available tool access; it never grants permission to write
or query external sources. Missing authorized tools remain explicit coverage gaps.

The no-comments Task role `Comment Sicko` uses the registered
`hugues-comment-sicko` agent in Claude Code. Codex supplies that canonical specialized role through its supported fresh-worker mechanism before work. Do not substitute a generic worker without those rules. Preserve its exact
comment exceptions, scope fence, MUST KILL proof and no application-code edits;
the no-comments coordinator retains rejection, one rerun and failure rules.

The pinned per-role defaults remain defaults. A panel launches one worker per
configured entry, including each auto or inherit-parent alias. List length sets
cardinality. Aliases omit model overrides; they are explicit configuration,
never an implicit replacement for every default. Report same-model process
independence separately from family diversity.

Pass a role value's effort token through the native tool's effort setting. Where
the tool has none, the worker runs at the host's effort and the report says so.
A role value may join alternatives with ` or `: use the first one the native tool
accepts, else `inherit-parent` at the first alternative's effort, and name which ran
in the Workers line.
Report deliberate effort lowering too, with its reason.

Enumerate models actually exposed by the native tool. Preserve each core skill's
fallback sequence on rejected slugs, using only confirmed capabilities; record
the requested and actual family/model/effort. If a seat needs a family the host cannot
supply, mark the seat blocked and ask for an explicit configuration choice. Never invent
an available model or label a blocked seat completed. Do not update or publish a
default-fix PR without publication authority.

`setup-hstack` uses the pinned detect → load → budget/map/confirm → validate
→ write → confirm → optional verification sequence. Translate the Cursor global
rule path to project-local `.hstack/models.md`. Read it before all role
selection; deleting a role restores its pinned default. Write only after the
skill's confirmation and current filesystem authority. Keep every role and panel,
the four budget choices and availability validation. This file is guidance;
restoring the plugin does not execute setup or change any user's configuration.

For Bun helper setup, read [helper setup](host-helper-setup.md) in full.

## Subagent fields and models

If a Cursor-only field has no row, drop it and say so. Never drop `subagent_type`, `model`, `effort`, `run_in_background` or `isolation`, and never pass a field or value the tool schema rejects.

### Subagent fields

| Cursor | Claude Code | Codex |
|---|---|---|
| `readonly: true` | `subagent_type: "general-purpose"`, or `"Explore"` when the brief's job is to locate or search code, as a `how` explorer's is. The brief says "do not edit files"; then run `git status` in the worker's checkout. | unobserved |
| `readonly: false` | `subagent_type: "general-purpose"` | unobserved |
| `environment: "cloud"` | `isolation: "worktree"`, only where the core permits local execution. If the repo's AGENTS.md sets a worktree location, use it and omit `isolation`. The brief names the branch. | unobserved |
| `environment: "local"` | Omit: the Agent tool has no such field. | unobserved |
| `cloud_base_branch: <b>` | The brief names the checkout `<b>`. | unobserved |
| `run_in_background: true` | Pass it. | unobserved |
| `resume` | A new agent, the earlier result's text pasted into its brief; `SendMessage` in the cases `hugues-mode/SKILL.md` allows. | Same; its message tool is unobserved. |
| `file_attachments` | The brief lists the paths. | Same. |

### Models

| Cursor | Claude Code | Codex |
|---|---|---|
| `claude-<family>-<version>-<effort>[-fast]`, such as `claude-opus-5-5-xhigh` | `model: "opus"` and `effort: "xhigh"`. So does a role value `claude-opus-5-5 xhigh`. Drop `-fast`. | unobserved |
| A `grok-*`, `gpt-*`, or other non-Claude slug | Not accepted: the ` or ` rule above applies, and the Workers line names the model that ran. | unobserved |

## Model defaults and role labels

**Defaults for every agent-tool call.** `run_in_background: true`, agent mode, file pointers instead of inlined context, and an explicit model and effort per role. The defaults are `inherit-parent xhigh` for code and `inherit-parent max` for prose and judgment, and `/setup-hstack` configures them.

Code delegates tier by difficulty. The hardest changes (cross-cutting design, gnarly concurrency, subtle algorithms) go to your strongest judgment model (default `inherit-parent max`), whether the task needs judgment on vague intent or is a precisely specified sequence of steps to execute to the letter. Trivial mechanical edits go to your fast code model.

Per-role lines in `.hstack/models.md`, written by `/setup-hstack`, override these defaults and the model choices in the routed skills (`how`, `why`, `arena`, `swarm`, `architect`, `interrogate`, `reflect`). A role with no line keeps its default; `inherit-parent` runs on the parent chat model (omit the agent tool's `model`). If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it.

**Match the model to the job.** Before each spawn, start from the role's line or default and pick the reasoning level and speed the job needs. The `/setup-hstack` budget sets each role's starting level, `xhigh` for code and `max` for prose and judgment by default. Raise it one step, up to max, for the hardest or subtlest work. Lower it one step for judgment and two or more steps for routine work. Use fast mode only when the job is urgent, meaning CI or trunk is red or a person is blocked on the result right now. Otherwise use standard speed. Fast mode is a speed option on the native agent tool; Claude Code's has none and Codex's is unobserved, so the worker runs at standard speed and the report says so. Verification is the exception and stays on the `swarm workers` model and speed (`inherit-parent xhigh` by default). Change only the effort level and the speed, and keep the family the role names, so a diverse panel stays diverse. If the family has no model at that level and speed, use its nearest one the native agent tool exposes. A role on `auto` or `inherit-parent` stays on the parent model. If the native agent tool rejects the adjusted value, do not try another adjusted value. Use the role's line or default and say so.

**Role labels.** `setup-hstack` writes these labels and the router's playbooks read them. A code playbook's configured model comes from its line: `feature, refactoring`, `bug-fix`, `perf-issue` or `hillclimb`. The hardest changes read `hardest tasks`. Prose and judgment read `judgment and prose`.
