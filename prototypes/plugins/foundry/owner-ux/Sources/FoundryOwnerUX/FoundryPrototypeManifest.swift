import Foundation

public struct FoundryPrototypeManifest: Codable, Equatable, Sendable {
    public struct GraduationFlags: Codable, Equatable, Sendable {
        public let integrate: Bool
        public let spinOff: Bool
        public let archive: Bool
    }

    public let id: String
    public let graduation: GraduationFlags

    public static func decode(from data: Data) throws -> FoundryPrototypeManifest {
        do {
            return try JSONDecoder().decode(FoundryPrototypeManifest.self, from: data)
        } catch {
            throw FoundryPlanError.manifestDecodeFailed
        }
    }

    public static func validateCanonicalPath(_ path: String) throws {
        let normalized = path.split(separator: "/").map(String.init).joined(separator: "/")
        guard !normalized.contains(".."), !normalized.hasPrefix("/") else {
            throw FoundryPlanError.invalidPrototypePath(path)
        }
        let parts = normalized.split(separator: "/")
        guard parts.count >= 3, parts[0] == "prototypes", parts[1] == "plugins", !parts[2].isEmpty else {
            throw FoundryPlanError.invalidPrototypePath(path)
        }
    }

    public static func load(prototypePath: String, repoRoot: String) throws -> FoundryPrototypeManifest {
        try validateCanonicalPath(prototypePath)
        let manifestURL = URL(fileURLWithPath: repoRoot)
            .appendingPathComponent(prototypePath)
            .appendingPathComponent("prototype.manifest.json")
        guard FileManager.default.fileExists(atPath: manifestURL.path) else {
            throw FoundryPlanError.manifestMissing(prototypePath)
        }
        let data = try Data(contentsOf: manifestURL)
        return try decode(from: data)
    }
}
