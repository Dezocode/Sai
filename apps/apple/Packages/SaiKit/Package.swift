// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SaiKit",
    products: [
        .library(name: "SaiDesignLanguage", targets: ["SaiDesignLanguage"]),
        .library(name: "SaiFoundation", targets: ["SaiFoundation"]),
        .library(name: "SaiAPI", targets: ["SaiAPI"]),
        .library(name: "SaiFeatures", targets: ["SaiFeatures"]),
    ],
    targets: [
        .target(name: "SaiDesignLanguage"),
        .target(name: "SaiFoundation"),
        .target(name: "SaiAPI", dependencies: ["SaiFoundation"]),
        .target(name: "SaiFeatures", dependencies: ["SaiDesignLanguage", "SaiAPI"]),
    ]
)
