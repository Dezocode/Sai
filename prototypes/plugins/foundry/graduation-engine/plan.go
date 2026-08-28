package graduation

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strings"
)

var (
	sha40 = regexp.MustCompile(`^[a-f0-9]{40}$`)
	sha64 = regexp.MustCompile(`^[a-f0-9]{64}$`)
)

func ValidDisposition(d Disposition) bool {
	switch d {
	case DispositionReuse, DispositionPromote, DispositionExport, DispositionRemote, DispositionPromoteShared, DispositionDrop:
		return true
	default:
		return false
	}
}

func canonicalOperations(ops []Operation) ([]byte, error) {
	cp := make([]Operation, len(ops))
	copy(cp, ops)
	sort.Slice(cp, func(i, j int) bool {
		if cp[i].Kind != cp[j].Kind {
			return cp[i].Kind < cp[j].Kind
		}
		return cp[i].IdempotencyKey < cp[j].IdempotencyKey
	})
	return json.Marshal(cp)
}

func ComputePlanID(p Plan) (string, error) {
	opsJSON, err := canonicalOperations(p.Operations)
	if err != nil {
		return "", err
	}
	h := sha256.New()
	for _, s := range []string{
		fmt.Sprintf("%d", p.SchemaVersion),
		p.Repo,
		p.Base,
		p.PrototypeHead,
		p.GraphHash,
		string(opsJSON),
	} {
		h.Write([]byte(s))
		h.Write([]byte("\n"))
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

func ValidatePlan(p *Plan) error {
	if p.SchemaVersion != SchemaVersion {
		return fmt.Errorf("schema_version mismatch: want %d got %d", SchemaVersion, p.SchemaVersion)
	}
	if p.Repo == "" {
		return fmt.Errorf("repo required")
	}
	if !sha40.MatchString(p.Base) {
		return fmt.Errorf("invalid base")
	}
	if !sha40.MatchString(p.PrototypeHead) {
		return fmt.Errorf("invalid prototype_head")
	}
	if !sha64.MatchString(p.GraphHash) {
		return fmt.Errorf("invalid graph_hash")
	}
	if len(p.Operations) == 0 {
		return fmt.Errorf("operations required")
	}
	for _, nd := range p.Dispositions {
		if !ValidDisposition(nd.Disposition) {
			return fmt.Errorf("invalid disposition for %s: %s", nd.Path, nd.Disposition)
		}
		if strings.EqualFold(string(nd.Disposition), "UNKNOWN") {
			return fmt.Errorf("UNKNOWN disposition fails closed")
		}
	}
	for _, op := range p.Operations {
		if op.IdempotencyKey == "" {
			return fmt.Errorf("idempotency_key required for %s", op.Kind)
		}
		if !op.OwnerConfirmed {
			return fmt.Errorf("owner confirmation required for %s", op.Kind)
		}
		switch op.Kind {
		case OpIntegrate, OpSpinoff, OpDeleteArchive:
		default:
			return fmt.Errorf("unsupported operation kind %q", op.Kind)
		}
	}
	want, err := ComputePlanID(*p)
	if err != nil {
		return err
	}
	if p.PlanID != "" && p.PlanID != want {
		return fmt.Errorf("plan_id mismatch: want %s got %s", want, p.PlanID)
	}
	p.PlanID = want
	return nil
}
