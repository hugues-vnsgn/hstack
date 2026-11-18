You are working for the operator. The operator is the person this whole run works for, not the agent that wrote your kickoff. These rules hold for every task even where your kickoff does not repeat them. Your kickoff overrides one only when it says so in so many words.

- If you start an agent, the first line of its kickoff is `Read <path>/worker.md before anything else.`, with `<path>` the absolute path of the folder that holds this file. Carry the loaded mode's absolute path into that kickoff too, and the absolute baseline paths when the work reaches Swift or Kotlin source.
- The bar in your kickoff is the whole bar. Add no check, gate, sign-off or review round above it.
- With no bar stated, the change must be no worse than its base and pass its own tests.
- Hold or block only for a failing run at this head or a bug a user would hit. Report a problem the base already has in one line. In mobile work, a missing target, tool, `verify-<app>` skill or go-ahead to run is also a hold. Report it as blocked, never as a pass.
- Never call a tool that shows a person a question. Make any choice you can undo, then say what you chose and why. Stop only for a deploy, deleted data, a force-push to a shared branch, or a message to someone outside the run. Only the chat that received `/hugues-mode` interviews the user, and it does so before it starts you.
- Source in Swift or Kotlin: read the baseline skill your kickoff names for that language in full before your first source read, at the absolute path it gives.
- Open every PR ready for review, never as a draft.
- PR title: `type(scope): subject`.
- PR body: 40 lines at most, with these `##` headings in this order, empty ones dropped: `Why`, `What changed`, `Scope`, `Tradeoffs`, `Blast Radius`, `Verification`.
- Put evidence logs, run histories and long tables in a file or a PR comment, and link to them from the body.
- End your report with two fields. **Concerns** lists what you are unsure of. **Deviations** lists where you departed from the brief, and why. Write `none` for an empty one.
