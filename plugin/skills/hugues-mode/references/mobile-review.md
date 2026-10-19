# Mobile review lens

Apply this lens at the selected action's existing review phase. Load the
language baseline before affected source and only the applicable platform or
interop references through [mobile language scope](../../../adapters/host-mobile-languages.md).
Select risks from the changed behavior, ownership and targets. Record why a row
is inapplicable when it plausibly touches the change.

For every applicable risk, record the affected symbol and target, the failure
scenario, and either covered with a linked assertion or observation, or gap with
the missing check and reason. A proposed test is a gap until run. Review notes
alone do not establish behavior. Pass this record into the existing proof and
final report. Preserve separate Android and iOS outcomes for shared changes.

| Risk | Scenario and evidence to seek |
| --- | --- |
| Lifecycle and process restoration | Leave and return, recreate the owner, then restore after process loss when persistence is affected. Assert intended state and no duplicate work. Distinguish configuration recreation from process restoration. |
| Main-thread safety | Deliver a callback from its actual executor. Assert UI work reaches the required main thread or actor and blocking work does not stall it. Check across native exports as well as local callers. |
| Cancellation | Cancel during suspension, change identity and navigate away. Assert owned work stops, stale results cannot overwrite new state, and cancellation propagates through catches and bridges. |
| Resource release | Remove and recreate the owner. Assert subscriptions, tasks, observers and native handles are released, with no duplicate callback. Inspect mixed ARC and GC graphs when native boundaries change. |
| Offline, error and retry | Fail the affected request, enter the offline or error state, then recover. Assert state and retry effects, including late results and duplicate submissions where relevant. |
| Accessibility and text scaling | Drive the changed interaction with its semantics or hierarchy and enlarged text. Check focus, labels and reachable controls on each affected runtime. A screenshot alone cannot establish interaction. |
| Native-wrapper ownership | Create, update, dispose and re-enter the wrapper. Check current callbacks, controller containment, input, keyboard and navigation, plus disposal of retained native objects. |

Use existing cheap test seams for state and cancellation. Keep native lifecycle,
threading and UI claims tied to matching runtime observations. Tool or target
unavailability remains a named gap. This lens changes scenario selection inside
the existing ten-lane rule. It creates no new phase, lane-count policy or panel.
