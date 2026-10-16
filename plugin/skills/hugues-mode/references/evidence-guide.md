# Durable mobile evidence

Use this guide before executing a mobile proof and when writing `evidence.md`. Keep one task folder outside both plugin and consumer repositories, normally `~/hstack-evidence/<date>-<task>/`. Choose a writable equivalent when that location is unavailable and disclose it. Preserve raw results and artifacts there before removing any scratch checkout or run state. The Markdown report records the full capture trail. New programs also use the small checked index in [program proof](../../../adapters/program-proof.md); the outline alone cannot certify a pass.

## Before the run

Start from the [evidence template](evidence-template.md). Record the goal, expected behavior and authority; plugin SHA; host/version; consumer repo, worktree and SHA; domains; schemes/variants; targets and explicit device identifiers. Record the dirty diff and relevant untracked file receipts that change the tested artifact. A SHA alone cannot identify an uncommitted build. Store private diff receipts locally, excluding credentials and irrelevant user data.

For new programs, link the protected approved checklist and its trusted digest.
The controller retains accepted records separately from worker output. Compare
against that original, never a builder's edited pass rules.

Plan a separate attempt directory for each target and retry. Record a read-only target health check and the baseline for the agreed journey. Bug claims require the original failing observation on the claimed runtime before a fix. A source mismatch without runtime reproduction is a source finding, not an observed UI defect.

## Record each execution

For a shell command, record the exact argv array, working directory, process-local environment changes, timestamps, exit code and log/result paths. Redact secret values explicitly; retain names needed to understand the invocation. Keep denied and failed attempts with their actual result; an unrun command has no exit code.

For MCP or host actions, record the actual tool name, structured arguments, response status/error and saved response/artifact paths. Do not invent argv or a process exit code for a tool call. Include the tool version or server identity when observable; mark unknown values unknown. A server name in config establishes no successful call.

For builds, tie the app/APK/framework path and hash to the artifact installed or launched. For several test report files, retain each original path, invocation, suite/test identity and target association; explain overlap before totaling assertions. Inspect executed relevant assertions, skips and retries, not just a green command exit. Keep target/device identity with every result.

For runtime proof, capture the action sequence and resulting state, not just a final screenshot. Inspect required native callers on each side of a shared boundary. Record screenshots, hierarchy/semantics observations and text-scaling conditions per target where required. Keep screen-text verdicts separate from visual layout observations; jev judges text and does not certify clipping or pixel layout.

## Judge and retain

Use the [mobile lane outcome rules](mobile-lanes.md#evidence-and-outcomes). Report failed attempts and flaky assertions even after a later pass. A different target's result supplies no proof for the missing target. A tool denial or missing permitted capability is a named blocker, not authority to bypass it.

Record the actual jev verdict, reason code, decisive checkpoint and report path. If no judged verdict exists, label **no judged verdict** and state what the alternative directly observed. Keep build/test/runtime outcomes separate and disclose unrun checks. Record reviewed revision, reviewer host/model, findings and their resolution separately from mobile proof.

After authorized teardown, reopen the evidence and inspect that its logs, result bundles and images remain readable. Report any missing artifact as an evidence gap. Keep private consumer source, paths, selectors, screenshots and reports local; publish only an explicitly authorized sanitized framework summary.

Generate new-program claims from `program-check` output after independent
inspection. Name actual outcomes, including crash, remaining defects/data
anomalies, missing proof and every open owner decision. Keep unsuccessful
reproductions and retries; one failure to reproduce does not resolve an anomaly.
