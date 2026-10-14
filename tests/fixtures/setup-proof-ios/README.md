# Setup proof iOS consumer

This disposable native iOS app has one user feature: tapping **Greet**
displays **Hello, Codex!** and persists the greeting in the app's Documents folder.
It has an existing harness and deliberately has no project verification skill.
Use the consumer's `.claude/skills/` convention for any generated recipe.

Run `python3 proof.py` with `ISSUE35_EVIDENCE_ROOT` set to an absolute evidence
directory outside this consumer. The harness uses XcodeGen and Xcode to build the app and its XCUITest target,
creates its own iPhone simulator on an available iOS 17+ runtime, and runs one
UI test that taps Greet and asserts the greeting. It checks persisted output and
exports the test screenshot. It shuts down and deletes only its own simulator.
Command results, the app, greeting, screenshot and cleanup result survive there.

This is a real device harness, not a project verification skill. The generated
skill should wrap it, identify this single feature, and inspect the greeting and
screenshot after cleanup. Use Read for the screenshot. No external screen judge,
MCP service or network service is required. The sample has no other features,
no shared platform, and one UI test and no separate unit-test target. Report those scope limits.
