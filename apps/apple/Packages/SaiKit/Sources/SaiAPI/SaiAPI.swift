import Foundation
import SaiFoundation

public protocol SaiAPIClient: Sendable {
    func health() async throws
    func ready() async throws
}

public struct SaiHTTPClient: SaiAPIClient {
    let cfg: SaiConfiguration
    let session: URLSession
    public init(configuration: SaiConfiguration, session: URLSession = .shared) {
        cfg = configuration
        self.session = session
    }
    public func health() async throws { try await get("health") }
    public func ready() async throws { try await get("ready") }
    func get(_ path: String) async throws {
        var req = URLRequest(url: cfg.apiBaseURL.appendingPathComponent(path))
        req.httpMethod = "GET"
        let (_, resp) = try await session.data(for: req)
        guard (resp as? HTTPURLResponse)?.statusCode == 204 else { throw URLError(.badServerResponse) }
    }
}
