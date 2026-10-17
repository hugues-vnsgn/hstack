# hStack

hStack is pstack for mobile development, running in Claude Code and Codex.
pstack is poteto's Cursor plugin: a router mode matches a task to a playbook,
the playbook calls skills and principles as its steps fire, and the work ends in
evidence. hStack preserves its upstream source in a nondiscoverable provenance archive
and authors one canonical native body per skill. Read the
[pstack guide](docs/pstack/guide/README.md) and [glossary](docs/GLOSSARY.md).

## Where an edit goes

- `plugin/skills/<name>/SKILL.md` is the authored canonical skill. Public names
  and paths are compatibility surfaces. Owned references load only when needed.
- `plugin/adapters/` contains host mechanics, mobile applicability and the
  conservative read-only activity audit. Do not bypass native skill controls.
- `provenance/upstream/` retains exact upstream bytes outside runtime discovery.
  `docs/upstream/consolidation.json` maps every original responsibility and binds
  the installed inventory. `scripts/seal_payload.py` updates reviewable receipts
  and bootstrap hashes after intentional edits; it is not a consumer repair tool.
- Current candidate tests and frozen historical release tests are separate.
  Do not edit frozen archives to make current failures pass.

## Checks

Run every command in [Reference and maintenance](README.md#reference-and-maintenance)
from inside your worktree before each commit; all must pass. Adding or removing
a test changes the counts quoted in [test accounting](docs/TEST-COVERAGE.md) and
[core restoration](docs/CORE-RESTORATION.md). No check catches stale counts, so
update them in the same commit.

Static checks prove source and wiring only. A claim about host or mobile
behavior in docs, release notes or a PR body needs *observed* evidence from that
host, domain and target. Write anything unobserved as a gap.

## Worktrees and branches

Every task that edits files runs in its own worktree on its own branch: one
worktree, one branch, one writer. The primary checkout stays on `main` as the
clean base everyone branches from. Read-only tasks stay where they are.

1. **Check where you are.**

   ```sh
   git rev-parse --path-format=absolute --git-dir --git-common-dir
   git branch --show-current
   ```

   Two different paths mean you are in a linked worktree, often one your host
   made: keep it and its branch. If the branch line is empty (detached HEAD),
   run `git switch -c <branch>` there, named per step 2, before the first edit.
   Two equal paths mean the primary checkout: continue.
2. **Name the branch** `fix/<slug>` for a defect fix and `feat/<slug>` for
   everything else, with a short kebab-case slug: `fix/plan-check-spaces`,
   `feat/android-proof-lane`.
3. **Create the worktree beside the repository**, at `<repo>.worktrees/<branch>`.
   `scripts/check_plugin.py` walks every file under the repository root, so a
   worktree inside it (`.worktrees/`, `.claude/worktrees/`) makes
   `check-plugin.sh` fail in the primary checkout.

   ```sh
   root=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
   git fetch origin
   git worktree add --no-track -b feat/<slug> "$root.worktrees/feat/<slug>" origin/main
   ```

   `--no-track` keeps `origin/main` from becoming the branch's upstream; the
   first push sets the real one with `git push -u origin <branch>`. If the
   branch already exists, `git worktree list` shows whether a worktree holds it:
   enter that one, or else run `git worktree add "$root.worktrees/<branch>" <branch>`.
4. **Move in.** `cd` into the worktree, or use the host's enter-worktree tool,
   and run every later command, edit and check from there. Done when
   `git worktree list` shows your path on your branch and `git status` there is
   clean. Report the path, branch and base commit.

Parallel writers (arena candidates, swarm workers, subagents that edit) each get
their own worktree the same way, on branch `<your-branch>-<n>` based on your
branch's HEAD instead of `origin/main`. Commits go on the worktree's own branch.

`docs/planning/` is gitignored, so it exists only in the primary checkout; read
it there by absolute path. It and the local `private/planning-snapshots` branch
hold the owner's private planning and stay on this machine.

After the owner merges, clean up with `git worktree remove <path>`, then
`git branch -d <branch>`. Both refuse when work would be lost; on a refusal,
stop and report it to the owner.

## Publishing

Pushing, opening a PR, merging and releasing each need the owner's go-ahead for
the current task. An operator's autopilot grant is that go-ahead for the run's
PRs, within the playbook's gates.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on hugues-vnsgn/hstack, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `docs/GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.
