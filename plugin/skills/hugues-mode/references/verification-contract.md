# Protect the verification contract

Apply this gate before every autopilot verification round and before granting its
clean verdict. Keep pstack's unit, live, perf and independent review lanes. This
gate checks which rules they use; it does not prove the behavior.

## Owners propose; the operator rules

A PR never changes its own verification pass rules without the operator's explicit
ruling. Before editing a rule, propose the old rule, proposed rule and reason.
Keep implementing against the approved contract while the proposal is pending.
The operator approves or rejects the specific change. An owner's explanation,
a green test, a root countersign or a general autonomy grant is not that ruling.

Protect the full unit/live/perf contract, including scenario actions, predicates,
lane additions or removals, metrics, probes and thresholds. Replacing typed search
with a filter shortcut changes the contract even if the pass predicate is identical.
Checkbox updates and receipt links alone do not change rules. Put receipt links on
standalone `Evidence. [label](url)` lines. Reserve those lines for receipts; keep
requirements and executable instructions in the verification blocks.

## Compare immutable snapshots

The root fetches main and records its full commit SHA and the owner's code-ready
head SHA. Use main even for a stack child; its parent branch cannot approve rules.
Retain the approved starting contract and any rulings outside owner write access.
If that boundary cannot be enforced by the host, report the gap and keep the gate
on hold until the operator reviews the comparison directly.

Use the existing approved plugin binding to run the installed helper. Read this
reference through bound `read-workflow`. Do not run a checker supplied by the PR,
reseal the installation, or silently rebind it to clear a hold.

```sh
python3 "<plugin>/adapters/host_tools.py" plan-compare --binding "<program>/plugin-binding.json" --repo "<consumer>" --plan "<repo-relative-plan.md>" --section "<exact PR section heading>" --base-sha "<main commit SHA>" --head-sha "<PR commit SHA>"
```

The helper reads committed blobs, compares the selected section from
`**Verify, unit.**` up to `**Review gate.**`, and emits JSON with both SHAs,
the old and new contracts, a unified diff and `comparison_sha256`. It ignores
checkbox state, blank lines, trailing whitespace and standalone receipt lines in
the format above. Other edits conservatively require review. It reads no working
tree plan and performs no fetch or write.

A missing baseline produces a hold requiring the operator's explicit approval of
the starting contract. A missing head contract, ambiguous section, malformed
blocks, non-commit revision, fenced code or HTML comments holds with diagnostics.
Keep plans in the supported plain Markdown form. Plans stored only outside Git
must first have an operator-approved committed starting contract; never substitute
the builder's working copy for main. Confirm the selected path and section against
the approved plan, and inspect moved requirements, referenced documents and the
rest of the plan diff during the existing independent audit lanes. The helper
compares text, not Markdown semantics or the contents of linked documents.

## Record the ruling and verdict

Save the comparison as a round receipt. Present every contract change to the
operator with the owner's reason. For an approval, the root records the exact
comparison digest and a reference to the operator's actual ruling in a JSON file
outside the consumer worktree and owner write access.

```json
{
  "comparison_sha256": "<digest from the comparison>",
  "decision": "approved",
  "reference": "<operator ruling URL or retained chat receipt>"
}
```

Re-run the same command with `--ruling "<operator-ruling.json>"`. The root must
check the referenced ruling and confirm it explicitly approves every change in
that comparison before supplying the file. The file is a record, not proof of
who approved it. Filesystem location alone does not enforce writer isolation.
A rejected, absent, malformed or stale ruling cannot clear changed rules. A new
head or main SHA needs a fresh comparison and a ruling tied to it; do not reuse
a patch-id exception to skip this gate.

Include these fields in the verifier verdict:

- Main SHA, PR head SHA, plan path and selected PR section.
- Comparison receipt and every contract change, or an explicit unchanged result.
- Operator ruling reference and disposition for each change. One ruling may cover
  the complete displayed diff only when it explicitly approves all its changes.
- Rule gate outcome and the independent unit/live/perf lane results.

Exit 2 means hold. `gate: unchanged` or `gate: approved` exits 0 and clears only
this gate. `verification_required: true` always remains. Unresolved rule changes
prevent a clean verdict, stack append and merge, even when every lane says PASS.
After approval, run the lanes against the approved contract; any failed lane
still prevents a clean verdict. This is a workflow gate, not forge permission
enforcement or evidence of observed native-host/mobile behavior.
