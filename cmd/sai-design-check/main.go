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
	return path.Clean(dir+v) == "/"+protoRoot || strings.HasPrefix(path.Clean(dir+v), "/"+protoRoot+"/")
}

// skipMeta reports whether a directory is tooling metadata to prune.
func skipMeta(name string) bool {
	return name == ".git" || name == ".build" || name == ".swiftpm"
}

// checkSymlinkEscape: reject symlinks on the lane path or resolving into it; no production alias consumes lane code.
func checkSymlinkEscape(root string) error {
	// Canonicalize root once (macOS /var -> /private/var) so target Rels share its basis.
	rootAbs, err := filepath.Abs(root)
	if err != nil { return fmt.Errorf("%s: cannot absolutize root, fails closed: %v", root, err) }
	rootCanon, err := filepath.EvalSymlinks(rootAbs)
	if err != nil { return fmt.Errorf("%s: cannot resolve root, fails closed: %v", root, err) }
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.Type()&fs.ModeSymlink == 0 {
			if d.IsDir() && skipMeta(d.Name()) { return fs.SkipDir }
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		slash := filepath.ToSlash(rel)
		if slash == "prototypes" || strings.HasPrefix(slash, "prototypes/") { return fmt.Errorf("%s: symlink on prototype lane path escapes verification", slash) }
		absPath, err := filepath.Abs(path)
		if err != nil {
			return err
		}
		resolved, err := filepath.EvalSymlinks(absPath)
		if err != nil { return fmt.Errorf("%s: cannot resolve symlink, fails closed: %v", slash, err) }
		trel, err := filepath.Rel(rootCanon, resolved)
		if err != nil {
			return err
		}
		if tslash := filepath.ToSlash(trel); tslash == "prototypes" || strings.HasPrefix(tslash, "prototypes/") { return fmt.Errorf("%s: symlink resolves into prototype lane (%s)", slash, tslash) }
		return nil
	})
}

// checkGoWorkFiles: EVERY production go.work (walk-discovered; canonical top-level prototypes/ tree pruned)
// must not `use` or `replace` into the lane. Workspace directives resolve relative to the go.work directory,
// are symlink-resolved, then judged against the canonical root; unreadable workspaces fail closed.
func checkGoWorkFiles(root string) error {
	rootCanon, err := filepath.EvalSymlinks(func() string { a, _ := filepath.Abs(root); return a }())
	if err != nil { return fmt.Errorf("go.work: cannot resolve root, fails closed: %v", err) }
	gwLane := func(wdir, tok string) bool {
		tok = strings.Trim(tok, "\"'")
		if tok == "" || strings.HasPrefix(tok, "//") { return false }
		p := tok
		if !filepath.IsAbs(p) { p = filepath.Join(wdir, p) }
		cand := filepath.ToSlash(filepath.Clean(p))
		for d := cand; ; { // canonicalize via nearest existing ancestor (resolvesInto-style): symlinked root components (/var to /private/var on macOS CI) and missing leaves are both judged against the resolved root
			if r, rerr := filepath.EvalSymlinks(d); rerr == nil {
				cand = filepath.ToSlash(filepath.Join(r, strings.TrimPrefix(cand, d)))
				break
			}
			u := filepath.Dir(d)
			if u == d { break }
			d = u
		}
		laneRoot := filepath.ToSlash(filepath.Clean(rootCanon))
		return cand == laneRoot+"/"+protoRoot || cand == laneRoot+"/prototypes" || strings.HasPrefix(cand, laneRoot+"/"+protoRoot+"/") || strings.HasPrefix(cand, laneRoot+"/prototypes/")
	}
	return filepath.WalkDir(root, func(p string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			if p == filepath.Join(root, protoRoot) || skipMeta(d.Name()) { return fs.SkipDir }
			return nil
		}
		if d.Name() != "go.work" { return nil }
		b, rerr := os.ReadFile(p)
		if rerr != nil { return fmt.Errorf("%s: unreadable workspace fails closed: %v", p, rerr) }
		wdir := filepath.Dir(p)
		var inUse, inRep bool
		for _, line := range strings.Split(string(b), "\n") {
			tr := line
			if i := strings.Index(tr, "//"); i >= 0 { tr = tr[:i] }
			tr = strings.TrimSpace(tr)
			if tr == "" { continue }
			hit := func(what string) error {
				return fmt.Errorf("%s: %s directive reaches %s", p, what, protoRoot)
			}
			test := func(tok string) error {
				if gwLane(wdir, tok) { return hit("use") }
				return nil
			}
			switch {
			case tr == "use (":
				inUse = true
			case tr == "replace (":
				inRep = true
			case tr == ")":
				inUse, inRep = false, false
			case strings.HasPrefix(tr, "use "):
				for _, f := range strings.Fields(strings.TrimPrefix(tr, "use ")) {
					if err := test(f); err != nil { return err }
				}
			case strings.HasPrefix(tr, "replace ") && !inRep:
				rhs := tr[len("replace "):]
				parts := strings.SplitN(rhs, "=>", 2)
				if len(parts) != 2 { return fmt.Errorf("%s: malformed replace fails closed: %q", p, tr) }
				{
					targets := strings.Fields(parts[1])
					if len(targets) == 0 {
						return fmt.Errorf("%s: replace target missing fails closed: %q", p, tr)
					}
					if err := test(targets[0]); err != nil {
						return err
					}
				}
			case inUse:
				if err := test(tr); err != nil { return err }
			case inRep:
				parts := strings.SplitN(tr, "=>", 2)
				if len(parts) != 2 { return fmt.Errorf("%s: malformed replace-block entry fails closed: %q", p, tr) }
				{
					targets := strings.Fields(parts[1])
					if len(targets) == 0 {
						return fmt.Errorf("%s: replace target missing fails closed: %q", p, tr)
					}
					if err := test(targets[0]); err != nil {
						return err
					}
				}
			}
		}
		if inUse || inRep { return fmt.Errorf("%s: unterminated use/replace block fails closed", p) }
		return nil
	})
}

// checkProductionManifests: EVERY production Package.swift under root (walk-discovered; only the canonical top-level prototypes/ tree and tooling metadata are pruned) stays out of the lane; unlisted/nested/vendored manifests cannot bypass, unreadable trees fail closed.
func checkProductionManifests(root string) error {
	return filepath.WalkDir(root, func(p string, d fs.DirEntry, err error) error {
		if err != nil { return err } // unreadable tree is unverifiable: fail closed
		if d.IsDir() { // prune ONLY the canonical top-level lane tree; nested/vendored prototypes/ dirs stay inspected (Saul 97279716328)
			if p == filepath.Join(root, "prototypes") || skipMeta(d.Name()) { return fs.SkipDir }
			return nil
		}
		if d.Name() != "Package.swift" { return nil }
		b, err := os.ReadFile(p)
		rel, rerr := filepath.Rel(root, p)
		if err != nil || rerr != nil { return err } // unreadable manifest or unrelativizable path fails closed
		manifest := filepath.ToSlash(rel)
		for _, q := range manifestPaths(string(b)) {
			if !q.ok { return fmt.Errorf("%s: path must be an inline string literal, got computed %q", manifest, q.raw) }
			if resolvesInto(root, manifest, q.val) { return fmt.Errorf("%s: production manifest references prototype tree (%q)", manifest, q.val) }
		}
		return nil
	})
}

// manifestPath is one `path:` value; ok marks exact evaluation, raw holds fail-closed diagnostics.
type manifestPath struct {
	val, raw string
	ok       bool
}

// manifestPaths scans src once, atomically consuming comments/literals, classifying every path value.
func manifestPaths(src string) []manifestPath {
	var out []manifestPath
	for i := 0; i < len(src); {
		if src[i] == '"' || src[i] == '#' {
			i = skipSwiftString(src, i)
			continue
		}
		if j := skipTrivia(src, i); j > i {
			i = j
		} else if isPathLabel(src, i) {
			var p manifestPath
			i = classifyPathValue(src, i+4, &p)
			out = append(out, p)
		} else {
			i++
		}
	}
	return out
}

// skipTrivia advances past whitespace/comments to the next code byte (len(src) at end).
func skipTrivia(src string, i int) int {
	for i < len(src) {
		switch {
		case src[i] == ' ', src[i] == '\t', src[i] == '\n', src[i] == '\r':
			i++
		case src[i] == '/' && i+1 < len(src) && src[i+1] == '/':
			for i += 2; i < len(src) && src[i] != '\n'; i++ {
			}
		case src[i] == '/' && i+1 < len(src) && src[i+1] == '*':
			for i += 2; i+1 < len(src) && !(src[i] == '*' && src[i+1] == '/'); i++ {
			}
			if i+1 < len(src) {
				i += 2
			} else {
				i = len(src)
			}
		default:
			return i
		}
	}
	return i
}

// stripSwiftComments drops // and nested /* */ comments (strings kept) so import /* x */ SwiftUI cannot dodge the lock.
func stripSwiftComments(src string) string {
	var b strings.Builder
	for i := 0; i < len(src); {
		if src[i] == '"' || src[i] == '#' {
			j := skipSwiftString(src, i)
			b.WriteString(src[i:j])
			i = j
			continue
		}
		if src[i] == '/' && i+1 < len(src) && (src[i+1] == '/' || src[i+1] == '*') {
			b.WriteByte(' ') // comments are token separators; import/**/SwiftUI must not concatenate
			if src[i+1] == '/' {
				for i += 2; i < len(src) && src[i] != '\n'; i++ {
				}
				continue
			}
			depth := 1
			i += 2
			for depth > 0 {
				if i+1 >= len(src) {
					i = len(src)
					break
				}
				if src[i] == '/' && src[i+1] == '*' {
					depth++
					i += 2
				} else if src[i] == '*' && src[i+1] == '/' {
					depth--
					i += 2
				} else {
					i++
				}
			}
			continue
		}
		b.WriteByte(src[i])
		i++
	}
	return b.String()
}

// isPathLabel: `path` at i, bounded left by non-word, right by trivia then ':'; identifier tails never qualify.
func isPathLabel(src string, i int) bool {
	if i+4 > len(src) || src[i:i+4] != "path" || i > 0 && isWordByte(src[i-1]) { return false }
	j := skipTrivia(src, i+4)
	return j < len(src) && src[j] == ':'
}
func isWordByte(c byte) bool {
	return c == '_' || c >= '0' && c <= '9' || c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z'
}

// skipSwiftString: offset just past a "..." or #"..."# literal (any hashes, single/multiline); unterminated advances.
func skipSwiftString(src string, i int) int {
	start := i
	n := 0
	for i < len(src) && src[i] == '#' {
		n++
		i++
	}
	if i >= len(src) || src[i] != '"' { return start + 1 }
	multi := 0
	if strings.HasPrefix(src[i:], `"""`) { multi = 2 }
	i += 1 + multi
	for i < len(src) {
		if n == 0 && src[i] == '\\' {
			if multi == 2 && strings.HasPrefix(src[i:], `\"\"\"`) {
				i += 4
			} else {
				i += 2
			}
		} else if src[i] == '"' {
			if multi == 2 && i+3 <= len(src) && src[i+1] == '"' && src[i+2] == '"' &&
				i+3+n <= len(src) && strings.Trim(src[i+3:i+3+n], "#") == "" {
				return i + 3 + n
			}
			if multi == 0 && i+1+n <= len(src) && strings.Trim(src[i+1:i+1+n], "#") == "" { return i + 1 + n }
			i++
		} else if n == 0 && multi == 0 && src[i] == '\n' {
			return i + 1
		} else {
			i++
		}
	}
	return len(src)
}

// classifyPathValue evaluates the value after path:: single-line literals joined by + evaluate exactly, ending at , ) ] or EOF; other continuations/non-literals fail closed.
func classifyPathValue(src string, i int, p *manifestPath) int {
	pos := skipTrivia(src, i)
	if pos < len(src) && src[pos] == ':' { pos = skipTrivia(src, pos+1) }
	var parts []string
	for {
		pos = skipTrivia(src, pos)
		frag, ok := readStringFragment(src, pos)
		if !ok || strings.IndexByte(frag, '\\') >= 0 {
			*p = manifestPath{raw: snippet(src, pos)}
			return pos + 1
		}
		parts = append(parts, frag)
		end := skipTrivia(src, skipSwiftString(src, pos))
		if end >= len(src) || src[end] == ',' || src[end] == ')' || src[end] == ']' {
			v := strings.Join(parts, "")
			*p = manifestPath{val: v, raw: v, ok: true}
			return end
		}
		if src[end] != '+' {
			*p = manifestPath{raw: snippet(src, end)}
			return end + 1
		}
		pos = end + 1
	}
}

// readStringFragment reads one single-line normal/raw literal; multiline or unterminated: ok=false.
func readStringFragment(src string, i int) (content string, ok bool) {
	n := 0
	for i+n < len(src) && src[i+n] == '#' {
		n++
	}
	if i+n >= len(src) || src[i+n] != '"' { return "", false }
	if strings.HasPrefix(src[i+n:], `"""`) { return "", false }
	body := src[i:skipSwiftString(src, i)]
	if n == 0 {
		k := 1
		for k < len(body) && body[k] != '"' {
			if body[k] == '\\' { k++ }
			k++
		}
		if k >= len(body) || strings.IndexByte(body[:k], '\n') >= 0 { return "", false }
		return body[1:k], true
	}
	for k := n + 1; k+n <= len(body); k++ {
		if body[k-1] == '"' && strings.Trim(body[k:k+n], "#") == "" { return body[n+1 : k-1], true }
	}
	return "", false
}
func snippet(s string, i int) string {
	if len(s)-i <= 24 { return s[i:] }
	return s[i:i+24] + "..."
}

// checkProductionGoPurity: production Go never imports prototypes/**; lane Go never redefines protected behavior.
func checkProductionGoPurity(root string) error {
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.IsDir() {
			if skipMeta(d.Name()) { return fs.SkipDir }
			return nil
		}
		if filepath.Ext(path) != ".go" { return nil }
		// Production _test.go links lane imports into the package test binary: one-way rule applies.
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		b, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		text := string(b)
		inProto := inCanonicalPrototype(rel)
		if !inProto && goImportsPrototype(text) { return fmt.Errorf("%s: production Go must not import or require prototypes/**", rel) }
		if inProto && modifiesProtectedGo(text) { return fmt.Errorf("%s: prototype code may not modify protected production Go behavior", rel) }
		return nil
	})
}

// goImportsPrototype: real-grammar scan so grouped/comment-adjacent forms cannot hide the import; unparseable input fails closed.
func goImportsPrototype(text string) bool {
	const protoMod = "github.com/Dezocode/Sai/prototypes"
	lit := func(p string) bool {
		if p == "" || strings.ContainsAny(p, " 	()") { return false }
		return p == protoMod || strings.HasPrefix(p, protoMod+"/") ||
			p == "prototypes" || strings.HasPrefix(p, "prototypes/")
	}
	f, err := parser.ParseFile(token.NewFileSet(), "x.go", text, parser.ImportsOnly)
	if err != nil { return true } // unparseable input fails closed on the lane gate
	for _, im := range f.Imports {
		if p := strings.Trim(im.Path.Value, `"`+"`"); lit(p) { return true }
	}
	return false
}

// modifiesProtectedGo: ANY reference to the resolved loader symbol fails closed — (plugin.Open)(...), o := plugin.Open, ((plugin)).Open; unparseable fails closed (protected-file edits hit the diff gate).
func modifiesProtectedGo(text string) bool {
	f, err := parser.ParseFile(token.NewFileSet(), "x.go", text, 0)
	if err != nil { return true } // unparseable input fails closed on the protection gate
	alias, dot := "", false // local binding of the std "plugin" import
	for _, im := range f.Imports {
		if strings.Trim(im.Path.Value, `"`+"`") != "plugin" { continue }
		switch {
		case im.Name == nil:
			alias = "plugin"
		case im.Name.Name == ".":
			dot = true
		case im.Name.Name != "_":
			alias = im.Name.Name
		}
	}
	hooked := false
	ast.Inspect(f, func(n ast.Node) bool {
		switch d := n.(type) {
		case *ast.Ident:
			// Dot-imported binding: deferred, assigned, or called mentions all flag.
			hooked = hooked || dot && d.Name == "Open"
		case *ast.SelectorExpr:
			// plugin.Open via resolved/unbound alias, aliased p.Open, paren-unwrapped — all fail closed.
			if base, ok := ast.Unparen(d.X).(*ast.Ident); ok && d.Sel.Name == "Open" &&
				(base.Name == alias || base.Name == "plugin") {
				hooked = true
			}
		}
		return true
	})
	return hooked
}

// git runs git in root, returning trimmed stdout ("" on any failure); gates needing fail-closed errors call exec directly.
func git(root string, args ...string) string {
	b, _ := exec.Command("git", append([]string{"-c", "safe.directory=*", "-C", root}, args...)...).Output()
	return strings.TrimSpace(string(b))
}

// prototypeLaneViolation: a prototype-scoped change editing protected production Go (cmd/sai/**, internal/**) violates the contract; verifiers exempt.
func prototypeLaneViolation(changed []string) error {
	hasProto, touched := false, []string{}
	for _, f := range changed {
		if f == "prototypes" || strings.HasPrefix(f, "prototypes/") {
			hasProto = true
			continue
		}
		if strings.HasSuffix(f, ".go") && (strings.HasPrefix(f, "cmd/sai/") || strings.HasPrefix(f, "internal/")) { touched = append(touched, f) }
	}
	if hasProto && len(touched) > 0 { return fmt.Errorf("prototype-scoped change must not edit protected production Go: %s", strings.Join(touched, ", ")) }
	return nil
}

// checkPrototypeLaneDiff: prototype-scoped diff vs SAI_TRUSTED_BASE (or origin/main merge-base) must not edit protected Go; non-git trees skip, unresolvable bases fail, as does go.mod replaces routing imports into prototypes/.
func checkPrototypeLaneDiff(root string) error {
	if b, err := os.ReadFile(filepath.Join(root, "go.mod")); err == nil && moduleTargetsLane(root, string(b)) {
		return fmt.Errorf("go.mod: replace target must not live under %s", protoRoot)
	} else if err != nil && !os.IsNotExist(err) { return err }
	// Nested/vendored production go.mod files are lane-checked too (reviewer r1 transitive vector): a nested module's replace can alias the lane for workspace consumers even when the root go.mod is clean. Walk-discovered; canonical top-level prototypes/ tree and tooling metadata pruned; unreadable manifests fail closed.
	if err := filepath.WalkDir(root, func(np string, d fs.DirEntry, werr error) error {
		if werr != nil { return werr }
		if d.IsDir() {
			if np == filepath.Join(root, protoRoot) || skipMeta(d.Name()) { return fs.SkipDir }
			return nil
		}
		if d.Name() != "go.mod" || np == filepath.Join(root, "go.mod") { return nil }
		nb, nerr := os.ReadFile(np)
		if nerr != nil {
			return fmt.Errorf("%s: unreadable go.mod fails closed: %v", np, nerr)
		}
		if moduleTargetsLaneFrom(filepath.Dir(np), root, string(nb)) {
			return fmt.Errorf("%s: replace target must not live under %s", np, protoRoot)
		}
		return nil
	}); err != nil {
		return err
	}
	if git(root, "rev-parse", "--is-inside-work-tree") != "true" { return nil }
	base := os.Getenv("SAI_TRUSTED_BASE")
	if base == "" {
		if base = git(root, "merge-base", "origin/main", "HEAD"); base == "" { return fmt.Errorf("prototype lane: cannot resolve trusted base; set SAI_TRUSTED_BASE or fetch origin/main") }
	} else if git(root, "rev-parse", "--verify", base+"^{commit}") == "" { return fmt.Errorf("prototype lane: SAI_TRUSTED_BASE %q does not resolve to a commit", base) }
	diffRaw, derr := exec.Command("git", "-c", "safe.directory=*", "-C", root, "diff", "-M", "--name-status", "-z", base+"..HEAD").Output() // -z keeps spaced filenames intact; a failed invocation must FAIL closed, never pass as an empty diff (Saul 97328846218); -M --name-status exposes BOTH rename paths so moving protected Go into the lane cannot pass as prototype-only (Saul 97348395053)
	if derr != nil { return fmt.Errorf("prototype lane: trusted-base diff failed; failing closed: %w", derr) }
	changed, perr := parseNameStatusPaths(diffRaw)
	if perr != nil { return fmt.Errorf("prototype lane: trusted-base diff unparseable; failing closed: %w", perr) }
	return prototypeLaneViolation(changed)
}

// parseNameStatusPaths flattens `git diff -M --name-status -z` records into every affected path — BOTH sides of rename/copy records; malformed records fail closed.
func parseNameStatusPaths(raw []byte) ([]string, error) {
	f := strings.Split(string(raw), "\x00")
	fail := func(m string) ([]string, error) { return nil, fmt.Errorf("trusted-base diff %s; failing closed", m) }
	paths := []string{}
	for i := 0; i < len(f); i++ {
		st := f[i]
		if st == "" && i == len(f)-1 { return paths, nil } // trailing NUL record terminator (or an entirely empty diff)
		i++
		if st == "" || i >= len(f) || f[i] == "" { return fail(fmt.Sprintf("record %q lacks a path", st)) }
		paths = append(paths, f[i])
		if st[0] == 'R' || st[0] == 'C' { // rename/copy records carry origin AND destination
			i++
			if i >= len(f) || f[i] == "" { return fail(fmt.Sprintf("rename/copy %q lacks its origin path", st)) }
			paths = append(paths, f[i])
		}
	}
	return paths, nil
}

// moduleTargetsLane: go.mod replace targets resolving inside prototypes/ fail — single-line/block/quoted. Relative targets resolve against the go.mod dir; absolute targets are symlink-resolved, then judged against the canonical root (an outside alias into the lane fails); missing "=>"/malformed targets fail closed.
func moduleTargetsLane(root, src string) bool {
	return moduleTargetsLaneFrom(root, root, src)
}

// moduleTargetsLaneFrom: same grammar, but relative targets resolve against the given manifest dir (nested go.mod files resolve against their own directory, not the repo root).
func moduleTargetsLaneFrom(manifestDir, root, src string) bool {
	rootAbs2, rootErr := filepath.Abs(root)
	if rootErr != nil { // cannot anchor repo root: fail closed
		return true
	}
	lane := func(p string) bool {
		if p = strings.Trim(p, `"`+"`"); p == "" { return false }
		var s string
		if filepath.IsAbs(p) { // symlink-resolve first, then judge vs canonical root: an outside alias into the lane must fail (Saul 97279716328)
			absRoot, aerr := filepath.Abs(root)
			rootCanon, err := filepath.EvalSymlinks(absRoot)
			if aerr != nil || err != nil { return true } // unresolvable root fails closed
			tgt := filepath.Clean(p)
			if resolved, err := filepath.EvalSymlinks(tgt); err == nil { tgt = resolved } // dangling target: keep lexical path; walk/read gates fail closed on it elsewhere
			rel, err := filepath.Rel(rootCanon, tgt)
			if err != nil || strings.HasPrefix(rel, "..") || rel == "." { return false } // outside this repo (lexically or through symlinks): not a lane target
			s = "/" + filepath.ToSlash(rel)
		} else if base, berr := filepath.Abs(manifestDir); berr != nil { // Relative targets resolve against the manifest dir, NOT "/" (Saul 97328846218): traversal above it leaves the repo and stays legal.
			return true // unresolvable resolution basis fails closed
		} else { // Relative targets resolve against the manifest dir (Saul 97328846218), then the ABSOLUTE result is judged against the canonical root — a nested go.mod's ../../prototypes/plugins/author IS a lane target even though it escapes the manifest's own directory.
			cand := filepath.Clean(filepath.Join(base, p))
			rootCanon2, rerr := filepath.EvalSymlinks(rootAbs2)
			if rerr != nil {
				return true
			} // unresolvable root fails closed
			for d := cand; ; { // canonicalize via nearest existing ancestor: symlinked roots (macOS /var->/private/var) and missing leaves both judged against the resolved root
				if r, rr := filepath.EvalSymlinks(d); rr == nil { cand = filepath.ToSlash(filepath.Join(r, strings.TrimPrefix(cand, d))); break }
				u := filepath.Dir(d)
				if u == d { break }
				d = u
			}
			rel, relerr := filepath.Rel(filepath.ToSlash(rootCanon2), cand)
			if relerr != nil || strings.HasPrefix(rel, "..") || rel == "." {
				return false
			} // lands outside this repo: not a lane target
			s = "/" + filepath.ToSlash(rel)
		}
		return s == "/"+protoRoot || strings.HasPrefix(s, "/"+protoRoot+"/") ||
			s == "/prototypes" || strings.HasPrefix(s, "/prototypes/")
	}
	directive := func(t string) bool {
		eq := strings.Index(t, "=>")
		if eq < 0 { return true } // replace without target fails closed
		rhs := t[eq+2:]
		if j := strings.LastIndex(rhs, "//"); j >= 0 { rhs = rhs[:j] } // trailing comment
		f := strings.Fields(rhs)
		if len(f) != 1 && len(f) != 2 { // path, or module path plus version
			return true // malformed target fails closed
		}
		return lane(f[0])
	}
	inBlock := false
	for _, line := range strings.Split(src, "\n") {
		t := strings.TrimSpace(line)
		if inBlock {
			if strings.HasPrefix(t, ")") {
				inBlock = false
			} else if t != "" && directive(t) { return true }
			continue
		}
		if !strings.HasPrefix(t, "replace") || len(t) > 7 && isWordByte(t[7]) { continue } // "replacex..." is an identifier, not the directive
		if rest := strings.TrimSpace(strings.TrimPrefix(t, "replace")); rest == "" {
			continue
		} else if strings.HasPrefix(rest, "(") {
			inBlock = !strings.HasSuffix(rest, ")") // closure tracking: EOF while open fails closed (Saul 97348395053); single-line block "replace (A => ./p)" closes here
			if s := strings.TrimSpace(strings.TrimSuffix(strings.TrimPrefix(rest, "("), ")")); s != "" && directive(s) { return true }
		} else if directive(rest) { return true }
	}
	return inBlock // unterminated replace block at EOF fails closed even when every scanned entry is lane-free (Saul 97348395053)
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
	for _, gate := range []func(string) error{checkProductionManifests, checkGoWorkFiles, checkProductionGoPurity, checkPrototypeLaneDiff} {
		if err := gate(root); err != nil { return err }
	}
	if err := checkSymlinkEscape(root); err != nil { return err }
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.IsDir() {
			if skipMeta(d.Name()) { return fs.SkipDir }
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
		inProto := inCanonicalPrototype(rel)
		if inProto && !c.FeatureUIAllowed && inPluginDesignScope(rel) { return nil }
		scope := "outside SaiDesignLanguage"
		if inProto && !c.FeatureUIAllowed { scope += " and PrototypeDesign scope" }
		for _, rule := range forbidden {
			if rule.re.MatchString(text) { return fmt.Errorf("%s: %s %s", rel, rule.name, scope) }
		}
		if !c.FeatureUIAllowed {
			shell := rel == macShell || rel == iosShell
			if !inProto && !shell && (swiftUIImport.MatchString(stripSwiftComments(text)) || strings.Contains(text, "SaiText") || strings.Contains(text, "SaiCanvas")) { return fmt.Errorf("%s: import SwiftUI is locked while design status=%s", rel, c.Status) }
			if shell && (strings.Count(text, "SaiCanvas") != 1 || strings.Count(text, "SaiText") != 1 || !shellBody.MatchString(text) || shellUI.MatchString(text)) { return fmt.Errorf("%s: shell composition", rel) }
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
