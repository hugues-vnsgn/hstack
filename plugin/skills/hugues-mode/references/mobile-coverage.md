# Select mobile verification by risk

Apply this extension only to an operator-approved mobile program using
`verification_profile: mobile-risk-v1`. Other programs retain pstack's default
verification contract. Reading this reference grants no profile or consumer authority.

## Approve coverage before dispatch

Read the actual diff, project instructions, supported targets and design sources.
Classify each PR as `mobile-behavior`, `documentation` or `tooling-workflow`.
Record changed areas and source evidence. Review the relevant entries in
[the shared risk catalog](mobile-risks.json). A risk names a coverage question,
not a new application requirement. Treat unknown impact as unresolved.

Load only relevant rows into worker briefs. Use the consumer's approved behavior
as the oracle; retain actual inputs and outcomes.

| Area | Assess and exercise |
| --- | --- |
| navigation | Background and reopen; kill the process and restore the saved route/back stack. Assess supported rotation and navigation gestures. |
| persistence | Read/write failures, corrupt stored bytes, interruption during writes and existing-data preservation. Inspect related paths when a failure repeats. |
| layout | Smallest supported width and large accessibility text. Type realistic input and exercise keyboard focus, dismissal and navigation. |
| native-views | Repeated presentation/dismissal, retained memory and cleanup after the view closes. |
| launch | Oldest supported OS, release build and the meaningful content-ready state the user waits for. Retain measurement resolution against the threshold. |
| network | Offline entry, request failure and recovery without lost state or duplicate effects. |

Each relevant risk is `applicable`, `not-applicable` with a reason and the actual
operator ruling, or `unresolved`. Applicable risks need checks on every affected
target. Unresolved risks hold verification. Preserve affected Android and iOS
proof for shared behavior; record actual schemes/variants, builds and devices.

Use any positive number of justified live checks for mobile behavior. Each names
its risks, target, reason, action, artifact and observable pass condition. Number
checks uniquely from 1 without gaps. Several risks may share a check when its
actions cover each. Keep trunk regression and independent audit roles. Check
count does not set worker concurrency; existing limits and model roles apply.

Commit the operator-approved starting plan. Apply [verification contract](verification-contract.md)
before each round and verdict, including profile selection, work type, coverage
and exemptions. Owners propose changes; the operator rules. Export the committed
round plan and run bound `plan-check` on it. Accepted structure authenticates no
approval, confirms no diff classification and proves no behavior; audit those facts.

## Use the supported plan grammar

Add the exact unquoted frontmatter field `verification_profile: mobile-risk-v1`.
Keep the existing headings and verification rule. Insert `**Coverage.**` after
`**Depends on.**` in each PR section. The actual plan uses plain Markdown outside
fences/comments. Fields end with periods; lists use commas. Target IDs use
lowercase letters, digits and hyphens.
Attach receipts after the final period as `Evidence. [Run](receipt-path)` or
`[Run](receipt-path)`. Keep acceptance text outside HTML comments. Risk rows and
check tags must map in both directions, including checks beyond the minimum.

```text
**Coverage.**
- Work type. mobile-behavior.
- Platforms. android, ios.
- Areas. navigation.
- Source. Read changed navigation declarations and supported targets.
- Target android-debug. Platform android. Identity actual variant and device.
- Target ios-debug. Platform ios. Identity actual scheme and device.
- Risk process-death. applicable. Checks 1, 2. Reason saved navigation changes.
- Risk background-reopen. applicable. Checks 1, 2. Reason reopening changes.
- Risk restored-navigation. applicable. Checks 1, 2. Reason restored state changes.
- Risk rotation. not-applicable. Checks none. Reason unchanged rotation ownership. Approval actual operator ruling.
- Risk navigation-gestures. not-applicable. Checks none. Reason unchanged gesture ownership. Approval actual operator ruling.
- Live. applicable.
- Performance. applicable.
```

In the live heading, replace `Ten lanes on` with `Risk-based lanes on`; retain the
rule, selected model and `at the PR head`. Fill each checkbox from approved sources:

```text
- [ ] Lane 1. Restore a saved route. Risks `process-death, background-reopen, restored-navigation`. Target `android-debug`. Reason the saved route changes. Action background, kill and reopen. Save `android/restore.png`. Pass when the approved route and back navigation restore.
```

Check 2 covers the affected iOS target in this example. Risk rows name covering
check IDs; check definitions name risk IDs and targets. The checker validates
both mappings. The catalog covers navigation, layout, persistence, native-views,
launch and network; use only relevant areas in each PR.

Documentation uses `Areas. documentation.` and `Platforms. none.`, without target
or risk rows. Tooling/workflow uses `Areas. workflow.` instead. Both need an
executable unit checkbox, such as `Run \`python3 check-docs.py\``. Independent review
verifies the classification and relevant commands against the diff.

An exempt live/performance block retains the rule, ends in `Not applicable.` and
contains no checkboxes. Its coverage field is
`not-applicable. Reason <specific reason>. Approval <actual operator ruling>.`
Report non-applicability explicitly, never as a device/performance pass. Mobile
behavior always requires live proof. Applicable performance retains metric,
probe, baseline and rule. Measure meaningful content readiness with pstack's
interleaved baseline method; insufficient precision is inconclusive.

## Inspect results

Give workers the approved checks, fixed commit/build, target and relevant risk
guidance. Keep the verifier's approved contract outside owner write access.
Independently inspect actual actions/artifacts. Distinguish failed, blocked,
untested, inconclusive and explicitly waived checks.

A later head requires a new round decision. Apply the existing patch/build rule
in [shipping](../playbooks/shipping.md) before reuse and retain each decision and
comparison. Old attempts retain their original source/build, target and capture
times. Assessment does not bypass current plan comparison or relabel old proof.

For an inaccessible required path, record the gap and a concrete testing-support
request in the verdict. Present unresolved owner decisions. Repeated inability
remains untested; debug hooks and consumer test infrastructure need separate scope.
