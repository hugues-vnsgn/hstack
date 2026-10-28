#!/usr/bin/env bash
# hStack host detection. Runs at session start in Claude Code.
#
# A session in an ADE, or in an agent beyond Claude Code and Codex, needs the hosts
# index before its first dispatch. Prose could not make that reliable: across rounds
# 2 to 4 of PR 142, a session read the index in 2 of 6 Orca runs, and the runs that
# skipped it never mentioned Orca at all. A hook does the test where the session
# cannot miss it.
#
# The hook adds no gate and no authority. It names one file to read, and the
# session reads nothing under hosts/ when no test matches.
#
# The written check in host-workers.md stays. It is the only path for Codex and
# omp, which load no plugin hook, and it covers a T3 Code thread that exposes no
# Orca variable.
#
# Observed: in an Orca 1.4.241 pane, ORCA_TERMINAL_HANDLE, ORCA_PANE_KEY and
# ORCA_TAB_ID are all set. Unobserved: a T3 Code thread exposes no Orca variable,
# and the hook cannot see the tools a session was given, so such a thread keeps the
# written check.
set -u

# A plain terminal session reads no hosts page. Print nothing, so the session
# starts with no extra bytes.
if [ -z "${ORCA_TERMINAL_HANDLE:-}" ] && [ -z "${ORCA_PANE_KEY:-}" ] && [ -z "${ORCA_TAB_ID:-}" ]; then
    exit 0
fi

# The message holds no quote, backslash or control character, so it is a JSON
# string as it stands. The path is absolute, so the session reads the index of the
# plugin it loaded rather than one guessed from the working directory.
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"This session runs in an ADE. Before your first dispatch, read %s/adapters/hosts/README.md in full, then read the page of the first ADE or agent in its lists whose detection test is true. A session that matches no line reads no page."}}\n' "${CLAUDE_PLUGIN_ROOT:-.}"
