# KMP source sets and contracts

Inspect the configured hierarchy and dependsOn relationships. Keep platform APIs
in their declared platform source sets. Common tests exercise common contracts
but each configured runner observes only its own runtime. Name the affected
Android and iOS callers before choosing tests.

Prefer a common interface with injected platform implementations when the
behavior is an ordinary dependency. Use expect/actual where platform linkage or
declarations require it within the existing design. Check that every affected
target supplies its implementation. The stability of expected classes and
related compiler warnings depends on the Kotlin version. Verify the configured
compiler rather than assuming all expect/actual forms share the same status.
See [expected and actual declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html).

Keep dispatcher selection, persistence, networking and clock dependencies behind
the existing common contract. Android lifecycle classes do not belong in common
logic. Assert shared values, error behavior and cancellation on each affected
target. Then exercise the native callers. JVM success does not verify an iOS
export. Read [native interop](native-interop.md) when Kotlin/Native declarations,
cinterop or exported APIs are involved. Read [CMP](cmp.md) only for shared UI.
