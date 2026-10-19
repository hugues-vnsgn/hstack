# Build doctor

source: Conceptual adaptation of hstack-alpha (retired predecessor; GitHub osxsystem/hstack, deleted 2026-10-16; bytes retained in `provenance/upstream/hstack-alpha-99cc612/`) at `99cc6129aea3f702ee6cd3b448e4f67700b4353c`, `skills/core/hstack/playbooks/build-doctor.md`; hStack first-release requirements. No managed-worker runtime is imported.

Diagnose first. Repair only within explicit authority.

For Xcode, SwiftPM and consumer Gradle reproduction or verification, read
[native execution](../../../adapters/native-execution.md) and run its helper
with the explicit consumer command, context and target. Resolve missing identity
before execution. Retain each attempt's bounded summary, raw logs and native
reports; distinguish command failure from unavailable tools or incomplete results.

## Steps

1. Capture the failing argv, exit code, relevant output, environment, selected target and expected artifact. Read repository instructions, [mobile lanes](../references/mobile-lanes.md) and the [evidence guide](../references/evidence-guide.md) before choosing experiments. Capture tool calls as tool calls, with their real response status.
2. Diagnose with repository evidence and authorized safe reproduction. Separate a code/configuration defect from a missing tool, SDK, license, signing capability, runtime or wrong target. Before changing agent settings or attributing a blocked proof tool to the agent environment, require the [host baseline](../references/mobile-lanes.md#host-baseline). Run the same operation outside the agent. With the sandbox off, the agent's shell counts and is labelled as such; with it on, the owner runs the printed command in a plain terminal. Record tool versions, time and the last good run from earlier evidence, or `unknown`. If the baseline fails, report a host blocker to the owner and stop iterating on agent settings. If it passes, investigate the agent-environment defect here. If it is unrun, hold that attribution and settings changes. A missing required MCP tool does not authorize an otherwise prohibited CLI alternative. Finish with a supported cause or a precise unresolved hypothesis.
3. Determine whether the owner requested diagnosis or scoped repair. Diagnosis-only ends with the evidence and blockers; retain later steps with skip reasons. A generic mode request grants no consumer edit/execution authority or permission to change global SDKs, JDKs, licenses, credentials or system settings.
4. For an authorized repair, establish the scoped checkout and brief a fresh implementation subagent with cause, owned files, permitted changes and original failing check. Prefer process-local configuration within that authority; report system changes as required permissions. The worker owns its diff directly and does not recursively delegate.
5. Inspect the actual diff and rerun the original command yourself, then the lane's relevant build, tests and runtime proof. Give every correction round to a fresh worker; retain every unavailable check with its missing prerequisite.
6. Obtain an independent fresh review of the cause and repair. Resolve findings and repeat coordinator verification; [opening a PR](opening-a-pr.md) prepares local review material unless publication is separately authorized.

**Reply:** cause, exact command outcomes, repair scope, evidence paths and remaining permission or tool blockers.
