package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestForbiddenFeatureLiteralFails(t *testing.T) {
	srcs := []string{`import SwiftUI
struct Bad: View { var body: some View { Text("x").padding(17) } }`, `import SwiftUI
struct C: View { var body: some View { Color.red } }`, `import SwiftUI
struct D: View { var body: some View { Color(red: 1, green: 0, blue: 0) } }`}
	for _, src := range srcs {
		if err := check(fixture(t, false, src)); err == nil {
			t.Fatal("expected arbitrary feature literal to fail")
		}
	}
}

func TestDesignAuthorityMayOwnRawValues(t *testing.T) {
	root := fixture(t, true, `public let allowed = "#112233"`)
	if err := check(root); err != nil {
		t.Fatal(err)
	}
}

func TestSchemaRejectsMissingRequired(t *testing.T) {
	root := fixture(t, true, `public let allowed = "#112233"`)
	cpath := filepath.Join(root, "design/sai-design-language.json")
	b, err := os.ReadFile(cpath)
	if err != nil {
		t.Fatal(err)
	}
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatal(err)
	}
	delete(m, "grid")
	out, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(cpath, out, 0644); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err == nil {
		t.Fatal("expected schema failure")
	}
}

func TestProductionContractSatisfiesSchema(t *testing.T) {
	src := filepath.Join("..", "..")
	if err := check(src); err != nil {
		t.Fatal(err)
	}
	root := fixture(t, true, "")
	for _, rel := range []string{"design/sai-design-language.json", "design/sai-design-language.schema.json", "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/SaiDesignLanguage.swift"} {
		b, err := os.ReadFile(filepath.Join(src, rel))
		if err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(root, rel), b, 0644); err != nil {
			t.Fatal(err)
		}
	}
	if err := check(root); err != nil {
		t.Fatal(err)
	}
	cpath := filepath.Join(root, "design/sai-design-language.json")
	b, err := os.ReadFile(cpath)
	if err != nil {
		t.Fatal(err)
	}
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatal(err)
	}
	m["featureUIAllowed"] = true
	out, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(cpath, out, 0644); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err == nil {
		t.Fatal("expected JSON/Swift featureUIAllowed drift to fail")
	}
}

func TestEnforcementClosed(t *testing.T) {
	rewrite := func(root, key, val string) {
		cpath := filepath.Join(root, "design/sai-design-language.json")
		b, err := os.ReadFile(cpath)
		if err != nil {
			t.Fatal(err)
		}
		var m map[string]interface{}
		if err := json.Unmarshal(b, &m); err != nil {
			t.Fatal(err)
		}
		m["codePolicy"].(map[string]interface{})[key] = val
		out, err := json.Marshal(m)
		if err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(cpath, out, 0644); err != nil {
			t.Fatal(err)
		}
	}
	root := fixture(t, true, "")
	rewrite(root, "swiftDesignAuthorityPath", "apps/apple")
	if err := check(root); err == nil {
		t.Fatal("widen")
	}
	root = fixture(t, true, "")
	rewrite(root, "featurePath", "apps/apple/nowhere")
	if err := check(root); err == nil {
		t.Fatal("move featurePath")
	}
	root = fixture(t, true, "")
	if err := os.Remove(filepath.Join(root, designAuth, "SaiDesignLanguage.swift")); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err == nil {
		t.Fatal("missing")
	}
	root = fixture(t, true, "")
	cpath := filepath.Join(root, "design/sai-design-language.json")
	b, err := os.ReadFile(cpath)
	if err != nil {
		t.Fatal(err)
	}
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatal(err)
	}
	m["featureUIAllowed"] = false
	out, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(cpath, out, 0644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, designAuth, "SaiDesignLanguage.swift"), []byte(authoritySwift(false)), 0644); err != nil {
		t.Fatal(err)
	}
	fail := func(rel, src string) {
		t.Helper()
		p := filepath.Join(root, rel)
		if err := os.MkdirAll(filepath.Dir(p), 0755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(p, []byte(src), 0644); err != nil {
			t.Fatal(err)
		}
		if err := check(root); err == nil {
			t.Fatal(rel)
		}
		os.Remove(p)
	}
	base := "apps/apple/Packages/SaiKit/Sources/SaiFoundation/Sneak.swift"
	fail(base, "import SwiftUI\nfunc dashboard() -> Text { Text(\"Dashboard\") }\n")
	fail(featureRoot+"/Dash.swift", "import Foundation; @_implementationOnly import SwiftUI\n")
	fail("Extra.swift", "import SaiDesignLanguage; public func dashboard() -> SaiText { SaiText(\"Dashboard\") }\n")
	mac := "apps/apple/SaiMac/SaiMacApp.swift"
	fail(mac, "import SwiftUI\n@main struct SaiMacApp: App { var body: some Scene { WindowGroup { SaiCanvas { SaiText(\"Sai\") } } } }\nstruct Dashboard: View { var body: some View { Rectangle() } }\n")
	if err := os.WriteFile(filepath.Join(root, featureRoot, "IDs.swift"), []byte("import Foundation\ntypealias UserID = UUID\n"), 0644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, filepath.Dir(mac)), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, mac), []byte("@main struct SaiMacApp: App { var body: some Scene { WindowGroup { SaiCanvas { SaiText(\"Sai\") } } } }\n"), 0644); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err != nil {
		t.Fatal(err)
	}
}

func lockedRoot(t *testing.T) string {
	t.Helper()
	root := fixture(t, true, "")
	cpath := filepath.Join(root, "design/sai-design-language.json")
	b, err := os.ReadFile(cpath)
	if err != nil {
		t.Fatal(err)
	}
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatal(err)
	}
	m["featureUIAllowed"] = false
	m["status"] = "foundation-draft"
	out, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(cpath, out, 0644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, designAuth, "SaiDesignLanguage.swift"), []byte(authoritySwift(false)), 0644); err != nil {
		t.Fatal(err)
	}
	for _, rel := range []string{"apps/apple/SaiMac/SaiMacApp.swift", "apps/apple/SaiIOS/SaiIOSApp.swift"} {
		if err := os.MkdirAll(filepath.Join(root, filepath.Dir(rel)), 0755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(root, rel), []byte("@main struct Shell: App { var body: some Scene { WindowGroup { SaiCanvas { SaiText(\"Sai\") } } } }\n"), 0644); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func TestPrototypeLaneAllowsSwiftUI(t *testing.T) {
	root := lockedRoot(t)
	rel := "prototypes/plugins/author/AuthorRootView.swift"
	p := filepath.Join(root, rel)
	if err := os.MkdirAll(filepath.Dir(p), 0755); err != nil {
		t.Fatal(err)
	}
	src := "import SwiftUI\nimport SaiDesignLanguage\npublic struct AuthorRootView: View { public var body: some View { TabView { Text(\"x\") } } }\n"
	if err := os.WriteFile(p, []byte(src), 0644); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err != nil {
		t.Fatal(err)
	}
}

func TestNearPrefixCannotBecomePrototypeLane(t *testing.T) {
	root := lockedRoot(t)
	rel := "prototypes/plugins-evil/Sneak.swift"
	p := filepath.Join(root, rel)
	if err := os.MkdirAll(filepath.Dir(p), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(p, []byte("import SwiftUI\nstruct Sneak: View { var body: some View { Text(\"no\") } }\n"), 0644); err != nil {
		t.Fatal(err)
	}
	if err := check(root); err == nil {
		t.Fatal("near-prefix must not bypass production SwiftUI lock")
	}
}

func authoritySwift(allowed bool) string {
	v := "false"
	if allowed {
		v = "true"
	}
	return "import SwiftUI\npublic enum SaiDesignLanguage {\npublic static let featureUIAllowed = " + v + "\npublic static let canvas = Color(red: 15.0 / 255.0, green: 17.0 / 255.0, blue: 21.0 / 255.0)\npublic static let textPrimary = Color(red: 244.0 / 255.0, green: 245.0 / 255.0, blue: 247.0 / 255.0)\npublic static let spacingLg: CGFloat = 24\npublic static let title2: CGFloat = 24\npublic static let title2LineHeight: CGFloat = 29\n}\n.font(.system(size: 1, weight: .semibold))\n"
}

func fixture(t *testing.T, designAuthority bool, source string) string {
	t.Helper()
	root := t.TempDir()
	for _, d := range []string{"design", designAuth, featureRoot} {
		if err := os.MkdirAll(filepath.Join(root, d), 0755); err != nil {
			t.Fatal(err)
		}
	}
	c := map[string]interface{}{
		"version": 1, "status": "approved", "featureUIAllowed": true,
		"grid": map[string]interface{}{"unit": 4, "spacing": map[string]float64{"lg": 24}},
		"typography": map[string]interface{}{"families": 1, "dynamicType": 1, "roles": map[string]interface{}{"title2": map[string]float64{"size": 24, "lineHeight": 29}}},
		"color": map[string]interface{}{"canvas": "#0F1115", "textPrimary": "#F4F5F7", "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10},
		"borders": map[string]int{"hairline": 1, "focus": 2, "radii": 1}, "elevation": map[string]int{"x": 1},
		"controls": map[string]int{"macOS": 1, "iOS": 1, "states": 1, "buttonVariants": 1},
		"layout": map[string]int{"adaptiveWidths": 1, "pagePadding": 1, "maxContentWidth": 1, "rules": 1},
		"motion": map[string]int{"durationsMs": 1, "easing": 1, "reducedMotion": 1}, "accessibility": map[string]int{"x": 1},
		"components": map[string]int{"required": 1, "localFeaturePrimitivesAllowed": 1}, "layers": map[string]int{"x": 1},
		"dataVisualization": map[string]int{"x": 1}, "media": map[string]int{"x": 1},
		"codePolicy": map[string]string{"swiftDesignAuthorityPath": designAuth, "featurePath": featureRoot},
	}
	b, _ := json.Marshal(c)
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.json"), b, 0644); err != nil {
		t.Fatal(err)
	}
	schema, err := os.ReadFile(filepath.Join("..", "..", "design/sai-design-language.schema.json"))
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.schema.json"), schema, 0644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, designAuth, "SaiDesignLanguage.swift"), []byte(authoritySwift(true)), 0644); err != nil {
		t.Fatal(err)
	}
	path := featureRoot + "/Test.swift"
	if designAuthority {
		path = designAuth + "/Test.swift"
	}
	if err := os.WriteFile(filepath.Join(root, path), []byte(source), 0644); err != nil {
		t.Fatal(err)
	}
	return root
}
