# CMP two-target change

source: hStack first-release requirements; conceptual reference to hstack-alpha (retired predecessor; GitHub osxsystem/hstack, deleted 2026-10-16; bytes retained in `provenance/upstream/hstack-alpha-99cc612/`) at `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, `packs/mobile/references/kmp-compose-pilot.md`, `packs/mobile/references/platforms.md` and `packs/mobile/references/evidence.md`. No fixture or consumer source is imported.

Own shared UI behavior and prove it on both runtimes.

This extends the selected core action playbook. Read that playbook in full, copy
its ordered todos verbatim, and add the target requirements below at its matching
phases. Do not execute this extension in place of the core procedure.

## Steps

1. Establish the authorized consumer checkout and Android/iOS deployment targets using [mobile lanes](../references/mobile-lanes.md). Read shared UI and interop entry points; use the owner's available `compose-multiplatform-ui` and relevant platform skills, disclosing missing skills.
2. Pin the changed interaction, states and expected UI behavior. For a bug, preserve the failing observation first; read [tdd](../../tdd/SKILL.md) in full and brief a fresh scoped regression-test worker on a cheap seam and independently run its check against unfixed production code for observed RED before the separate fresh production worker in step 3, or retain the impractical-seam reason and runtime failure. Choose an explicit semantics or text-scaling case and device conditions before implementation.
3. Read [how](../../how/SKILL.md) in full for shared UI and platform interop. For changes across a function boundary, read [architect](../../architect/SKILL.md) in full and complete design-only synthesis; for wide shared-primitive changes, read [blast-radius](../../blast-radius/SKILL.md) in full and identify the downstream safety check. Apply the selected core implementation gate and configured role models. For Feature work with multiple valid shapes, read [arena](../../arena/SKILL.md) in full and complete the implementation arena. Mandatory: no skip-with-reason escape. Design-only synthesis cannot satisfy this implementation gate, even within one function. Otherwise brief the fresh implementation worker permitted by the core with owned shared/platform files, chosen design, behavior, target builds/tests and UI success criteria. Account for input, navigation, accessibility and platform interop affected by the change. Preserve the core scoped-worker exception and review separation; each correction round uses a fresh worker.
4. Inspect the actual diff and run [mobile proof](mobile-proof.md) yourself on an Android emulator and an iOS simulator. Preserve each target's build/tests, driven UI path and screenshots, plus the selected semantics or text-scaling observation. A successful JVM test or one target's screen cannot prove the other.
5. Obtain an independent fresh review of both UI paths and platform boundaries. Resolve findings, repeat coordinator proof and run [opening a PR](opening-a-pr.md) with separate per-target outcomes and remaining gaps.

**Reply:** shared UI behavior, Android and iOS proof, semantics/text-scaling result, independent review and blockers.
