#!/bin/bash

# PreToolUse hook for the implementer subagents: nothing a dispatched
# implementer runs may publish, close its Issue, or change a branch that is
# not an agent branch. Exit 2 = blocked, exit 0 = allowed.
#
# Two layers. git's destructive forms are left to the fork's hardened
# guardrail, skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.sh,
# which already blocks `git push` in every form it knows (plain, `git -C`,
# env-prefixed, after a separator). This script then enforces:
#
# - no publishing: opening or merging a pull request, a `gh api` write, or
#   syncing the beads remote;
# - no bd call without `--sandbox`, which disables Dolt auto-push;
# - no closing an Issue (`bd close`, `--status closed`): the orchestrator
#   closes it after the merge;
# - git changes only through `git -C <absolute path>` into a repository whose
#   checked-out branch starts with `agent/`. Read-only git runs anywhere. The
#   repository is never inferred from a `cd` or the payload's `cwd`: Codex
#   gives each shell call its own working directory and reports only the
#   session's in the payload, so an explicit `-C` is the one location both
#   harnesses let the hook see truthfully.
#
# The command `implementer-guard-check` is a canary: it is always blocked with
# a fixed message, so an implementer can prove at startup that its guard is
# live. Codex runs a command whose hook is missing, untrusted or crashed, so
# the canary is what turns a silent open failure into a FAILED report.
#
# Prose-only, in the implementing-an-issue skill: that the agent branch is the
# one the brief names, and that the implementer never merges into FEATURE. The
# hook cannot see the brief, so it enforces the class of branch, not the
# branch.
#
# Installed as a symlink by scripts/link-agents.sh; the guardrail is found by
# resolving that link back into the skills repo, so a `git pull` there keeps
# both current. Fails CLOSED, like the guardrail: a missing guardrail, a
# missing jq, an unreadable payload, or a git change whose repository or
# branch cannot be resolved blocks the command.
#
# A seatbelt, not a sandbox: it reads the command line, so a publishing call
# hidden inside a script file, a git alias (`git -c alias.p=push p`) or a
# Makefile target still gets through, and so does anything typed into a shell
# Codex already started (its `write_stdin` input is never hooked). It stops an
# implementer that follows or half-follows its instructions, which is the
# failure it exists for.

block() {
  echo "BLOCKED: $1 An implementer never publishes; the orchestrator and the user decide what leaves this machine." >&2
  exit 2
}

SELF="$(readlink -f "${BASH_SOURCE[0]}")"
# Vendored into this repo's .claude/hooks/ beside the guardrail it calls.
GUARDRAIL="$(dirname "$SELF")/block-dangerous-git.sh"

[ -f "$GUARDRAIL" ] || block "implementer guard cannot find the git guardrail at $GUARDRAIL."
command -v jq >/dev/null 2>&1 || block "implementer guard cannot run (jq not found on PATH)."

INPUT=$(cat)

# Any non-zero exit from the guardrail is a block: 2 is its verdict, anything
# else means it could not decide, and an undecided guard must not allow.
if ! printf '%s' "$INPUT" | bash "$GUARDRAIL"; then
  exit 2
fi

if ! COMMAND=$(printf '%s' "$INPUT" | jq -re '.tool_input.command' 2>/dev/null); then
  block "implementer guard could not read .tool_input.command from the hook payload."
fi

if [ "$(printf '%s' "$COMMAND" | tr -d '[:space:]')" = implementer-guard-check ]; then
  echo "BLOCKED: implementer guard is live." >&2
  exit 2
fi

# The guardrail matches only the plain shapes of a command, which suits a
# human's hook. This layer normalizes harder, because an implementer that
# reaches for a workaround should still hit the wall: every control operator,
# grouping and substitution starts a new segment, and each segment is peeled
# of wrappers (`command`, `env`, `nohup`, `bash -c "..."`, `/usr/bin/git`)
# until the real tool is first. The cost is over-blocking a quoted mention
# that contains a separator (`-m "a; gh pr create"`), which is acceptable for
# an agent that is not meant to write such commands anyway.
#
# A substitution also leaves a SUBST marker where it cut, so a git segment
# still sees that its `-C` path or subcommand came from one: without it,
# `git -C $(pwd) commit` would split into a `git -C` with nothing to check.
SUBST=__implementer_guard_substitution__
SEGMENTS=$(printf '%s\n' "$COMMAND" | sed -E "s/\\\$\\(|\`/ $SUBST\\n/g; s/\\|&|&&|\\|\\||[;|&(){}]/\\n/g")

# normalize <segment>: strip, repeatedly, leading whitespace and quotes, env
# assignments, wrapper commands with their flags, `sh -c`, and a directory
# prefix on the tool, until nothing changes.
normalize() {
  local s="$1" prev=""
  while [ "$s" != "$prev" ]; do
    prev="$s"
    s=$(printf '%s' "$s" | sed -E \
      -e "s/^[[:space:]\"']+//" \
      -e "s/^[A-Za-z_][A-Za-z0-9_]*=(\"[^\"]*\"|'[^']*'|[^[:space:]]*)([[:space:]]+|$)//" \
      -e 's/^(command|builtin|exec|eval|env|time|nohup|nice|sudo|xargs|stdbuf)(([[:space:]]+-[^[:space:]]*)*)([[:space:]]+|$)//' \
      -e 's/^timeout(([[:space:]]+-[^[:space:]]*)*)[[:space:]]+[^[:space:]]+([[:space:]]+|$)//' \
      -e 's/^(ba|z|da|k)?sh(([[:space:]]+-[^[:space:]]*)*)[[:space:]]+-[[:alpha:]]*c([[:space:]]+|$)//' \
      -e 's#^[^[:space:]]*/(git|gh|bd)([[:space:]]|$)#\1\2#')
  done
  printf '%s' "$s"
}

# Global flags may sit between a tool and its subcommand (`git -c k=v push`,
# `bd --actor "x" dolt push`), so FLAGS allows any run of `-flag` or
# `--flag value` tokens there, quoted values included. A bare word is never a
# flag, so a mention (`bd create "never run bd dolt push"`) does not match.
VALUE="(\"[^\"]*\"|'[^']*'|[^-[:space:]\"'][^[:space:]]*)"
FLAGS="([[:space:]]+-[^[:space:]]*([[:space:]]+${VALUE})?)*"
END="([[:space:]\"']|$)"
PUBLISHING_PATTERNS=(
  "git${FLAGS}[[:space:]]+push"
  "gh${FLAGS}[[:space:]]+pr${FLAGS}[[:space:]]+(create|merge)"
  "bd${FLAGS}[[:space:]]+dolt${FLAGS}[[:space:]]+(push|pull)"
)
# `gh api` reads are fine; any write (a non-GET method, or fields, which make
# gh send a POST) can open or merge a pull request by another route. Short
# options may carry their value attached (`-XPUT`, `-ftitle=x`) or follow the
# boolean `-i` (`-iXPOST`); the match ignores case, as HTTP methods do.
GH_API="^gh${FLAGS}[[:space:]]+api${END}"
GH_API_WRITE="(^|[[:space:]])(-i*X(=|[[:space:]]*)[\"']?(POST|PUT|PATCH|DELETE)|--method(=|[[:space:]]+)[\"']?(POST|PUT|PATCH|DELETE)|-i*[fF]|--(field|raw-field|input)([[:space:]=]|$))"
# bd pushes on its own when `dolt.auto-push` is on, so an ordinary write would
# sync the remote without any command above. `--sandbox` turns that off, and an
# implementer must pass it on every bd call. The flag is looked for with quoted
# text removed, so a comment that mentions it does not count as passing it.
BD="^bd${END}"
BD_SANDBOX="(^|[[:space:]])--sandbox([[:space:]]|=true|$)"
BD_CLOSE="^bd${FLAGS}[[:space:]]+close${END}"
BD_STATUS_CLOSED="(^|[[:space:]])(--status|-s)(=|[[:space:]]+)[\"']?closed([[:space:]\"']|$)"
# GIT_DIR and friends point git at another repository without `-C`.
GIT_REDIRECT="(^|[^A-Za-z0-9_])GIT_(DIR|WORK_TREE|COMMON_DIR|INDEX_FILE)="

strip_quoted() { printf '%s' "$1" | sed -E "s/\"[^\"]*\"//g; s/'[^']*'//g"; }

# tokens <segment>: the segment's words, one per line, quotes honoured the way
# a shell would. xargs parses the quotes and runs only printf; on a quote it
# cannot pair, fall back to dropping every quote and splitting on blanks.
tokens() {
  local out
  if out=$(printf '%s' "$1" | xargs -n1 printf '%s\n' 2>/dev/null); then
    printf '%s\n' "$out"
  else
    printf '%s' "$1" | tr -d "\"'" | tr -s '[:space:]' '\n'
  fi
}

# resolve <base> <path>: the absolute path <path> names from <base>, or nothing
# when it does not exist or <base> is unknown.
resolve() {
  local base="$1" p="$2"
  case "$p" in
    "~") p="$HOME" ;;
    "~/"*) p="$HOME/${p#\~/}" ;;
  esac
  case "$p" in
    /*) ;;
    *) [ -n "$base" ] || return 0; p="$base/$p" ;;
  esac
  (cd "$p" 2>/dev/null && pwd -P) || true
}

# git_reads <subcommand> <args...>: succeeds when the git call only reads.
git_reads() {
  local sub="$1" a
  shift
  case "$sub" in
    status|log|diff|show|rev-parse|rev-list|ls-files|ls-tree|ls-remote|cat-file|blame|annotate|grep|describe|shortlog|show-ref|show-branch|for-each-ref|merge-base|name-rev|whatchanged|version|help|var|check-ignore|check-attr|count-objects|cherry|diff-tree|diff-files|diff-index|range-diff|verify-commit|verify-tag)
      return 0 ;;
    branch)
      for a in "$@"; do
        case "$a" in
          --show-current|--list|-l|-a|--all|-r|--remotes|-v|-vv|--verbose|--sort=*|--format=*|--color*|--no-color|--column*|--no-column|--abbrev=*|--no-abbrev|-i|--ignore-case) ;;
          *) return 1 ;;
        esac
      done
      return 0 ;;
    config)
      for a in "$@"; do
        case "$a" in --get|--get-all|--get-regexp|--get-urlmatch|-l|--list) return 0 ;; esac
      done
      return 1 ;;
    symbolic-ref)
      [ "$(printf '%s\n' "$@" | grep -cv '^-')" -le 1 ] ;;
    stash)
      case "${1:-}" in list|show) return 0 ;; esac
      return 1 ;;
    worktree|remote|reflog|notes|tag)
      case "${1:-}" in ""|list|show|-v|--verbose|get-url|-l|--list) return 0 ;; esac
      return 1 ;;
  esac
  return 1
}

# check_git <segment>: block a git change that is not `git -C <path>` into an
# agent branch. Chained `-C`s resolve each against the one before, as git does;
# a relative first `-C` has no trustworthy base, so it stays unresolved.
check_git() {
  local dir="" named="" dynamic="" sub="" expect="" redirect="" t branch
  local -a args=()
  while IFS= read -r t; do
    if [ -n "$expect" ]; then
      if [ "$expect" = C ]; then
        named=1
        dir=$(resolve "$dir" "$t")
        case "$t" in *'$'*|*'`'*|"$SUBST") dynamic=1 ;; esac
      fi
      [ "$expect" = redirect ] && redirect=1
      expect=""
      continue
    fi
    if [ -z "$sub" ]; then
      case "$t" in
        git) ;;
        -C) expect=C ;;
        --git-dir|--work-tree) expect=redirect ;;
        --git-dir=*|--work-tree=*) redirect=1 ;;
        -c|--namespace|--config-env|--super-prefix|--exec-path) expect=skip ;;
        -*) ;;
        *) sub="$t" ;;
      esac
    else
      args+=("$t")
    fi
  done <<< "$(tokens "$1")"
  if [ -z "$sub" ]; then
    [ -n "$dynamic" ] && block "'$COMMAND' names git's repository with a shell variable or substitution, and the rest of the call cannot be read. Write the path out literally: 'git -C <absolute path of your worktree> ...'."
    return 0
  fi
  [ "$sub" = "$SUBST" ] && block "'$COMMAND' takes git's subcommand from a substitution, which the guard cannot read. Write the subcommand out literally."
  if git_reads "$sub" ${args[@]+"${args[@]}"}; then
    return 0
  fi
  case "$sub" in
    update-ref|branch|worktree)
      block "'$COMMAND' runs 'git $sub', which rewrites refs or worktrees the orchestrator owns." ;;
    fetch|pull)
      for t in ${args[@]+"${args[@]}"}; do
        case "$t" in -*) ;; *:*) block "'$COMMAND' fetches into a local branch ('$t')." ;; esac
      done ;;
  esac
  [ -n "$redirect" ] && block "'$COMMAND' points git at another repository with --git-dir or --work-tree. Use 'git -C <your worktree>'."
  [ -n "$named" ] || block "'$COMMAND' runs 'git $sub' without naming its repository. Run it as 'git -C <absolute path of your worktree> $sub ...'."
  [ -n "$dynamic" ] && block "'$COMMAND' names its repository with a shell variable or substitution, which the guard cannot expand. Write the path out literally: 'git -C <absolute path of your worktree> $sub ...'."
  branch=""
  [ -n "$dir" ] && branch=$(git -C "$dir" symbolic-ref --short -q HEAD 2>/dev/null)
  case "$branch" in
    agent/*) return 0 ;;
  esac
  block "'$COMMAND' changes a repository on branch '${branch:-unknown}' (${dir:-unresolved -C path}). An implementer changes only its agent/ branch: run 'git -C <absolute path of the worktree your brief names> ...'."
}

if printf '%s' "$COMMAND" | grep -qE "$GIT_REDIRECT"; then
  block "'$COMMAND' sets GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR or GIT_INDEX_FILE. Use 'git -C <your worktree>'."
fi

while IFS= read -r segment; do
  segment=$(normalize "$segment")
  [ -z "$segment" ] && continue

  for pattern in "${PUBLISHING_PATTERNS[@]}"; do
    if printf '%s' "$segment" | grep -qE "^${pattern}${END}"; then
      block "'$COMMAND' runs a publishing command ('${segment%% *} ...')."
    fi
  done
  if printf '%s' "$segment" | grep -qE "$GH_API" && printf '%s' "$segment" | grep -qiE "$GH_API_WRITE"; then
    block "'$COMMAND' writes through the GitHub API."
  fi
  if printf '%s' "$segment" | grep -qE "$BD"; then
    if ! strip_quoted "$segment" | grep -qE "$BD_SANDBOX"; then
      echo "BLOCKED: '$COMMAND' runs bd without --sandbox, which would let Dolt auto-push sync the tracker remote. Re-run it with --sandbox (for example 'bd --sandbox update <id> --claim')." >&2
      exit 2
    fi
    if printf '%s' "$segment" | grep -qE "$BD_CLOSE" || printf '%s' "$segment" | grep -qE "$BD_STATUS_CLOSED"; then
      echo "BLOCKED: '$COMMAND' closes an Issue. Leave it open: the orchestrator closes it once your work is reviewed and merged." >&2
      exit 2
    fi
  fi
  if printf '%s' "$segment" | grep -qE "^git${END}"; then
    check_git "$segment"
  fi
done <<< "$SEGMENTS"

exit 0
