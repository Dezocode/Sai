package main

import "testing"

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

func TestFoundryIntegratePlannerMapEntryParses(t *testing.T) {
	feats, probs := loadFeats("../..")
	if len(feats) == 0 {
		t.Fatalf("no features parsed: %v", probs)
	}
	for _, f := range feats {
		if f.ID != "foundry-integrate-planner" {
			continue
		}
		for _, want := range []string{"prototypes/plugins/foundry/integrate-planner/*", "docs/roadmap/foundry/07-integrate-planner-v1.md"} {
			if !pathCovered(f.Paths, want) {
				t.Fatalf("foundry-integrate-planner feature missing path %s; has %v", want, f.Paths)
			}
		}
		if len(f.Subs) < 3 || len(f.Ent) == 0 || len(f.Proof) == 0 {
			t.Fatal("foundry-integrate-planner contract incomplete")
		}
		return
	}
	t.Fatal("foundry-integrate-planner feature not in map index")
}

func pathCovered(paths []string, want string) bool {
	for _, k := range paths {
		if k == want || len(k) > 0 && k[len(k)-1] == '*' && len(want) >= len(k) && want[:len(k)-1] == k[:len(k)-1] {
			return true
		}
	}
	return false
}
