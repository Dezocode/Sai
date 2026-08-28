package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io/fs"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

const (
	designAuth     = "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage"
	featureRoot    = "apps/apple/Packages/SaiKit/Sources/SaiFeatures"
	protoRoot      = "prototypes/plugins"
	protoDesignDir = "PrototypeDesign"
	macShell       = "apps/apple/SaiMac/SaiMacApp.swift"
	iosShell       = "apps/apple/SaiIOS/SaiIOSApp.swift"
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
	swiftUIImport = regexp.MustCompile(`(?m)(?:^|;)\s*(?:@[_\w]+(?:\([^)]*\))?\s+|\b(?:open|public|package|internal|fileprivate|private)\s+)*import\s+(?:(?:struct|class|enum|protocol|func|let|var|typealias)\s+)?SwiftUI\b`)
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
	if m := regexp.MustCompile(`featureUIAllowed\s*=\s*(true|false)`).FindStringSubmatch(s); len(m) < 2 || (m[1] == "true") != c.FeatureUIAllowed { return fmt.Errorf("tokens: featureUIAllowed") }
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

// inCanonicalPrototype: rel in the verifier-owned prototype root under a non-empty plugin; fails closed on traversal/abs/near-prefix/root/direct child.
func inCanonicalPrototype(rel string) bool {
	raw := filepath.ToSlash(rel)
	if strings.Contains(raw, "..") || strings.HasPrefix(raw, "/") { return false }
	p := filepath.ToSlash(filepath.Clean("/" + strings.TrimPrefix(raw, "/")))
	if p == "/"+protoRoot || !strings.HasPrefix(p, "/"+protoRoot+"/") { return false }
	return strings.IndexByte(strings.TrimPrefix(p, "/"+protoRoot+"/"), '/') > 0
}

// inPluginDesignScope: canonical-prototype file in its plugin's PrototypeDesign/ (nested ok).
func inPluginDesignScope(rel string) bool {
	if !inCanonicalPrototype(rel) { return false } // canonical form guarantees prototypes/plugins/<plugin>/...
	p := strings.SplitN(filepath.ToSlash(rel), "/", 4)
	return len(p) == 4 && strings.HasPrefix(p[3], protoDesignDir+"/")
}

// resolvesInto: manifest path value resolved against its manifest dir (or repo root when absolute); fails closed.
func resolvesInto(root, from, value string) bool {
	v := strings.TrimSpace(strings.ReplaceAll(value, "\\", "/"))
	if v == "" { return false }
	if filepath.IsAbs(v) || strings.HasPrefix(v, "~") {
		abs := v
		if abs[0] == '~' {
			home, err := os.UserHomeDir()
			if err != nil { return true }
			abs = filepath.Join(home, abs[1:])
		} // unresolvable ~ fails closed
		rootAbs, err := filepath.Abs(root)
		if err != nil {
			return true
		} // cannot anchor repo root: fail closed
		rootCanon, err := filepath.EvalSymlinks(rootAbs)
		if err != nil {
			return true
		} // root must resolve: fail closed
		cand := filepath.ToSlash(filepath.Clean(abs))
		for d := cand; ; { // canonicalize via nearest existing ancestor: /var->/private/var roots and dead symlinked dirs caught even with missing leaves
			if r, err := filepath.EvalSymlinks(d); err == nil {
				cand = filepath.ToSlash(filepath.Join(r, strings.TrimPrefix(cand, d)))
				break
			}
			u := filepath.Dir(d)
			if u == d { break }
			d = u
		}
		lane := filepath.ToSlash(filepath.Clean(rootCanon)) + "/prototypes"
		return cand == "/"+protoRoot || strings.HasPrefix(cand, "/"+protoRoot+"/") || cand == lane || strings.HasPrefix(cand, lane+"/")
	}
	base := filepath.ToSlash(filepath.Clean("/" + strings.TrimPrefix(filepath.ToSlash(from), "/")))
	dir := base[:strings.LastIndexByte(base, '/')+1]
	c := path.Clean(dir + v); lane := "/prototypes"; return c == "/"+protoRoot || strings.HasPrefix(c, "/"+protoRoot+"/") || c == lane || strings.HasPrefix(c, lane+"/")
}

// skipMeta reports whether a directory is tooling metadata to prune.
func skipMeta(name string) bool {
	return name == ".git" || name == ".build" || name == ".swiftpm"
}

// TRUNCATED_FOR_SIZE - WILL CONTINUE IN NEXT PUSH
