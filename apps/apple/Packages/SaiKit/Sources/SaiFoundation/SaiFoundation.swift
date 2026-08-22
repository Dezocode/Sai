import Foundation

public struct SaiConfiguration: Sendable {
    public static let developmentAPIBaseURL = "http://127.0.0.1:8080"
    public let environment: String
    public let apiBaseURL: URL

    public static func load(
        env: [String: String] = ProcessInfo.processInfo.environment,
        bundle: Bundle = .main
    ) throws -> SaiConfiguration {
        let e = env["SAI_ENVIRONMENT"]
            ?? (bundle.object(forInfoDictionaryKey: "SAI_ENVIRONMENT") as? String)
            ?? "development"
        let injected = env["SAI_API_BASE_URL"]
            ?? (bundle.object(forInfoDictionaryKey: "SAI_API_BASE_URL") as? String)
        let raw: String
        if e == "development" {
            raw = (injected?.isEmpty == false) ? injected! : developmentAPIBaseURL
        } else {
            guard let injected, !injected.isEmpty else { throw SaiConfigurationError.missingURL }
            raw = injected
        }
        guard let url = URL(string: raw), let host = url.host, !host.isEmpty else { throw SaiConfigurationError.missingURL }
        let scheme = url.scheme?.lowercased()
        guard scheme == "https" || (scheme == "http" && e == "development") else { throw SaiConfigurationError.missingURL }
        return SaiConfiguration(environment: e, apiBaseURL: url)
    }
}

public enum SaiConfigurationError: Error { case missingURL }
