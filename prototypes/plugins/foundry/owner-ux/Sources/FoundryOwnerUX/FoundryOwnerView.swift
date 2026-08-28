import Foundation

public struct FoundryOwnerView {
    public enum LineKind: Equatable, Sendable {
        case heading
        case body
        case action(FoundryOwnerAction)
        case confirm
        case cancel
        case error
        case planStep
    }

    public struct Line: Equatable, Sendable {
        public let kind: LineKind
        public let text: String

        public init(kind: LineKind, text: String) {
            self.kind = kind
            self.text = text
        }
    }

    private let model: FoundryOwnerModel

    public init(model: FoundryOwnerModel) {
        self.model = model
    }

    public var lines: [Line] {
        var result: [Line] = [
            .init(kind: .heading, text: "Foundry Owner UX"),
            .init(kind: .body, text: "Dry-run first. Production promotion requires an independent PR and cannot push to main."),
            .init(kind: .body, text: "Prototype: \(model.prototypeID) at \(model.prototypePath)"),
            .init(kind: .body, text: "Source HEAD: \(model.prototypeHead)"),
            .init(kind: .body, text: "Graph hash: \(model.graphHash)"),
            .init(kind: .body, text: "Schema version: \(FoundryPlanTemplate.schemaVersion)"),
            .init(kind: .body, text: "Harness telemetry: unavailable (display-only; not policy authority)"),
        ]
        if model.manifestIntegrate {
            result.append(.init(kind: .action(.integrate), text: "Integrate into Sai"))
        }
        if model.manifestSpinOff {
            result.append(.init(kind: .action(.spinOff), text: "Spin Off as App"))
        }
        if model.manifestArchive {
            result.append(.init(kind: .action(.archive), text: "Delete / Archive"))
        }
        if let errorMessage = model.errorMessage {
            result.append(.init(kind: .error, text: "Blocked: \(errorMessage)"))
        }
        switch model.state {
        case .idle:
            result.append(.init(kind: .body, text: "Select an action to preview the graduation plan."))
        case .planReady(let plan):
            result.append(.init(kind: .body, text: "Plan preview for \(plan.action.rawValue)"))
            result.append(.init(kind: .body, text: "Plan hash: \(plan.planHash)"))
            for step in plan.steps {
                result.append(.init(kind: .planStep, text: "\(step.label): \(step.disposition.rawValue) — \(step.detail)"))
            }
            result.append(.init(kind: .confirm, text: "Confirm execution"))
            result.append(.init(kind: .cancel, text: "Cancel"))
        case .completed(let execution):
            result.append(.init(kind: .body, text: "Completed: \(execution.message)"))
        case .cancelled:
            result.append(.init(kind: .body, text: "Cancelled. No effectful graduation was performed."))
        }
        return result
    }

    public func perform(_ kind: LineKind) {
        switch kind {
        case .action(let action):
            model.requestPlan(action)
        case .confirm:
            model.confirmExecution()
        case .cancel:
            model.cancel()
        default:
            break
        }
    }
}
