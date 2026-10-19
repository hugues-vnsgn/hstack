# Native runtime forensics

Translate Runtime forensics steps 1 to 4 for the selected mobile runtime.
Keep the diagnosis deliverable, source mapping and read-only throughput checkpoint.
Use authorized tools that exist on this host and can inspect the actual target.
Inspect tool and OS versions, build configuration, symbols and attach capability
before capture. Name unavailable capture or intervention as a gap.

| Mechanism | Swift or Kotlin/Native on iOS | Kotlin or Compose on Android |
| --- | --- | --- |
| CPU spin or blocked UI | Instruments Time Profiler or an authorized process sample with symbolicated stacks. Use signposts or debugger probes to correlate the triggering action. | System Trace or Perfetto for scheduling and UI stalls, CPU profiling for hot methods. Capture the affected app process and interval. |
| Retained objects | Xcode Memory Graph for reference paths, Instruments Allocations or Leaks for lifetime evidence. Include native and Kotlin ownership where a bridge participates. | Heap dump and allocation tracking with a debuggable target. Reduce the retained Activity, ViewModel or wrapper path to its retaining owner. |
| Rendering or input glitch | Native hierarchy inspection and a matching Instruments trace, with a recorded action and resulting state. | Layout Inspector and a matching system trace, with the action, semantics and resulting state. |
| Coroutine or callback lifetime | Debugger, signposts and explicit task or callback lifetime probes across the native boundary. | Coroutine debugger when supported, trace events or explicit job lifetime probes correlated with the lifecycle owner. |

The table selects a capture, not a preset conclusion. Reduce the real artifact
to a hot stack, retainer path or repeated event. Preserve the full trace outside
model context and retain timestamps, process, target and tested artifact identity.
For KMP or CMP, capture on the runtime where the symptom occurs. A JVM trace
cannot establish an iOS mechanism.

At step 3, use debugger breakpoints, signposts or a reversible instrumented build
on the same runtime to test the hypothesis. Native targets need no CDP eval or
browser reload. If rebuilding is necessary, record the new artifact and repeat
the trigger. Compare the predicted signal before and after the probe. If an
intervention is unavailable, report the hypothesis as unconfirmed. Keep probe
edits disposable and restore them before handing off to Bug fix or Perf.

Tool capabilities differ by Xcode, Android Studio, OS and build type. Memory
inspection may require a debuggable build while CPU profiling can use a
profileable build. Check the applicable tool's requirements and avoid a
physical-device performance claim from a simulator capture. See
[Xcode memory tools](https://developer.apple.com/documentation/xcode/gathering-information-about-memory-use),
[Android profiling requirements](https://developer.android.com/studio/profile)
and [Kotlin ARC integration](https://kotlinlang.org/docs/native-arc-integration.html).
