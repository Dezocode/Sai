package planner

// Classification values consumed from slice 78 dependency graphs.
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

const (
	GraphSchema = "foundry.graph.v1"
	PlanSchema  = "foundry.integrate.plan.v1"
)

// Graph is a validated foundry.graph.v1 document.
type Graph struct {
	Schema        string `json:"schema"`
	PrototypeID   string `json:"prototype_id"`
	SourceHeadSHA string `json:"source_head_sha"`
	GraphHash     string `json:"graph_hash"`
	Nodes         []Node `json:"nodes"`
	Edges         []Edge `json:"edges"`
}

// Node is one classified artifact in the graph.
type Node struct {
	ID                     string         `json:"id"`
	Path                   string         `json:"path"`
	Classification         Classification `json:"classification"`
	ProposedProductionPath string         `json:"proposed_production_path,omitempty"`
	DesignAuthority        string         `json:"design_authority,omitempty"`
	ModuleVisibility       string         `json:"module_visibility,omitempty"`
	Notes                  string         `json:"notes,omitempty"`
}

// Edge is a classified dependency between nodes.
type Edge struct {
	From           string         `json:"from"`
	To             string         `json:"to"`
	Classification Classification `json:"classification"`
}

// Plan is deterministic integrate planner output.
type Plan struct {
	Schema                    string                      `json:"schema"`
	SourceHeadSHA             string                      `json:"source_head_sha"`
	GraphHash                 string                      `json:"graph_hash"`
	PrototypeID               string                      `json:"prototype_id"`
	Ready                     bool                        `json:"ready"`
	Entries                   []Entry                     `json:"entries"`
	ProposedPaths             []string                    `json:"proposed_paths"`
	DependencyClassifications map[string]Classification `json:"dependency_classifications"`
	Checks                    []Check                     `json:"checks"`
	Blockers                  []Blocker                   `json:"blockers"`
	HumanSummary              string                      `json:"human_summary"`
}

// Entry records the integrate action for one node.
type Entry struct {
	NodeID                 string         `json:"node_id"`
	Path                   string         `json:"path"`
	Classification         Classification `json:"classification"`
	Action                 string         `json:"action"`
	ProposedProductionPath string         `json:"proposed_production_path,omitempty"`
}

// Check records a planner self-check.
type Check struct {
	ID      string `json:"id"`
	Status  string `json:"status"`
	Message string `json:"message"`
}

// Blocker prevents ready=true.
type Blocker struct {
	Code    string `json:"code"`
	NodeID  string `json:"node_id,omitempty"`
	Path    string `json:"path,omitempty"`
	Message string `json:"message"`
}
