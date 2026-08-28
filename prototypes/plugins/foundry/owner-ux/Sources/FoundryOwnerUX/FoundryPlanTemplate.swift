import CryptoKit
import Foundation

public enum FoundryPlanTemplate {
    public static let schemaVersion = 1
    public static let repo = "Dezocode/Sai"

    private struct EnginePlan: Encodable {
        struct Operation: Encodable {
            let kind: String
            let idempotency_key: String
            let prototype_path: String?
            let target_branch: String?
            let spinoff_name: String?
            let owner_confirmed: Bool
        }

        struct NodeDisposition: Encodable {
            let path: String
            let disposition: String
        }

        var plan_id: String = ""
        let schema_version: Int
        let repo: String
        let base: String
        let prototype_head: String
        let graph_hash: String
        let operations: [Operation]
        let dispositions: [NodeDisposition]
    }

    public static func stubPlanID(head: String, action: FoundryOwnerAction) -> String {
        "\(action.rawValue)-\(head.prefix(8))"
    }

    public static func graphHash(head: String) -> String {
        let digest = SHA256.hash(data: Data(head.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    public static func normalizedHead(_ head: String) -> String {
        let trimmed = head.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count >= 40 { return String(trimmed.prefix(40)) }
        return trimmed.padding(toLength: 40, withPad: "0", startingAt: 0)
    }

    public static func pluginSlug(for prototypePath: String) -> String {
        prototypePath.split(separator: "/").last.map(String.init) ?? "prototype"
    }

    public static func enginePlanJSON(
        action: FoundryOwnerAction,
        prototypePath: String,
        head: String,
        base: String? = nil,
        ownerConfirmed: Bool
    ) throws -> Data {
        try FoundryPrototypeManifest.validateCanonicalPath(prototypePath)
        let protoHead = normalizedHead(head)
        let mergeBase = normalizedHead(base ?? protoHead)
        let operation = engineOperation(action: action, prototypePath: prototypePath, ownerConfirmed: ownerConfirmed)
        let plan = EnginePlan(
            schema_version: schemaVersion,
            repo: repo,
            base: mergeBase,
            prototype_head: protoHead,
            graph_hash: graphHash(head: protoHead),
            operations: [operation],
            dispositions: defaultDispositions(prototypePath: prototypePath)
        )
        return try JSONEncoder().encode(plan)
    }

    public static func uiPlan(
        action: FoundryOwnerAction,
        prototypePath: String,
        head: String,
        planID: String
    ) throws -> FoundryPlan {
        try FoundryPrototypeManifest.validateCanonicalPath(prototypePath)
        var steps = actionPreview(action: action, prototypePath: prototypePath)
        for node in defaultDispositions(prototypePath: prototypePath) {
            guard let disposition = FoundryDisposition(rawValue: node.disposition) else {
                throw FoundryPlanError.unknownDisposition(node.disposition)
            }
            let label = node.path.split(separator: "/").last.map(String.init) ?? node.path
            steps.append(FoundryPlanStep(label: label, disposition: disposition, detail: dispositionDetail(disposition, path: node.path)))
        }
        return FoundryPlan(action: action, head: head, planHash: planID, prototypePath: prototypePath, steps: steps)
    }

    private static func actionPreview(action: FoundryOwnerAction, prototypePath: String) -> [FoundryPlanStep] {
        switch action {
        case .integrate:
            return [
                FoundryPlanStep(
                    label: "Production authority",
                    disposition: .promote,
                    detail: "Integrate \(prototypePath) via independent production PR; cannot push main from UI."
                ),
            ]
        case .spinOff:
            return [
                FoundryPlanStep(
                    label: "Standalone tree",
                    disposition: .export,
                    detail: "Spin off \(prototypePath) with dependency closure and independent-build evidence."
                ),
            ]
        case .archive:
            return [
                FoundryPlanStep(
                    label: "Production dependency proof",
                    disposition: .drop,
                    detail: "Archive \(prototypePath) only after zero-production-dependency verification."
                ),
            ]
        }
    }

    private static func engineOperation(
        action: FoundryOwnerAction,
        prototypePath: String,
        ownerConfirmed: Bool
    ) -> EnginePlan.Operation {
        let slug = pluginSlug(for: prototypePath)
        switch action {
        case .integrate:
            return .init(
                kind: "integrate",
                idempotency_key: "\(slug)-integrate",
                prototype_path: prototypePath,
                target_branch: "foundry/candidate",
                spinoff_name: nil,
                owner_confirmed: ownerConfirmed
            )
        case .spinOff:
            return .init(
                kind: "spinoff",
                idempotency_key: "\(slug)-spinoff",
                prototype_path: prototypePath,
                target_branch: nil,
                spinoff_name: "\(slug)-app",
                owner_confirmed: ownerConfirmed
            )
        case .archive:
            return .init(
                kind: "delete-archive",
                idempotency_key: "\(slug)-archive",
                prototype_path: prototypePath,
                target_branch: nil,
                spinoff_name: nil,
                owner_confirmed: ownerConfirmed
            )
        }
    }

    private static func defaultDispositions(prototypePath: String) -> [EnginePlan.NodeDisposition] {
        [
            .init(path: "\(prototypePath)/prototype.manifest.json", disposition: FoundryDisposition.reuse.rawValue),
            .init(path: "\(prototypePath)/Sources", disposition: FoundryDisposition.promote.rawValue),
            .init(path: "\(prototypePath)/Package.swift", disposition: FoundryDisposition.reuse.rawValue),
            .init(path: ".foundry/telemetry", disposition: FoundryDisposition.remote.rawValue),
            .init(path: ".build", disposition: FoundryDisposition.drop.rawValue),
        ]
    }

    private static func dispositionDetail(_ disposition: FoundryDisposition, path: String) -> String {
        switch disposition {
        case .reuse:
            return "Reuse \(path) in the graduation candidate."
        case .promote:
            return "Promote \(path) via an independent production PR."
        case .export:
            return "Export \(path) for standalone packaging."
        case .remote:
            return "Harness telemetry for \(path) is display-only."
        case .promoteShared:
            return "Promote shared dependency at \(path)."
        case .drop:
            return "Drop ephemeral artifacts at \(path)."
        }
    }
}
