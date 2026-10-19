# Evidence: <date> / <task>

Copy this plain Markdown outline into the private task evidence folder. Replace prompts with observed values; use unknown, unrun or blocked with the reason where needed. It is not a schema and filling it is not proof.

## Scope and identity

- Goal, expected behavior and granted authority: <facts>
- Plugin SHA; host and version; reviewer model/effort if applicable: <facts>
- Consumer repo/worktree and SHA; carried dirty diff/untracked receipts: <local paths and hashes>
- Domains, selected schemes/variants, target tests and native callers: <facts>
- Devices: <per-target UDID/serial, runtime/API, dimensions and text-scale conditions>
- Evidence folder and artifact privacy boundary: <local path>

## Preflight

- Bash sandbox on/off; host/version; OS; tool versions: <observed values>
- Proof-tool checks before lane planning: <one real harmless operation per required tool, argv or structured arguments, exit code or response status, output paths, works/blocked>
- Dropped or replaced lanes and gaps: <blocked tool and affected lane>
- Host baseline after a blocked result: <same operation, target and working directory outside the agent; label sandbox-off agent shell or owner's plain terminal>
- Baseline versions, time and last good run: <facts from earlier evidence, or unknown>
- Baseline outcome: <host blocker reported to owner and settings iteration stopped; passing baseline routed to build-doctor; or blocked pending result>

## Baseline

<Original behavior, target/device, build identity and observations. For a bug, link the pre-fix failing observation. Distinguish source findings from reproduced behavior.>

## Attempts

### <target>/<attempt>

- Time; purpose; working directory: <facts>
- Command argv array and environment changes, OR actual tool name/structured arguments: <facts, secrets redacted>
- Exit code for a process, OR tool result/status: <actual value; absent if unrun>
- Original logs, reports and response files: <separate paths for every result file>
- Native helper attempt and summary: <exact retained invocation, raw logs, native copies and report manifest; command status separate from interpretation; unknown counts preserved>
- Regression phase: <independently observed RED/GREEN on the same regression, or concrete impractical-test reason and executable runtime reproduction; no automated RED/GREEN claim for the exception>
- App/APK/framework identity and installed/launched artifact association: <path/hash>
- Current artifact/target check: <comparison with the built artifact and explicit target; stale or wrong-target results excluded>
- Tests: <relevant executed assertions, failures, skips, retries, suite/test identities and target provenance>
- User actions and observed checkpoints/native callers: <observations and paths>
- Screen/semantics/text-scaling artifacts: <paths and conditions>
- Jev verdict, reason code and decisive checkpoint: <recorded result/report, or no judged verdict>
- Outcome and limits: <pass/fail/flaky/skipped/incomplete; wrong-target exclusions and blocked checks>

## Review and final assessment

<Exact reviewed revision/diff, reviewer host/model/effort, independence label, findings and adjudication.>
<Per-domain build, tests, native callers and runtime outcomes. Support states remain separate from run outcomes.>
<Unrun/blocked checks, missing prerequisites and next permitted action.>

## Teardown and evidence survival

<Owned instances/scratch state removed or retained, action/result, and post-teardown readable artifact paths. Keep the original attempts and evidence folder.>
