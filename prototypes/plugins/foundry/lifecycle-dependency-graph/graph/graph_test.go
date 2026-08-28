package graph

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const (
	goldenRepo = "Dezocode/Sai"
	goldenBase = "3159b58753a140ef052bb41dc987c8a5cd6fad81"
	goldenHead = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)

func goldenSpec() DepSpec {
	return DepSpec{
		Repo:        goldenRepo,
		Base:        goldenBase,
		Head:        goldenHead,
		FixtureRoot: filepath.Join("..", "synthetic-fixture"),
	}
}

func TestGoldenHash(t *testing.T) {
	out, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	want, err := os.ReadFile(filepath.Join("testdata", "golden-hash.txt"))
	if err != nil {
		t.Fatal(err)
	}
	if strings.TrimSpace(string(want)) != out.GraphHash {
		t.Fatalf("golden hash mismatch: got %s", out.GraphHash)
	}
}

func TestUnknownFails(t *testing.T) {
	if err := validateClassification(UNKNOWN); err == nil {
		t.Fatal("expected UNKNOWN to fail")
	}
}

func TestUnclassifiedFails(t *testing.T) {
	if err := validateClassification(""); err == nil {
		t.Fatal("expected empty classification to fail")
	}
}

func TestStaleHeadFails(t *testing.T) {
	out, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	if err := ValidateHeadBinding(out, "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"); err == nil {
		t.Fatal("expected stale head failure")
	}
}

func TestStaleGraphHashFails(t *testing.T) {
	out, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	if err := ValidateGraphHashBinding(out, "0"+out.GraphHash); err == nil {
		t.Fatal("expected stale graph_hash failure")
	}
}

func TestDeterministicReorder(t *testing.T) {
	a, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	b, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	if a.GraphHash != b.GraphHash {
		t.Fatalf("rebuild hash mismatch: %s vs %s", a.GraphHash, b.GraphHash)
	}
	reordered := Deps{
		Nodes: []Node{
			{ID: "drop-legacy", Path: "legacy/drop.go", Classification: DROP},
			{ID: "reuse-lib", Path: "lib/reuse.go", Classification: REUSE},
			{ID: "promote-mod", Path: "mod/promote.go", Classification: PROMOTE},
			{ID: "export-pkg", Path: "pkg/export.go", Classification: EXPORT},
			{ID: "remote-api", Path: "api/remote.go", Classification: REMOTE},
		},
		Edges: []Edge{{From: "reuse-lib", To: "promote-mod", Classification: PROMOTE_SHARED}},
	}
	manifest, err := ParseManifest([]byte(`{"schema_version":1,"id":"synthetic-fixture"}`))
	if err != nil {
		t.Fatal(err)
	}
	c, err := Build(BuildInput{Repo: goldenRepo, Base: goldenBase, Head: goldenHead, Manifest: manifest, Deps: reordered})
	if err != nil {
		t.Fatal(err)
	}
	if c.GraphHash != a.GraphHash {
		t.Fatalf("reordered hash mismatch: %s vs %s", c.GraphHash, a.GraphHash)
	}
}

func TestForbiddenManifestFieldFails(t *testing.T) {
	_, err := ParseManifest([]byte(`{"schema_version":1,"id":"x","permissions":["admin"]}`))
	if err == nil {
		t.Fatal("expected forbidden manifest field failure")
	}
}

func TestValidateForPlanningOK(t *testing.T) {
	out, err := goldenSpec().Build()
	if err != nil {
		t.Fatal(err)
	}
	if err := ValidateForPlanning(out); err != nil {
		t.Fatal(err)
	}
}

func TestParseDepsRoundTrip(t *testing.T) {
	body, err := os.ReadFile(filepath.Join("..", "synthetic-fixture", "deps.json"))
	if err != nil {
		t.Fatal(err)
	}
	deps, err := ParseDeps(body)
	if err != nil {
		t.Fatal(err)
	}
	if len(deps.Nodes) != 5 {
		t.Fatalf("expected 5 nodes, got %d", len(deps.Nodes))
	}
	enc, err := json.Marshal(deps)
	if err != nil {
		t.Fatal(err)
	}
	again, err := ParseDeps(enc)
	if err != nil {
		t.Fatal(err)
	}
	if len(again.Edges) != 1 {
		t.Fatalf("expected 1 edge, got %d", len(again.Edges))
	}
}
