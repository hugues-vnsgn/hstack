# Mobile proof

source: Conceptual adaptation of hstack-alpha (retired predecessor; GitHub osxsystem/hstack, deleted 2026-10-16; bytes retained in `provenance/upstream/hstack-alpha-99cc612/`) at `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, `packs/mobile/skills/mobile-proof/SKILL.md, packs/mobile/references/platforms.md, packs/mobile/references/evidence.md`; hStack first-release requirements. No managed-worker runtime is imported.

Select the changed domain's proof and report what actually ran.

## Steps

1. Confirm the authorized consumer repo and SHA, plugin SHA, host/version and changed domains. Read [mobile lanes](../references/mobile-lanes.md) and repository instructions. Invoke the existing project `verify-<app>` through the host's supported native mechanism. If unavailable, disabled, denied or unknown, hold its dependent proof; request explicit native invocation only when the host requires it. Never read its body as a fallback. Reconcile the invoked recipe's commands, selectors and readiness signals with current authority and repo facts before execution. Pin scheme or variant, target tests, native callers, device identity and expected changed behavior before execution.
2. Read the [durable evidence guide](../references/evidence-guide.md) and create a task evidence folder outside the plugin and consumer repositories for authorized runs. Record each proposed argv or tool call and its target; retain original pre-fix evidence for bugs. If consumer execution is not authorized, report the missing authority and retain remaining run steps as blocked.
3. Run the lane's build and target tests yourself against the exact current artifact. Preserve output and result bundles. Verify executed assertion counts and target identity; record skipped assertions as skipped, retried/flaky assertions as flaky and wrong-target results as invalid for the requested target.
4. Exercise the lane's required runtime behavior and native callers on their own targets. Read [jev Drive](../references/jev-drive.md). Use available permitted jev-ios-bridge for judged screen proof, otherwise the labeled repository-compliant UI-test/device-tooling fallback. CMP requires Android and iOS UI evidence plus semantics or text-scaling evidence. Preserve artifact identity with each observation.
5. Complete the [evidence template](../references/evidence-template.md) with actual identities, command/tool results, outcomes and artifact paths; independently reopen the artifacts after authorized teardown. Finish when every applicable requirement has an inspected result or named blocker; compilation and authored instructions remain separate from observed support.

**Reply:** per-domain build, test, caller and screen outcomes, evidence folder, flaky/skipped/blocked checks and limits of fallback proof.
