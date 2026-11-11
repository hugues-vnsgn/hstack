# hStack 0.5.9

## What's new

Version 0.5.9 refines `setup-hstack` and names the product hStack everywhere a
user reads it. The pin stays at upstream 0.15.36, the skill count stays at 63,
and the native build and test helpers, the mobile adapters and the agents are
unchanged.

- **A Frontier model tier.** Setup's tier table gains `Frontier`, on
  `claude-fable-5-2` at `high` effort. Only the `hardest tasks` role uses it:
  `claude-fable-5-2 high or claude-opus-5-5 xhigh or gpt-6-astra high`. A host
  whose agent tool does not accept Fable runs the role on Opus, and setup says
  which alternative it dropped. Every other role keeps its 0.5.8 value. The
  `fable` alias now maps to `claude-fable-5-2`.
- **The verification offer is optional for every project.** Setup's step 7 checks
  for a project `verify-*` skill or an existing harness and offers once to
  generate one when neither exists. A mobile project keeps its 0.5.8 behaviour as
  one conditional paragraph: setup offers the `verify-<app>` recipe even when a
  harness exists, and declining holds dependent mobile proof.
- **Setup reads the host contract alone.** It no longer reads mobile
  applicability, because it routes no task.
- **Mobile is an optional adapter.** `AGENTS.md`, the glossary, the README and the
  user guide describe hStack as an agent workflow plugin for Claude Code, Codex
  and Cursor, with mobile development as one optional adapter.
- **One product name.** Product text says hStack. Where it means the project
  hStack is forked from, it says "upstream". The guide moved to
  [`docs/guide/`](guide/README.md), and the upstream MIT notice is now
  [`UPSTREAM-LICENSE`](../UPSTREAM-LICENSE), its text unchanged.
  `scripts/check_plugin.py` rejects the upstream name in product text; the
  upstream records, dated history and the scripts and tests that compare against
  upstream keep it.

The repository also vendors the owner's project skills under `.claude/` for
cloud sessions. They are not part of the plugin payload.

## Upgrade

Update or reinstall the plugin on each host, as in the
[0.5.8 upgrade](RELEASE-0.5.8.md#upgrade), then restart the Claude Code process
and start fresh sessions. Check that the resolved payload reports 0.5.9.

```sh
claude plugin marketplace update hstack
claude plugin update hstack@hstack
```

```sh
codex plugin marketplace upgrade hstack
codex plugin add hstack@hstack
```

A project that already ran setup keeps its `hardest tasks` line on Opus, because
a rerun keeps any role whose value differs from the default. To pick up the
Fable default, delete that line or the whole `.hstack/models.md`, then run
`/setup-hstack` again.

The Bun install key is unchanged from 0.5.8: neither `package.json` nor
`bun.lock` changed. One comment in `watch-pr/github.ts` changed.

## Validation

Static checks establish source and wiring contracts only. They ran at the release
head.

| Static release check | Result | Scope |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | PASS, 586 cases | Current source, installed adapters, helper contracts and historical restoration driver. |
| `./scripts/check-plugin.sh` | PASS, 63 skills | Plugin layout, manifests, installed payload and the upstream-name guard. |
| `python3 scripts/check_core.py` | PASS, 573 archive files | Canonical source and core workflow contracts. |
| `python3 scripts/upstream-diff.py check` | PASS, 573 ledger rows | Pinned upstream source and responsibility accounting. |
| `python3 scripts/check_whitespace.py` | PASS | Repository whitespace. |

The `hugues-mode` helper's Bun suite (81 tests) and its strict type check pass
on a copy of the release tree.

## Known gaps

- No host session ran for this release. Setup's new Frontier line, its dropped
  alternative report and the optional verification offer are static contracts,
  not observed runs.
- Fable availability is unobserved on Bedrock, Vertex, Codex and Cursor. The
  Opus alternative covers a host that does not accept it.
- The update from 0.5.8 to 0.5.9 is unobserved on every host.
- A copy installed before 0.5.9 links `hugues-help`'s guide pages to the old
  guide path on GitHub, which no longer exists on `main`.
- The gaps listed in the [0.5.8 notes](RELEASE-0.5.8.md#known-gaps) carry over
  unless this page says otherwise.
