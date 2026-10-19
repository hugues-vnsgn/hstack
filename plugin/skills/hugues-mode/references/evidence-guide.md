# Durable mobile evidence

Use this guide before executing a mobile proof and when writing `evidence.md`. Keep one task folder outside both plugin and consumer repositories, normally `~/hstack-evidence/<date>-<task>/`. Choose a writable equivalent when that location is unavailable and disclose it. Preserve raw results and artifacts there before removing any scratch checkout or run state. This is plain Markdown guidance, with no report parser, runtime or evidence schema.

## Before the run

Start from the [evidence template](evidence-template.md). Record the goal, expected behavior and authority; plugin SHA; host/version; consumer repo, worktree and SHA; domains; schemes/variants; targets and explicit device identifiers. Record the dirty diff and relevant untracked file receipts that change the tested artifact. A SHA alone cannot identify an uncommitted build. Store private diff receipts locally, excluding credentials and irrelevant user data.

Plan a separate attempt directory for each target and retry. Record a read-only target health check and the baseline for the agreed journey. Bug claims require the original failing observation on the claimed runtime before a fix. A source mismatch without runtime reproduction is a source finding, not an observed UI defect.

## Record each execution

For a shell command, record the exact argv array, working directory, process-local environment changes, timestamps, exit code and log/result paths. Redact secret values explicitly; retain names needed to understand the invocation. Keep denied and failed attempts with their actual result; an unrun command has no exit code.

For MCP or host actions, record the actual tool name, structured arguments, response status/error and saved response/artifact paths. Do not invent argv or a process exit code for a tool call. Include the tool version or server identity when observable; mark unknown values unknown. A server name in config establishes no successful call.

For builds, tie the app/APK/framework path and hash to the artifact installed or launched. For several test report files, retain each original path, invocation, suite/test identity and target association; explain overlap before totaling assertions. Inspect executed relevant assertions, skips and retries, not just a green command exit. Keep target/device identity with every result.

For runtime proof, capture the action sequence and resulting state, not just a final screenshot. Inspect required native callers on each side of a shared boundary. Record screenshots, hierarchy/semantics observations and text-scaling conditions per target where required. Keep screen-text verdicts separate from visual layout observations; jev judges text and does not certify clipping or pixel layout.

## Build/test helper attempts and artifact identity

Run selected Xcode, SwiftPM and consumer Gradle checks through the
[native helpers](../../../adapters/native-execution.md). Keep the bounded summary,
invocation, raw logs, native copies and report manifest for every attempt.
Unknown counts stay unknown; zero selected tests cannot pass. Keep failed RED,
GREEN and retry attempts separate, even after a later pass. If automated testing
is impractical, retain its specific reason and executable runtime reproduction
without claiming automated RED/GREEN.

Before installing, compare the current built artifact's path and hash with the
installed/launched artifact receipt and explicit target. A stale artifact or
different target invalidates the claimed proof. Record each action and resulting
state with assertions or native caller observations. Keep functional observations
separate from screenshots and hierarchy/semantics evidence. One CMP runtime or a
JVM test cannot satisfy the other required native boundary. After task-owned
cleanup, reopen the helper's retained copies and the runtime artifacts.

## Judge and retain

A step counts as passed only with evidence that it was reached. The absence of an error that would appear later is not proof that an earlier step passed. Retain that step's command output or tool response and its actual result.

Use the [mobile lane outcome rules](mobile-lanes.md#evidence-and-outcomes). Report failed attempts and flaky assertions even after a later pass. A different target's result supplies no proof for the missing target. A tool denial or missing permitted capability is a named blocker, not authority to bypass it.

Record the actual jev verdict, reason code, decisive checkpoint and report path. If no judged verdict exists, label **no judged verdict** and state what the alternative directly observed. Keep build/test/runtime outcomes separate and disclose unrun checks. Record reviewed revision, reviewer host/model, findings and their resolution separately from mobile proof.

After authorized teardown, reopen the evidence and inspect that its logs, result bundles and images remain readable. Report any missing artifact as an evidence gap. Keep private consumer source, paths, selectors, screenshots and reports local; publish only an explicitly authorized sanitized framework summary.
