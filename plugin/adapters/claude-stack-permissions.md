# Claude auto-mode stack permissions

Read this reference for Claude Code auto-mode `autopilot-stack` setup or before
its unattended topology writes. Keep pstack's rebase and lease-protected push
strategy, root-only topology ownership, verification and operator landing gates.
This recipe supplies a scoped classifier exception, not new task authority.
Other hosts use their native controls.

## 1. Establish the authorized scope

Record the configured remote, repository identity, trunk/release refs, exact
unmerged child-branch names and the operator's topology grant. Inspect with:

```sh
git remote get-url origin
git ls-remote --symref origin HEAD
claude --version
claude auto-mode config
```

Use the active `CLAUDE_CONFIG_DIR` profile when one is configured. Check the
consumer's standing orders and existing ask/deny rules too. A permission rule
cannot override an operator hold or a consumer's prohibition on rebasing.
Hold topology work if authority, branch ownership or the applicable configuration
is unresolved. Record any tools or settings that could not be inspected as gaps.

## 2. Propose the scoped exception

Replace `REPOSITORY_URL` and `CHILD_BRANCH` with concrete approved values. Use one
entry per approved child branch; exclude trunk, release and unrelated refs.
Show the complete proposed settings change before applying it. Existing scope
authorization carries forward; widening it or changing persistent settings
requires the operator's authorization for that change.

```json
{
  "autoMode": {
    "allow": [
      "$defaults",
      "hStack approved topology restack: Only in repository REPOSITORY_URL, allow the appointed topology root to publish the unmerged delegated-owner branch CHILD_BRANCH with git push --force-with-lease=CHILD_BRANCH:<expected-current-remote-SHA> after fetching and checking its exact remote tip. This is the operator-approved autopilot-stack rebase preserving the child patch, including commits written by delegated owners. This exception grants no authority over trunk, default or release branches, other refs or repositories, bare --force, ref deletion, discarded unrelated work, PR landing, or any operator-held action."
    ]
  }
}
```

Merge the entry into the existing allow array, retaining custom entries and
`$defaults`. Preserve other settings, including `permissions.ask`,
`permissions.deny`, `soft_deny`, `hard_deny` and trusted-environment entries.
If an existing array intentionally omits `$defaults`, get the operator's ruling
before restoring defaults; do not silently replace their policy. Do not add
blanket Bash allowances or disable permission checks.

The classifier accepts prose rules from user settings (normally
`~/.claude/settings.json`, under the active profile), managed settings or
invocation settings. It ignores `autoMode` in project `.claude/settings.json`
and `.claude/settings.local.json`. For a bounded run, save the reviewed fragment
in an operator-approved settings file outside the consumer repository and use:

```sh
claude --settings /absolute/path/stack-permissions.json auto-mode config
claude --settings /absolute/path/stack-permissions.json --permission-mode auto
```

These are invocation settings, even though the file is external. Keep existing
CLI settings options as well. For a persistent profile, edit only the reviewed
allow entries after authorization. The effective configuration must contain the
concrete scoped exception and retained defaults/custom entries. Compare it with
the pre-change output and hold unexpected changes. If a setup inspection is
denied, record the command/reason and hold that step until the operator authorizes
that exact review or completes it; do not widen the exception to unblock setup. Record the authorization,
settings scope, effective configuration and version in the program evidence.
Scope constraints in prose guide the classifier; they are not Git access controls.

## 3. Restack within that scope

The root coordinates with the child owner, fetches the exact intended parent,
records the current remote child SHA and rebases the child. Just before pushing,
check that `ls-remote` still reports that recorded SHA. Use an explicit lease:

```sh
git push --force-with-lease=CHILD_BRANCH:EXPECTED_REMOTE_SHA origin HEAD:refs/heads/CHILD_BRANCH
```

A changed remote tip holds the push; coordinate with the owner rather than
refreshing the lease blindly. Reuse the approved permission scope during the
run, and obtain a new ruling before adding a branch or repository to it.
Apply the existing shipping patch-id rules, verification-contract comparison,
fresh mergeability/CI checks and re-verification requirements. A matching
patch-id does not skip those checks.

If Claude denies the operation, preserve the exact command, reason, effective
settings and affected branch in evidence. Hold dependent topology work, continue
only independently authorized work, and report the unresolved permission.
Keep the rebase strategy; do not retry through another tool, weaken settings,
or substitute parent merges to evade the denial. Explicit ask/deny rules and
operator holds still apply; this exception addresses classifier soft blocks.

## Evidence and limits

[Issue 33's observed proof](https://github.com/hugues-vnsgn/hstack/issues/33#issuecomment-6142773678) records two
default-rule denials and a configured success on Claude 2.1.293 in a private
GitHub mobile fixture. Treat other host/version/target combinations and installed
setup execution as gaps until observed. Missing auto-mode CLI/configuration
support holds this setup step; do not infer compatibility from a version number.
See [Anthropic's configuration reference](https://code.claude.com/docs/en/auto-mode-config)
for settings scopes, effective configuration and rule precedence.
