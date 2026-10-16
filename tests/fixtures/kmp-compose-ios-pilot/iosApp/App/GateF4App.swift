import SwiftUI
import UIKit
import SharedUI

@main
struct GateF4App: App {
    var body: some Scene {
        WindowGroup {
            CalculatorScreen()
        }
    }
}

/// Keeps the application shell native while Compose owns the entire calculator.
struct CalculatorScreen: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
