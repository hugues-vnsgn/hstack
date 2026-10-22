---
status: accepted
---

# hugues-mode is user-only

`hugues-mode` sets `disable-model-invocation: true`, and its Codex policy sets `allow_implicit_invocation: false`. The owner starts it by typing `/hstack:hugues-mode` in Claude Code or `$hugues-mode` in Codex. This is pstack's design. `poteto-mode` has been manual-only since 0.15.25, the current pin, and still is at 0.15.29. Its description names a style, not a list of triggers.

On 2026-10-08 hStack kept the router model-invocable while 48 other skills went user-only ([#21](https://github.com/hugues-vnsgn/hstack/issues/21)). The [#22 routing eval](../hugues-mode-router-eval.md) then saw it fire unprompted on 3 of 4 task prompts. On 2026-10-22 the owner chose pstack's design over that reach. Only `setup-hstack` stays model-invocable.

The decision has three parts.

- The description follows `poteto-mode`'s line: "hugues's agent style for mobile and engineering work", then the same style list and "Use for" clause. It is written for a person browsing the skill menu.
- `hugues-agent` no longer preloads the mode, because Claude Code cannot preload a `disable-model-invocation` skill into a subagent. It reads `hugues-mode/SKILL.md` from its parent's absolute path, else from a search of the installed plugins, as `poteto-agent` does. This replaces the base-directory step and "The preload stays" in [ADR 0002](0002-read-bundled-user-only-skills-by-path.md).
- `host.md` puts `hugues-mode` in the bundled user-only class, so an agent reads its SKILL.md by path. The native-only set is now `setup-hstack` plus consumer and external skills.

The same change drops the tool name from the router's question trigger. `AskUserQuestion` exists only in a Claude Code main session. Claude Code removes it from every subagent, and Codex's question tool is unobserved here. The trigger now says to ask the user. It keeps pstack's rule that a fact you can observe gets a prototype, not a question. On a product or preference call no experiment can settle, the agent interviews the user until they reach a shared understanding.

## Consequences

- A mobile task phrased without `/hugues-mode` no longer reaches the router. The owner or the worker brief names it.
- hStack's share of the per-turn skill list drops from two descriptions (352 characters) to one (116).
- A Codex worker brief names `$hugues-mode` or the mode's absolute path, since the implicit catalog entry is gone. `$hugues-mode` under the new policy is unobserved.
- Source checks prove the frontmatter, the policy file, the wording and the lint. On 2026-10-22, Claude Code 2.1.307 in print mode, with hooks and MCP off, listed only `hstack:setup-hstack` when asked for its `hstack:` skills on this branch, and both skills on `main`. That list is model-reported. Typing `/hstack:hugues-mode` still loaded the router.
- Unobserved: Codex under the new policy, a live `hugues-agent` reading the mode by path, and the interview trigger in a real run.
