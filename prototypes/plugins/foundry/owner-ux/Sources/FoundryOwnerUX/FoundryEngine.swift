import Foundation

public protocol FoundryGraduationEngine: Sendable {
    func dryRunIntegrate(head: String) throws -> FoundryPlan
    func executeIntegrate(head: String, planHash: String) throws -> FoundryExecution
    func dryRunSpinOff(head: String) throws -> FoundryPlan
    func executeSpinOff(head: String, planHash: String) throws -> FoundryExecution
    func dryRunArchive(head: String) throws -> FoundryPlan
    func executeArchive(head: String, planHash: String) throws -> FoundryExecution
}

public struct FoundryGraduationEngineStub: FoundryGraduationEngine {
    public let prototypePath: String

    public init(prototypePath: String = FoundryHarnessFixture.defaultOwnerUXPath) {
        self.prototypePath = prototypePath
    }

    public func dryRunIntegrate(head: String) throws -> FoundryPlan {
        try plan(for: .integrate, head: head)
    }

    public func executeIntegrate(head: String, planHash: String) throws -> FoundryExecution {
        try execution(for: .integrate, head: head, planHash: planHash)
    }

    public func dryRunSpinOff(head: String) throws -> FoundryPlan {
        try plan(for: .spinOff, head: head)
    }

    public func executeSpinOff(head: String, planHash: String) throws -> FoundryExecution {
        try execution(for: .spinOff, head: head, planHash: planHash)
    }

    public func dryRunArchive(head: String) throws -> FoundryPlan {
        try plan(for: .archive, head: head)
    }

    public func executeArchive(head: String, planHash: String) throws -> FoundryExecution {
        try execution(for: .archive, head: head, planHash: planHash)
    }

    private func plan(for action: FoundryOwnerAction, head: String) throws -> FoundryPlan {
        try FoundryPlanTemplate.uiPlan(
            action: action,
            prototypePath: prototypePath,
            head: head,
            planID: FoundryPlanTemplate.stubPlanID(head: head, action: action)
        )
    }

    private func execution(for action: FoundryOwnerAction, head: String, planHash: String) throws -> FoundryExecution {
        let expected = FoundryPlanTemplate.stubPlanID(head: head, action: action)
        guard planHash == expected else {
            return FoundryExecution(action: action, phase: .failed, head: head, message: "stale plan hash")
        }
        return FoundryExecution(
            action: action,
            phase: .completed,
            head: head,
            message: "Graduation engine recorded execution; production promotion still requires an independent PR."
        )
    }
}
