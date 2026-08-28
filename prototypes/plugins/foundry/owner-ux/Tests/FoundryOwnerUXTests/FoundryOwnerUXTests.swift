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
        XCTAssertNotEqual(model.state, .completed(FoundryExecution(action: .integrate, phase: .completed, head: plan.head, message: "")))
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
}
