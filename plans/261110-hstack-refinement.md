# hStack refinement plan for the owner's own setup

Date: 2026-11-10. Source: a question-and-answer session with the owner. This
file records decisions only. No plugin file changed in that session.

## Goal

Refine hStack for the owner's daily setup: Claude Code running inside the Orca
and Herdr apps, on the owner's own projects. Two cross-cutting aims apply to
all the work: spend fewer tokens, and make adding a skill simple.

Out of scope for now: gaps that only affect other users, such as Codex, stock
Cursor and the marketplace install route.

## What the research found

Five subagents read upstream pstack 0.15.36 and compared it with this
repository at commit `2515e9e`.

- **Herdr is absent.** No file in the repository mentions it. Orca has a host
  page (`plugin/adapters/hosts/orca.md`) and a SessionStart detection hook
  (`plugin/hooks/host-detect.sh`).
- **The verification generator is browser-first.** The drive guidance in
  `plugin/skills/create-verification-skill/SKILL.md` covers Playwright, CDP and
  ARIA. Its output path is not a problem: `plugin/adapters/host-special-skills.md`
  already translates `.cursor/skills` to the host's own folder.
- **The arena cross-judge needs a pool.** It is skipped unless
  `.hstack/models.md` names a judge pool (`docs/RELEASE-0.5.8.md`, known gaps).
- **Startup cost is already small.** Only `setup-hstack` is model-invocable, so
  about 116 characters of description load at session start.
- **The cost is per workflow.** `docs/CONTEXT-FOOTPRINT.md` estimates about
  35,000 tokens of instructions for a one-function bug fix and about 37,000 for
  a three-module feature. These are source-byte estimates. Nothing in the
  repository measures what a real run spends, including its workers.
- **Plugin markdown totals about 620 KB**, roughly 155,000 tokens at four
  characters per token. The three groups are listed under
  [Compression worklist](#compression-worklist).
- **An earlier rewrite was reversed.** `docs/CONTEXT-FOOTPRINT.md` records that
  a router rewrite restated pstack's rules and that the original wording was
  later put back.

Owner-reported and not recorded in this repository: hStack works in Claude Code
inside Orca and Herdr, and a full run on a real app succeeded on the owner's
Mac. The README still lists a complete consumer journey as unobserved.

## Decisions

### Hosts

- Add a Herdr page beside `plugin/adapters/hosts/orca.md` and add Herdr
  detection to `plugin/hooks/host-detect.sh`. Cover terminal and worktree
  mechanics only, as the Orca page does.

### Verification on every stack

- Keep one `create-verification-skill`. Add one small reference file per
  surface, and read a reference only when the project has that surface.
- Write the references in this order: iOS simulator, Android emulator, backend
  API (.NET), desktop. Leave web and CLI as they are.
- This applies to every stack, not only mobile.

### Model roles

- Add `.hstack/models.md` in each project so arena and architect get a second
  opinion. Use Codex as the other-family judge where it is available. Otherwise
  use Claude tiers, and state in the file that this is weaker than a true
  other-family judge.

### Personal tuning

- Run `/reflect` after each real session and `/correct` when the agent repeats
  a mistake. Do not hand-edit skills to tune behavior.

### Token spend

- Reduce the text in the files without losing any rule, so every agent reads
  less. A smaller `/setup-hstack` budget is not the chosen lever.
- The owner rewrites each file by hand and chooses which files to skip.
- Start with the files hStack wrote itself. Leave the files that are identical
  to pstack untouched.
- Compress a pstack-derived file only if the measurement ranks it among the
  most expensive, and then one file at a time. Each such file must be merged by
  hand at every later pstack update.
- Keep plain full sentences. Use no symbols, abbreviations or telegraphic
  shorthand.
- Set no percentage target. Cut each file as far as the check below allows.
- Measure before and after, on the same kind of task.
- A lighter route for small tasks waits for the measurement. It would move the
  router away from pstack's design, so it needs the numbers first.

### Adding a skill

- A new skill starts project-local, in the project's own skills folder
  (`.claude/skills/<name>/SKILL.md` in Claude Code). No hStack change is needed.
- Move a skill into hStack only when more than one project needs it. The
  bundled route is: follow `plugin/skills/hugues-mode/playbooks/authoring-a-skill.md`,
  add `plugin/skills/<name>/SKILL.md`, register it in
  `docs/upstream/consolidation.json`, run `scripts/seal_payload.py --accept <path>`,
  update the counts in `docs/TEST-COVERAGE.md` and `docs/CORE-RESTORATION.md`,
  then pass the five checks in the README.
- The only bundled additions for now are the Herdr page and the surface
  references. Other new skills wait for `/reflect` to propose them.

### Unattended runs

- Overnight and autopilot runs wait until the verification references work on
  the owner's app.

## Work order

1. Run the baseline measurement on the Mac.
2. Add the Herdr host page and detection.
3. Compress the files marked in the worklist.
4. Write the surface references: iOS, Android, .NET backend, desktop.
5. Run the second measurement.
6. Decide on the light route for small tasks.
7. Start overnight runs.

The model-role file and the `/reflect` and `/correct` habit need no development
and can start at any time.

## Measurement prompt

Run this in Claude Code on the Mac, inside one project where hStack was used.
It has not been tested: the session that wrote it had no access to the owner's
transcripts. Step 1 therefore makes the agent learn the transcript format
instead of assuming it.

```text
Read-only task. Do not edit, delete or upload anything. Do not print transcript text.

Goal: measure what hStack workflows really cost in tokens in this project.

1. Find this project's Claude Code transcripts under ~/.claude/projects/ (the
   folder named after this project's path). Open one .jsonl file and report
   which fields hold token usage (input, output, cache write, cache read) and
   how subagent turns are marked or stored. Stop and tell me if you cannot
   find usage fields.
2. Select the sessions from the last 14 days where the user typed
   /hugues-mode or another hStack skill. List them by date and first
   user request (first 80 characters only).
3. For each selected session, write a small script that sums tokens, split into:
   - main agent vs subagents
   - input, output, cache write, cache read
   Also record which hStack playbook the session followed, the number of
   subagents spawned, and the model each one ran on.
4. For each session, list the 10 largest file reads under the hStack plugin
   folder (path and bytes), and how many times each file was read across
   the main agent and all subagents.
5. Report one table per session, then a summary: median tokens per playbook,
   share spent by subagents, share spent re-reading hStack instruction files,
   and the five files that cost the most in total.

Say plainly what you could not measure. Give counts only, never guesses.
```

## Compression procedure

For each file the owner marks `compress`:

1. The agent lists every rule in the original file. A rule is any requirement,
   decision or condition that changes what an agent does.
2. The owner rewrites the file by hand.
3. A fresh agent that sees only the short version confirms each listed rule is
   still there. It reports the rules it cannot find. It never rewrites the text.
4. For `plugin/skills/hugues-mode/SKILL.md`, also run the blind `eval` playbook,
   because that file decides every route.
5. The agent runs `python3 scripts/seal_payload.py --accept <path>` and the five
   checks in the README.

The existing tests pin hashes and a few required phrases. They do not catch a
dropped rule, which is why step 3 exists.

## Compression worklist

Sizes are bytes at commit `2515e9e`. Fill the Decision column with `compress`
or `skip`. Add the cost ranking after the baseline measurement.

### Group A: in scope now

These are the files hStack wrote itself, plus the router, help and setup
skills, which carry hStack's own changes. Paths are relative to `plugin/`.

| File | Bytes | Decision |
|---|---:|---|
| `skills/hugues-mode/SKILL.md` | 20,825 | |
| `skills/hugues-help/SKILL.md` | 20,127 | |
| `adapters/host-tools.md` | 17,320 | |
| `skills/hugues-mode/references/mobile-lanes.md` | 13,876 | |
| `adapters/native-execution.md` | 13,697 | |
| `skills/setup-hstack/SKILL.md` | 11,387 | |
| `adapters/host-workers.md` | 10,124 | |
| `adapters/mobile-workflows.md` | 7,619 | |
| `adapters/host.md` | 6,863 | |
| `adapters/hosts/orca.md` | 5,941 | |
| `adapters/hosts/cursor.md` | 5,608 | |
| `skills/hugues-mode/references/jev-drive.md` | 5,389 | |
| `skills/hugues-mode/references/evidence-guide.md` | 5,105 | |
| `adapters/host-workflow-tools.md` | 4,989 | |
| `skills/hugues-mode/playbooks/mobile-proof.md` | 4,550 | |
| `skills/swift-best-practices/SKILL.md` | 3,654 | |
| `skills/hugues-mode/references/evidence-template.md` | 3,597 | |
| `skills/hugues-mode/playbooks/kmp-bridge-change.md` | 3,522 | |
| `skills/kotlin-best-practices/SKILL.md` | 3,491 | |
| `skills/hugues-mode/playbooks/cmp-two-target-change.md` | 3,405 | |
| `adapters/host-mobile-languages.md` | 3,389 | |
| `skills/hugues-mode/playbooks/build-doctor.md` | 3,385 | |
| `skills/create-verification-skill/references/project-skill-template.md` | 3,221 | |
| `adapters/host-special-skills.md` | 3,042 | |
| `skills/hugues-mode/references/mobile-forensics.md` | 3,025 | |
| `skills/hugues-mode/references/mobile-review.md` | 2,849 | |
| `adapters/host-helper-setup.md` | 2,124 | |
| `skills/kotlin-best-practices/references/native-interop.md` | 1,972 | |
| `skills/setup-hstack/references/cursor-models.md` | 1,890 | |
| `skills/kotlin-best-practices/references/cmp.md` | 1,823 | |
| `adapters/hosts/README.md` | 1,618 | |
| `skills/swift-best-practices/references/uikit.md` | 1,591 | |
| `skills/kotlin-best-practices/references/android-compose.md` | 1,545 | |
| `skills/swift-best-practices/references/swiftui.md` | 1,484 | |
| `skills/kotlin-best-practices/references/kmp.md` | 1,373 | |
| `adapters/host-publication.md` | 1,286 | |
| `adapters/host-typescript.md` | 603 | |
| `adapters/mobile.md` | 544 | |
| `skills/hugues-mode/references/host-notes.md` | 179 | |
| **Total, 39 files** | **208,032** | |

### Group B: derived from pstack, compress only if the measurement ranks them high

These differ from pstack 0.15.36 but follow its text. Paths are relative to
`plugin/`.

| File | Bytes |
|---|---:|
| `skills/hugues-mode/playbooks/multi-phase-plan.md` | 13,715 |
| `skills/statechart/SKILL.md` | 9,350 |
| `skills/technical-writing/SKILL.md` | 9,343 |
| `skills/why/SKILL.md` | 9,258 |
| `skills/hugues-mode/playbooks/babysit.md` | 7,791 |
| `skills/automate-me/SKILL.md` | 7,662 |
| `skills/maintain-formal-verification-skill/SKILL.md` | 7,262 |
| `skills/ketchup/SKILL.md` | 7,068 |
| `skills/hugues-mode/playbooks/autopilot-full.md` | 6,985 |
| `skills/show-me-your-work/SKILL.md` | 6,817 |
| `skills/create-verification-skill/SKILL.md` | 6,744 |
| `skills/recall/SKILL.md` | 6,588 |
| `skills/unslop/SKILL.md` | 6,077 |
| `skills/teach/SKILL.md` | 5,937 |
| `skills/create-formal-verification-skill/SKILL.md` | 5,876 |
| `skills/architect/SKILL.md` | 5,830 |
| `skills/hugues-mode/playbooks/opening-a-pr.md` | 5,598 |
| `skills/reflect/SKILL.md` | 5,467 |
| `skills/benchmark-checklist/SKILL.md` | 5,252 |
| `skills/maintain-verification-skill/SKILL.md` | 5,209 |
| `skills/arena/SKILL.md` | 5,012 |
| `skills/make-bot-ui/SKILL.md` | 4,893 |
| `skills/hugues-help/references/recipes.md` | 4,706 |
| `skills/hugues-mode/playbooks/hillclimb.md` | 4,508 |
| `skills/hugues-mode/playbooks/shipping.md` | 4,438 |
| `skills/figure-it-out/SKILL.md` | 4,377 |
| `skills/ketchup-video/SKILL.md` | 4,137 |
| `skills/blast-radius/SKILL.md` | 4,106 |
| `skills/hugues-mode/playbooks/bug-fix.md` | 3,913 |
| `skills/hugues-help/references/prompting.md` | 3,719 |
| `skills/tdd/SKILL.md` | 3,393 |
| `skills/hugues-mode/playbooks/worktree-cleanup.md` | 3,324 |
| `skills/hugues-mode/playbooks/refactoring.md` | 3,316 |
| `skills/interrogate/SKILL.md` | 3,248 |
| `skills/swarm/SKILL.md` | 3,078 |
| `skills/typescript-best-practices/SKILL.md` | 3,015 |
| `skills/how/SKILL.md` | 2,984 |
| `skills/no-comments/SKILL.md` | 2,959 |
| `skills/hugues-mode/playbooks/feature.md` | 2,871 |
| `skills/correct/SKILL.md` | 2,728 |
| `agents/hugues-comment-sicko.md` | 2,581 |
| `agents/hugues-agent.md` | 2,477 |
| `skills/hugues-mode/playbooks/autonomous-run.md` | 2,004 |
| `skills/hugues-mode/playbooks/perf-issue.md` | 1,551 |
| `skills/hugues-mode/playbooks/runtime-forensics.md` | 1,521 |
| `skills/hugues-mode/playbooks/autopilot-stack.md` | 1,127 |
| `skills/sharpen/SKILL.md` | 911 |
| `skills/in-your-own-words/SKILL.md` | 565 |
| `skills/bro/SKILL.md` | 517 |
| **Total, 49 files** | **231,808** |

### Not on the worklist

- 93 markdown files are byte-identical to pstack 0.15.36 once the
  three renames are applied. They stay untouched.
- `skills/control-cli/SKILL.md`, `skills/control-ui/SKILL.md` and
  `skills/deslop/SKILL.md` come from Cursor's cursor-team-kit. They stay
  untouched.

## Open facts to gather

- **Herdr mechanics.** On the Mac, inside a Herdr pane, record which
  environment variables Herdr sets and how it creates worktrees and panes. The
  Herdr page cannot be written without this.
- **Real token cost.** Unknown until the baseline measurement runs.
- **Codex availability.** Decides whether the judge pool has a true
  other-family judge.

## Not decided

- Whether the light route for small tasks is built at all.
- Which pstack-derived files, if any, get compressed.
- Which files in Group A the owner skips.
