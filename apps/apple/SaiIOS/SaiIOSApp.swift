import SwiftUI
import SaiDesignLanguage
import SaiFoundation
import SaiAPI

@main
struct SaiIOSApp: App {
    var body: some Scene {
        WindowGroup {
            SaiCanvas { SaiText("Sai") }
                .task { await ping() }
        }
    }

    private func ping() async {
        guard let cfg = try? SaiConfiguration.load() else { return }
        let client = SaiHTTPClient(configuration: cfg)
        _ = try? await client.health()
        _ = try? await client.ready()
    }
}
