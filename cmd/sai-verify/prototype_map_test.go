package main

import "testing"

func TestPrototypeRootIsClaimableAndNearPrefixesAreDistinct(t *testing.T) {
	sample := "`prototypes/plugins/*` `prototypes/plugins/*/PrototypeDesign/*` `prototypes/plugins/author/Editor.swift`"
	got := pathRe.FindAllString(sample, -1)
	need := []string{"prototypes/plugins/*", "prototypes/plugins/*/PrototypeDesign/*", "prototypes/plugins/author/Editor.swift"}
	have := map[string]bool{}
	for _, g := range got { have[g] = true }
	if len(got) != len(need) {
		t.Fatalf("pathRe classified %v, want exactly %v", got, need)
	}
	for _, n := range need {
		if !have[n] { t.Fatalf("pathRe missed %s from %v", n, got) }
	}
	// Near-prefix surfaces stay distinct claims: recognized verbatim or provably unrecognized, never absorbed by the root glob (no vacuous passes).
	for _, near := range []string{"`prototypes/plugin/*`", "`prototypes/plugins-evil/*`"} {
		if got := pathRe.FindAllString(near, -1); len(got) != 1 || got[0] != near[1:len(near)-1] {
			t.Fatalf("near-prefix %s classified as %v, must stay distinct from the canonical root", near, got)
		}
	}
	if got := pathRe.FindAllString("`prototype/plugins/*`", -1); len(got) != 0 {
		t.Fatalf("`prototype/plugins/*` must be unrecognized, got %v", got)
	}
}

func TestPrototypeMapEntryParses(t *testing.T) {
	feats, probs := loadFeats("../..")
	if len(feats) == 0 {
		t.Fatalf("no features parsed: %v", probs)
	}
	found := false
	for _, f := range feats {
		if f.ID != "prototype-plugins" { continue }
		found = true
		covered := map[string]bool{}
		for _, p := range f.Paths { covered[p] = true }
		for _, want := range []string{"prototypes/plugins/*", "cmd/sai-design-check/*", ".github/workflows/sai-design-language.yml"} {
			if !covered[want] && !coveredHasPrefix(covered, want) {
				t.Fatalf("prototype-plugins feature missing path %s; has %v", want, covered)
			}
		}
		if len(f.Subs) < 4 {
			t.Fatalf("prototype-plugins sub-features incomplete: %v", f.Subs)
		}
		if len(f.Ent) == 0 || len(f.Proof) == 0 {
			t.Fatal("prototype-plugins entry/proof recipes missing")
		}
	}
	if !found {
		t.Fatal("prototype-plugins feature not in map index")
	}
}

func coveredHasPrefix(m map[string]bool, want string) bool {
	for k := range m {
		if k == want || len(k) > 0 && k[len(k)-1] == '*' && len(want) >= len(k) && want[:len(k)-1] == k[:len(k)-1] { return true }
	}
	return false
}
