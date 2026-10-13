# Installed planning, proof and worktree commands

New-program scheduling, progress and runtime waiting use `run-control` and
`run-wait`; the controller loads [program control](program-control.md) at dispatch
or pickup. They record/check state and grant no native dispatch permission.

These are mechanical translations of bundled operands in the canonical playbooks.
Reach the selected skill first, as [host.md](host.md) directs, and preserve its todo order,
verification rules, explicit execution go and active/pinned-chat gate. Python 3 and Git must already
be available; plan validation also needs Node. Missing tools block the gate.
The adapters do not install dependencies, fetch or query a forge. `worker-run`
executes authorized worker argv within its write scope. `run-control` writes the
protected progress store; the remaining commands read inputs and print results.

## Bind and reread the approved installed payload

For either autopilot, read [payload protection](payload-protection.md) before
write-capable work. Binding and guarded reads detect drift; native host policy
must prevent payload writes. The bound `payload-policy` command prints a
reviewable host fragment without applying settings or asserting enforcement.
Bound `helper-ready` checks Bun and the pinned helper's package/lock install key
without execution or installation. Run it before selecting a Bun helper under
protection; missing or stale prerequisites hold that operation. See the same
protection reference for separate preparation and exact-root readiness evidence.

Resolve `<plugin>` from the loaded public entrypoint, not the consumer directory.
Use absolute paths below. The plugin may be an installed directory without Git.
At program authoring, save a binding in the authorized program evidence directory:

```sh
python3 "<plugin>/adapters/host_tools.py" bind > "<program>/plugin-binding.json"
```

The binding records the canonical layout identity, approved manifest digest,
installation path and every plugin file's hash and full permission mode. The
manifest covers the entire installed inventory except the three trust anchors
(manifest, payload verifier and bootstrap); the bootstrap binds runtime source
and the saved binding also covers those anchors. Unexpected files hold. Only
runtime Python bytecode caches, `.DS_Store` host metadata files and the
`skills/hugues-mode/scripts/node_modules/` tree that the Bun bootstrap installs
are excluded; none is ever a workflow input. Installed modes are compared by
what matters for safety: a world-writable file or a changed executable bit
holds, while group-write from a `002` umask or archive extraction does not.
Windows permission modes are not modelled; installed checks there are unobserved.
The upstream revision is provenance, not the installed revision. Record the
candidate commit separately. A 0.2.0 binding cannot be reused after migration;
review and create a new binding explicitly.

Reread an owned playbook through the saved binding:

```sh
python3 "<plugin>/adapters/host_tools.py" read-workflow --binding "<program>/plugin-binding.json" skills/hugues-mode/playbooks/feature.md
```

The helper never reads a skill body: `read-workflow` rejects every `SKILL.md`,
including a bundled skill's own, a legacy alias and any consumer or external
skill's. Read a bundled user-only skill's `SKILL.md` with the host's own
file-read tool, resolved per [host.md](host.md); a plan names the skill to apply,
never a path to read. A helper cannot grant invocation permission or report an
owner-disabled skill as enabled; the reach and denial rules are in [host.md](host.md).
Owned references and playbooks are ordinary resources; never move a skill body
into them as an invocation workaround.

Translate the filled bundled references in multi-phase-plan, autopilot-full and
autopilot-stack before handing the plan to another worker:

```sh
python3 "<plugin>/adapters/host_tools.py" translate-plan --markdown --binding "<program>/plugin-binding.json" "<program>/plan-draft.md" > "<program>/plan.md"
python3 "<plugin>/adapters/host_tools.py" plan-check --binding "<program>/plugin-binding.json" "<program>/plan.md"
```

Use `--markdown` for pstack-style plans. Write executable commands in complete
single-backtick code spans or fenced code blocks; text outside them is prose and
is preserved. A `markdown` or `md` fence contains another Markdown example;
other fences contain commands. Nested list items keep inline-code handling. Other
four-space or tab-indented lines receive command checks, including list
continuations; keep prose and its inline command on the list-item line. Indented
list items also check text outside inline spans as commands, because the same
shape can be executable indented code. Fences inside lists or blockquotes, and code
indented directly after a container marker, hold: move those code blocks to the
top level. Each code fragment is checked before translation.
Incomplete or multi-backtick inline spans and unclosed fences hold. When executing
a translated Markdown plan, treat its prose as explanation, not shell input.

Without `--markdown`, bare lines and text surrounding inline references receive
the command checks too. Shell backticks around a `skill.md` token are checked
before inline references are split. Adding a backtick comment never switches the
input mode.
Use this default for standalone commands. Mixing translated standalone commands
with other text holds, even across blank lines. The caller selects the mode;
the file cannot declare its own mode. Neither mode requires prose markers in a
pstack plan.

For a command that names a skill directory, use only a known owned Markdown
resource path, `cat <known path>`, `git show origin/main:<known path>`, or the exact
bundled Node plan-check command with one literal plan operand outside skill
directories. Any path segment named `skills` is in scope, including consumer,
home, plugin and absolute paths, with quotes, escapes and letter case accounted
for. Unknown paths, other Git revisions and unsupported commands in that scope
hold. Glob, brace, tilde, variable and command-substitution syntax near a skill
directory or a `skill.md` token also hold, even inside quotes. Name the skill to
apply when the step needs a skill; reach it as [host.md](host.md) directs.

A literal path to any `SKILL.md` still holds on every line, after `.`, `..` and
repeated slashes resolve, in any letter case, at any Git revision, including as
the plan-check operand. A bare `SKILL.md` in prose names no file. Supported owned
resource reads become quoted, binding-guarded `read-workflow` commands; the Node
command becomes `plan-check`. Exact emitted commands can be translated again.
Shell operators and expansions on bundled operands hold rather than being
partially rewritten. Commands outside skill directories that name no skill body
or bundled operand retain their shell syntax and consumer Git revisions.

Fill placeholders first and inspect the translated plan. Exact known bundled
paths in the supported forms designate bundled workflow references; arbitrary
text does not establish ownership. Line continuations and heredocs hold before
fragment processing. This translator enforces a plan contract, not a shell
sandbox; host permissions remain the execution boundary.

The unchanged installed Node helper validates the absolute consumer plan path
and preserves its exit code and diagnostics. Any binding, hash, mode or
required-file drift blocks rereading or validation. Reconcile changed payloads
with the operator; never silently rebind a live program. These commands do not
arm loops or start implementation.

## Compare a PR's verification contract

Use bound `plan-compare` with a consumer repository, repository-relative plan path,
exact PR section heading, and full main/head commit SHAs. It executes the installed
comparison helper only after the existing payload binding passes. See the
[verification contract](../skills/hugues-mode/references/verification-contract.md)
for the command, ruling record and verdict gate. The comparison is read-only;
exit 0 clears only the rule-change gate, and exit 2 holds. The root authenticates
the operator ruling separately. Source tests do not establish host writer isolation.

## Integrity trust boundary

The trusted entrypoint is `adapters/host_tools.py`, including its approved runtime
hash table. It verifies all five runtime source buffers before executing any,
checks saved runtime/bootstrap binding data for bound commands, and executes those
same buffers without reopening them. Package checks reject a runtime/hash-table
mismatch. Python bytecode caches are not executed. The saved binding then checks
the remaining installed payload before the requested operation.

This requires a trusted entrypoint, Python interpreter/standard-library environment,
and owner-approved binding. A maliciously rewritten entrypoint or trust table can
lie; it cannot authenticate itself. Initial `bind` is the owner's approval point
for the installed non-core files, not an external signature service. These checks
detect drift; they do not promise protection against an adversary concurrently
rewriting every workflow or external helper during later reads/execution.

## Approved program proof and scoped workers

Before a new program's first build, read [program proof](program-proof.md)
for its four additive commands and [record format](program-records.md) for JSON
inputs. Keep `plan-check` and existing gates. Changed installations require
explicit migration; never replace a live binding silently.

## Audit explicit authorized native activity sources

In worktree-cleanup step 1, replace the Cursor-only upstream shell helper with:

```sh
python3 "<plugin>/adapters/host_tools.py" worktree-audit --binding "<program>/plugin-binding.json" --repo "<consumer>" --sources "<program>/sources.json" --pr-snapshot "<program>/prs.json"
```

The adapter reads paths from the consumer's local Git worktree list, handles paths
with spaces, and inspects local dirty/merge state. `--base` defaults to the local
`refs/remotes/origin/main`; no fetch occurs and freshness is reported unverified.
It does not enumerate native history directories. Supply only roots or individual
files covered by the user's current authority, including authorized subagent
records. Never discover private history to fill a missing source. For example:

```json
{
  "schema_version": 1,
  "coverage": "complete",
  "sources": [
    {"provider": "claude", "files": ["/absolute/authorized/session.jsonl"], "authorization": "owner-approved source scope", "coverage": "complete"},
    {"provider": "codex", "root": "/absolute/authorized/session-directory", "authorization": "owner-approved source scope including subagents", "coverage": "complete"}
  ]
}
```

The supported hosts are Claude Code and Codex. Cursor sources are ignored without
reading them; they contribute no evidence or coverage for these hosts. A manifest
containing only ignored sources remains unavailable. Supported sources determine
coverage independently; no Cursor source is required.

`complete` is the owner's explicit assertion that the supplied set covers all
relevant supported-host chats and sibling trees; a successful scan cannot establish that
assertion. Mark either level `partial` when coverage is uncertain. No sources,
partial coverage, unreadable/missing/changed files, symlinks, unsupported envelopes
or malformed records produce unavailable coverage and a hold (exit 2). A complete
empty root, empty file list, or empty/whitespace-only transcript also holds.
Duplicate JSON keys and JSON nesting over 64 levels hold instead of hiding records. Valid complete sources with no recent evidence report that limited result.

Supported inputs are Claude JSONL user/assistant records and string summaries
and Codex JSONL session/turn/response records including JSON-encoded function
arguments. Claude content blocks are text, tool_use, tool_result and plaintext
thinking, with required content fields. Tool-result content is a string
or a list of text leaves with only `type` and string `text` fields; nested,
malformed or opaque result blocks hold coverage. Codex messages require a known
role and a content list of input_text/output_text blocks with
their required fields. Missing, malformed or unknown blocks hold.
Nested progress envelopes and unknown block/tool types hold
coverage for inspection. Codex tool outputs require a nonempty call identifier
and string output. Reasoning permits only reviewed plaintext summary/content
blocks; encrypted reasoning holds. Textual agent/user events require string
content and no opaque attachments. Other events, web-search responses, Claude
system/history/queue records and redacted thinking have no reviewed content
schema and hold. Unsupported records/files keep coverage unavailable while
independent later records/files can retain activity hints. Those hints are
labeled as validated records or unparsed path hints, never as deletion safety.
Opaque records invalidate inherited relative context until a reviewed context
resets it. Envelope/message metadata also uses bounded fields and types;
unknown metadata, including unreviewed usage structures, holds. Other formats hold.
The text matcher checks literal paths, current-user `~/` aliases, and up to
three percent-decoding passes (including file URLs). Other-user home aliases and
unresolved deeper encodings hold. Word characters and hyphens continue a filename;
other punctuation, Markdown delimiters, shell separators and CJK punctuation
can end a mention. This is a conservative text rule, not a universal path parser:
ambiguous punctuation can produce extra recent-activity evidence. Case variants
must identify the same filesystem object. Structured native operations still use
their bounded schemas and directory contexts. The scan counts worktree paths,
child paths and session working directories count as activity even in quoted
messages. Encoded function arguments are decoded; relative path operations need
session or tool working-directory context. Each operation retains its own context;
relative tool working directories resolve against their enclosing session.
Codex operation-local directories never replace persistent session/turn context.
Session/turn contexts need an absolute working directory and reviewed string
metadata fields; unknown context fields or opaque metadata hold. Operations without a
resolvable working directory or absolute operation path hold.
Simple shell operands and bounded native patch
file headers resolve relative to that context, including sibling worktrees and
parent-directory scopes and sequential `git -C` directory changes. Shell support is deliberately bounded to cat, ls, head,
tail, wc, stat, rg, grep, git status, pwd, readlink and realpath with literal
operands and a finite option allowlist. Unknown options, command paths outside
the reviewed bare/system forms and preprocessors hold. Compound commands,
expansions, arbitrary programs and unknown tool
operations hold coverage for inspection; the adapter never executes transcript
commands. Patch envelopes, operation headers, moves and hunk/body lines must
fit the bounded grammar; unknown directives or unconsumed content hold.
Sed, find and other embedded programs hold. Claude file operations support
Read/Write/Edit with required `file_path` and tool-specific fields; unknown fields
or wrong types hold. Glob/Grep/MultiEdit and unknown file tools hold for inspection.
Missing/malformed
function arguments or tool inputs also hold. This is a conservative operand scan,
not a prediction of every program's implicit filesystem access or side effects.
Record timestamps take priority; missing timestamps use file
mtime conservatively and label that evidence. Recent means within four days.
This is supported-format synthetic evidence, not attestation of every host version.

The CLI accepts an omitted PR snapshot for diagnostics, but complete candidate
metadata requires an owner-supplied snapshot, for example
`{"coverage":"complete","states":{"branch-name":"NONE"}}`. Valid states are
`OPEN`, `CLOSED`, `MERGED` and `NONE`. A detached candidate uses an exact absolute
worktree key, such as `"worktree:/absolute/candidate":"NONE"`. Branch and worktree
entries that disagree hold. The primary worktree is always retained and its PR
metadata is not required for candidate completeness.

Each candidate reports `metadata_coverage` and `metadata_errors`; the primary row
reports `not-required`. Unknown PR/merge state or unavailable Git status holds the
candidate, including scratch work. Global `metadata_coverage` aggregates candidates;
`audit_status` is `hold` and the CLI exits 2 if activity or candidate metadata is
unavailable. Complete inputs exit 0 but still grant no deletion permission.
`pr_snapshot_error` separately explains a missing or invalid snapshot. Check the
snapshot's freshness and completeness separately before any pruning decision.
The report retains source paths and timestamps, never transcript bodies. Size
and disk measurements remain the separate core `df`/local disk inspection steps.

Buckets are advice. Dirty tracked work, open PRs and unavailable activity hold;
recent activity requires verification. A clean merged candidate with complete
no-recent evidence reaches `verify-active-pinned`, never deletion permission.
Obtain the real active/pinned-chat set separately, including sibling worktrees,
and apply core steps 2–4. Every row says `deletion_authorized: false`. This adapter
never prunes or deletes, and no automated deletion is established by its tests.
