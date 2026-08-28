package planner

import (
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"testing"
)

// TestPrintFixtureHashes logs canonical graph hashes for fixture maintenance.
func TestPrintFixtureHashes(t *testing.T) {
	files := []string{
		"harness_golden.graph.json",
		"author_golden.graph.json",
		"negative_unknown.graph.json",
		"negative_stale_head.graph.json",
		"negative_path_conflict.graph.json",
	}
	for _, name := range files {
		b, err := ioutil.ReadFile(filepath.Join(fixturesDir(), name))
		if err != nil {
			t.Fatal(err)
		}
		var g Graph
		if err := json.Unmarshal(b, &g); err != nil {
			t.Fatal(err)
		}
		t.Logf("%s => %s", name, CanonicalGraphHash(&g))
	}
}
