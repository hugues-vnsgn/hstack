## Native workers and role models

Before your first dispatch, run `printenv ORCA_TERMINAL_HANDLE ORCA_PANE_KEY ORCA_TAB_ID`; if it prints a value, `ORCA_BOT_TOOLS_TOKEN` is set (test it with `[ -n "${ORCA_BOT_TOOLS_TOKEN-}" ]`, never print it), `t3-code` tools are listed or the agent is omp, read [Hosts](hosts/README.md).

Translate Cursor Task to the current host's native agent tool. Each new work
round gets a fresh worker. Preserve the core's narrow resume exceptions and the
scoped-worker direct implementation exception; do not recursively delegate the
same assignment. Supply absolute paths
to the public mode, plugin skills directory and the host adapter and applicable mobile adapter,
the exact base/head, writable scope, success predicate and evidence destination.
Carry the loaded mode's absolute path, derived from the current loaded skill, into every
fresh worker, including general-purpose helpers; see [workflow tools](host-workflow-tools.md).
The first line of every kickoff is `Read <path>/worker.md before anything else.`, with `<path>` the
absolute path of the loaded mode's folder, so the operator's rules in
[worker.md](../skills/hugues-mode/worker.md) reach the worker. Only the mobile regression worker
omits it, since its reading list is closed below. The kickoff also carries the mode path and, for
Swift or Kotlin source, the baseline paths the router names.
Full-mode workers load the mode per [host.md](host.md) before work. On Codex, select its enabled
catalog entry and read the complete SKILL.md yourself.
If the host cannot preserve required context isolation or parallelism, mark
that phase blocked.

**`hugues-agent` by host.** Claude Code registers it as `hstack:hugues-agent`, the
`subagent_type` to pass. Codex has no registered name observed here: the fresh worker
takes the role instructions of `agents/hugues-agent.md`. In Cursor, read [hosts/cursor.md](hosts/cursor.md) for the agent registration.

For routed research/review calls, preserve the workflow's
own prompt, readonly/agent-mode requirement, model, cardinality and handoff order.
Do not replace these workers with `hugues-agent`.
Codex uses a fresh native worker with the workflow's prompt.
Each owning skill names its complete worker prompts alongside its workflow.
Read the selected role's ordinary prompt reference, fill its named placeholders,
and preserve the owning workflow's order, cardinality and context isolation.
Architect sends a large or contested design through arena. Read arena's SKILL.md
in full as the scoped bundled reference; never substitute a consumer or external
fallback for it. Inline briefs remain with their owner.
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
setup-hstack's ` or ` rule picks first: the first alternative the native tool accepts,
else `inherit-parent` at the first alternative's effort. A skill's own fallback to its
default applies only if the tool then rejects the value that rule picked.
Report deliberate effort lowering too, with its reason.

Enumerate models actually exposed by the native tool, using only confirmed capabilities.
The Workers line records the requested and actual family/model/effort. A seat needs a
family only when its workflow requires one and no alternative on its line is accepted:
mark the seat blocked and ask for an explicit configuration choice. Never invent
an available model or label a blocked seat completed.

`setup-hstack` writes project-local `.hstack/models.md` in place of the Cursor global
rule, only after the skill's confirmation and current filesystem authority. Read it
before all role selection. This file is guidance; restoring the plugin does not
execute setup or change any user's configuration.

For Bun helper setup, read [helper setup](host-helper-setup.md) in full.

## Subagent fields and models

If a Cursor-only field has no row, drop it and say so. Never drop `subagent_type`, `model`, `effort`, `run_in_background` or `isolation`, and never pass a field or value the tool schema rejects.

### Subagent fields

| Cursor | Claude Code | Codex |
|---|---|---|
| `readonly: true` | `subagent_type: "general-purpose"`, or `"Explore"` when the brief's job is to locate or search code. The brief says "do not edit files"; then run `git status` in the worker's checkout. | unobserved |
| `readonly: false` | `subagent_type: "general-purpose"`, also for `generalPurpose` without `readonly`. | unobserved |
| `environment: "cloud"` | `isolation: "worktree"`, only where the core permits local execution. If the repo's AGENTS.md sets a worktree location, the coordinator creates the worktree there before dispatch and omits `isolation`. The brief names the branch. | unobserved |
| `environment: "local"` | Omit; no such field. | unobserved |
| `cloud_base_branch: <b>` | The brief names the checkout `<b>`. | unobserved |
| `run_in_background: true` | Pass it. | unobserved |
| `resume` | A new agent, the earlier result's text pasted whole into its brief; `SendMessage` in the cases `hugues-mode/SKILL.md` allows. | Same; its message tool is unobserved. |
| `file_attachments` | The brief lists the paths. | Same. |

In Cursor, read [hosts/cursor.md](hosts/cursor.md) for the field meanings.

### Models

| Cursor | Claude Code | Codex |
|---|---|---|
| `claude-<family>-<version>-<effort>[-fast]`, such as `claude-opus-5-5-xhigh` | `model: "opus"` while the Agent tool takes only aliases, and `effort: "xhigh"` to start, which "Match the model to the job" may lower with a reported reason. So does a role value `claude-opus-5-5 xhigh`. Drop `-fast`. | unobserved |
| A `gemini-*` or other non-Claude slug | Not accepted: the ` or ` rule above applies, and the Workers line names the model that ran. | unobserved |

## Model defaults and role labels

**Defaults for every agent-tool call.** `run_in_background: true` (a steer or resume of a running agent too, because a foreground call holds your turn while other reports wait), agent mode, file pointers instead of inlined context, and an explicit model and effort per role. `/setup-hstack` configures these defaults, and the ` or ` rule above picks the host's model:

- Code, prose and judgment: `claude-opus-5-5 xhigh or gpt-6-astra xhigh`.
- Trivial mechanical edits, swarm workers and verification: `claude-opus-5-5 high or gpt-6.1-sol high`.
- Diverse review and design panels, one worker per seat: `claude-fable-5-2 high or claude-opus-5-5 high or gpt-6-astra high`, `claude-opus-5-5 high or gpt-6.1-sol high`, and `gpt-6-astra high or claude-opus-5-5 high`.

Fable 5.2 runs outside a panel only on the router's Fable exception. No role runs above `xhigh`, and none asks for a speed, since the native agent tools have no speed setting to pass.

Per-role lines in `.hstack/models.md`, written by `/setup-hstack`, override these defaults and the model choices in the routed skills (`arena`, `swarm`, `interrogate`). A role with no line keeps its default; `inherit-parent` runs on the parent chat model (omit the agent tool's `model`), and so does a role whose alternatives the native agent tool all rejects. A file without a `# defaults: 3` line comes from an older setup. Keep honoring its lines, and tell the user once per session to rerun `/setup-hstack`. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it.

**Match the model to the job.** Before each spawn, start from the role's line or default, keep its family, and set the reasoning level the job needs. The `/setup-hstack` budget sets each role's starting level. Panel seats keep their listed level. Raise any other role one step, up to `xhigh`, for the hardest or subtlest work. Lower it one step for judgment and two or more steps for routine work. Verification always runs on the `swarm workers` model and level (`claude-opus-5-5 high or gpt-6.1-sol high` by default). Change only the effort level, so a diverse panel stays diverse. If the family has no model at that level, use its nearest one the native agent tool exposes. A role on `auto` or `inherit-parent` stays on the parent model. If the native agent tool rejects the adjusted value, do not try another adjusted value. Use the role's line or default and say so. If the native agent tool rejects that too, continue with the calling skill's fallback, or the ` or ` rule above when it has none. A value counts as rejected once a tool error says the model is not valid or leaves it out of its list of valid values. Never pass it again, and skip any fallback that names it. When the calling skill's fallback runs out without saying what to do next, omit `model` so the worker runs on the parent model, and say so.

**Role labels.** `setup-hstack` writes these labels and the router's playbooks read them. A code playbook's configured model comes from its line: `feature, refactoring`, `bug-fix`, `perf-issue` or `hillclimb`. Prose and judgment read `judgment and prose`. Trivial mechanical edits read `swarm workers`.
