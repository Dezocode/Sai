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
	if err := check(filepath.Join("..", "..")); err != nil {
		t.Fatal(err)
	}
}

func fixture(t *testing.T, designAuthority bool, source string) string {
	t.Helper()
	root := t.TempDir()
	for _, d := range []string{"design", "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage", "apps/apple/Packages/SaiKit/Sources/SaiFeatures"} {
		if err := os.MkdirAll(filepath.Join(root, d), 0755); err != nil {
			t.Fatal(err)
		}
	}
	c := map[string]interface{}{
		"version": 1, "status": "approved", "featureUIAllowed": true,
		"grid": map[string]int{"unit": 4, "spacing": 1}, "typography": map[string]int{"families": 1, "dynamicType": 1, "roles": 1},
		"color": map[string]int{"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9, "j": 10},
		"borders": map[string]int{"hairline": 1, "focus": 2, "radii": 1}, "elevation": map[string]int{"x": 1},
		"controls": map[string]int{"macOS": 1, "iOS": 1, "states": 1, "buttonVariants": 1},
		"layout": map[string]int{"adaptiveWidths": 1, "pagePadding": 1, "maxContentWidth": 1, "rules": 1},
		"motion": map[string]int{"durationsMs": 1, "easing": 1, "reducedMotion": 1}, "accessibility": map[string]int{"x": 1},
		"components": map[string]int{"required": 1, "localFeaturePrimitivesAllowed": 1}, "layers": map[string]int{"x": 1},
		"dataVisualization": map[string]int{"x": 1}, "media": map[string]int{"x": 1},
		"codePolicy": map[string]string{"swiftDesignAuthorityPath": "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage", "featurePath": "apps/apple/Packages/SaiKit/Sources/SaiFeatures"},
	}
	b, _ := json.Marshal(c)
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.json"), b, 0644); err != nil {
		t.Fatal(err)
	}
	schema, err := os.ReadFile(filepath.Join("..", "..", "design", "sai-design-language.schema.json"))
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.schema.json"), schema, 0644); err != nil {
		t.Fatal(err)
	}
	path := "apps/apple/Packages/SaiKit/Sources/SaiFeatures/Test.swift"
	if designAuthority {
		path = "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage/Test.swift"
	}
	if err := os.WriteFile(filepath.Join(root, path), []byte(source), 0644); err != nil {
		t.Fatal(err)
	}
	return root
}
