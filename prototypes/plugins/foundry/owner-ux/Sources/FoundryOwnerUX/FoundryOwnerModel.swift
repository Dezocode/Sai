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
    @Published public private(set) var errorMessage: String?

    public let prototypePath: String
    public let prototypeID: String
    public let manifestIntegrate: Bool
    public let manifestSpinOff: Bool
    public let manifestArchive: Bool
    public let prototypeHead: String

    private let engine: FoundryGraduationEngine

    public init(
        prototypePath: String,
        prototypeID: String,
        head: String,
        manifestIntegrate: Bool,
        manifestSpinOff: Bool,
        manifestArchive: Bool,
        engine: FoundryGraduationEngine
    ) {
        self.prototypePath = prototypePath
        self.prototypeID = prototypeID
        self.prototypeHead = head
        self.manifestIntegrate = manifestIntegrate
        self.manifestSpinOff = manifestSpinOff
        self.manifestArchive = manifestArchive
        self.engine = engine
    }

    public convenience init(
        prototypePath: String,
        head: String,
        repoRoot: String? = nil,
        engine: FoundryGraduationEngine? = nil
    ) throws {
        let root = repoRoot ?? FoundryEngineBridge.discoverRepoRoot()
        let manifest = try FoundryPrototypeManifest.load(prototypePath: prototypePath, repoRoot: root)
        let resolvedEngine = engine ?? FoundryEngineBridge(repoRoot: root, prototypePath: prototypePath)
        self.init(
            prototypePath: prototypePath,
            prototypeID: manifest.id,
            head: head,
            manifestIntegrate: manifest.graduation.integrate,
            manifestSpinOff: manifest.graduation.spinOff,
            manifestArchive: manifest.graduation.archive,
            engine: resolvedEngine
        )
    }

    public var graphHash: String {
        FoundryPlanTemplate.graphHash(head: FoundryPlanTemplate.normalizedHead(prototypeHead))
    }

    public func requestPlan(_ action: FoundryOwnerAction) {
        guard supports(action) else {
            errorMessage = "Manifest does not declare \(action.rawValue)."
            return
        }
        errorMessage = nil
        do {
            let plan = try dryRun(action)
            state = .planReady(plan)
            lastExecution = FoundryExecution(
                action: action,
                phase: .dryRun,
                head: prototypeHead,
                message: "Dry-run only; confirm to execute."
            )
        } catch {
            errorMessage = error.localizedDescription
            state = .idle
        }
    }

    public func confirmExecution() {
        guard case .planReady(let plan) = state else { return }
        guard plan.head == prototypeHead else {
            errorMessage = FoundryPlanError.staleHead(expected: plan.head, actual: prototypeHead).localizedDescription
            state = .idle
            return
        }
        errorMessage = nil
        do {
            let execution = try execute(plan)
            lastExecution = execution
            if execution.phase == .completed {
                state = .completed(execution)
            } else {
                errorMessage = execution.message
                state = .idle
            }
        } catch {
            errorMessage = error.localizedDescription
            lastExecution = FoundryExecution(
                action: plan.action,
                phase: .failed,
                head: prototypeHead,
                message: error.localizedDescription
            )
            state = .idle
        }
    }

    public func cancel() {
        if case .planReady(let plan) = state {
            lastExecution = FoundryExecution(
                action: plan.action,
                phase: .cancelled,
                head: prototypeHead,
                message: "Owner cancelled before execution."
            )
        }
        errorMessage = nil
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
        case .integrate: return try engine.dryRunIntegrate(head: prototypeHead)
        case .spinOff: return try engine.dryRunSpinOff(head: prototypeHead)
        case .archive: return try engine.dryRunArchive(head: prototypeHead)
        }
    }

    private func execute(_ plan: FoundryPlan) throws -> FoundryExecution {
        switch plan.action {
        case .integrate:
            return try engine.executeIntegrate(head: plan.head, planHash: plan.planHash)
        case .spinOff:
            return try engine.executeSpinOff(head: plan.head, planHash: plan.planHash)
        case .archive:
            return try engine.executeArchive(head: plan.head, planHash: plan.planHash)
        }
    }
}
