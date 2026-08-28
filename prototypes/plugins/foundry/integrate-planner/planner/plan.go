package planner

import (
	"fmt"
	"sort"
	"strings"
)

// BuildPlan produces a deterministic integrate plan for graph g bound to expectedHeadSHA.
func BuildPlan(g *Graph, expectedHeadSHA string) Plan {
	plan := Plan{
		Schema:                    PlanSchema,
		SourceHeadSHA:             g.SourceHeadSHA,
		GraphHash:                 g.GraphHash,
		PrototypeID:               g.PrototypeID,
		Ready:                     true,
		Entries:                   []Entry{},
		ProposedPaths:             []string{},
		DependencyClassifications: map[string]Classification{},
		Checks:                    []Check{},
		Blockers:                  []Blocker{},
	}

	if expectedHeadSHA != "" && g.SourceHeadSHA != expectedHeadSHA {
		plan.addBlocker("stale_head", "", "", fmt.Sprintf("graph source_head_sha %s does not match expected %s", g.SourceHeadSHA, expectedHeadSHA))
	}
	if want := CanonicalGraphHash(g); want != g.GraphHash {
		plan.addBlocker("stale_graph", "", "", fmt.Sprintf("graph_hash %s does not match canonical %s", g.GraphHash, want))
	}

	nodes := append([]Node(nil), g.Nodes...)
	sort.Slice(nodes, func(i, j int) bool { return nodes[i].ID < nodes[j].ID })

	promoteTargets := map[string]string{}
	for _, n := range nodes {
		entry, blockers := classifyNode(n)
		plan.Entries = append(plan.Entries, entry)
		for _, b := range blockers {
			plan.addBlocker(b.Code, b.NodeID, b.Path, b.Message)
		}
		if entry.Classification == ClassPromote && entry.ProposedProductionPath != "" {
			if other, ok := promoteTargets[entry.ProposedProductionPath]; ok {
				plan.addBlocker("path_conflict", n.ID, entry.ProposedProductionPath,
					fmt.Sprintf("production path %q already claimed by node %q", entry.ProposedProductionPath, other))
			} else {
				promoteTargets[entry.ProposedProductionPath] = n.ID
				plan.ProposedPaths = append(plan.ProposedPaths, entry.ProposedProductionPath)
			}
		}
	}

	edges := append([]Edge(nil), g.Edges...)
	sort.Slice(edges, func(i, j int) bool {
		if edges[i].From != edges[j].From {
			return edges[i].From < edges[j].From
		}
		return edges[i].To < edges[j].To
	})
	for _, e := range edges {
		key := e.From + "->" + e.To
		plan.DependencyClassifications[key] = e.Classification
		if e.Classification == ClassUnknown {
			plan.addBlocker("unknown_edge", e.From, e.To, fmt.Sprintf("edge %s has UNKNOWN classification", key))
		}
	}

	sort.Strings(plan.ProposedPaths)
	plan.Checks = buildChecks(&plan)
	plan.HumanSummary = buildSummary(&plan)
	return plan
}

func classifyNode(n Node) (Entry, []Blocker) {
	entry := Entry{
		NodeID:         n.ID,
		Path:           n.Path,
		Classification: n.Classification,
	}
	var blockers []Blocker
	switch n.Classification {
	case ClassReuse:
		entry.Action = "reference_production"
	case ClassPromote:
		entry.Action = "promote_to_production"
		entry.ProposedProductionPath = n.ProposedProductionPath
		blockers = append(blockers, validatePromote(n)...)
	case ClassExport:
		entry.Action = "export_only"
		blockers = append(blockers, blocker("export_not_integrate", n.ID, n.Path, "EXPORT is not a valid integrate graduation path"))
	case ClassRemote:
		entry.Action = "document_remote_boundary"
	case ClassPromoteShared:
		entry.Action = "await_shared_capability"
		blockers = append(blockers, blocker("promote_shared_blocked", n.ID, n.Path, "PROMOTE_SHARED requires an existing shared production capability"))
	case ClassDrop:
		entry.Action = "no_integration"
	case ClassUnknown:
		entry.Action = "blocked"
		blockers = append(blockers, blocker("unknown_classification", n.ID, n.Path, "UNKNOWN classification blocks integrate planning"))
	}
	return entry, blockers
}

func validatePromote(n Node) []Blocker {
	var out []Blocker
	p := strings.TrimSpace(n.ProposedProductionPath)
	if p == "" {
		out = append(out, blocker("missing_promote_path", n.ID, n.Path, "PROMOTE requires proposed_production_path"))
		return out
	}
	if isPrototypeRootPath(p) {
		out = append(out, blocker("folder_move_forbidden", n.ID, p, "folder-move graduation of prototype plugin root is forbidden"))
	}
	if !isAllowedPromotePath(p) {
		out = append(out, blocker("forbidden_promote_path", n.ID, p, "proposed path is outside allowed production roots"))
	}
	if !isResolvedDesignAuthority(n.DesignAuthority) {
		out = append(out, blocker("design_authority_unresolved", n.ID, p, "design authority must be resolved before PROMOTE"))
	}
	if !isSupportedModuleVisibility(n.ModuleVisibility) {
		out = append(out, blocker("module_visibility_unsupported", n.ID, p, fmt.Sprintf("module_visibility %q is not supported", n.ModuleVisibility)))
	}
	return out
}

func blocker(code, nodeID, path, msg string) Blocker {
	return Blocker{Code: code, NodeID: nodeID, Path: path, Message: msg}
}

func (p *Plan) addBlocker(code, nodeID, path, msg string) {
	p.Blockers = append(p.Blockers, blocker(code, nodeID, path, msg))
	p.Ready = false
}

func buildChecks(p *Plan) []Check {
	checks := []Check{
		{ID: "head_binding", Status: "pass", Message: "graph bound to source_head_sha"},
		{ID: "graph_hash", Status: "pass", Message: "graph_hash matches canonical digest"},
		{ID: "folder_move", Status: "pass", Message: "no folder-move graduation proposed"},
	}
	for i, c := range checks {
		for _, b := range p.Blockers {
			switch b.Code {
			case "stale_head":
				if c.ID == "head_binding" {
					checks[i].Status, checks[i].Message = "fail", b.Message
				}
			case "stale_graph":
				if c.ID == "graph_hash" {
					checks[i].Status, checks[i].Message = "fail", b.Message
				}
			case "folder_move_forbidden":
				if c.ID == "folder_move" {
					checks[i].Status, checks[i].Message = "fail", b.Message
				}
			}
		}
	}
	if len(p.Blockers) > 0 {
		checks = append(checks, Check{ID: "blockers", Status: "fail", Message: fmt.Sprintf("%d blocker(s) present", len(p.Blockers))})
	} else {
		checks = append(checks, Check{ID: "blockers", Status: "pass", Message: "no blockers"})
	}
	return checks
}

func buildSummary(p *Plan) string {
	if !p.Ready {
		return fmt.Sprintf("Integrate plan for %s is NOT READY: %d blocker(s).", p.PrototypeID, len(p.Blockers))
	}
	return fmt.Sprintf("Integrate plan for %s is READY with %d entries and %d proposed production path(s).", p.PrototypeID, len(p.Entries), len(p.ProposedPaths))
}
