# Desktop app surface

Authored guidance, not an observed run. This page says what each section of the generated skill pins for a native desktop app. An Electron app follows the generator's own browser recipe and reads nothing here.

- **Launch:** the repository's build command, then the app started with its own profile or data directory, so it leaves the user's real profile alone. Ready means the main window exists and the driver can reach its first control.
- **Doctor:** the running binary is the build under test, there is one instance, the window is on screen, and the driver's operating-system permission is granted. A missing permission, such as macOS Accessibility, is a prerequisite to name for the user.
- **Drive:** the repository's own UI tests first. Otherwise the platform's accessibility layer: XCUITest on macOS, UI Automation on Windows, AT-SPI on Linux. A Tauri app can use WebDriver through `tauri-driver`, which Tauri documents for Windows and Linux. Select by accessibility identifier, name or role, not by screen coordinates.
- **Evidence:** a window screenshot per checkpoint, the state of the queried element, and the side effect read back: the saved file, the setting that survives a relaunch, or the row in the local database. Keep the app log for the run.
- **Cleanup:** quit the instance this run started, by PID, and remove its scratch profile. The user's own running copy stays untouched.
- **Isolate:** many desktop apps allow one instance or share one profile directory. If a second instance cannot run beside the user's own, say so in the generated skill and decline to drive the user's instance.
