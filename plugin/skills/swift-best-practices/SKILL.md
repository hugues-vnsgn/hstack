---
name: swift-best-practices
description: Swift API, ownership, concurrency and testability guidance with conditional platform references.
paths: ["**/*.swift"]
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Swift best practices

Read this body before Swift source. Inspect the consumer's compiler, Swift
language mode, strict-concurrency level, default actor isolation, upcoming
features and deployment targets. Inspect Package.swift or Xcode settings for
each affected target. A Swift 6 compiler can compile Swift 5 language mode.
Preserve the project's conventions and availability constraints.

| Decision | Guidance |
| --- | --- |
| API | Check the call site. Name effects and argument roles clearly. Represent absence, failure and domain alternatives explicitly instead of sentinel values. Follow the [API design guidelines](https://www.swift.org/documentation/api-design-guidelines/). |
| Ownership | Prefer value semantics for independent data. Use a reference for shared identity or managed lifetime. Trace stored closures and delegates through their owners. Choose weak captures from the required lifetime, rather than applying them to every closure. |
| Isolation | Identify who owns mutable state. Use actor isolation for shared state and MainActor for UI state. Review invariants again after every await because actor code can interleave. Sendable describes safe transfer, not automatic synchronization. |
| Execution | Async does not guarantee off-main execution. Check the configured isolation and compiler features before moving expensive work. Swift 6.2's NonisolatedNonsendingByDefault changes nonisolated async execution when enabled. |
| Tasks | Prefer structured child tasks for bounded work. An unstructured Task needs an owner and cancellation path. Propagate cancellation, check it in long loops, and release resources on every exit. Bridge callbacks with exactly one continuation resume and explicit cancellation behavior. |
| Tests | Keep domain transformations independent of UI and real time. Inject the clock or dependency at the existing boundary. Assert values, cancellation and failure behavior with the consumer's supported XCTest or Swift Testing tools. Sleeps do not establish synchronization. |

Concurrency rules follow the [Swift concurrency migration guide](https://www.swift.org/migration/)
and [language guide](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html).
Check [nonisolated async defaults](https://docs.swift.org/latest/documentation/diagnostics/nonisolated-nonsending-by-default/)
against the actual Swift version and enabled features before applying them.

Load only the references the affected declarations require.

- SwiftUI state, navigation or task lifetime requires [SwiftUI](references/swiftui.md).
- UIKit controllers, delegates or SwiftUI native wrappers require [UIKit](references/uikit.md).
- A Swift caller of exported Kotlin requires [native interop](../kotlin-best-practices/references/native-interop.md).

SwiftPM tests establish package behavior on their actual runner. They cannot
establish an iOS user journey. For mobile changes, keep the selected action's
native proof and consumer verification recipe.
