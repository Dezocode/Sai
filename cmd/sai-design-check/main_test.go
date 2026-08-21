package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestForbiddenFeatureLiteralFails(t *testing.T) {
	root := fixture(t, false, `import SwiftUI
struct Bad: View { var body: some View { Text("x").padding(17) } }`)
	if err := check(root); err == nil {
		t.Fatal("expected arbitrary feature padding to fail")
	}
}

func TestDesignAuthorityMayOwnRawValues(t *testing.T) {
	root := fixture(t, true, `public let allowed = "#112233"`)
	if err := check(root); err != nil {
		t.Fatal(err)
	}
}

func fixture(t *testing.T, designAuthority bool, source string) string {
	t.Helper()
	root := t.TempDir()
	for _, d := range []string{"design", "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage", "apps/apple/Packages/SaiKit/Sources/SaiFeatures"} {
		if err := os.MkdirAll(filepath.Join(root, d), 0755); err != nil { t.Fatal(err) }
	}
	c := map[string]interface{}{
		"version":1, "status":"approved", "featureUIAllowed":true,
		"grid":map[string]int{"x":1}, "typography":map[string]int{"x":1}, "color":map[string]int{"x":1},
		"borders":map[string]int{"x":1}, "elevation":map[string]int{"x":1}, "controls":map[string]int{"x":1},
		"layout":map[string]int{"x":1}, "motion":map[string]int{"x":1}, "accessibility":map[string]int{"x":1},
		"components":map[string]int{"x":1}, "layers":map[string]int{"x":1}, "dataVisualization":map[string]int{"x":1}, "media":map[string]int{"x":1},
		"codePolicy":map[string]string{"swiftDesignAuthorityPath":"apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage", "featurePath":"apps/apple/Packages/SaiKit/Sources/SaiFeatures"},
	}
	b, _ := json.Marshal(c)
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.json"), b, 0644); err != nil { t.Fatal(err) }
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.schema.json"), []byte("{}"), 0644); err != nil { t.Fatal(err) }
	path := "apps/apple/Packages/SaiKit/Sources/SaiFeatures/Test.swift"
	if designAuthority { path = "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/Test.swift" }
	if err := os.WriteFile(filepath.Join(root, path), []byte(source), 0644); err != nil { t.Fatal(err) }
	return root
}
