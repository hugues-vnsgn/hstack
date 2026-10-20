# Mobile adapter

Read this with the host adapter before executing pinned core guidance. It adds
mobile proof and consumer boundaries without replacing the core workflow.

## Applicability

Apply this adapter only to an explicitly selected mobile task (Swift/iOS,
Kotlin/Android, KMP or CMP). For all other work, follow the pinned core unchanged.
The regression-worker and arena-isolation additions below apply only to that
mobile scope; loading this document alone does not activate them.

## Intent before domain

Choose lifecycle or action intent first: pause, pickup, verification maintenance,
verification-skill authoring, review, investigation, prototype, then implementation.
A language or target keyword alone is not implementation authority. First select
the core action playbook and retain its complete procedure. Native Swift or Kotlin
implementation uses that playbook. Shared KMP boundary implementation adds
[kmp-bridge-change](../skills/hugues-mode/playbooks/kmp-bridge-change.md);
CMP rendering implementation adds [cmp-two-target-change](../skills/hugues-mode/playbooks/cmp-two-target-change.md).
These extensions compose target requirements into the selected core phases;
they never replace core todos or implementation gates. Feature work with multiple
valid shapes completes the mandatory implementation arena before target proof,
even when no function boundary changes. Design-only arena does not satisfy it.
Build/toolchain diagnosis uses [build-doctor](../skills/hugues-mode/playbooks/build-doctor.md).
Existing-recipe proof uses [mobile-proof](../skills/hugues-mode/playbooks/mobile-proof.md).
These four are explicit extension routes. Large, cross-cutting, unmatched and
standing-program work still follows the core fallback before a narrow mobile
route. Add applicable target proof as a phase in that designed workflow.

## Language, review and diagnosis guidance

Before reading or editing Swift or Kotlin source, apply [mobile language scope](host-mobile-languages.md).
The bundled baselines and their conditional references supply essential guidance.
Personal expert skills are optional supplements, reached through native controls.
The consumer's required verification recipe remains required.

At the selected action's existing review phase, read the [mobile review lens](../skills/hugues-mode/references/mobile-review.md)
and give it to the independent reviewer. Carry each applicable risk into proof as
covered with evidence or as a named gap. This adds no phase or review panel.
For mobile Runtime forensics, read [native forensics](../skills/hugues-mode/references/mobile-forensics.md)
before capture and translate the existing steps on the matching runtime.

## Evidence and scope

For mobile multi-phase plans, before step 4 of the selected
[multi-phase plan](../skills/hugues-mode/playbooks/multi-phase-plan.md) writes
the live lanes, read [mobile lanes](../skills/hugues-mode/references/mobile-lanes.md)
and the [mobile review lens](../skills/hugues-mode/references/mobile-review.md).
Choose scenarios within the existing ten lanes and carry applicable risks into
their actions and pass predicates. Keep the ten-lane rule unchanged.

Read [mobile lanes](../skills/hugues-mode/references/mobile-lanes.md),
[evidence guide](../skills/hugues-mode/references/evidence-guide.md), and
[jev drive](../skills/hugues-mode/references/jev-drive.md) at the relevant proof
phase. Establish language, native/shared ownership, exact target identity and
runner from independent source reads and the request. Preserve unknown components
instead of guessing. A build does not prove behavior; one target does not prove
the other. Record revision, actual command/exit, target and surviving artifacts.
Use the bundled language baselines and applicable platform references. Optional
expert skills add depth without becoming baseline prerequisites. Keep consumer
apps outside this plugin.

For mobile bug fixes, assign a fresh general-purpose regression worker before the production
worker. Independently observe RED against unfixed production, then give a separate
fresh production worker the failing regression and observe GREEN on that same
regression. Preserve the core TDD impractical-test exception with a concrete
reason and real surface proof. For shared changes, cover affected Android and iOS
surfaces. Missing proof is blocked or inconclusive, never a pass.

The regression worker reads only the `tdd` SKILL.md, the matching language baseline
at absolute installed paths, the native execution adapter at its absolute installed
path, and the files named in its brief. It does not load
the full mode or principles. The production worker is unchanged.
Include `<plugin>/adapters/native-execution.md` as an absolute installed path in the brief.
Any build or test command the regression worker runs goes through the native helper.
Put this contract in the regression brief. It overrides transitive skill reads
and TDD's production-edit steps.
The coordinator never writes the regression test. On a stall, dispatch one fresh
replacement with a narrower brief. A second stall marks the regression step
blocked. State it in the final message.
A worker spawned with the coordinator's turns, `fork_turns: "all"` or the equivalent,
is not fresh for either the regression or production role.

For native build and test commands, read [native execution](native-execution.md)
in full and use its helpers with the consumer-selected argv and task evidence
store. During iteration choose the narrowest relevant supported tests. Retain
separate RED and GREEN attempts on the same regression, including actual test
counts and failures. Keep the impractical-test reason and executable runtime
reproduction when that exception applies. Final integration, native callers and
runtime proof still follow the consumer recipe; a helper pass does not replace them.

For mobile arena work, give candidates fresh contexts containing only the sanitized candidate
brief and isolated write paths. Keep the rubric and parent preference out. After
candidates finish, give the fresh read-only judge only neutral artifacts and the
rubric. Inspect actual isolation capability. If unavailable, block blind judging;
do not claim blind review. The coordinator reads and scores actual artifacts and
verifies the synthesized result. This strengthens isolation and preserves core
model selection and phase order.

## Verification skills

The pinned generator owns feature-map discovery and seeding: features/README.md
plus the top 3–5 user-facing features. Prove its instructions end to end on one
mapped feature with evidence surviving cleanup. Maintenance covers the whole map,
discovers source-only missing features and serially drives every mapped feature.
Neither a single successful journey nor a bounded checkpoint proves a clean
whole-map maintenance cycle.

Honor the consumer's existing `.claude/skills` or `.agents/skills` layout and
use supported native invocation for consumer and external skills; never substitute
direct body reads for unavailable or denied invocation of those. A bundled user-only
skill is read as [host.md](host.md) says. A user may explicitly
request a bounded one-journey diagnostic. Label that as the bounded-mobile
extension and report unvisited features. Use the authored
[bounded-mobile template](../skills/create-verification-skill/references/project-skill-template.md)
only for that explicit opt-in. It cannot replace or satisfy the core
generator/maintenance contract. Screenshots/logs remain local unless their
transmission is explicitly authorized; apply the Jev/TypeSafe authority rules.
