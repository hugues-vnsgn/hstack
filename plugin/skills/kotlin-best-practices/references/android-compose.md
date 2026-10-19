# Android lifecycle and Compose

Keep screen work in its lifecycle owner. With the consumer's supported AndroidX
Lifecycle version, collect UI flows with collectAsStateWithLifecycle or
repeatOnLifecycle. A ViewModel can survive configuration changes but not process
death. Preserve only the minimal restorable input through the project's saved
state mechanism and reconstruct derived state. Test both recreation and process
restoration when affected. See [lifecycle collection](https://developer.android.com/topic/libraries/architecture/lifecycle)
and [state saving](https://developer.android.com/develop/ui/compose/state-saving).

Keep composable evaluation free of work with external effects. Choose
LaunchedEffect keys for restart and cancellation, rememberUpdatedState for a
current callback in a retained effect, and DisposableEffect for paired cleanup.
Composition lifetime and Android foreground lifetime differ. Select both
explicitly when an operation must stop in the background.
See [Compose effects](https://developer.android.com/develop/ui/compose/side-effects).

Check state hoisting, stable item identity, duplicate collectors and stale retry
results. Move blocking work off the main dispatcher at the owning dependency.
Verify affected navigation and back behavior, keyboard and focus, TalkBack
semantics and large font scale on the Android target. Use the existing unit seam
for transitions and platform tests for lifecycle or native ownership behavior.
AndroidX APIs and experimental annotations must match installed versions.
