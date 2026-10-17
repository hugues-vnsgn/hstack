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

## Evidence and scope

Read [mobile lanes](../skills/hugues-mode/references/mobile-lanes.md),
[evidence guide](../skills/hugues-mode/references/evidence-guide.md), and
[jev drive](../skills/hugues-mode/references/jev-drive.md) at the relevant proof
phase. Establish language, native/shared ownership, exact target identity and
runner from independent source reads and the request. Preserve unknown components
instead of guessing. A build does not prove behavior; one target does not prove
the other. Record revision, actual command/exit, target and surviving artifacts.
Use available Swift/iOS, Kotlin/Android, KMP and CMP expertise by name when needed;
do not copy a consumer app into this plugin.

For mobile bug fixes, assign a fresh scoped regression-test worker before the production
worker. Independently observe RED against unfixed production, then give a separate
fresh production worker the failing regression and observe GREEN on that same
regression. Preserve the core TDD impractical-test exception with a concrete
reason and real surface proof. For shared changes, cover affected Android and iOS
surfaces. Missing proof is blocked or inconclusive, never a pass.

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
