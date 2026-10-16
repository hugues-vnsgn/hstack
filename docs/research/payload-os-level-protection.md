# OS-level controls that keep the installed payload read-only without the Bash sandbox

Research ticket: [#65](https://github.com/hugues-vnsgn/hstack/issues/65), under map
[#63](https://github.com/hugues-vnsgn/hstack/issues/63). Background: the `uchg` lock
removed in [#53](https://github.com/hugues-vnsgn/hstack/issues/53) and the current
procedure in `plugin/adapters/payload-protection.md`. This note records viability only.
It makes no decision; that belongs to #66.

Researched 2026-10-16.

## Versions

| Item | Version |
|---|---|
| macOS | 27.0.1 (26A434), Darwin 27.0.0 `xnu-13432.1.9`, arm64; SIP enabled, `kern.securelevel` 0 |
| Claude Code | 2.1.301 installed. Docs read at code.claude.com on 2026-10-16 |
| Codex CLI | 0.163.0. Source read at tag `rust-v0.163.0` of openai/codex |
| Apple man pages | local pages on the machine above: `chflags(1)` (June 12, 2018 page, macOS 27.0), `chflags(2)`, `chmod(1)`, `mount(8)`, `hdiutil(1)`, `access(2)`, `rename(2)`, `sysctl(8)` |
| xnu source | `apple-oss-distributions/xnu` default branch at `f6217f891ac0` (committed 2025-10-16, the `xnu-12377` line). This is not the macOS 27 kernel on the test machine (`xnu-13432`), so source citations are evidence for the mechanism, not for macOS 27 itself |

## Evidence labels

- **[D]** documented in a primary source (cited).
- **[O]** observed on this machine on a scratch directory under `/tmp` and a scratch disk image. No flag, owner change or mount touched a real file, any plugin cache or the live payload. The scratch tree was deleted.
- **[I]** inferred from documentation, source or observation, not observed.
- **[U]** unknown: no primary source found and not tested.

Limits of the observations. Every probe ran as the owner of the scratch files (uid 501, an
admin-group user with no passwordless `sudo`: `sudo -n true` fails with "a password is
required" [O]). Nothing was run as another user or as root, because that needs privilege the
task did not authorize. Claims about "another user" or "root" rest on documentation and xnu
source, not on a run.

## What matters before the option list

1. **Where the writers run.** Claude's Bash sandbox covers shell commands only. Read, Edit,
   Write, MCP servers, command hooks, plugin monitors, LSP servers, the status-line command
   and `apiKeyHelper` all run outside it, with the user's full access [D: code.claude.com
   `/docs/en/sandboxing#what-runs-outside-the-sandbox`; `/docs/en/sandbox-environments`
   "Sandboxed Bash tool"]. Every one of these is a process of the invoking OS user [D, same
   pages]. A control keyed to the OS user or to the filesystem therefore covers all of them
   in one place. A control that only a Seatbelt profile enforces covers only the processes
   inside that profile.
2. **Codex.** The Codex sandbox applies to "spawned commands, not just to built-in file
   operations" and uses Seatbelt on macOS [D: learn.chatgpt.com `/docs/sandboxing`]. MCP
   servers "use their own controls" [D: learn.chatgpt.com `/docs/permissions`]. Whether
   `apply_patch` runs inside or outside that sandbox is not stated [U]. An OS-user or
   filesystem control does not depend on the answer.
3. **Identity is the common requirement.** A kernel check lets a principal change a
   protection only if the rules give that principal the right. So every option below only
   protects against the agent if the agent's uid is not the owner or the mounter. Nothing
   short of that works. The `uchg` lock failed in #53 for this reason: the owner may set and
   clear it [D: `chflags(2)`: "UF_IMMUTABLE ... may be set or unset by either the owner of a
   file or the super-user"; O].

## Where plugins live and how they are rewritten

### Claude Code

- Plugins root is `~/.claude/plugins`, or `$CLAUDE_CODE_PLUGIN_CACHE_DIR` when set [D:
  `/docs/en/plugins/loading#find-plugins-on-disk`; `/docs/en/env-vars`]. Marketplace plugins
  are copied to `cache/<marketplace>/<plugin>/<version>/` at install and loaded from that
  copy [D, same page, "In-place and copied plugins"]. `${CLAUDE_PLUGIN_ROOT}` is that
  version directory and "changes when the plugin updates" [D: `/docs/en/plugins-reference`].
- An update writes a new version directory, then "writes an `.orphaned_at` marker into the
  previous version directory" and removes it in a background cleanup 14 days later [D:
  loading page, "Cleanup of previous versions"]. Updates are skipped when the computed
  version is unchanged [D, "Versions and updates"]. Auto-update runs only for marketplaces
  with it on; the default is off for third-party marketplaces [D, "Which marketplaces and
  plugins auto-update"]. `claude plugin install name@marketplace` refreshes that
  marketplace first [D, "When Claude Code refreshes a marketplace before an install"].
- **Read-only seed directory.** `CLAUDE_CODE_PLUGIN_SEED_DIR` names "one or more read-only
  plugin seed directories". Claude Code "loads plugin caches from the seed in place,
  without cloning", "never writes to the seed and forces `autoUpdate` off for seed
  marketplaces", and `marketplace update` and `remove` on a seed marketplace "fail with a
  message that names the seed directory" [D: `/docs/en/plugins/org#seed-containers-and-ci`;
  `/docs/en/env-vars`]. The seed is built with
  `CLAUDE_CODE_PLUGIN_CACHE_DIR=/seed claude plugin install ...`, can be mounted at a
  different path, and its plugins still need `enabledPlugins` [D, same section]. Seeded
  plugins load with `path` under the seed [D, same section]. This is the one place either
  host documents an in-place, never-written plugin location.
- The Bash sandbox's own write protection covers "most of" `~/.claude`, including
  `~/.claude.json` and `.credentials.json` [D: sandboxing page, "Protected paths"]. Whether
  `~/.claude/plugins/cache` is in that list is not stated [U]. It is a Bash-sandbox
  mechanism in any case and so out of scope here.
- On this machine `~/.claude/plugins/cache` is `drwxr-xr-x hugues_mini staff` with no flags,
  and `installed_plugins.json` shows no hstack entry in the default config dir [O].

### Codex

- Installed copies live in `~/.codex/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION/`;
  Codex "loads the installed copy from that cache path rather than directly from the
  marketplace entry" [D: developers.openai.com `/codex/plugins/build`]. During marketplace
  refresh "Codex can install or refresh files for configured plugins, even when
  `enabled = false`" [D, same page]. The cache path is under `$CODEX_HOME` [I from source;
  the config reference documents `$CODEX_HOME` but not the cache path]. Git marketplaces are
  cloned under `$CODEX_HOME/.tmp/marketplaces` [I from source constant
  `INSTALLED_MARKETPLACES_DIR = ".tmp/marketplaces"`, `core-plugins/src/installed_marketplaces.rs`].
- Install mechanics, from `codex-rs/core-plugins/src/store.rs` at `rust-v0.163.0` [D as
  source, I as behavior]: `copy_dir_recursive` with `fs::copy` into a `plugin-install-*`
  temp directory created in the parent of the plugin base root, then `fs::rename` into
  `<base>/<version>`; for a new version it then `remove_dir_all`s older version
  directories and fails the install only when the older version "would stay active"; for an
  existing version it renames the whole base root to a `plugin-backup-*` directory, renames
  the staged root in, and rolls back on failure. Uninstall is `remove_dir_all` of the base
  root.
- The docs name no seed, no read-only cache location and no permission handling for
  installed files [D: the build page "doesn't address file permissions or ownership"; U for
  anything Codex-specific beyond the source reading].
- On this machine `~/.codex/plugins/cache/hstack/hstack/0.4.0` is `drwxr-xr-x hugues_mini`
  with no flags and no ACL [O].

## Option A: payload owned by a different user

Make the version directory, and every ancestor the agent could use to swap it, owned by
root or a dedicated service user, mode 755 / files 644. The agent's user cannot write it.

| Question | Answer |
|---|---|
| Can the agent's own user undo it without root/admin? | No for the data and mode bits: POSIX mode and ownership changes are for the owner or the superuser [D: `chmod(1)` "Only the owner of a file or the super-user is permitted to change the mode"; `chflags(2)` `[EPERM]` text]. A group-write grant or ACL given to the agent user would reopen it, so the entry set must be minimal. An admin-group user who can type a `sudo` password can undo it; the agent must have no passwordless `sudo` and no Touch ID `sudo` path [I; `sudo -n` check shown [O]]. |
| Install/update survival | **Breaks the host's own install and update path.** Claude and Codex both create and rename directories as the user inside the cache [D loading page; I source]. With root-owned `cache/<marketplace>/<plugin>`, `claude plugin install/update` and Codex marketplace refresh cannot write there. Codex's flow fails closed with the old copy active (rollback path in `store.rs`) [I]. Claude's failure behavior and its `.orphaned_at` write into a root-owned old directory are not documented [U]. Updates become an admin-run step. For Claude, the documented route that fits is a root-owned seed: build as the admin with `CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/hstack-seed ...`, point `CLAUDE_CODE_PLUGIN_SEED_DIR` at it, enable via `enabledPlugins` [D]. For Codex no equivalent is documented [U]; the nearest is a root-owned `$CODEX_HOME/plugins/cache` subtree populated by an admin, with Codex errors on refresh [I]. |
| Granularity trap | A protected version directory inside a user-owned parent can still be renamed away or deleted by the user (rename and unlink need write on the parent [D: `rename(2)` EACCES text]) and replaced with a new directory. The protected unit must include the ancestors up to a directory the agent cannot write, or be paired with option C on the directory itself. [I; the uchg-on-directory case blocks rename and delete for the scratch directory [O]] |
| `Edit` deny alongside | Still applies. Permission rules are "evaluated before any tool runs" and cover every tool [D: sandboxing page, "Permission rules"]. The Edit tool runs in the Claude process as the user [D: sandbox-environments page], so the kernel denies it too (`EACCES` [I]). The Edit deny becomes a faster, clearer refusal and a second layer. |
| Writers covered | All processes under the agent's uid: Edit/Write, Bash (sandboxed or not), workers, hooks, MCP servers, LSP, monitors, status line, credential helpers [D that they run as the user; I that the kernel check then applies]. Not covered: anything running as root or as the owner, a user who can `sudo`, and writers that act through another user's process (Apple Events to a different app, a daemon with write access) [I]. |
| Startup proof | See "Startup proof shape" below. Identity-based: `stat -f %u <root>` differs from `id -u`; `access(W_OK)` is false on the root, a file and a directory; errno on a probe copy is `EACCES`. |

Viability: viable. Cost is the install/update path and the admin step it forces.

## Option B: read-only mount or disk image

Put the version directory (or a seed/cache subtree) on a volume mounted read-only, for
example a `UDRO` image attached with `-readonly`.

| Question | Answer |
|---|---|
| Can the agent's own user undo it without root/admin? | **Depends on who mounted it.** [O] I attached a scratch `UDRO` image as my user with `hdiutil attach -readonly -nobrowse -mountpoint ...`: `mount` showed `read-only ... mounted by hugues_mini`, writes returned "Read-only file system" and `chmod` failed with the same error. My own user then ran `hdiutil detach` successfully. [D] `mount(8)`: `rdonly` / `-r` "even the super-user may not write it". [D as source] xnu allows unmount and remount (`mount -u`) by "only root, or the user that did the original mount" (`bsd/vfs/vfs_syscalls.c`, `safedounmount` and the update path) [I for macOS 27]. So a user-attached image is undoable by the agent; a root-attached one is not. `hdiutil attach -notremovable` is "Only root" and needs a reboot to detach [D: `hdiutil(1)`]. |
| Install/update survival | The mount point is read-only for every writer, including the host's updater. All install and update writes under it fail with `EROFS` [O for the error, I for the host reaction]. Updating needs an admin to detach, rebuild the image and reattach. Reboot behavior: a mount made by hand does not survive a reboot; persistent attach needs a root `launchd` job or `fstab` entry [I; `hdiutil(1)` points to `fstab(5)` for mountpoints but gives no boot recipe, so U for the exact recipe]. If the mount is absent at launch, the host sees an empty or user-owned directory beneath it and may reinstall there [I]. This makes a mount check part of every startup and tick. Claude's seed is a cleaner fit: mount the image read-only at `CLAUDE_CODE_PLUGIN_SEED_DIR` [D: seed "can be mounted at a different path"]. |
| `Edit` deny alongside | Still applies and is redundant with the mount. The Edit tool gets `EROFS` from the kernel [I from O on the shell path]. |
| Writers covered | Every writer on that volume, regardless of uid, including root (absent a remount), so it also covers a root-run MCP server or hook [D `mount(8)`]. It does not cover a second copy elsewhere, or a writer that remounts (needs root or the mounter). |
| Startup proof | `statvfs`/`statfs` read-only flag [O: `os.statvfs(...).f_flag & os.ST_RDONLY` was true on the mounted scratch image]; `mount` line shows `read-only` and the mounter (`mounted by root`); `access(W_OK)` false [O]; errno `EROFS`. |

Viability: viable only if the image is attached by root. A user-attached image is not a
boundary against the agent.

Other facts [D: `hdiutil(1)`]: disk images default to extra restrictive options such as
`nosuid` and `quarantine`; `-shadow` lets a read-only image be attached read/write with
writes diverted to a shadow file, so the shadow option must not be used. Ownership is shown
as the mounting user under `noowners` [O: `mount` printed `noowners` and files appeared
owned by the mounting user on the scratch image]. Executing prepared helpers from an image
needs `exec` (not `noexec`) [I]. Whether Gatekeeper or quarantine attributes affect the
Bun helpers or scripts run from an attached image was not tested [U].

## Option C: `chflags schg` (system immutable)

| Question | Answer |
|---|---|
| Can the agent's own user undo it without root/admin? | Setting `schg` is super-user only [D: `chflags(1)` "set the system immutable flag (super-user only)"; `chflags(2)` "may only be set or unset by the super-user"]. [O] As a non-root user, `chflags schg` returned `Operation not permitted` (EPERM). So the agent user cannot set or clear it. **But root can clear it at the default securelevel.** xnu `vnode_immutable` says that when a flag change is being authorized, "if (securelevel <= 0) ... flags do not inhibit changes" and only above level 0 do SF_ flags resist root [D as source: `bsd/vfs/vfs_subr.c`]. `kern.securelevel` is 0 here [O], is writable by root and can be raised but never lowered except by pid 1 [D as source: `bsd/kern/kern_sysctl.c`, `sysctl_securelvl`]. What raising it to 1 does on macOS beyond `schg` (it is also consulted for raw disk write access, pf, dummynet) is not documented for macOS 27 [U]. So `schg` stops the agent user (no root) but not a root process, and no macOS document describes using securelevel as a persistent hardening step [U]. |
| SIP interaction | **SIP does not apply.** The SIP `restricted` flag marks Apple-installed system paths ("System files can be modified only by system processes signed with Apple's code signing identity"; "File system protections apply only to a system's boot and root volumes") and its path list is a sealed system file (`/System/Library/Sandbox/rootless.conf` on this machine lists Apple paths) [D: Apple Platform Security, "System Integrity Protection"; Apple SIP guide; O for `ls -lO` showing `restricted` on `/usr/bin/true` and the file contents]. `chflags(1)` documents `schg` but not `restricted`. No document found describes SIP protecting a user-chosen path [U]. `schg` is a plain file flag, not a SIP mechanism. |
| Install/update survival | Any writer, including the host updater running as the user, fails with `EPERM` on a flagged tree: `rm`, `mv`, `rename` and writes all returned `Operation not permitted` with `uchg` on the scratch tree (same kernel check, user flag) [O]. The updater cannot unflag it itself, so every update needs a root-run `chflags -R noschg` first, then reflag [I]. Recursive flagging of the cache subtree, plus the version directory itself so it cannot be renamed away [O: uchg on the directory blocked `mv` and `rm -rf`]. Claude's `.orphaned_at` marker write into the old directory and the 14-day cleanup would fail [I; Claude's handling of that failure is U]. |
| `Edit` deny alongside | Still applies; the Edit tool is stopped by the kernel (`EPERM`) [I from O]. The flag is not visible in `ls -l` without `-O`, so a failure can look like a bug. |
| Writers covered | Every writer under a non-root uid, including all the host's tools [I]. Not covered: root, and any writer that can reach root. |
| Startup proof | `ls -lO` shows `schg` (configuration read only); `access(W_OK)` false [O for the `uchg` equivalent]; errno `EPERM`; plus the non-escalation facts (`sudo -n` fails). |

Viability: viable as a layer on top of A (root-owned plus `schg`) or alone against the agent
user. Alone it does not stop root, and the cost is the same admin-only update path as A.
Compared with the `uchg` lock removed in #53, `schg` closes the "owner can clear it" hole
[D/O] and nothing else.

## Option D: ACL deny entries

| Question | Answer |
|---|---|
| Can the agent's own user undo it without root/admin? | **Yes if the agent's user owns the file.** [D as source] xnu removes `KAUTH_VNODE_WRITE_SECURITY` from the rights it checks when the caller is the file owner: "If we are the file owner, we automatically have some rights", so an ACL cannot deny the owner the right to change the ACL (`vnode_authorize_simple`, `bsd/vfs/vfs_subr.c`). [O] I added `user:<me> deny write,append,delete,writeattr,writeextattr,writesecurity,chown` to a scratch file: appends failed with "permission denied", and `chmod -a ...` and `chmod -N` then removed the entry as the owner, including on a directory entry with `deny add_file,delete_child,...`. [D] `chmod(1)` documents the grammar (`+a`, `-a`, `-N`), `writesecurity` and `chown`, but not this owner exception. If the file is owned by a different user, the agent cannot change the ACL, but then option A already stops it, and the ACL adds only nuance. |
| Other limits | A directory ACL with `file_inherit` applies to files created afterwards, not to existing files: the existing file stayed appendable while `touch` and `rm` in the directory failed [O]. Existing files need their own entries. `deny` entries are ordered before `allow` entries [D: `chmod(1)` canonical order]. ACL entries and mode bits are not flags: copies made by `cp` and archive tools may drop them [I; `chflags(1)` BUGS says only a limited number of utilities are flag-aware, which is the nearest document, U for ACLs]. |
| Install/update survival | An ACL on the version directory with user-specific deny entries blocks the user's updater the same way as A, and the user (the updater) cannot clear it only if not the owner. In the owner case the updater can clear it, so the entry would also have to be re-added after each update by the same user that is the agent, which is no boundary. |
| `Edit` deny alongside | Applies; no interaction. |
| Writers covered | The listed principal only, and only while the agent is not the owner. |
| Startup proof | `ls -le` shows the entry (configuration read only); `access(W_OK)` false [O]. Neither shows the agent cannot remove it. |

Viability: not viable as the primary control when the agent owns the files. Useful only to
tighten a root-owned tree (for example denying a service group), where mode bits already do
the job.

## Option E: other credible controls

These are outside the four named in the ticket but passed a primary-source check.

1. **Run the whole agent process under a dedicated OS user (the inverse of A).** The payload
   stays owned by the admin or install user; the agent runs as a separate, unprivileged
   standard user. Same kernel checks as A with the identities swapped. The costs are
   moving `~/.claude` / `~/.codex` auth and config to the agent user and keeping that user
   out of `admin` and `sudoers` [I]. No Anthropic or OpenAI document describes this setup
   [U]. Viable [I].
2. **Wrap the entire Claude Code process in `@anthropic-ai/sandbox-runtime` (Seatbelt).**
   This is documented to constrain "the session's tools, hooks, and MCP servers as well as
   shell commands" with `denyWrite` taking precedence over `allowWrite` [D:
   `/docs/en/sandbox-environments`, "Sandbox runtime"]. The runtime is "a beta research
   preview, and its configuration format may change" [D, same section]. It is a different
   mechanism from the built-in Bash sandbox but is still Seatbelt, and it does not protect
   other processes outside the wrapper (a second `claude` run elsewhere, anything started
   by launchd). A process cannot leave its own Seatbelt profile [I; not found in a primary
   source]. Codex has the analogous native Seatbelt for spawned commands, and its permission
   profile carves out `read` for a path [D: learn.chatgpt.com `/docs/permissions`, and the
   existing `plugin/adapters/payload-protection.md`]; Codex MCP servers are not covered by
   the profile [D, same page]. Viable for Claude with the beta caveat [D].
3. **Container or VM with the payload mounted read-only.** The documented route to put
   "file tools, MCP servers, and hooks" behind one boundary is a dev container, custom
   container or VM [D: `/docs/en/sandbox-environments`, "Dev containers" onward]. Read-only
   mounting is a container-runtime property, not described in the Claude docs [U for any
   Claude-specific recipe]. Heavy for mobile work that needs host Simulator, adb and Xcode
   [I; see the #53 round notes].
4. **Claude seed directory plus managed settings.** A root-owned seed (option A or B) set
   through the `env` block of the root-owned managed settings file (macOS:
   `/Library/Application Support/ClaudeCode/managed-settings.json`) so the agent's user
   cannot unset `CLAUDE_CODE_PLUGIN_SEED_DIR` in a project file [D: `/docs/en/managed-settings`,
   "Deploy a managed settings file"; per-variable `env` merge needs v2.1.223+]. The file's
   write protection is ordinary root ownership [I]. The managed settings directory does not
   exist on this machine [O], so this is a new admin step.
5. **Endpoint Security / MDM-based file protection.** Not examined: no primary source tied it
   to a payload path, and it needs a signed system extension [U].

## Comparison

"Agent can undo" = the agent's OS user, with no sudo, can remove the protection.
"Update path" = what happens to the hosts' own install or update of the payload.

| Option | Agent can undo? | Survives host install/update | Covers Edit/Write, shell, workers, MCP, hooks | Startup proof | Viable for #66? |
|---|---|---|---|---|---|
| A. Different owner | No [D/I] | Host updater fails; admin or seed step required [I]; Claude has a documented seed [D], Codex none [U] | All same-uid writers [I] | `stat` uid vs `id -u`, `access(W_OK)`, errno `EACCES` | Yes |
| B. Read-only mount, root-attached | No [D/I] | All writes fail with `EROFS`; admin remount to update [O/I]; mount must be re-established after reboot [I] | All writers on the volume, including root [D] | `statvfs` read-only, `mount` owner, `access`, `EROFS` [O] | Yes |
| B'. Read-only mount, user-attached | **Yes** (`hdiutil detach` worked [O]) | Same | Same until detached | Same | No |
| C. `chflags schg` | Not by the agent user [D/O]; root can [D as source, securelevel 0] | Updater fails; root `noschg` then reflag; Claude `.orphaned_at` and cleanup behavior U | All non-root writers [I] | `ls -lO`, `access`, errno `EPERM` | Yes, as a layer; alone does not stop root |
| D. ACL deny | **Yes**, if the agent owns the files [D as source/O] | Same as the owner case | Named principal only | `ls -le`, `access` | No as primary |
| E1. Agent as separate OS user | No [I] | Install user keeps its own update path [I]; agent user moves its config [I] | All of the agent user's processes [I] | As A | Yes, if the setup cost is acceptable |
| E2. `sandbox-runtime` around the process | Not from inside the wrapper [I] | Unchanged; payload is writable outside the wrapper | Whole Claude process incl. file tools, MCP, hooks [D] | Seatbelt profile inspection plus a denied write on a probe copy | Yes for Claude, beta [D]; Codex unaddressed [U] |
| E3. Container or VM, read-only mount | No [I] | Unchanged outside | Whole environment [D] | Mount flags inside the guest | Probably heavy for mobile [I] |
| E4. Managed settings plus seed (Claude) | Not without root [I] | Documented route [D] | As A or B | Seed `path` in the `init` event [D] plus A or B proofs | Yes, Claude only |

## Startup proof shape (what survives #53's ruling)

#53's ruling is that a file lock or a classifier refusal cannot prove that the *sandbox*
enforces. For the controls above the argument changes: the OS control is the enforcement, so
the proof is about the control and the agent's identity, not about the sandbox.

1. **Configuration reads are not proof.** `ls -leO`, `mount` and `stat` show configuration. A
   `uchg`-like lock shows up in them too, and #53 already ruled such a lock out as evidence
   about the sandbox. They are useful only to pin the root and the control type. [D #53]
2. **Kernel-answered checks that write nothing.** [O] `os.access(path, os.W_OK)` from
   Python returned false for a `uchg` file, a mode-444 file and both the file and directory
   on a read-only mount; `os.statvfs(...).f_flag & os.ST_RDONLY` was true on the read-only
   mount. `access(2)` documents `EROFS` for read-only filesystems and uses the real uid; use
   `AT_EACCESS`/`effective_ids` where the effective uid differs [D: `access(2)`]. These
   probes are not deliberate payload writes, which is what the classifier refused in #53
   round 2 (whether the classifier accepts them in auto mode is not tested [U]). They must
   run in each writer's own execution context (coordinator, fresh worker, hook, MCP server),
   recorded with actor identity.
3. **Control-specific errno on a disposable copy under the same control.** [O] Read-only
   mount: `EROFS` ("Read-only file system"). Immutable flag: `EPERM` ("Operation not
   permitted"). Mode or ACL deny: `EACCES` ("permission denied"). The error code tells the
   operator which control refused, so a denial from some other source (a stray mode bit,
   say) is distinguishable. A destructive probe still belongs on a disposable copy, never on
   the live root, as the existing procedure says.
4. **Non-escalation facts.** `id -u` differs from the owner's uid; the agent user is not
   root; `sudo -n true` fails [O]; the flag/ownership/mount owner is root or a service user
   (`mount` shows `mounted by <user>`; xnu allows that user to unmount [D as source]). This
   is what excludes B' and D.
5. **Binding to the live root.** All of the above must name the canonical `plugin_root` in
   the program's binding and its ancestors, since renaming the version directory away
   defeats a file-level control [I; O for the directory uchg case]. Read-only checks on the
   live root (`access`, `statvfs`, `ls -lO`, `mount`) do not write to it.
6. **Re-check cadence.** A mount can disappear on reboot and a flag or ownership can be
   reset by an admin update, so the proof repeats on fresh dispatch, restart and each audit
   tick, as the current procedure already requires [D: `plugin/adapters/payload-protection.md`].

Gaps stay explicit: no run as another user or as root, no run of Claude Code or Codex itself
against a protected cache, and no check of what Claude or Codex do when an update hits a
protected directory.

## Writer coverage summary

| Writer | Bash sandbox (now) | A / B / C | E2 `sandbox-runtime` |
|---|---|---|---|
| Edit/Write/NotebookEdit (Claude) | No; `Edit` deny only [D] | Yes, kernel check in the Claude process [D that it runs there; I] | Yes [D] |
| Shell and child processes | Yes [D] | Yes | Yes |
| Workers (subagents) | Inherit sandbox [D] | Yes, same uid | Yes |
| MCP servers, command hooks, monitors, LSP, status line, credential helpers | No [D] | Yes if same uid and not root [D that they run as the user; I] | Yes [D] |
| Codex shell and patch tools | Seatbelt covers spawned commands [D]; patch tool U | Yes [I] | not applicable |
| Codex MCP servers | Own controls [D] | Yes if same uid [I] | not applicable |
| Anything root-run or sudo-capable | n/a | Not covered by A, C; covered by B [D `mount(8)`] | n/a |

## What I could not establish

- Behavior of Claude Code 2.1.301 and Codex 0.163.0 when a plugin update meets a root-owned,
  read-only or immutable cache tree (error text, retries, partial state, the `.orphaned_at`
  write). No test was run against a protected cache.
- Whether `~/.claude/plugins/cache` is already inside the Bash sandbox's protected list.
- Whether Codex has any seed or in-place read-only plugin location. None found in the
  docs or in `core-plugins` source at `rust-v0.163.0`; other crates were not searched.
- Whether Codex's `apply_patch` runs inside its Seatbelt sandbox.
- Whether `sudo` on this machine accepts Touch ID or has a `sudo_local` rule: only the
  `-n` password check was run.
- macOS 27 specifics. xnu citations come from the public `xnu-12377` line; the machine
  runs `xnu-13432`. The securelevel and owner-exception behavior was *observed* on macOS
  27.0.1 only for the owner case (`uchg`, ACL), not for `schg` or `securelevel`.
- A persistent root-owned read-only mount recipe (launchd job, `fstab`, or APFS snapshot) and
  its boot ordering; whether helpers run from an attached image under quarantine/Gatekeeper.
- Whether the Claude auto-mode classifier accepts `access(2)`-style probes.
- A non-admin ("Standard") agent account, whose home-directory and Keychain access were not
  investigated.

## Sources

Apple, local on macOS 27.0.1: `man chflags`, `man 2 chflags`, `man chmod`, `man 8 mount`,
`man hdiutil`, `man 2 access`, `man 2 rename`, `man sysctl`, `man csrutil`.

Apple, web: Apple Platform Security, System Integrity Protection
(support.apple.com/guide/security/system-integrity-protection-secb7ea06b49/web);
System Integrity Protection Guide, Introduction and File System Protections
(developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/).

Apple open source: apple-oss-distributions/xnu at `f6217f891ac0`: `bsd/vfs/vfs_subr.c`
(`vnode_immutable`, `vnode_authorize_simple`), `bsd/kern/kern_sysctl.c` (`sysctl_securelvl`),
`bsd/vfs/vfs_syscalls.c` (`safedounmount`, mount update).

Claude Code docs (read 2026-10-16): code.claude.com/docs/en/ plugins/loading,
plugins-reference, plugins/org, env-vars, sandboxing, sandbox-environments, permissions,
managed-settings.

Codex: developers.openai.com/codex/plugins/build; learn.chatgpt.com/docs/sandboxing,
/docs/permissions, /docs/config-file/config-reference; openai/codex at `rust-v0.163.0`:
`codex-rs/core-plugins/src/store.rs`, `installed_marketplaces.rs`.

Local observations: scratch files and a scratch disk image under `/tmp` (deleted), and
read-only listings of `~/.claude/plugins` and `~/.codex/plugins`. No real file was changed.
