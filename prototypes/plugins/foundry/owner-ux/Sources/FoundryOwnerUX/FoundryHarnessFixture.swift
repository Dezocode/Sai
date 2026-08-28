import Foundation

public enum FoundryHarnessFixture {
    public static let defaultOwnerUXPath = "prototypes/plugins/foundry/owner-ux"

    @MainActor
    public static func makeOwnerModel(
        prototypePath: String,
        head: String,
        repoRoot: String? = nil
    ) throws -> FoundryOwnerModel {
        try FoundryOwnerModel(prototypePath: prototypePath, head: head, repoRoot: repoRoot)
    }

    @MainActor
    public static func makeOwnerView(
        prototypePath: String,
        head: String,
        repoRoot: String? = nil
    ) throws -> FoundryOwnerView {
        FoundryOwnerView(model: try makeOwnerModel(prototypePath: prototypePath, head: head, repoRoot: repoRoot))
    }
}
