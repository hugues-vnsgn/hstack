import XCTest

final class AppUITests: XCTestCase {
    private let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = true
    }

    func testDiscountThresholdCases() throws {
        for testCase in [
            (subtotal: "9999", expected: "Discount: 0 cents"),
            // The fixture intentionally starts with `> 10000` in common code.
            // This assertion must fail until the live worker changes it to `>=`.
            (subtotal: "10000", expected: "Discount: 1000 cents"),
            (subtotal: "10001", expected: "Discount: 1000 cents"),
        ] {
            runCase(subtotal: testCase.subtotal, expected: testCase.expected)
        }
    }

    private func runCase(subtotal: String, expected: String) {
        app.terminate()
        app.launch()

        let subtotalInput = control(tag: "subtotal_input")
        XCTAssertTrue(
            subtotalInput.waitForExistence(timeout: 10),
            "subtotal_input did not become available"
        )
        replaceText(in: subtotalInput, with: subtotal)

        let calculateButton = control(tag: "calculate_button")
        XCTAssertTrue(
            calculateButton.waitForExistence(timeout: 5),
            "calculate_button did not become available"
        )
        calculateButton.tap()

        let discountResult = control(tag: "discount_result")
        let resultExists = discountResult.waitForExistence(timeout: 5)
        attachScreenshot(named: "subtotal-\(subtotal)")
        XCTAssertTrue(resultExists, "discount_result did not become available")

        let observed = discountResult.label.isEmpty
            ? (discountResult.value as? String ?? "")
            : discountResult.label
        XCTAssertEqual(observed, expected, "subtotal \(subtotal) produced the wrong discount")
    }

    private func control(tag: String) -> XCUIElement {
        app.descendants(matching: .any).matching(identifier: tag).firstMatch
    }

    private func replaceText(in field: XCUIElement, with text: String) {
        field.tap()
        let currentValue = field.value as? String ?? ""
        let placeholder = field.placeholderValue ?? ""
        let textToDelete = currentValue == placeholder ? "" : currentValue
        if !textToDelete.isEmpty {
            field.typeText(String(repeating: XCUIKeyboardKey.delete.rawValue, count: textToDelete.count))
        }
        field.typeText(text)
    }

    private func attachScreenshot(named name: String) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
