# Claude Code and Codex host adapter

Read this file once per session, and again after compaction. A skill's "read the host contract" is that read. Apply this adapter and mobile applicability before the canonical workflow.
Follow the consumer project's PR policy. Adapters translate host mechanics and
limit authority; the canonical skill owns workflow
phases, mandatory gates, panel cardinality, fallback and stop rules. A constraint
can block execution. It cannot turn an omitted gate into success.

## Loading and routing

Native discovery uses each canonical `skills/<name>/SKILL.md`. There is no
custom runtime registry or custom host loader. `poteto-mode` maps to `hugues-mode`,
`poteto-agent` to `hugues-agent`, `Comment Sicko` to `hugues-comment-sicko`,
`setup-pstack` to `setup-hstack` and `poteto-help` to `hugues-help`; other
public names are unchanged.

Only `setup-hstack` is model-invocable. Every other
bundled skill, including each `principle-*`, is user-only: the owner can still
type it by name. On Claude Code, never call the Skill tool for one. In a
playbook, `/<name>` and "the **<name>** skill" mean reading `../<name>/SKILL.md`.
An agent
reads its SKILL.md in full as the scoped bundled reference, with the host's own
file-read tool. Helpers never read a skill body. A missing or unreadable path
holds the dependent step.
A native denial on such a skill does not stop the host's file read; the owner's real
control over those skills is enabling or disabling the plugin as a whole.

Reach `setup-hstack` and each consumer or external skill (the native-only
skills) only through the host's supported native mechanism.
On Codex, select the enabled skill from the host-provided catalog and read
its complete SKILL.md. No separate Skill tool exists.
Respect manual-only selection, owner-disabled entries and native denials.
Outside that mechanism, never use a file read as an invocation fallback.
For a native-only skill, unavailable, disabled, denied or unknown invocation stops
the dependent step.
If user invocation is required, give the exact native command and wait.
Printed commands do not prove native invocation.
An available file or a successful binding check establishes no skill permission.
Read owned references only as the phase needs. Base relative paths on the owning file or mode root, never consumer cwd. Never traverse links recursively or
invoke linked skills eagerly. For native-only skills, this rule overrides inherited sibling reads; bundled
user-only skills keep their scoped read above.
For a principles consultation from figure-it-out, use already-loaded mode context
or read the needed principle's SKILL.md in full: never restart task routing.
A fresh worker reads any bundled user-only skill itself. It loads any native-only
skill itself through the host-specific mechanism above; a parent's claim of
permission is insufficient. Missing capability holds the phase without scanning user settings.

Bundled commands use [workflow tools](host-workflow-tools.md) in every worker.

Read the full canonical playbook and copy its ordered todos verbatim.

## Tools

Map Cursor `AskQuestion`, todos, filesystem and Git to host tools.

| Cursor | Claude Code | Codex |
|---|---|---|
| `AskQuestion` | `AskUserQuestion`. In `-p` mode it is absent: write the question in plain text in your report and hold the dependent step. | unobserved. Use its question tool. |
| Open a todolist | `TodoWrite` if offered, else a Markdown checklist in the task's [agent store](host-workflow-tools.md#agent-store-translation), copied and marked per [Playbooks](../skills/hugues-mode/SKILL.md#playbooks). Name the file in your reply. | unobserved |
| `Grep`, `Glob` | `Bash`: `rg`, else `grep` and `find`, for whichever the session lacks. | unobserved |

No translation grants new authority. User scope governs consumer runs and edits,
network sends, installs, credentials, system settings, pushes, PR publication,
merges and releases. Hold actions without authority or capability. Continue independent work.

## Cursor-only features

Keep pstack's playbook text. A step that needs a Cursor-only feature gets one plain line, no bullet or bold: `Skipped in <host>: <step>. <reason>.` Never ask the user to choose, offer an alternative or retry. Independent steps continue; one that needs the skipped output holds, with a named placeholder. A skip line never checks a gate: a skipped mandatory gate holds the result.

| Cursor | Claude Code | Codex |
|---|---|---|
| Cursor Automations: routines, `update_state` routine calls, `api2.cursor.sh/automations` webhooks, routine wakes, and `SendToUser` secret requests | Skip with the line. | unobserved |
| Bugbot | [Publication](host-publication.md) | Same. |
| A built-in PR tool | The step's forge command, such as `gh pr create`. No line. | unobserved |
| "control skill" / "matching control skill", `cursor-team-kit` attributions | Bundled `control-cli` (CLI, TUI) or `control-ui` (browser, Electron, web). iOS or Android: the repo's installed simulator-driving skill, such as `test-ios` or `test-android`, through the native mechanism, else XCTest or UiAutomator through the native helper. A missing driver stays an execution gap. | Same. |
| Cursor's `/loop` | `/loop` in the current local session, never a cloud schedule for work that needs local devices. | Only active-session waits. Between-turn scheduling stays an unsatisfied gap, per #34 item 6. |

## Required phase guidance

Before the triggering action, read its complete reference. Deferral never skips a rule.
Retain loaded guidance and reread after compaction when needed. These are owned references, not skill bodies or a native loader.

| Before this action | Read in full |
|---|---|
| Worker dispatch, worker execution, role selection or setup-hstack | [Workers and models](host-workers.md) |
| Installed planning or audit commands, workflow ticks, other installed helpers, Bun bootstrap, cloud/loop/forge operations | [Workflow tools](host-workflow-tools.md) |
| Transcript-dependent skills, optional integrations or consumer skill placement | [Special skills](host-special-skills.md) |
| Reading or editing Swift or Kotlin files | [Mobile language scope](host-mobile-languages.md) |
| Reading or editing TypeScript files | [TypeScript scope](host-typescript.md) |
| Running `xcodebuild`, `swift build` / `swift test`, or Gradle in an Android/KMP/CMP project | [Native execution](native-execution.md) |
| Skill authoring, commits, review, Bugbot triage or its plan box, PR preparation/publication or missing control/writing capability reports | [Publication](host-publication.md) |
| Dispatch with `$ORCA_TERMINAL_HANDLE` set, `t3-code` tools or omp | [Hosts](hosts/README.md) |

Plain JVM or server Gradle projects stay out of scope.

Do not load a phase reference merely because it is listed here.
