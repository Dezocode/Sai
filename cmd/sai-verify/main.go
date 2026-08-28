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
	PLACEHOLDER_REMAINDER_OF_MAIN_GO_FILE