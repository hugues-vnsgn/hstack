# Claude Code and Codex host adapter

Apply this adapter and the mobile applicability section before the canonical workflow. Follow the consumer project’s own PR policy. These adapters translate host
mechanisms and limit authority; the canonical skill owns workflow
phases, mandatory gates, panel cardinality, fallback and stop rules. A constraint
can block execution. It cannot turn an omitted gate into success.

## Loading and routing

Native discovery uses each canonical `skills/<name>/SKILL.md`. There is no
custom runtime registry or custom host loader. `poteto-mode` maps to `hugues-mode`,
`poteto-agent` to `hugues-agent`, `Comment Sicko` to `hugues-comment-sicko`,
`setup-pstack` to `setup-huguesstack` and `poteto-help` to `hugues-help`; other
public names are unchanged.

Only `hugues-mode` and `setup-huguesstack` are model-invocable; their
descriptions enter the host's skill list. Every other bundled skill, including
each `principle-*`, is user-only: the owner can still type it by name. An agent
reads its SKILL.md in full as the scoped bundled reference, with the host's own
file-read tool and resolved as an owned resource below. The installed helpers
never read a skill body. A missing or unreadable path holds the dependent step.
A native denial on such a skill does not stop the host's file read; the owner's real
control over those skills is enabling or disabling the plugin as a whole.

Inherited Cursor worker wording translates before any dispatch: `poteto-agent` is
`hugues-agent`, `generalPurpose` is Claude Code's `general-purpose` agent,
`run_in_background: true` is the host's background option, and Cursor model slugs
are role defaults to resolve against models the native tool exposes. Read
[workers and models](host-workers.md), which names each host's registered
`hugues-agent`, before the dispatch itself.

Reach `hugues-mode`, `setup-huguesstack` and each consumer or external skill (the
native-only skills) only through the host's supported native mechanism. Respect
manual-only selection, owner-disabled entries and native denials; for those skills, never use a file read as an invocation fallback.
For a native-only skill, unavailable, disabled, denied or unknown invocation stops
the dependent step.
When supported execution requires explicit user invocation, provide the exact
native command and wait; do not imply this handoff is always required. A model's
printed slash or dollar command is not proof that a native invocation occurred.
An available file or a successful binding check establishes no skill permission.
Read ordinary references owned by the invoked skill only when its phase needs them.
Resolve relative resources from their owning file or the stated mode root, never
from the consumer cwd. Do not recursively traverse navigation links or eagerly
invoke all linked skills. This native-mechanism requirement overrides inherited
raw sibling-read wording for the native-only skills alone; a bundled user-only
skill keeps that read wording (the scoped bundled reference above).
For a principles consultation from figure-it-out, use already-loaded mode context
or read the needed principle's SKILL.md in full: never restart task routing.
A fresh worker reads any bundled user-only skill itself. It starts its own native
invocation of any native-only skill; a parent's claim of permission is
insufficient. Missing capability holds the phase without scanning user settings.

The mode applies the pinned router, including figure-it-out for large,
cross-cutting or unmatched work and Orchestrate for standing programs. For a
selected playbook, read its canonical file in full. Copy its ordered todos verbatim.
Keep every skipped todo with its reason.

## Tools and authority

Translate `AskUserQuestion` (`AskQuestion` in inherited Cursor wording), todos,
filesystem and Git operations to actual host tools. Codex's equivalent is
unobserved here, so use the question tool it exposes.
No translation grants new authority. Consumer execution/edits, network data
transmission, installations, credentials, system settings, pushing, PR publication,
merging and releases use the user's current scope. Stop the dependent action when
authority or a necessary capability is absent and continue independent work.

## Required phase guidance

Before the triggering action, read its complete reference. A deferred read is a
prerequisite, not permission to skip a rule. Keep already-loaded guidance in
context; reread it after compaction when needed. These are ordinary owned
references, not alternate skill bodies or a custom native loader.

| Before this action | Read in full |
|---|---|
| Worker dispatch, worker execution, role selection or setup-huguesstack | [Workers and models](host-workers.md) |
| Installed planning or audit commands, workflow ticks, other installed helpers, Bun bootstrap, cloud/loop/forge operations | [Workflow tools](host-workflow-tools.md) |
| Transcript-dependent skills, optional integrations or consumer skill placement | [Special skills](host-special-skills.md) |
| Reading or editing TypeScript files | [TypeScript scope](host-typescript.md) |
| Skill authoring, commits, review, PR preparation/publication or missing control/writing capability reports | [Publication](host-publication.md) |

Apply [mobile applicability](mobile.md#applicability) before selecting a route.
Do not load a phase reference merely because it is listed here.
