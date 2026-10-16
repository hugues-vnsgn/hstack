# Prompts worth copying

Swap in the real paths, skills, and done checks. Informal wording works. These use the short slash form. In Claude Code, type the plugin prefix, as in `/hugues-stack:hugues-mode`. In Codex, type `$hugues-mode`.

## Understand

- `/hugues-mode read <thread>. restate the underlying issue in your own words, in plain english.`
- `/in-your-own-words <long or messy ask>`
- `/sharpen <your task>`
- `/hugues-mode investigate why <symptom>. give me what we know, what data you used, and your best hypotheses. don't change any code yet.`
- `use /how to understand <subsystem>. then use /why to find out why it broke recently.`
- `/recall my work on <topic> from last week, then read <issue>.`
- `/teach me why you implemented it this way and not <other way>. what did you trade off?`
- `/hugues-mode take over this branch. read the decision log, find what's done, and continue. don't redo finished work.`

## Build

- Bug: `/hugues-mode <symptom>. repro first, then fix and verify.`
- Bug in an app: `/hugues-mode repro this with /verify-<app>. if it repros on main, fix it and show me a video as proof.`
- Bug with a cheap test: `/hugues-mode repro <bug> first. if there's a cheap test path, /tdd it. then fix and rerun.`
- Feature: `/hugues-mode add <behavior>. <current output> stays byte-identical. verify both.`
- Refactor: `/hugues-mode move <code> into one module, zero behavior change. record the current output first and prove it's unchanged after.`
- Perf: `/hugues-mode <operation> takes <time> on <fixture>. trace it, fix the measured cause, show me before and after.`

## Mobile

- Build failure: `/hugues-mode the <ios or android> build fails with <error>. diagnose it and tell me the cause. don't change any code yet.`
- Mobile bug: `/hugues-mode <symptom> in <app>. write a failing regression test first and show it failing on the unfixed code. then fix it and show the same test passing. you may edit <paths> and run the existing tests.`
- Proof on simulator and emulator: `/hugues-mode prove <flow> works on the iOS simulator and the Android emulator with /verify-<app>. keep the commands, screenshots, and videos in the evidence folder.`
- Shared KMP change: `/hugues-mode change <shared api> in the KMP module. prove one Android caller and one iOS caller still work, and say which targets you did not check.`
- Shared Compose screen: `/hugues-mode <ui change> in the shared Compose screen. show it on the Android emulator and the iOS simulator, with a screenshot from each.`

## Design and plan

- `/hugues-mode prototype a few options for <feature>. take screenshots or videos for me to compare.`
- `/hugues-mode we need <feature>. /architect it first, and answer open questions with prototypes. let me review before proceeding.`
- `/hugues-mode write a tutorial for how i would use <new package> first. then /teach me why it beats the current one.`
- `ask /arena for a second opinion on this thread and our approach.`
- `/hugues-mode turn this design into a plan. small verifiable PRs, each with its own verification steps.`
- `/hugues-mode plan the migration of <library> to <target>. small verifiable PRs. the result must match the original exactly, bugs included.`

## Review and ship

- `/interrogate the whole branch, but skeptically. don't change anything yet. no nitpicks unless it's a real bug or regression.` Read the dismissals too.
- `/swarm check every package under <dir> against its check script. one worker per package. one report.`
- `/hugues-mode open the pr. small ordered commits, evidence in the description.`
- `/hugues-mode babysit this pr. get it green.` For status only: `/hugues-mode check on pr <number>. anything outstanding?`
- `/hugues-mode land the stack.`

## Away and back

- `/hugues-mode im going to bed. <goal> in a fresh worktree off <base>. done means <checks>. keep a decision log. don't ask me before committing. loop until done. if you're truly stuck after a few hours, stop and write up why.`
- `/show-me-your-work catch me up on what you did last night.` Read its Attention section first.
- `/ketchup` catches you up on this chat since your last message.
- `/hugues-mode full autopilot on this queue. each item is independent.`
- `/hugues-mode autopilot these changes but stack them, don't ship. i'll land the stack.`
- `/reflect capture what we learned so the next run doesn't repeat it.` Approve only edits that change a future decision.
- `/bro` restates the last reply in plain words.
