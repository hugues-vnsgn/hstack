# Bundled control-skill validation

On 19 October 2026, worker-1 read both bundled procedures in a Codex session.
The CLI procedure ran against a disposable Python prompt through local tmux.
The UI procedure reached setup but could not run an interaction.

## CLI observation

The repository has no application CLI to exercise. A temporary fixture printed
`HSTACK CLI READY` and `command>`, accepted `help`, and printed
`AVAILABLE: help, quit` followed by another prompt. The harness used
`tmux new-session`, `capture-pane` and `send-keys` in that order.

Before sending input, the captured pane contained:

```text
HSTACK CLI READY
command>
```

The harness sent one action, `help` followed by Enter. It polled `capture-pane`
until the response marker appeared, with a five-second deadline. The resulting
pane contained:

```text
HSTACK CLI READY
command> help
AVAILABLE: help, quit
command>
```

The before capture lacked the response marker. The after capture included it.
The harness saved both captures, killed its named tmux session and verified
that `tmux has-session` failed for that session. It removed the temporary
fixture. The private worker evidence retains the captures and result receipt.
This observes one harmless terminal flow. It does not establish profiling,
terminal resize, consumer CLI behavior or native skill-menu invocation.

## UI gap

A disposable local HTTP page exposed a stable application marker, an
`Increment` button and a `Count: 0` status. The host's
`cua.createBrowserTab("iab", local_url, { visible: false })` returned
`Browser is not available: iab`. `cua.listBrowsers()` returned `[]`.
The repository had no installed Playwright or Puppeteer package, and Python
Playwright was unavailable. No browser dependency was added.

No UI action or after-state was observed. The local server stopped and the
fixture directory was removed. Browser interaction, screenshots, CDP and
Electron remain gaps. The bundled source and links passed static validation;
that does not replace an observed UI run.
