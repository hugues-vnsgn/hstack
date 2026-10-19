# Authoring, review and publication

Cursor create-skill translates to an available agent-writing skill plus this
repository's package checks. Before commits, use the bundled deslop
and the pinned unslop and technical-writing skills; retain no-comments before
review. Control steps use the bundled control-cli and control-ui skills.
Missing external writing-for-agents is reported as a capability gap, never
silently marked performed. The bundled pinned
unslop remains the prose contract.

On Claude Code and Codex, "Bugbot" in pstack's text means the review bot installed
on the repository: Claude Code Review or the Claude GitHub Action review workflow
(both post as the Claude GitHub App), Codex review (`chatgpt-codex-connector`), or
Cursor Bugbot. `bugbot-triage.md` applies to its comments unchanged, and the PR
watcher's `isBugbot` and `bugbotReviewPasses` cover each. The watcher's match on
Claude's login, `claude`, is unconfirmed until a Claude review is seen on a PR. The
user installs the bot and setup installs nothing. When no review bot is installed on
the repository, record the plan box "Bugbot triage done." as
`Bugbot triage done. Not applicable. Reason no review bot.`, leave it unticked,
name it not applicable in the verdict and never tick it as if triage happened.
