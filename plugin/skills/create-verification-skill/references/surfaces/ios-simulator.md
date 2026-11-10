# iOS simulator surface

Authored guidance, not an observed run. When the [mobile adapter](../../../../adapters/mobile-workflows.md) applies to the task, its authority, tool and evidence rules win over this page. This page says what each section of the generated skill pins on a simulator.

- **Launch:** the scheme, the configuration and the simulator by UDID, because two simulators can share a device name. Build through the [native execution helper](../../../../adapters/native-execution.md). Ready means the app's first screen is up on the pinned simulator. A passing build or a booted simulator is not ready.
- **Doctor:** the simulator with that UDID is booted, the installed app's bundle ID and build match the artifact just built, and the app is in the foreground.
- **Drive:** the repository's own UI path first: its `test-ios` skill, its XCUITest target, or the tool its instructions mandate. `simctl` installs, launches and captures, but it cannot tap or type, so a journey needs one of those. Select by accessibility identifier or label, not by coordinates.
- **Evidence:** the result bundle of each test run, a screenshot or recording per checkpoint with the UDID and build beside it, and the app's log for the run. A screenshot shows appearance, not that an action succeeded.
- **Cleanup:** terminate the app and remove the data this run created. Shut down or erase a simulator only when this run booted it. The user's other simulators keep their state.
- **Isolate:** one simulator per concurrent run. Two runs on one simulator share the app's data and mix their evidence.
