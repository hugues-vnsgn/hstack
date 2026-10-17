---
status: accepted
---

# Follow pstack's run safety model

hStack keeps unattended runs safe the way pstack does: a checkable finish condition, an isolated worktree or cloud agent, a decision log the operator audits afterwards, and the permissions the run needs written into its handoff. It adds no payload or plugin write protection.

From 0.4.0 until 2026-10-17 the autopilots did add it. Before any write they required a host-enforced read-only boundary around the installed plugin, and they sent plugin defects to separate owner-authorized maintenance. Per-host policy fragments, a macOS mobile recipe, a Bun helper readiness check and a native boundary regression existed only to support that. Every problem in the #53 mobile work came from this layer, and an hStack that diverged from pstack confused the owner, who withdrew it on 2026-10-17 (#77).

A skill that breaks mid-run is now fixed by the agent in its own PR against the hStack repository, as pstack's autonomous-run step 4 says, never by editing the installed cache. The plugin binding, manifest digest, guarded reads and drift checks stay, so an edited installed copy holds the run where the operator can see it.

The rule for this and later alignment work: follow the original pstack, and remove whatever pstack lacks unless it is a mobile adaptation.

## Consequences

- Under an operator's full-autonomy grant, an hStack skill-fix PR goes from opening to merge on a clean verdict, as in pstack. Lab installs that track `main` pick up that fix on their next run without a manual review; the owner accepted this to match pstack.
- Approved-checklist, accepted-proof and control-directory protection stay for now. [#78](https://github.com/hugues-vnsgn/hstack/issues/78) decides their fate under the same rule.
