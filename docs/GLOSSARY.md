# hStack

hStack is the standalone adaptation of pstack for first-class mobile development through Claude Code, Codex and Cursor.

## Language

**hStack**:
The project named by the product owner for this mobile-first pstack adaptation. It was called huguesStack until 0.4.0. The rename moved the plugin and marketplace name to `hstack`, the command prefix to `/hstack:`, the setup skill to `setup-hstack` and the project-local folder to `.hstack/`. The `hugues-*` skill names are unchanged.
_Avoid_: Mobile Stack, mobile stack as the product name, bare "hstack" for the retired predecessor (see **hstack-alpha**)

**hstack-alpha**:
The retired predecessor, GitHub `osxsystem/hstack`, deleted on 2026-10-16. It is a different project from hStack. The files this repository cites from it stay in [`provenance/upstream/hstack-alpha-99cc612/`](../provenance/upstream/hstack-alpha-99cc612/), byte for byte at revision `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, and the [source receipts](wp3-source-receipts.json) hold their hashes. Name it "hstack-alpha (retired predecessor)" in prose.
_Avoid_: hstack, the old hStack

**Mobile domains**:
The four first-class areas covered by hStack: native Swift/iOS, native Kotlin/Android, Kotlin Multiplatform shared logic, and Compose Multiplatform shared UI.
_Avoid_: Primary native platforms with secondary multiplatform support

**Consumer app**:
A mobile application that hStack helps its owner develop and verify. It is a separate project from hStack.
_Avoid_: Bundled demo app, plugin app

**Upstream responsibility**:
An identifiable purpose or behavior supplied or required by the pinned pstack baseline, regardless of the file or feature that carries it.
_Avoid_: File count as feature parity

**Master inventory**:
The complete accounting of upstream responsibilities, including items recommended for adaptation, deferral, or exclusion.
_Avoid_: Selected subset, implementation checklist

**Observed support**:
Support demonstrated by evidence from the actual claimed host, mobile domain, target, and workflow.
_Avoid_: Assumed support, installed support

**Release candidate**:
A bounded version presented for acceptance against declared requirements, with its supporting evidence and remaining limitations visible.
_Avoid_: Full parity, production-ready by date alone

**Layer 1**:
The hStack plugin itself: skills, playbooks, principles, one agent definition, two scripts and docs, installed in Claude Code, Codex and Cursor from a marketplace manifest. It is the whole 0.1.0 release candidate.
_Avoid_: The harness, the runtime, the core

**Layer 2**:
The Orca-managed worker runtime, Work Units and captured-review contracts of hstack-alpha (retired predecessor), kept as a deferred option. Its existing evidence is never cited as Layer 1 proof.
_Avoid_: Phase 2, the full product

**ADE**:
An agent development environment: an app that hosts several agent sessions and their worktrees, such as Orca or T3 Code. hStack maps only its terminal and worktree mechanics ([ADR 0004](adr/0004-adapters-for-ades-and-agents.md)). It is not **Layer 1** or **Layer 2**.
_Avoid_: Host (that means Claude Code, Codex or Cursor), orchestrator, Layer 2

**Agent**:
A program that runs a model, such as Claude Code, Codex, Cursor or omp. Not a **PR owner**, which is a role an agent can hold, and not **Layer 1** or **Layer 2**.
_Avoid_: PR owner, subagent, worker

**hugues-mode**:
The hStack router skill, forked from pstack's `poteto-mode`. It matches a request to a playbook, copies the steps into the todo list, and names a domain lane and proof surface for build and bug work.
_Avoid_: mobile-mode, the orchestrator

**Proof lane**:
The build, target tests and screen check selected for one changed mobile domain, plus the evidence folder that records them. Implemented by the `mobile-proof` playbook.
_Avoid_: Verification pipeline, CI

**Host baseline**:
The same operation outside the agent, used to split host faults from agent-environment faults.
_Avoid_: Agent settings check, device proof

**Proof-tool check**:
One real operation per required proof tool under the active settings, before lanes are planned.
_Avoid_: Version listing, build proof

**Cross-host review**:
An `interrogate` run in the host that did not produce the diff: Claude Code reviews a Codex diff or the reverse. The only model-independent review available when each host's subagents are single-vendor.
_Avoid_: Multi-model panel, second opinion from the same host

**Consumer fixture**:
A small disposable app with a planted defect, used as a consumer when no real app is selected for a domain. The default for KMP and CMP is the `kmp-compose-ios-pilot` app, copied from hstack-alpha (retired predecessor) into [`tests/fixtures/kmp-compose-ios-pilot/`](../tests/fixtures/kmp-compose-ios-pilot/).
_Avoid_: Demo app, sample bundled in the plugin

**Personal-workflow bar**:
The 0.1.0 proof standard: Claude Code primary, Codex smoke-tested, one observed task per domain, gaps listed in `support.md` rather than gating the release. The one fixed rule is that no flaky, skipped or wrong-target result is reported as a pass.
_Avoid_: NO-GO gate, parity bar

**Per-cell state**:
One of authored, static-tested, observed-pass, observed-fail, blocked or deferred, recorded for each host, domain and workflow cell. Distinct from a run outcome such as pass, fail, flaky or skipped.
_Avoid_: Status, done

**Upstream delta**:
The list of files added, changed or removed between the pinned pstack revision and upstream main, produced by blob-SHA comparison and triaged at most weekly.
_Avoid_: Upgrade, resync

**PR owner**:
The agent responsible for a PR's change throughout its assigned workflow. Reviewers and helper workers are separate participants.
_Avoid_: Builder when referring to every code-writing participant
