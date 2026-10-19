# Installed helper path validation

Issue [#44](https://github.com/hugues-vnsgn/hstack/issues/44) concerns which plugin copy executes a bundled command. This check uses disposable consumer directories with decoy scripts. It does not exercise a mobile target, forge polling or an unattended program.

## Reproduction and regression

From a disposable consumer directory, the canonical `node skills/hugues-mode/scripts/check-plan.mjs plan.md` exited 1 with `Cannot find module`. The bound installed command passed the same plan with `1 PR sections, 0 problems`.

Two installed Python regression cases cover a Gitless plugin with spaces in its path, a consumer decoy and real consumer commit, and a tracked plugin checkout on validation failure. The first reports a null plugin commit instead of the consumer commit. The second reports the plugin commit and preserves exit 1 and the original validation diagnostics.

## Host checks

The first Claude Code and Codex sessions loaded the candidate worktree plugin from disposable consumers. Each parent and one fresh helper bound that same loaded copy, translated a plan, passed its plan check and wrote a decision-log row. The briefs contained canonical commands and no absolute script path. Each parent supplied the loaded mode identity to its helper through the adapter rule. Neither selected a consumer decoy or a competing installed cache.

The first runs left watcher and orchestration help unlaunched because their local dependencies were absent. A second run uses a separate copied plugin directory with spaces in its path and prepared locked dependencies. Both parent and child in both hosts executed the installed plan checker, watcher help, orchestration help and log writer with exit 0. Each plan check reported `1 PR sections, 0 problems`; each log contained one data row. All four identity records named the copied installed checker and agreed on its file and payload digests. The plugin commit was null for this Gitless copy. Direct readback confirmed the output files and that the copied plugin source matched the final worktree byte for byte.

| Host | Version | Parent commands | Fresh helper commands |
|---|---|---|---|
| Claude Code | 2.1.303 | All four passed | All four passed |
| Codex CLI | 0.163.0 | All four passed | All four passed |

The runtimes were Python 3.14.7, Node 26.8.1 and Bun 1.3.14. Locked dependencies were prepared only in the disposable copy. The first Codex run needed an isolated retry after its initial child dispatch could not load thread context; the retry and second run completed. Raw transcript hashes are recorded in the worker report alongside the local logs.

Claude Code loads the candidate with `--plugin-dir` and `--agent hstack:hugues-agent`. Codex discovers its skills through a project-local `.agents/skills` link and receives `$hugues-mode`. These are bounded local host observations, not an installation on another machine. The helper check preserves the consumer working directory. A literal relative plan operand in the translated plan still resolves there; the checker executable itself is absolute.

## Context figures for issue 84

After resealing, the generated budget counts 9,078.25 estimated tokens per fresh bug-fix mode worker and 72,626.0 for eight feature mode workers. The comparison values remain 9,403.5 and 75,228. The scenarios contain five and fifteen workers overall, respectively, of which one and eight load mode context.

The historical 252.5-token increase is 8,410.75 at `8b7127a` minus 8,158.25 at `4b13e5b`. Both values come from each commit's `docs/CONTEXT-BUDGET.json`, not from today's floor. The current prose and table use the regenerated budget. Token estimates are Unicode characters divided by four, not observed host token usage.

## Review and limits

Three fresh Interrogate reviewers returned no findings. They used the parent model, so this is process independence without model-family diversity. The comment review found no changed code comments or suppressions.

The raw local host transcripts and checks remain under the worker's release notes directory. No consumer source, installed user cache, frozen release archive or private planning file changed. Task B is outside this change.

All five README maintenance commands passed. The Python suite ran 427 collected cases, including the separate 50-case historical driver, with no failures or skips. Source checks still validate 169 upstream rows, 55 skills, 23 core playbooks, four mobile playbooks and 15 worker roles.
