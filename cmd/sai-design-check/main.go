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

type contract struct {
	Status           string `json:"status"`
	FeatureUIAllowed bool   `json:"featureUIAllowed"`
	CodePolicy       struct {
		DesignPath  string `json:"swiftDesignAuthorityPath"`
		FeaturePath string `json:"featurePath"`
	} `json:"codePolicy"`
}

var forbidden = []struct {
	name string
	re   *regexp.Regexp
}{
	{"raw hex color", regexp.MustCompile(`#[0-9A-Fa-f]{6,8}`)},
	{"numeric padding", regexp.MustCompile(`\.padding\s*\([^)]*\b[0-9]+(?:\.[0-9]+)?\b`)},
	{"numeric corner radius", regexp.MustCompile(`\.cornerRadius\s*\(\s*[0-9]`)},
	{"raw system font size", regexp.MustCompile(`\.font\s*\(\s*\.system\s*\(\s*size\s*:\s*[0-9]`)},
	{"fixed frame geometry", regexp.MustCompile(`\.frame\s*\([^)]*(?:width|height)\s*:\s*[0-9]`)},
	{"numeric shadow radius", regexp.MustCompile(`\.shadow\s*\([^)]*radius\s*:\s*[0-9]`)},
	{"numeric z-index", regexp.MustCompile(`\.zIndex\s*\(\s*[0-9]`)},
}

func main() {
	if err := check("."); err != nil {
		fmt.Fprintln(os.Stderr, "Sai Design Language: FAIL:", err)
		os.Exit(1)
	}
	fmt.Println("Sai Design Language: PASS")
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
	if c.CodePolicy.DesignPath == "" || c.CodePolicy.FeaturePath == "" {
		return fmt.Errorf("contract metadata/codePolicy incomplete")
	}
	apple := filepath.Join(root, "apps", "apple")
	return filepath.WalkDir(apple, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.IsDir() || filepath.Ext(path) != ".swift" {
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
		if strings.HasPrefix(rel, filepath.ToSlash(c.CodePolicy.DesignPath)+"/") {
			return nil
		}
		for _, rule := range forbidden {
			if rule.re.MatchString(text) {
				return fmt.Errorf("%s: %s outside SaiDesignLanguage", rel, rule.name)
			}
		}
		if !c.FeatureUIAllowed && strings.HasPrefix(rel, filepath.ToSlash(c.CodePolicy.FeaturePath)+"/") &&
			(strings.Contains(text, ": View") || strings.Contains(text, "some View") {
			return fmt.Errorf("%s: feature UI is locked while design status=%s", rel, c.Status)
		}
		return nil
	})
}

func validateSchema(schema, doc []byte) error {
	var s, d any
	if err := json.Unmarshal(schema, &s); err != nil {
		return err
	}
	if err := json.Unmarshal(doc, &d); err != nil {
		return err
	}
	return applySchema(s, d, "$")
}

func applySchema(schema, doc any, path string) error {
	sm, ok := schema.(map[string]any)
	if !ok {
		return nil
	}
	if t, ok := sm["type"].(string); ok {
		if err := checkJSONType(t, doc, path); err != nil {
			return err
		}
	}
	switch v := doc.(type) {
	case map[string]any:
		if req, ok := sm["required"].([]any); ok {
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
		if props, ok := sm["properties"].(map[string]any); ok {
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

func checkJSONType(t string, doc any, path string) error {
	ok := false
	switch t {
	case "object":
		_, ok = doc.(map[string]any)
	case "array":
		_, ok = doc.([]any)
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
