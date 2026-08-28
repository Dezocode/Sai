package integrateplanner

import (
	"strings"
	"testing"
)

func TestComputeGraphHashMatchesFixture(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	h, err := ComputeGraphHash(g)
	if err != nil {
		t.Fatal(err)
	}
	if h != g.GraphHash {
		t.Fatalf("hash %s != fixture %s", h, g.GraphHash)
	}
}

func TestValidateGraphRejectsHashMismatch(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	g.GraphHash = "0000000000000000000000000000000000000000000000000000000000000000"
	if err := ValidateGraph(g); err == nil {
		t.Fatal("expected graph_hash mismatch")
	}
}

func TestValidateGraphRejectsDuplicateNodeID(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	g.Nodes = append(g.Nodes, g.Nodes[0])
	if err := BindGraphHash(&g); err != nil {
		t.Fatal(err)
	}
	if err := ValidateGraph(g); err == nil {
		t.Fatal("expected duplicate node id error")
	}
}

func TestValidateGraphRejectsDanglingEdge(t *testing.T) {
	g := loadGraphFixture("harness_golden.graph.json")
	g.Edges = append(g.Edges, GraphEdge{From: "missing", To: g.Nodes[0].ID, Classification: ClassReuse})
	if err := BindGraphHash(&g); err != nil {
		t.Fatal(err)
	}
	if err := ValidateGraph(g); err == nil {
		t.Fatal("expected dangling edge error")
	}
}

func TestRenderHumanSummaryListsBlockers(t *testing.T) {
	plan := IntegratePlan{
		PrototypeID:   "sai-harness",
		SourceHeadSHA: "1111111111111111111111111111111111111111",
		Blockers:      []string{"stale head", "UNKNOWN node"},
	}
	summary := RenderHumanSummary(plan)
	if !strings.Contains(summary, "BLOCKED") || !strings.Contains(summary, "stale head") {
		t.Fatalf("summary missing blockers: %s", summary)
	}
}
