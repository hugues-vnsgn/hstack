# Planning, cleanup and executable helpers

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

The pinned Bun helpers include a bootstrap that can install dependencies.
Do not execute it without installation authority. First inspect local runtime and
cached dependencies. A missing runtime, dependency, cloud worker, forge API or
loop primitive blocks that operation; preserve its intended gate and report the
gap. Native local workers substitute for cloud only where the core permits local
execution; do not simulate a race sequentially. Nothing in Babysit, Shipping or
Orchestrate arms a remote action without explicit scope.
