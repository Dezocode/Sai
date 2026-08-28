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
    dependencies: [
        .package(path: "../../../../../apps/apple/Packages/SaiKit"),
    ],
    targets: [
        .target(
            name: "FoundryOwnerUX",
            dependencies: [
                .product(name: "SaiDesignLanguage", package: "SaiKit"),
            ]
        ),
        .testTarget(
            name: "FoundryOwnerUXTests",
            dependencies: ["FoundryOwnerUX"]
        ),
    ]
)
