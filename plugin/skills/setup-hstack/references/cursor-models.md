# Cursor model roles

`setup-hstack` writes `.hstack/models.md` for the host it runs in. This file
covers Cursor.

If `.hstack/models.md` is absent and `.huguesstack/models.md` exists, read the legacy file and tell the user to move it.

## Free plan

Per Cursor's loader; not observed in the IDE: on Cursor's free plan the IDE
exposes no per-model choice to the agent tool, so
the detected model set is empty and every role stays on `inherit-parent`. P1
found `model` stripped for plugin agents. Write
the role lines with `inherit-parent` as the only alternative, keeping the
budget's effort on each line, and say that the free plan offers no model
choice.

## Paid plan

Per Cursor's loader; not observed in the IDE: on a paid plan the IDE exposes
model ids the agent tool accepts. Detect them
from the agent tool's own schema in the session, the same way step 1 detects
them in Claude Code, and write each role's first alternative as the detected
id that matches its tier, followed by its effort. Keep the Claude and Codex
alternatives after it, so the same file still serves the other hosts:

```
judgment and prose: claude-opus-5-5 high or gpt-6-astra high
```

When Cursor's detected id differs from the Claude and Codex ids, put Cursor's
first, because a host runs the first alternative its agent tool accepts:

```
judgment and prose: <cursor-id> high or claude-opus-5-5 high or gpt-6-astra high
```

## What a Cursor role value cannot say

A Cursor plugin agent runs in the foreground, so a role value does not make a
worker run in the background. A value names the model and the effort only.

Cursor's `inherit-parent` means the parent chat model, and it is valid on every
host. A role that stays on it needs no detected id.

Never write a Cursor model id the agent tool did not list. A role whose
alternatives are all unconfirmed is written with `inherit-parent` and reported
as unverified, the same as the other host's alternatives in step 4.
