package graduation

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const (
	CanonicalPrototypeRoot   = "prototypes/plugins/"
	DefaultPrototypePath     = "prototypes/plugins/foundry/test-widget"
	SaiDesignLanguageDefault = "default"
)

var dispositionByOp = map[OperationKind][]Disposition{
	OpIntegrate:     {DispositionPromote, DispositionPromoteShared},
	OpSpinoff:       {DispositionExport},
	OpDeleteArchive: {DispositionDrop},
}

func NormalizePrototypePath(path string) string {
	if path == "" {
		return DefaultPrototypePath
	}
	return filepath.ToSlash(path)
}

func ValidateCanonicalPrototypePath(path string) error {
	norm := NormalizePrototypePath(path)
	if strings.Contains(norm, "..") {
		return fmt.Errorf("prototype path traversal rejected: %s", path)
	}
	if !strings.HasPrefix(norm, CanonicalPrototypeRoot) {
		return fmt.Errorf("prototype path outside canonical root %s: %s", CanonicalPrototypeRoot, norm)
	}
	return nil
}

func dispositionForPath(plan Plan, protoPath string) (Disposition, bool) {
	norm := NormalizePrototypePath(protoPath)
	for _, nd := range plan.Dispositions {
		if NormalizePrototypePath(nd.Path) == norm {
			return nd.Disposition, true
		}
	}
	return "", false
}

func EnforceDisposition(plan Plan, op Operation) error {
	proto := ResolvePrototypePath(plan, op)
	disp, ok := dispositionForPath(plan, proto)
	if !ok {
		return fmt.Errorf("no disposition for prototype path %s", proto)
	}
	for _, allowed := range dispositionByOp[op.Kind] {
		if disp == allowed {
			return nil
		}
	}
	return fmt.Errorf("disposition %s not allowed for operation %s", disp, op.Kind)
}

func ResolvePrototypePath(plan Plan, op Operation) string {
	if op.PrototypePath != "" {
		return NormalizePrototypePath(op.PrototypePath)
	}
	if len(plan.Dispositions) > 0 {
		return NormalizePrototypePath(plan.Dispositions[0].Path)
	}
	return DefaultPrototypePath
}

func PrimaryPrototypePath(plan Plan) string {
	if len(plan.Dispositions) > 0 {
		return NormalizePrototypePath(plan.Dispositions[0].Path)
	}
	for _, op := range plan.Operations {
		if op.PrototypePath != "" {
			return NormalizePrototypePath(op.PrototypePath)
		}
	}
	return DefaultPrototypePath
}

func ValidatePrototypePolicy(repoRoot, protoPath string) error {
	if err := ValidateCanonicalPrototypePath(protoPath); err != nil {
		return err
	}
	manifestPath := filepath.Join(repoRoot, NormalizePrototypePath(protoPath), "manifest.json")
	b, err := os.ReadFile(manifestPath)
	if err != nil {
		return fmt.Errorf("prototype manifest required: %w", err)
	}
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(b, &raw); err != nil {
		return fmt.Errorf("invalid manifest.json: %w", err)
	}
	if v, ok := raw["featureUIAllowed"]; ok {
		var allowed bool
		if err := json.Unmarshal(v, &allowed); err != nil {
			return fmt.Errorf("invalid featureUIAllowed in manifest")
		}
		if allowed {
			return fmt.Errorf("featureUIAllowed must be false")
		}
	}
	if v, ok := raw["sai_design_language"]; ok {
		var lang string
		if err := json.Unmarshal(v, &lang); err != nil {
			return fmt.Errorf("invalid sai_design_language in manifest")
		}
		if lang != SaiDesignLanguageDefault {
			return fmt.Errorf("sai_design_language must be %q, got %q", SaiDesignLanguageDefault, lang)
		}
	}
	return nil
}
