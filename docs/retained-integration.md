> Historical 0.1.0 implementation record. Its rewritten workflows and deferrals are superseded on the unreleased restoration branch. Read the [development guide](DEVELOPER-GUIDE.md) for current source contracts and evidence limits.

# Retained tools and RC2 integration

RC2 combined the eight owner-approved retained tools with the existing mobile
mode. Combined [PR #13](https://github.com/hugues-vnsgn/huguesStack/pull/13)
merged into main at `18c73d183f19ed9b401f4b58c6743705a6bfc3da`.
The final 0.1.0 metadata/docs change has separate checks and review obligations;
publication receipts belong with
[GitHub Releases](https://github.com/hugues-vnsgn/huguesStack/releases).
Draft PR #2's feature maps/CLI-first changes remain deferred. Target remains
9 October 2026, end of day GMT+7.

## Reviewed package inputs

The following completed package checks and independent Astra High reviews were
observed before this integration. Each package's seven exact-head checks passed.
These verdicts cover those heads, not the later integration commit.

| Package | Reviewed head | Public draft and receipt |
|---|---|---|
| Foundation | `3af59a9c78e710ac51b0a886e4abf9d79c4b2af3` | [PR #9](https://github.com/hugues-vnsgn/huguesStack/pull/9); shared retained-source accounting |
| Research | `615edc7b40336acc60adfb82d3f41a34d8119919` | [PR #10](https://github.com/hugues-vnsgn/huguesStack/pull/10); [research receipt](upstream/retained-research-provenance.json), [contracts](retained-research.md) |
| Design | `f4026d5e4f15df7666a47876aa06d7cc18da266d` | [PR #11](https://github.com/hugues-vnsgn/huguesStack/pull/11); [design receipt](upstream/retained-design-provenance.json), [contracts](retained-design.md) |
| Verification | `f126656d2718084de8292cda0cb40b81333e4d6e` | [PR #12](https://github.com/hugues-vnsgn/huguesStack/pull/12); [verification receipt](upstream/retained-verification-provenance.json), [contracts](retained-verification.md) |

The reviewed verification tree is `dc9920b430d37d2d368492831f2345d45e639ec9`.
It passed 152 framework tests and all seven checks before integration. The
combined package contains 35 skills, 14 playbooks and one worker, across 79 plugin
files. The eight leaves and their 25 source-accounted files retain their reviewed
bytes. All 24 principles remain verbatim at the unchanged pstack 0.15.9 pin
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`.
The pstack 0.15.25 merge rebound the provenance receipt to `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f` after porting the upstream changes; this record still describes the original package.

## Existing playbook handoffs

Read each linked tool in full from the package before using it. Their disabled
model invocation means a direct file read, not a Skill-tool call. Keep the
[host adapter](../plugin/skills/hugues-mode/references/host-notes.md), scoped
worker role and current consumer authority throughout.

| Existing route | Handoff |
|---|---|
| [investigation](../plugin/skills/hugues-mode/playbooks/investigation.md) | `how` for mechanics; `why` for rationale and regression history; read-only findings and confidence |
| [bug-fix](../plugin/skills/hugues-mode/playbooks/bug-fix.md) | `how`/`why`, design-only `architect` when a function boundary changes, fresh test-only worker and independently observed cheap `tdd` RED before the separate production worker, preserved RED and same-check GREEN afterward; original runtime path still required |
| [feature](../plugin/skills/hugues-mode/playbooks/feature.md) | `how`, design-only `architect` with arena's two distinct sketches and verified synthesis; `arena` for warranted competing implementations |
| [prototype](../plugin/skills/hugues-mode/playbooks/prototype.md) | Design tools for an actual structural decision or competing executable experiment, within throwaway scratch scope |
| [refactoring](../plugin/skills/hugues-mode/playbooks/refactoring.md) | `how`, characterization first, design-only `architect` across boundaries and `blast-radius` for wide/shared-API changes |
| [authoring-a-skill](../plugin/skills/hugues-mode/playbooks/authoring-a-skill.md) | New bounded recipe uses `create-verification-skill`; existing recipe hands off to coordinator-owned `maintain-verification-skill` before generic worker briefing; recurring classes hand off to `correct` |
| [opening-a-pr](../plugin/skills/hugues-mode/playbooks/opening-a-pr.md) and direct review | `blast-radius` for big/wide diffs, retaining falsifiable safety checks and unrun facts within actual check authority |
| [kmp-bridge-change](../plugin/skills/hugues-mode/playbooks/kmp-bridge-change.md) / [cmp-two-target-change](../plugin/skills/hugues-mode/playbooks/cmp-two-target-change.md) | Cheap bug RED before the production worker; design and wide-change tools retain both targets' proof obligations |

Maintenance covers the existing agreed journey, every named checkpoint and every
required target. Its source readers remain read-only; the coordinator owns one
live mobile session at a time and re-proves owned harness repairs. Clean and
blocked outcomes produce no PR; changed permits at most one bounded authorized
correction. A missing live pass is blocked. The generic authoring route ends at
this handoff. `correct` requires repeated real evidence per class and proves
chosen enforcement against a real past mistake. A scoped implementation worker
performs its assignment directly; these links do not authorize recursive workflow
delegation.

All fourteen routes plus `interrogate`, routing precedence and numbered checklist
counts remain intact. Optional owner writing/unslop and mobile specialty skills
retain explicit absence reporting. The 6 October approval defers only `swarm`,
`show-me-your-work` and `setup-huguesstack` to 0.2; existing feature-map, CLI-first,
Layer 2 and other deferred scope remains in the [plan](PLAN.md).

## Static checks and observed-proof boundary

The integration regressions use manifest-driven discovery, actual numbered-step
links, pre-worker RED ordering, maintenance handoff and deferred-scope accounting.
Mutations remove or move those inputs; real package checking rejects missing
shipped targets. This tests Markdown/package contracts, not LLM adherence or
native execution. Run the existing unittest, package, upstream, strict Claude
plugin/marketplace, shell syntax and whitespace checks. Record their exact
candidate head/tree, raw-log hashes and independent final-head review before
publication; no future SHA or verdict is assumed.

The [RC1 receipt](rc-validation.md) retains 54 fingerprints bound only to the
plugin bytes at `21a82942019292f7212ff1185e9ef187ac96e86d`. Its two-host
16-case/87-step previews and bounded scratch delegation are historical. RC2's
changed mode/playbooks and 79 plugin files subsequently received fresh native
Claude loading and manual Codex previews at `e2ff899`. The [RC2 receipt](rc2-host-validation.md)
records sixteen route cases/87 exact steps per host, the unsupported-language
gap, bounded synthetic workflows and later six-case lane-evidence observations.
Later [S1/K1 native proof](rc2-native-feature-proof.md) establishes bounded
Swift RED/GREEN/native assertion phases and Kotlin RED/GREEN/unit/build evidence,
plus a later bounded K1 device/recipe/maintenance cycle with owned cleanup and
reopened evidence. Full eight-workflow adherence, native todo behavior,
four-domain feature completeness, compaction/general persistence and the clean
generated-recipe cycle remain incomplete. Historical failures, native results and target limits
remain in [support](support.md) and the [evidence index](evidence-index.md).

The later [repaired schema probes](rc2-host-validation.md#repaired-schema-probes)
passed six unique cases and 36 copied steps per host, with actual scoped source
reads. They used corrected uncommitted plugin bytes and a revised prompt schema;
all 79 plugin fingerprints remained unchanged during the probes. This establishes
bounded planning previews. Full workflow adherence remains unproven. Final
committed-byte binding now matches all 79 files at `68cb710`, tree
`41dcde6fbe6330aec21ec6570fe70b107ba69da9`. That clean routing candidate passed
194 framework tests/seven checks and independent same-host Astra High review.
These receipts cover that head. Merged combined PR #13 subsequently passed
202 framework tests/seven checks and independent Astra High final-head review.
The final 0.1.0 metadata/docs candidate needs its own checks/review. The version
change preserves skill, playbook and worker bodies; no fresh host load with the
0.1.0 manifest has been observed.

## Delivery path

Verified remote state on 6 October: the selected combined PR #13 is merged into
main at `18c73d183f19ed9b401f4b58c6743705a6bfc3da`. The earlier alternative
draft stack #8 → #9 → #10 → #11 → #12 is no longer open. Its individual
reviewed inputs remain historical receipts above. The only open PR is deferred
draft [#2](https://github.com/hugues-vnsgn/huguesStack/pull/2) at
`4f032119f887407885a5e90851633d1887cc57cc`; it remains unmerged and outside 0.1.0.

The owner authorized completion, push, merge and release on 6 October. The final
metadata/docs change must pass applicable package checks and fresh independent
GPT-6 Astra High review before publication. Consult GitHub Releases for the
published tag, exact revision and release-asset verification.
