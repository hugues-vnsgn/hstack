# Prepare installed Bun helpers

Before `watch-pr` or `orch`, inspect Bun and the loaded copy's dependency state.
Both helpers share `<plugin>/skills/hugues-mode/scripts`. Standard cache directories
are shown below. Use the loaded root from [workflow tools](host-workflow-tools.md)
for custom locations and versions.

| Host | Dependency directory |
|---|---|
| Claude Code | `~/.claude/plugins/cache/hstack/hstack/<loaded-version>/skills/hugues-mode/scripts` |
| Codex | `~/.codex/plugins/cache/hstack/hstack/<loaded-version>/skills/hugues-mode/scripts` |

For each newly installed copy, offer this one-time, owner-approved setup in a
session that can write that directory. Expand `<plugin>` to the absolute loaded
root before presenting or running the command. Run it only with installation
authority for that copy.

```sh
cd "<plugin>/skills/hugues-mode/scripts" && bun install --frozen-lockfile && bun "<plugin>/skills/hugues-mode/scripts/watch-pr/watch-pr" --help
```

The help call lets the unchanged bootstrap record its install key. If the key
is absent or stale, the bootstrap runs its own frozen install once more before
showing help. Require exit 0 and inspect both `node_modules/commander/package.json`
and `node_modules/.poteto-mode-tools-install-key`. The key must match the
SHA-256 of package.json, a NUL byte, and bun.lock, in that order. A standalone
`bun install --frozen-lockfile` does not write the key. Resume later helper calls
from the consumer directory, using the
[workflow command table](host-workflow-tools.md#resolve-bundled-commands-on-both-hosts).

If dependencies or the matching key are missing and the cache is not writable,
hold the dependent step. Report the exact expanded setup command as the gap,
with its dependency directory and required owner approval outside the sandbox.
Do not retry the helper or silently skip the step. Apply the same hold when
installation authority is absent. A missing Bun runtime remains a separate gap.
This setup grants no permission to publish, change host settings, or widen the
consumer sandbox.
