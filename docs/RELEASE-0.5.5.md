# hStack 0.5.5

## What's new

Version 0.5.5 moves hStack's pstack baseline from 0.15.25 to 0.15.32. The pin is upstream `main` at `e73df471`, which is 0.15.32 plus eight later fixes. The release adds four user-only skills, takes pstack's rewrites of existing skills, and ships a rewritten user guide.

- **pstack 0.15.32 baseline ([#133](https://github.com/hugues-vnsgn/hstack/pull/133)).** The pin moves from `6ce45c59` to `e73df471`. The ledger now accounts for 200 upstream files, with 31 added, 43 changed and none removed. The later fixes touch `watch-pr`, `orch`, `check-plan`, swarm and reflect.
- **Four user-only skills (#133).** `create-formal-verification-skill` writes a project skill that formally verifies the code where a bug costs most and tests reach least. `maintain-formal-verification-skill` brings that verification back in line after the code changes. `statechart` draws a system's states as a Mermaid chart from a TLA+ model, with each bug as a numbered path. `ketchup-video` catches you up like `ketchup`, with a short silent video of slides. Type them by name. They stay out of the host's skill list, so only `setup-hstack` appears there. The skill count goes from 59 to 63.
- **Changed skill behavior (#133).** `/sharpen` returns a rewritten prompt and no longer does the task. `ketchup` lists every item waiting on you, with what you need to decide it. `setup-hstack` makes a one-time offer to set up formal verification. `reflect` never edits a skill inside the plugin cache. Upstream rewrote six principle skills and parts of `swarm`, `interrogate`, `correct` and `typescript-best-practices`.
- **User guide ([#134](https://github.com/hugues-vnsgn/hstack/pull/134)).** [docs/hstack-user-guide.html](hstack-user-guide.html) adds Part II, "Lead the team". It covers briefing workers, designing before planning, picking the team shape, running the team in Claude Code and reviewing like a lead, with poteto's worked examples. Every claim about a host carries a label that says whether hStack observed it.
- **Seal fix (#133).** `scripts/seal_payload.py` sorts files by POSIX path, the same order `check_core.py` uses. The two orders differed for `ketchup/` and `ketchup-video/`, so every reseal had failed.

The native build and test helpers, the mobile adapters, the bundled Swift and Kotlin guidance, the agents, and the Bun dependency inputs (`package.json`, `bun.lock`) are unchanged from 0.5.4.

## Upgrade

Update or reinstall the plugin on each host. Restart the Claude Code process after updating, then start a fresh session. A process started before the update can keep loading its old cached copy. Start a fresh Codex session too. The plugin remains `hstack@hstack`, Claude commands keep `/hstack:`, and the setup skill remains `setup-hstack`.

On Claude Code, refresh the configured marketplace and update the plugin:

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

For a new install, use `claude plugin install hstack@hstack`. Once the release tag exists, a session-only checkout can use the `v0.5.5` tree with `claude --plugin-dir "/absolute/path/to/hstack/plugin"`.

On Codex, refresh the configured marketplace and install its current plugin payload:

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

Check that the resolved payload reports 0.5.5. On the maintainer machine on 2026-10-26, the Claude Code cache at `~/.claude/plugins/cache/hstack/hstack/0.5.4` matched the `v0.5.4` tag. The Codex cache with the same 0.5.4 label had already refreshed to `main` at `af2c1a7`, so it held this release's skills under the old version number. The update from 0.5.4 to 0.5.5 has not been observed on either host.

Each new copy needs its Bun dependencies once before `watch-pr` or `orch` runs. Follow [0.5.4's setup command](RELEASE-0.5.4.md#upgrade) with `<plugin>` set to the 0.5.5 copy. The `package.json` and `bun.lock` inputs are unchanged from 0.5.4.

For upgrades from 0.4.x, also follow [0.5.0's settings and plan migration](RELEASE-0.5.0.md#upgrade-from-04x).

## Validation

The release tree collects 540 top-level unittest cases, the same count as 0.5.4. Neither #133 nor #134 added a test. Static checks establish source and wiring contracts only.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 540 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests and installed payload. |
| `python3 scripts/check_core.py` | PASS, 200 archive files | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 200 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

`claude plugin validate --strict` passes on `plugin` and on the marketplace.

At #133, `bun test` on a scratch copy of the `hugues-mode` helpers passed 102 of 102 (watch-pr, orch and check-plan). No helper changed after that, so it was not rerun.

## Known gaps

- No host has run the four new skills. The `statechart` test suite has not run, because it downloads TLC and Java.
- No host run has used the new `/sharpen` behavior or the formal-verification offer in `setup-hstack`.
- The update from 0.5.4 to 0.5.5 is unobserved on both hosts.
- Most of the guide's Part II is labeled "Defined, not yet observed". hStack has no recorded run of Orchestrate, the autopilots, the Prototype or Multi-phase plan playbooks, or `/recall` over past transcripts.
- `docs/pstack/guide/07-overnight.md` and `09-make-it-yours.md` still mention Cursor in three places.
- Every [0.5.4 known gap](RELEASE-0.5.4.md#known-gaps) still applies.
