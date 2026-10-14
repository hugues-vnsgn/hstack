# Native setup-to-proof regression

Run this opt-in check on an authorized Mac with Xcode, an available iOS runtime,
XcodeGen, Python 3 and an authenticated Claude Code CLI:

```sh
python3 scripts/check_setup_proof.py --output /absolute/new/evidence-directory
```

The command copies the plugin and sample consumer into the new external folder.
It invokes setup without requesting a verification skill and fails if mobile setup
skips the offer despite the existing harness. It accepts the offer in a second
session, requires a generated recipe and generation proof, then invokes that
recipe in a fresh native session and requires another successful iOS proof.
The harness taps Greet with XCUITest and checks the visible and persisted output;
Claude inspects the retained screenshot. Every run owns a new simulator.

A missing tool, host error, permission denial, omitted offer, undiscovered recipe,
failed feature assertion or failed cleanup exits nonzero. Logs and evidence remain
in the output directory, including on failure. An existing output directory is
refused. Use `--plugin /path/to/plugin` to test another candidate or the pre-fix
plugin. Authentication is supplied by the runner's existing Claude setup; the
check does not configure credentials or persistent permissions.

`.github/workflows/setup-proof.yml` exposes the same command as an explicit
workflow dispatch on a self-hosted macOS runner labeled `huguesstack-proof`.
Provisioning or dispatching that runner is separate from this local check.
The ordinary unittest suite checks source contracts and installed command paths
without requiring Claude credentials or a simulator. A source pass is not a native
host pass; a local native pass is not evidence that the CI runner is configured.

The sample covers one native iOS button-driven feature on Claude Code. It does not
prove Codex setup, Android, KMP/CMP, touch gestures or a consumer application's
full feature map. The one-feature sample is the generator's entire feature map,
not the bounded-mobile extension.
