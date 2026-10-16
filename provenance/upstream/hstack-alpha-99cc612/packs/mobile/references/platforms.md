# Mobile platform discovery

Inspect build files and the repository's own instructions before choosing tasks.
Detection markers identify a candidate pack; they do not identify every target
or establish a working SDK.

- For Android/Kotlin, inspect Android plugins, modules, build variants, and the
  wrapper. Use the repository's chosen unit and instrumentation test tasks.
- For KMP, inspect targets and source sets. Place proof at the changed boundary:
  shared logic needs shared tests, while platform adapters need target tests.
- For Compose Multiplatform, identify each deployed UI target and interop view.
  Test the affected runtime for input, navigation, and accessibility changes.
- For iOS/Swift, inspect the workspace, project or package and its schemes and
  test destinations. Use the repository's signing and simulator configuration.

Display proposed argv commands before executing them. Keep credentials,
provider launch settings, worktree ownership, and cleanup outside pack policy.
