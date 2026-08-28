package main
import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)
const mapDir = ".cursor/skills/verify-sai/features"
var (
	linkRe  = regexp.MustCompile(`\]\((?:\./)?([^)]+\.md)\)`)
	idRe    = regexp.MustCompile("`([a-z][a-z0-9-]*)`")
	pathRe  = regexp.MustCompile(`(?:\./)?(?:\.ai|\.cursor|\.github|\.githooks|scripts|openclaw-dashboard|prototypes|cmd|apps|api|design|docs|internal|deploy|migrations)(/[A-Za-z0-9_.*{},-]+)+|\.gitignore|(?:AGENTS|CLAUDE|CODEX|OPENCLAW|README|Team)\.md|go\.mod`)
	rmRe    = regexp.MustCompile(`(?i)^Removal-authorized:\s*(.+)$`)
	h2Re    = regexp.MustCompile(`^## `)
	allEv   = []string{"sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop", "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought", "workspaceOpen"}
	matchEv = map[string]bool{"preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "beforeShellExecution": true, "afterShellExecution": true, "beforeReadFile": true, "afterFileEdit": true, "subagentStart": true, "subagentStop": true}
)
type feat struct {
	ID, Title, File, Desc string
	Subs [][2]string
	Ent, Proof, Paths, Rm, Unreach, Gotchas []string
}
type hit struct {
	ID string `json:"id"`
	Title string `json:"title"`
	Why string `json:"why"`
	Subs []string `json:"subfeatures"`
	Entries []string `json:"entry_points"`
	Proofs []string `json:"proofs"`
	Paths []string `json:"affected_paths_or_surfaces"`
	Gotchas []string `json:"gotchas"`
}
type snap struct {
	Repo string `json:"repo"`
	Base string `json:"base"`
	Head string `json:"head"`
	Path string `json:"path,omitempty"`
	Tool string `json:"tool,omitempty"`
	Dirty bool `json:"dirty"`
	OK bool `json:"ok"`
	Err string `json:"err,omitempty"`
	MapValid bool `json:"map_valid"`
	MapFiles int `json:"map_files"`
	MapFeatures int `json:"map_features"`
	MapSubs int `json:"map_subfeatures"`
	MapEntries int `json:"map_entry_points"`
	IDs []string `json:"ids"`
	Problems []string `json:"problems,omitempty"`
	PreserveOK bool `json:"preserve_ok"`
	Missing []string `json:"missing,omitempty"`
	Weakened []string `json:"weakened,omitempty"`
	Relevant []hit `json:"features"`
	HooksOK bool `json:"hooks_ok"`
	HookPre bool `json:"hook_pre"`
	HookPost bool `json:"hook_post"`
	HookStop bool `json:"hook_stop"`
	HookMatcher string `json:"hook_matcher"`
	HookFailClosed bool `json:"hook_fail_closed"`
	HookEvents []string `json:"hook_events"`
	MaintRequired bool `json:"maintenance_required"`
	MaintReason string `json:"maintenance_reason,omitempty"`
	Obligations []string `json:"obligations"`
	Unreachable []string `json:"unreachable"`
	ImplFiles int `json:"impl_files"`
	ImplLOC int `json:"impl_loc"`
	ImplFuncs int `json:"impl_funcs"`
	MaintStatus string `json:"maintenance_status"`
	MaintHead string `json:"maintenance_head,omitempty"`
	MaintMapHash string `json:"maintenance_map_hash,omitempty"`
	Completeness string `json:"whole_repo_completeness"`
	EvidenceBound bool `json:"evidence_bound"`
	Unmapped []string `json:"unmapped,omitempty"`
}
func main() { os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr)) }
