// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FoundryOwnerUX",
    platforms: [
        .macOS(.v14),
        .iOS(.v17),
    ],
    products: [
        .library(name: "FoundryOwnerUX", targets: ["FoundryOwnerUX"]),
    ],
    targets: [
        .target(
            name: "FoundryOwnerUX"
        ),
        .testTarget(
            name: "FoundryOwnerUXTests",
            dependencies: ["FoundryOwnerUX"]
        ),
    ]
)
