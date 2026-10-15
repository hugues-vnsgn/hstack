---
date: 2026-10-15
session: PR 55 review corrections
---

# Journal: PR 55 review corrections

## Context

Read the review in Orca pane
`8a2fcbde-322c-47e9-98b9-624f0d5f4993:0b22c6c5-7e6b-4729-bc2f-0d0e94cb14be`.
The owner authorized implementing the findings we agreed with. Research and plan
review confirmed four corrections against the PR at `8d767fa`.

## What happened

- Reject broad explicit tool-write roots and aliases, malformed domains and JDK
  paths resolving into the protected payload. Preserve legacy consumer/evidence
  behavior and valid policy output.
- Require explicit `dontAsk` mode before Claude editor receipts qualify as
  protection proof. Auto-mode runs remain diagnostic because their receipts do
  not reliably identify why a permission was denied.
- Mark unobserved administrative precedence and weaker-network rationale as gaps.
  Restore existing authorization as a condition for optional writer removal.
- Keep native receipt hashes tied to the historical candidate. Replay the policy
  generator with original recorded inputs and base Claude/Codex inputs; all four
  outputs remain byte-identical. The historical four editor denials still qualify
  in `dontAsk`; none qualify in auto or unspecified mode.

## Reflection

A permission-denial entry identifies a rejected request, but alone does not prove
which control rejected it. Keep that distinction explicit instead of inferring a
sandbox result from a classifier refusal.

## Decisions

Keep the correction in adapters and the proof runner. Skills, provenance,
playbooks, topology and operator gates remain unchanged. Semantic mobile-gate
validation, temporary-directory scope and optional refactors remain follow-up
work. No new native mobile run was performed; historical receipts do not bind
the amended source.

## Next

The correction passed 445 tests and both review axes with zero findings. Main
then advanced through PR #54, producing conflicts in the runner and accounting.
Conflict resolution preserved its helper/startup checks alongside the mobile
gates. All 447 tests and maintenance checks passed; both integration reviews
reported zero findings. Update PR #55. Leave merging to the owner.
