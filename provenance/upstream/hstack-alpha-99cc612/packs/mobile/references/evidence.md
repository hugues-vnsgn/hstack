# Mobile evidence

Select checks from the repository's documented commands and the changed target.
Record every command as an argv array, its outcome, and paths to its evidence.
Keep unavailable checks blocked with the missing tool or host as the reason.

| Family | Required evidence when affected |
| --- | --- |
| Android/Kotlin | Run the selected Gradle build/test tasks. Prove user-visible behavior on an emulator or device when available. |
| KMP | Run tests for each affected target. Check exported APIs and interop when the change crosses the platform boundary. |
| Compose Multiplatform | Run affected target tests and exercise the changed UI on the target runtime; a successful JVM test does not prove iOS UI behavior. |
| iOS/Swift | Run repository-selected Xcode build/test tasks on a configured Mac and prove changed behavior on a simulator or device when available. Defer these checks on other hosts. |

When a runtime is unavailable, record the missing evidence explicitly. Never
replace device behavior evidence with a compilation claim. Passing one family
does not prove support for another. Gate B provides the contract and initial
guidance; production pack workflows and device proof close in Gate F.

Read [platforms.md](./platforms.md) when choosing target-specific commands.
