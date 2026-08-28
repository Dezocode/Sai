package integrateplanner

const (
	SchemaGraph = "foundry.graph.v1"
	SchemaPlan  = "foundry.integrate.plan.v1"
)

type Classification string

const (
	ClassReuse         Classification = "REUSE"
	ClassPromote       Classification = "PROMOTE"
	ClassExport        Classification = "EXPORT"
	ClassRemote        Classification = "REMOTE"
	ClassPromoteShared Classification = "PROMOTE_SHARED"
	ClassDrop          Classification = "DROP"
	ClassUnknown       Classification = "UNKNOWN"
)

type GraphNode struct {
	ID                     string         `json:"id"`
	Path                   string         `json:"path"`
	Classification         Classification `json:"classification"`
	ProposedProductionPath string         `json:"proposed_production_path,omitempty"`
	DesignAuthority        string         `json:"design_authority,omitempty"`
	ModuleVisibility       string         `json:"module_visibility,omitempty"`
}

type GraphEdge struct {
	From           string         `json:"from"`
	To             string         `json:"to"`
	Classification Classification `json:"classification"`
}

type DependencyGraph struct {
	Schema         string      `json:"schema"`
	PrototypeID    string      `json:"prototype_id"`
	SourceHeadSHA  string      `json:"source_head_sha"`
	GraphHash      string      `json:"graph_hash"`
	Nodes          []GraphNode `json:"nodes"`
	Edges          []GraphEdge `json:"edges"`
}

type PlanEntry struct {
	NodeID                 string         `json:"node_id"`
	Path                   string         `json:"path"`
	Classification         Classification `json:"classification"`
	Action                 string         `json:"action"`
	ProposedProductionPath string         `json:"proposed_production_path,omitempty"`
}

type PlanCheck struct {
	ID      string `json:"id"`
	Status  string `json:"status"`
	Message string `json:"message"`
}

type IntegratePlan struct {
	Schema                    string            `json:"schema"`
	SourceHeadSHA             string            `json:"source_head_sha"`
	GraphHash                 string            `json:"graph_hash"`
	PrototypeID               string            `json:"prototype_id"`
	Ready                     bool              `json:"ready"`
	Entries                   []PlanEntry       `json:"entries"`
	ProposedPaths             []string          `json:"proposed_paths"`
	DependencyClassifications map[string]string `json:"dependency_classifications"`
	Checks                    []PlanCheck       `json:"checks"`
	Blockers                  []string          `json:"blockers"`
	HumanSummary              string            `json:"human_summary"`
}
