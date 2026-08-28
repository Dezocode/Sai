import Foundation

/// Invokes the #164 graduation-engine CLI when present; otherwise falls back to the test stub.
public struct FoundryEngineBridge: FoundryGraduationEngine {
    private static let engineMain = "prototypes/plugins/foundry/graduation-engine/cmd/graduate/main.go"
    private static let graduatePkg = "./prototypes/plugins/foundry/graduation-engine/cmd/graduate"

    private let repoRoot: String
    private let fallback: FoundryGraduationEngineStub

    public init(repoRoot: String? = nil) {
        self.repoRoot = repoRoot ?? Self.discoverRepoRoot()
        self.fallback = FoundryGraduationEngineStub()
    }

    public func dryRunIntegrate(head: String) throws -> FoundryPlan {
        try run(action: .integrate, head: head, dryRun: true)
    }

    public func executeIntegrate(head: String, planHash: String) throws -> FoundryExecution {
        try execute(action: .integrate, head: head, planHash: planHash)
    }

    public func dryRunSpinOff(head: String) throws -> FoundryPlan {
        try run(action: .spinOff, head: head, dryRun: true)
    }

    public func executeSpinOff(head: String, planHash: String) throws -> FoundryExecution {
        try execute(action: .spinOff, head: head, planHash: planHash)
    }

    public func dryRunArchive(head: String) throws -> FoundryPlan {
        try run(action: .archive, head: head, dryRun: true)
    }

    public func executeArchive(head: String, planHash: String) throws -> FoundryExecution {
        try execute(action: .archive, head: head, planHash: planHash)
    }

    private var enginePresent: Bool {
        FileManager.default.fileExists(atPath: (repoRoot as NSString).appendingPathComponent(Self.engineMain))
    }

    private func run(action: FoundryOwnerAction, head: String, dryRun: Bool) throws -> FoundryPlan {
        guard enginePresent else {
            return try fallbackPlan(action: action, head: head)
        }
        let planData = try FoundryPlanTemplate.enginePlanJSON(action: action, head: head, ownerConfirmed: true)
        let planFile = try writeTempPlan(planData)
        defer { try? FileManager.default.removeItem(at: planFile) }
        var args = ["run", Self.graduatePkg, "--plan", planFile.path, "--repo", repoRoot]
        if dryRun { args.append("--dry-run") }
        let output = try launchGo(args: args)
        let planID = parseDryRunPlanID(output) ?? FoundryPlanTemplate.stubPlanID(head: head, action: action)
        return FoundryPlanTemplate.uiPlan(action: action, head: head, planID: planID)
    }

    private func execute(action: FoundryOwnerAction, head: String, planHash: String) throws -> FoundryExecution {
        guard enginePresent else {
            return try fallbackExecution(action: action, head: head, planHash: planHash)
        }
        let planData = try FoundryPlanTemplate.enginePlanJSON(action: action, head: head, ownerConfirmed: true)
        let planFile = try writeTempPlan(planData)
        defer { try? FileManager.default.removeItem(at: planFile) }
        let args = ["run", Self.graduatePkg, "--plan", planFile.path, "--repo", repoRoot]
        do {
            _ = try launchGo(args: args)
            return FoundryExecution(
                action: action,
                phase: .completed,
                head: head,
                message: "Graduation engine recorded execution; production promotion still requires an independent PR."
            )
        } catch {
            return FoundryExecution(action: action, phase: .failed, head: head, message: error.localizedDescription)
        }
    }

    private func fallbackPlan(action: FoundryOwnerAction, head: String) throws -> FoundryPlan {
        switch action {
        case .integrate: return try fallback.dryRunIntegrate(head: head)
        case .spinOff: return try fallback.dryRunSpinOff(head: head)
        case .archive: return try fallback.dryRunArchive(head: head)
        }
    }

    private func fallbackExecution(action: FoundryOwnerAction, head: String, planHash: String) throws -> FoundryExecution {
        switch action {
        case .integrate: return try fallback.executeIntegrate(head: head, planHash: planHash)
        case .spinOff: return try fallback.executeSpinOff(head: head, planHash: planHash)
        case .archive: return try fallback.executeArchive(head: head, planHash: planHash)
        }
    }

    private func writeTempPlan(_ data: Data) throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("foundry-plan-\(UUID().uuidString).json")
        try data.write(to: url)
        return url
    }

    private func launchGo(args: [String]) throws -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["go"] + args
        process.currentDirectoryURL = URL(fileURLWithPath: repoRoot)
        let stdout = Pipe()
        let stderr = Pipe()
        process.standardOutput = stdout
        process.standardError = stderr
        try process.run()
        process.waitUntilExit()
        let outData = stdout.fileHandleForReading.readDataToEndOfFile()
        let errData = stderr.fileHandleForReading.readDataToEndOfFile()
        let out = String(data: outData, encoding: .utf8) ?? ""
        let err = String(data: errData, encoding: .utf8) ?? ""
        guard process.terminationStatus == 0 else {
            throw BridgeError.engineFailed(err.isEmpty ? out : err)
        }
        return out
    }

    private func parseDryRunPlanID(_ output: String) -> String? {
        for line in output.split(separator: "\n") {
            let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.hasPrefix("dry-run ok:") {
                return trimmed.replacingOccurrences(of: "dry-run ok:", with: "").trimmingCharacters(in: .whitespacesAndNewlines)
            }
        }
        return nil
    }

    private static func discoverRepoRoot() -> String {
        let fm = FileManager.default
        var dir = fm.currentDirectoryPath
        while true {
            if fm.fileExists(atPath: (dir as NSString).appendingPathComponent("go.mod")) {
                return dir
            }
            let parent = (dir as NSString).deletingLastPathComponent
            if parent == dir || parent.isEmpty { break }
            dir = parent
        }
        return fm.currentDirectoryPath
    }

    private enum BridgeError: LocalizedError {
        case engineFailed(String)

        var errorDescription: String? {
            switch self {
            case .engineFailed(let message):
                return message.trimmingCharacters(in: .whitespacesAndNewlines)
            }
        }
    }
}
