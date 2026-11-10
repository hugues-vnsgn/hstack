# Android emulator surface

Authored guidance, not an observed run. When the [mobile adapter](../../../../adapters/mobile-workflows.md) applies to the task, its authority, tool and evidence rules win over this page. This page says what each section of the generated skill pins on an emulator.

- **Launch:** the build variant, the APK it produces and the device by serial, such as `emulator-5554`. Build through the [native execution helper](../../../../adapters/native-execution.md). Pass `-s <serial>` on every `adb` command. Ready means `sys.boot_completed` reads `1` and the app's first screen is up. A running emulator process is not ready.
- **Doctor:** `adb devices` lists that serial as `device`, the installed package's version matches the APK just built, and the app's activity is in the foreground.
- **Drive:** the repository's own UI path first: its `test-android` skill, its instrumentation tests, or the flow files of a UI runner it already uses. Plain `adb` taps by coordinates only, so a journey needs one of those. Select by resource ID, content description or test tag.
- **Evidence:** the instrumentation report of each run, a screenshot or recording per checkpoint with the serial and APK identity beside it, and the logcat output for the run. A screenshot shows appearance, not that an action succeeded.
- **Cleanup:** stop the app and clear only this app's test data. Stop an emulator only when this run started it. The user's other devices keep their state.
- **Isolate:** one emulator per concurrent run, each with its own serial. Two runs on one device share the app's data and mix their evidence.
