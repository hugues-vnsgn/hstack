# hStack 0.5.0

## Unreleased

- **Payload protection is withdrawn** ([#77](https://github.com/hugues-vnsgn/hstack/issues/77)). Autopilot-full and autopilot-stack no longer require a host-enforced read-only boundary around the installed plugin before write-capable work. The `payload-policy` and `helper-ready` host-tool verbs, the `--macos-mobile` recipe and the native payload-boundary regression are gone, and `worker-run` no longer treats the installed plugin or its binding as protected paths. pstack never had this layer. In hStack it turned a broken skill into a run that waited for the owner, and every problem in the #53 mobile work came from it. A mid-run skill fix now follows pstack's autonomous-run step 4: the agent fixes the skill in its own PR against the hStack repository. The plugin binding and drift checks stay, so an edit to the installed copy still holds the run. [ADR 0001](adr/0001-follow-pstack-run-safety.md) records the decision.

If you applied a `payload-policy` fragment, either the Claude Code permissions and sandbox entries or the `hstack-program` Codex permission profile, it is no longer needed and you can remove it by hand; hStack changes nothing on your machine.

- **Approved proof, `worker-run` and program control are removed** ([#80](https://github.com/hugues-vnsgn/hstack/issues/80)). The `program-check`, `artifact-hash`, `decode-design`, `worker-run`, `run-control` and `run-wait` verbs and their guides are gone, device reservations included; pstack 0.15.25 has none of them.

- **Risk-based mobile coverage is removed** ([#81](https://github.com/hugues-vnsgn/hstack/issues/81)). Plans return to pstack 0.15.25's fixed "Ten lanes on `<model>` at the PR head" rule, and `plan-check` ignores a `verification_profile` field. A plan written with risk-based lanes fails `plan-check` until its live block has the ten-lane heading and ten lanes.

- **The verification-contract gate is removed** ([#82](https://github.com/hugues-vnsgn/hstack/issues/82)). The `plan-compare` verb, its comparison helper and contract reference are gone, and `plan-check` no longer requires a contract box under "Verdict and merge". Plans again go under the agent store's `docs/` as in pstack 0.15.25, with no Git-tracked path or fenced-code rule, and a verdict is clean when every lane passes.
