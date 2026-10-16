# huguesStack maintainer reference

This reference describes the native consolidation shipped in 0.3.0. Start with the [developer guide](DEVELOPER-GUIDE.md) for the current layout and invocation limits. Published release evidence remains bound to its original revision. The source pin is now pstack 0.15.25 at `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f`, merged after 0.3.0 and not yet released.

## Load the intended checkout

Use a fresh Claude Code session in the intended consumer repository:

```sh
claude --plugin-dir /absolute/path/to/huguesStack/plugin
```

Verify discovery of hugues-mode and use the registered command the host exposes. The manifest name is hugues-stack and carries version 0.3.0, a new minor version because the native layout, payload schema 2 and bindings are incompatible with 0.2.0. Verify the checkout path and exact commit as well as the cache/version label. Claude discovery and router invocation were observed once, at commit `0988b56` (see the [interactive check](router-interactive-check.md)); a later checkout still needs its own invocation evidence.

For Codex, use an already-authorized supported native invocation. If discovery or invocation is unavailable, disabled, denied or unknown, hold the dependent step. Provide a manual handoff only when the host requires explicit user invocation; never substitute a direct file read. These instructions authorize no host configuration changes or installations.

Canonical native skill bodies apply host guidance and mobile applicability before their workflow steps. A consumer or external skill still uses supported native invocation, with conditional handoff or hold; never a direct-read fallback for those. A bundled user-only skill, including every principle, is the mode's reference instead: read its own SKILL.md in full with the host's own file-read tool; the installed helper never reads a skill body. Reread relevant files after compaction if the contract is no longer available in context.

## State a task and follow its route

```text
/hugues-mode reproduce the Swift list jump on the named iOS simulator, then fix it
/hugues-mode explain why this Kotlin search code uses that boundary
/hugues-mode change this KMP boundary; prove Android and iOS callers
/hugues-mode compare this CMP screen on both targets including text scaling
```

Give the consumer path/revision, authorized actions and observable result. Intent precedes language: lifecycle, authoring, review, investigation and verification retain their routes. Native implementation uses core playbooks; KMP/CMP use named extensions. Large/cross-cutting/unmatched work uses figure-it-out; standing programs use Orchestrate. Mobile proof becomes a phase of that designed workflow.

The coordinator invokes the selected native skill, loads its phase-required owned references, copies ordered todos, grounds/designs, delegates fresh rounds and independently checks actual artifacts. Feature work with multiple valid shapes requires arena. For mobile arena work, candidates get sanitized fresh contexts and isolated write paths; the judge gets neutral artifacts/rubric after writers finish. Missing isolation blocks blind judging.

## Configure roles explicitly

Every role defaults to `inherit-parent` at the effort its skill names. Optional project-local `.huguesstack/models.md` overrides roles; deleting a role restores its skill default. `/setup-huguesstack` detects exposed models, loads state, asks for budget/role choices, validates and writes only after confirmation and authority. Restoring the plugin does not execute setup.

Budgets remain unlimited/max, large/xhigh, medium/high and small/medium. Panel lists launch one worker per entry, `inherit-parent` entries included. `inherit-parent` omits the model override. A rejected value runs on `inherit-parent` at its effort. Report actual models/efforts, blocked seats and process independence separately from model diversity.

Generic interrogate keeps its three `inherit-parent` seats or configured list, sends the same prompt/rubric, synthesizes adjudicated findings and does not auto-fix. The [two-seat Astra High policy](../plugin/policies/astra-pr-review.md) is suspended for huguesStack PRs; re-activating it in AGENTS.md restores its exact-head review, fix and fresh re-review gate.

## Prove the actual mobile behavior

Establish language, native/shared ownership and target from source and the request. Preserve unknowns; Gradle syntax alone does not establish language. Record plugin/consumer revisions, target/runner, actual commands/exits and surviving artifacts. A build is not behavior proof; skipped tests and wrong targets do not pass.

Mobile bug work uses a fresh regression worker and independently observed RED against unfixed production, then a separate production worker and GREEN on the same regression. The core practical-test exception retains a concrete reason and closest useful verification. Shared changes need both affected targets.

Generation interviews the repository and writes launch/doctor/drive/evidence/cleanup/helpers. It seeds features/README.md and the top 3–5 user-facing feature files, then proves one mapped feature end to end. Translate the Cursor example layout to the existing `.claude/skills` or `.agents/skills` convention. Preserve user edits. An unexecuted recipe remains a draft.

Maintenance covers the whole map: source readers, reconciliation/source-only omissions, serial live proof of every mapped feature, doctor/recovery, one drift retry and evidence-preserving cleanup. Outcomes are clean/changed/blocked. An opt-in one-journey diagnostic is bounded-mobile coverage and cannot satisfy whole-map maintenance.

Read [lane rules](../plugin/skills/hugues-mode/references/mobile-lanes.md), [evidence guide](../plugin/skills/hugues-mode/references/evidence-guide.md) and [Jev transmission rules](../plugin/skills/hugues-mode/references/jev-drive.md). Consumer edits/execution and data transmission use current owner scope. No consumer app is bundled.

## Long work and publication

Long/autonomous work keeps the pinned append-only TSV trail, ownership start rows, evidence pointers and superseding corrections. Audit only the current run against its available transcript. Missing native transcript/cross-family review is an explicit audit gap. Use pause-safely/session-pickup to reconstruct actual state and preserve evidence.

Helpers live alongside their owning canonical skills. Inspect local runtime/cache/authority first. Before a protected Bun helper, run bound `helper-ready`; missing or stale prerequisites hold before bootstrap. Prepare dependencies separately with installation scope. Bound `payload-policy` prints a host fragment for review; it applies nothing and proves no enforcement. Follow [payload protection](../plugin/adapters/payload-protection.md) for the exact bound root and every enabled writer, including hooks. Missing cloud, loop, forge or model capability blocks dependent work. Shipping does not gain merge authority from green tests.

For planning and cleanup, use the [installed host commands](../plugin/adapters/host-tools.md). Save the approved payload binding when authoring a program. Fill and translate bundled plan operands, validate with `plan-check`, compare committed plans with bound `plan-compare` before autopilot verdicts, and reread workflows through that binding at every required tick. Payload/adapter drift blocks the program; consumer-owned files still come from consumer trunk. The native worktree audit takes an explicit authorized source manifest and local PR snapshot. Incomplete activity coverage holds candidates. The separate active/pinned-chat gate remains required before any prune decision; the helper never deletes or discovers private transcript directories.

Opening a PR retains ready-PR and stack/base mechanics. Prepare local commits/body when authorized; push/publication/merge/release need separate scope. Do not replace a blocked ready gate with a draft fallback.

## Change and validate the plugin

Edit canonical skills or owned adapters, then run `python3 scripts/seal_payload.py`, naming each changed canonical file with `--accept <repository path>`, and update retained-source receipts for affected files. Review these changes and run all checks; sealing is not behavioral approval. The upstream archive is immutable provenance. `render_core.py` is retired. Mobile redesign remains separate from this consolidation.

```sh
python3 -m unittest discover -s tests -v
./scripts/check-plugin.sh
python3 scripts/check_core.py
python3 scripts/upstream-diff.py check
python3 scripts/check_whitespace.py
```

Source checks verify all 169 archived upstream files against the Git snapshot, then check canonical mappings, installed inventory, modes, hashes and workflow boundaries. Development tests cover source, phases/cardinality/fallback, active wiring, bounded overrides and helpers. Installed adapter tests use external disposable consumer directories and synthetic native transcripts. Frozen release tests cover historical contracts only; [test accounting](TEST-COVERAGE.md) separates these roots. Passing static checks cannot attest to unrun host/mobile journeys.

See [restoration scope](CORE-RESTORATION.md) and [historical support](support.md). All upstream responsibilities stay in the ledger, including all 54 registered top-level skills, both native agent definitions and the separate Benny service source. Registration of automate-me or make-bot-ui grants no authority for personal transcript processing or bot/webhook execution. TypeScript guidance remains available alongside mobile adapters.

The canonical Comment Sicko agent retains its complete source rules for no-comments. KMP/CMP extensions compose the selected core action procedure and require implementation arena within step 3 when Feature has multiple valid shapes; design-only arena cannot satisfy that gate. Both wiring failures have phase-local mutation regressions.
