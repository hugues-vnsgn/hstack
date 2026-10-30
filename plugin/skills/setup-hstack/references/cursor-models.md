# Cursor model roles

`setup-hstack` writes `.hstack/models.md` for the host it runs in. This file
covers Cursor.

If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it.

## The detected models

Observed in the IDE on 2026-10-30: the agent tool's own schema listed one real
model id plus `inherit`, and it has no effort parameter. Detect the ids from
that schema in the session, the same way step 1 detects them in Claude Code,
and write each role's first alternative as the detected id that matches its
tier, followed by its effort.

The agent tool has no effort setting, so the effort token in a role value is
recorded but the worker runs at the host's effort. Say so in the report.

Keep the Claude and Codex alternatives after the detected id, so the same file
still serves the other hosts:

```
judgment and prose: claude-opus-5-5 high or gpt-6-astra high
```

When Cursor's detected id differs from the Claude and Codex ids, put Cursor's
first, because a host runs the first alternative its agent tool accepts:

```
judgment and prose: <cursor-id> high or claude-opus-5-5 high or gpt-6-astra high
```

A Claude or Codex id that Cursor's agent tool does not accept is an
alternative it cannot run, so the roles holding it land on the detected id.
Say which roles that is.

## What a Cursor role value cannot say

A Cursor plugin agent runs in the foreground, so a role value does not make a
worker run in the background. A value names the model and the effort only.

Cursor's `inherit-parent` means the parent chat model, and it is valid on every
host. A role that stays on it needs no detected id.

Never write a Cursor model id the agent tool did not list. A role whose
alternatives are all unconfirmed is written with `inherit-parent` and reported
as unverified, the same as the other host's alternatives in step 4.
