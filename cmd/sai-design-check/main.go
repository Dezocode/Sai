package main

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const (
	designAuth  = "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage"
	featureRoot = "apps/apple/Packages/SaiKit/Sources/SaiFeatures"
)

type contract struct {
	Status           string `json:"status"`
	FeatureUIAllowed bool   `json:"featureUIAllowed"`
	CodePolicy       struct {
		DesignPath  string `json:"swiftDesignAuthorityPath"`
		FeaturePath string `json:"featurePath"`
	} `json:"codePolicy"`
}

var (
	swiftUIImport = regexp.MustCompile(`(?m)(?:^|;)\s*(?:@_exported\s+)?import\s+(?:(?:struct|class|enum|func|var|typealias)\s+)?SwiftUI\b`)
	shellUI       = regexp.MustCompile(`\b(?:VStack|HStack|ZStack|LazyVStack|LazyHStack|LazyVGrid|LazyHGrid|List|Form|NavigationStack|NavigationView|NavigationSplitView|TabView|Text|Button|Image|Label|Picker|Toggle|Slider|Stepper|TextField|SecureField|TextEditor|ProgressView|Spacer|Divider|ScrollView|ForEach|Section|Menu|Grid|GeometryReader|View|Rectangle|Circle|Ellipse|Capsule|Path|Canvas|AnyView)\b`)
	shellBody     = regexp.MustCompile(`WindowGroup\s*\{\s*SaiCanvas\s*\{\s*SaiText\s*\(\s*"[^"]*"\s*\)\s*\}\s*(?:\.task\s*\{\s*await\s+ping\(\)\s*\}\s*)?\}`)
	forbidden     = []struct {
		name string
		re   *regexp.Regexp
	}{
		{"raw hex or Color literal", regexp.MustCompile(`#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6,8})\b|\b(?:Color|UIColor|NSColor)\s*\(|\b(?:Color|UIColor|NSColor)\.(?:red|blue|green|orange|yellow|pink|purple|gray|grey|black|white|primary|secondary|accentColor)\b`)},
		{"numeric padding", regexp.MustCompile(`\.padding\s*\([^)]*\b[0-9]+(?:\.[0-9]+)?\b`)},
		{"numeric corner radius", regexp.MustCompile(`\.cornerRadius\s*\(\s*[0-9]`)},
		{"raw system font size", regexp.MustCompile(`\.font\s*\(\s*\.system\s*\(\s*size\s*:\s*[0-9]`)},
		{"fixed frame geometry", regexp.MustCompile(`\.frame\s*\([^)]*(?:width|height)\s*:\s*[0-9]`)},
		{"numeric shadow radius", regexp.MustCompile(`\.shadow\s*\([^)]*radius\s*:\s*[0-9]`)},
		{"numeric z-index", regexp.MustCompile(`\.zIndex\s*\(\s*[0-9]`)},
	}
)

func main() {
	if err := check("."); err != nil {
		fmt.Fprintln(os.Stderr, "Sai Design Language: FAIL:", err)
		os.Exit(1)
	}
	fmt.Println("Sai Design Language: PASS")
}

func nest(v interface{}, keys ...string) interface{} {
	for _, k := range keys {
		m, _ := v.(map[string]interface{})
		v = m[k]
	}
	return v
}

func matchSwift(root string, c contract, body []byte) error {
	var raw map[string]interface{}
	if json.Unmarshal(body, &raw) != nil {
		return fmt.Errorf("tokens: contract")
	}
	b, err := os.ReadFile(filepath.Join(root, designAuth, "SaiDesignLanguage.swift"))
	if err != nil {
		return fmt.Errorf("tokens: missing SaiDesignLanguage.swift")
	}
	s := string(b)
	m := regexp.MustCompile(`featureUIAllowed\s*=\s*(true|false)`).FindStringSubmatch(s)
	if len(m) < 2 || (m[1] == "true") != c.FeatureUIAllowed {
		return fmt.Errorf("tokens: featureUIAllowed")
	}
	eqRGB := func(field, hex string) error {
		g := regexp.MustCompile(field + `\s*=\s*Color\(\s*red:\s*([0-9.]+)\s*/\s*255(?:\.0)?\s*,\s*green:\s*([0-9.]+)\s*/\s*255(?:\.0)?\s*,\s*blue:\s*([0-9.]+)\s*/\s*255(?:\.0)?\s*\)`).FindStringSubmatch(s)
		var hr, hg, hb int
		var r, gv, bv float64
		nhex, _ := fmt.Sscanf(hex, "#%02x%02x%02x", &hr, &hg, &hb)
		if len(g) < 4 || nhex != 3 {
			return fmt.Errorf("tokens: %s", field)
		}
		fmt.Sscanf(g[1]+" "+g[2]+" "+g[3], "%f %f %f", &r, &gv, &bv)
		if int(r+0.5) != hr || int(gv+0.5) != hg || int(bv+0.5) != hb {
			return fmt.Errorf("tokens: %s != %s", field, hex)
		}
		return nil
	}

eqN := func(field string, want float64) error {
		g := regexp.MustCompile(field + `:\s*CGFloat\s*=\s*([0-9.]+)`).FindStringSubmatch(s)
		var n float64
		if len(g) < 2 {
			return fmt.Errorf("tokens: %s", field)
		}
		fmt.Sscanf(g[1], "%f", &n)
		if n != want {
			return fmt.Errorf("tokens: %s", field)
		}
		return nil
	}
	canvas, _ := nest(raw, "color", "canvas").(string)
	text, _ := nest(raw, "color", "textPrimary").(string)
	if err := eqRGB("canvas", canvas); err != nil {
		return err
	}
	if err := eqRGB("textPrimary", text); err != nil {
		return err
	}
	lg, _ := nest(raw, "grid", "spacing", "lg").(float64)
	t2, _ := nest(raw, "typography", "roles", "title2", "size").(float64)
	lh, _ := nest(raw, "typography", "roles", "title2", "lineHeight").(float64)
	if err := eqN("spacingLg", lg); err != nil {
		return err
	}
	if err := eqN("title2", t2); err != nil || eqN("title2LineHeight", lh) != nil || !strings.Contains(s, "weight: .semibold") {
		return fmt.Errorf("tokens: title2")
	}
	return nil
}

func check(root string) error {
	body, err := os.ReadFile(filepath.Join(root, "design", "sai-design-language.json"))
	if err != nil {
		return fmt.Errorf("contract: %w", err)
	}
	schema, err := os.ReadFile(filepath.Join(root, "design", "sai-design-language.schema.json"))
	if err != nil {
		return fmt.Errorf("schema: %w", err)
	}
	if err := validateSchema(schema, body); err != nil {
		return fmt.Errorf("schema: %w", err)
	}
	var c contract
	if err := json.Unmarshal(body, &c); err != nil {
		return fmt.Errorf("contract JSON: %w", err)
	}
	if filepath.ToSlash(c.CodePolicy.DesignPath) != designAuth || filepath.ToSlash(c.CodePolicy.FeaturePath) != featureRoot {
		return fmt.Errorf("codePolicy: verifier-owned paths")
	}
	if err := matchSwift(root, c, body); err != nil {
		return err
	}
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.IsDir() {
			switch d.Name() {
			case ".git", ".build", ".swiftpm":
				return fs.SkipDir
			}
			return nil
		}
		if filepath.Ext(path) != ".swift" {
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		textb, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		text := string(textb)
		if strings.HasPrefix(rel, designAuth+"/") {
			return nil
		}
		for _, rule := range forbidden {
			if rule.re.MatchString(text) {
				return fmt.Errorf("%s: %s outside SaiDesignLanguage", rel, rule.name)
			}
		}
		if !c.FeatureUIAllowed && (rel == "apps/apple/SaiMac/SaiMacApp.swift" || rel == "apps/apple/SaiIOS/SaiIOSApp.swift") && (strings.Count(text, "SaiCanvas") != 1 || strings.Count(text, "SaiText") != 1 || !shellBody.MatchString(text) || shellUI.MatchString(text)) {
			return fmt.Errorf("%s: shell composition", rel)
		}
		if !c.FeatureUIAllowed && rel != "apps/apple/SaiMac/SaiMacApp.swift" && rel != "apps/apple/SaiIOS/SaiIOSApp.swift" && swiftUIImport.MatchString(text) {
			return fmt.Errorf("%s: import SwiftUI is locked while design status=%s", rel, c.Status)
		}
		return nil
	})
}

func validateSchema(schema, doc []byte) error {
	var s, d interface{}
	if err := json.Unmarshal(schema, &s); err != nil {
		return err
	}
	if err := json.Unmarshal(doc, &d); err != nil {
		return err
	}
	return applySchema(s, d, "$")
}

func applySchema(schema, doc interface{}, path string) error {
	sm, ok := schema.(map[string]interface{})
	if !ok {
		return nil
	}
	if t, ok := sm["type"].(string); ok {
		if err := checkJSONType(t, doc, path); err != nil {
			return err
		}
	}
	switch v := doc.(type) {
	case map[string]interface{}:
		if req, ok := sm["required"].([]interface{}); ok {
			for _, r := range req {
				key, _ := r.(string)
				if _, ok := v[key]; !ok {
					return fmt.Errorf("%s missing required %s", path, key)
				}
			}
		}
		if min, ok := sm["minProperties"].(float64); ok && float64(len(v)) < min {
			return fmt.Errorf("%s minProperties", path)
		}
		if props, ok := sm["properties"].(map[string]interface{}); ok {
			for k, sub := range props {
				if child, ok := v[k]; ok {
					if err := applySchema(sub, child, path+"."+k); err != nil {
						return err
					}
				}
			}
		}
	case float64:
		if min, ok := sm["minimum"].(float64); ok && v < min {
			return fmt.Errorf("%s minimum", path)
		}
	}
	return nil
}

func checkJSONType(t string, doc interface{}, path string) error {
	ok := false
	switch t {
	case "object":
		_, ok = doc.(map[string]interface{})
	case "array":
		_, ok = doc.([]interface{})
	case "string":
		_, ok = doc.(string)
	case "boolean":
		_, ok = doc.(bool)
	case "integer":
		n, isNum := doc.(float64)
		ok = isNum && n == float64(int64(n))
	case "number":
		_, ok = doc.(float64)
	default:
		return nil
	}
	if !ok {
		return fmt.Errorf("%s want %s", path, t)
	}
	return nil
}
