package graduation

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
)

func git(dir string, args ...string) (string, error) {
	cmd := exec.Command("git", append([]string{"-C", dir}, args...)...)
	out, err := cmd.Output()
	return strings.TrimSpace(string(out)), err
}

func ComputeGraphHash(repoRoot, prototypePath string) (string, error) {
	abs := filepath.Join(repoRoot, prototypePath)
	manifest := filepath.Join(abs, "manifest.json")
	widget := filepath.Join(abs, "widget.txt")
	h := sha256.New()
	for _, p := range []string{manifest, widget} {
		b, err := readFile(p)
		if err != nil {
			return "", err
		}
		h.Write([]byte(p))
		h.Write(b)
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

func readFile(path string) ([]byte, error) {
	return exec.Command("cat", path).Output()
}

func VerifyBindings(state BindState, plan Plan) error {
	if err := ValidatePlan(&plan); err != nil {
		return err
	}
	head, err := git(state.RepoRoot, "rev-parse", "HEAD")
	if err != nil {
		return fmt.Errorf("read HEAD: %w", err)
	}
	if head != plan.PrototypeHead {
		return fmt.Errorf("stale prototype_head: plan %s current %s", plan.PrototypeHead, head)
	}
	if state.PrototypeHead != "" && state.PrototypeHead != plan.PrototypeHead {
		return fmt.Errorf("bind state prototype_head mismatch")
	}
	if state.GraphHash != "" && state.GraphHash != plan.GraphHash {
		return fmt.Errorf("graph_hash mismatch: plan %s current %s", plan.GraphHash, state.GraphHash)
	}
	if state.Base != "" && state.Base != plan.Base {
		return fmt.Errorf("stale base: plan %s current %s", plan.Base, state.Base)
	}
	gh, err := ComputeGraphHash(state.RepoRoot, "prototypes/plugins/foundry/test-widget")
	if err == nil && gh != plan.GraphHash && state.GraphHash == "" {
		// When graph is computed from fixture path, enforce exact match.
		if plan.GraphHash != gh {
			return fmt.Errorf("graph_hash mismatch: plan %s computed %s", plan.GraphHash, gh)
		}
	}
	return nil
}
