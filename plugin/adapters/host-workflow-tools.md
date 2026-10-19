# Planning, cleanup and executable helpers

## Resolve bundled commands on both hosts

Use the absolute loaded `skills/hugues-mode/SKILL.md` found by
`hugues-agent` as [host.md](host.md) directs. Its grandparent's parent is
`<plugin>`. Keep that root for this run, including helpers and subagents.
On Codex, the available skills list supplies the absolute `hugues-mode` path.
On Claude Code, the loaded skill's base directory supplies it. A known loaded
path wins over discovery, even when that path is a maintainer checkout.
Never replace it with a newer checkout or another cached version.

Translate each bundled command before execution. Quote the resulting absolute
script path and keep the consumer working directory and arguments. Resolve
consumer plans, stores and log files against that directory.

| Canonical operand and caller | Installed command |
|---|---|
| `node skills/hugues-mode/scripts/check-plan.mjs <plan.md>` in multi-phase-plan | `python3 "<plugin>/adapters/host_tools.py" plan-check --binding "<program>/plugin-binding.json" "<absolute-consumer-plan.md>"` |
| `scripts/watch-pr/watch-pr` in babysit and shipping, including `--queued-stack` | `bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" <same arguments>` |
| `bun scripts/orch/orch.ts` and its `orch` shorthand in orchestrate | `bun "<plugin>/skills/hugues-mode/scripts/orch/orch.ts" <same arguments>` |
| `scripts/log.sh` in show-me-your-work | `bash "<plugin>/skills/show-me-your-work/scripts/log.sh" <same arguments>` |
| Worktree-cleanup's upstream audit script | `worktree-audit` through the installed host tools below |

The same rule covers a bundled script named from its owning skill directory.
The example `scripts/snapshot.sh` in a decision-log row is consumer evidence,
not a bundled helper. Consumer commands retain their own paths.
An absent loaded root or script holds the dependent step. Do not search the
consumer or another plugin copy to fill it. Worker dispatch carries the loaded
mode path through [workers and models](host-workers.md); a helper resolves this
table itself, without a hand-written script path in its brief.

## Agent-store translation

Before a plan, program or decision trail needs the inherited "agent store",
use the operator-named directory or the existing program's recorded directory,
including an explicit `--store` or `ORCH_STORE` binding. Preserve the existing
flag/environment precedence. With none established, use
`~/hstack-evidence/<date>-<task>/`. Resolve that choice once to an absolute path
and carry it into briefs, helpers, pickup notes and replacement coordinators.
Resume the recorded store rather than creating a new dated directory.

Keep pstack's relative layout: plans under `docs/`, programs under
`orchestrate/<project-slug>/`, and their decision trails, agent registers,
receipts and recovery files. Explicit plan and log targets still win. Pass the
actual orchestration program directory through the existing `--store` or
`ORCH_STORE`, preserving a bound program path without appending another program
subdirectory. Pass the complete log-file path to `log.sh`. Keep all state outside
the installed plugin. This is a path translation, not a new runtime or permission
to access another program's state.

## Planning and audit translations

For executable operands in planning and cleanup, use the installed
[host tools](host-tools.md) and [entrypoint](host_tools.py). In multi-phase-plan,
replace the consumer-relative Node command with `plan-check`. Translate bundled
`git show origin/main:pstack/...` reads in that plan and autopilot-full/stack to
`read-workflow` using the program's saved installed-payload binding at every tick.
Consumer-owned trunk reads stay on consumer Git. In worktree-cleanup step 1 use
`worktree-audit` with explicit authorized native source inputs. Unknown activity
coverage holds candidates; the separate active/pinned-chat gate remains required.
The supported native hosts are Claude Code and Codex. Ignore Cursor transcript
sources without reading them or counting them as supported-host coverage.
These are mechanical operand translations, not new execution or deletion scope.

Before Bun helpers, read [helper setup](host-helper-setup.md) in full.
The bootstrap can install dependencies.
Do not execute it without installation authority. Missing runtimes, dependencies,
cloud workers, forge APIs or loop primitives hold their operation, preserve its
intended gate and report the gap. Native local workers substitute for cloud only
where the core permits local execution. Never simulate a race sequentially.
Remote actions require explicit scope.
