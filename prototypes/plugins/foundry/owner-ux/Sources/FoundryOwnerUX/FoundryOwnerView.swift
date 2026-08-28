import SaiDesignLanguage
import SwiftUI

public struct FoundryOwnerView: View {
    @ObservedObject private var model: FoundryOwnerModel

    public init(model: FoundryOwnerModel) {
        self.model = model
    }

    public var body: some View {
        SaiCanvas {
            SaiText("Foundry Owner UX")
            SaiText("Dry-run first. Production promotion requires an independent PR and cannot push to main.")
            SaiText("Source HEAD: \(model.prototypeHead)")
            SaiText("Graph hash: \(model.graphHash)")
            SaiText("Harness telemetry: unavailable (display-only; not policy authority)")
            if model.manifestIntegrate {
                SaiText("Integrate into Sai").onTapGesture { model.requestPlan(.integrate) }
            }
            if model.manifestSpinOff {
                SaiText("Spin Off as App").onTapGesture { model.requestPlan(.spinOff) }
            }
            if model.manifestArchive {
                SaiText("Delete / Archive").onTapGesture { model.requestPlan(.archive) }
            }
            if let errorMessage = model.errorMessage {
                SaiText("Blocked: \(errorMessage)")
            }
            switch model.state {
            case .idle:
                SaiText("Select an action to preview the graduation plan.")
            case .planReady(let plan):
                SaiText("Plan preview for \(plan.action.rawValue)")
                SaiText("Plan hash: \(plan.planHash)")
                ForEach(plan.steps.indices, id: \.self) { index in
                    let step = plan.steps[index]
                    SaiText("\(step.label): \(step.disposition.rawValue) — \(step.detail)")
                }
                SaiText("Confirm execution").onTapGesture { model.confirmExecution() }
                SaiText("Cancel").onTapGesture { model.cancel() }
            case .completed(let execution):
                SaiText("Completed: \(execution.message)")
            case .cancelled:
                SaiText("Cancelled. No effectful graduation was performed.")
            }
        }
    }
}
