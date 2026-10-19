# Mobile proof

source: Conceptual adaptation of hstack-alpha (retired predecessor; GitHub osxsystem/hstack, deleted 2026-10-16; bytes retained in `provenance/upstream/hstack-alpha-99cc612/`) at `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, `packs/mobile/skills/mobile-proof/SKILL.md, packs/mobile/references/platforms.md, packs/mobile/references/evidence.md`; hStack first-release requirements. No managed-worker runtime is imported.

Select the changed domain's proof and report what actually ran.

Run Xcode, SwiftPM and consumer Gradle build/test commands through the
[native execution helpers](../../../adapters/native-execution.md). Preserve the
recipe's explicit command and selectors, and inspect actual counts and native
reports. Zero selected tests, stale artifacts or a different target cannot pass.
During iteration use focused checks; final proof still covers the required
integration and runtime behavior on each affected native boundary.

## Steps

1. Run the preflight before planning lanes. Read [mobile lanes](../references/mobile-lanes.md#proof-tool-preflight), repository instructions and the [evidence guide](../references/evidence-guide.md). Establish the authorized consumer and discover its required proof tools through the project's native verification recipe and current configuration. Hold dependent checks if that recipe or execution authority is unavailable. Create the task evidence folder before any probe. Record whether the Bash sandbox is on or off, host/version, OS and tool versions. Run one real, harmless operation per required proof tool under the active settings. Record argv, exit code, output and a `works` or `blocked` verdict for each. A blocked tool drops or replaces its lane up front, recorded as a gap. After a blocked result, obtain the [host baseline](../references/mobile-lanes.md#host-baseline) before changing agent settings. With the sandbox off, the agent's shell counts and is labelled as such. With it on, print the same command for the owner to run outside the agent in a plain terminal. Record versions, time and the last good run from earlier evidence, or `unknown`. A failing baseline is a host blocker reported to the owner; stop iterating on agent settings. A passing baseline routes to [build-doctor](build-doctor.md). An unrun baseline remains blocked.
2. Confirm the authorized consumer repo and SHA, plugin SHA, host/version and changed domains. Read [mobile lanes](../references/mobile-lanes.md) and repository instructions. Invoke the existing project `verify-<app>` through the host's supported native mechanism. If unavailable, disabled, denied or unknown, hold its dependent proof; request explicit native invocation only when the host requires it. Never read its body as a fallback. Reconcile the invoked recipe's commands, selectors and readiness signals with current authority and repo facts before execution. Pin scheme or variant, target tests, native callers, device identity and expected changed behavior before execution.
3. Use the task evidence folder from step 1, outside the plugin and consumer repositories, for authorized runs. Record each proposed argv or tool call and its target; retain original pre-fix evidence for bugs. If consumer execution is not authorized, report the missing authority and retain remaining run steps as blocked.
4. Run the lane's build and target tests yourself against the exact current artifact. Preserve output and result bundles. Verify executed assertion counts and target identity; record skipped assertions as skipped, retried/flaky assertions as flaky and wrong-target results as invalid for the requested target.
5. Exercise the lane's required runtime behavior and native callers on their own targets. Read [jev Drive](../references/jev-drive.md). Use available permitted jev-ios-bridge for judged screen proof, otherwise the labeled repository-compliant UI-test/device-tooling fallback. CMP requires Android and iOS UI evidence plus semantics or text-scaling evidence. Preserve artifact identity with each observation.
6. Complete the [evidence template](../references/evidence-template.md) with actual identities, command/tool results, outcomes and artifact paths; independently reopen the artifacts after authorized teardown. Finish when every applicable requirement has an inspected result or named blocker; compilation and authored instructions remain separate from observed support.

**Reply:** per-domain build, test, caller and screen outcomes, evidence folder, flaky/skipped/blocked checks and limits of fallback proof.
