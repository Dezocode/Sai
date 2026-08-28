package integrateplanner

const (
	SchemaVersionGraph = "foundry.dependency-graph/v1"
	SchemaVersionPlan  = "foundry.integrate-plan/v1"
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

type NodeKind string

const (
	KindSwift    NodeKind = "swift"
	KindGo       NodeKind = "go"
	KindOpenAPI  NodeKind = "openapi"
	KindDesign   NodeKind = "design"
	KindResource NodeKind = "resource"
)

type DependencyGraph struct {
	SchemaVersion    string      `json:"schema_version"`
	PrototypeID      string      `json:"prototype_id"`
	PrototypeRoot    string      `json:"prototype_root"`
	PrototypeHeadSHA string      `json:"prototype_head_sha"`
	GraphHash        string      `json:"graph_hash"`
	Nodes            []GraphNode `json:"nodes"`
	Edges            []GraphEdge `json:"edges"`
}

type GraphNode struct {
	ID             string         `json:"id"`
	Path           string         `json:"path"`
	Kind           NodeKind       `json:"kind"`
	Classification Classification `json:"classification"`
}

type GraphEdge struct {
	From string `json:"from"`
	To   string `json:"to"`
}

type PlanStatus string

const (
	StatusPlanned PlanStatus = "PLANNED"
	StatusBlocked PlanStatus = "BLOCKED"
)

type ArtifactPlan struct {
	NodeID                 string         `json:"node_id"`
	SourcePath             string         `json:"source_path"`
	Classification         Classification `json:"classification"`
	Action                 string         `json:"action"`
	ProposedProductionPath string         `json:"proposed_production_path,omitempty"`
	Checks                 []string       `json:"checks"`
	Blockers               []string       `json:"blockers"`
}

type IntegratePlan struct {
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
}
