# Sai Author reference shell

Non-shipping prototype plugin for slice 77 (issue #160). macOS and iOS/iPadOS
placeholders compose production `SaiDesignLanguage` only. Deleting this tree
must not break production Sai.

## Build

```bash
swift build --package-path prototypes/plugins/author
(cd prototypes/plugins/author && xcodebuild -scheme SaiAuthorIOS -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO)
```

Production `apps/apple` targets are unchanged. This package depends on SaiKit via
a relative path and is not referenced from production manifests.
