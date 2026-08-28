package graduation

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"
)

type Engine struct {
	State      BindState
	Journal    *Journal
	Production []string
}

func NewEngine(state BindState) (*Engine, error) {
	if state.JournalPath == "" {
		state.JournalPath = filepath.Join(state.WorkDir, ".foundry", "journal.json")
	}
	if state.CandidatesRoot == "" {
		state.CandidatesRoot = filepath.Join(state.WorkDir, ".foundry", "candidates")
	}
	j, err := OpenJournal(state.JournalPath)
	if err != nil {
		return nil, err
	}
	if len(state.Production) == 0 {
		state.Production = []string{"production"}
	}
	return &Engine{State: state, Journal: j, Production: state.Production}, nil
}

func (e *Engine) Execute(plan Plan) ([]ExecutionResult, error) {
	if err := VerifyBindings(e.State, plan); err != nil {
		return nil, err
	}
	var out []ExecutionResult
	for _, op := range plan.Operations {
		if prior, ok, err := e.Journal.Lookup(op.IdempotencyKey, plan.PlanID); err != nil {
			return out, err
		} else if ok {
			out = append(out, ExecutionResult{Audit: *prior, Idempotent: true})
			continue
		}
		rec, err := e.runOperation(plan, op)
		if err != nil {
			return out, err
		}
		if err := e.Journal.Record(op.IdempotencyKey, plan.PlanID, rec); err != nil {
			return out, err
		}
		out = append(out, ExecutionResult{Audit: rec})
	}
	return out, nil
}

func (e *Engine) runOperation(plan Plan, op Operation) (AuditRecord, error) {
	switch op.Kind {
	case OpIntegrate:
		return e.execIntegrate(plan, op)
	case OpSpinoff:
		return e.execSpinoff(plan, op)
	case OpDeleteArchive:
		return e.execDeleteArchive(plan, op)
	default:
		return AuditRecord{}, fmt.Errorf("unsupported operation %s", op.Kind)
	}
}

func (e *Engine) execIntegrate(plan Plan, op Operation) (AuditRecord, error) {
	proto := op.PrototypePath
	if proto == "" {
		proto = "prototypes/plugins/foundry/test-widget"
	}
	branch := op.TargetBranch
	if branch == "" {
		branch = "foundry/integrate-candidate"
	}
	if branch == "main" {
		return AuditRecord{}, fmt.Errorf("integrate refuses direct main target")
	}
	branchDir := filepath.Join(e.State.CandidatesRoot, "integrate", branch)
	if err := os.MkdirAll(branchDir, 0755); err != nil {
		return AuditRecord{}, err
	}
	if err := copyTree(filepath.Join(e.State.RepoRoot, proto), filepath.Join(branchDir, "integrated")); err != nil {
		return AuditRecord{}, err
	}
	prCandidate := map[string]interface{}{
		"title":       "Foundry integrate candidate",
		"head":        branch,
		"base":        "main",
		"draft":       true,
		"ready":       false,
		"plan_id":     plan.PlanID,
		"source_sha":  plan.PrototypeHead,
		"graph_hash":  plan.GraphHash,
	}
	prPath := filepath.Join(branchDir, "production-pr-candidate.json")
	if err := writeJSON(prPath, prCandidate); err != nil {
		return AuditRecord{}, err
	}
	return AuditRecord{
		SourceSHA:      plan.PrototypeHead,
		PlanHash:       plan.PlanID,
		Operation:      OpIntegrate,
		IdempotencyKey: op.IdempotencyKey,
		Outputs:        []string{branchDir, prPath},
		FileMap:        map[string]string{"pr_candidate": prPath, "branch_dir": branchDir},
		ExecutedAt:     time.Now().UTC(),
	}, nil
}

func (e *Engine) execSpinoff(plan Plan, op Operation) (AuditRecord, error) {
	name := op.SpinoffName
	if name == "" {
		name = "foundry-spinoff-candidate"
	}
	if os.Getenv("GITHUB_TOKEN") == "" && os.Getenv("GH_TOKEN") == "" {
		// Repository creation blocked without owner token.
	}
	proto := op.PrototypePath
	if proto == "" {
		proto = "prototypes/plugins/foundry/test-widget"
	}
	outDir := filepath.Join(e.State.CandidatesRoot, "spinoff", name)
	if err := os.MkdirAll(outDir, 0755); err != nil {
		return AuditRecord{}, err
	}
	if err := copyTree(filepath.Join(e.State.RepoRoot, proto), filepath.Join(outDir, "app")); err != nil {
		return AuditRecord{}, err
	}
	prov := map[string]interface{}{
		"source_repo":    plan.Repo,
		"source_sha":     plan.PrototypeHead,
		"plan_id":        plan.PlanID,
		"graph_hash":     plan.GraphHash,
		"spinoff_name":   name,
		"github_create":  "blocked-without-owner-token",
		"materialized_at": time.Now().UTC().Format(time.RFC3339),
	}
	provPath := filepath.Join(outDir, "PROVENANCE.json")
	if err := writeJSON(provPath, prov); err != nil {
		return AuditRecord{}, err
	}
	return AuditRecord{
		SourceSHA:      plan.PrototypeHead,
		PlanHash:       plan.PlanID,
		Operation:      OpSpinoff,
		IdempotencyKey: op.IdempotencyKey,
		Outputs:        []string{outDir, provPath},
		FileMap:        map[string]string{"candidate_root": outDir, "provenance": provPath},
		ExecutedAt:     time.Now().UTC(),
	}, nil
}

func (e *Engine) execDeleteArchive(plan Plan, op Operation) (AuditRecord, error) {
	proto := op.PrototypePath
	if proto == "" {
		proto = "prototypes/plugins/foundry/test-widget"
	}
	if err := AssertNoProductionDependency(e.State.RepoRoot, proto, e.Production); err != nil {
		return AuditRecord{}, err
	}
	archiveRoot := filepath.Join(e.State.CandidatesRoot, "archive")
	if err := os.MkdirAll(archiveRoot, 0755); err != nil {
		return AuditRecord{}, err
	}
	stamp := time.Now().UTC().Format("20060102-150405")
	dest := filepath.Join(archiveRoot, filepath.Base(proto)+"-"+stamp)
	src := filepath.Join(e.State.RepoRoot, proto)
	if err := copyTree(src, dest); err != nil {
		return AuditRecord{}, err
	}
	if err := os.RemoveAll(src); err != nil {
		return AuditRecord{}, err
	}
	return AuditRecord{
		SourceSHA:      plan.PrototypeHead,
		PlanHash:       plan.PlanID,
		Operation:      OpDeleteArchive,
		IdempotencyKey: op.IdempotencyKey,
		Outputs:        []string{dest},
		FileMap:        map[string]string{"archived_to": dest, "removed": proto},
		ExecutedAt:     time.Now().UTC(),
	}, nil
}

func writeJSON(path string, v interface{}) error {
	b, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0644)
}

func copyTree(src, dst string) error {
	return filepath.Walk(src, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		target := filepath.Join(dst, rel)
		if info.IsDir() {
			return os.MkdirAll(target, info.Mode())
		}
		return copyFile(path, target, info.Mode())
	})
}

func copyFile(src, dst string, mode os.FileMode) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
		return err
	}
	out, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, mode)
	if err != nil {
		return err
	}
	defer out.Close()
	_, err = io.Copy(out, in)
	return err
}
