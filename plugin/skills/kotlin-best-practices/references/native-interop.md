# Kotlin/Native and Swift boundaries

Inspect the actual exported framework or Swift export configuration and generated
API. Objective-C export and Swift export have different capabilities. Match the
consumer's Kotlin version and export mode before advising on generics, suspending
APIs or error mapping. Check cinterop definition files, headers, target-specific
linker settings and pointer lifetimes. Keep native memory ownership and callback
lifetime explicit.

For Objective-C export, inspect @Throws and the generated NSError contract.
Unlisted exceptions crossing the boundary can terminate the process. Suspending
export has its own cancellation and completion rules. Do not assume a Swift Task
cancellation cancels the underlying Kotlin Job. Inspect the actual bridge and
test propagation in both directions. Callbacks must deliver UI changes on the
required executor. See [Swift and Objective-C interoperability](https://kotlinlang.org/docs/native-objc-interop.html).

Trace Swift closures, Kotlin objects and native delegates as one ownership graph.
ARC release and Kotlin GC happen at different times. Mixed cycles can retain
objects. Check disposal, callback unregister and long-lived references. Deinit
thread behavior depends on where objects enter Kotlin and runtime settings.
Do not put required main-thread cleanup in a deinitializer based on an assumed
collection thread. See [ARC integration](https://kotlinlang.org/docs/native-arc-integration.html).

Verify the changed API through both affected native callers. Assert values,
failure, callback threading, cancellation and release where applicable. Linking
a framework is build evidence only. Keep unknown bridge behavior as a named gap.
