package integrateplanner

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"path/filepath"
	"sort"
	"strings"
)

type graphHashBody struct {
	Schema         string      `json:"schema"`
	PrototypeID    string      `json:"prototype_id"`
	SourceHeadSHA  string      `json:"source_head_sha"`
	Nodes          []GraphNode `json:"nodes"`
	Edges          []GraphEdge `json:"edges"`
}

func ParseGraphJSON(data []byte) (DependencyGraph, error) {
	var g DependencyGraph
	if err := json.Unmarshal(data, &g); err != nil {
		return DependencyGraph{}, err
	}
	if err := ValidateGraph(g); err != nil {
		return DependencyGraph{}, err
	}
	return g, nil
}

func ValidateGraph(g DependencyGraph) error {
	if g.Schema != SchemaGraph {
		return fmt.Errorf("unsupported schema: %q", g.Schema)
	}
	if g.PrototypeID == "" {
		return fmt.Errorf("prototype_id required")
	}
	if len(g.SourceHeadSHA) != 40 {
		return fmt.Errorf("source_head_sha must be 40 characters")
	}
	if g.GraphHash == "" {
		return fmt.Errorf("graph_hash required")
	}
	want, err := ComputeGraphHash(g)
	if err != nil {
		return err
	}
	if g.GraphHash != want {
		return fmt.Errorf("graph_hash mismatch: got %s want %s", g.GraphHash, want)
	}
	seen := map[string]bool{}
	for _, n := range g.Nodes {
		if n.ID == "" {
			return fmt.Errorf("node id required")
		}
		if seen[n.ID] {
			return fmt.Errorf("duplicate node id: %s", n.ID)
		}
		seen[n.ID] = true
		if err := validateClassification(n.Classification); err != nil {
			return fmt.Errorf("node %s: %w", n.ID, err)
		}
		if _, err := normalizePath(n.Path); err != nil {
			return fmt.Errorf("node %s: %w", n.ID, err)
		}
	}
	for _, e := range g.Edges {
		if e.From == "" || e.To == "" {
			return fmt.Errorf("edge endpoints required")
		}
		if !seen[e.From] || !seen[e.To] {
			return fmt.Errorf("edge references unknown node: %s -> %s", e.From, e.To)
		}
		if err := validateClassification(e.Classification); err != nil {
			return fmt.Errorf("edge %s->%s: %w", e.From, e.To, err)
		}
	}
	return nil
}

func ComputeGraphHash(g DependencyGraph) (string, error) {
	nodes := append([]GraphNode(nil), g.Nodes...)
	sort.Slice(nodes, func(i, j int) bool { return nodes[i].ID < nodes[j].ID })
	edges := append([]GraphEdge(nil), g.Edges...)
	sort.Slice(edges, func(i, j int) bool {
		if edges[i].From != edges[j].From {
			return edges[i].From < edges[j].From
		}
		return edges[i].To < edges[j].To
	})
	body := graphHashBody{
		Schema:        g.Schema,
		PrototypeID:   g.PrototypeID,
		SourceHeadSHA: g.SourceHeadSHA,
		Nodes:         nodes,
		Edges:         edges,
	}
	b, err := json.Marshal(body)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:]), nil
}

func BindGraphHash(g *DependencyGraph) error {
	h, err := ComputeGraphHash(*g)
	if err != nil {
		return err
	}
	g.GraphHash = h
	return nil
}

func validateClassification(c Classification) error {
	switch c {
	case ClassReuse, ClassPromote, ClassExport, ClassRemote, ClassPromoteShared, ClassDrop, ClassUnknown:
		return nil
	case "":
		return fmt.Errorf("classification unresolved")
	default:
		return fmt.Errorf("unknown classification: %q", c)
	}
}

func normalizePath(p string) (string, error) {
	p = filepath.Clean(filepath.ToSlash(strings.TrimSpace(p)))
	if p == "." || p == ".." || strings.HasPrefix(p, "../") || strings.Contains(p, "/../") {
		return "", fmt.Errorf("invalid path: %s", p)
	}
	return p, nil
}
