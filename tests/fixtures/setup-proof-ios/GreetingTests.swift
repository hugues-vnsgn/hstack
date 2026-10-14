import XCTest

final class GreetingTests: XCTestCase {
    func testGreeting() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.staticTexts["Ready for greeting"].waitForExistence(timeout: 15))
        app.buttons["Greet"].tap()
        XCTAssertTrue(app.staticTexts["Hello, Codex!"].waitForExistence(timeout: 5))
        let screenshot = XCTAttachment(screenshot: app.screenshot())
        screenshot.name = "greeting"
        screenshot.lifetime = .keepAlways
        add(screenshot)
    }
}
