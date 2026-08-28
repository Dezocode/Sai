package graduation

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
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
	h := sha256.New()
	err := filepath.Walk(abs, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(abs, path)
		if err != nil {
			return err
		}
		b, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		h.Write([]byte(rel))
		h.Write(b)
		return nil
	})
	if err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
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
	return nil
}
