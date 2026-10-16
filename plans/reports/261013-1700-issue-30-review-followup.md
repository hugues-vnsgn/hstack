# Issue 30: assess and fix the Claude review

## Summary

The owner requested verification of the review from Orca pane
`8a2fcbde-322c-47e9-98b9-624f0d5f4993:6b0b27ea-daac-42ca-bb95-86aa0b151398`
and fixes for findings that hold. Review baseline is `99a58b3` in the existing
`feat/issue-30-spec` worktree. The approved spec remains unchanged.

Accept the plan/proof integration gap and the reproducible parser defects.
Keep the intentionally combined history and the approved mobile-only scope.
No consumer application, published installation or historical archive is changed.

## Standards findings

| Reviewer item | Assessment and disposition |
| --- | --- |
| 1. Prior zero-findings claim | Earlier reviewers did return zero remaining findings after two fixes. Scope the report to that earlier review and identify session responses as its source. The later review has findings; the old statement cannot describe it. |
| 2. Combined merge and branch name | Integration was deliberate and recorded in the approved spec and handoff. A merge commit preserves both histories; it is not a violation of one writer per branch. Publish only on the owner's separate go-ahead, describing combined scope. |
| 3. Authority wording | Agree the shortening was ambiguous. Commands grant no authority; quota warnings alone never pause. Required owner stops and other holds still apply. |
| 4. Plan/record IDs | Agree a mandatory mapping was missing for mobile plans. Add a hashed plan source, selected PR section and complete lane-to-approved-check mapping. Validate through the shared installed plan checker. |
| 5. Weak test assertions | Extend the installed comparison test to profile migration, risk removal and pass-condition changes. New parser regressions assert named diagnostics as well as rejection. Existing fixture Git setup stays local. |
| 6. Checker shape | Keep the existing default/mobile dispatch. Move no phase gates and add no generic abstraction solely for a length heuristic. |
| 7. Angle brackets | Agree mathematical thresholds were rejected. Accept comparisons and receipt links; reject angle-bracket placeholders and name unresolved fields. |
| 8. Legacy frontmatter | Agree. Restore the prior scan for unfinished legacy frontmatter, while attempted mobile profiles still fail closed. |
| 9. Vocabulary | The guide distinguishes a numbered live check from worker concurrency and a broader proof lane. Explicit mapping connects its number to any approved check ID without renaming public terms. |
| 10. Context disclosure | Correct stale helper text and add a generated inventory for the deferred mobile guide/catalog. Record the existing 369-byte mobile pointer addition. Preserve frozen accounting baselines. |
| 11. Pointers in several workflows | These are conditional entry points into one shared guide, not duplicate rule bodies. Removing them would hide the contract from relevant execution paths. |
| 12. Earlier control code shape | Existing engine is intentionally reused. No demonstrated new defect justifies rewriting its event dispatcher or bootstrap trust boundary in this issue. |

## Spec findings

| Reviewer item | Assessment and disposition |
| --- | --- |
| a1. Plan/proof integration | Agree the evidence checker could certify its indexed subset while a separate plan required more. It did not actually emit an iOS pass. The new protected mapping rejects omitted iOS lanes and every extra selected lane, wrong actions/targets/pass conditions, missing mapping and missing attempts. Legacy records keep their previous semantics. |
| a2. Per-area guidance | Agree bare IDs were insufficient. Add concise assessment/action guidance for each approved area; worker briefs load only applicable rows. |
| a3. Native view repetition | Add the missing repeated-presentation risk and exercise it in the existing installed catalog test. |
| a4. Planning skeleton | Give explicit conditional substitutions next to the default skeleton: mobile frontmatter, Coverage insertion, risk heading/check replacement and exemptions. Keep the default skeleton for legacy programs. |
| a5. Prose requirements | Export explicit live/performance applicability in the derived mobile verdict. Documentation still needs nonempty approved executable checks and actual evidence. Inconclusive is already a supported proof status. Measurement meaning and actual device baseline/restoration require independent observations; this fix does not pretend receipt strings establish them. |
| a6. Missing tests/transcript | Add the comparison variants and retain an explicit external installed-command transcript for twelve checks, complete synthetic proof and missing check twelve. |
| b1. Legacy frontmatter change | Restore and test the prior behavior. |
| b2. Catalog loaded by legacy runs | Load catalog data only when mobile validation executes. Installed integrity still checks the full pinned installation before dispatch. |
| c1. Receipt suffixes | Accept the verification contract's fixed receipt labels, with or without the Evidence delimiter; strip attachments before extracting the pass condition. |
| c2. Placeholder values | Reject TBD, n/a and zero-width-only values. A nonempty approval reference still cannot authenticate an operator; retain independent approval inspection. |
| c3. Commented lanes | Reject HTML comments in the explicit mobile plan rather than count hidden acceptance text. Preserve legacy behavior. |
| c4. One-way mappings | Enforce both directions. Update the synthetic twelve-check fixture to list every check that tags each risk, rather than its former minimum pair. |
| c5. Closed work types/areas | Preserve the approved classifications and six mobile areas. Unknown impact holds discovery. Broadening the profile requires a separate scope decision, not a guessed new fallback. |

## Verification and evidence

Use the already approved public seams: installed bound `plan-check`,
`plan-compare` and `program-check` in disposable consumers outside the plugin.
Seven new collected cases bring the candidate to 527: nineteen mobile cases,
forty-five proof cases and the unchanged remaining groups. Subtests are separate
from collected counts. Tests use synthetic actions/artifacts, not native journeys.

The follow-up evidence directory is
`/Users/hugues_mini/huguesstack-evidence/2026-10-13-issue-30/review-followup/`.
It retains the exact Claude report, installed command argv/exits/output, source
hashes, maintenance logs and the final review responses. Required final checks
are the five README commands; their recorded exits govern the local result.
The first complete follow-up run executed 527 cases in 368.407 seconds and
failed one existing budget assertion: the larger profile equalled its baseline,
while the contract requires a strict reduction. Shorten the authority subject
without removing its rule, then regenerate the inventory; keep the assertion.
This run is retained as history, not a final pass. Re-run all five checks for the
final candidate after this correction and the review fixes below.
Any subsequent edit needs an explicit assessment before reusing those results.

Red checks observed the missing optional plan binding, rejected threshold/receipt,
accepted inconsistent risk tags/comments/placeholders, changed legacy handling
and omitted native-view risk before their respective fixes. The document verdict
also lacked its applicability field before that export was added. Focused logs
record the resulting public-command behavior.

The review's statement that comparison had no installed test is incorrect:
`test_profile_and_risk_changes_require_exact_operator_ruling` already called
bound `plan-compare`; this follow-up expands its cases. Source/build binding,
independent inspection and device ownership holds remain in the reused engines.

## Fresh review corrections

The follow-up spec reviewer reproduced a P2: a malformed retained profile could
skip the mandatory mapping while `plan-check` rejected that same plan. Use the installed JavaScript parser's profile detection directly, require the
mapping and validate its snapshot through that same parser. Separate Python and
JavaScript regexes disagreed on U+FEFF and non-ASCII word boundaries; sharing the
parser removes that disagreement. Installed regression subcases cover eight
malformed variants with matching record digests.
A profile quoted in ordinary design prose preserves legacy record behavior.

The standards reviewer also flagged paired mathematical comparisons. Preserve
`< 2 s` together with `> 0 MB` instead of interpreting the intervening words as a
placeholder. The same installed receipt/threshold test exercises both forms.
The first attempted final suite at tree `77d2763` was interrupted after the
Unicode recheck exposed the remaining bypass. Its exit -2 and four completed
static passes are superseded evidence, not a clean final result. Root identified
the test process through its exact log file, PID/parent and command before the
interrupt. No device process or another agent's run was signalled.
Earlier review responses apply to their recorded source tree; final rechecks and
the complete final maintenance run are retained separately in the evidence folder.

## Remaining observations and next step

Real Claude Code/Codex worker dispatch, owner write protection across native host
tools, meaningful performance timing, actual device baseline/restoration and
inaccessible-path escalation remain deferred. The mobile plan binding validates
declared snapshots; it cannot discover a deliberately omitted plan or establish
approval identity, real diff classification or artifact meaning.

This work remains local. Publishing, merging, installation and issue closure
require the owner's current-task go-ahead. Preserve the earlier evidence as
history and review the combined change before the later real trial.
