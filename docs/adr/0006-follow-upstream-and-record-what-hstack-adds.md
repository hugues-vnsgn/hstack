---
status: accepted
---

# Follow upstream, and record what hStack adds

hStack follows upstream. It keeps or adds what upstream lacks only when the addition is one of three kinds, and each kept addition carries its reason, so a sync can be run mechanically.

This replaces the last paragraph of [ADR 0001](0001-follow-pstack-run-safety.md), which said to follow the original pstack and remove whatever pstack lacks unless it is a mobile adaptation. That rule named one exception, and hStack has since grown two more kinds of work that upstream cannot have: adapters for the hosts and ADEs it runs in ([ADR 0004](0004-adapters-for-ades-and-agents.md), [ADR 0005](0005-cursor-is-a-native-host.md)), and fixes for friction in the owner's own runs ([ADR 0002](0002-read-bundled-user-only-skills-by-path.md), [ADR 0003](0003-hugues-mode-is-user-only.md)). A rule with only a mobile exception could not say whether those stay.

## The rule

Upstream's text wins. When upstream cuts, renames or removes something, hStack follows. The only things hStack keeps or adds are these.

1. **A host or ADE adapter.** Names, paths and mechanics that map upstream's host onto Claude Code, Codex, Cursor, Orca or another host: the model file `.hstack/models.md` and the translation of upstream's model slugs to host model IDs, plugin cache and skill folders, the agent tool in place of upstream's `Task`, and the Orca terminal-only policy. An adapter maps mechanics and adds no gate or authority ([ADR 0004](0004-adapters-for-ades-and-agents.md)).
2. **A stack adapter, for any tech stack.** Guidance that makes upstream's workflow fit a stack upstream does not cover. Mobile is the first: the mobile routes, the Swift and Kotlin baselines and baseline paths in worker briefs, the mobile lanes and review lens. Web, backend or any other stack qualifies the same way, on the same terms: it adapts a workflow and does not fork it.
3. **A fix for friction observed in the owner's runs, cited by transcript or issue.** A change that stops a failure seen in a real run, with the transcript id or the issue number in its reason. An opinion or a guess is not enough. The router's interview rule ([ADR 0003](0003-hugues-mode-is-user-only.md)) and the by-path read of user-only skills ([ADR 0002](0002-read-bundled-user-only-skills-by-path.md)) are of this kind.

Anything else goes. A feature that only restates upstream, or that upstream has since cut, is removed in the sync that cuts it.

## Each kept item has a row and a reason

An adaptation of an upstream file is recorded in that file's row of the [upstream ledger](../upstream/README.md), with `port with adaptation` and a reason that names which of the three kinds it is and what upstream text it leaves alone. A merge then has one question per row: does the adaptation still have text to attach to? If yes, keep it. If upstream removed that text, the adaptation goes with it, unless it is a kind-two or kind-three item that still earns its place against the new upstream.

A change in a sync that upstream did not make has to name its kind. If it cannot, it does not ship.

## Consequences

- The 0.15.43 sync follows upstream on everything the owner chose to follow: model routing (Opus 5.5 at xhigh, no role above xhigh, Fable only on request or after two failed runs), the single-file `how`, `why`, `architect` and `reflect`, the five-step Multi-phase plan, and the deletion of Orchestrate and of the plan checker. The retained-family receipts record that these skills are now upstream's single files and that the retained references and worker roles are retired.
- What stays is kind-one and kind-two work: host names and paths, the models file with its ` or ` alternatives, the Orca policy, the mobile routes and their ten-lane rule re-pointed at the new plan, the Swift and Kotlin brief paths, and the arena cross-judge fallback to a different model where the host offers no other vendor. The interview rule and the by-path read stay as kind three.
- The ledger has one row per upstream file. A pure hStack addition with no upstream file, such as a mobile playbook or a host page, has no row, so its reason lives in the ADR or the release note that approved it until the ledger has a row type for it.
- A later sync that finds an adaptation with no stated kind removes it, or asks the owner to name the kind before it stays.
