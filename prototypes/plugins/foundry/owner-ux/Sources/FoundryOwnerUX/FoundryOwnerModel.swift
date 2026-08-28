import Foundation

@MainActor
public final class FoundryOwnerModel: ObservableObject {
    public enum State: Equatable, Sendable {
        case idle
        case planReady(FoundryPlan)
        case completed(FoundryExecution)
        case cancelled
    }

    @Published public private(set) var state: State = .idle
    @Published public private(set) var lastExecution: FoundryExecution?

    public let manifestIntegrate: Bool
    public let manifestSpinOff: Bool
    public let manifestArchive: Bool

    private let engine: FoundryGraduationEngine
    private let head: String

    public init(
        head: String,
        manifestIntegrate: Bool = true,
        manifestSpinOff: Bool = true,
        manifestArchive: Bool = true,
        engine: FoundryGraduationEngine = FoundryEngineBridge()
    ) {
        self.head = head
        self.manifestIntegrate = manifestIntegrate
        self.manifestSpinOff = manifestSpinOff
        self.manifestArchive = manifestArchive
        self.engine = engine
    }

    public func requestPlan(_ action: FoundryOwnerAction) {
        guard supports(action) else { return }
        do {
            let plan = try dryRun(action)
            state = .planReady(plan)
            lastExecution = FoundryExecution(action: action, phase: .dryRun, head: head, message: "Dry-run only; confirm to execute.")
        } catch {
            state = .idle
        }
    }

    public func confirmExecution() {
        guard case .planReady(let plan) = state else { return }
        do {
            let execution = try execute(plan)
            lastExecution = execution
            state = execution.phase == .completed ? .completed(execution) : .idle
        } catch {
            lastExecution = FoundryExecution(action: plan.action, phase: .failed, head: head, message: "execution refused")
            state = .idle
        }
    }

    public func cancel() {
        if case .planReady(let plan) = state {
            lastExecution = FoundryExecution(action: plan.action, phase: .cancelled, head: head, message: "Owner cancelled before execution.")
        }
        state = .cancelled
    }

    private func supports(_ action: FoundryOwnerAction) -> Bool {
        switch action {
        case .integrate: return manifestIntegrate
        case .spinOff: return manifestSpinOff
        case .archive: return manifestArchive
        }
    }

    private func dryRun(_ action: FoundryOwnerAction) throws -> FoundryPlan {
        switch action {
        case .integrate: return try engine.dryRunIntegrate(head: head)
        case .spinOff: return try engine.dryRunSpinOff(head: head)
        case .archive: return try engine.dryRunArchive(head: head)
        }
    }

    private func execute(_ plan: FoundryPlan) throws -> FoundryExecution {
        switch plan.action {
        case .integrate: return try engine.executeIntegrate(head: plan.head, planHash: plan.planHash)
        case .spinOff: return try engine.executeSpinOff(head: plan.head, planHash: plan.planHash)
        case .archive: return try engine.executeArchive(head: plan.head, planHash: plan.planHash)
        }
    }
}
