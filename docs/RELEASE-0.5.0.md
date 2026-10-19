# hStack 0.5.0

Version 0.5.0 restores pstack 0.15.25's workflow rules where hStack had added its own controls. It removes payload protection and program-control helpers, returns mobile plans to ten lanes, and drops the verification-contract and stack-permission gates. Review existing plans and host settings before resuming work.

This release also bundles terminal and browser control procedures, resolves helpers from the loaded plugin copy, and defines native project-skill paths and a durable evidence store. The release has 57 public skills. Mobile proof starts with a real proof-tool preflight.

## Breaking and notable changes

- **Payload protection is withdrawn** ([#77](https://github.com/hugues-vnsgn/hstack/issues/77)). Autopilot runs no longer require a host-enforced read-only boundary around the installed plugin. The `payload-policy` and `helper-ready` verbs, `--macos-mobile` recipe, and native payload-boundary regression are removed. Plugin bindings and drift checks remain. A broken skill follows pstack's procedure for a fix in its own hStack PR. See [ADR 0001](adr/0001-follow-pstack-run-safety.md).
- **Approved proof and program control are removed** ([#80](https://github.com/hugues-vnsgn/hstack/issues/80)). The `program-check`, `artifact-hash`, `decode-design`, `worker-run`, `run-control`, and `run-wait` verbs and their guides are gone. Their hStack-specific fan-out limits, checkpoint recovery, and device reservations are also removed.
- **Mobile plans return to ten lanes** ([#81](https://github.com/hugues-vnsgn/hstack/issues/81)). Risk-based coverage is removed. `plan-check` ignores `verification_profile` and requires the fixed "Ten lanes on `<model>` at the PR head" heading and ten lanes.
- **The verification-contract gate is removed** ([#82](https://github.com/hugues-vnsgn/hstack/issues/82)). `plan-compare` and its contract reference are gone. A plan no longer needs a contract box under "Verdict and merge". Plans return to the agent store's `docs/` directory without the former Git-tracked-path or fenced-code requirements. A clean verdict requires every lane to pass.
- **Stack-permission and Astra High review policies are removed** ([#83](https://github.com/hugues-vnsgn/hstack/issues/83)). Autopilot-stack and setup no longer require the Claude auto-mode preflight. The hStack publication-scope policy is also removed. Consumer repository policy and current task authority still govern publication.
- **pstack's model-selection rule is restored** ([#89](https://github.com/hugues-vnsgn/hstack/issues/89)). Workers adjust role effort to task difficulty and use fast mode only for urgent work. Native model names and host mechanics remain adapted.
- **Bundled user-only skills load by file read on Claude Code** ([#48](https://github.com/hugues-vnsgn/hstack/issues/48)). Playbook references to these skills mean a complete `SKILL.md` read, rather than a denied Skill-tool call. Consumer and external skills keep native loading requirements. See [ADR 0002](adr/0002-read-bundled-user-only-skills-by-path.md).
- **Codex native loading is explicit** ([#99](https://github.com/hugues-vnsgn/hstack/pull/99)). The adapter defines loading as selecting an enabled host-catalog skill and reading its complete `SKILL.md`. A fresh worker performs its own load. Missing entries, disabled entries, and native denials retain their holds. The fix includes a source-contract regression. The final Codex run loaded the installed skill and saved the required local PR artifacts.
- **A publication hold keeps the local PR draft** ([#100](https://github.com/hugues-vnsgn/hstack/pull/100)). The adapter requires separate local title and body files checked against Opening a PR, including its section order, Scope, and verification requirements. Only forge writes are skipped when publication is held or unavailable. The source-contract regression passes. Both final host runs saved separate local PR files under the publication hold.
- **Bundled commands use the loaded plugin copy** ([#44](https://github.com/hugues-vnsgn/hstack/issues/44)). Plan checks, PR watching, orchestration, and decision logs use that copy even from another consumer directory. Workers carry its identity forward. Plan checks report the checker path, file and payload digests, and plugin commit when available. The [host validation](installed-helper-paths-validation.md) records bounded parent and child runs on both hosts.
- **Bun helpers have a one-time setup procedure** ([#101](https://github.com/hugues-vnsgn/hstack/pull/101)). The procedure requires an authorized frozen install and watcher help call for each installed copy. Missing dependencies or an absent or stale install key hold the dependent step. After setup, the final Codex read-only run called both helpers successfully without an install attempt or dependency changes. First-time installation into a read-only cache remains blocked.
- **Hosts without a todo tool use a checklist file** ([#102](https://github.com/hugues-vnsgn/hstack/pull/102)). The adapter translates the existing todo requirement to Markdown in the task's agent store. It preserves verbatim playbook steps, completion or skip reasons, and a path in the reply. Both final host runs wrote todos after reproduction. Codex used a numbered list. Recorded delegation skips allowed by pstack remain allowed.
- **Read the host contract before tools** ([#103](https://github.com/hugues-vnsgn/hstack/pull/103)). The skill headers explicitly require a full host-contract and mobile-applicability read before tools. In the final Claude Code run with hooks off, the first tool call read the host contract. The checklist still appeared after reproduction.
- **Project skills and agent stores use native locations** ([#34](https://github.com/hugues-vnsgn/hstack/issues/34)). New projects default to `.claude/skills` on Claude Code and `.agents/skills` on Codex. Existing supported layouts, categories, update targets, user edits, and feature maps take precedence. A named or existing program store wins. Otherwise the store is `~/hstack-evidence/<date>-<task>/`. Existing store arguments and internal layout remain.
- **Terminal and browser procedures are bundled** ([#34](https://github.com/hugues-vnsgn/hstack/issues/34)). `control-cli` and `control-ui` join `deslop` from Cursor's MIT-licensed `cursor-team-kit`. The [control-skills receipt](control-skills-validation.md) records the earlier tmux observation. U3 below adds a real Chrome observation without establishing autonomous procedure selection or Electron support.
- **Mobile proof begins with preflight** ([#75](https://github.com/hugues-vnsgn/hstack/issues/75)). Before lane planning, record sandbox state, host, OS, and tool versions. Check each required proof tool with a real harmless operation. Record blocked tools as gaps and drop or replace their lanes. Run the same operation as a host baseline before changing agent settings. A failing baseline stops settings iteration. These instructions do not establish a completed mobile journey.

## Upgrade from 0.4.x

1. Update or reinstall the plugin on each host, then start a fresh session. Keep an active task on its recorded copy until you can reconcile its binding. The plugin remains `hstack@hstack`, Claude commands retain `/hstack:`, and the setup skill remains `setup-hstack`.

   On Claude Code, refresh the configured marketplace and update the plugin:

   ```sh
   claude plugin marketplace update hstack
   claude plugin update hstack@hstack
   ```

   For a new install from that configured marketplace, use `claude plugin install hstack@hstack`. A session-only checkout uses the `v0.5.0` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

   On Codex, refresh the configured marketplace, then install its current plugin payload:

   ```sh
   codex plugin marketplace upgrade hstack
   codex plugin add hstack@hstack
   ```

   Check that the resolved payload reports 0.5.0. These command forms are present in the local CLI help. An update to a version-bumped release remains unobserved. In the pretest, a same-version `claude plugin update` retained the old commit. That result prompted this version bump. The commands above do not yet have observed 0.5.0 update evidence. If your host retains an older copy, use its supported reinstall controls and preserve the complete resource layout. Confirm native discovery before invoking `$hugues-mode` or `/hstack:hugues-mode`.

2. Before using `watch-pr` or `orch` from a newly installed copy, prepare its Bun dependencies once. Use a session authorized to install packages and write that copy's scripts directory. Expand `<plugin>` to the absolute root of the copy actually loaded:

   ```sh
   cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
   ```

   Standard roots are `~/.claude/plugins/cache/hstack/hstack/0.5.0` and `~/.codex/plugins/cache/hstack/hstack/0.5.0`. A custom loaded root takes precedence. Require exit 0 and inspect `node_modules/commander/package.json` and `node_modules/.poteto-mode-tools-install-key`. The key must equal SHA-256 of `package.json`, a NUL byte, and `bun.lock`, in that order. The help call lets the bootstrap write that key. A standalone frozen install does not write it. If setup lacks authority or the directory is not writable, hold the dependent step and report the exact expanded command. This setup does not widen the consumer sandbox.

3. Remove settings added only for the withdrawn controls, if you no longer need them. hStack does not edit host settings during this upgrade:

   - Remove the Claude permissions and sandbox fragments generated by `payload-policy`, or the generated Codex `hstack-program` permission profile and launch options that select it. Retain unrelated permissions and any settings your own project still requires.
   - Remove the Claude `autoMode.allow` entry beginning `hStack approved topology restack:` if you added it for the removed stack-permission preflight. Remove its dedicated `--settings /absolute/path/stack-permissions.json` launch argument if it is no longer used. Preserve other allow entries and defaults.
   - Remove project instructions that opt into the deleted `plugin/policies/astra-pr-review.md` two-seat Astra High policy. Ordinary `.hstack/models.md` model choices, including Astra choices, remain valid role configuration.

4. Review existing plans and scripts. Replace removed helper calls, rewrite risk-based live verification blocks to ten lanes, and drop obsolete contract boxes. Reconcile changed bindings explicitly. Do not rewrite hashes to hide unexpected drift.

## Validation

The first pre-release plan tested candidate `5601fd4` on 2026-10-19. Final Codex runs used `86e771f`; the final Claude run used the change merged in [#103](https://github.com/hugues-vnsgn/hstack/pull/103), now on main at `208c602`. The installed caches still carried the 0.4.0 version label. The chief's `decisions.tsv` is the verdict authority. The result cells below reproduce its recorded wording exactly. First-run failures remain as history. The chief accepted the final U4 runs with the checklist deviations recorded below, while the worker reports judged full adherence incomplete. Evidence classes describe what the recorded operation proves.

| Unit | Recorded verdict | Evidence class and limit |
|---|---|---|
| U0, Codex installed copy | `VERIFIED: Codex cache already byte-identical to main plugin/, includes control-cli` | Installed-file comparison against source. This proves payload identity, not a workflow. Logged at 04:14:07Z. |
| U1, Codex subagent | `VERIFIED; defect: Codex skill loading is a SKILL.md read` | Observed on Codex CLI 0.163.0. A native spawn links to a fresh child that reads its installed mode and role. No separate Skill RPC was observed. Chief judgment at 04:33:23Z. |
| U2, helper first run | `NOT VERIFIED on Codex default; defect: deps install into the read-only plugin cache` | Observed on Codex CLI 0.163.0 with its default read-only sandbox. The same chief row judges Claude headless `INCONCLUSIVE` and says both hosts pass with broad permissions. This does not establish interactive Claude approvals or default-permission success. Logged at 04:36:27Z. |
| U3, real browser control | `VERIFIED` | Observed operator run on Google Chrome 155.0.8059.80 over CDP. A click reserved seat A12, with screenshots, DOM and accessibility snapshots, and independent teardown checks. This was not an autonomous subject-selection test. Chief judgment at 04:36:27Z. |
| U4, Codex end to end | `NOT VERIFIED; defect: held publication skips the body` | Observed on Codex CLI 0.163.0 with workspace-write. The fix passed nine independently rerun Swift tests, but the required PR title and body were missing. Logged at 04:33:23Z. |
| U4, Claude Code end to end | `NOT VERIFIED; workflow adherence gap on a one-line fix` | Observed on Claude Code 2.1.303. The broader retry fixed the bug and passed Swift tests but omitted workflow steps and Opening a PR. Normal headless approval denials are a separate limit. Logged at 04:36:27Z. |
| Final U2, Codex after setup | `VERIFIED` | Codex CLI 0.163.0, default read-only sandbox. Both helpers exited 0 without an install attempt. Dependency hashes stayed unchanged. Chief judgment at 05:57:18Z. |
| Final U4, Codex | `VERIFIED; known gap: late or numbered todo list` | Workspace-write run at `86e771f`. Separate checked PR files were saved under the hold. The operator reran nine Swift tests successfully. The numbered plan appeared after reproduction. Chief judgment at 05:57:18Z. |
| Final U4, Claude before the host-read fix | `NOT VERIFIED; root cause: 'apply the host contract' doesn't say read it` | The subject omitted host/publication reads, checklist and PR files. Hook memory confounded diagnosis. Chief judgment at 06:00:35Z. |
| Final U4, Claude with the host-read fix, hooks off | `VERIFIED; known gap: late todo list (both hosts)` | Claude Code 2.1.303 in headless bypassPermissions mode. The subject read host.md first, saved a checklist and separate PR files, and passed four operator-run Swift tests. The checklist came after reproduction. Chief judgment at 06:17:15Z. |

The local evidence root is `~/hstack-evidence/2026-10-19-release-0.5.0-pretest/`. It contains `plan.md`, `decisions.tsv`, the linked native parent and child records under `worker-1/u1-role-normal/`, both hosts' helper runs under `worker-2/u2-*`, Chrome captures under `worker-2/u3-browser/`, and the U4 transcripts and independent Swift results. Worker reports remain in the chief's local release notes folder.

All five pretest fixes are merged in [#99](https://github.com/hugues-vnsgn/hstack/pull/99), [#100](https://github.com/hugues-vnsgn/hstack/pull/100), [#101](https://github.com/hugues-vnsgn/hstack/pull/101), [#102](https://github.com/hugues-vnsgn/hstack/pull/102), and [#103](https://github.com/hugues-vnsgn/hstack/pull/103). Their maintenance checks passed. The release preparation retains 436 collected top-level tests, including the historical restoration driver. The five maintenance commands are listed in the [README](../README.md#reference-and-maintenance). Static checks prove source and wiring, separately from the bounded host observations above.

The final evidence is summarized in `final-worker-1-report.md`, `final-worker-2-report.md`, and `f5-worker-2-report.md` under the chief's local `_notes/release-0.5.0/` folder. The latter two files contain the same final Claude report. Earlier Claude results remain in `f5-worker-2-evidence/prior-final-worker-2-report.md`. The ledger, rather than the workers' proposed verdicts, supplies the recorded release decisions.

## Known gaps

- Both hosts wrote their todo list after reproduction, rather than before step 1. Codex used a numbered list without Markdown checkboxes. The final accepted results do not establish full checklist adherence.
- The final Claude result used hooks disabled and bypassPermissions in headless mode. Interactive use under normal permissions remains unobserved. Earlier headless sessions could not answer approval prompts. Other configured plugins and task-management MCP tools remained enabled, so the no-todo-tool fallback was not fully isolated.
- Each final run is a single sample. The observed results do not establish repeatability.
- Codex's initial default read-only sandbox blocked dependency installation into the plugin cache. The final pass proves helper use after authorized setup, not installation under those permissions.
- Updating a version-bumped marketplace release remains unobserved. The same-version Claude update kept the old commit.
- The release trail records `claude-review` blocked by [anthropics/claude-code-action#1901](https://github.com/anthropics/claude-code-action/issues/1901). Maintenance passing is separate from a completed Claude review. The watcher's match on bot login `claude` remains unconfirmed until a real review is observed on a PR.
- [#34](https://github.com/hugues-vnsgn/hstack/issues/34) items 4 through 6 remain deferred. They cover native history acquisition, managed cloud workers, and loop or scheduler bindings. The optional Orca adapter in [#50](https://github.com/hugues-vnsgn/hstack/issues/50) and [#96](https://github.com/hugues-vnsgn/hstack/issues/96) are also deferred. This release does not close those work items.
- Native skill creation and categorized updates, whole-map maintenance, replacement-coordinator store recovery, Origin execution, Electron control, and complete mobile consumer journeys were not established by these release tests. The U4 fixture was a standalone macOS Swift package. It does not prove iOS, Android, KMP, or CMP behavior.
