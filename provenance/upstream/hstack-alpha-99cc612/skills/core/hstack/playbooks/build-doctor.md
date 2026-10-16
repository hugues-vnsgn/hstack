# Build-doctor

1. Capture the failing command, output, environment, and expected artifact.
2. Diagnose and reproduce through repository evidence and safe experiments in
   the coordinator. Determine whether the user requested diagnosis or a repair.
3. For diagnosis only, report the cause, evidence, and unresolved facts. Stop
   without implementation delegation or edits.
4. For an authorized repair, load relevant leaves and Active Stack Pack guidance,
   establish the checkout through `use-git-worktree` when its trigger matches,
   and brief one implementer with the cause, fileset, and original failing check.
5. Delegate implementation/configuration edits through the
   [delegation contract](../references/delegation.md). If delegation is
   unavailable, report blocked and retain coordinator diagnosis without coding.
6. Inspect the actual diff and rerun the original failure plus appropriate
   checks and pack proof. Send corrections back to the implementer.
7. Report the cause, child/result reference, artifacts, observed proof, and
   limitations. PR and shipping actions require a separate request.
