# F4 baseline proof

The planted boundary defect is reproduced on both installed applications.
The existing common tests pass on both targets, establishing the gap the live
worker must close with a new regression test.

| Check | Below 9,999 | Exact 10,000 | Above 10,001 |
| --- | --- | --- | --- |
| Android installed UI | 0, pass | 0, expected failure | 1,000, pass |
| iOS installed UI | 0, pass | 0, expected failure | 1,000, pass |

The baseline common tests cover below, above, and negative input: three pass,
zero skipped on Android and the allocated iOS simulator. The exact-boundary
common test is deliberately absent until the live worker adds it.

The iOS XCTest ran one method containing all three cases and reported exactly
one assertion failure: expected `Discount: 1000 cents`, observed `Discount: 0 cents`
for input 10,000. All three screenshot attachments are retained. Android's
wait ended with a UI-dump deadline message; the retained XML and screenshot
independently confirm input 10,000 and rendered zero. This is an expected
product mismatch, not a passing runtime check.

The clean disposable baseline is commit
`ccbbae970ac93b818e269215e883050c940fab87`. Separate implementation and review
checkouts start at that commit. The source fixture in hstack remains planted.

Raw evidence root:
`/var/folders/yd/86fjng8s4hbfhcz7_0yqcl9w0000gn/T/hstack-gate-f4-krthktsg`.
Key paths: `baseline-build/test-results/`, `baseline-android-ui/`,
`baseline-android-observations.json`, `baseline-ios-summary.json`,
`baseline-ios.log`, `baseline-ios.xcresult`, and `baseline-ios-attachments/`.

Android APK SHA-256:
`fd688577c615c3dfaf8866bd060b288acd45a45632f4a5e492b7e7dbe830e398`.
Android: emulator-5554, Medium_Phone_API_36.1. iOS: owned simulator
`6FB28FD2-CB6B-45EB-9B5B-FADB2BAB20C4`, iPhone 17, runtime 26.4.1.

Fixture setup corrected AndroidX enablement and the simulator architecture
profile before these tests. The host minimum is iOS 18.5 to match the linked
Compose ICU object. AGP 8.11 reports non-fatal Kotlin 2.4.10 metadata warnings;
this proof covers debug artifacts on the recorded local toolchain.
