package planner

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

var validClassifications = map[Classification]bool{
	ClassReuse: true, ClassPromote: true, ClassExport: true, ClassRemote: true,
	ClassPromoteShared: true, ClassDrop: true, ClassUnknown: true,
}

// ParseGraphJSON decodes and validates a foundry.graph.v1 document.
func ParseGraphJSON(data []byte) (Graph, error) {
	var g Graph
	if err := json.Unmarshal(data, &g); err != nil {
		return Graph{}, fmt.Errorf("parse graph: %w", err)
	}
	if err := ValidateGraph(&g); err != nil {
		return Graph{}, err
	}
	return g, nil
}

// ValidateGraph checks schema, bindings, and canonical hash.
func ValidateGraph(g *Graph) error {
	if g.Schema != GraphSchema {
		return fmt.Errorf("unsupported schema %q", g.Schema)
	}
	if g.PrototypeID == "" {
		return fmt.Errorf("prototype_id is required")
	}
	if len(g.SourceHeadSHA) != 40 {
		return fmt.Errorf("source_head_sha must be 40 characters")
	}
	ids := map[string]bool{}
	for _, n := range g.Nodes {
		if n.ID == "" {
			return fmt.Errorf("node id is required")
		}
		if ids[n.ID] {
			return fmt.Errorf("duplicate node id %q", n.ID)
		}
		ids[n.ID] = true
		if !validClassifications[n.Classification] {
			return fmt.Errorf("node %q has invalid classification %q", n.ID, n.Classification)
		}
	}
	for _, e := range g.Edges {
		if !ids[e.From] || !ids[e.To] {
			return fmt.Errorf("edge %s->%s references unknown node", e.From, e.To)
		}
		if !validClassifications[e.Classification] {
			return fmt.Errorf("edge %s->%s has invalid classification", e.From, e.To)
		}
	}
	want := CanonicalGraphHash(g)
	if g.GraphHash != want {
		return fmt.Errorf("graph_hash mismatch: got %q want %q", g.GraphHash, want)
	}
	return nil
}

// CanonicalGraphHash returns SHA-256 of the graph with graph_hash cleared.
func CanonicalGraphHash(g *Graph) string {
	clone := *g
	clone.GraphHash = ""
	sort.Slice(clone.Nodes, func(i, j int) bool { return clone.Nodes[i].ID < clone.Nodes[j].ID })
	sort.Slice(clone.Edges, func(i, j int) bool {
		a, b := clone.Edges[i], clone.Edges[j]
		if a.From != b.From {
			return a.From < b.From
		}
		return a.To < b.To
	})
	b, _ := json.Marshal(clone)
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:])
}

func isPrototypeRootPath(p string) bool {
	p = strings.Trim(p, "/")
	parts := strings.Split(p, "/")
	if len(parts) == 3 && parts[0] == "prototypes" && parts[1] == "plugins" && parts[2] != "" {
		return true
	}
	if len(parts) == 4 && parts[0] == "prototypes" && parts[1] == "plugins" && parts[2] != "" && parts[3] == "" {
		return true
	}
	return false
}

func isAllowedPromotePath(p string) bool {
	p = strings.Trim(p, "/")
	return strings.HasPrefix(p, "apps/SaiFeatures/") ||
		strings.HasPrefix(p, "design/") ||
		strings.HasPrefix(p, "internal/") ||
		strings.HasPrefix(p, "api/")
}

func isResolvedDesignAuthority(v string) bool {
	switch strings.ToLower(strings.TrimSpace(v)) {
	case "resolved", "production", "dezocode", "monaecode":
		return true
	default:
		return false
	}
}

func isSupportedModuleVisibility(v string) bool {
	switch strings.ToLower(strings.TrimSpace(v)) {
	case "", "public", "internal", "package":
		return true
	default:
		return false
	}
}
