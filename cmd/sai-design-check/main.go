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
	Version           int             `json:"version"`
	Status            string          `json:"status"`
	FeatureUIAllowed  bool            `json:"featureUIAllowed"`
	Grid              json.RawMessage `json:"grid"`
	Typography        json.RawMessage `json:"typography"`
	Color             json.RawMessage `json:"color"`
	Borders           json.RawMessage `json:"borders"`
	Elevation         json.RawMessage `json:"elevation"`
	Controls          json.RawMessage `json:"controls"`
	Layout            json.RawMessage `json:"layout"`
	Motion            json.RawMessage `json:"motion"`
	Accessibility     json.RawMessage `json:"accessibility"`
	Components        json.RawMessage `json:"components"`
	Layers            json.RawMessage `json:"layers"`
	DataVisualization json.RawMessage `json:"dataVisualization"`
	Media             json.RawMessage `json:"media"`
	CodePolicy        struct {
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
	c, err := loadContract(filepath.Join(root, "design", "sai-design-language.json"))
	if err != nil {
		return err
	}
	if _, err := os.Stat(filepath.Join(root, "design", "sai-design-language.schema.json")); err != nil {
		return fmt.Errorf("schema: %w", err)
	}
	for _, raw := range []json.RawMessage{c.Grid, c.Typography, c.Color, c.Borders, c.Elevation, c.Controls, c.Layout, c.Motion, c.Accessibility, c.Components, c.Layers, c.DataVisualization, c.Media} {
		if len(raw) == 0 || string(raw) == "null" {
			return fmt.Errorf("contract is missing a required design domain")
		}
	}
	if c.Version < 1 || c.Status == "" || c.CodePolicy.DesignPath == "" || c.CodePolicy.FeaturePath == "" {
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
		body, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		text := string(body)
		if strings.HasPrefix(rel, filepath.ToSlash(c.CodePolicy.DesignPath)+"/") {
			return nil
		}
		for _, rule := range forbidden {
			if rule.re.MatchString(text) {
				return fmt.Errorf("%s: %s outside SaiDesignLanguage", rel, rule.name)
			}
		}
		if !c.FeatureUIAllowed && strings.HasPrefix(rel, filepath.ToSlash(c.CodePolicy.FeaturePath)+"/") &&
			(strings.Contains(text, ": View") || strings.Contains(text, "some View")) {
			return fmt.Errorf("%s: feature UI is locked while design status=%s", rel, c.Status)
		}
		return nil
	})
}

func loadContract(path string) (contract, error) {
	var c contract
	body, err := os.ReadFile(path)
	if err != nil {
		return c, fmt.Errorf("contract: %w", err)
	}
	if err := json.Unmarshal(body, &c); err != nil {
		return c, fmt.Errorf("contract JSON: %w", err)
	}
	return c, nil
}
