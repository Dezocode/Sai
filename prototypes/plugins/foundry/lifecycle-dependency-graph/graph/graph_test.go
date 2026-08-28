package graph

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const (
	testRepo = "github.com/Dezocode/Sai"
	testBase = "main"
	testHead = "3159b58753a140ef052bb41dc987c8a5cd6fad81"
)

func fixtureDir(t *testing.T) string {
	t.Helper()
	return filepath.Join("..", "synthetic-fixture")
}

func TestBuildGoldenHash(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	golden, err := os.ReadFile(filepath.Join("testdata", "golden-hash.txt"))
	if err != nil {
		t.Fatalf("read golden: %v", err)
	}
	want := strings.TrimSpace(string(golden))
	if out.GraphHash != want {
		t.Fatalf("graph_hash mismatch\nwant %s\ngot  %s", want, out.GraphHash)
	}
	if out.SchemaVersion != SchemaVersion {
		t.Fatalf("schema_version = %d, want %d", out.SchemaVersion, SchemaVersion)
	}
	if out.ToolVersion != ToolVersion {
		t.Fatalf("tool_version = %q, want %q", out.ToolVersion, ToolVersion)
	}
	if out.Repo != testRepo || out.Base != testBase || out.Head != testHead {
		t.Fatalf("binding fields: repo=%q base=%q head=%q", out.Repo, out.Base, out.Head)
	}
	if len(out.Nodes) != 5 {
		t.Fatalf("nodes len = %d, want 5", len(out.Nodes))
	}
	if len(out.Edges) != 1 {
		t.Fatalf("edges len = %d, want 1", len(out.Edges))
	}
}

func TestValidateForPlanningRejectsUnknownNode(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	out.Nodes = append(out.Nodes, Node{ID: "mystery", Classification: ClassUnknown})
	if err := ValidateForPlanning(out); err == nil {
		t.Fatal("expected planning error for UNKNOWN node")
	}
}

func TestValidateForPlanningRejectsUnknownEdge(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	out.Edges = append(out.Edges, Edge{From: "reuse-lib", To: "mystery", Classification: ClassUnknown})
	if err := ValidateForPlanning(out); err == nil {
		t.Fatal("expected planning error for UNKNOWN edge")
	}
}

func TestValidateHeadBindingRejectsStaleHead(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	if err := ValidateHeadBinding(out, strings.Repeat("a", 40)); err == nil {
		t.Fatal("expected stale head error")
	}
}

func TestValidateGraphHashBindingRejectsTamper(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	out.GraphHash = strings.Repeat("0", 64)
	if err := ValidateGraphHashBinding(out); err == nil {
		t.Fatal("expected graph hash binding error")
	}
}

func TestBuildDeterministicAcrossReorder(t *testing.T) {
	dir := t.TempDir()
	manifest := filepath.Join(dir, "manifest.json")
	deps := filepath.Join(dir, "deps.json")
	if err := os.WriteFile(manifest, []byte(`{"schema_version":1,"id":"reorder"}`), 0o644); err != nil {
		t.Fatal(err)
	}
	raw := `{"nodes":[{"id":"z-node","classification":"REUSE"},{"id":"a-node","classification":"PROMOTE"}],"edges":[]}`
	if err := os.WriteFile(deps, []byte(raw), 0o644); err != nil {
		t.Fatal(err)
	}
	in := BuildInput{Repo: testRepo, Base: testBase, Head: testHead, ManifestDir: dir}
	first, err := Build(in)
	if err != nil {
		t.Fatalf("first Build: %v", err)
	}
	reordered := `{"nodes":[{"id":"a-node","classification":"PROMOTE"},{"id":"z-node","classification":"REUSE"}],"edges":[]}`
	if err := os.WriteFile(deps, []byte(reordered), 0o644); err != nil {
		t.Fatal(err)
	}
	second, err := Build(in)
	if err != nil {
		t.Fatalf("second Build: %v", err)
	}
	if first.GraphHash != second.GraphHash {
		t.Fatalf("hash drift on reorder: %s vs %s", first.GraphHash, second.GraphHash)
	}
}

func TestParseManifestForbiddenAuthority(t *testing.T) {
	raw := []byte(`{"schema_version":1,"id":"x","signing_key":"bad"}`)
	if _, err := ParseManifest(raw); err == nil {
		t.Fatal("expected forbidden field error")
	}
}

func TestParseDepsRejectsUnknownClassification(t *testing.T) {
	raw := []byte(`{"nodes":[{"id":"n","classification":"NOPE"}],"edges":[]}`)
	if _, err := ParseDeps(raw); err == nil {
		t.Fatal("expected unknown classification error")
	}
}

func TestBuildRejectsInvalidHead(t *testing.T) {
	_, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        "short",
		ManifestDir: fixtureDir(t),
	})
	if err == nil {
		t.Fatal("expected invalid head error")
	}
}

func TestOutputJSONRoundTrip(t *testing.T) {
	out, err := Build(BuildInput{
		Repo:        testRepo,
		Base:        testBase,
		Head:        testHead,
		ManifestDir: fixtureDir(t),
	})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	b, err := json.Marshal(out)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var again Output
	if err := json.Unmarshal(b, &again); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if again.GraphHash != out.GraphHash {
		t.Fatalf("round-trip hash mismatch")
	}
}
