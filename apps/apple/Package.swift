// swift-tools-version: 5.9
import PackageDescription

let sai: [Target.Dependency] = [
    .product(name: "SaiDesignLanguage", package: "SaiKit"),
    .product(name: "SaiFoundation", package: "SaiKit"),
    .product(name: "SaiAPI", package: "SaiKit"),
]
let package = Package(
    name: "SaiApple",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [
        .executable(name: "SaiMac", targets: ["SaiMac"]),
        .executable(name: "SaiIOS", targets: ["SaiIOS"]),
    ],
    dependencies: [.package(path: "Packages/SaiKit")],
    targets: [
        .executableTarget(name: "SaiMac", dependencies: sai, path: "SaiMac"),
        .executableTarget(name: "SaiIOS", dependencies: sai, path: "SaiIOS"),
    ]
)
