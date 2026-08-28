package integrateplanner

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

func Plan(g DependencyGraph, requestedHeadSHA string) (IntegratePlan, error) {
	if err := ValidateGraph(g); err != nil {
		return IntegratePlan{}, err
	}
	if len(requestedHeadSHA) != 40 {
		return IntegratePlan{}, fmt.Errorf("requested head must be 40 characters")
	}

	blockers := []string{}
	entries := []PlanEntry{}
	depClass := map[string]string{}
	promoteTargets := map[string]string{}

	nodes := append([]GraphNode(nil), g.Nodes...)
	sort.Slice(nodes, func(i, j int) bool { return nodes[i].ID < nodes[j].ID })

	nodeByID := make(map[string]GraphNode, len(nodes))
	for _, node := range nodes {
		nodeByID[node.ID] = node
	}

	for _, node := range nodes {
		entry, nodeBlockers := planEntry(node, g.PrototypeID)
		if entry.ProposedProductionPath != "" {
			if prev, ok := promoteTargets[entry.ProposedProductionPath]; ok {
				nodeBlockers = append(nodeBlockers, fmt.Sprintf("production path conflict: %s and %s -> %s", prev, node.ID, entry.ProposedProductionPath))
			} else {
				promoteTargets[entry.ProposedProductionPath] = node.ID
			}
		}
		entries = append(entries, entry)
		blockers = append(blockers, nodeBlockers...)
	}

	for _, e := range g.Edges {
		key := e.From + "->" + e.To
		depClass[key] = string(e.Classification)
		if e.Classification == ClassUnknown {
			blockers = append(blockers, fmt.Sprintf("edge %s has UNKNOWN classification", key))
		}
		to, ok := nodeByID[e.To]
		if ok && isOtherPrototypePath(to.Path, g.PrototypeID) {
			switch e.Classification {
			case ClassReuse, ClassPromote:
				blockers = append(blockers, fmt.Sprintf("edge %s: forbidden prototype dependency on %s", key, to.Path))
			}
		}
	}

	for _, node := range nodes {
		if node.Classification == ClassReuse && isOtherPrototypePath(node.Path, g.PrototypeID) {
			blockers = append(blockers, fmt.Sprintf("node %s: REUSE cannot reference prototype path %s", node.ID, node.Path))
		}
	}

	if g.SourceHeadSHA != requestedHeadSHA {
		blockers = append(blockers, fmt.Sprintf("stale prototype head: graph binds %s requested %s", g.SourceHeadSHA, requestedHeadSHA))
	}

	blockers = uniqueSorted(blockers)
	checks := buildChecks(g, requestedHeadSHA, blockers)
	ready := len(blockers) == 0

	plan := IntegratePlan{
		Schema:                    SchemaPlan,
		SourceHeadSHA:             requestedHeadSHA,
		GraphHash:                 g.GraphHash,
		PrototypeID:               g.PrototypeID,
		Ready:                     ready,
		Entries:                   entries,
		ProposedPaths:             collectProposedPaths(entries, blockers),
		DependencyClassifications: depClass,
		Checks:                    checks,
		Blockers:                  blockers,
	}
	plan.HumanSummary = RenderHumanSummary(plan)
	return plan, nil
}

func planEntry(node GraphNode, prototypeID string) (PlanEntry, []string) {
	var blockers []string
	entry := PlanEntry{
		NodeID:         node.ID,
		Path:           node.Path,
		Classification: node.Classification,
	}
	switch node.Classification {
	case ClassReuse:
		entry.Action = "reference_production"
	case ClassRemote:
		entry.Action = "document_remote_boundary"
	case ClassDrop:
		entry.Action = "no_integration"
	case ClassExport:
		entry.Action = "export_only"
		blockers = append(blockers, fmt.Sprintf("node %s: EXPORT is not integratable", node.ID))
	case ClassPromoteShared:
		entry.Action = "promote_shared_blocked"
		blockers = append(blockers, fmt.Sprintf("node %s: PROMOTE_SHARED blocks integrate until shared capability exists", node.ID))
	case ClassUnknown:
		entry.Action = "unresolved"
		blockers = append(blockers, fmt.Sprintf("node %s: UNKNOWN classification blocks planning", node.ID))
	case ClassPromote:
		entry.Action = "promote_to_production"
		entry.ProposedProductionPath = node.ProposedProductionPath
		if entry.ProposedProductionPath == "" {
			blockers = append(blockers, fmt.Sprintf("node %s: PROMOTE requires proposed_production_path", node.ID))
		}
		if strings.HasPrefix(entry.ProposedProductionPath, "prototypes/") {
			blockers = append(blockers, fmt.Sprintf("node %s: proposed production path remains in prototype tree", node.ID))
		}
		if node.DesignAuthority == "" || node.DesignAuthority == "unresolved" {
			blockers = append(blockers, fmt.Sprintf("node %s: unresolved design authority", node.ID))
		}
		if node.ModuleVisibility == "prototype-only" || node.ModuleVisibility == "private" {
			blockers = append(blockers, fmt.Sprintf("node %s: unsupported module visibility %q", node.ID, node.ModuleVisibility))
		}
		if isFolderMovePath(node.Path, entry.ProposedProductionPath, prototypeID) {
			blockers = append(blockers, fmt.Sprintf("node %s: folder-move graduation forbidden", node.ID))
		}
	}
	return entry, blockers
}

func isFolderMovePath(sourcePath, proposedPath, prototypeID string) bool {
	root := "prototypes/plugins/" + prototypeID
	sourcePath = strings.TrimSuffix(sourcePath, "/")
	proposedPath = strings.TrimSuffix(proposedPath, "/")
	if sourcePath == root || proposedPath == root {
		return true
	}
	if proposedPath == "prototypes/plugins/"+prototypeID {
		return true
	}
	return false
}

func isOtherPrototypePath(path, selfPrototypeID string) bool {
	if !strings.HasPrefix(path, "prototypes/plugins/") {
		return false
	}
	rest := strings.TrimPrefix(path, "prototypes/plugins/")
	lane := rest
	if i := strings.Index(rest, "/"); i >= 0 {
		lane = rest[:i]
	}
	return lane != "" && lane != selfPrototypeID
}

func buildChecks(g DependencyGraph, requestedHeadSHA string, blockers []string) []PlanCheck {
	headStatus, headMsg := "pass", "graph bound to source_head_sha"
	if g.SourceHeadSHA != requestedHeadSHA {
		headStatus, headMsg = "fail", "source_head_sha does not match requested head"
	}
	folderStatus, folderMsg := "pass", "no folder-move graduation proposed"
	for _, b := range blockers {
		if strings.Contains(b, "folder-move") {
			folderStatus, folderMsg = "fail", "folder-move graduation detected"
			break
		}
	}
	blockerStatus, blockerMsg := "pass", "no blockers"
	if len(blockers) > 0 {
		blockerStatus, blockerMsg = "fail", "plan has blockers"
	}
	return []PlanCheck{
		{ID: "head_binding", Status: headStatus, Message: headMsg},
		{ID: "graph_hash", Status: "pass", Message: "graph_hash matches canonical digest"},
		{ID: "folder_move", Status: folderStatus, Message: folderMsg},
		{ID: "blockers", Status: blockerStatus, Message: blockerMsg},
	}
}

func collectProposedPaths(entries []PlanEntry, blockers []string) []string {
	if len(blockers) > 0 {
		return nil
	}
	set := map[string]bool{}
	for _, e := range entries {
		if e.ProposedProductionPath != "" {
			set[e.ProposedProductionPath] = true
		}
	}
	out := make([]string, 0, len(set))
	for p := range set {
		out = append(out, p)
	}
	sort.Strings(out)
	return out
}

func uniqueSorted(in []string) []string {
	return mapKeysSorted(sliceSet(in))
}

func sliceSet(in []string) map[string]bool {
	m := map[string]bool{}
	for _, s := range in {
		if s != "" {
			m[s] = true
		}
	}
	return m
}

func mapKeysSorted(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func CanonicalPlanJSON(plan IntegratePlan) ([]byte, error) {
	clone := plan
	clone.HumanSummary = RenderHumanSummary(plan)
	return json.Marshal(clone)
}
