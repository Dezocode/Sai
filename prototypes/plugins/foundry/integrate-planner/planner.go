package integrateplanner

import (
	"fmt"
	"path/filepath"
	"sort"
	"strings"
)

func Plan(g DependencyGraph, requestedHeadSHA string) (IntegratePlan, error) {
	if err := ValidateGraph(g); err != nil {
		return IntegratePlan{}, err
	}
	plan := IntegratePlan{
		SchemaVersion: SchemaVersionPlan,
		PrototypeID:   g.PrototypeID,
		SourceHeadSHA: requestedHeadSHA,
		GraphHash:     g.GraphHash,
		Status:        StatusPlanned,
	}
	blockers := []string{}
	if g.PrototypeHeadSHA != requestedHeadSHA {
		blockers = append(blockers, fmt.Sprintf("stale prototype head: graph binds %s requested %s", g.PrototypeHeadSHA, requestedHeadSHA))
	}
	if isExportOnlyIntegrate(g) {
		blockers = append(blockers, "integrate path unavailable: graph is EXPORT-only")
	}
	blockers = append(blockers, forbiddenDeps(g)...)

	promoteTargets := map[string]string{}
	nodes := append([]GraphNode(nil), g.Nodes...)
	sort.Slice(nodes, func(i, j int) bool { return nodes[i].ID < nodes[j].ID })

	for _, node := range nodes {
		art := planArtifact(node, g)
		if isFolderMove(node, g.PrototypeRoot) {
			art.Blockers = append(art.Blockers, "folder-move graduation forbidden")
		}
		if art.ProposedProductionPath != "" {
			if prev, ok := promoteTargets[art.ProposedProductionPath]; ok {
				art.Blockers = append(art.Blockers, fmt.Sprintf("production path conflict: %s and %s -> %s", prev, node.ID, art.ProposedProductionPath))
			} else {
				promoteTargets[art.ProposedProductionPath] = node.ID
			}
		}
		plan.Artifacts = append(plan.Artifacts, art)
		blockers = append(blockers, art.Blockers...)
	}

	plan.Blockers = uniqueSorted(blockers)
	plan.RequiredChecks = collectChecks(plan.Artifacts)
	if len(plan.Blockers) > 0 {
		plan.Status = StatusBlocked
		plan.Ready = false
	} else {
		plan.Status = StatusPlanned
		plan.Ready = true
	}
	plan.HumanSummary = RenderHumanSummary(plan)
	return plan, nil
}

func planArtifact(node GraphNode, g DependencyGraph) ArtifactPlan {
	art := ArtifactPlan{
		NodeID:         node.ID,
		SourcePath:     node.Path,
		Classification: node.Classification,
		Checks:         []string{},
		Blockers:       []string{},
	}
	switch node.Classification {
	case ClassReuse:
		art.Action = "reuse_production"
	case ClassRemote:
		art.Action = "declare_remote"
		art.Checks = []string{"remote-boundary-review"}
	case ClassDrop:
		art.Action = "drop_prototype"
	case ClassExport:
		art.Action = "export_only"
		art.Blockers = append(art.Blockers, "EXPORT classification is not integratable")
	case ClassPromoteShared:
		art.Action = "promote_shared_blocked"
		art.Blockers = append(art.Blockers, "PROMOTE_SHARED requires prior production capability")
	case ClassPromote:
		art.Action = "promote_to_production"
		art.ProposedProductionPath = proposeProductionPath(node, g.PrototypeRoot)
		art.Checks = checksForKind(node.Kind)
	case ClassUnknown:
		art.Action = "unresolved"
		art.Blockers = append(art.Blockers, "UNKNOWN classification blocks planning")
	}
	return art
}

func proposeProductionPath(node GraphNode, root string) string {
	rel := strings.TrimPrefix(node.Path, root)
	rel = strings.TrimPrefix(rel, "/")
	switch node.Kind {
	case KindGo:
		return filepath.ToSlash(filepath.Join("internal", rel))
	case KindSwift:
		return filepath.ToSlash(filepath.Join("apps/Sai/Features", rel))
	case KindOpenAPI:
		return filepath.ToSlash(filepath.Join("api", rel))
	case KindDesign:
		return filepath.ToSlash(filepath.Join("design/review", rel))
	default:
		return filepath.ToSlash(filepath.Join("internal/resources", rel))
	}
}

func checksForKind(k NodeKind) []string {
	switch k {
	case KindGo:
		return []string{"production-authority-review", "go-vet", "sai-verify-preserve"}
	case KindSwift:
		return []string{"production-authority-review", "sai-design-check"}
	case KindOpenAPI:
		return []string{"production-authority-review", "openapi-contract-review"}
	case KindDesign:
		return []string{"production-authority-review", "design-language-review"}
	default:
		return []string{"production-authority-review"}
	}
}

func isFolderMove(node GraphNode, root string) bool {
	root = strings.TrimSuffix(root, "/")
	path := strings.TrimSuffix(node.Path, "/")
	if path == root {
		return true
	}
	if node.Classification == ClassPromote && strings.Count(strings.TrimPrefix(path, root), "/") == 0 {
		return true
	}
	return false
}

func isExportOnlyIntegrate(g DependencyGraph) bool {
	hasPromote := false
	hasExport := false
	for _, n := range g.Nodes {
		if n.Classification == ClassPromote || n.Classification == ClassPromoteShared {
			hasPromote = true
		}
		if n.Classification == ClassExport {
			hasExport = true
		}
	}
	return hasExport && !hasPromote
}

func forbiddenDeps(g DependencyGraph) []string {
	byID := map[string]GraphNode{}
	for _, n := range g.Nodes {
		byID[n.ID] = n
	}
	var out []string
	for _, e := range g.Edges {
		from, to := byID[e.From], byID[e.To]
		if from.Classification == ClassPromote && to.Classification == ClassExport {
			out = append(out, fmt.Sprintf("forbidden dependency: %s (PROMOTE) -> %s (EXPORT)", e.From, e.To))
		}
		if to.Classification == ClassUnknown {
			out = append(out, fmt.Sprintf("forbidden dependency on UNKNOWN node: %s -> %s", e.From, e.To))
		}
	}
	return out
}

func collectChecks(arts []ArtifactPlan) []string {
	set := map[string]bool{}
	for _, a := range arts {
		if len(a.Blockers) > 0 {
			continue
		}
		for _, c := range a.Checks {
			set[c] = true
		}
	}
	return mapKeysSorted(set)
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
	return jsonMarshalPlan(clone)
}

func jsonMarshalPlan(plan IntegratePlan) ([]byte, error) {
	import_json := struct {
		SchemaVersion  string         `json:"schema_version"`
		PrototypeID    string         `json:"prototype_id"`
		SourceHeadSHA  string         `json:"source_head_sha"`
		GraphHash      string         `json:"graph_hash"`
		Ready          bool           `json:"ready"`
		Status         PlanStatus     `json:"status"`
		Artifacts      []ArtifactPlan `json:"artifacts"`
		Blockers       []string       `json:"blockers"`
		RequiredChecks []string       `json:"required_checks"`
		HumanSummary   string         `json:"human_summary"`
	}{
		SchemaVersion:  plan.SchemaVersion,
		PrototypeID:    plan.PrototypeID,
		SourceHeadSHA:  plan.SourceHeadSHA,
		GraphHash:      plan.GraphHash,
		Ready:          plan.Ready,
		Status:         plan.Status,
		Artifacts:      plan.Artifacts,
		Blockers:       plan.Blockers,
		RequiredChecks: plan.RequiredChecks,
		HumanSummary:   plan.HumanSummary,
	}
	return json.Marshal(import_json)
}
