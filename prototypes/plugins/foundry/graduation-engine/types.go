package graduation

import "time"

const SchemaVersion = 1

type Disposition string

const (
	DispositionReuse         Disposition = "REUSE"
	DispositionPromote       Disposition = "PROMOTE"
	DispositionExport        Disposition = "EXPORT"
	DispositionRemote        Disposition = "REMOTE"
	DispositionPromoteShared Disposition = "PROMOTE_SHARED"
	DispositionDrop          Disposition = "DROP"
)

type OperationKind string

const (
	OpIntegrate     OperationKind = "integrate"
	OpSpinoff       OperationKind = "spinoff"
	OpDeleteArchive OperationKind = "delete-archive"
)

type NodeDisposition struct {
	Path        string      `json:"path"`
	Disposition Disposition `json:"disposition"`
}

type Operation struct {
	Kind           OperationKind `json:"kind"`
	IdempotencyKey string        `json:"idempotency_key"`
	PrototypePath  string        `json:"prototype_path,omitempty"`
	TargetBranch   string        `json:"target_branch,omitempty"`
	SpinoffName    string        `json:"spinoff_name,omitempty"`
	OwnerConfirmed bool          `json:"owner_confirmed"`
}

type Plan struct {
	PlanID        string            `json:"plan_id"`
	SchemaVersion int               `json:"schema_version"`
	Repo          string            `json:"repo"`
	Base          string            `json:"base"`
	PrototypeHead string            `json:"prototype_head"`
	GraphHash     string            `json:"graph_hash"`
	GeneratedAt   time.Time         `json:"generated_at,omitempty"`
	Operations    []Operation       `json:"operations"`
	Dispositions  []NodeDisposition `json:"dispositions"`
	Recovery      []string          `json:"recovery,omitempty"`
}

type AuditRecord struct {
	SourceSHA      string            `json:"source_sha"`
	PlanHash       string            `json:"plan_hash"`
	Operation      OperationKind     `json:"operation"`
	IdempotencyKey string            `json:"idempotency_key"`
	Outputs        []string          `json:"outputs"`
	FileMap        map[string]string `json:"file_map"`
	ExecutedAt     time.Time         `json:"executed_at"`
}

type ExecutionResult struct {
	Audit      AuditRecord `json:"audit"`
	Idempotent bool        `json:"idempotent"`
}

type BindState struct {
	RepoRoot       string
	PrototypeHead  string
	GraphHash      string
	Base           string
	WorkDir        string
	JournalPath    string
	CandidatesRoot string
	Production     []string
}
