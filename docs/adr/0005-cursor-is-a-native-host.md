---
status: accepted
---

# Cursor is a native host

Cursor joins Claude Code and Codex as hStack's third native host. One tree, one plugin, three hosts. This ADR records the decisions that make that true and the gaps that come with it. It supersedes the Claude-Code-and-Codex-only scope in [ADR 0004](0004-adapters-for-ades-and-agents.md).

## The decisions

1. **Cursor is a native host.** The identity line reads "hStack is pstack for mobile development, running in Claude Code, Codex and Cursor." A Cursor user installs the plugin, sees its skills and runs `/hugues-mode`, `/hugues-help` and `/setup-hstack`.
2. **The only Cursor surface is the Cursor IDE.** The Cursor CLI (`agent`), Cloud Agents, the Cursor SDK, T3 Code's Cursor provider and Bugbot are out of scope. hStack does not document, support or test through them.
3. **One tree, one source.** A `.cursor-plugin/` manifest pair points at the existing `plugin/skills/` and `plugin/agents/`. No generated tree, no copied bodies. Pick exactly one route: **A**, you already use hStack in Claude Code, so install nothing in Cursor and Cursor loads hStack from Claude Code's install; or **B**, you don't use Claude Code, so hold a copy of this tree's `plugin/` folder at `~/.cursor/plugins/local/hstack`. One hStack source at a time: a user who holds route B's local copy *and* keeps hStack enabled in Claude Code gets every shared skill registered twice, because Cursor loads the Claude plugin cache as well as `~/.cursor/plugins/local/` and de-duplicates within one plugin rather than across plugins. Both halves of that observation come from one lab session on 2026-10-30 with both sources present, observed in Cursor 3.27.22 with a third-party auth extension: that session loaded `hstack` from the local copy (`loadUserLocalPlugin`) and from `~/.claude/plugins/cache/hstack/hstack/0.5.6` (`loadClaudePlugin hstack@hstack`), and ran the `host-detect.sh` hook once per copy. Route A is expected, not proven: it is checked at the end, on the released plugin, with hStack on in Claude Code and no local copy, so the README marks it expected and this ADR records it as a gap. The README's Cursor section names pstack as the first thing to remove, since 55 of hStack's 63 skill names are shared with it.
4. **The proof environment is the owner's Cursor.** Proof runs in the owner's own Cursor IDE, observed in Cursor <version> with a third-party auth extension; stock Cursor not observed. Every Cursor claim in the README, the PR body and the 0.5.7 release notes is worded the same way. Stock Cursor is a gap, and the free plan without the extension is a gap. A feature that needs a paid Cursor plan keeps the skip line, and it is skipped on every host, including Cursor. A free feature that a lane exercises is simply native in Cursor.

## The gaps

These are not observed in the Cursor IDE. Each one is a claim hStack does not
make until a run in the IDE shows it.

- **Subagents are not observed in the Cursor IDE.** No lane ran a read-only
  Explore subagent, and no lane confirmed that a Cursor plugin subagent leaves
  the working tree clean.
- **The paid-feature skip line is not observed in the Cursor IDE.** No lane
  asked for a paid Cursor feature and read the line it printed.
- **The Swift skill is not observed in the Cursor IDE.** No lane loaded
  `swift-best-practices` on a Swift task.
- **`recall` is not observed in the Cursor IDE.** No lane found an earlier
  chat in Cursor's transcripts. The slug rules below come from the observed
  on-disk layout, not from a run of the skill.
- **Route A is not observed in the Cursor IDE.** Cursor loading hStack from
  Claude Code's install is expected, and it is checked at the end, on the
  released plugin, with hStack on in Claude Code and no local copy. Until
  then the README marks it expected.
- **Stock Cursor is not observed.** Every observation here comes from Cursor
  3.27.22 with a third-party auth extension. The free plan without that
  extension is unobserved too.

Two lanes moved from gaps to observed, and the transcripts are the evidence.

- **The install shows up once, with no duplicate names.** On 2026-10-30 the
  owner counted 63 hStack skills in the Cursor IDE's `/` list, no name twice,
  with hStack listed once, from the local copy. Cursor's plugin log carries
  the load side: with hStack off in Claude Code, one reload holds a single
  `loadUserLocalPlugin hstack` line and no `loadClaudePlugin hstack@hstack`
  line. The `/` list itself is an IDE surface, so the count is the owner's
  reading and the log is the corroboration.
- **`setup-hstack` is observed in the Cursor IDE.** On 2026-10-30 a
  `/hugues-help` session read the setup skill and the Cursor model roles,
  asked for a budget and a model per role, and wrote `.hstack/models.md`. The
  transcript is `af1aa92a-1e13-414d-afd6-65fc11841389`.
- **The `hugues-agent` delegate is observed in the Cursor IDE.** On
  2026-10-30 a `/hugues-mode` session routed to `bug-fix` and dispatched one
  `Task` call with `subagent_type: "hugues-agent"`. The delegate ran in the
  foreground, reported back, and the parent verified its work against the
  committed file. The transcript is `8cf8c8f7-771d-4dd3-8452-90144dd23ce9`
  and the subagent's is `a0514e09-d859-41e1-8ae6-1cc53cf1db54`.

Both runs also produced two observations that change what hStack states.

- **The agent tool exposes a model id and no effort parameter.** The setup
  session read the agent tool's own schema and found one real model id plus
  `inherit`, and no effort setting. The earlier claim that the detected model
  set is empty on the free plan does not survive that run, so the
  [model roles reference](../../plugin/skills/setup-hstack/references/cursor-models.md)
  now tells a Cursor session to detect the ids from the schema instead.
- **Cursor's shell adds a commit trailer.** The shell wrapper adds a
  `Co-authored-by` trailer to every `git commit`, and `git commit --amend`
  adds it again. Never bypass hooks to remove it: if a project forbids the
  trailer, say so and leave the commit to the user. The
  [Cursor page](../../plugin/adapters/hosts/cursor.md) says so.

One more observation, with no change to hStack: the `/hugues-help` session
ran `setup-hstack` and the repository's test suite itself, where the skill
offers the user the choice to type `/setup-hstack` instead.

## Why

Cursor is where a lot of the mobile work already happens, and hStack was invisible there. pstack was built for Cursor, so Cursor is not a new host so much as the host hStack was forked from. The fork is what let the third host be cheap: the plugin tree, the skills and the playbooks were already Cursor-shaped, so adding Cursor is a manifest and an adapter rather than a rewrite.

The paid-plan boundary is the real constraint. Cloud Agents, the Cursor SDK and Bugbot all need a paid plan, and T3 Code's Cursor provider needs one too, so none of them can carry the proof. That is why the only surface is the IDE on the free plan, and why a paid feature keeps a skip line rather than becoming a claim.

The CLI is excluded for the same reason of evidence. The CLI shares the plugin loader, the skill registry and the transcript store with the IDE, so it is a good guide while building. It is not the surface hStack supports, and a CLI run is not evidence about the IDE.

## The background gap

A Cursor plugin agent runs in the foreground. Observed in the IDE on
2026-10-30: a `Task` call with `subagent_type: "hugues-agent"` ran one helper
task to completion inside the parent's turn, and the delegate's transcript
sits beside the parent's under `subagents/`. Per Cursor's loader; not observed
in the IDE: Cursor's own plugin-agent conversion drops the background flag on
the way to the Task call, so `is_background: true` would be inert, and no
hStack agent carries a read-only field: Claude Code also reads
`permissionMode`, and `readonly` is not a value Claude Code accepts.

This is a written gap, not a field. The [workers adapter](../../plugin/adapters/host-workers.md)
says so, and a Cursor workflow that expects a background delegate dispatches
the worker and waits for its result in the same turn.

## The transcript gap

A Cursor transcript carries no `cwd` and no record-level timestamp, and it may carry no tool results. So a Cursor source resolves only an absolute path, gets its recency from the transcript file's modification time, and cannot claim to see what a tool returned. The [tools adapter](../../plugin/adapters/host-tools.md) states those limits, and the activity reader reports them as a coverage gap rather than as proof that nothing happened.

A Cursor transcript's project slug has two forms, because Cursor ships more than one way to compute it. Every `/` becomes a hyphen, and a segment's own `_` is written either as `-` or as `_`, so one workspace can have two slug directories. A segment's own `-` stays `-`, a long path is truncated with a hash suffix, and some chats use a slug that is not a path name at all. A slug is lossy, so hStack never reverses one into a workspace path: two different workspaces can share a slug, one workspace can have two slugs, and a slug may name no path. The [recall skill](../../plugin/skills/recall/SKILL.md) states the rules and says to look for the other form before concluding a history is gone.

## Consequences

- The identity line and the glossary name three hosts. Claude Code and Codex keep their behavior: no edit in this change alters what those hosts load or do.
- The [host adapter](../../plugin/adapters/host.md) splits its Cursor-only features into free and paid. The paid rows keep the skip line format `Skipped in <host>: <step>. <reason>.`
- The [setup skill](../../plugin/skills/setup-hstack/SKILL.md) points at [cursor-models.md](../../plugin/skills/setup-hstack/references/cursor-models.md). A Cursor session detects the model ids from the agent tool's own schema, and the effort token is recorded but not applied, because the tool has no effort setting.
- The activity reader lives in [activity.py](../../plugin/adapters/runtime/activity.py) and covers three providers. It reads Cursor's `{"role", "message"}` envelope, its `text` and `tool_use` blocks and its `turn_ended` marker, and it treats any other shape as unreviewed and holds coverage.
- Runtime behaviour in the IDE was unobserved until the owner ran the lanes, and three lanes have now run. `setup-hstack` and the `hugues-agent` delegate are observed. The read-only subagent, the paid-feature skip line, the Swift skill and `recall` are still not observed in the Cursor IDE, and the release notes carry those gaps. Route A is expected until the final check on the released plugin proves it: stock Cursor is unobserved, and the free plan without the third-party auth extension is unobserved.
