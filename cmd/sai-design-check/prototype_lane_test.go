package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

// patchContract decodes the contract JSON beneath root, applies patch, writes it back.
func patchContract(t *testing.T, root string, patch func(map[string]interface{})) {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(root, "design/sai-design-language.json"))
	if err != nil {
		t.Fatal(err)
	}
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil {
		t.Fatal(err)
	}
	patch(m)
	if b, err = json.Marshal(m); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.json"), b, 0644); err != nil {
		t.Fatal(err)
	}
}

// lockedFixture: repo fixture locked to production (featureUIAllowed=false in JSON and Swift source).
func lockedFixture(t *testing.T) string {
	t.Helper()
	root := fixture(t, true, "")
	patchContract(t, root, func(m map[string]interface{}) { m["featureUIAllowed"] = false })
	writeRel(t, root, designAuth+"/SaiDesignLanguage.swift", authoritySwift(false))
	return root
}

func writeRel(t *testing.T, root, rel, src string) {
	t.Helper()
	p := filepath.Join(root, rel)
	if os.MkdirAll(filepath.Dir(p), 0755) == nil && os.WriteFile(p, []byte(src), 0644) == nil {
		return
	}
	t.Fatal("writeRel " + rel)
}

const protoView = "import SwiftUI\nstruct AuthorEditor: View {\n    var body: some View {\n        VStack { Text(\"Author\") }\n    }\n}\n"

const expTokens = "let experiment = \"#FF00AA\"\n"

// mustFail: rel→src on a fresh locked fixture must fail; mustPass is the inverse over a file set.
func mustFail(t *testing.T, rel, src string) {
	t.Helper()
	root := lockedFixture(t)
	writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
	writeRel(t, root, rel, src)
	if err := check(root); err == nil {
		t.Fatalf("expected %s to fail", rel)
	}
}

func mustPass(t *testing.T, files map[string]string) {
	t.Helper()
	root := lockedFixture(t)
	for rel, src := range files {
		writeRel(t, root, rel, src)
	}
	if err := check(root); err != nil {
		t.Fatalf("expected pass, got: %v", err)
	}
}

// SwiftUI lock + PrototypeDesign boundaries: lookalikes fail.
func TestPrototypeSwiftUIBoundariesFail(t *testing.T) {
	for _, tc := range []struct{ rel, src string }{
		{featureRoot + "/Dash.swift", "import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {featureRoot + "/Dash.swift", "import /* sneaky */ SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {featureRoot + "/Dash.swift", "import/**/SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {"prototypes/plugins-evil/Evil.swift", protoView}, {"prototypes/plugin/NotEvil.swift", protoView}, {"prototype/plugins/AlsoWrong.swift", protoView}, {"prototypes/plugins/author/Editor.swift", protoView + ".padding(17)\n"}, {"prototypes/plugins/Evil.swift", protoView}, {"prototypes/plugins-evil/PrototypeDesign/Tokens.swift", expTokens}, {"prototype/plugins/x/PrototypeDesign/Tokens.swift", expTokens}, {"prototypes/plugins/author/views/PrototypeDesign/Tokens.swift", expTokens},
	} {
		mustFail(t, tc.rel, tc.src)
	}
	// Access-modified imports (Saul P1 @7b67330): every modifier/attr form locks exactly like plain `import SwiftUI`.
	for _, mod := range []string{"open", "public", "package", "internal", "fileprivate", "private"} {
		mustFail(t, featureRoot+"/Dash.swift", mod+" import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n")
	}
	mustFail(t, featureRoot+"/Dash.swift", "@available(macOS 13, *)\nfileprivate import SwiftUI\n")
	mustFail(t, featureRoot+"/Dash.swift", "let x = 1; public import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n")
	// Access-modified non-SwiftUI imports stay legal (lockedFixture is production-locked, so only SwiftUI trips).
}

// Exemptions hold only in the canonical lane: plain prototype SwiftUI, PrototypeDesign experiments, one-way reuse of stable production Go.
func TestPrototypeExemptionsPass(t *testing.T) {
	mustPass(t, map[string]string{
		"prototypes/plugins/author/Editor.swift": protoView, "prototypes/plugins/author/PrototypeDesign/Tokens.swift": expTokens, "prototypes/plugins/author/PrototypeDesign/nested/deep/Tokens.swift": expTokens, "prototypes/plugins/author/bridge.go": "package author\nimport _ \"github.com/Dezocode/Sai/internal/app\"\nvar _ = 1\n", "prototypes/plugins/author/fs.go": "package author\nimport \"os\"\nvar _ = os.Open\n", "prototypes/plugins/author/init.go": "package author\nfunc init() {}\n", // bare init is legal lane Go
		featureRoot + "/Dash.swift": "public import Foundation\nlet dash = 1\n", // access-modified non-UI import stays legal
	})
}

// Production _test.go never skips the purity gate (STEER 97234516350): lane imports there fail; lane-free test files stay legal.
func TestProductionTestGoCannotImportLane(t *testing.T) {
	mustFail(t, "internal/app/leak_test.go",
		"package app\n\nimport (\n\t\"testing\"\n\n\t_ \"github.com/Dezocode/Sai/prototypes/plugins/author\"\n)\n\nfunc TestLeak(t *testing.T) {}\n")
	mustFail(t, "cmd/sai/tool_test.go", "package main\nimport _ `github.com/Dezocode/Sai/prototypes`\n")
	root := lockedFixture(t)
	writeRel(t, root, "internal/app/clean_test.go", "package app\n\nimport \"testing\"\n\nfunc TestClean(t *testing.T) {}\n")
	if err := check(root); err != nil {
		t.Fatalf("lane-free production test file must pass: %v", err)
	}
}

func TestInCanonicalPrototypeFailsClosed(t *testing.T) {
	for _, tc := range []struct {
		rel  string
		want bool
	}{{"prototypes/plugins/author/Editor.swift", true}, {"prototypes/plugins/x/y/z.swift", true}, {"prototypes/plugins", false}, {"prototypes/plugins-evil/x.swift", false}, {"prototypes/plugin/x.swift", false}, {"prototype/plugins/x.swift", false}, {"prototypes/plugins/../plugins-evil/x.swift", false}, {"../prototypes/plugins/x.swift", false}, {"/prototypes/plugins/x.swift", false}, {"Prototypes/plugins/x.swift", false}, {"prototypes/plugins/Evil.swift", false}, {"prototypes/plugins//x.swift", false}, {"prototypes/plugins/author", false}} {
		if got := inCanonicalPrototype(tc.rel); got != tc.want {
			t.Fatalf("inCanonicalPrototype(%q) = %v, want %v", tc.rel, got, tc.want)
		}
	}
}

func TestStripSwiftComments(t *testing.T) {
	cases := map[string]string{
		"import /* x */ SwiftUI": "import   SwiftUI", "import /* a /* b */ c */ SwiftUI": "import   SwiftUI", "import // line\n SwiftUI": "import  \n SwiftUI", "import/**/SwiftUI": "import SwiftUI", `let s = "import /* not */ SwiftUI"`: `let s = "import /* not */ SwiftUI"`,
	}
	for in, want := range cases {
		if got := stripSwiftComments(in); got != want {
			t.Fatalf("stripSwiftComments(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestCandidateJSONCannotRelocatePrototypeRoot(t *testing.T) {
	root := lockedFixture(t)
	writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
	// Candidate nominates its own prototype root and moves pinned design authority: verifier-owned root ignored, pinned paths fail.
	patchContract(t, root, func(m map[string]interface{}) {
		m["prototypeRoot"] = "evil/plugins"
		m["codePolicy"].(map[string]interface{})["swiftDesignAuthorityPath"] = "evil/design"
	})
	if err := check(root); err == nil {
		t.Fatal("pinned codePolicy paths must fail closed when tampered")
	}
}

// Classifier: single-line literals (+ chains) evaluate exactly; vars, calls, interpolation, escapes, multiline, unterminated fail closed.
func TestManifestPathValueClassifier(t *testing.T) {
	exact := map[string]string{`path: "Sources/X"`: "Sources/X", `path:#"Raw/X"#`: "Raw/X", `path: ###"Hashed/X"###`: "Hashed/X", `path: "A/" + "B" + "C"`: "A/BC", `path: #"a"# +#"b"#`: "ab", `path /* c */ : /* d */ "W"`: "W"}
	for src, want := range exact {
		got := manifestPaths(src)
		if len(got) != 1 || !got[0].ok || got[0].val != want {
			t.Fatalf("%q classified %+v, want exactly %q", src, got, want)
		}
	}
	failed := []string{
		`path: dir`, `path: resolve("x")`, `path: "a" + var`, `path: "a" + f("b")`, `path: "A\(x)"`, `path: #"A\#(x)"#`, `path: "a\u{2F}b"`, "path: \"a\u005ctb\"", `path: "unterminated\`, "path: \"\"\"multi\nline\"\"\"", `somePath: "x"`, `nodePath: "y"`, `path: /* unterminated`, // unterminated comment must not panic the scanner
	}
	for _, src := range failed {
		for _, p := range manifestPaths(src) {
			if p.ok {
				t.Fatalf("%q must fail closed, got %+v", src, p)
			}
		}
	}
	hidden := []string{
		`// path: "z"`, "// .target(name: \"x\", path: \"../../../prototypes/plugins/author\")\n", `/* path: "w" */`, `let s = "path: not-a-declaration"`,
	}
	for _, src := range hidden {
		if got := manifestPaths(src); len(got) != 0 {
			t.Fatalf("%q must yield no declarations, got %+v", src, got)
		}
	}
}

// E2E manifest gate: lane-referencing declarations fail wherever the walk finds them; non-declarations/outside-lane paths never trip.
func TestProductionManifestGateEndToEnd(t *testing.T) {
	for _, tc := range []struct {
		file, src string
		wantFail  bool
	}{
		{"apps/apple/Package.swift", "let pkg = Package(name: \"x\", path: \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: #\"../../../../prototypes/plugins/author\"#)\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: \"../../../../prototypes/./plugins/author\")\n", true}, {"apps/apple/Package.swift", ".target(name: \"x\", path /* c */ : \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: \"../../../../prototypes/plugins\")\n", true}, {"apps/apple/Package.swift", "let p = \"../../../prototypes/plugins/author\"\n.target(name: \"x\", path: p)\n", true},
		{"apps/apple/Package.swift", ".target(name: \"x\", path: \"../../..\" + \"/prototypes/plugins/author\")\n", true}, {"apps/apple/Package.swift", ".target(name: \"x\", path: \"safe\".appending(\"/../../../prototypes/plugins/author\"))\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let doc = #\"\"\"\nraw multiline before a lane path\n\"\"\"#\n.target(name: \"x\", path: \"../../../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"../../../../xprototypes/plugins/author\")\n", false},
		// Walk discovery (STEER 97251286237 residue): unlisted/nested/vendored manifests cannot bypass the gate.
		{"apps/apple/Packages/NestedKit/Sources/deep/Package.swift", ".target(name: \"x\", path: \"../../../../../../../prototypes/plugins/author\")\n", true}, {"third_party/vendored/Package.swift", "let pkg = Package(name: \"v\", path: \"../../../prototypes/plugins/author\")\n", true},
		{"third_party/prototypes/Package.swift", "let pkg = Package(name: \"v\", path: \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/prototypes/Sources/deep/Package.swift", ".target(name: \"x\", path: \"../../../../../../prototypes/plugins/author\")\n", true}, {"third_party/prototypes/Package.swift", "let pkg = Package(name: \"v\", path: \"Sources/V\")\n", false}, // Saul 97279716328: vendored/nested trees NAMED prototypes stay inspected; only the canonical top-level lane tree is pruned
		// The lane's own manifests are pruned from the walk: plugin packages legitimately reference their parent tree.
		{"prototypes/plugins/author/Package.swift", "let pkg = Package(name: \"a\", path: \"../..\")\n", false}, {"apps/apple/Packages/SaiKit/Package.swift", "let doc = \"\"\"\npath: \"../../../../prototypes/plugins/author\" is only prose\n\"\"\"\nlet pkg = Package(name: \"x\", path: \"Sources/Safe\")\n", false}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"%s/prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"%s/prototypes\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"/opt/vendor/Lib\")\n", false},
	} {
		root := lockedFixture(t)
		writeRel(t, root, tc.file, strings.ReplaceAll(tc.src, "%s", root))
		if err := check(root); (err == nil) == tc.wantFail {
			t.Fatalf("%s: wantFail=%v, got err=%v\n%s", tc.file, tc.wantFail, err, tc.src)
		}
	}
	root := lockedFixture(t)
	if err := checkProductionGoPurity(root); err != nil {
		t.Fatalf("clean tree must pass purity: %v", err)
	}
	if err := checkProductionManifests(root); err != nil {
		t.Fatalf("clean tree must pass manifests: %v", err)
	}
	// Walk fail-closed wiring: an unwalkable root is an unverifiable tree, not a pass.
	if err := checkProductionManifests(filepath.Join(root, "no", "such")); err == nil {
		t.Fatal("unwalkable root must fail closed")
	}
}

// Absolute manifest values resolve vs the repo root (incl. symlinked ancestors of missing leaves); unresolvable homes fail closed.
func TestAbsoluteManifestResolution(t *testing.T) {
	root := lockedFixture(t)
	if os.MkdirAll(filepath.Join(root, "prototypes/plugins/author"), 0755) != nil || os.Symlink(filepath.Join(root, "prototypes"), filepath.Join(root, "proto-link")) != nil {
		t.Fatal("fixture")
	}
	t.Setenv("HOME", root)
	for _, tc := range []struct {
		v   string
		hit bool
	}{
		{root + "/prototypes/plugins/author", true}, {"~/prototypes/plugins/author", true}, {root + "/proto-link/plugins/author2", true}, // dead leaf behind symlinked ancestor must still hit
		{root + "/does/not/exist", false}, {"/opt/vendor/Lib", false},
	} {
		if resolvesInto(root, "apps/apple/Package.swift", tc.v) != tc.hit {
			t.Fatalf("resolvesInto(%q) want %v", tc.v, tc.hit)
		}
	}
	t.Setenv("HOME", "")
	if !resolvesInto(root, "apps/apple/Package.swift", "~x/plugin") {
		t.Fatal("unresolvable home must fail closed")
	}
}

// Import classifier flags real lane-naming import specs in any legal placement; comments/strings/near-prefixes never trip it.
func TestGoImportClassifier(t *testing.T) {
	hit := []string{
		"package app\nimport _ \"github.com/Dezocode/Sai/prototypes/plugins/author\"\n", "package app\nimport _ `prototypes/plugins/author`\n", "package app\nimport (\n	_ \"a\"\n	_ \"prototypes/plugins/author\"\n)\n", "package app\nimport\n	_ \"prototypes/plugins/author\"\n", "package app\n/* c */import _ \"prototypes/plugins/author\"\n", "package app; import _ \"prototypes/plugins/author\"\n", "package app\nimport \"github.com/Dezocode/Sai/internal/app\"; import _ \"prototypes/plugins/author\"\n",
	}
	for _, src := range hit {
		if !goImportsPrototype(src) {
			t.Fatalf("classifier missed lane import:\n%s", src)
		}
	}
	// One representative drives the end-to-end wiring; per-placement fixtures duplicate TestProductionTestGoCannotImportLane.
	root := lockedFixture(t)
	writeRel(t, root, "internal/app/leak.go", hit[0])
	if err := check(root); err == nil {
		t.Fatal("production Go lane import must fail end-to-end")
	}
	miss := []string{
		"package app\n\n// doc: prototypes/plugins/author is documented here.\nvar note = \"prototypes/plugins/author\"\n", "package app\nvar s = \"import _ \\\"prototypes/plugins/author\\\"\"\n", "package app\nimport \"fmt\"\n",
	}
	for _, src := range miss {
		if goImportsPrototype(src) {
			t.Fatalf("classifier flagged non-import mention:\n%s", src)
		}
	}
	root = lockedFixture(t)
	writeRel(t, root, "internal/app/doc.go", miss[0])
	if err := check(root); err != nil {
		t.Fatalf("non-import mention must not trip the gate: %v", err)
	}
}

func TestPrototypeGoCannotModifyProtectedProduction(t *testing.T) {
	for _, src := range []string{
		"package author\nimport \"plugin\"\nfunc x() { plugin.Open(\"\") }\n",
		// comments between tokens and aliased/dot-imported Open are valid Go.
		"package author\nimport pl \"plugin\"\nfunc x() { pl.Open(\"\") }\n", "package author\nimport . \"plugin\"\nfunc y() { Open(\"\") }\n", "package author\nfunc z() { plugin.Open(\"\") }\n", // unbound plugin.Open fails closed
		"package author\nimport \"plugin\"\nfunc x() { (plugin.Open)(\"\") }\n", "package author\nimport \"plugin\"\nfunc x() { o := plugin.Open; o(\"\") }\n", "package author\nimport pl \"plugin\"\nfunc x() { f := pl.Open; f(\"\") }\n", "package author\nimport \"plugin\"\nfunc x() { ((plugin)).Open(\"\") }\n",
	} {
		mustFail(t, "prototypes/plugins/author/hook.go", src)
	}
}

// Symlink redirects/lane reach fail closed; production aliases stay legal.
func TestSymlinkEscapeFailsClosed(t *testing.T) {
	cases := []struct {
		at, target string
		legal      bool
	}{
		{"prototypes/plugins/author/link.go", "apps/apple/Packages/SaiKit/Sources/SaiFoundation/outside.go", false}, {"prototypes/plugins", "", false}, {"prototypes", "", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/alias.swift", "prototypes/plugins/author/Editor.swift", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/aliased", "prototypes/plugins/author", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/alias.go", "apps/apple/Packages/SaiKit/Sources/SaiFoundation/real.go", true},
	}
	for _, tc := range cases {
		root := lockedFixture(t)
		writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
		link := filepath.Join(root, tc.at)
		os.MkdirAll(filepath.Dir(link), 0755)
		target := tc.target
		switch {
		case target == "":
			os.RemoveAll(link)
			target = t.TempDir()
		case strings.HasPrefix(target, "prototypes/"):
			target = filepath.Join(root, target)
		default:
			writeRel(t, root, target, "package foundation\n")
			target = filepath.Join(root, target)
		}
		if err := os.Symlink(target, link); err != nil {
			t.Skipf("symlinks unavailable: %v", err)
		}
		if err := check(root); (err == nil) != tc.legal {
			t.Fatalf("symlink %s -> %q: want legal=%v, got err=%v", tc.at, target, tc.legal, err)
		}
	}
}

// Verifier's own source mentions lane paths only as string data: real imports/bare init() absent.
func TestVerifierSourceNotSelfFlagged(t *testing.T) {
	b, err := os.ReadFile("main.go")
	if err != nil || goImportsPrototype(string(b)) || strings.Contains(string(b), "\nfunc init()") {
		t.Fatal("verifier source unreadable or self-triggers the gates")
	}
}

func TestPrototypeLaneDiffGate(t *testing.T) {
	fail := [][]string{
		{"prototypes/plugins/author/Editor.swift", "internal/app/app.go"}, {"prototypes/plugins/author/bridge.go", "cmd/sai/main.go"}, {"prototypes/x.go", "internal/app/app_test.go"},
		{"prototypes/plugins/author/x.go", "internal/app dir/evil.go"}, {"prototypes/plugins/author/y.go", "cmd/sai/tool dir/main.go"}, // -z handling: a space must not let whitespace splitting drop the .go suffix.
	}
	for _, c := range fail {
		if err := prototypeLaneViolation(c); err == nil {
			t.Fatalf("expected lane violation for %v", c)
		}
	}
	pass := [][]string{
		{"prototypes/plugins/author/Editor.swift"}, {"internal/app/app.go"}, {"prototypes/plugins/author/x.go", "cmd/sai-design-check/main.go"}, // prod-only PR passes; verifiers are not protected production Go
	}
	for _, c := range pass {
		if err := prototypeLaneViolation(c); err != nil {
			t.Fatalf("expected pass for %v: %v", c, err)
		}
	}
	// E2E wiring through check(): STEER counterexample (proto PR editing internal/**, zero init()/plugin.Open) fails.
	root := lockedFixture(t)
	gitc := func(a ...string) string {
		t.Helper()
		o, err := exec.Command("git", append([]string{"-C", root}, a...)...).CombinedOutput()
		if err != nil {
			t.Fatalf("git %v: %v", a, err)
		}
		return strings.TrimSpace(string(o))
	}
	gitc("init", "-q")
	gitc("-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-qm", "base")
	os.Setenv("SAI_TRUSTED_BASE", gitc("rev-parse", "HEAD"))
	defer os.Unsetenv("SAI_TRUSTED_BASE")
	writeRel(t, root, "prototypes/plugins/author/bridge.go", "package author\nvar x = 1\n")
	writeRel(t, root, "internal/app/app.go", "package app\nvar bumped = 1\n")
	gitc("add", "-A")
	gitc("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "touch")
	if err := check(root); err == nil {
		t.Fatal("prototype-scoped change editing internal/** must fail")
	}
}
func TestModuleReplaceIntoLaneFails(t *testing.T) {
	root := lockedFixture(t) // resolution basis; moduleTargetsLane reads no disk
	parent := t.TempDir()    // Saul 97279716328: absolute targets are judged AFTER symlink resolution — an outside alias into the lane must fail
	if os.MkdirAll(filepath.Join(root, "prototypes", "plugins", "author"), 0755) != nil || os.Symlink(filepath.Join(root, "prototypes", "plugins", "author"), filepath.Join(parent, "alias")) != nil {
		t.Fatal("fixture")
	}
	hit := []string{
		"module m\nreplace github.com/evil/bad => ../prototypes/plugins/author\n", "replace example.com/x => ./prototypes/plugins/author\n", "replace (\n	A => prototypes/plugins/author\n	B => ./prototypes\n)\n", "replace e.com/x => \"../prototypes/../prototypes/plugins/author\" // pinned\n", "replacex y\nreplace e.com/x => prototypes/plugins/author", "replace (e.com/x => ./prototypes/author)", // single-line block form
		// Absolute targets resolve against the repo root (STEER 97234516350): rooted paths must not evade via ../.
		"module m\nreplace github.com/evil/bad => " + filepath.Join(root, "prototypes/plugins/author") + "\n", "replace e.com/x => \"" + filepath.Join(root, "prototypes") + "\"\n", "replace e.com/x => " + filepath.Join(parent, "alias") + "\n",
	}
	for _, src := range hit {
		if !moduleTargetsLane(root, src) {
			t.Fatalf("expected lane replace to fail closed:\n%s", src)
		}
	}
	miss := []string{
		"// replace e.com/x => prototypes/plugins/author is only a comment\n", "there is no replace of anything into prototypes/plugins here\n", "replace e.com/x => ../vendor/some/module v1.0.0\n", "replace e.com/x => ./internal/gen v0.0.0\n", "replace e.com/x => /opt/elsewhere/module v1.0.0\n", // absolute, outside the repo
		"replace e.com/x => \"..\"\n",                       // repo parent is not the lane
		"replace e.com/x => " + parent + "\n",               // a real outside directory stays legal
		"replace e.com/x => " + filepath.Clean(root) + "\n", // repo root itself is not a lane target
	}
	for _, src := range miss {
		if moduleTargetsLane(root, src) {
			t.Fatalf("non-lane content must not trip the guard:\n%s", src)
		}
	}
	// End-to-end: tampered go.mod with an ABSOLUTE lane target fails check().
	writeRel(t, root, "go.mod", "module m\nreplace e.com/x => "+filepath.Join(root, "prototypes/plugins/author")+"\n")
	if err := check(root); err == nil {
		t.Fatal("go.mod replace into the lane must fail check()")
	}
}
