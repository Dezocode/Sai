package integrateplanner

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func loadGraphFixture(name string) DependencyGraph {
	path := filepath.Join("fixtures", name)
	data, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	g, err := ParseGraphJSON(data)
	if err != nil {
		panic(err)
	}
	return g
}

func loadPlanFixture(name string) IntegratePlan {
	path := filepath.Join("fixtures", name)
	data, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	var plan IntegratePlan
	if err := json.Unmarshal(data, &plan); err != nil {
		panic(err)
	}
	return plan
}

func TestGoldenHarnessPlan(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	want := loadPlanFixture("harness_golden.plan.json")
	want.GraphHash = g.GraphHash
	if !planEqual(plan, want) {
		t.Fatalf("plan mismatch: got %s want %s", mustJSON(plan), mustJSON(want))
	}
}

func TestGoldenAuthorPlan(t *testing.T) {
	g := loadGraphFixture("author_golden.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	want := loadPlanFixture("author_golden.plan.json")
	want.GraphHash = g.GraphHash
	if !planEqual(plan, want) {
		t.Fatalf("plan mismatch: got %s want %s", mustJSON(plan), mustJSON(want))
	}
}

func TestPlanStability(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	p1, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	p2, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if mustJSON(p1) != mustJSON(p2) {
		t.Fatal("plan is not deterministic")
	}
}

func TestNegativeUnknownNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_unknown.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("UNKNOWN classification must not be ready")
	}
}

func TestNegativeStaleHeadNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_stale_head.graph.json")
	plan, err := Plan(g, "0000000000000000000000000000000000000000")
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("stale head must not be ready")
	}
}

func TestNegativePathConflictNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_path_conflict.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("path conflict must not be ready")
	}
}

func TestNegativeForbiddenPrototypeDepNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_forbidden_proto_dep.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("forbidden prototype dependency must not be ready")
	}
}

func TestNegativeDesignAuthorityNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_design_authority.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("unresolved design authority must not be ready")
	}
}

func TestNegativeFolderMoveNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_folder_move.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("folder-move graduation must not be ready")
	}
}

func TestNegativeModuleVisibilityNotReady(t *testing.T) {
	g := loadNegativeGraph("negative_module_visibility.graph.json")
	plan, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if plan.Ready {
		t.Fatal("prototype-only module visibility must not be ready")
	}
}

func TestPlanDoesNotMutateGraph(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	before := mustJSON(g)
	_, err := Plan(g, g.SourceHeadSHA)
	if err != nil {
		t.Fatal(err)
	}
	if mustJSON(g) != before {
		t.Fatal("Plan mutated input graph")
	}
}

func loadNegativeGraph(name string) DependencyGraph {
	path := filepath.Join("fixtures", name)
	data, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	var g DependencyGraph
	if err := json.Unmarshal(data, &g); err != nil {
		panic(err)
	}
	if err := BindGraphHash(&g); err != nil {
		panic(err)
	}
	return g
}

func planEqual(a, b IntegratePlan) bool {
	return mustJSON(a) == mustJSON(b)
}

func mustJSON(v interface{}) string {
	b, err := json.Marshal(v)
	if err != nil {
		panic(err)
	}
	return string(b)
}
