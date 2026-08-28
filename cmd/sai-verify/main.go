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
	pathRe  = regexp.MustCompile(`(?:\./)?(?:\.ai|\.cursor|\.github|\.githooks|scripts|openclaw-dashboard|cmd|apps|api|design|docs|internal|deploy|migrations|prototypes)(/[A-Za-z0-9_.*{},-]+)+|\.gitignore|(?:AGENTS|CLAUDE|CODEX|OPENCLAW|README|Team)\.md|go\.mod`)
	rmRe    = regexp.MustCompile(`(?i)^Removal-authorized:\s*(.+)$`)
	h2Re    = regexp.MustCompile(`^## `)
	allEv   = []string{"sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop", "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought", "workspaceOpen"}
	matchEv = map[string]bool{"preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "beforeShellExecution": true, "afterShellExecution": true, "beforeReadFile": true, "afterFileEdit": true, "subagentStart": true, "subagentStop": true}
)
func jq(s string) string { b, _ := json.Marshal(s); return string(b) }
