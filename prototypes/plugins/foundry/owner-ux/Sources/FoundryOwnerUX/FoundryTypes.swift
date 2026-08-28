import Foundation

public enum FoundryOwnerAction: String, CaseIterable, Sendable {
    case integrate
    case spinOff
    case archive
}

public enum FoundryDisposition: String, CaseIterable, Sendable {
    case reuse = "REUSE"
    case promote = "PROMOTE"
    case export = "EXPORT"
    case remote = "REMOTE"
    case promoteShared = "PROMOTE_SHARED"
    case drop = "DROP"
}

public struct FoundryPlanStep: Equatable, Sendable {
    public let label: String
    public let disposition: FoundryDisposition
    public let detail: String

    public init(label: String, disposition: FoundryDisposition, detail: String) {
        self.label = label
        self.disposition = disposition
        self.detail = detail
    }
}

public struct FoundryPlan: Equatable, Sendable {
    public let action: FoundryOwnerAction
    public let head: String
    public let planHash: String
    public let steps: [FoundryPlanStep]

    public init(action: FoundryOwnerAction, head: String, planHash: String, steps: [FoundryPlanStep]) {
        self.action = action
        self.head = head
        self.planHash = planHash
        self.steps = steps
    }
}

public struct FoundryExecution: Equatable, Sendable {
    public enum Phase: String, Sendable {
        case dryRun
        case confirmed
        case completed
        case cancelled
        case failed
    }

    public let action: FoundryOwnerAction
    public let phase: Phase
    public let head: String
    public let message: String

    public init(action: FoundryOwnerAction, phase: Phase, head: String, message: String) {
        self.action = action
        self.phase = phase
        self.head = head
        self.message = message
    }
}
