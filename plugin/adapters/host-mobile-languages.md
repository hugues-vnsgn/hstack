# Swift and Kotlin scope

Before reading or editing `.swift`, read `../skills/swift-best-practices/SKILL.md`
in full. Before reading or editing `.kt` or `.kts`, read
`../skills/kotlin-best-practices/SKILL.md` in full. Resolve these paths from this
adapter's directory. These are scoped bundled file reads on both hosts, as
[host.md](host.md) specifies. `paths` metadata establishes no auto-load.
Each fresh worker performs its own reads before the relevant source.

Read the baseline first, then inspect consumer configuration and declarations
to select conditional references. Record the relevant paths and declarations.
Use source sets, imports, plugins and native entry points together. A filename
alone establishes language, not platform, framework or shared ownership.
Keep unresolved ownership explicit until source and configuration establish it.

The following selection cases name the required body and conditional references.
Paths in the last two columns are relative to `../skills/`. A dash means none.
Read only references whose subject the affected behavior reaches.

| Source and configuration evidence | Baseline | Conditional references |
| --- | --- | --- |
| Swift package, Package.swift targets and Swift declarations, no UI imports | swift-best-practices/SKILL.md | - |
| SwiftUI app, SwiftUI import and View or App declaration | swift-best-practices/SKILL.md | swift-best-practices/references/swiftui.md |
| UIKit app, UIKit import and controller or view declaration | swift-best-practices/SKILL.md | swift-best-practices/references/uikit.md |
| Native Android Compose, Android plugin and Compose UI declarations | kotlin-best-practices/SKILL.md | kotlin-best-practices/references/android-compose.md |
| Common Kotlin, multiplatform plugin and commonMain or commonTest declarations | kotlin-best-practices/SKILL.md | kotlin-best-practices/references/kmp.md |
| Platform Kotlin, multiplatform plugin and iosMain native API declarations | kotlin-best-practices/SKILL.md | kotlin-best-practices/references/kmp.md, kotlin-best-practices/references/native-interop.md |
| CMP wrappers, Compose Multiplatform configuration and UIKitView or AndroidView declarations | kotlin-best-practices/SKILL.md | kotlin-best-practices/references/kmp.md, kotlin-best-practices/references/cmp.md |
| Kotlin build scripts, build.gradle.kts or settings.gradle.kts without app declarations | kotlin-best-practices/SKILL.md | - |
| Unrelated non-mobile task, no Swift or Kotlin source read or edited | - | - |

Combine applicable rows for mixed SwiftUI and UIKit work. Swift callers of an
exported Kotlin API also read `kotlin-best-practices/references/native-interop.md`.
Android platform source in a KMP module adds Android guidance only for affected
Android lifecycle or UI behavior. Common Kotlin without UI loads no Compose
reference. CMP on iOS adds native interop when the exported boundary is affected.
Generic Kotlin or `.kts` scripts load the Kotlin baseline without Android or KMP
assumptions. Kotlin DSL does not establish an app's implementation language.

This selection does not choose an action playbook or grant execution authority.
For explicit mobile tasks, [mobile workflows](mobile-workflows.md) still applies.
Consumer and external skills retain native invocation controls. Personal expert
skills can supplement this guidance. Their absence does not block this baseline.
