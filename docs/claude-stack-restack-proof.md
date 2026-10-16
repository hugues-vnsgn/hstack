# Claude stack restack proof

Issue [#33](https://github.com/hugues-vnsgn/huguesStack/issues/33) keeps pstack's
rebase workflow and adds [Claude permission setup](../plugin/adapters/claude-stack-permissions.md).
This receipt records the bounded host experiment performed on 13 October 2026
before that setup reference was authored. It does not establish installed setup
execution or the complete unattended stack workflow.

## Observed environment

The private disposable GitHub fixture contained the original mobile consumer's
B05 parent and B06 child commits. Its GitHub Actions were disabled. Claude Code
2.1.293, with `claude-opus-5-5`, ran in auto mode with permission prompts disabled.
Only Bash was available; MCP servers and hooks were disabled. Invocation settings
held `classifyAllShell: true` constant so shell allow rules could not skip the
classifier. No persistent profile settings or live consumer branches changed.

The historical replay copied the original conversation through the pending
push, remapped repository/worktree/branch references into the fixture and forked
that copy. The original session was not resumed. Both default-rule runs and the
configured run used that same input snapshot and user prompt. Claude generated
equivalent expected-SHA lease commands rather than byte-identical Bash calls.

## Results

| Probe | Observed outcome |
|---|---|
| Fresh-session original two-commit rebase, mobile compile and lease push | Pass without an exception |
| Historical-context replay with default configuration | Mobile compile passed; lease push denied as `Git Destructive`; remote unchanged |
| Same historical replay and defaults, repeated | Same denial and unchanged remote |
| Same replay with one repository/child-branch-scoped `autoMode.allow` entry | Mobile compile and lease push passed without a denial |
| Forced mobile compile after that push | Exit 0; `BUILD SUCCESSFUL`; `19 actionable tasks: 19 executed` |
| Deliberately stale expected-SHA lease | Git rejected it with `stale info`; remote unchanged |
| Scoped exception plus an explicit `permissions.deny` push rule | Permission layer rejected the tool call; command did not execute |

The compile command after the push was:

```sh
./gradlew :shared:compileAndroidMain :shared:compileKotlinIosSimulatorArm64 --rerun-tasks --no-build-cache
```

The pushed child contained the intended parent and matched the local rebased
head. Its base-to-head stable patch-id before and after the rebase was
`63bc00c3b9ebffae720b752aeec578fd41f6983c`. The configured allow array retained
`$defaults`. Native `claude auto-mode config` confirmed one additional allow entry
and unchanged `soft_deny`, `hard_deny` and trusted-environment lists.

Raw CLI streams, configuration snapshots, Git assertions and build logs remain
in the owner's private issue-33 diagnostic artifacts. The
[triage brief](https://github.com/hugues-vnsgn/huguesStack/issues/33#issuecomment-6142773678)
records the result and the approved implementation contract. These observed
probes are separate from the repository's top-level unittest count.

## Candidate setup check

A session-local load of the implementation candidate on Claude 2.1.296 invoked
`setup-huguesstack` for permissions only. It generated the reviewed JSON fragment
from the new reference, captured effective configurations and left the model-role
file and persistent profile settings unchanged. Its scripted snapshot comparison
was refused as `Instruction Poisoning`; it held and reported that gap.

A separately authorized read-only native review completed the audit and wrote
its scope record without a denial. An independent exact JSON comparison confirmed
one added allow entry and unchanged remaining lists in both captured settings
variants. The candidate-generated fragment then passed the historical restack
replay on Claude 2.1.293, including both mobile compile targets and the real
lease-protected GitHub update. Raw candidate setup/replay streams and snapshot
comparisons remain with the private diagnostic artifacts.

This is bounded native setup evidence with an initial refused check and a
separate authorized completion, not an uninterrupted setup pass. The root restack
uses the existing workflow; the full installed program remains unobserved.

## What this supports

A scoped classifier exception permits the reproduced root-on-delegated-owner
restack on Claude 2.1.293 while preserving the lease and explicit-deny boundaries.
Fresh sessions passed without it, so a lease push is not universally blocked.
The accumulated conversation was part of the reproducing conditions; the
individual message or internal classifier interpretation responsible was not
isolated. The original compile-only refusal after a denied push was not
separately reproduced.

The real Gradle targets cover KMP shared compilation for Android and the iOS
ARM64 simulator. They do not prove native Swift/Android app behavior or CMP UI
journeys. Public remotes, other versions under this replay configuration,
PR retargeting/landing, CI, devices, the full unattended loop and uninterrupted installed setup
execution remain gaps. Source/package checks prove wiring only.

Since the 0.4.0 rename, the recipe's allow rule says "hStack approved topology
restack" where the observed runs used "HuguesStack". The renamed wording has not
been replayed.

Claude's supported settings scopes and precedence are documented in
[Anthropic's auto-mode configuration reference](https://code.claude.com/docs/en/auto-mode-config).
