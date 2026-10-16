# What Claude Code's sandbox matches and protects (macOS)

Answers wayfinder ticket #64 (map #63, measurements on #53). Research date
2026-10-16. Nothing here modifies live settings or runs sandbox experiments.

## Sources and the version each holds for

| Source | Version | Notes |
|---|---|---|
| Sandboxing docs, https://code.claude.com/docs/en/sandboxing | live page fetched 2026-10-16 (`.md` form); pages are not versioned, so read it as "current at Claude Code 2.1.301" | Quoted as "sandboxing docs" |
| Settings reference, https://code.claude.com/docs/en/settings-reference | same | `sandbox.excludedCommands`, `sandbox.network.allowMachLookup` |
| Permissions docs, https://code.claude.com/docs/en/permissions (Wrappers section) | same | Defines the `Bash(...)` pattern syntax that `excludedCommands` reuses |
| Changelog, https://code.claude.com/docs/en/changelog | through 2.1.301 | Version-pinned fixes below |
| Sandbox runtime ("srt"), https://github.com/anthropic-experimental/sandbox-runtime (the npm package `@anthropic-ai/sandbox-runtime` links the same code) | `v0.0.79` plus 67 commits, HEAD `0ded0c80bf8f44b64b30ad9e6bfc084cb9fc9dc5` (2026-10-16); `package.json` says 0.0.79 | Seatbelt profile and mandatory deny list |
| Installed Claude Code binary | 2.1.301, read-only string extraction of `~/.local/share/claude/versions/2.1.301` | Minified, bundled JS; used only to check the docs, never as the authority |
| #53 comments by hugues-vnsgn | Claude Code 2.1.300 for rounds 1-3 and the 2026-10-15 and 2026-10-16 headless measurements (version of the later runs not stated in the comments) | "Correction to round 4" table and "Round 5" |

Evidence labels used below: **(a)** documented, **(b)** evident from source,
**(c)** observed on #53, **(d)** unknown.

Important scoping fact (b): srt contains no `excludedCommands` logic at all.
`grep -ri excludedCommands` over srt's `src/`, `README.md`, `docs/` and `test/`
returns nothing. The exclusion decision lives in the closed-source Claude Code
layer, which decides per Bash call whether to wrap the command with srt. srt
answers questions 2 and 3; it cannot answer question 1.

## Question 1: how `sandbox.excludedCommands` matches

### (a) Documented

- Entries "use the same syntax as the content of a `Bash(...)` permission
  rule: an exact command, a prefix such as `docker *`, or a wildcard pattern.
  A pattern with no wildcard is an exact match." (settings reference,
  `sandbox.excludedCommands`).
- "Claude Code matches the text of the call: a script or `make` target that
  calls `docker` internally doesn't match, and neither does
  `/usr/local/bin/docker`." (sandboxing docs, "Run commands outside the sandbox
  with `excludedCommands`").
- Compound commands: "Every command in the call has to match."
  `npm ci && docker compose build` stays sandboxed unless `npm ci` is also
  covered. Introduced in 2.1.277: "a `sandbox.excludedCommands` glob exempting
  an entire compound Bash command from the sandbox when only one part matched;
  every part must now match" (changelog 2.1.277, 2026-09-18).
- Shapes that keep a call sandboxed "among others" (settings reference): a
  command starting with `sudo`, `eval` or `xargs`; `cd`, `pushd`, `popd`
  anywhere; command substitution, subshell or control-flow block; a redirection
  other than fd duplication; a command name from a variable; some `git clone`,
  `init`, `worktree add` forms with absolute, `~` or `..` paths.
  **Env-assignment prefixes and `env` wrappers are not in that list**, and
  "among others" leaves it open.
- Permission-rule wrapper stripping (permissions docs, "Wrappers"): the fixed
  stripped set is `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`,
  `builtin`, zsh `noglob`, and bare `xargs`. "Claude Code also strips a leading
  assignment of certain known-safe environment variables, so
  `Bash(npm test *)` matches `NODE_ENV=test npm test`. An allow rule won't match
  past an assignment of any other variable. A deny or ask rule matches past any
  leading assignment." The list of "known-safe" variables is not published.
  `env`, `bash -c`, `direnv exec`, `devbox run`, `npx` are not stripped.
- `excludedCommands` is "a convenience, not a security boundary" and the
  recommended alternative for a tool that only needs a path is
  `filesystem.allowWrite`.
- The per-call escape hatch is separate: Claude may retry with
  `dangerouslyDisableSandbox`, subject to `allowUnsandboxedCommands` (default
  true) and the permission flow. With it `false`, only `excludedCommands`
  entries run unsandboxed (sandboxing docs, "The unsandboxed retry escape
  hatch").
- Entries in project settings (`.claude/settings.json`,
  `.claude/settings.local.json`) are ignored while the sandbox is
  admin-required (managed or `--settings` sets `allowUnsandboxedCommands:
  false`, among other triggers); user, managed and `--settings` entries still
  apply. The docs say this "Requires Claude Code v2.1.285 or later" and that
  v2.1.282 to v2.1.284 behaved differently (changelog 2.1.282). Relevant to
  hStack if the entry lives in a project settings file.

### (b) Evident from source

The binary for 2.1.301 contains the decision code. Names are minified and the
`strings` dump flattens many bundle chunks into one namespace, so identifiers
collide; read this as corroboration, not as a spec.

- The entry point takes the call text, splits it into subcommands, and
  requires every subcommand to be "covered": `h.every(part => covered(part, ...))`.
- A subcommand is covered when a pattern matches any of a set of candidate
  strings: the normalised text plus variants produced by repeatedly stripping
  wrappers and leading `NAME=value` assignments. Matching is the same three
  pattern types as permission rules (prefix, exact, wildcard).
- There is an explicit gate before matching: a command whose first word is
  `env` (including `/bin/env`, `/usr/bin/env`, `genv`) is classified
  "trusted" or "untrusted" and is never coverable by a pattern. This accounts
  for the `env VAR=1 bash ...` row in the #53 table.
- The leading-assignment stripper is the same one permission rules use: it
  removes `NAME=value ` prefixes until it meets a name rejected by a predicate,
  which matches the documented "known-safe variables" behaviour.
- Separately, 2.1.292 added "an interpreter command with an env var prefix like
  `FOO=bar python3 app.py` runs unprompted" under strict sandbox mode. That is
  the auto-allow path, not exclusion, and must not be read as a change to
  `excludedCommands` (changelog 2.1.292, 2026-10-06).

What I could not resolve from the bundle: a textual glob `*android.sh boot *`
does match the string `VAR=1 /path/android.sh boot x`, so some other gate in
the covered-check rejects the assignment-prefixed form (candidates are the
hazard checks that run on each subcommand and the assignment predicate). I did
not identify which one.

### (c) Observed on #53 (correction to round 4, 2026-10-15)

Pattern `*android.sh boot *`, headless session, probe script `android.sh`:

| Command | Result |
|---|---|
| `/path/android.sh boot x` | excluded |
| `bash /path/android.sh boot x` | excluded |
| `VAR=1 /path/android.sh boot x` | sandboxed |
| `VAR=1 bash /path/android.sh boot x` | sandboxed |
| `env VAR=1 bash /path/android.sh boot x` | sandboxed |

### (d) Answer and what stays unknown

1. **Is `VAR=1 cmd` staying sandboxed documented?** Not in terms. The docs say
   entries follow `Bash(...)` rule syntax, that an allow-style match does not
   see past a non-allowlisted assignment, and that call shapes stay sandboxed
   "among others". The observation is consistent with those statements read
   together and with the bundle's `env` gate, but no page states it. The
   `env` wrapper case is backed by source; the plain assignment case rests on
   the permissions-docs rule plus observation.
2. **Is there a supported shape that matches through a prefix?** By the docs,
   possibly for the fixed wrapper set (`timeout 30 cmd`, `nice`, `nohup`,
   `stdbuf`, `time`, `command`) and for a "known-safe" env variable, but
   neither has been shown to work for `excludedCommands` (only for allow
   rules), and the safe-variable list is unpublished. Treat as unverified.
   `env`, `bash -c`, and any custom runner are not stripped. A
   `ANDROID_TMP=...` style variable is not documented as safe.
3. **Shapes that are supported without depending on a prefix:**
   - put the environment inside the helper script and call it as one fixed
     command line (the form measured as excluded in #53);
   - use the per-call `dangerouslyDisableSandbox` retry, if
     `allowUnsandboxedCommands` is left true;
   - choose `filesystem.allowWrite` for pure path needs (docs recommendation),
     which does not apply to the emulator because Mach registration cannot be
     allowed (see Question 3).
4. **A leading `*` does not make a prefix match.** Observed (c); the docs say
   the "text of the call" is matched, which a naive reading would accept.
5. Unknown: whether `timeout`/`nice`/`nohup` in front of a pattern-matching
   command is excluded; the known-safe variable list; whether `VAR=1 cmd` stays
   sandboxed in versions before 2.1.300; the exact gate that rejects it. A
   targeted check is cheap: run the five #53 rows plus `timeout 30`, `nice` and
   `NODE_ENV=test` variants in a headless session with `--settings <tmpfile>`
   (never the user's settings), reading the "Bash command (unsandboxed)"
   prompt title in manual mode (sandboxing docs give that confirmation method).
   This was not run.

## Question 2: files the sandbox write-protects regardless of `allowWrite`

### (a) Documented ("Protected paths", sandboxing docs)

Inside directories sandboxed commands can write to, writes are still denied
for four groups:

- In the working directory **and the directories above it**: the `.claude`
  settings files, `.claude/skills`, `.claude/agents`, `.claude/commands`,
  `.claude/hooks`, `.mcp.json`, and files Claude Code runs on its own, such as
  `.claude/workflows` and `.claude/scheduled_tasks.json`.
- In the working directory **only**: shell startup files (`.bashrc`,
  `.zshrc`), `.gitconfig`, the `.vscode` and `.idea` directories, and `hooks`
  and `config` inside `.git`.
- Files that would turn the working directory into a bare git repo: `HEAD`,
  `objects`, `refs` at the top level, plus existing `config` and `hooks` when a
  `HEAD` sits beside them; a file named `config` is denied even without `HEAD`.
- In `~/.claude` or `CLAUDE_CONFIG_DIR`: most contents, plus `~/.claude.json`
  and `.credentials.json`.

Also documented: a symlink appearing at a protected settings path makes the
sandbox deny the target too, from the next command (late-appearing `.claude/*`
symlinks fixed in 2.1.210); "There is no way to exempt one of these paths. An
`allowWrite` entry or an `Edit` allow rule ... doesn't lift the protection";
the only switch is `sandbox.filesystem.disabled`, which turns off filesystem
isolation entirely (requires 2.1.216 or later). `/sandbox`, Config tab, lists
most paths resolved for the machine under "Denied within allowed".

So the answer to "are there others, such as `.claude/settings*.json` or
`.git/hooks`?" is yes, and both are documented. The sandboxing docs also
document the symptom in #53 round 5: "A git command fails with `unable to
unlink old`": `git merge` and `git checkout` fail when they must replace a
file the sandbox denies writes to, and the docs suggest rerunning outside the
sandbox or in another terminal. The docs do not name `.mcp.json` in that
troubleshooting entry, but it is in the protected list.

### (b) Evident from srt (v0.0.79, `src/sandbox/sandbox-utils.ts`, `macos-sandbox-utils.ts`)

srt's own mandatory deny list, which Claude Code builds on:

- `DANGEROUS_FILES`: `.gitconfig`, `.gitmodules`, `.bashrc`, `.bash_profile`,
  `.zshrc`, `.zprofile`, `.profile`, `.ripgreprc`, `.mcp.json`.
- Directories: `.vscode`, `.idea`, `.claude/commands`, `.claude/agents`;
  `.git/hooks` always; `.git/config` unless `allowGitConfig` is true.
- On macOS (`macGetMandatoryDenyEntries`) each name is denied at the cwd and
  with a `**/<name>` pattern beneath the cwd, so nested copies are covered and
  not-yet-existing files are covered ("macOS uses glob patterns, which cover
  existing and new files alike", README "Mandatory Deny Paths").
- srt's list does **not** contain `.claude/settings*.json`, `.claude/skills`,
  `.claude/hooks`, `.claude/workflows`, `~/.claude`, or the bare-repo files.
  The extra Claude Code entries are therefore added in the closed layer,
  consistent with the docs. `.gitmodules`, `.profile`, `.zprofile`,
  `.bash_profile` and `.ripgreprc` appear in srt's list but not in the Claude
  Code docs' prose ("such as ..."); treat them as likely protected, not
  documented for Claude Code.
- `allowGitConfig` is a srt option; I found no counterpart in the Claude Code
  settings reference, so it is not documented as user-settable there.

### (c) Observed on #53 (round 5, 2026-10-16)

`touch plain.txt` succeeded and `touch .mcp.json` failed in the same allowed
folder; `git merge origin/main` failed with `unable to unlink old '.mcp.json':
Operation not permitted` once the base branch changed `.mcp.json`. Widening
`allowWrite` did not help. Matches (a) and (b).

### (d) Unknown

- Whether a linked worktree's `.git/hooks` and `.git/config` (which live under
  the main repo's `.git/worktrees/<name>` or the common dir, outside the
  worktree's cwd) are protected when only the worktree is writable. In srt's
  README a worktree `.git` is a file, blocked on Linux; the macOS behaviour for
  that file and for the common dir is not stated. Not observed.
- Which of the srt-only names (`.gitmodules`, `.profile`, ...) Claude Code
  2.1.301 actually enforces; the Config tab would show it and was not
  inspected.
- Whether the protection applies identically to files reached through the
  `Edit` tools versus Bash (the permission-mode "protected paths" list is a
  separate, prompt-time mechanism, see permission-modes docs).

## Question 3: Mach service registration (`bootstrap_check_in`)

### (a) Documented

Only `sandbox.network.allowMachLookup` exists: "List additional XPC and Mach
service names the macOS sandbox may look up", with a single trailing `*`
prefix wildcard, and `"*"` alone matching every service (settings reference).
`sandbox.enableWeakerNetworkIsolation` adds one lookup (`com.apple.trustd.agent`)
and `sandbox.allowAppleEvents` adds Apple Events and a few CoreServices
lookups. Nothing in the sandboxing docs, the settings reference or the
changelog (searched for `mach`, `register`, `bootstrap`, `check_in`) mentions
registering a Mach service.

### (b) Evident from srt

- The macOS profile is `(deny default ...)`. The only Mach grants in
  `macos-sandbox-utils.ts` are `(allow mach-lookup ...)` entries (a fixed
  list, the user's `allowMachLookup` as `global-name` or `global-name-prefix`,
  and the two opt-in groups above) and `(allow mach-priv-task-port (target
  same-sandbox))`. There is no `mach-register` or other Mach grant anywhere in
  `src/`, `test/` or `README.md` (greps for `mach-register`, `bootstrap`,
  `bootstrap_check_in`, and any `(allow mach` that is not `mach-lookup`).
- The config schema (`sandbox-config.ts`) has no field for raw profile text or
  extra rules; the only Mach field is `allowMachLookup`.
- Consequence: under the default-deny profile a process cannot register a
  service the profile does not grant. This is consistent with Crashpad's
  `bootstrap_check_in` being refused with permission denied, which is what
  #53 round 3 observed.

### (c) Observed on #53 (round 3)

Android emulator exits with code 132 within a second; Crashpad's
`bootstrap_check_in` is refused with "Permission denied (1100)". The comment
attributes it to the lack of a register allowance. Consistent with (b). The
mapping of `bootstrap_check_in` to the Seatbelt `mach-register` operation is
standard Seatbelt background that I did not verify against Apple
documentation and that the sources above do not state.

### (d) Answer

No setting allows Mach service registration. Not `allowMachLookup` (lookup
only, even with `"*"`), not `enableWeakerNetworkIsolation`, not
`allowAppleEvents`, not `ignoreViolations` (that silences reports, it does not
allow), and not `filesystem.disabled` (documented as turning off filesystem
isolation only; it is not documented to change Mach rules). The only ways to run a program that
must register a Mach service are `excludedCommands` (an exact helper line, see
Question 1), the per-call `dangerouslyDisableSandbox` retry, or turning the
sandbox off. Unknown: whether a future srt version adds a register allowance (none at
HEAD `0ded0c8`), and whether `filesystem.disabled` changes what the profile
grants for Mach operations (not checked).

## Consequences for hStack (inputs for the map, not decisions)

- The mobile fragment should ship the emulator boot as one fixed helper, take
  its environment from the script or a file, and state the exact
  `excludedCommands` pattern next to it. Round 4's `ANDROID_TMP=... android.sh
  boot` form stays sandboxed on current evidence (c) and, for `env`, by source
  (b).
- A doctor check can use the documented confirmation method (manual mode, look
  for the "Bash command (unsandboxed)" prompt title) or a probe that writes
  outside the write list, as #53 did.
- `.mcp.json`, `.claude/settings*.json`, `.claude/skills|agents|commands|hooks`,
  shell startup files, `.gitconfig`, `.vscode`, `.idea`, `.git/hooks` and
  `.git/config` are write-protected and cannot be exempted. Local `git merge`
  or `checkout` that changes any of them fails with `unable to unlink old`; the
  server-side merge workaround from round 5 is consistent with this.
- Adding a sandbox allowance cannot fix the emulator's Mach registration.
  Do not propose `allowMachLookup` entries for it.
