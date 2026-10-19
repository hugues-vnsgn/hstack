# Compose Multiplatform and native wrappers

Inspect the consumer's Compose Multiplatform, Kotlin and platform dependency
versions. Shared UI does not establish identical input, navigation or lifecycle
behavior on Android and iOS. Identify the native controller or activity that
owns the composition, its state and its coroutine work.

Keep wrapper creation separate from updates. For UIKitView or UIKitViewController,
apply current Compose state in the supported update API, keep callbacks current
and release delegates, observers and native resources on disposal. Inspect the
version's onRelease and reuse contracts. A remembered instance must have an
explicit owner. Preserve controller containment and keyboard behavior. See
[UIKit integration](https://kotlinlang.org/docs/multiplatform/compose-uikit-integration.html).
For AndroidView, check the configured Compose API's factory, update, onReset and
onRelease contracts before enabling reuse. See
[Android view integration](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/views-in-compose).

Test a state update after creation, disposal and re-entry for duplicate callbacks
and leaked work. Exercise touch arbitration, focus, scrolling, navigation and
keyboard dismissal on each runtime. Interop interaction modes and native
accessibility options vary with CMP versions. Read the installed API and
[iOS touch guidance](https://kotlinlang.org/docs/multiplatform/compose-ios-touch.html)
before choosing them. Verify semantics, screen-reader reachability and text
scaling on both runtimes. One screenshot establishes appearance only.

Read [native interop](native-interop.md) for exported iOS boundaries. Android
lifecycle guidance applies to Android ownership only. Keep two target results,
including failed, skipped and unobserved cases.
