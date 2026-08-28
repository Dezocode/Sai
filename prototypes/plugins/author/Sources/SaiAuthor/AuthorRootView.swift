import SaiDesignLanguage
import SwiftUI

public struct AuthorRootView: View {
    public init() {}

    public var body: some View {
        TabView {
            EditorPlaceholder()
                .tabItem { Label("Editor", systemImage: "square.and.pencil") }
            SettingsPlaceholder()
                .tabItem { Label("Settings", systemImage: "gearshape") }
        }
    }
}
