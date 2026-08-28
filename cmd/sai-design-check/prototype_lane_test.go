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
func TestGoWorkUseWithoutSpaceIntoLaneFails(t *testing.T) {
	root := lockedFixture(t)
	writeRel(t, root, "go.work", "go 1.22\n\nuse(\n\t./prototypes/plugins/author\n)\n")
	if err := checkGoWorkFiles(root); err == nil { t.Fatal("use( block into lane must fail") }
	writeRel(t, root, "go.work", "go 1.22\n\nreplace(\n\texample.com/x => ./prototypes/plugins/author\n)\n")
	if err := checkGoWorkFiles(root); err == nil { t.Fatal("replace( block into lane must fail") }
}
func TestResolvesIntoRelativePrototypesTree(t *testing.T) {
	root := lockedFixture(t)
	if !resolvesInto(root, "apps/apple/Package.swift", "../../prototypes/other") { t.Fatal("relative prototypes/ tree must resolve into lane") }
	if resolvesInto(root, "apps/apple/Package.swift", "../../vendor/safe") { t.Fatal("non-lane relative path must not hit") }
}
