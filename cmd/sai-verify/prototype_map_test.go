package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPrototypeRootIsClaimableAndNearPrefixesAreDistinct(t *testing.T) {
	got := pathRe.FindAllString("`prototypes/plugins/*` `prototypes/plugins/*/PrototypeDesign/*` `prototypes/plugins/author/Editor.swift`", -1)
	if len(got) != 3 || got[0] != "prototypes/plugins/*" || got[1] != "prototypes/plugins/*/PrototypeDesign/*" || got[2] != "prototypes/plugins/author/Editor.swift" {
		t.Fatalf("pathRe classified %v, want exactly [prototypes/plugins/* prototypes/plugins/*/PrototypeDesign/* prototypes/plugins/author/Editor.swift]", got)
	}
	for _, near := range []string{"`prototypes/plugin/*`", "`prototypes/plugins-evil/*`"} {
		if g := pathRe.FindAllString(near, -1); len(g) != 1 || g[0] != near[1:len(near)-1] {
			t.Fatalf("near-prefix %s classified as %v, must stay distinct from the canonical root", near, g)
		}
	}
	if g := pathRe.FindAllString("`prototype/plugins/*`", -1); len(g) != 0 {
		t.Fatalf("`prototype/plugins/*` must be unrecognized, got %v", g)
	}
}
func TestPrototypeMapEntryParses(t *testing.T) {
	feats, probs := loadFeats("../..")
	if len(feats) == 0 {
		t.Fatalf("no features parsed: %v", probs)
	}
	for _, f := range feats {
		if f.ID != "prototype-plugins" {
			continue
		}
		for _, want := range []string{"prototypes/plugins/*", "cmd/sai-design-check/*", ".github/workflows/sai-design-language.yml"} {
			if !pathCovered(f.Paths, want) {
				t.Fatalf("prototype-plugins feature missing path %s; has %v", want, f.Paths)
			}
		}
		if len(f.Subs) < 4 {
			t.Fatalf("prototype-plugins sub-features incomplete: %v", f.Subs)
		}
		if len(f.Ent) == 0 || len(f.Proof) == 0 {
			t.Fatal("prototype-plugins entry/proof recipes missing")
		}
		return
	}
	t.Fatal("prototype-plugins feature not in map index")
}
func TestSaiDesignLanguageWorkflowTriggersOnPrototypes(t *testing.T) {
	b, err := os.ReadFile(filepath.Join("..", "..", ".github", "workflows", "sai-design-language.yml"))
	if err != nil {
		t.Fatal(err)
	}
	body := string(b)
	for _, block := range []string{"pull_request:", "push:"} {
		i := strings.Index(body, block)
		if i < 0 {
			t.Fatalf("missing %s trigger", block)
		}
		end := i + 300
		if end > len(body) {
			end = len(body)
		}
		if !strings.Contains(body[i:end], `"prototypes/**"`) {
			t.Fatalf("%s paths must include prototypes/**", block)
		}
	}
}
func pathCovered(paths []string, want string) bool {
	for _, k := range paths {
		if k == want || len(k) > 0 && k[len(k)-1] == '*' && len(want) >= len(k) && want[:len(k)-1] == k[:len(k)-1] {
			return true
		}
	}
	return false
}
