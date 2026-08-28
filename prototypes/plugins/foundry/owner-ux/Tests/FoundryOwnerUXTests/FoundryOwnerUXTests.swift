import XCTest
@testable import FoundryOwnerUX

@MainActor
final class FoundryOwnerUXTests: XCTestCase {
    private let head = "abcdef1234567890abcdef1234567890"
    private let path = FoundryHarnessFixture.defaultOwnerUXPath

    func testDryRunDoesNotCompleteGraduation() async {
        let model = FoundryOwnerModel(head: head, engine: FoundryGraduationEngineStub())
        model.requestPlan(.integrate)
        guard case .planReady(let plan) = model.state else {
            XCTFail("expected planReady after dry run")
            return
        }
        XCTAssertEqual(plan.action, .integrate)
        XCTAssertEqual(plan.prototypePath, path)
        XCTAssertEqual(model.lastExecution?.phase, .dryRun)
        XCTAssertNil(model.errorMessage)
    }

    func testConfirmationExecutesAfterDryRun() async {
        let model = FoundryOwnerModel(head: head, engine: FoundryGraduationEngineStub())
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
        let model = FoundryOwnerModel(head: head, engine: FoundryGraduationEngineStub())
        model.requestPlan(.archive)
        model.cancel()
        XCTAssertEqual(model.state, .cancelled)
        XCTAssertEqual(model.lastExecution?.phase, .cancelled)
    }

    func testUnsupportedManifestSurfacesError() async {
        let model = FoundryOwnerModel(
            head: head,
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
        let model = FoundryOwnerModel(head: head, engine: engine)
        model.requestPlan(.integrate)
        model.confirmExecution()
        XCTAssertEqual(model.lastExecution?.phase, .failed)
        XCTAssertEqual(model.errorMessage, "stale plan hash")
    }

    func testManifestDecode() throws {
        let data = Data("{\"id\":\"author\",\"graduation\":{\"integrate\":true,\"spinOff\":false,\"archive\":true}}".utf8)
        let manifest = try FoundryPrototypeManifest.decode(from: data)
        XCTAssertEqual(manifest.id, "author")
        XCTAssertFalse(manifest.graduation.spinOff)
        XCTAssertTrue(manifest.graduation.archive)
    }

    func testInvalidPrototypePathFailsClosed() {
        XCTAssertThrowsError(try FoundryPrototypeManifest.validateCanonicalPath("prototypes/plugins-evil/x"))
    }

    func testPlanTemplateRejectsInvalidPath() {
        XCTAssertThrowsError(
            try FoundryPlanTemplate.uiPlan(
                action: .integrate,
                prototypePath: "prototypes/plugins",
                head: head,
                planID: "test"
            )
        )
    }

    func testIntegratePreviewIncludesProductionAuthorityStep() throws {
        let plan = try FoundryPlanTemplate.uiPlan(
            action: .integrate,
            prototypePath: path,
            head: head,
            planID: "test"
        )
        XCTAssertTrue(plan.steps.contains { $0.label == "Production authority" })
    }

    func testHarnessFixtureLoadsManifestFromRepo() throws {
        let root = FoundryEngineBridge.discoverRepoRoot()
        let goMod = (root as NSString).appendingPathComponent("go.mod")
        guard FileManager.default.fileExists(atPath: goMod) else {
            throw XCTSkip("repo root not available in package-only test context")
        }
        let model = try FoundryHarnessFixture.makeOwnerModel(
            prototypePath: path,
            head: head,
            repoRoot: root
        )
        XCTAssertEqual(model.prototypeID, "foundry-owner-ux")
        XCTAssertTrue(model.manifestIntegrate)
        XCTAssertTrue(model.manifestSpinOff)
        XCTAssertTrue(model.manifestArchive)
    }
}

private struct StalePlanEngine: FoundryGraduationEngine {
    func dryRunIntegrate(head: String) throws -> FoundryPlan {
        FoundryPlan(
            action: .integrate,
            head: head,
            planHash: "preview-hash",
            prototypePath: FoundryHarnessFixture.defaultOwnerUXPath,
            steps: []
        )
    }

    func executeIntegrate(head: String, planHash: String) throws -> FoundryExecution {
        FoundryExecution(action: .integrate, phase: .failed, head: head, message: "stale plan hash")
    }

    func dryRunSpinOff(head: String) throws -> FoundryPlan { try dryRunIntegrate(head: head) }
    func executeSpinOff(head: String, planHash: String) throws -> FoundryExecution { try executeIntegrate(head: head, planHash: planHash) }
    func dryRunArchive(head: String) throws -> FoundryPlan { try dryRunIntegrate(head: head) }
    func executeArchive(head: String, planHash: String) throws -> FoundryExecution { try executeIntegrate(head: head, planHash: planHash) }
}
