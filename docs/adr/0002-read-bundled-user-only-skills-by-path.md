---
status: accepted
---

# Read bundled user-only skills by path

On Claude Code, hStack agents read a bundled `disable-model-invocation` skill as a file, the way pstack does. They never call the Skill tool on one. The flag keeps the skill list small. It does not restrict agents.

pstack marks `no-comments`, `technical-writing` and `unslop` user-only too. Its `poteto-agent` finds `poteto-mode/SKILL.md` on disk and reads every skill at `../<name>/SKILL.md`, so there is no invoke call to refuse. This is inferred from the agent's text. Cursor was not observed.

Claude Code leaves the Skill tool as the obvious move for a `/no-comments` step, and the tool refuses the call. Its answer tells the model to ask the user to run the skill and not to reach it any other way. In the BFSManifest lab runs (Claude Code 2.1.293), five `hugues-agent` owners made that call and none read the file afterward. Owners that read the three files by path first had no error ([#48](https://github.com/hugues-vnsgn/hstack/issues/48)). hStack made the call more likely than pstack did. `hugues-agent` started from a preloaded skill and said to invoke natively, and none of the sampled briefs carried the `hugues-mode` path.

The decision has three parts.

- `hugues-agent` finds `hugues-mode/SKILL.md` itself, as `poteto-agent` does. It uses its parent's absolute path, else the base directory Claude Code shows with the preloaded skill, else a search of the installed plugins. The preload stays.
- `host.md` and the `hugues-agent` header say that on Claude Code a bundled user-only skill is never a Skill-tool call. In a playbook, a router trigger or a plan, `/<name>` and "the **<name>** skill" mean reading `../<name>/SKILL.md` in full. The playbooks keep pstack's wording, and the adapter translates it.
- The playbook headers drop the hStack-only clause that held a step when invocation was unavailable or denied. pstack has no such clause, and a read does not depend on invocation.

Consumer and external skills stay native-only. Unavailable, disabled or denied native invocation still stops the dependent step.

## Consequences

- The owner's control over a bundled user-only skill is still enabling or disabling the plugin as a whole.
- A brief no longer has to carry the `hugues-mode` path. A path the parent gives still wins.
- Source checks prove the wording and the lint that guards it. They do not show how Claude Code behaves with it. A live owner-style run is the evidence, and it is recorded on the pull request.
- Codex wording is unchanged beyond the shared `host.md` paragraph. Its `hugues-agent` path is still unobserved here.
