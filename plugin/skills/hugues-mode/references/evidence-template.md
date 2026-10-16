# Evidence: <date> / <task>

Copy this plain Markdown outline into the private task evidence folder. Replace prompts with observed values; use unknown, unrun or blocked with the reason where needed. It is not a schema and filling it is not proof.

## Scope and identity

- Goal, expected behavior and granted authority: <facts>
- Plugin SHA; host and version; reviewer model/effort if applicable: <facts>
- Consumer repo/worktree and SHA; carried dirty diff/untracked receipts: <local paths and hashes>
- Domains, selected schemes/variants, target tests and native callers: <facts>
- Devices: <per-target UDID/serial, runtime/API, dimensions and text-scale conditions>
- Evidence folder and artifact privacy boundary: <local path>
- New program: protected approved checklist, trusted digest, binding and candidate record: <controller-held paths; actual approval reference>

## Baseline

<Original behavior, target/device, build identity and observations. For a bug, link the pre-fix failing observation. Distinguish source findings from reproduced behavior.>

## Attempts

### <target>/<attempt>

- Time; purpose; working directory: <facts>
- Command argv array and environment changes, OR actual tool name/structured arguments: <facts, secrets redacted>
- Exit code for a process, OR tool result/status: <actual value; absent if unrun>
- Original logs, reports and response files: <separate paths for every result file>
- App/APK/framework identity and installed/launched artifact association: <path/hash>
- Tests: <relevant executed assertions, failures, skips, retries, suite/test identities and target provenance>
- User actions and observed checkpoints/native callers: <observations and paths>
- Screen/semantics/text-scaling artifacts: <paths and conditions>
- Jev verdict, reason code and decisive checkpoint: <recorded result/report, or no judged verdict>
- Outcome and limits: <pass/fail/flaky/skipped/incomplete; wrong-target exclusions and blocked checks>

## Review and final assessment

<Exact reviewed revision/diff, reviewer host/model/effort, independence label, findings and adjudication.>
<Per-domain build, tests, native callers and runtime outcomes. Support states remain separate from run outcomes.>
<Unrun/blocked checks, missing prerequisites and next permitted action.>
<New program: derived program-check verdict and inspected record. Actual user-visible outcome, including crash; remaining defects/unexplained data changes; missing proof; every unresolved owner decision. Keep passed, failed, untested, blocked, inconclusive and owner-waived checks distinct.>

## Teardown and evidence survival

<Owned instances/scratch state removed or retained, action/result, and post-teardown readable artifact paths. Keep the original attempts and evidence folder.>
