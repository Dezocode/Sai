package main
import ("encoding/json"; "os"; "os/exec"; "path/filepath"; "strings"; "testing")
func patchContract(t *testing.T, root string, patch func(map[string]interface{})) {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(root, "design/sai-design-language.json"))
	if err != nil { t.Fatal(err) }
	var m map[string]interface{}
	if err := json.Unmarshal(b, &m); err != nil { t.Fatal(err) }
	patch(m)
	if b, err = json.Marshal(m); err != nil { t.Fatal(err) }
	if err := os.WriteFile(filepath.Join(root, "design/sai-design-language.json"), b, 0644); err != nil { t.Fatal(err) }
}
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
	if os.MkdirAll(filepath.Dir(p), 0755) == nil && os.WriteFile(p, []byte(src), 0644) == nil { return }
	t.Fatal("writeRel " + rel)
}
const protoView = "import SwiftUI\nstruct AuthorEditor: View {\n    var body: some View {\n        VStack { Text(\"Author\") }\n    }\n}\n"
const expTokens = "let experiment = \"#FF00AA\"\n"
func mustFail(t *testing.T, rel, src string) {
	t.Helper()
	root := lockedFixture(t)
	writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
	writeRel(t, root, rel, src)
	if err := check(root); err == nil { t.Fatalf("expected %s to fail", rel) }
}
func mustPass(t *testing.T, files map[string]string) {
	t.Helper()
	root := lockedFixture(t)
	for rel, src := range files { writeRel(t, root, rel, src) }
	if err := check(root); err != nil { t.Fatalf("expected pass, got: %v", err) }
}
func TestPrototypeSwiftUIBoundariesFail(t *testing.T) {
	for _, tc := range []struct{ rel, src string }{
		{featureRoot + "/Dash.swift", "import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {featureRoot + "/Dash.swift", "import /* sneaky */ SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {featureRoot + "/Dash.swift", "import/**/SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n"}, {"prototypes/plugins-evil/Evil.swift", protoView}, {"prototypes/plugin/NotEvil.swift", protoView}, {"prototype/plugins/AlsoWrong.swift", protoView}, {"prototypes/plugins/author/Editor.swift", protoView + ".padding(17)\n"}, {"prototypes/plugins/Evil.swift", protoView}, {"prototypes/plugins-evil/PrototypeDesign/Tokens.swift", expTokens}, {"prototype/plugins/x/PrototypeDesign/Tokens.swift", expTokens}, {"prototypes/plugins/author/views/PrototypeDesign/Tokens.swift", expTokens},
	} { mustFail(t, tc.rel, tc.src) }
	for _, mod := range []string{"open", "public", "package", "internal", "fileprivate", "private"} { mustFail(t, featureRoot+"/Dash.swift", mod+" import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n") }
	mustFail(t, featureRoot+"/Dash.swift", "@available(macOS 13, *)\nfileprivate import SwiftUI\n")
	mustFail(t, featureRoot+"/Dash.swift", "let x = 1; public import SwiftUI\nstruct Dash: View { var body: some View { Text(\"d\") } }\n")
}
func TestPrototypeExemptionsPass(t *testing.T) {
	mustPass(t, map[string]string{
		"prototypes/plugins/author/Editor.swift": protoView, "prototypes/plugins/author/PrototypeDesign/Tokens.swift": expTokens, "prototypes/plugins/author/PrototypeDesign/nested/deep/Tokens.swift": expTokens, "prototypes/plugins/author/bridge.go": "package author\nimport _ \"github.com/Dezocode/Sai/internal/app\"\nvar _ = 1\n", "prototypes/plugins/author/fs.go": "package author\nimport \"os\"\nvar _ = os.Open\n", "prototypes/plugins/author/init.go": "package author\nfunc init() {}\n",
		featureRoot + "/Dash.swift": "public import Foundation\nlet dash = 1\n",
	})
}
func TestProductionTestGoCannotImportLane(t *testing.T) {
	mustFail(t, "internal/app/leak_test.go", "package app\n\nimport (\n\t\"testing\"\n\n\t_ \"github.com/Dezocode/Sai/prototypes/plugins/author\"\n)\n\nfunc TestLeak(t *testing.T) {}\n")
	mustFail(t, "cmd/sai/tool_test.go", "package main\nimport _ `github.com/Dezocode/Sai/prototypes`\n")
	root := lockedFixture(t)
	writeRel(t, root, "internal/app/clean_test.go", "package app\n\nimport \"testing\"\n\nfunc TestClean(t *testing.T) {}\n")
	if err := check(root); err != nil { t.Fatalf("lane-free production test file must pass: %v", err) }
}
func TestInCanonicalPrototypeFailsClosed(t *testing.T) {
	for _, tc := range []struct{ rel string; want bool }{{"prototypes/plugins/author/Editor.swift", true}, {"prototypes/plugins/x/y/z.swift", true}, {"prototypes/plugins", false}, {"prototypes/plugins-evil/x.swift", false}, {"prototypes/plugin/x.swift", false}, {"prototype/plugins/x.swift", false}, {"prototypes/plugins/../plugins-evil/x.swift", false}, {"../prototypes/plugins/x.swift", false}, {"/prototypes/plugins/x.swift", false}, {"Prototypes/plugins/x.swift", false}, {"prototypes/plugins/Evil.swift", false}, {"prototypes/plugins//x.swift", false}, {"prototypes/plugins/author", false}} {
		if got := inCanonicalPrototype(tc.rel); got != tc.want { t.Fatalf("inCanonicalPrototype(%q) = %v, want %v", tc.rel, got, tc.want) }
	}
}
func TestStripSwiftComments(t *testing.T) {
	cases := map[string]string{"import /* x */ SwiftUI": "import   SwiftUI", "import /* a /* b */ c */ SwiftUI": "import   SwiftUI", "import // line\n SwiftUI": "import  \n SwiftUI", "import/**/SwiftUI": "import SwiftUI", `let s = "import /* not */ SwiftUI"`: `let s = "import /* not */ SwiftUI"`}
	for in, want := range cases { if got := stripSwiftComments(in); got != want { t.Fatalf("stripSwiftComments(%q) = %q, want %q", in, got, want) } }
}
func TestCandidateJSONCannotRelocatePrototypeRoot(t *testing.T) {
	root := lockedFixture(t)
	writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
	patchContract(t, root, func(m map[string]interface{}) { m["prototypeRoot"] = "evil/plugins"; m["codePolicy"].(map[string]interface{})["swiftDesignAuthorityPath"] = "evil/design" })
	if err := check(root); err == nil { t.Fatal("pinned codePolicy paths must fail closed when tampered") }
}
func TestManifestPathValueClassifier(t *testing.T) {
	exact := map[string]string{`path: "Sources/X"`: "Sources/X", `path:#"Raw/X"#`: "Raw/X", `path: ###"Hashed/X"###`: "Hashed/X", `path: "A/" + "B" + "C"`: "A/BC", `path: #"a"# +#"b"#`: "ab", `path /* c */ : /* d */ "W"`: "W"}
	for src, want := range exact { got := manifestPaths(src); if len(got) != 1 || !got[0].ok || got[0].val != want { t.Fatalf("%q classified %+v, want exactly %q", src, got, want) } }
	for _, src := range []string{`path: dir`, `path: resolve("x")`, `path: "a" + var`, `path: "a" + f("b")`, `path: "A\(x)"`, `path: #"A\#(x)"#`, `path: "a\u{2F}b"`, "path: \"a\u005ctb\"", `path: "unterminated\`, "path: \"\"\"multi\nline\"\"\"", `somePath: "x"`, `nodePath: "y"`, `path: /* unterminated`} {
		for _, p := range manifestPaths(src) { if p.ok { t.Fatalf("%q must fail closed, got %+v", src, p) } }
	}
	for _, src := range []string{`// path: "z"`, "// .target(name: \"x\", path: \"../../../prototypes/plugins/author\")\n", `/* path: "w" */`, `let s = "path: not-a-declaration"`} {
		if got := manifestPaths(src); len(got) != 0 { t.Fatalf("%q must yield no declarations, got %+v", src, got) }
	}
}
func TestProductionManifestGateEndToEnd(t *testing.T) {
	for _, tc := range []struct{ file, src string; wantFail bool }{
		{"apps/apple/Package.swift", "let pkg = Package(name: \"x\", path: \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: #\"../../../../prototypes/plugins/author\"#)\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: \"../../../../prototypes/./plugins/author\")\n", true}, {"apps/apple/Package.swift", ".target(name: \"x\", path /* c */ : \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", ".target(name: \"x\", path: \"../../../../prototypes/plugins\")\n", true}, {"apps/apple/Package.swift", "let p = \"../../../prototypes/plugins/author\"\n.target(name: \"x\", path: p)\n", true},
		{"apps/apple/Package.swift", ".target(name: \"x\", path: \"../../..\" + \"/prototypes/plugins/author\")\n", true}, {"apps/apple/Package.swift", ".target(name: \"x\", path: \"safe\".appending(\"/../../../prototypes/plugins/author\"))\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let doc = #\"\"\"\nraw multiline before a lane path\n\"\"\"#\n.target(name: \"x\", path: \"../../../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"../../../../xprototypes/plugins/author\")\n", false},
		{"apps/apple/Packages/NestedKit/Sources/deep/Package.swift", ".target(name: \"x\", path: \"../../../../../../../prototypes/plugins/author\")\n", true}, {"third_party/vendored/Package.swift", "let pkg = Package(name: \"v\", path: \"../../../prototypes/plugins/author\")\n", true},
		{"third_party/prototypes/Package.swift", "let pkg = Package(name: \"v\", path: \"../../prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/prototypes/Sources/deep/Package.swift", ".target(name: \"x\", path: \"../../../../../../prototypes/plugins/author\")\n", true}, {"third_party/prototypes/Package.swift", "let pkg = Package(name: \"v\", path: \"Sources/V\")\n", false},
		{"prototypes/plugins/author/Package.swift", "let pkg = Package(name: \"a\", path: \"../..\")\n", false}, {"apps/apple/Packages/SaiKit/Package.swift", "let doc = \"\"\"\npath: \"../../../../prototypes/plugins/author\" is only prose\n\"\"\"\nlet pkg = Package(name: \"x\", path: \"Sources/Safe\")\n", false}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"%s/prototypes/plugins/author\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"%s/prototypes\")\n", true}, {"apps/apple/Packages/SaiKit/Package.swift", "let pkg = Package(name: \"x\", path: \"/opt/vendor/Lib\")\n", false},
	} {
		root := lockedFixture(t); writeRel(t, root, tc.file, strings.ReplaceAll(tc.src, "%s", root))
		if err := check(root); (err == nil) == tc.wantFail { t.Fatalf("%s: wantFail=%v, got err=%v\n%s", tc.file, tc.wantFail, err, tc.src) }
	}
	root := lockedFixture(t)
	if err := checkProductionGoPurity(root); err != nil { t.Fatalf("clean tree must pass purity: %v", err) }
	if err := checkProductionManifests(root); err != nil { t.Fatalf("clean tree must pass manifests: %v", err) }
	if err := checkProductionManifests(filepath.Join(root, "no", "such")); err == nil { t.Fatal("unwalkable root must fail closed") }
}
func TestAbsoluteManifestResolution(t *testing.T) {
	root := lockedFixture(t)
	if os.MkdirAll(filepath.Join(root, "prototypes/plugins/author"), 0755) != nil || os.Symlink(filepath.Join(root, "prototypes"), filepath.Join(root, "proto-link")) != nil { t.Fatal("fixture") }
	t.Setenv("HOME", root)
	for _, tc := range []struct{ v string; hit bool }{{root + "/prototypes/plugins/author", true}, {"~/prototypes/plugins/author", true}, {root + "/proto-link/plugins/author2", true}, {root + "/does/not/exist", false}, {"/opt/vendor/Lib", false}} {
		if resolvesInto(root, "apps/apple/Package.swift", tc.v) != tc.hit { t.Fatalf("resolvesInto(%q) want %v", tc.v, tc.hit) }
	}
	t.Setenv("HOME", "")
	if !resolvesInto(root, "apps/apple/Package.swift", "~x/plugin") { t.Fatal("unresolvable home must fail closed") }
}
func TestGoImportClassifier(t *testing.T) {
	hit := []string{"package app\nimport _ \"github.com/Dezocode/Sai/prototypes/plugins/author\"\n", "package app\nimport _ `prototypes/plugins/author`\n", "package app\nimport (\n\t_ \"a\"\n\t_ \"prototypes/plugins/author\"\n)\n", "package app\nimport\n\t_ \"prototypes/plugins/author\"\n", "package app\n/* c */import _ \"prototypes/plugins/author\"\n", "package app; import _ \"prototypes/plugins/author\"\n", "package app\nimport \"github.com/Dezocode/Sai/internal/app\"; import _ \"prototypes/plugins/author\"\n"}
	for _, src := range hit { if !goImportsPrototype(src) { t.Fatalf("classifier missed lane import:\n%s", src) } }
	root := lockedFixture(t); writeRel(t, root, "internal/app/leak.go", hit[0])
	if err := check(root); err == nil { t.Fatal("production Go lane import must fail end-to-end") }
	miss := []string{"package app\n\n// doc: prototypes/plugins/author is documented here.\nvar note = \"prototypes/plugins/author\"\n", "package app\nvar s = \"import _ \\\"prototypes/plugins/author\\\"\"\n", "package app\nimport \"fmt\"\n"}
	for _, src := range miss { if goImportsPrototype(src) { t.Fatalf("classifier flagged non-import mention:\n%s", src) } }
	root = lockedFixture(t); writeRel(t, root, "internal/app/doc.go", miss[0])
	if err := check(root); err != nil { t.Fatalf("non-import mention must not trip the gate: %v", err) }
}
func TestPrototypeGoCannotModifyProtectedProduction(t *testing.T) {
	for _, src := range []string{"package author\nimport \"plugin\"\nfunc x() { plugin.Open(\"\") }\n", "package author\nimport pl \"plugin\"\nfunc x() { pl.Open(\"\") }\n", "package author\nimport . \"plugin\"\nfunc y() { Open(\"\") }\n", "package author\nfunc z() { plugin.Open(\"\") }\n", "package author\nimport \"plugin\"\nfunc x() { (plugin.Open)(\"\") }\n", "package author\nimport \"plugin\"\nfunc x() { o := plugin.Open; o(\"\") }\n", "package author\nimport pl \"plugin\"\nfunc x() { f := pl.Open; f(\"\") }\n", "package author\nimport \"plugin\"\nfunc x() { ((plugin)).Open(\"\") }\n"} { mustFail(t, "prototypes/plugins/author/hook.go", src) }
}
func TestSymlinkEscapeFailsClosed(t *testing.T) {
	for _, tc := range []struct{ at, target string; legal bool }{{"prototypes/plugins/author/link.go", "apps/apple/Packages/SaiKit/Sources/SaiFoundation/outside.go", false}, {"prototypes/plugins", "", false}, {"prototypes", "", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/alias.swift", "prototypes/plugins/author/Editor.swift", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/aliased", "prototypes/plugins/author", false}, {"apps/apple/Packages/SaiKit/Sources/SaiFoundation/alias.go", "apps/apple/Packages/SaiKit/Sources/SaiFoundation/real.go", true}} {
		root := lockedFixture(t); writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
		link := filepath.Join(root, tc.at); os.MkdirAll(filepath.Dir(link), 0755); target := tc.target
		switch {
		case target == "": os.RemoveAll(link); target = t.TempDir()
		case strings.HasPrefix(target, "prototypes/"): target = filepath.Join(root, target)
		default: writeRel(t, root, target, "package foundation\n"); target = filepath.Join(root, target)
		}
		if err := os.Symlink(target, link); err != nil { t.Skipf("symlinks unavailable: %v", err) }
		if err := check(root); (err == nil) != tc.legal { t.Fatalf("symlink %s -> %q: want legal=%v, got err=%v", tc.at, target, tc.legal, err) }
	}
}
func TestVerifierSourceNotSelfFlagged(t *testing.T) {
	b, err := os.ReadFile("main.go")
	if err != nil || goImportsPrototype(string(b)) || strings.Contains(string(b), "\nfunc init()") { t.Fatal("verifier source unreadable or self-triggers the gates") }
}
func gitc(t *testing.T, root string, a ...string) string {
	t.Helper()
	o, err := exec.Command("git", append([]string{"-C", root}, a...)...).CombinedOutput()
	if err != nil { t.Fatalf("git %v: %v\n%s", a, err, o) }
	return strings.TrimSpace(string(o))
}
func TestPrototypeLaneDiffGate(t *testing.T) {
	for _, c := range [][]string{{"prototypes/plugins/author/Editor.swift", "internal/app/app.go"}, {"prototypes/plugins/author/bridge.go", "cmd/sai/main.go"}, {"prototypes/x.go", "internal/app/app_test.go"}, {"prototypes/plugins/author/x.go", "internal/app dir/evil.go"}, {"prototypes/plugins/author/y.go", "cmd/sai/tool dir/main.go"}} {
		if err := prototypeLaneViolation(c); err == nil { t.Fatalf("expected lane violation for %v", c) }
	}
	for _, c := range [][]string{{"prototypes/plugins/author/Editor.swift"}, {"internal/app/app.go"}, {"prototypes/plugins/author/x.go", "cmd/sai-design-check/main.go"}} {
		if err := prototypeLaneViolation(c); err != nil { t.Fatalf("expected pass for %v: %v", c, err) }
	}
	root := lockedFixture(t); gitc(t, root, "init", "-q"); gitc(t, root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-qm", "base")
	t.Setenv("SAI_TRUSTED_BASE", gitc(t, root, "rev-parse", "HEAD"))
	writeRel(t, root, "prototypes/plugins/author/bridge.go", "package author\nvar x = 1\n"); writeRel(t, root, "internal/app/app.go", "package app\nvar bumped = 1\n")
	gitc(t, root, "add", "-A"); gitc(t, root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "touch")
	if err := check(root); err == nil { t.Fatal("prototype-scoped change editing internal/** must fail") }
	os.RemoveAll(filepath.Join(root, ".git", "refs", "heads"))
	if _, derr := exec.Command("git", "-C", root, "diff", "--name-only", "-z", os.Getenv("SAI_TRUSTED_BASE")+"..HEAD").Output(); derr == nil { t.Skip("git diff unexpectedly succeeded; fixture could not induce the failure vector") }
	if err := check(root); err == nil { t.Fatal("failed trusted-base git diff must fail the gate closed") }
}
func TestPrototypeLaneRenameIntoLaneFails(t *testing.T) {
	root := lockedFixture(t); gitc(t, root, "init", "-q")
	writeRel(t, root, "internal/app/app.go", "package app\nvar x = 1\n"); writeRel(t, root, "prototypes/plugins/author/Editor.swift", protoView)
	gitc(t, root, "add", "-A"); gitc(t, root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-qm", "base")
	t.Setenv("SAI_TRUSTED_BASE", gitc(t, root, "rev-parse", "HEAD")); os.MkdirAll(filepath.Join(root, "prototypes/plugins/author"), 0755)
	gitc(t, root, "mv", "internal/app/app.go", "prototypes/plugins/author/app.go"); gitc(t, root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-aqm", "move production Go into the lane")
	raw, rerr := exec.Command("git", "-C", root, "diff", "-M", "--name-status", "-z", os.Getenv("SAI_TRUSTED_BASE")+"..HEAD").Output()
	nameOnly := gitc(t, root, "diff", "-M", "--name-only", os.Getenv("SAI_TRUSTED_BASE")+"..HEAD")
	if rerr != nil || !strings.HasPrefix(string(raw), "R100\x00internal/app/app.go\x00") || strings.Contains(nameOnly, "internal/") || !strings.HasPrefix(nameOnly, "prototypes/") { t.Fatalf("fixture could not induce the rename vector: %v %q %q", rerr, raw, nameOnly) }
	if err := checkPrototypeLaneDiff(root); err == nil { t.Fatal("rename of protected production Go into prototypes/ must trip the trusted-base gate") }
}
func TestParseNameStatusPaths(t *testing.T) {
	ok := map[string][]string{"": nil, "M\x00a.txt\x00": {"a.txt"}, "A\x00n.txt\x00D\x00o.txt\x00": {"n.txt", "o.txt"}, "C75\x00x\x00y\x00": {"x", "y"}, "T\x00a b dir/c d.txt\x00": {"a b dir/c d.txt"}, "R100\x00a\x00b": {"a", "b"}, "R100\x00internal/app/app.go\x00prototypes/plugins/author/app.go\x00": {"internal/app/app.go", "prototypes/plugins/author/app.go"}}
	for raw, want := range ok { if got, err := parseNameStatusPaths([]byte(raw)); err != nil || strings.Join(got, "|") != strings.Join(want, "|") { t.Fatalf("parseNameStatusPaths(%q) = %v, %v; want %v", raw, got, err, want) } }
	for _, raw := range []string{"\x00M\x00x\x00", "M", "R100\x00only-dest\x00", "M\x00"} { if got, err := parseNameStatusPaths([]byte(raw)); err == nil { t.Fatalf("malformed record %q must fail closed, got %v", raw, got) } }
}
func TestModuleReplaceIntoLaneFails(t *testing.T) {
	root := lockedFixture(t); parent := t.TempDir()
	if os.MkdirAll(filepath.Join(root, "prototypes", "plugins", "author"), 0755) != nil || os.Symlink(filepath.Join(root, "prototypes", "plugins", "author"), filepath.Join(parent, "alias")) != nil { t.Fatal("fixture") }
	hit := []string{"replace example.com/x => ./prototypes/plugins/author\n", "replace (\n\tA => prototypes/plugins/author\n\tB => ./prototypes\n)\n", "replacex y\nreplace e.com/x => prototypes/plugins/author", "replace (e.com/x => ./prototypes/author)", "replace e.com/x => prototypes/../prototypes/plugins/author\n", "replace (\n\texample.com/x => ./internal/x\n", "replace (\n\ta => ./vendor/x v1.0.0\n", "module m\nrequire e.com/y v1.2.3\n\nreplace (\n\te.com/z => ../shared\n", "module m\nreplace github.com/evil/bad => " + filepath.Join(root, "prototypes/plugins/author") + "\n", "replace e.com/x => \"" + filepath.Join(root, "prototypes") + "\"\n", "replace e.com/x => " + filepath.Join(parent, "alias") + "\n"}
	for _, src := range hit { if !moduleTargetsLane(root, src) { t.Fatalf("expected lane replace to fail closed:\n%s", src) } }
	miss := []string{"// replace e.com/x => prototypes/plugins/author is only a comment\n", "there is no replace of anything into prototypes/plugins here\n", "replace e.com/x => ../vendor/some/module v1.0.0\n", "replace e.com/x => ./internal/gen v0.0.0\n", "replace e.com/x => /opt/elsewhere/module v1.0.0\n", "module m\nreplace github.com/evil/bad => ../prototypes/plugins/author\n", "replace e.com/x => ../../prototypes/plugins/author\n", "replace e.com/x => \"../prototypes/../prototypes/plugins/author\" // pinned\n", "replace e.com/x => \"..\"\n", "replace e.com/x => " + parent + "\n", "replace e.com/x => " + filepath.Clean(root) + "\n", "replace (\n\tok.com/a => ./vendor/x v1.0.0\n)\nmodule m\n"}
	for _, src := range miss { if moduleTargetsLane(root, src) { t.Fatalf("non-lane content must not trip the guard:\n%s", src) } }
	writeRel(t, root, "go.mod", "module m\nreplace e.com/x => "+filepath.Join(root, "prototypes/plugins/author")+"\n")
	if err := check(root); err == nil { t.Fatal("go.mod replace into the lane must fail check()") }
}
func TestGoWorkUseIntoLaneFails(t *testing.T) { root := lockedFixture(t); writeRel(t, root, "go.work", "go 1.22\n\nuse .\nuse ./prototypes/plugins/author\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("use into lane must fail") } }
func TestGoWorkReplaceBlockIntoLaneFails(t *testing.T) { root := lockedFixture(t); writeRel(t, root, "tools/go.work", "go 1.22\n\nreplace (\n\texample.com/x => ../prototypes/plugins/author\n)\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("replace-block into lane must fail (relative to go.work dir)") } }
func TestGoWorkNestedWorkspaceCannotBypass(t *testing.T) { root := lockedFixture(t); writeRel(t, root, "cmd/nested/go.work", "go 1.22\n\nuse ../../prototypes/plugins/author\nreplace e.com/y => ../../prototypes/plugins/author\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("nested workspace traversal into lane must fail") } }
func TestGoWorkSymlinkedAliasIntoLaneFails(t *testing.T) {
	root := lockedFixture(t); parent := t.TempDir()
	if os.MkdirAll(filepath.Join(root, "prototypes", "plugins", "author"), 0755) != nil || os.Symlink(filepath.Join(root, "prototypes", "plugins", "author"), filepath.Join(parent, "alias")) != nil { t.Fatal("fixture") }
	writeRel(t, root, "sub/go.work", "go 1.22\n\nuse "+filepath.Join(parent, "alias")+"\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("symlink-aliased use into lane must fail") }
}
func TestGoWorkCleanPasses(t *testing.T) { root := lockedFixture(t); writeRel(t, root, "go.work", "// production workspace\ngo 1.22\n\nuse .\nuse ./internal/app\n\nreplace example.com/a => ./internal/a v1.0.0\n"); if err := checkGoWorkFiles(root); err != nil { t.Fatal(err) } }
func TestGoWorkMalformedFailsClosed(t *testing.T) { root := lockedFixture(t); writeRel(t, root, "go.work", "replace (\n\texample.com/x ./no-arrow-entry\n)\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("malformed replace block must fail closed") } }
func TestGoWorkUnterminatedBlockFailsClosed(t *testing.T) {
	root := lockedFixture(t); writeRel(t, root, "go.work", "go 1.22\n\nuse (\n\t./prototypes/plugins/author\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("unterminated use block must fail closed") }
	writeRel(t, root, "go.work", "go 1.22\n\nreplace (\n\texample.com/x => ./internal/a\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("unterminated replace block with lane-free entries must still fail closed") }
}
func TestGoWorkEmptyReplaceTargetFailsClosed(t *testing.T) {
	root := lockedFixture(t); writeRel(t, root, "go.work", "go 1.22\n\nreplace example.com/x => \n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("empty single-line replace target must fail closed") }
	writeRel(t, root, "go.work", "go 1.22\n\nreplace (\n\texample.com/x =>\n)\n"); if err := checkGoWorkFiles(root); err == nil { t.Fatal("empty block replace target must fail closed") }
}
func TestNestedGoModReplaceIntoLaneFails(t *testing.T) {
	root := lockedFixture(t)
	writeRel(t, root, "internal/evilmod/go.mod", "module github.com/Dezocode/Sai/internal/evilmod\n\nreplace github.com/SomeBody/lanealias => ../../prototypes/plugins/author\n")
	if err := checkPrototypeLaneDiff(root); err == nil { t.Fatal("nested go.mod replace into lane must fail") }
	writeRel(t, root, "tools/vendored/go.mod", "module vend\n\nreplace e.com/x => ./vendor/x v1.0.0\n"); writeRel(t, root, "third_party/prototypes/keep/go.mod", "module keep\n")
	if err := checkPrototypeLaneDiff(root); err == nil { t.Fatal("unreadable nested manifest path handling diverged") }
}
