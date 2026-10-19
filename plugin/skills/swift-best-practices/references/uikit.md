# UIKit and native wrappers

Match controller, scene and delegate ownership to the consumer's architecture.
Pair observer registration and callback subscriptions with teardown. Test
presentation, dismissal and re-entry for duplicate work and retained controllers.
Use weak delegates when the API's ownership contract calls for them. Trace
closures retained by a controller or service and break unintended cycles.
See [controller responsibilities](https://developer.apple.com/documentation/uikit/uiviewcontroller)
and [scene lifecycle](https://developer.apple.com/documentation/uikit/managing-your-app-s-life-cycle).

UI changes run on the main thread. Inspect callback delivery instead of assuming
that a completion arrives there. Swift actor annotations and SDK imports vary
with the configured toolchain. Confirm isolation at each legacy callback entry.
See [UIView threading](https://developer.apple.com/documentation/uikit/uiview).

For UIViewRepresentable or UIViewControllerRepresentable, separate creation,
state updates and dismantling. Keep coordinator callbacks current, prevent
update feedback loops, and release observers and delegates on removal.
Preserve controller containment. Verify keyboard, focus, gestures, navigation,
accessibility and text scaling across the wrapper after updates and recreation.
Check method availability against the deployment target. See
[UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
and [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable).
