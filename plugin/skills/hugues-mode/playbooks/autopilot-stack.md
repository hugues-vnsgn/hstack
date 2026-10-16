Apply [installed host tools](../../../adapters/host-tools.md): bound `read-workflow`
for owned playbook/reference rereads, `plan-check` for validation and
`plan-compare` for verification-contract changes. Neither
reads a skill body: reach each skill as [host.md](../../../adapters/host.md)
directs, and write the skill a plan step applies, never a path to read.
Unavailable or denied invocation holds that step.

For a new consumer program, apply [program proof](../../../adapters/program-proof.md)
before owner dispatch and at the existing round verification step. The root
runs `program-check` against the protected approved baseline and complete
decision/finding state before accepting STACK-READY or appending a clean link.
Enforce application write scopes and protect the installed plugin and accepted
proof. A worker's revised plan cannot replace the approved checklist. Keep the
phase order and all gates below.

For an explicitly approved mobile program, apply
[mobile coverage](../references/mobile-coverage.md) before verification dispatch.
Use its selected checks and applicability; preserve this playbook's phase timing,
review roles and operator gates. Default/non-mobile plans retain their rules.

### Autopilot-stack

**Before write-capable work:** complete [payload protection](../../../adapters/payload-protection.md)
through bound `read-workflow`. Establish native read-only protection for the bound
installation, record effective writer coverage and require it for every worker.
Missing or unverifiable protection holds dependent execution. Keep the payload
readable and report plugin defects for separate owner-authorized maintenance.

**Before unattended topology writes in Claude Code auto mode:** complete the
[stack permission preflight](../../../adapters/claude-stack-permissions.md) through
bound `read-workflow`. Record the approved repository/child branches, operator
authorization and effective configuration in the program evidence. Reuse
authorization within that scope; hold an unresolved or expanded scope. Other hosts
keep their native permission controls.

For a new program, the controller applies [program control](../../../adapters/program-control.md)
before every owner/helper/group dispatch and on pickup. Its approved scheduling
limits override parallel-owner defaults; preserve complete required groups.

**You own the stack, never the landing. Hand the operator one linear stack of base-chained PRs to review and land.** **Autopilot-full** holds except for how verified work leaves. Each tick re-reads both playbooks from trunk (`git show origin/main:skills/hugues-mode/playbooks/autopilot-full.md` and `git show origin/main:skills/hugues-mode/playbooks/autopilot-stack.md`), and this one wins where they differ.

1. **Run Autopilot-full's owners, minus the landing.** Owners report STACK-READY in place of merge-ready. They never rebase onto another branch, trunk included, and never retarget, merge, close a PR, or arm auto-merge, because the root owns the chain's topology and the operator owns the landing. When an item depends on another, its owner branches from that item's branch, not from trunk.
2. **Give the topology one writer.** Owners push only their own branches and report each tip and its intended parent. Only you rebase or retarget a link, because two writers on one chain undo each other. Append each clean PR in dependency order, with its base set to its parent's branch (`origin pr edit <pr> --base <parent-branch>` or `gh pr edit <pr> --base <parent-branch>`). Never require `gt`. An owner takes your push as its new base and lease, and on a conflict resolves its own slice for you to push. The verification-contract gate from Autopilot-full step 4 applies to every link: unresolved changes block a clean verdict and the append.
3. **Absorb drift at the root.** Until landing starts, apply Autopilot-full step 5's test to each link and rebase the chain bottom-up where it calls for one. Then apply the patch-id rule link by link, since a link's base is its parent. Re-run the verification-contract comparison for each new head or main SHA even when lane results survive by patch-id.
4. **Deliver the chain, then keep your hands off it.** Each link carries its verdict in its PR. Once landing starts, nobody writes to the chain except the post-merge retarget that `playbooks/shipping.md` sanctions, because a second writer breaks a landing in flight. A mid-landing problem goes through you to the operator, and any fix waits for the operator's go.

**Choosing between the autopilots.** Autopilot-full when the PRs are independent and landing authority is granted. Autopilot-stack when the operator wants review before landing, the work is sequenced or coupled, or merge authority is withheld.

**Reply:** catch the operator up per the **ketchup** skill, with links to the stack root and tip, a one-line verdict per link, and anything parked or excluded with the reason.
