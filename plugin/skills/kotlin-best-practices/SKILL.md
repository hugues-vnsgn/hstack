---
name: kotlin-best-practices
description: Kotlin state, nullability, coroutines and testability guidance with conditional platform and interop references.
paths: ["**/*.kt", "**/*.kts"]
disable-model-invocation: true
---

## Host invocation contract

Before tools, read [host contract](../../adapters/host.md)
and [mobile applicability](../../adapters/mobile.md#applicability) in full, then apply.
The host contract governs how this skill reaches any sibling dependency.

# Kotlin best practices

Read this body before Kotlin source or scripts. Inspect the consumer's Kotlin,
coroutines and Gradle plugin versions, language and API settings, source sets and
declared targets. Load platform guidance from declarations and configuration.
Kotlin DSL build scripts establish build logic, not Android application code.
Keep script changes within the wrapper and plugin APIs that the repository uses.

| Decision | Guidance |
| --- | --- |
| Contracts | Use nullability to represent meaningful absence. Validate platform types at the external boundary. Prefer exhaustive sealed alternatives for distinct states and failures. Replace a forced non-null assertion with the ownership or validation rule that makes the value available. |
| Exposed state | Expose immutable values and read-only StateFlow while retaining mutation with its owner. A val or read-only collection interface does not make referenced mutable objects deeply immutable. Keep state transitions explicit. |
| Coroutine ownership | Use a scope whose lifetime matches the operation. Keep child work structured. GlobalScope or a detached Job needs a concrete lifetime justification. Suspending APIs do not establish background execution. Make blocking operations safe for the caller's dispatcher. |
| Cancellation | Preserve CancellationException through catches and result wrappers. Use cancellable suspension and check cancellation in CPU loops. Release resources in finally. Restrict NonCancellable to the cleanup that actually requires suspension. |
| Tests | Inject dispatchers and existing dependency seams. With supported kotlinx-coroutines-test, use runTest and test dispatchers sharing one scheduler. Advance virtual time or await explicit state instead of arbitrary delays. Verify cancellation and error to retry transitions. |

Follow [Kotlin conventions](https://kotlinlang.org/docs/coding-conventions.html)
and the configured [coroutine test API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/).
The coroutine ownership and main-safety recommendations follow
[Android coroutine practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices).
Their Android scope examples apply only to Android. Check API availability and
experimental annotations against the consumer's dependency versions.

Load only the applicable references.

- Android lifecycle or Android Compose UI requires [Android Compose](references/android-compose.md).
- Multiplatform source sets or contracts require [KMP boundaries](references/kmp.md).
- Kotlin/Native, cinterop or exported Swift callers require [native interop](references/native-interop.md).
- Compose Multiplatform UI or native wrappers require [CMP](references/cmp.md).

Common Kotlin without UI requires no Compose reference. A Kotlin build script
requires no platform reference unless its actual task changes that platform's
behavior. Consumer verification recipes and affected native target proof remain
part of the selected action.
