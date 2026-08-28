// swift-tools-version: 5.9
import PackageDescription

let saiKit = Package.Dependency.package(path: "../../../../apps/apple/Packages/SaiKit")
let sai: [Target.Dependency] = [
    .product(name: "SaiDesignLanguage", package: "SaiKit"),
]

let package = Package(
    name: "SaiAuthor",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [
        .executable(name: "SaiAuthorMac", targets: ["SaiAuthorMac"]),
        .executable(name: "SaiAuthorIOS", targets: ["SaiAuthorIOS"]),
    ],
    dependencies: [saiKit],
    targets: [
        .target(name: "SaiAuthor", dependencies: sai, path: "Sources/SaiAuthor"),
        .executableTarget(name: "SaiAuthorMac", dependencies: ["SaiAuthor"], path: "SaiAuthorMac"),
        .executableTarget(name: "SaiAuthorIOS", dependencies: ["SaiAuthor"], path: "SaiAuthorIOS"),
    ]
)
