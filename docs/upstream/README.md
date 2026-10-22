## Native consolidation

All 169 pstack 0.15.25 source files are preserved byte-for-byte with their modes in
`provenance/upstream/pstack-0.15.25.tar.gz`. Canonical native bodies retain all 54 top-level skills,
both upstream agents, 23 generic playbooks and four mobile routes. The runtime
core mirror and generated body loaders are retired. The current ledger and
[consolidation map](consolidation.json) distinguish adapted runtime files from
provenance-only assets. Historical releases and source snapshots remain unchanged.
See [migration contracts](../NATIVE-CONSOLIDATION.md). The ledger target `0.2` means release `0.2.0`; this consolidation ships as `0.3.0` without moving any ledger target. A pin upgrade is separate.

A later native restoration made 46 of the 50 skills model-invocable, so every
description entered the host's per-turn skill list. The skill-list-budget work
reverses that: it returns to pstack's own router design, where only
`poteto-mode` (here `hugues-mode`) was model-invocable and read every other
skill as a file. At the 0.15.25 pin `poteto-mode` is manual-only too, so
`hugues-mode` is user-only ([ADR 0003](../adr/0003-hugues-mode-is-user-only.md)). Only `setup-hstack` stays
model-invocable now; the other 58 bundled skills are user-only (53 from pstack, three from Cursor's
`cursor-team-kit`, and the two hStack-authored Swift and Kotlin baselines), which is the host invocation table's `user_only` list in [consolidation.json](consolidation.json).
The invocation-exposure change moves no upstream responsibility or destination.
Issue #105 adds hStack-authored mobile baselines in the separate authored inventory.
Its conditional native-forensics pointer changes that playbook's disposition to
`port with adaptation` while preserving the five upstream steps.

The router rewrite (issue #22) then moves `plugin/skills/hugues-mode/SKILL.md`
further from pstack's `poteto-mode/SKILL.md`, which stays `port with adaptation`
in the ledger. The title reads "Hugues mode" with the host invocation contract
beneath it, and the four Cursor-only frontmatter fields (`mode`, `icon`,
`color`, `reminder`) are gone. `AskQuestion` is now Claude Code's
`AskUserQuestion` (Codex's question tool is unobserved), `Task` is the host's
agent tool and `poteto-agent` is `hugues-agent`. The four mobile routes joined
the Playbooks list, and the model-defaults paragraph now lives in
[the worker reference](../../plugin/adapters/host-workers.md#model-defaults-and-role-labels).
The rewrite also restated many rules as the behavior to do. Issue #83 put
pstack 0.15.25's wording back in all of them, so the body now differs from
upstream only by these renames, the host translation and the mobile routes.
ADR 0003 later took `poteto-mode`'s frontmatter description and manual-only
flag, and replaced `AskUserQuestion` in the question trigger with asking the
user, plus an interview on a call no experiment can settle.
The next upstream sync of this file is a manual merge against this body, not
a line-by-line port.

## pstack 0.15.25 merge

The pin moves from 0.15.9 to 0.15.25. Upstream changed 94 files and added 8.
Each adapted body took upstream's intent by a manual merge, and every
hStack adaptation stayed. `setup-hstack` is unchanged: its upstream
hunks only move Cursor model defaults and budget semantics. Verbatim files took the new upstream bytes.
Four skills are new: `ketchup`, `sharpen`, `in-your-own-words` and
`hugues-help` (upstream `poteto-help`, the third alias). All four are user-only,
so the per-turn skill list does not grow. Upstream's model defaults (Opus,
Grok, Sol) do not apply; hStack keeps its own defaults and takes only the
rule that moves effort to fit the job. Upstream's Agent Plugins root manifest
stays in provenance. One upstream change is a known gap: the audit helper
still defaults its MERGED base to `origin/main` (pass `--base` otherwise),
where upstream's script now detects the default branch.
Changed and added rows carry the release target
`unreleased-pstack-0.15.25` until a release ships them.

# Upstream sync

The current pin is [cursor/plugins pstack 0.15.25](https://github.com/cursor/plugins/tree/6ce45c59b9301a638c1fe1a7b8dc2a82b650898f/pstack)
at `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f`, committed
14 October 2026 at 23:24:26 UTC. [pin.json](pin.json) binds the version, date,
169-file inventory and pstack tree hash to the checked-in snapshot bytes.
The previous pin, 0.15.9, is now the [baseline pin](baseline-pin.json) and
accounts for 161 files. A fresh public Git fetch reproduced **8 added /
94 changed / 0 removed** paths in [the delta](delta-e43c7ee2-6ce45c59.md).
WP5's first sync, 0.15.5 to 0.15.9, stays in
[its delta](delta-2eb7ed46-e43c7ee2.md), with its 158-file pin and ledger in
[history](history/).

[The current ledger](hstack-dispositions.json), also available as
[CSV](hstack-dispositions.csv), has one active row per upstream file.
The 161 responsibilities at 0.15.9 remain in
[baseline-dispositions.json](baseline-dispositions.json); the current ledger
retains their `earlier_proposal` fields and the previous decisions for the
94 changed files. Current decisions follow [the revised plan](../PLAN.md).
The inaccessible prototype ZIP contributes no rows or implementation claims.

Each row distinguishes its decision (`port verbatim`, `port with adaptation`,
`ignore with reason`) from its release target and implementation state.
`present` means the named file exists in this repository; it does not claim
observed host or app behavior. Planned destinations may not exist yet.
`external` means reference an installed skill, subject to availability.
Previous deferral decisions remain visible as historical fields. The current
restoration activates benchmark wiring, feature-map contracts and top-level
automatic workflow definitions; their runtime prerequisites and authority remain
separate gates. Layer 2 service execution remains outside this restoration.

## Historical retained 0.1.0 tools

The owner approved eight retained families on 6 October 2026. All eight are now
authored and static-tested: `how`, `why`, `architect`, `arena`, `tdd`,
`blast-radius`, `maintain-verification-skill` and `correct`. Their source and
destination fingerprints remain in the research, design and verification receipts
linked from [retained integration](../retained-integration.md). The current ledger
marked their 25 files present. At that release, `swarm`, `show-me-your-work` and
`setup-hstack` (then `setup-huguesstack`) remained deferred to 0.2. The subsequent approved core
restoration registers those definitions too. The pin, historical snapshots and
private owner originals remain unchanged. Static accounting proves no native
host execution of the eight workflows.

## Reproduce offline

Python 3.9+ and Git are sufficient. No dependency install or upstream code
execution is needed. From the repository root:

```sh
python3 scripts/upstream-diff.py check
python3 scripts/upstream-diff.py diff \
  --from-snapshot docs/upstream/snapshots/pstack-0.15.9.json \
  --to-snapshot docs/upstream/snapshots/pstack-0.15.25.json \
  --ledger docs/upstream/hstack-dispositions.json \
  --output docs/upstream/delta-e43c7ee2-6ce45c59.md --check
python3 -m unittest discover -s tests -v
./scripts/check-plugin.sh
```

Snapshots retain the raw Git commit, root tree and manifest, plus sorted
pstack blob fingerprints (mode, SHA-1, byte SHA-256 and size). Capture reads
every blob and verifies its Git object hash. Offline validation reconstructs
the complete pstack tree and binds it through the root tree to the commit;
it also verifies manifest bytes, version and commit date. The pin's snapshot
SHA-256 anchors the recorded byte fingerprints. Offline validation cannot
rehash unretained blob bodies; a fresh capture verifies those bodies again.
Unsupported symlinks, submodules, incomplete trees, duplicate paths/JSON keys,
stale ledger fingerprints and missing reasons fail closed.

To recapture from public Git, use a separate bare clone outside the plugin:

```sh
git clone --bare https://github.com/cursor/plugins.git /tmp/pstack-upstream.git
python3 scripts/upstream-diff.py snapshot --repo /tmp/pstack-upstream.git \
  --revision 6ce45c59b9301a638c1fe1a7b8dc2a82b650898f \
  --output docs/upstream/snapshots/pstack-0.15.25.json --check
```

Capture resolves a ref once and records its full commit SHA. Git replacement
objects are disabled. No checkout, filter, upstream script or consumer app runs.

## Weekly triage

Triage at most once a week. This is a manual maintenance procedure, with no
scheduler or unattended publishing. Compare the current pin with public main:

```sh
python3 scripts/upstream-diff.py diff
```

This fetches main into temporary bare Git storage, validates complete evidence
and writes `docs/upstream/delta-<from>-<to>.md`. Paths are sorted; blob changes
and executable-mode changes are reported. Every newly discovered row is
`pending`. Equal input produces equal bytes; existing output is accepted only
when identical. Different existing content is never overwritten, including
human triage notes. Supply a new `--output` path to preserve an earlier report.
Network/fetch failures stop before report generation.

For a candidate re-pin, capture the candidate snapshot as above at its full SHA
and generate a separate ledger proposal:

```sh
python3 scripts/upstream-diff.py reconcile \
  --from-snapshot docs/upstream/snapshots/pstack-0.15.25.json \
  --to-snapshot /tmp/pstack-candidate.json \
  --ledger docs/upstream/hstack-dispositions.json \
  --output /tmp/pstack-ledger-proposal.json
```

Unchanged rows keep their decisions. Added and changed rows become pending,
with prior decisions preserved. Removed rows move into `retired_items`, retaining
their fingerprints and decisions; a revived path requires fresh triage.
Review every delta row and supply a disposition, concrete reason, release target,
implementation state and intended destinations. Port principles verbatim.
Read playbook and mode diffs before adapting them; never replace the fork with
upstream files. The tool writes only reports or separate evidence/proposals;
it never updates the pin, ledger or plugin automatically.

Commit the reviewed snapshot, ledger, CSV, pin digest and corresponding delta
in a separately reviewed change. The current `check` command validates the
maintained baseline-to-current report and rejects pending active rows. Export
CSV to a new output path with the validated command below, then include it in
the reviewed update. Existing human edits are never overwritten. Until triage and
checks finish, list the candidate delta as pending in [support](../support.md).
```sh
python3 scripts/upstream-diff.py csv \
  --ledger /tmp/pstack-ledger-proposal.json \
  --snapshot /tmp/pstack-candidate.json \
  --output /tmp/pstack-ledger-candidate.csv
```

A changed pin requires matching WP2 receipts and WP3 generator source
fingerprints, or a reviewed update to those receipts. The generator changed at
0.15.25 (readiness now means the app is usable), so its WP3 receipt was
reviewed and now records the 0.15.25 input; its blob and byte SHA-256 must
match the current ledger. A future changed generator requires source review
before re-pinning; stale provenance is rejected rather than silently accepted.

## Attribution

Keep [PSTACK-LICENSE](../../PSTACK-LICENSE) and the fork's
[LICENSE](../../LICENSE). [WP2 provenance](wp2-provenance.json) names the
source and destination of imported plugin files. Adapted skills/playbooks
retain `source:` annotations. The 24 principles and four interrogate references
remain byte-for-byte upstream copies, with attribution in the receipts instead
of altered frontmatter. The checker binds all WP2 receipts and the present WP3
generator's source fingerprints, adaptation disposition and ledger destinations
to the complete inventory. It verifies bytes at every present verbatim ledger destination.
The sync tool itself adds no skills or mobile app code.

## Bundled skills from cursor-team-kit

`deslop`, `control-cli` and `control-ui` are not pstack skills. No row of the
pstack archive or ledger names them. pstack calls them in its workflows, and
hStack bundles them so those steps have local procedures to read. All three
come from `cursor-team-kit/skills/<name>/SKILL.md` in
[cursor/plugins at `ccb5507`](https://github.com/cursor/plugins/tree/ccb5507cec1546dc88135c1139c811e6c59115ba/cursor-team-kit),
under the MIT license, Copyright (c) 2026 Cursor.

- Exact source bytes and Cursor's license remain in
  [provenance/upstream/cursor-team-kit-ccb5507](../../provenance/upstream/cursor-team-kit-ccb5507/),
  outside runtime discovery.
- Each installed skill ships the notice with its procedure. See
  [deslop](../../plugin/skills/deslop/SKILL.md),
  [control-cli](../../plugin/skills/control-cli/SKILL.md) and
  [control-ui](../../plugin/skills/control-ui/SKILL.md).
- The installed bodies are hStack-maintained and may be edited. The provenance
  copy records where each started.
- The `external_skills` receipt in [consolidation.json](consolidation.json) and
  `EXTERNAL_SKILLS` in `scripts/check_core.py` pin the repository, commit, blob
  and SHA-256 of each skill and license. The checker holds the provenance copy
  and the license, and requires each skill to be user-only and to carry the
  shared host invocation contract. It does not compare the installed body to
  the source.
- A newer Cursor pin needs manual review, new provenance bytes, both table
  updates and a reseal.
