import XCTest
@testable import FoundryOwnerUX

@MainActor
final class FoundryOwnerUXTests: XCTestCase {
    func testDryRunDoesNotCompleteGraduation() async {
        let model = FoundryOwnerModel(head: "abcdef1234567890abcdef1234567890", engine: FoundryGraduationEngineStub())
        model.requestPlan(.integrate)
        guard case .planReady(let plan) = model.state else {
            XCTFail("expected planReady after dry run")
            return
        }
        XCTAssertEqual(plan.action, .integrate)
        XCTAssertEqual(model.lastExecution?.phase, .dryRun)
        XCTAssertNil(model.errorMessage)
    }

    func testConfirmationExecutesAfterDryRun() async {
        let model = FoundryOwnerModel(head: "abcdef1234567890abcdef1234567890", engine: FoundryGraduationEngineStub())
        model.requestPlan(.spinOff)
        model.confirmExecution()
        guard case .completed(let execution) = model.state else {
            XCTFail("expected completed after confirmation")
            return
        }
        XCTAssertEqual(execution.action, .spinOff)
        XCTAssertEqual(execution.phase, .completed)
        XCTAssertTrue(execution.message.contains("independent PR"))
    }

    func testCancelBeforeExecution() async {
        let model = FoundryOwnerModel(head: "abcdef1234567890abcdef1234567890", engine: FoundryGraduationEngineStub())
        model.requestPlan(.archive)
        model.cancel()
        XCTAssertEqual(model.state, .cancelled)
        XCTAssertEqual(model.lastExecution?.phase, .cancelled)
    }

    func testUnsupportedManifestSurfacesError() async {
        let model = FoundryOwnerModel(
            head: "abcdef1234567890abcdef1234567890",
            manifestIntegrate: false,
            manifestSpinOff: false,
            manifestArchive: false,
            engine: FoundryGraduationEngineStub()
        )
        model.requestPlan(.integrate)
        XCTAssertNotNil(model.errorMessage)
        XCTAssertEqual(model.state, .idle)
    }

    func testStalePlanHashFailsClosed() async {
        let engine = StalePlanEngine()
        let model = FoundryOwnerModel(head: "abcdef1234567890abcdef1234567890", engine: engine)
        model.requestPlan(.integrate)
        model.confirmExecution()
        XCTAssertEqual(model.lastExecution?.phase, .failed)
        XCTAssertEqual(model.errorMessage, "stale plan hash")
    }
}

private struct StalePlanEngine: FoundryGraduationEngine {
    func dryRunIntegrate(head: String) throws -> FoundryPlan {
        FoundryPlan(action: .integrate, head: head, planHash: "preview-hash", steps: [])
    }

    func executeIntegrate(head: String, planHash: String) throws -> FoundryExecution {
        FoundryExecution(action: .integrate, phase: .failed, head: head, message: "stale plan hash")
    }

    func dryRunSpinOff(head: String) throws -> FoundryPlan { try dryRunIntegrate(head: head) }
    func executeSpinOff(head: String, planHash: String) throws -> FoundryExecution { try executeIntegrate(head: head, planHash: planHash) }
    func dryRunArchive(head: String) throws -> FoundryPlan { try dryRunIntegrate(head: head) }
    func executeArchive(head: String, planHash: String) throws -> FoundryExecution { try executeIntegrate(head: head, planHash: planHash) }
}
