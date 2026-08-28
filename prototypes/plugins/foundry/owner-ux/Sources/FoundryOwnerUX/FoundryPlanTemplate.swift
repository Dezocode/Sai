import CryptoKit
import Foundation

/// Builds graduation-engine plan JSON (#164 schema) and maps dispositions to UI `FoundryPlan`.
public enum FoundryPlanTemplate {
    public static let prototypePath = "prototypes/plugins/foundry/owner-ux"
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

    public static func enginePlanJSON(
        action: FoundryOwnerAction,
        head: String,
        base: String? = nil,
        ownerConfirmed: Bool
    ) throws -> Data {
        let protoHead = normalizedHead(head)
        let mergeBase = normalizedHead(base ?? protoHead)
        let operation = engineOperation(action: action, ownerConfirmed: ownerConfirmed)
        let plan = EnginePlan(
            schema_version: schemaVersion,
            repo: repo,
            base: mergeBase,
            prototype_head: protoHead,
            graph_hash: graphHash(head: protoHead),
            operations: [operation],
            dispositions: defaultDispositions()
        )
        return try JSONEncoder().encode(plan)
    }

    public static func uiPlan(action: FoundryOwnerAction, head: String, planID: String) -> FoundryPlan {
        FoundryPlan(
            action: action,
            head: head,
            planHash: planID,
            steps: defaultDispositions().map { node in
                let disposition = FoundryDisposition(rawValue: node.disposition) ?? .reuse
                let label = node.path.split(separator: "/").last.map(String.init) ?? node.path
                return FoundryPlanStep(
                    label: label,
                    disposition: disposition,
                    detail: dispositionDetail(disposition, path: node.path)
                )
            }
        )
    }

    private static func engineOperation(action: FoundryOwnerAction, ownerConfirmed: Bool) -> EnginePlan.Operation {
        switch action {
        case .integrate:
            return .init(
                kind: "integrate",
                idempotency_key: "owner-ux-integrate",
                prototype_path: prototypePath,
                target_branch: "foundry/candidate",
                spinoff_name: nil,
                owner_confirmed: ownerConfirmed
            )
        case .spinOff:
            return .init(
                kind: "spinoff",
                idempotency_key: "owner-ux-spinoff",
                prototype_path: prototypePath,
                target_branch: nil,
                spinoff_name: "foundry-owner-ux-app",
                owner_confirmed: ownerConfirmed
            )
        case .archive:
            return .init(
                kind: "delete-archive",
                idempotency_key: "owner-ux-archive",
                prototype_path: prototypePath,
                target_branch: nil,
                spinoff_name: nil,
                owner_confirmed: ownerConfirmed
            )
        }
    }

    private static func defaultDispositions() -> [EnginePlan.NodeDisposition] {
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
