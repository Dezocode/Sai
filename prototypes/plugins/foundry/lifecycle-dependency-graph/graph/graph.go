package graph

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const ToolVersion = "foundry-lifecycle-graph/1"

type Node struct {
	ID             string `json:"id"`
	Path           string `json:"path"`
	Classification string `json:"classification"`
}

type Edge struct {
	From           string `json:"from"`
	To             string `json:"to"`
	Classification string `json:"classification"`
}

type Provenance struct {
	Repo          string `json:"repo"`
	Base          string `json:"base"`
	Head          string `json:"head"`
	SchemaVersion int    `json:"schema_version"`
	ToolVersion   string `json:"tool_version"`
}

type Output struct {
	Provenance Provenance `json:"provenance"`
	ManifestID string     `json:"manifest_id"`
	Nodes      []Node     `json:"nodes"`
	Edges      []Edge     `json:"edges"`
	GraphHash  string     `json:"graph_hash"`
}

type Deps struct {
	Nodes []Node `json:"nodes"`
	Edges []Edge `json:"edges"`
}

type BuildInput struct {
	Repo     string
	Base     string
	Head     string
	Manifest Manifest
	Deps     Deps
}

type DepSpec struct {
	Repo        string
	Base        string
	Head        string
	FixtureRoot string
}

func ParseDeps(data []byte) (Deps, error) {
	var deps Deps
	if err := json.Unmarshal(data, &deps); err != nil {
		return Deps{}, err
	}
	return deps, nil
}

func normalizePath(p string) (string, error) {
	p = filepath.Clean(filepath.ToSlash(strings.TrimSpace(p)))
	if p == "." || p == ".." || strings.HasPrefix(p, "../") || strings.Contains(p, "/../") {
		return "", fmt.Errorf("invalid path: %s", p)
	}
	return p, nil
}

func Build(in BuildInput) (Output, error) {
	if in.Repo == "" || in.Base == "" || in.Head == "" {
		return Output{}, fmt.Errorf("provenance repo, base, and head required")
	}
	if len(in.Head) != 40 {
		return Output{}, fmt.Errorf("head must be 40 characters")
	}
	out := Output{
		Provenance: Provenance{
			Repo:          in.Repo,
			Base:          in.Base,
			Head:          in.Head,
			SchemaVersion: SchemaVersion,
			ToolVersion:   ToolVersion,
		},
		ManifestID: in.Manifest.ID,
	}
	seen := map[string]bool{}
	for _, n := range in.Deps.Nodes {
		if n.ID == "" {
			return Output{}, fmt.Errorf("node id required")
		}
		if seen[n.ID] {
			return Output{}, fmt.Errorf("duplicate node id: %s", n.ID)
		}
		seen[n.ID] = true
		path, err := normalizePath(n.Path)
		if err != nil {
			return Output{}, err
		}
		if err := validateClassification(n.Classification); err != nil {
			return Output{}, err
		}
		n.Path = path
		out.Nodes = append(out.Nodes, n)
	}
	sort.Slice(out.Nodes, func(i, j int) bool { return out.Nodes[i].ID < out.Nodes[j].ID })
	for _, e := range in.Deps.Edges {
		if e.From == "" || e.To == "" {
			return Output{}, fmt.Errorf("edge endpoints required")
		}
		if !seen[e.From] || !seen[e.To] {
			return Output{}, fmt.Errorf("edge references unknown node: %s -> %s", e.From, e.To)
		}
		if err := validateClassification(e.Classification); err != nil {
			return Output{}, err
		}
		out.Edges = append(out.Edges, e)
	}
	sort.Slice(out.Edges, func(i, j int) bool {
		if out.Edges[i].From != out.Edges[j].From {
			return out.Edges[i].From < out.Edges[j].From
		}
		return out.Edges[i].To < out.Edges[j].To
	})
	hash, err := canonicalHash(out)
	if err != nil {
		return Output{}, err
	}
	out.GraphHash = hash
	return out, nil
}

func (spec DepSpec) Build() (Output, error) {
	manifestPath := filepath.Join(spec.FixtureRoot, "manifest.json")
	depsPath := filepath.Join(spec.FixtureRoot, "deps.json")
	mb, err := os.ReadFile(manifestPath)
	if err != nil {
		return Output{}, err
	}
	db, err := os.ReadFile(depsPath)
	if err != nil {
		return Output{}, err
	}
	manifest, err := ParseManifest(mb)
	if err != nil {
		return Output{}, err
	}
	deps, err := ParseDeps(db)
	if err != nil {
		return Output{}, err
	}
	return Build(BuildInput{
		Repo:     spec.Repo,
		Base:     spec.Base,
		Head:     spec.Head,
		Manifest: manifest,
		Deps:     deps,
	})
}

func ValidateForPlanning(o Output) error {
	for _, n := range o.Nodes {
		if err := validateClassification(n.Classification); err != nil {
			return fmt.Errorf("node %s: %w", n.ID, err)
		}
	}
	for _, e := range o.Edges {
		if err := validateClassification(e.Classification); err != nil {
			return fmt.Errorf("edge %s->%s: %w", e.From, e.To, err)
		}
	}
	return nil
}

func ValidateHeadBinding(o Output, wantHead string) error {
	if len(wantHead) != 40 {
		return fmt.Errorf("want head must be 40 characters")
	}
	if o.Provenance.Head != wantHead {
		return fmt.Errorf("stale head binding: got %s want %s", o.Provenance.Head, wantHead)
	}
	return nil
}

func ValidateGraphHashBinding(o Output, wantHash string) error {
	if wantHash == "" {
		return fmt.Errorf("want graph_hash required")
	}
	if o.GraphHash != wantHash {
		return fmt.Errorf("stale graph_hash binding: got %s want %s", o.GraphHash, wantHash)
	}
	return nil
}
