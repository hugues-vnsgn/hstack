# Approved requirements and inspected proof

Apply this contract to new consumer programs before their first build. Keep the
selected playbook's phases, worker roles, gates and invocation controls. Reuse
its existing plan approval; do not add an approval per test. Keep an active
program on its approved installation until the owner explicitly migrates it.
Do not certify an old report by filling in missing observations afterward.

## Freeze the rules at plan approval

1. Resolve the installed plugin from the loaded entrypoint. Save its binding
   using [host tools](host-tools.md). Keep it for the whole program; drift holds
   the run for review. Plugin maintenance is a separate authorized task.
2. Create an owner control directory outside the plugin and consumer checkouts.
   Only the trusted controller writes accepted records there. Put the binding,
   design snapshots, approved checklist, candidate, accepted proof and current
   coordinator state there. Keep worker scratch/attempt output elsewhere.
3. Read the relevant design sources, including bundled prototype content.
   Extract compressed fields as data. For an extracted base64/gzip field use:

   ```sh
   python3 "<plugin>/adapters/host_tools.py" decode-design --binding "<control>/plugin-binding.json" "<control>/prototype.base64" > "<control>/prototype.txt"
   ```

   This decoder accepts UTF-8 text up to 4 MiB and executes no HTML or scripts.
   Keep both raw and decoded snapshots with their hashes and original locator.
   Unsupported formats or omitted content remain a named gap; never execute a
   bundle to discover its rules. Inspect the text, not just the wrapper page.
4. For each requirement record its source, expected behavior, target and planned
   actions in `approved.json`, following [record format](program-records.md).
   Settle conflicting sources with an explicit owner decision at plan approval.
   Include that decision as a source snapshot; no implicit last-file-wins rule.
5. Obtain the owner's approval of that exact checklist. Retain the real message
   reference and SHA256 in controller-held state outside worker write access.
   A JSON field or hash does not authenticate approval. Do not regenerate the
   trusted digest from a worker's copy. Builders may propose corrections; the
   controller asks the owner, creates a new revision and reassesses proof before
   using one. Builders never revise their own pass conditions.

## Enforce the write boundary before dispatch

Pass workers the checklist and only the application paths authorized for their
change, plus separate scratch/output directories. Protect the entire owner
control directory, installed plugin and binding. Read-only Markdown and hash
checks detect drift; they do not deny a write.

For local macOS worker processes, use this installed launcher:

```sh
python3 "<plugin>/adapters/host_tools.py" worker-run --binding "<control>/plugin-binding.json" --approved "<control>/approved.json" --approval-sha256 "<trusted-digest>" --writable "<authorized-app-worktree>" --writable "<worker-output>" --cwd "<authorized-app-worktree>" -- <native-worker-executable> <literal-arguments>
```

The launcher uses macOS `sandbox-exec` to deny writes outside the supplied roots
for the process and its children. It rejects overlapping protected roots and
hardlinked protected files. It does not install tools or fall back to an
unprotected process. Add an existing cache/temp root only within owner-approved
scope; never grant the home directory or an ancestor of protected files.

Remote MCP servers, host file-edit tools outside that process, IPC services and
other host processes are outside this process guard. Disable their write access
or enforce the same boundary in the native host before using them. Native agent
tools require verified equivalent enforcement; a read-only role label is not
enforcement. If the host cannot enforce the boundary, hold dependent worker
execution and name the missing capability. Do not bypass the hold by switching
to a broader tool. The macOS subprocess boundary has local regression coverage;
completed Claude Code/Codex worker journeys remain a separate observation gap.

## Accept proof for one frozen build

The controller records the actual source commit and dirty/untracked receipts,
and fingerprints the whole artifact installed or launched:

```sh
python3 "<plugin>/adapters/host_tools.py" artifact-hash --binding "<control>/plugin-binding.json" "<absolute-build-path>"
```

Files use SHA256; directories use the versioned tree digest, including names,
file modes and resources. Empty builds, symlinks, hardlinks and unsupported entries
hold. Use a regular exported build if its original bundle contains links.
Freeze that source/build for the round. A later edit creates a new candidate and
requires an explicit evidence assessment. A matching patch-id alone does not
carry behavioral evidence to another build. Keep prior rounds separately.

Have an independent verifier run the approved actions on the named target,
record actual results and retain each attempt. Bind artifacts to the attempt,
build, platform and capture time. Inspect artifact contents and the capture
trail against the actual tool/build receipt before accepting them. An old image
with new labels is invalid. Reopen logs/images; a path's existence proves nothing.
Export a readable summary for unsupported image/result formats and retain the
original bundle. The checker accepts nonempty UTF-8 text, strict JSON and bounded
8-bit noninterlaced PNGs; it cannot judge what a screenshot means.

The trusted controller copies inspected artifacts and accepted records into the
protected directory. Record the actual builder/verifier IDs and independent
inspection receipt. Different strings establish no process independence by
themselves. Export **every** unresolved owner decision from the coordinator's
single current decision list (for the bundled store, `gates.list()`), and all
remaining defects or unexplained data changes to `state.json`. Do not let a
worker replace that state with its recollection. A failed reproduction leaves a
stored-data anomaly open until a supported resolution is recorded.

At the existing verification/verdict step run:

```sh
python3 "<plugin>/adapters/host_tools.py" program-check --binding "<control>/plugin-binding.json" --approved "<control>/approved.json" --approval-sha256 "<trusted-digest>" --candidate "<control>/candidate.json" --record "<control>/proof.json" --state "<control>/state.json" > "<control>/verdict.json"
```

Exit 0 supports a clean verdict only after the independent inspection and all
other playbook gates. Exit 2 holds it. Preserve diagnostics; never turn a checker
error into an empty successful report. Binding failures can stop before a JSON
report exists. Null finding/decision lists on an invalid-record hold mean their
completeness is unknown, not that nothing remains.

## Report the derived verdict

Write proof claims from the accepted record and derived verdict. Name actual
user-visible outcomes, including **crash**, remaining defects/data anomalies,
missing proof and all unresolved owner decisions. For calculations, include the
independently computed expected value and observed value in the source/attempt
receipts. Do not infer a pass from a green process exit or free-form recollection.

Keep passed, failed, untested, blocked, inconclusive and explicitly owner-waived
checks distinct. A waiver references the controller's real owner approval and
reason; it never becomes a passed test or an automatic clean verdict. Retain
failed attempts after retries; a later pass requires an inspected resolution
receipt. One unsuccessful reproduction is not a resolution.
