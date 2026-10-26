> Historical 0.1.0 implementation record. Its rewritten workflows and deferrals are superseded on the unreleased restoration branch. Read the [development guide](DEVELOPER-GUIDE.md) for current source contracts and evidence limits.

# Retained design workflows

`architect` and `arena` retain pstack 0.15.9's design exploration workflow at
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Read
[architect](../plugin/skills/architect/SKILL.md) for Ground, Sketch, opt-in Agree,
Implement and Scrap. Read [arena](../plugin/skills/arena/SKILL.md) for Frame,
Fan out, Cross-judge, Pick, Graft and Verify. Both are explicit user tools;
coordinators read their local dependencies directly.
The pstack 0.15.25 merge rebound the provenance receipt to `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f` after porting the upstream changes, and the 0.15.32 merge rebound it to `e73df471cd4bd918367e99f3dd9c51bd53ddf5f0`; this record still describes the original package.

Architect grounds each touched subsystem through [how](../plugin/skills/how/SKILL.md)
and changed ownership/layering through [why](../plugin/skills/why/SKILL.md). A
missing dependency blocks Ground. Greenfield work may skip only with evidence
that no surrounding system needs integration. At least two structurally distinct
viable packages precede synthesis. Each begins with caller usage and derives its
types, signatures and module map from that usage.

Arena declares its rubric before fan-out and gives candidates sanitized briefs
and grounding in verified fresh contexts. Codex spawns explicitly use
`fork_turns: 'none'` when exposed, while omitting model and reasoning overrides
to inherit the parent. Prompt omissions alone do not isolate a forked conversation;
a missing fresh-context capability blocks the affected phase.
A fresh judge sees completed candidate files under neutral path labels, with
runner identities, self-scores and coordinator preferences excluded from its
context and supplied evidence. A read-only judge returns its report for private
coordinator persistence; a report-only write needs an explicitly restricted path.
The coordinator reads and scores every candidate concurrently with that judge, then
resolves disagreement against the artifacts. The synthesis record names its
base, every graft's source, rejected ideas, dropouts and actual verification.
Convergence may establish generic arena consensus; architect still needs two
distinct whole-shape designs. Wide divergence returns to Frame. Verification
failure returns to Frame or Graft according to the evidence.

The host changes replace Cursor model rules, fixed vendor defaults and Task API
parameters with the package's native host adapter. Fresh same-host runners and
judges inherit the parent unless the owner chose an accepted role model. This
establishes process independence only. Candidates own separate local paths;
judges read finished artifacts; the coordinator owns the design choices and
design synthesis, including direct hand-grafting. Executable consumer grafts go
to a fresh scoped implementation worker under existing authority. The coordinator
inspects the actual diff before verifying the resulting synthesis. Assigned workers
perform their scope directly. Architect implementation starts with a fresh worker
briefed by the coordinator after synthesis and any requested checkpoint.

Mobile additions carry Swift/iOS, Kotlin/Android, KMP and CMP ownership, lifecycle,
threading, cancellation, exported API and target constraints from grounding into
the sketches. Design-only work ends with a verified design package. Consumer
implementation and executable proof follow existing explicit owner authority and
[mobile lanes](../plugin/skills/hugues-mode/references/mobile-lanes.md). Static
checks or a sketch do not establish mobile runtime behavior.

[Provenance](upstream/retained-design-provenance.json) records all five upstream
files with verified source Git blobs, SHA-256, mode and destination hashes.
`design-red-flags.md` and `rationale-template.md` are byte-verbatim, including the
0.15.9 agent-resistance checks for split ownership, duplicate paths, importable
internals and hand-synced lists. The runner prompt adapts host identity and mobile
scope. The arena-specific briefs live in its skill and reuse canonical
[host notes](../plugin/skills/hugues-mode/references/host-notes.md). MIT attribution remains in
[PSTACK-LICENSE](../PSTACK-LICENSE).

Run `python3 -m unittest discover -s tests -p test_retained_design.py` for
structural and mutation regressions. Run the repository package and provenance
checks after integrating the research dependency. These checks inspect shipped
contracts and fingerprints; they do not execute the design workflows in a host or
prove a consumer implementation. No installs, cloud workers, consumer
transmissions or Git publication are part of this package's validation.
