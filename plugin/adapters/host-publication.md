# Authoring, review and publication

create-skill means writing-for-agents plus package checks.
Before commits use bundled deslop, unslop and technical-writing, before review
no-comments, and for control bundled control-cli or control-ui.
Missing writing-for-agents is reported as a capability gap, never silently marked performed.
The bundled pinned
unslop remains the prose contract.

On every host, "Bugbot" means installed Claude Code Review,
Claude GitHub Action review workflow, Codex review (`chatgpt-codex-connector`)
or Cursor Bugbot. Both Claude bots use the Claude GitHub App.
`bugbot-triage.md` applies to its comments unchanged.
Watcher `isBugbot` and `bugbotReviewPasses` cover all. The watcher's match on
Claude's login, `claude`, is unconfirmed until a Claude review is seen on a PR. The user installs the bot and setup installs nothing.
Without a bot, record the plan box "Bugbot triage done." as
`Bugbot triage done. Not applicable. Reason no review bot.`,
leave it unticked, report not applicable and never tick it as if triage happened.

With publication held or no remote or forge, save local PR title and body
separately. Check Opening a PR's format, section order, Scope and verification.
Report paths and hold. Skip only forge writes. Drafts grant no authority.
