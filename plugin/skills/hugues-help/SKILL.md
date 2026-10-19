---
name: hugues-help
description: Guides users through hStack setup, /hugues-mode, mobile routes, and picking the skill, playbook, or principle for a task. Type /hugues-help with a question.
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Hugues help

Answer the user's question about hStack, hand them a prompt they can send, and link the file the answer came from. For a help question, don't start the work. The user asked how, and an hStack run spends real tokens, so let them send the prompt.

A message that asks for work, such as "use hStack to fix this bug", is not a help question. Reach [`hugues-mode`](../hugues-mode/SKILL.md) through the host's supported native mechanism, as the [host contract](../../adapters/host.md) says, and do the work under it. If the host cannot, give the user the exact command to type, `/hstack:hugues-mode` in Claude Code or `$hugues-mode` in Codex, and stop.

This file maps questions to the skills and guide pages that hold the answers. Those files own the details. Read the file you route to before you quote it, and trust it when it disagrees with this map. The links here point into the installed plugin, and the guide lives outside it, so give the user the file's public copy: `https://github.com/hugues-vnsgn/hstack/blob/main/` followed by its repository path, such as `plugin/skills/how/SKILL.md` or `docs/pstack/guide/01-setup.md`.

Commands in this file use the short slash form. The user types the plugin prefix in Claude Code, as in `/hstack:how`, and `$` in Codex, as in `$how`.

## Find out what they need

Infer the need from the message and the conversation. A named situation, such as "which skill reviews a PR?", goes straight to its section. If the need is still unclear, ask one multiple-choice question with the host's question tool (`AskUserQuestion` in Claude Code), then answer only the section they pick:

- Get set up
- Start a task with `/hugues-mode`, mobile work included
- Pick a skill for a situation
- Fix a run that went wrong
- Make hStack my own

Check the state that changes the answer, and mention it only when it does:

- No `.hstack/models.md` at the project root means `/setup-hstack` hasn't run for this project, so every role keeps its default: the chat's own model at `xhigh` for code and `max` for prose and judgment. If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it.
- No `verify-*` skill or other app harness in the project means agents have no scripted way to drive the app. Mention `/create-verification-skill` when the question is about proving a change works. Mobile proof needs the project's `verify-<app>` skill.

When the model file is missing and it matters, ask whether the user wants to pick a model for each role and a reasoning budget now. It matters when the user is new, the question is about setup or cost, or the answer depends on which models run. Ask at most once per chat. If the need is also unclear, ask both questions together. Offer two choices:

- Now: give them `/setup-hstack` to type, and answer their question too.
- Later: answer their question, and add one line saying every role keeps its default model until they run `/setup-hstack`.

## Get set up

1. Install the plugin. In Claude Code, load the checkout for one session with `claude --plugin-dir "/absolute/path/to/hstack/plugin"` and confirm `/hstack:hugues-mode` is discovered before using it. In Codex, use a supported native discovery route and confirm `hugues-mode` appears before typing `$hugues-mode`. The Codex install route is unverified. If discovery or typing the command fails, stop. Don't paste a SKILL.md path as a workaround.
2. Run [`/setup-hstack`](../setup-hstack/SKILL.md). It asks for a reasoning budget, maps a model to each role, and writes `.hstack/models.md` in the project. Each skill reads the file at its next role selection, so the roles apply from the next subagent spawn. For a mobile project it also looks for a `verify-<app>` skill and offers once to generate one.
3. Start a real task with `/hugues-mode`, a goal, and a check that can pass or fail.

Only `hugues-mode` and `setup-hstack` appear in the host's skill list. Every other skill is user-only: the user types its name, or `/hugues-mode` reads its SKILL.md as a file when a step needs it. The [README](https://github.com/hugues-vnsgn/hstack/blob/main/README.md) and [guide page 1](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/01-setup.md) have the details. Offer to word their first prompt with them, per [`references/prompting.md`](references/prompting.md).

If cost is the worry, say where the tokens go and how to spend fewer. hStack spends extra tokens on subagents and review panels. Rerun `/setup-hstack` and pick a smaller budget or cheaper models, and match the budget to the job: less for easy work, more for hard design and review. A role set to `inherit-parent` runs on the chat's model, which saves tokens when the chat runs on a cheaper model. A shorter panel list runs fewer subagents, one for each entry. Save `/hugues-mode` for work that needs rigor.

hStack targets Claude Code and Codex. Its workflow skills hand work to the host's own subagents: Claude Code's registered `hstack:hugues-agent` and `general-purpose` agents, and fresh workers that Codex starts with the same role instructions. See [workers and models](../../adapters/host-workers.md). The README lists what has and hasn't been observed on each host. Say "not observed" instead of promising that a workflow will run end to end.

## Start a task with `/hugues-mode`

`/hugues-mode` matches the task to a playbook, copies the playbook's steps into the todo list, and runs the other skills as the steps need them. A step it skips stays in the list as `skip: <reason>`. A good prompt states the goal and how to tell it's done. It doesn't list skills, because a hand-written sequence tends to drop or reorder steps the playbook would keep. Read [`references/prompting.md`](references/prompting.md) before you help word one. [Guide page 2](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/02-poteto-mode.md) has examples.

Don't promise that the mode stays on every turn. hStack documents no host setting that pins it, so when it fades, start the next task with `/hugues-mode` again. Mid-chat, "new task" makes the mode match a fresh playbook.

`/hugues-mode` already uses `hugues-agent` for the subagents its playbook steps spawn. To get the same style from a subagent of your own, spawn it as `hugues-agent`. Claude Code registers it as `hstack:hugues-agent`, the `subagent_type` to pass. Codex takes the role instructions of `agents/hugues-agent.md` through its supported fresh-worker mechanism.

## Work on a mobile app

For an explicit Swift/iOS, Kotlin/Android, KMP, or CMP task, `/hugues-mode` applies [mobile applicability](../../adapters/mobile.md#applicability) first, picks a core playbook from the intent, and adds a mobile route when one fits. Intent comes before domain. Mentioning Swift or Kotlin grants no permission to edit, build, or run the app, so the prompt says what the agent may do and in which checkout. [Mobile workflows](../../adapters/mobile-workflows.md) owns the routing.

| The user wants to | Route |
|---|---|
| Find why an iOS or Android build or toolchain fails | [build-doctor](../hugues-mode/playbooks/build-doctor.md) |
| Prove a change on a simulator or emulator with the project's existing `verify-<app>` skill | [mobile-proof](../hugues-mode/playbooks/mobile-proof.md) |
| Change a shared KMP boundary and prove both native callers | [kmp-bridge-change](../hugues-mode/playbooks/kmp-bridge-change.md) |
| Change shared Compose Multiplatform UI and prove it on both runtimes | [cmp-two-target-change](../hugues-mode/playbooks/cmp-two-target-change.md) |

What to tell the user about proof:

- A build is not proof. The routes ask for a run on each affected target, the iOS simulator, the Android emulator, or both for shared code. One target doesn't prove the other.
- A mobile bug gets a regression test seen failing on the unfixed code before the fix, then passing on the same test, or a recorded reason a test is impractical.
- Logs, screenshots, and videos go in a task evidence folder outside the repository, such as `~/hstack-evidence/<date>-<task>/`. They stay on the computer unless the user authorizes sending them. `/ketchup` shows them when it catches the user up.
- A missing simulator, emulator, tool, `verify-<app>` skill, or go-ahead to run is reported as blocked, never as a pass.

Point to [mobile lanes](../hugues-mode/references/mobile-lanes.md) and the [evidence guide](../hugues-mode/references/evidence-guide.md) for the detail.

## Pick a skill

The default answer is `/hugues-mode`, which runs most of the others when its steps need them. Name a skill directly when the user wants more or less of something than the playbook gives. Read the skill before you recommend it, and give one example prompt.

| The user wants to | Skill |
|---|---|
| Do any non-trivial task with rigor | [`/hugues-mode`](../hugues-mode/SKILL.md) |
| Work on a Swift/iOS, Kotlin/Android, KMP, or CMP app | [`/hugues-mode`](../hugues-mode/SKILL.md) and its mobile routes above |
| Check that the agent understood their goal and the problem before it starts | [`/in-your-own-words`](../in-your-own-words/SKILL.md) |
| Aim a task higher before starting: more expert, more outcome-focused, not overspecified | [`/sharpen`](../sharpen/SKILL.md) |
| Know how code works now, or where new code should live | [`/how`](../how/SKILL.md) |
| Know why code is shaped this way, or where a number came from | [`/why`](../why/SKILL.md) |
| Understand a change or subsystem, explained plainly | [`/teach`](../teach/SKILL.md) |
| Catch up on their own recent work on a topic | [`/recall`](../recall/SKILL.md) |
| Catch up on what changed in this chat since their last message, in a few plain sentences and small visuals, with enough context to decide each action item | [`/ketchup`](../ketchup/SKILL.md) |
| Know what a small diff could break outside itself | [`/blast-radius`](../blast-radius/SKILL.md) |
| Settle types and module shape before code that crosses a function boundary | [`/architect`](../architect/SKILL.md) |
| Get several attempts at one brief, merged into the best one | [`/arena`](../arena/SKILL.md) |
| Run parallel checks over slices, or race workers | [`/swarm`](../swarm/SKILL.md) |
| Have different models review a diff and try to break it | [`/interrogate`](../interrogate/SKILL.md) |
| Fix a bug test-first when a cheap local test exists | [`/tdd`](../tdd/SKILL.md) |
| Apply TypeScript rules to `.ts` or `.tsx` work | [`/typescript-best-practices`](../typescript-best-practices/SKILL.md) |
| Strip AI slop from the diff before committing | [`/deslop`](../deslop/SKILL.md) |
| Strip comments before review, using a reviewer that didn't write them | [`/no-comments`](../no-comments/SKILL.md) |
| Clean AI tells out of prose | [`/unslop`](../unslop/SKILL.md) |
| Write docs, an RFC, a README, a PR description, or a commit message to a standard | [`/technical-writing`](../technical-writing/SKILL.md) |
| Hear the last reply again in plain words | [`/bro`](../bro/SKILL.md) |
| Give agents a scripted way to drive the app and prove behavior | [`/create-verification-skill`](../create-verification-skill/SKILL.md) |
| Bring a verification skill and its feature map back in line with the app | [`/maintain-verification-skill`](../maintain-verification-skill/SKILL.md) |
| Vet a performance number before reporting or acting on it | [`/benchmark-checklist`](../benchmark-checklist/SKILL.md) |
| Run a large or cross-cutting change, or one to review after stepping away | [`/figure-it-out`](../figure-it-out/SKILL.md) |
| Keep a decision log during a run, and review it afterward | [`/show-me-your-work`](../show-me-your-work/SKILL.md) |
| Pick a model for each role and a reasoning budget | [`/setup-hstack`](../setup-hstack/SKILL.md) |
| Turn their own working habits into a personal mode skill | [`/automate-me`](../automate-me/SKILL.md) |
| Turn what a finished task taught into skill edits | [`/reflect`](../reflect/SKILL.md) |
| Stop agents from repeating the same mistakes in this repo | [`/correct`](../correct/SKILL.md) |
| Build a page whose buttons wake a bot over a webhook, where the host has the routine tool the skill calls | [`/make-bot-ui`](../make-bot-ui/SKILL.md) |
| Find their way around hStack | `/hugues-help` |

If a skill directory next to this one is missing from the table, read its frontmatter and route by its description. The `principle-*` directories are covered under principles below.

Close calls:

- `/how` explains what the code does. `/why` explains the reasons. `/teach` runs one or both and explains the result plainly.
- `/arena` gives every worker the same brief and merges the best parts. `/swarm` splits work into slices or a race and returns one report.
- `/architect` implements right after it settles the design. Add "with checkpoint" to review the design before it writes code.
- `/interrogate` reviews the diff. `/blast-radius` looks for breakage outside the diff and proves the one fact that makes the change safe.
- `/recall` rebuilds context across recent chats. `/ketchup` covers only this chat since the user's last message. Resuming one specific chat or branch is the Session pickup playbook.
- `/figure-it-out` designs one rigorous run. The Orchestrate playbook runs a program that spans days and many PRs. The Autonomous run playbook drives one task to a finish condition.

hStack bundles [`control-cli`](../control-cli/SKILL.md) and [`control-ui`](../control-ui/SKILL.md) from Cursor's `cursor-team-kit`. A playbook reaches them through the bundled-skill read rule. Their harnesses use available local terminal and browser tools; a missing driver remains an execution gap, not a missing skill.

Not in hStack:

- There is no `/orchestrate` skill. Orchestrate is a `/hugues-mode` playbook. If the skill menu shows `/orchestrate`, another plugin provides it.
- There is no loop skill. Playbooks that loop use the host's loop primitive, and a host without one blocks that operation and reports the gap.

## Playbooks and principles

Playbooks are step lists inside `/hugues-mode`, not skills, so they have no slash command. Inside `/hugues-mode`, describing the task picks one, and these phrases name one directly:

- "babysit this pr" or "check on pr 123" runs Babysit. It drives the PR to merge-ready and stops there. It doesn't merge unless the user asks to merge, land, or ship.
- "land the stack" runs Shipping.
- "take over this branch" runs Session pickup.
- "pause safely" runs Pause safely.
- "full autopilot on this queue" runs Autopilot-full. "stack them, don't ship" runs Autopilot-stack.
- "run the eval playbook" runs Eval.

The Playbooks section of [`hugues-mode`](../hugues-mode/SKILL.md) lists every playbook and when it applies. [Guide page 6](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/06-verify-and-ship.md) covers opening, babysitting, and landing a PR.

hStack has no planning skill. For work that spans phases or stacked PRs, asking `/hugues-mode` for a plan runs the [Multi-phase plan playbook](../hugues-mode/playbooks/multi-phase-plan.md), which writes the plan and doesn't implement it. For a design question, the Prototype playbook or `/architect` settles it in code first.

Principles are one-rule skills that `/hugues-mode` reads and cites in its replies. The user rarely types one. They steer with the names instead, as in "apply prove it works. show me the real output." Typing `/principle-<name>` still loads one on demand. [Guide page 8](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/08-principles.md) lists them.

## Fix a run that went wrong

| Symptom | Fix |
|---|---|
| The mode stopped applying after a few turns | Start each task by typing `/hugues-mode` again. |
| A question got treated as the next step of the last task | Say "new task", or say the turn doesn't need the mode. |
| A new model choice had no effect | Skills read `.hstack/models.md` at each role selection. Check that the role's line exists and is spelled as `/setup-hstack` wrote it, and whether the host rejected that model and fell back to the role's alternative, which the report names. |
| Runs cost more than expected | See the cost paragraph under Get set up. |
| A skill didn't run on its own | Only `hugues-mode` and `setup-hstack` can be picked from the user's words. The others run when the user types them or when `/hugues-mode` reads them, and it doesn't read every skill. |
| Parallel agents overwrote each other | Give each agent its own worktree. |
| An overnight run moved but finished nothing | A loop needs a check that can pass or fail, not a duration. See [guide page 7](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/07-overnight.md). |
| The reply claims success from a green build | Ask for the real command, flow, stored value, or profile. That's the prove-it-works principle. |
| A mobile result passed on one platform and was reported for both | Ask which target each result came from. A build or one target doesn't prove the other. |
| A mobile proof step is reported blocked | A prerequisite is missing: the `verify-<app>` skill, a simulator or emulator, a tool, or the user's go-ahead to run. Supply it, or leave the gap visible. |

For a run that drifts, [`references/prompting.md`](references/prompting.md) has one-line steers. [Guide page 10](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/10-recipes-and-pitfalls.md) has more pitfalls and the recipes worth copying.

## Make hStack my own

- [`/automate-me`](../automate-me/SKILL.md) drafts a personal mode skill from the user's own history, to use alongside `/hugues-mode`. It places the draft in the project's established `.claude/skills` or `.agents/skills` convention, and without an authorized transcript source its history mining stays blocked.
- [`/reflect`](../reflect/SKILL.md) after a session turns its lessons into skill edits the user approves.
- `/hugues-mode write a skill for <workflow>` runs the authoring playbook. The eval playbook tests a skill change blind.
- Fix a misbehaving skill in its own PR, not inside the feature work where it went wrong.

[Guide page 9](https://github.com/hugues-vnsgn/hstack/blob/main/docs/pstack/guide/09-make-it-yours.md) covers each of these.

## Reply

Lead with the answer. Give at most one example prompt in a code block, adapted from [`references/recipes.md`](references/recipes.md) when one fits, then the link to that file. Keep it short unless the user asked for the whole map.
