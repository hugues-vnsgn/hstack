# Native skill consolidation

Version 0.3.0 consolidates the 0.2.0 layout at `4ae13bb` without
changing the public set of 50 skills, 23 generic playbooks, four mobile playbooks,
two agents or 15 specialized worker roles. No installation or live host
execution is implied by this document.

## Layout and ownership

Each `plugin/skills/<name>/SKILL.md` owns its native metadata and full workflow.
Owned references and scripts remain alongside it. `agents/openai.yaml` contains
Codex invocation metadata only. There is no second procedure body, runtime core
mirror, symlink shadow or custom discovery registry. The former generated
entrypoints are authored files now; `render_core.py` refuses to regenerate them.

The two historical aliases remain `poteto-mode` → `hugues-mode` and
`setup-pstack` → `setup-hstack` (then `setup-huguesstack`; the 0.4.0 rename moved
that one skill, its folder and the plugin name from `hugues-stack` to `hstack`).
Every other public native path remains stable, including
paths an owner may have used to disable skills. Different installation roots can
still affect path-based host settings; reconcile those explicitly during an update.
The pstack 0.15.25 merge adds a third alias, `poteto-help` → `hugues-help`.

All 573 original source files at the current pin, pstack 0.15.36, keep their
modes and bytes in `provenance/upstream/pstack-0.15.36.tar.gz`, outside runtime
discovery. The
Git-object snapshot independently checks the archive. The current adaptation
map is `docs/upstream/consolidation.json`. The original releases and their frozen
tests are retained. `docs/upstream/core-restoration.json` remains the historical
0.2.0 restoration receipt; `consolidation.json` is the current installed receipt. Upstream byte equality applies to the archive; it is no
longer a claim about the adapted runtime tree.

The upstream human guide lives under `docs/pstack/`. Benny's Cursor automation,
the Cursor manifest and the legacy history-scanning cleanup shell script remain
provenance-only. The installed artifact includes the original MIT notice.

## Invocation and resources

Use native skill invocation for `hugues-mode`, `setup-hstack` and any
consumer or external skill. Read ordinary owned references only when the
current phase needs them. None of those is a reference-file fallback:
unavailable, owner-disabled, denied or unknown invocation stops its dependent
phase. A manual handoff is
needed only when the host requires explicit user invocation; it is not a
proven universal limitation in this setup.

At the pstack 0.15.9 pin, upstream Cursor metadata marked 49 skills manual-only,
with `poteto-mode` the one exception. At 0.15.25, 53 of 54 are manual-only and
only `setup-pstack` is model-invocable; at 0.15.32 and 0.15.36 that holds for 57 of 58. hStack restores that design instead of the earlier native
table that made 46 skills model-invocable: only `setup-hstack` is
model-invocable now, so only its description enters startup context on Claude
Code. The other 62 bundled skills, including `hugues-mode` ([ADR 0003](adr/0003-hugues-mode-is-user-only.md)), `deslop`, `control-cli` and `control-ui`, are user-only; the
owner can still type any of them by name, and the mode reaches each one as its
router's reference: the agent reads its SKILL.md in full with the host's own
file-read tool instead of invoking it natively. The installed helper takes no
part in that read. `hugues-agent` reads `hugues-mode/SKILL.md` from its parent's
path, else from the installed plugins, as `poteto-agent` does; Claude Code cannot
preload a `disable-model-invocation` skill. Generated
project verification skills stay consumer-local and model-invocable so proof
steps can drive them; that tier is unrelated to the bundled table above.

The host adapter's native-only rule takes precedence over inherited
sibling-read wording for `hugues-mode`, `setup-hstack` and consumer or
external skills; a bundled user-only skill keeps that inherited wording, read
in full as the mode's reference. The adapter also prevents unconditional
traversal of navigation links. A figure-it-out consultation of mode principles
must not restart mode routing. This is an instruction contract, not a
filesystem security boundary or proof of every possible runtime trace.

The shared contract now loads specialized adapter references only before their
named phases. Mobile applicability is a small separate entry; explicit mobile
work must load the complete mobile rules before routing or execution. The partition
receipt accounts for every prior adapter requirement as kept, replaced or removed,
with a recorded reason for each change. See [progressive disclosure](CONTEXT-FOOTPRINT.md)
for the partition and comparable required-read inventories.

The installed `read-workflow` helper refuses every `SKILL.md`, bundled or not,
and their legacy aliases. `translate-plan` also rejects such reads, including a
path to any `SKILL.md` in any letter case or with `.`, `..` or repeated slashes.
A plan names the bundled skill to apply, never a path to read: the agent reads a user-only
skill's file with the host's own file-read tool, and reaches `hugues-mode`,
`setup-hstack` and consumer or external skills natively. Owned
playbook/reference rereads stay binding-guarded. PR 1 fix rounds 1 and 2 briefly
let the helper read bundled skill bodies; each review found another branch that
slipped past the skill-body guard, and round 3 restored the `a67df90` runtime
(its `payload.py` differed only by the resealed manifest digest). The skill-path
normalization fix then replaced that runtime's literal-path test with one that
normalizes the path first. The translator
preserves consumer-owned Git reads and supports only its documented bounded
literal shapes. It does not become a host dispatcher or shell interpreter.

## Integrity and cleanup

The installed manifest covers canonical instructions, metadata, helpers and
adapters, with complete file inventory and permission modes. Three linked
trust anchors avoid a circular self-hash: the bootstrap verifies runtime source,
the verifier binds the manifest, and the saved binding records every plugin file
including those anchors. A changed install, file, permission or inventory holds.
The bootstrap is still the trusted entrypoint; this is drift detection, not a
signature system against replacement of all code and trust anchors.

Run `python3 scripts/seal_payload.py` after intentional edits, review its diff,
update source-provenance receipts for changed retained families, then run all
checks. Sealing refuses a changed canonical destination unless each reviewed
file is named with `--accept <repository path>`; an edit is not re-approved by
hash regeneration alone. `docs/HELPER-INPUTS.json` is checked against the
installed helpers, so its byte-identity claims cannot go stale. The receipts live
in this repository: `--accept` makes a canonical change deliberate and visible in
review, it is not an external signature. Hash regeneration cannot approve lost
workflow gates. Never regenerate
receipts as a consumer workaround for drift. Old 0.2.0 program bindings fail;
review and explicitly rebind migrated programs.

The activity parser and audit logic are unchanged. Missing/empty/unsupported
activity and unknown PR state remain holds with exit 2. The audit grants no
deletion authority; active/pinned-chat verification remains a separate gate.
Only synthetic transcripts and disposable Git consumers are used in current tests.

## Validation and limitations

See [test accounting](TEST-COVERAGE.md) for current versus historical totals.
Current checks exercise actual installed helpers, negative inventory/mode/body
mutations, skill-body read rejection for every bundled skill, consumer and
external path, public names, workflow phase contracts, owned links and
parser/audit safety. The helper never returns a `SKILL.md`; a bundled user-only
skill's file is read by the agent's own file-read tool. Context budgets are measured
source bytes and characters, with characters/4 as an explicit token estimate;
they are not observed host prompt usage.

The following figures are historical: measured at this consolidation's own
`7db3e80` disclosure pass, not recomputed since. Initial bug-fix routing,
including its full playbook, todos and required unslop reply guidance, was
then 34,456 bytes versus 45,289 before disclosure, about 8,604 versus 11,308
estimated tokens. The larger workflow inventories include their required
transitive skills and resources. Native frontmatter was 13,431 bytes after
the host invocation table removed 45 inherited manual-only lines and the
setup description named the native model-role file. Workflow bodies
excluding frontmatter changed only where nine skills replaced Cursor
model-role wiring. These were source budgets, not actual startup exposure,
full execution cost or runtime savings, and they predate PR 1's restoration
of pstack's user-only tiering; see [context footprint](CONTEXT-FOOTPRINT.md)
and [the budget record](CONTEXT-BUDGET.json) for current figures.

Live Codex invocation, disabled-skill and planning behavior remain UNVERIFIED
for this consolidation. Separate prior-layout trials cannot validate this source
revision. Claude Code sessions on this layout are bounded: the
[skill-list host validation](skill-list-host-validation.md) and the
[router interactive check](router-interactive-check.md) observed it discovering
the plugin, listing exactly two of its skills and invoking `hugues-mode` natively
in one session. No workflow ran to completion, and the audit's compatibility with
persisted transcripts remains unverified. Generic workflow content and mobile
scope rules are retained; mobile redesign and optional automatic cross-skill
composition are separate future work.

Implementation review can proceed on this finite contract. A green static suite
does not establish full runtime parity, unattended execution, native transcript
compatibility, or mobile device/forge/cloud/loop behavior.
