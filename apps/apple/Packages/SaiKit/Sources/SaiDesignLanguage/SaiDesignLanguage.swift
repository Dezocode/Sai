import SwiftUI

public enum SaiDesignLanguage {
    public static let featureUIAllowed = false
    public static let canvas = Color(red: 15.0 / 255.0, green: 17.0 / 255.0, blue: 21.0 / 255.0)
    public static let textPrimary = Color(red: 244.0 / 255.0, green: 245.0 / 255.0, blue: 247.0 / 255.0)
    public static let spacingLg: CGFloat = 24
    public static let title2: CGFloat = 24
}

public struct SaiText: View {
    let text: String
    public init(_ text: String) { self.text = text }
    public var body: some View {
        Text(text).font(.system(size: SaiDesignLanguage.title2, relativeTo: .title2)).foregroundStyle(SaiDesignLanguage.textPrimary)
    }
}

public struct SaiCanvas<Content: View>: View {
    let content: Content
    public init(@ViewBuilder _ content: () -> Content) { self.content = content() }
    public var body: some View {
        content.padding(SaiDesignLanguage.spacingLg).frame(maxWidth: .infinity, maxHeight: .infinity).background(SaiDesignLanguage.canvas)
    }
}
