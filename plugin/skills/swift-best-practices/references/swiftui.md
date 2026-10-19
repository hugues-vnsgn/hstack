# SwiftUI state and lifetime

Use the consumer's deployment target and observation model. SwiftUI Observation
requires iOS 17 or the corresponding supported OS. For that model, keep an owned
observable instance in State and use Binding or Bindable where mutation crosses
the view boundary. For ObservableObject code, distinguish StateObject ownership
from ObservedObject input. Preserve stable view and navigation identity. Check
that view recreation does not recreate long-lived work or discard intended state.
See [model ownership](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
and [Monitoring model data changes](https://developer.apple.com/documentation/swiftui/monitoring-model-data-changes-in-your-app).

Tie view work to the correct identity. A supported `.task(id:)` cancels and
restarts when its id changes and can cancel when the view disappears. The work
must cooperate with cancellation. Reject stale results after a changed query or
navigation. An inner unstructured Task needs its own lifetime contract.
See [view task lifetime](https://developer.apple.com/documentation/swiftui/view/task(id:name:priority:file:line:_:)).

Test disappearance and re-entry, changed inputs during suspension, and error to
retry transitions. For affected UI, exercise accessibility labels, focus and
Dynamic Type on the actual target. Restorable navigation or persisted user input
needs a restoration test. In-memory State alone is not durable storage.
