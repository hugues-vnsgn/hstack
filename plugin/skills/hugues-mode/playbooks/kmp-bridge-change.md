# KMP bridge change

source: hStack first-release requirements; conceptual reference to hstack-alpha (retired predecessor; GitHub osxsystem/hstack, deleted 2026-10-16; bytes retained in `provenance/upstream/hstack-alpha-99cc612/`) at `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, `packs/mobile/references/kmp-compose-pilot.md`, `packs/mobile/references/platforms.md` and `packs/mobile/references/evidence.md`. No fixture or consumer source is imported.

Own the shared contract and prove both native boundaries.

This extends the selected core action playbook. Read that playbook in full, copy
its ordered todos verbatim, and add the target requirements below at its matching
phases. Do not execute this extension in place of the core procedure.

## Steps

1. Establish the authorized consumer checkout and affected targets using [mobile lanes](../references/mobile-lanes.md). Read the shared API, source sets and Android/iOS callers; use the owner's available `kmp-boundaries`, `kmp-ios-integration`, `kmp-test-seams` and `tdd-kmp` skills where relevant, disclosing missing skills.
2. Pin behavior and boundary cases in common tests before edits. For a bug, observe the failing case on the affected target and preserve red evidence; read [tdd](../../tdd/SKILL.md) in full and brief a fresh scoped regression-test worker on a cheap seam and independently run its check against unfixed production code for observed RED before the separate fresh production worker in step 3, or record the impractical-seam reason and runtime failure. Record Android and iOS export, lifecycle, threading, cancellation and error contracts that the change touches.
3. Read [how](../../how/SKILL.md) in full for shared code and native callers. Design the smallest shared change and account for every platform adapter and caller. For changes across a function boundary, read [architect](../../architect/SKILL.md) in full and complete design-only synthesis. For wide exported-API changes, read [blast-radius](../../blast-radius/SKILL.md) in full and identify the downstream safety check. Apply the selected core implementation gate and configured role models. For Feature work with multiple valid shapes, read [arena](../../arena/SKILL.md) in full and complete the implementation arena. Mandatory: no skip-with-reason escape. Design-only synthesis cannot satisfy this implementation gate, even within one function. Otherwise brief the fresh implementation worker permitted by the core with the design, owned paths, target tasks and at least one native caller per side; preserve the core scoped-worker exception and review separation. Each correction round uses a fresh worker.
4. Inspect the actual diff and run [mobile proof](mobile-proof.md) yourself: execute common tests on each Android and iOS target, build each affected native artifact and exercise at least one Android caller and one iOS caller. Framework linking or a JVM-only pass does not prove either native call path.
5. Obtain an independent fresh review of shared behavior and exported boundaries. Resolve findings, repeat coordinator proof and run [opening a PR](opening-a-pr.md) with separate target outcomes and any gaps.

**Reply:** shared contract, changed boundaries, each target's test and native-caller evidence, independent review and limits.
