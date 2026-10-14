import UIKit

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {}

@objc(SceneDelegate)
final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    private let label = UILabel()

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let scene = scene as? UIWindowScene else { return }
        label.text = "Ready for greeting"
        label.textAlignment = .center
        label.font = .systemFont(ofSize: 30)
        label.backgroundColor = .white
        label.textColor = .black
        let controller = UIViewController()
        let button = UIButton(type: .system)
        button.setTitle("Greet", for: .normal)
        button.addTarget(self, action: #selector(greet), for: .touchUpInside)
        let stack = UIStackView(arrangedSubviews: [label, button])
        stack.axis = .vertical
        stack.spacing = 24
        stack.translatesAutoresizingMaskIntoConstraints = false
        controller.view.backgroundColor = .white
        controller.view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.centerXAnchor.constraint(equalTo: controller.view.centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: controller.view.centerYAnchor)
        ])
        window = UIWindow(windowScene: scene)
        window?.rootViewController = controller
        window?.makeKeyAndVisible()
        save("ready", as: "ready.txt")
    }

    @objc private func greet() {
        label.text = "Hello, Codex!"
        save("Hello, Codex!", as: "greeting.txt")
    }

    private func save(_ text: String, as name: String) {
        let file = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent(name)
        try? text.write(to: file, atomically: true, encoding: .utf8)
    }
}
