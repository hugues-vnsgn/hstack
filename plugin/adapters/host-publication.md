# Authoring, review and publication

Cursor create-skill translates to an available agent-writing skill plus this
repository's package checks. Before commits, use the bundled deslop
and the pinned unslop and technical-writing skills; retain no-comments before
review. Missing external control-cli, control-ui or writing-for-agents is
reported as a capability gap, never silently marked performed. The bundled pinned
unslop remains the prose contract; an owner's differently worded skill is an
additional style preference, not a source-equivalent replacement.

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

Opening a PR retains the core's ready-PR and stack/base mechanics. Local commits
and a PR-ready body can be prepared under local-work authority. Publication waits
for explicit scope. Only this hStack repository’s AGENTS.md activates its
Astra High PR profile. Installing the plugin does not impose it on consumers.
Consumer policies and generic interrogate defaults remain in force.
That AGENTS.md currently suspends the profile, so no Astra review gate applies.
