# hStack 0.5.10

## What's new

Version 0.5.10 moves the pin from upstream 0.15.36 to 0.15.43 (`2f87c85`) and
follows upstream fully, model routing included. Upstream changed 80 files,
added 2 and removed 24. The skill count stays at 63. The generic playbooks go
from 23 to 22, and the four mobile playbooks are unchanged.

- **Opus-first routing.** Code, prose and judgment roles start on
  `claude-opus-5-5` at `xhigh`, and light work runs at `high`. No role runs
  above `xhigh`. `claude-fable-5-2` runs only when you ask for it, or after two
  Opus runs of the same brief fail their check. Review panels seat Fable,
  Opus and a Codex model at `high`. The Frontier tier and the `hardest tasks`
  role from 0.5.9 are retired, and the `unlimited` budget becomes `large`.
- **Workers read `worker.md`.** Every started worker reads
  `hugues-mode/worker.md` for its rules. It never stops to ask a person a
  question, and it holds only for a failing run. Its report ends with
  **Concerns** and **Deviations**. The coordinator keeps the interview rule, and
  the mobile hold stays a mobile adaptation.
- **Shorter skills.** The 14 shortened principles and the statechart fixes come
  over verbatim. `how`, `why`, `architect` and `reflect` are single files.
  Their 21 reference files and their worker roles are retired, and `architect`
  sends a large or contested design to `arena`. `unslop`, `technical-writing`,
  Babysit, Opening a PR and the router are shorter, as they are upstream.
- **Removed: Orchestrate and the plan checker.** Multi-phase plan follows
  upstream's five steps. The `plan-check` helper verb, `check-plan.mjs` and their
  tests are gone, and a draft that still runs the checker is refused.
- **Activity reader fixed (#151, PR #157).** The worktree audit reads Claude
  Code 2.1.31x transcripts again, and a manifest that lists `omp` beside a
  complete Claude source now holds instead of reporting complete.
- **ADR 0006.** hStack keeps what upstream lacks only for a host or ADE adapter,
  a stack adapter for any tech stack, or a fix for friction seen in the owner's
  runs. It replaces ADR 0001's mobile-only exception.
- **User guides.** The guide chapters, the HTML user guide and the README
  describe the new routing, the 22 playbooks, `worker.md` and the single-file
  skills.

## Upgrade

Update or reinstall the plugin on each host, as in the
[0.5.8 upgrade](RELEASE-0.5.8.md#upgrade), then restart the Claude Code process
and start fresh sessions. Check that the resolved payload reports 0.5.10.

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Run `/setup-hstack` again in each project that already has `.hstack/models.md`.
It reads `budget: unlimited` as `large`, and it drops the `hardest tasks` line and
the retired `how`, `why`, `architect` and `reflect` role lines without asking. It
says so once in its output. A role you changed from its default keeps your
value, including an old Sonnet line. To take every new default, delete the file
first.

`/orchestrate` and `plan-check` no longer exist. Use Figure it out or
Multi-phase plan.

The Bun install key changes, because `hugues-mode/scripts/package.json` dropped
check-plan from its test command. `bun.lock` is unchanged.

## Validation

Static checks establish source and wiring contracts only. They ran at the sync
head in a `python:3.14` container.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 594 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests, installed payload and the upstream-name guard. |
| `python3 scripts/check_core.py` | PASS, 551 archive files, 22 core playbooks | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 551 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

The `hugues-mode` helper's Bun suite (73 tests, down from 81 because the
check-plan tests are gone) and its strict type check pass on a copy of the
release tree, with the lockfile frozen.

One host load was observed on Claude Code 2.1.327, with `claude -p
--plugin-dir <sync head>/plugin` on `claude-haiku-5-5`. Only `setup-hstack` was
model-invocable, and `hugues-agent` was registered. `/hstack:hugues-mode` listed
22 generic playbooks without Orchestrate and named `hugues-mode/worker.md` as
the started worker's rules file.

## Known gaps

- No Codex or Cursor session ran for this release. No full playbook run and no
  real setup migration of an existing `unlimited` file was observed.
- The statechart TypeScript suite needs TLC and Java and did not run.
- The update from 0.5.9 to 0.5.10 is unobserved on every host.
- A pure hStack addition with no upstream file, such as a mobile playbook or a
  host page, has no ledger row yet. ADR 0006 records its reason until the ledger
  gains a row type for it.
- The gaps listed in the [0.5.9 notes](RELEASE-0.5.9.md#known-gaps) carry over
  unless this page says otherwise.
