package planner

import (
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"reflect"
	"testing"
)

func fixturesDir() string {
	return filepath.Join("..", "fixtures")
}

func loadFixtureGraph(t *testing.T, name string) Graph {
	t.Helper()
	b, err := ioutil.ReadFile(filepath.Join(fixturesDir(), name))
	if err != nil {
		t.Fatal(err)
	}
	var g Graph
	if err := json.Unmarshal(b, &g); err != nil {
		t.Fatal(err)
	}
	g.GraphHash = CanonicalGraphHash(&g)
	if err := ValidateGraph(&g); err != nil {
		t.Fatal(err)
	}
	return g
}

func loadFixturePlan(t *testing.T, name string) Plan {
	t.Helper()
	b, err := ioutil.ReadFile(filepath.Join(fixturesDir(), name))
	if err != nil {
		t.Fatal(err)
	}
	var p Plan
	if err := json.Unmarshal(b, &p); err != nil {
		t.Fatal(err)
	}
	return p
}

func assertPlanEqual(t *testing.T, got, want Plan) {
	t.Helper()
	want.GraphHash = got.GraphHash
	if !reflect.DeepEqual(got, want) {
		b, _ := json.MarshalIndent(got, "", "  ")
		t.Fatalf("plan mismatch:\n%s", string(b))
	}
}

func TestGoldenHarness(t *testing.T) {
	g := loadFixtureGraph(t, "harness_golden.graph.json")
	got := BuildPlan(&g, g.SourceHeadSHA)
	want := loadFixturePlan(t, "harness_golden.plan.json")
	assertPlanEqual(t, got, want)
	if !got.Ready {
		t.Fatal("expected ready plan")
	}
}

func TestGoldenAuthor(t *testing.T) {
	g := loadFixtureGraph(t, "author_golden.graph.json")
	got := BuildPlan(&g, g.SourceHeadSHA)
	want := loadFixturePlan(t, "author_golden.plan.json")
	assertPlanEqual(t, got, want)
	if !got.Ready {
		t.Fatal("expected ready plan")
	}
}

func TestNegativeUnknown(t *testing.T) {
	g := loadFixtureGraph(t, "negative_unknown.graph.json")
	plan := BuildPlan(&g, g.SourceHeadSHA)
	if plan.Ready {
		t.Fatal("UNKNOWN must block ready")
	}
	found := false
	for _, b := range plan.Blockers {
		if b.Code == "unknown_classification" {
			found = true
		}
	}
	if !found {
		t.Fatal("expected unknown_classification blocker")
	}
}

func TestNegativeStaleHead(t *testing.T) {
	g := loadFixtureGraph(t, "negative_stale_head.graph.json")
	plan := BuildPlan(&g, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
	if plan.Ready {
		t.Fatal("stale head must block ready")
	}
	found := false
	for _, b := range plan.Blockers {
		if b.Code == "stale_head" {
			found = true
		}
	}
	if !found {
		t.Fatal("expected stale_head blocker")
	}
}

func TestNegativePathConflict(t *testing.T) {
	g := loadFixtureGraph(t, "negative_path_conflict.graph.json")
	plan := BuildPlan(&g, g.SourceHeadSHA)
	if plan.Ready {
		t.Fatal("path conflict must block ready")
	}
	found := false
	for _, b := range plan.Blockers {
		if b.Code == "path_conflict" {
			found = true
		}
	}
	if !found {
		t.Fatal("expected path_conflict blocker")
	}
}
