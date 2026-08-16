package main

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"syscall"
	"time"
)

type Action string
type Status string

const (
	ActImplement  Action = "IMPLEMENT"
	ActWaitCI     Action = "WAIT_CI"
	ActWaitSaul   Action = "WAIT_SAUL"
	ActRemediate  Action = "REMEDIATE"
	ActReady      Action = "READY_FOR_HUMAN_REVIEW"
	ActObserve    Action = "OBSERVE"
	StMissing     Status = "missing"
	StPending     Status = "pending"
	StPass        Status = "pass"
	StFail        Status = "fail"
	StStale       Status = "stale"
	DecisionAllow        = "ALLOW"
	DecisionDeny         = "DENY"
	checkRalph           = "Ralph / Program State"
	checkSaul            = "Saul / Product Quality"
	schemaB              = "ralph-blocker-v1"
	schemaBs             = "ralph-blockers-v1"
	schemaE              = "saul-evidence-v2"
	signDom              = "SAI_SAUL_EVIDENCE_V2\n"
	marker               = "<!-- RALPH-BLOCKERS:v1 -->"
	awaitVal             = "IMPLEMENTED_AWAITING_VALIDATION"
)

var (
	readOnly     = fields("Read Grep Glob SemanticSearch WebSearch WebFetch GetMcpTools FetchMcpResource ReadLints AwaitShell Task TodoWrite SwitchMode CallMcpTool")
	mutate       = fields("Write StrReplace Delete EditNotebook ApplyPatch")
	shellRead    = []string{"git status", "git log", "git diff", "git show", "git rev-parse", "git merge-base", "git fetch", "git branch", "git remote", "git rev-list", "git cat-file", "go test", "go run ./ralph", "go fmt", "go vet", "go env", "go version", "scripts/verify-", "./scripts/verify-", "gh pr view", "gh api ", "gh run ", "python3 -m json.tool", "pwd", "ls", "true"}
	shellMut     = []string{"git add", "git commit", "git push"}
	ghAPI        = "https://api.github.com"
	doHTTP       = func(req *http.Request) (*http.Response, error) { return http.DefaultClient.Do(req) }
	headOverride string
	rootOverride string
	testWorld    *World
)

func fields(s string) map[string]bool {
	m := map[string]bool{}
	for _, x := range strings.Fields(s) {
		m[x] = true
	}
	return m
}

type Appl struct {
	Mode    string `json:"mode"`
	HeadSHA string `json:"head_sha"`
}
type EvRef struct {
	Message     string `json:"message"`
	EvidenceRef string `json:"evidence_ref"`
}
type Blocker struct {
	SchemaVersion       string   `json:"schema_version"`
	ID                  string   `json:"id"`
	SourceKind          string   `json:"source_kind"`
	SourceID            string   `json:"source_id"`
	SourceActor         string   `json:"source_actor"`
	Repository          string   `json:"repository"`
	PR                  int      `json:"pr"`
	HeadSHA             string   `json:"head_sha"`
	Applicability       Appl     `json:"applicability"`
	Severity            string   `json:"severity"`
	Blocking            bool     `json:"blocking"`
	Status              string   `json:"status"`
	Priority            int      `json:"priority"`
	Objective           string   `json:"objective"`
	Scope               []string `json:"scope"`
	DependsOn           []string `json:"depends_on"`
	Acceptance          []string `json:"acceptance"`
	ResolutionAuthority string   `json:"resolution_authority"`
	Evidence            []EvRef  `json:"evidence"`
	CreatedAt           string   `json:"created_at"`
	UpdatedAt           string   `json:"updated_at"`
	Actionable          bool     `json:"actionable,omitempty"`
}
type WorkItem struct {
	ID         string   `json:"work_item_id"`
	BlockerIDs []string `json:"blocker_ids"`
	BaseSHA    string   `json:"base_sha"`
	Objective  string   `json:"objective"`
	Scope      []string `json:"scope"`
	Acceptance []string `json:"acceptance"`
	DependsOn  []string `json:"depends_on"`
	Priority   int      `json:"priority"`
	Evidence   []string `json:"evidence_refs"`
	HeadSHA    string   `json:"head_sha"`
	GrantID    string   `json:"grant_id"`
	Status     string   `json:"status"`
}
type Grant struct {
	WorkItem, HeadSHA, Objective string
	Scope                        []string
}
type Disp struct {
	Kind     string   `json:"kind"`
	Grant    Grant    `json:"grant"`
	Head     string   `json:"head"`
	WorkItem WorkItem `json:"work_item"`
}
type Shard struct {
	ID     string   `json:"id"`
	Digest string   `json:"digest"`
	Paths  []string `json:"paths"`
	Status Status   `json:"status"`
}
type Review struct {
	SHA, Schema                       string
	Trusted                           bool
	Shards                            []Shard
	LocalArch, ImpactArch, SystemArch Status
	Blockers                          []Blocker
}
type State struct {
	SchemaVersion, Repository, ProgramID, HeadSHA, BaseSHA, CIAt, ReconciledAt string
	PR, Generation                                                             int
	Terminal                                                                   bool
	Phase, NextAction                                                          Action
	Blockers                                                                   []Blocker
	Workers                                                                    []WorkItem
	Grant                                                                      Grant
	Dispatch                                                                   Disp
	CI                                                                         Status
	Saul                                                                       Review
}
type Decision struct {
	Decision, Reason, HeadSHA, WorkItem, Objective, NextAction string
	Scope                                                      []string
}
type AuthReq struct{ HeadSHA, Path, WorkItem, Tool string }
type WorkerResult struct {
	WorkItem, BaseSHA, ResultSHA, Status string
	SetsReady                            bool
}
type Evidence struct {
	SchemaVersion      string    `json:"schema_version"`
	Repository         string    `json:"repository"`
	PR                 int       `json:"pr"`
	BaseSHA            string    `json:"base_sha"`
	HeadSHA            string    `json:"head_sha"`
	ManifestHash       string    `json:"manifest_hash"`
	ReviewerIdentity   string    `json:"reviewer_identity"`
	KeyID              string    `json:"key_id"`
	CheckRunID         int64     `json:"check_run_id"`
	CodexInvoked       bool      `json:"codex_invoked"`
	Synthetic          bool      `json:"synthetic"`
	RuntimeAttestation string    `json:"runtime_attestation"`
	Shards             []Shard   `json:"shards"`
	LocalArch          Status    `json:"local_arch"`
	ImpactArch         Status    `json:"impact_arch"`
	SystemArch         Status    `json:"system_arch"`
	Blockers           []Blocker `json:"blockers"`
	BlockerSetHash     string    `json:"blocker_set_hash"`
	Tests              []string  `json:"tests"`
	FinalDisposition   string    `json:"final_disposition"`
	Sig                string    `json:"signature,omitempty"`
}
type Producer struct {
	AppID     int64  `json:"app_id"`
	AppSlug   string `json:"app_slug"`
	CheckName string `json:"check_name"`
	Workflow  string `json:"workflow_path"`
}
type Envelope struct {
	SchemaVersion string    `json:"schema_version"`
	Repository    string    `json:"repository"`
	PR            int       `json:"pr"`
	HeadSHA       string    `json:"head_sha,omitempty"`
	Producer      *Producer `json:"producer,omitempty"`
	Blockers      []Blocker `json:"blockers"`
}
type hookIn struct {
	ToolName  string         `json:"tool_name"`
	ToolInput map[string]any `json:"tool_input"`
}
type ghCheck struct {
	ID         int64  `json:"id"`
	Name       string `json:"name"`
	HeadSHA    string `json:"head_sha"`
	Status     string `json:"status"`
	Conclusion string `json:"conclusion"`
	DetailsURL string `json:"details_url"`
	App        struct {
		ID   int64  `json:"id"`
		Slug string `json:"slug"`
	} `json:"app"`
	Output struct {
		Summary string `json:"summary"`
		Text    string `json:"text"`
	} `json:"output"`
}
type ghComment struct {
	ID, Body, HTMLURL, Assoc, Login string
}
type World struct {
	Repo, Head, Base string
	PR               int
	Comments         []ghComment
	Checks           []ghCheck
	Perms            map[string]string
}

func gitOut(args ...string) (string, error) {
	cmd := exec.Command("git", args...)
	if rootOverride != "" {
		cmd.Dir = rootOverride
	}
	out, err := cmd.Output()
	return strings.TrimSpace(string(out)), err
}
func gitPick(over, arg, errn string, min int) (string, error) {
	if over != "" {
		return over, nil
	}
	h, err := gitOut("rev-parse", arg)
	if err != nil || len(h) < min {
		return "", fmt.Errorf("%s", errn)
	}
	return h, nil
}
func gitHead() (string, error) {
	if headOverride != "" {
		return headOverride, nil
	}
	if os.Getenv("RALPH_WORLD") != "" {
		if w, err := resolveWorld(); err == nil && w.Head != "" {
			return w.Head, nil
		}
	}
	return gitPick("", "HEAD", "git HEAD", 7)
}
func gitRoot() (string, error) { return gitPick(rootOverride, "--show-toplevel", "git root", 1) }
func h8(s string) string {
	x := sha256.Sum256([]byte(s))
	return hex.EncodeToString(x[:8])
}
func now() string                 { return time.Now().UTC().Format(time.RFC3339) }
func shardUnits(s State) []string { return []string{"ralph"} }
func repoRel(path, root string) (string, error) {
	if path == "" || root == "" {
		return "", fmt.Errorf("empty path")
	}
	if !filepath.IsAbs(path) {
		path = filepath.Join(root, path)
	}
	clean := filepath.Clean(path)
	if st, err := os.Lstat(clean); err == nil && st.Mode()&os.ModeSymlink != 0 {
		if clean, err = filepath.EvalSymlinks(clean); err != nil {
			return "", fmt.Errorf("symlink")
		}
	}
	rel, err := filepath.Rel(filepath.Clean(root), clean)
	if err != nil || strings.HasPrefix(rel, "..") || filepath.IsAbs(rel) {
		return "", fmt.Errorf("escape")
	}
	return filepath.ToSlash(rel), nil
}
func applicable(b Blocker, head string) bool {
	if b.Status != "OPEN" || !b.Blocking {
		return false
	}
	if b.Applicability.Mode == "sticky" {
		return true
	}
	h := b.Applicability.HeadSHA
	if h == "" {
		h = b.HeadSHA
	}
	return h == "" || h == head
}
func depsReady(b Blocker, all []Blocker) bool {
	st := map[string]string{}
	for _, x := range all {
		st[x.ID] = x.Status
	}
	for _, d := range b.DependsOn {
		if st[d] != "RESOLVED" {
			return false
		}
	}
	return true
}
func awaiting(s State, id string) bool {
	for _, w := range s.Workers {
		if w.Status != awaitVal || w.BaseSHA != s.HeadSHA {
			continue
		}
		for _, x := range w.BlockerIDs {
			if x == id {
				return true
			}
		}
	}
	return false
}
func isActionable(b Blocker, s State) bool {
	return applicable(b, s.HeadSHA) && depsReady(b, s.Blockers) && len(b.Scope) > 0 && !awaiting(s, b.ID)
}
func hashBlockers(bs []Blocker) string {
	if bs == nil {
		bs = []Blocker{}
	}
	b, _ := json.Marshal(bs)
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:])
}
func saulConverged(s State) bool {
	r := s.Saul
	if !r.Trusted || r.SHA == "" || r.SHA != s.HeadSHA || r.Schema != schemaE {
		return false
	}
	got := map[string]Status{}
	for _, sh := range r.Shards {
		got[sh.ID] = sh.Status
	}
	for _, id := range shardUnits(s) {
		if got[id] != StPass {
			return false
		}
	}
	if r.LocalArch != StPass || r.ImpactArch != StPass || r.SystemArch != StPass {
		return false
	}
	for _, b := range s.Blockers {
		if b.SourceKind == "saul" && applicable(b, s.HeadSHA) {
			return false
		}
	}
	return true
}
func Ready(s State) bool {
	if s.CI != StPass || s.CIAt != s.HeadSHA || !saulConverged(s) {
		return false
	}
	for _, b := range s.Blockers {
		if applicable(b, s.HeadSHA) {
			return false
		}
	}
	return true
}
func pick(s State) *Blocker {
	var c []Blocker
	for _, b := range s.Blockers {
		if b.Actionable {
			c = append(c, b)
		}
	}
	sort.Slice(c, func(i, j int) bool {
		a, b := c[i], c[j]
		ra, rb := map[string]int{"P0": 0, "P1": 1, "P2": 2}[a.Severity], map[string]int{"P0": 0, "P1": 1, "P2": 2}[b.Severity]
		if ra != rb {
			return ra < rb
		}
		if a.Priority != b.Priority {
			return a.Priority < b.Priority
		}
		if a.CreatedAt != b.CreatedAt {
			return a.CreatedAt < b.CreatedAt
		}
		return a.ID < b.ID
	})
	if len(c) == 0 {
		return nil
	}
	return &c[0]
}
func Observe(head string, s State) State {
	if head == "" {
		head = s.HeadSHA
	}
	if s.HeadSHA != "" && head != s.HeadSHA {
		if s.CIAt != head {
			s.CI = StStale
		}
		s.Saul.Trusted = s.Saul.Trusted && s.Saul.SHA == head
		s.Grant, s.Dispatch = Grant{}, Disp{}
		for i := range s.Workers {
			if s.Workers[i].BaseSHA != head {
				s.Workers[i].Status = "STALE"
			}
		}
	}
	s.HeadSHA = head
	if s.BaseSHA == "" && len(head) == 40 {
		s.BaseSHA, _ = gitOut("merge-base", "HEAD", "origin/main")
	}
	return s
}
func inScope(rel string, scope []string) bool {
	if rel == "" || len(scope) == 0 {
		return false
	}
	rel = filepath.ToSlash(rel)
	for _, s := range scope {
		s = strings.TrimSuffix(strings.TrimSuffix(filepath.ToSlash(s), "/**"), "/")
		if rel == s || strings.HasPrefix(rel, s+"/") {
			return true
		}
	}
	return false
}
func findItem(s State, id string) *WorkItem {
	for i := range s.Workers {
		if s.Workers[i].ID == id && s.Workers[i].Status != "COMPLETE" && s.Workers[i].Status != "STALE" {
			return &s.Workers[i]
		}
	}
	return nil
}
func Authorize(s State, req AuthReq) Decision {
	s = Observe(req.HeadSHA, s)
	d := Decision{HeadSHA: s.HeadSHA, NextAction: string(s.NextAction), Decision: DecisionDeny}
	switch {
	case s.NextAction == ActReady:
		d.Reason = "PROGRAM_READY"
	case s.NextAction != ActImplement && s.NextAction != ActRemediate:
		d.Reason = string(s.NextAction) + "_REQUIRED"
	case s.Grant.WorkItem == "" || s.Grant.HeadSHA != s.HeadSHA:
		d.Reason = "NO_GRANT"
	case os.Getenv("RALPH_WORK_ITEM") != "" && os.Getenv("RALPH_WORK_ITEM") != s.Grant.WorkItem:
		d.Reason = "WORKER_SPOOF"
	case req.WorkItem != "" && req.WorkItem != s.Grant.WorkItem:
		d.Reason = "UNAUTHORIZED_WORK_ITEM"
	case req.HeadSHA != s.HeadSHA:
		d.Reason = "STALE_SHA"
	case req.Path != "" && !inScope(req.Path, s.Grant.Scope):
		d.Reason = "OUT_OF_SCOPE"
	default:
		return Decision{Decision: DecisionAllow, HeadSHA: s.HeadSHA, WorkItem: s.Grant.WorkItem, Scope: s.Grant.Scope, Objective: s.Grant.Objective, NextAction: string(s.NextAction)}
	}
	return d
}
func signMsg(e Evidence) ([]byte, error) {
	e.Sig = ""
	b, err := json.Marshal(e)
	if err != nil {
		return nil, err
	}
	return append([]byte(signDom), b...), nil
}
func canResolve(old, neu Blocker) bool {
	switch old.ResolutionAuthority {
	case "saul":
		return neu.SourceKind == "saul"
	case "ci":
		return (neu.SourceKind == "ci" || neu.SourceKind == "check") && neu.SourceID == old.SourceID
	case "ralph":
		return neu.SourceKind == "runtime" || neu.SourceKind == "primary"
	case "source_actor":
		return neu.SourceActor == old.SourceActor && neu.SourceKind == old.SourceKind
	case "owner":
		return neu.SourceKind == "comment"
	}
	return false
}
func mergeFrontier(prior, inc []Blocker, head string) []Blocker {
	m, order := map[string]Blocker{}, []string{}
	put := func(b Blocker) {
		if b.ID == "" {
			return
		}
		if b.SchemaVersion == "" {
			b.SchemaVersion = schemaB
		}
		old, ok := m[b.ID]
		if !ok {
			if b.Status == "RESOLVED" {
				return
			}
			m[b.ID], order = b, append(order, b.ID)
			return
		}
		if b.Status == "RESOLVED" {
			if canResolve(old, b) {
				old.Status, old.UpdatedAt = "RESOLVED", b.UpdatedAt
				m[b.ID] = old
			}
			return
		}
		if old.CreatedAt != "" {
			b.CreatedAt = old.CreatedAt
		}
		m[b.ID] = b
	}
	for _, b := range prior {
		put(b)
	}
	for _, b := range inc {
		put(b)
	}
	out := make([]Blocker, 0, len(order))
	for _, id := range order {
		out = append(out, m[id])
	}
	return out
}
func trusted(login, assoc string, perms map[string]string) bool {
	p := perms[login]
	return assoc == "OWNER" || p == "admin" || p == "maintain"
}
func parseEnv(body string) (Envelope, bool) {
	s := body
	if strings.Contains(body, marker) {
		rest := body[strings.Index(body, marker):]
		a := strings.Index(rest, "```")
		if a < 0 {
			return Envelope{}, false
		}
		rest = strings.TrimPrefix(strings.TrimSpace(rest[a+3:]), "json")
		b := strings.Index(rest, "```")
		if b < 0 {
			return Envelope{}, false
		}
		s = rest[:b]
	}
	var e Envelope
	if json.Unmarshal([]byte(strings.TrimSpace(s)), &e) != nil || e.SchemaVersion != schemaBs {
		return Envelope{}, false
	}
	return e, true
}
func blk(id, kind, src, actor, sev, auth, obj string, scope []string, sticky bool, head, repo string, pr int) Blocker {
	b := Blocker{SchemaVersion: schemaB, ID: id, SourceKind: kind, SourceID: src, SourceActor: actor, Repository: repo, PR: pr, HeadSHA: head, Severity: sev, Blocking: true, Status: "OPEN", Objective: obj, Scope: scope, ResolutionAuthority: auth, CreatedAt: now(), UpdatedAt: now()}
	if sticky {
		b.Applicability.Mode = "sticky"
	} else {
		b.Applicability = Appl{Mode: "exact_head", HeadSHA: head}
	}
	return b
}
func ingestTrustedComments(w World) []Blocker {
	var out []Blocker
	for _, c := range w.Comments {
		if !trusted(c.Login, c.Assoc, w.Perms) {
			continue
		}
		src := "github-comment:" + c.ID
		if e, ok := parseEnv(c.Body); ok && strings.Contains(c.Body, marker) {
			if e.Repository != w.Repo || e.PR != w.PR {
				continue
			}
			for _, b := range e.Blockers {
				if b.SchemaVersion != schemaB || b.ID == "" || (b.SourceID != "" && b.SourceID != src) {
					continue
				}
				b.SourceKind, b.SourceID, b.SourceActor, b.Repository, b.PR = "comment", src, c.Login, w.Repo, w.PR
				if b.Applicability.Mode == "" {
					b.Applicability.Mode = "sticky"
				}
				out = append(out, b)
			}
			continue
		}
		ln := strings.TrimSpace(strings.SplitN(strings.TrimSpace(c.Body), "\n", 2)[0])
		if strings.Contains(c.Body, "RALPH-BLOCKERS:v1") || !(strings.HasPrefix(ln, "BLOCKING") || strings.HasPrefix(ln, "**BLOCKING")) {
			continue
		}
		b := blk("COMMENT-"+c.ID, "comment", src, c.Login, "P1", "saul", "Satisfy trusted blocking comment "+c.HTMLURL, nil, true, w.Head, w.Repo, w.PR)
		b.Evidence = []EvRef{{Message: ln, EvidenceRef: c.HTMLURL}}
		out = append(out, b)
	}
	return out
}
func skipCheck(n string) bool {
	return n == checkRalph || n == "continue" || n == "Cursor Automation: Sai" || n == "merge-handoff-slack"
}
func ciRole(c ghCheck) bool {
	return !skipCheck(c.Name) && c.Name != checkSaul && (c.App.Slug == "github-actions" || c.App.ID == 15368 || c.App.Slug == "")
}
func srcCheck(c ghCheck) string {
	return fmt.Sprintf("check:%d/%s/%s", c.App.ID, c.App.Slug, c.Name)
}
func checkFail(c ghCheck) bool {
	if c.Status != "completed" {
		return false
	}
	switch c.Conclusion {
	case "failure", "action_required", "timed_out", "cancelled":
		return true
	}
	return false
}
func ingestChecks(w World) []Blocker {
	var out []Blocker
	for _, c := range w.Checks {
		if c.HeadSHA != "" && c.HeadSHA != w.Head {
			continue
		}
		if e, ok := parseEnv(c.Output.Text); ok && !strings.Contains(c.Output.Text, marker) {
			if e.Repository != w.Repo || e.PR != w.PR || (e.HeadSHA != "" && e.HeadSHA != w.Head) {
				continue
			}
			if p := e.Producer; p != nil && ((p.AppID != 0 && p.AppID != c.App.ID) || (p.AppSlug != "" && p.AppSlug != c.App.Slug) || (p.CheckName != "" && p.CheckName != c.Name)) {
				continue
			}
			for _, b := range e.Blockers {
				if b.SchemaVersion != schemaB || b.ID == "" {
					continue
				}
				if b.SourceKind == "" {
					b.SourceKind = "check"
				}
				if b.SourceID == "" {
					b.SourceID = srcCheck(c)
				}
				b.HeadSHA = w.Head
				out = append(out, b)
			}
			continue
		}
		if skipCheck(c.Name) || c.Status != "completed" {
			continue
		}
		id, src, kind := "CHECK-"+h8(fmt.Sprintf("%d/%s/%s", c.App.ID, c.App.Slug, c.Name)), srcCheck(c), "check"
		if ciRole(c) {
			kind = "ci"
		}
		if checkFail(c) {
			sc, auth := []string(nil), "ci"
			if ciRole(c) {
				sc = []string{"ralph/", ".github/workflows/", "scripts/"}
			}
			if c.Name == checkSaul {
				auth = "saul"
			}
			b := blk(id, kind, src, c.App.Slug, "P1", auth, "Make required Check "+c.Name+" pass on exact current HEAD", sc, false, w.Head, w.Repo, w.PR)
			b.Evidence = []EvRef{{Message: c.Conclusion, EvidenceRef: c.DetailsURL}}
			out = append(out, b)
			continue
		}
		if c.Conclusion == "success" {
			out = append(out, Blocker{SchemaVersion: schemaB, ID: id, SourceKind: kind, SourceID: src, Status: "RESOLVED", ResolutionAuthority: "ci"})
		}
	}
	return out
}
func verifySaul(e Evidence, s State, pub ed25519.PublicKey, checkID int64) bool {
	got := map[string]bool{}
	for _, sh := range e.Shards {
		got[sh.ID] = sh.ID != ""
	}
	cover := len(e.Shards) > 0
	for _, id := range shardUnits(s) {
		cover = cover && got[id]
	}
	msg, err := signMsg(e)
	sig, err2 := hex.DecodeString(e.Sig)
	idOK := e.ReviewerIdentity != "" && !strings.Contains(strings.ToLower(e.ReviewerIdentity), "candidate")
	ok := e.SchemaVersion == schemaE && e.Repository == s.Repository && e.PR == s.PR && e.PR != 0 &&
		e.BaseSHA == s.BaseSHA && e.HeadSHA == s.HeadSHA && e.HeadSHA != "" && e.ManifestHash != "" &&
		idOK && e.KeyID != "" && e.CheckRunID != 0 && (checkID == 0 || e.CheckRunID == checkID) &&
		e.CodexInvoked && !e.Synthetic && cover && e.LocalArch != "" && e.ImpactArch != "" &&
		e.SystemArch != "" && e.BlockerSetHash == hashBlockers(e.Blockers) && len(e.Tests) > 0 && e.FinalDisposition != ""
	return ok && err == nil && err2 == nil && len(pub) != 0 && ed25519.Verify(pub, msg, sig)
}
func ingestSaul(w World, s State) (Review, []Blocker) {
	var c *ghCheck
	for i := range w.Checks {
		if w.Checks[i].Name == checkSaul && (w.Checks[i].HeadSHA == "" || w.Checks[i].HeadSHA == w.Head) {
			c = &w.Checks[i]
		}
	}
	if c == nil || c.Status != "completed" {
		return Review{SHA: w.Head}, nil
	}
	proto := blk("SAUL_PROTOCOL_V2", "runtime", "saul-publisher", c.App.Slug, "P1", "owner", "Saul publisher protocol needs v2", nil, false, w.Head, w.Repo, w.PR)
	var e Evidence
	pub, perr := loadPub()
	if strings.TrimSpace(c.Output.Text) == "" || json.Unmarshal([]byte(c.Output.Text), &e) != nil || perr != nil || !verifySaul(e, s, pub, c.ID) {
		return Review{SHA: w.Head}, []Blocker{proto}
	}
	r := Review{SHA: e.HeadSHA, Schema: schemaE, Trusted: true, Shards: e.Shards, LocalArch: e.LocalArch, ImpactArch: e.ImpactArch, SystemArch: e.SystemArch, Blockers: e.Blockers}
	var bs []Blocker
	for _, b := range e.Blockers {
		b.SourceKind = "saul"
		if b.ResolutionAuthority == "" {
			b.ResolutionAuthority = "saul"
		}
		bs = append(bs, b)
	}
	return r, bs
}
func ReconcileBlockers(w World, prior State) ([]Blocker, Review) {
	rev, sb := ingestSaul(w, prior)
	in := append(ingestTrustedComments(w), ingestChecks(w)...)
	in = append(in, sb...)
	return mergeFrontier(prior.Blockers, in, w.Head), rev
}
func setCI(w World, s State) State {
	st, saw := Status(StPass), false
	for _, c := range w.Checks {
		if !ciRole(c) || (c.HeadSHA != "" && c.HeadSHA != w.Head) {
			continue
		}
		saw = true
		if c.Status != "completed" {
			if st != StFail {
				st = StPending
			}
		} else if checkFail(c) {
			st = StFail
		}
	}
	if !saw {
		st = StPending
	}
	s.CI, s.CIAt = st, w.Head
	return s
}
func scheduleState(s State) State {
	n := 0
	for i := range s.Blockers {
		s.Blockers[i].Actionable = isActionable(s.Blockers[i], s)
		if s.Blockers[i].Actionable {
			n++
		}
	}
	switch {
	case Ready(s):
		s.NextAction = ActReady
	case n > 0 && s.CI == StFail && s.CIAt == s.HeadSHA:
		s.NextAction = ActRemediate
	case n > 0:
		s.NextAction = ActImplement
	case s.CI == StPending && s.CIAt == s.HeadSHA:
		s.NextAction = ActWaitCI
	case !saulConverged(s):
		s.NextAction = ActWaitSaul
	default:
		s.NextAction = ActObserve
	}
	s.Phase, s.Terminal = s.NextAction, s.NextAction == ActReady
	return ensureWork(s, pick(s))
}
func ensureWork(s State, p *Blocker) State {
	if s.NextAction != ActImplement && s.NextAction != ActRemediate {
		s.Grant, s.Dispatch = Grant{}, Disp{}
		return s
	}
	if s.Grant.HeadSHA == s.HeadSHA && s.Grant.WorkItem != "" {
		if w := findItem(s, s.Grant.WorkItem); w != nil && w.BaseSHA == s.HeadSHA && w.Status != awaitVal {
			s.Dispatch = Disp{Kind: "cursor_primary", Grant: s.Grant, Head: s.HeadSHA, WorkItem: *w}
			return s
		}
	}
	if p == nil {
		s.Grant, s.Dispatch = Grant{}, Disp{}
		return s
	}
	ev := []string{}
	for _, e := range p.Evidence {
		if e.EvidenceRef != "" {
			ev = append(ev, e.EvidenceRef)
		}
	}
	w := WorkItem{ID: "WI-" + p.ID, BlockerIDs: []string{p.ID}, BaseSHA: s.HeadSHA, HeadSHA: s.HeadSHA, Objective: p.Objective, Scope: p.Scope, Acceptance: p.Acceptance, DependsOn: p.DependsOn, Priority: p.Priority, Evidence: ev, GrantID: "G-" + h8(s.HeadSHA+"|"+p.ID), Status: "OPEN"}
	found := false
	for i := range s.Workers {
		if s.Workers[i].ID == w.ID && s.Workers[i].BaseSHA == s.HeadSHA && s.Workers[i].Status != "STALE" {
			s.Workers[i], found = w, true
		}
	}
	if !found {
		s.Workers = append(s.Workers, w)
	}
	s.Grant = Grant{WorkItem: w.ID, HeadSHA: s.HeadSHA, Objective: w.Objective, Scope: w.Scope}
	s.Dispatch = Disp{Kind: "cursor_primary", Grant: s.Grant, Head: s.HeadSHA, WorkItem: w}
	return s
}
func CompleteWork(s State, r WorkerResult) (State, error) {
	w := findItem(s, r.WorkItem)
	switch {
	case r.SetsReady || r.Status == string(ActReady) || r.Status == "RESOLVED" || r.Status == "done" || r.Status == "approved":
		return s, fmt.Errorf("worker cannot resolve")
	case w == nil:
		return s, fmt.Errorf("unknown work item")
	case r.BaseSHA != s.HeadSHA || w.BaseSHA != s.HeadSHA:
		return s, fmt.Errorf("stale work item")
	}
	if r.Status == "" {
		r.Status = awaitVal
	}
	w.Status = r.Status
	head, err := gitHead()
	if err != nil {
		return s, err
	}
	return Observe(head, s), nil
}
func localOnly() bool { return os.Getenv("RALPH_LOCAL_ONLY") == "1" }
func statePath() string {
	if p := os.Getenv("RALPH_STATE"); p != "" {
		return p
	}
	return ".ralph-state.json"
}
func locked(path string, fn func() error) error {
	lk, err := os.OpenFile(path+".lock", os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		return err
	}
	defer lk.Close()
	if err := syscall.Flock(int(lk.Fd()), syscall.LOCK_EX); err != nil {
		return err
	}
	defer syscall.Flock(int(lk.Fd()), syscall.LOCK_UN)
	return fn()
}
func loadState(path string) (State, error) {
	var s State
	err := locked(path, func() error {
		b, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		return json.Unmarshal(b, &s)
	})
	return s, err
}
func saveState(path string, s State) error {
	return locked(path, func() error {
		b, err := json.Marshal(s)
		if err != nil {
			return err
		}
		tmp := path + ".tmp"
		if err := os.WriteFile(tmp, append(b, '\n'), 0644); err != nil {
			return err
		}
		return os.Rename(tmp, path)
	})
}
func shellKind(cmd string) int {
	c := strings.TrimSpace(cmd)
	low := strings.ToLower(c)
	if c == "" || strings.ContainsAny(c, "|;$()`<>") || strings.Contains(c, "&&") || strings.Contains(c, "../") ||
		strings.Contains(c, "\n") || strings.Contains(c, "<<") || strings.Contains(low, "-x post") ||
		strings.Contains(low, "-x put") || strings.Contains(low, "-x patch") || strings.Contains(low, "-x delete") ||
		strings.HasPrefix(low, "git checkout") || strings.HasPrefix(low, "git reset") || strings.HasPrefix(low, "git apply") ||
		((strings.HasPrefix(low, "gofmt") || strings.HasPrefix(low, "go fmt")) && strings.Contains(low, "-w")) {
		return 0
	}
	for _, p := range shellMut {
		if strings.HasPrefix(c, p) {
			return 2
		}
	}
	for _, p := range shellRead {
		if strings.HasPrefix(c, p) {
			return 1
		}
	}
	return 0
}
func shellOK(cmd string) bool { return shellKind(cmd) == 1 }
func allow() map[string]any   { return map[string]any{"permission": "allow"} }
func deny(reason string) map[string]any {
	msg := "ralph DENY " + reason
	return map[string]any{"permission": "deny", "agent_message": msg, "user_message": msg}
}
func hookDecision(s State, in hookIn, head, root string) map[string]any {
	switch {
	case in.ToolName == "":
		return deny("MALFORMED")
	case readOnly[in.ToolName]:
		return allow()
	case in.ToolName == "Shell" && shellKind(fmt.Sprint(in.ToolInput["command"])) == 1:
		return allow()
	case in.ToolName == "Shell" && shellKind(fmt.Sprint(in.ToolInput["command"])) == 0:
		return deny("SHELL_MUTATION")
	case in.ToolName == "Shell":
		// mut shell falls through to grant
		break
	case !mutate[in.ToolName]:
		return deny("UNKNOWN_TOOL")
	}
	path := ""
	for _, k := range []string{"path", "file_path", "target_notebook"} {
		if v, ok := in.ToolInput[k].(string); ok && v != "" {
			path = v
			break
		}
	}
	rel := ""
	if path != "" {
		var err error
		if rel, err = repoRel(path, root); err != nil {
			return deny("PATH")
		}
	}
	d := Authorize(Observe(head, s), AuthReq{HeadSHA: head, Path: rel, Tool: in.ToolName})
	if d.Decision == DecisionAllow {
		return allow()
	}
	return deny(d.Reason)
}
func ghToken() string {
	if t := os.Getenv("GITHUB_TOKEN"); t != "" {
		return t
	}
	if t := os.Getenv("GH_TOKEN"); t != "" {
		return t
	}
	out, _ := exec.Command("gh", "auth", "token").Output()
	return strings.TrimSpace(string(out))
}
func repoName() string {
	if r := os.Getenv("GITHUB_REPOSITORY"); r != "" {
		return r
	}
	u, _ := gitOut("remote", "get-url", "origin")
	u = strings.TrimSuffix(strings.TrimSpace(u), ".git")
	for _, sep := range []string{"github.com:", "github.com/"} {
		if i := strings.Index(u, sep); i >= 0 {
			return u[i+len(sep):]
		}
	}
	return ""
}
func ghJSON(method, path string, body, out any) error {
	var rdr io.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return err
		}
		rdr = bytes.NewReader(b)
	}
	req, err := http.NewRequest(method, strings.TrimRight(ghAPI, "/")+path, rdr)
	if err != nil {
		return err
	}
	tok := ghToken()
	if tok == "" {
		return fmt.Errorf("github token missing")
	}
	req.Header = http.Header{"Authorization": {"Bearer " + tok}, "Accept": {"application/vnd.github+json"}, "Content-Type": {"application/json"}}
	resp, err := doHTTP(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("github %s %s: %d", method, path, resp.StatusCode)
	}
	if out == nil {
		return nil
	}
	return json.Unmarshal(b, out)
}
func listChecks(sha string) ([]ghCheck, error) {
	var wrap struct {
		CheckRuns []ghCheck `json:"check_runs"`
	}
	err := ghJSON("GET", "/repos/"+repoName()+"/commits/"+sha+"/check-runs?per_page=100", nil, &wrap)
	return wrap.CheckRuns, err
}
func persist(s State) error {
	s.ReconciledAt, s.SchemaVersion, s.Terminal = now(), "ralph-state-v1", Ready(s)
	if err := saveState(statePath(), s); err != nil || localOnly() {
		return err
	}
	sum, err := json.Marshal(s)
	if err != nil {
		return err
	}
	human := fmt.Sprintf("phase=%s head=%s blockers=%d grant=%s", s.NextAction, s.HeadSHA, len(s.Blockers), s.Grant.WorkItem)
	body := map[string]any{"name": checkRalph, "head_sha": s.HeadSHA, "status": "completed", "conclusion": map[bool]string{true: "success", false: "neutral"}[Ready(s)], "output": map[string]string{"title": string(s.NextAction), "summary": human + "\n" + string(sum), "text": string(sum)}}
	path := "/repos/" + repoName() + "/check-runs"
	if runs, _ := listChecks(s.HeadSHA); true {
		for _, c := range runs {
			if c.Name == checkRalph && (c.HeadSHA == s.HeadSHA || c.HeadSHA == "") {
				_ = ghJSON("PATCH", fmt.Sprintf("%s/%d", path, c.ID), body, nil)
				return nil
			}
		}
	}
	if err := ghJSON("POST", path, body, nil); err != nil {
		fmt.Fprintln(os.Stderr, "ralph persist:", err)
	}
	return nil
}
func recoverState(head string) (State, error) {
	repo, pr := repoName(), 0
	fmt.Sscanf(os.Getenv("RALPH_PR"), "%d", &pr)
	boot := State{SchemaVersion: "ralph-state-v1", Repository: repo, ProgramID: "ralph-" + strings.ReplaceAll(repo, "/", "-") + "-" + fmt.Sprint(pr), PR: pr, HeadSHA: head, CI: StMissing}
	local, lerr := loadState(statePath())
	if localOnly() {
		if lerr == nil {
			boot = local
		}
		return Observe(head, boot), nil
	}
	runs, err := listChecks(head)
	if err != nil {
		return State{}, err
	}
	for i := len(runs) - 1; i >= 0; i-- {
		raw := runs[i].Output.Text
		if raw == "" {
			raw = runs[i].Output.Summary
		}
		if runs[i].Name != checkRalph || raw == "" {
			continue
		}
		if j := strings.Index(raw, "{"); j >= 0 {
			raw = raw[j:]
		}
		var s State
		if json.Unmarshal([]byte(raw), &s) == nil {
			return Observe(head, s), nil
		}
	}
	if lerr == nil && local.HeadSHA == head {
		return Observe(head, local), nil
	}
	return boot, nil
}
func fetchWorld() (World, error) {
	repo := repoName()
	if repo == "" {
		return World{}, fmt.Errorf("repository undiscoverable")
	}
	head, err := gitPick(headOverride, "HEAD", "git HEAD", 7)
	if err != nil {
		return World{}, err
	}
	pr := 0
	fmt.Sscanf(os.Getenv("RALPH_PR"), "%d", &pr)
	if r := os.Getenv("GITHUB_REF"); pr == 0 && strings.HasPrefix(r, "refs/pull/") {
		fmt.Sscanf(r, "refs/pull/%d", &pr)
	}
	var pulls []map[string]any
	if pr == 0 {
		_ = ghJSON("GET", "/repos/"+repo+"/commits/"+head+"/pulls", nil, &pulls)
		if len(pulls) == 0 {
			return World{}, fmt.Errorf("pr undiscoverable")
		}
		pr = int(pulls[0]["number"].(float64))
	}
	var prj map[string]any
	_ = ghJSON("GET", fmt.Sprintf("/repos/%s/pulls/%d", repo, pr), nil, &prj)
	if h, ok := prj["head"].(map[string]any); ok {
		if sha, _ := h["sha"].(string); sha != "" {
			head = sha
		}
	}
	base := ""
	if b, ok := prj["base"].(map[string]any); ok {
		base, _ = b["sha"].(string)
	}
	var raw []map[string]any
	if err := ghJSON("GET", fmt.Sprintf("/repos/%s/issues/%d/comments?per_page=100", repo, pr), nil, &raw); err != nil {
		return World{}, err
	}
	perms, comments := map[string]string{}, []ghComment{}
	for _, c := range raw {
		user, _ := c["user"].(map[string]any)
		login, _ := user["login"].(string)
		assoc, _ := c["author_association"].(string)
		body, _ := c["body"].(string)
		url, _ := c["html_url"].(string)
		id := fmt.Sprint(int64(c["id"].(float64)))
		comments = append(comments, ghComment{ID: id, Body: body, HTMLURL: url, Assoc: assoc, Login: login})
		if login == "" || perms[login] != "" {
			continue
		}
		if assoc == "OWNER" {
			perms[login] = "admin"
			continue
		}
		var p map[string]any
		if ghJSON("GET", "/repos/"+repo+"/collaborators/"+login+"/permission", nil, &p) != nil {
			perms[login] = "none"
		} else {
			perms[login], _ = p["permission"].(string)
		}
	}
	checks, err := listChecks(head)
	return World{Repo: repo, PR: pr, Head: head, Base: base, Comments: comments, Checks: checks, Perms: perms}, err
}
func resolveWorld() (World, error) {
	if testWorld != nil {
		return *testWorld, nil
	}
	if p := os.Getenv("RALPH_WORLD"); p != "" {
		b, err := os.ReadFile(p)
		var w World
		if err != nil {
			return w, err
		}
		return w, json.Unmarshal(b, &w)
	}
	return fetchWorld()
}
func dispatch(s State) State {
	if s.NextAction == ActWaitSaul && !localOnly() {
		_ = ghJSON("POST", "/repos/"+repoName()+"/dispatches", map[string]any{"event_type": "saul-review", "client_payload": map[string]string{"sha": s.HeadSHA, "pr": fmt.Sprint(s.PR)}}, nil)
	}
	return s
}
func applyWorld(w World, s State) State {
	if s.Repository == "" {
		s.Repository = w.Repo
	}
	if s.PR == 0 {
		s.PR = w.PR
	}
	if s.BaseSHA == "" {
		s.BaseSHA = w.Base
	}
	if s.ProgramID == "" {
		s.ProgramID = "ralph-" + strings.ReplaceAll(s.Repository, "/", "-") + "-" + fmt.Sprint(s.PR)
	}
	s = Observe(w.Head, s)
	bl, rev := ReconcileBlockers(w, s)
	s.Saul, s.Blockers = rev, bl
	return scheduleState(setCI(w, s))
}
func Cycle() (State, error) {
	w, err := resolveWorld()
	if err != nil {
		return State{}, err
	}
	if w.Head == "" {
		if w.Head, err = gitHead(); err != nil {
			return State{}, err
		}
	}
	s, err := recoverState(w.Head)
	if err != nil {
		return s, err
	}
	s = dispatch(applyWorld(w, s))
	return s, persist(s)
}
func loadPub() (ed25519.PublicKey, error) {
	try := func(b []byte) (ed25519.PublicKey, error) {
		raw, err := hex.DecodeString(strings.TrimSpace(string(b)))
		if err != nil || len(raw) != ed25519.PublicKeySize {
			return nil, fmt.Errorf("saul pub")
		}
		return ed25519.PublicKey(raw), nil
	}
	if p := os.Getenv("SAI_SAUL_ATTEST_PUB"); p != "" {
		if b, err := os.ReadFile(p); err == nil {
			return try(b)
		}
		return try([]byte(p))
	}
	for _, p := range []string{os.Getenv("SAI_TRUSTED_TREE") + "/.ai/authorizations/saul-attestation-ed25519.pub", "/opt/sai/trusted-reviewer/.ai/authorizations/saul-attestation-ed25519.pub"} {
		if b, err := os.ReadFile(p); err == nil {
			return try(b)
		}
	}
	return nil, fmt.Errorf("saul trust anchor unavailable")
}
func hookMain() int {
	raw, _ := io.ReadAll(os.Stdin)
	var in hookIn
	if json.Unmarshal(raw, &in) != nil || in.ToolName == "" {
		var m map[string]any
		_ = json.Unmarshal(raw, &m)
		in.ToolName, _ = m["toolName"].(string)
	}
	if in.ToolInput == nil {
		in.ToolInput = map[string]any{}
	}
	cmd, _ := in.ToolInput["command"].(string)
	head, herr := gitHead()
	root, rerr := gitRoot()
	out := deny("MALFORMED")
	switch {
	case in.ToolName == "":
		out = deny("MALFORMED")
	case readOnly[in.ToolName] || (in.ToolName == "Shell" && shellKind(cmd) == 1):
		out = allow()
	case herr != nil || rerr != nil:
		out = deny("HEAD")
	default:
		s, lerr := loadState(statePath())
		if lerr != nil || s.HeadSHA != head {
			s, lerr = recoverState(head)
		}
		out = map[bool]map[string]any{true: hookDecision(s, in, head, root), false: deny("NO_STATE")}[lerr == nil]
	}
	_ = json.NewEncoder(os.Stdout).Encode(out)
	return 0
}
func runMain(once bool) int {
	dead, delay, n := time.Time{}, 20*time.Second, 0
	if fmt.Sscanf(os.Getenv("RALPH_WAIT_MS"), "%d", &n); n > 0 {
		dead = time.Now().Add(time.Duration(n) * time.Millisecond)
	}
	if fmt.Sscanf(os.Getenv("RALPH_POLL_MS"), "%d", &n); n > 0 {
		delay = time.Duration(n) * time.Millisecond
	}
	for {
		s, err := Cycle()
		_ = json.NewEncoder(os.Stdout).Encode(s)
		if err != nil {
			fmt.Fprintln(os.Stderr, "ralph:", err)
			return 2
		}
		if Ready(s) {
			return 0
		}
		fmt.Fprintf(os.Stderr, "NONTERMINAL head=%s phase=%s action=%s dispatch=%s blockers=%d\n", s.HeadSHA, s.Phase, s.NextAction, s.Dispatch.Kind, len(s.Blockers))
		if once {
			return 1
		}
		if !dead.IsZero() && time.Now().After(dead) {
			return 2
		}
		time.Sleep(delay)
	}
}
func workerMain() int {
	id, base, result, st := "", "", "", awaitVal
	for i, a := range os.Args {
		if i+1 < len(os.Args) {
			switch a {
			case "--work-item":
				id = os.Args[i+1]
			case "--base":
				base = os.Args[i+1]
			case "--result":
				result = os.Args[i+1]
			case "--status":
				st = os.Args[i+1]
			}
		}
	}
	head, err := gitHead()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	s, err := recoverState(head)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	if base == "" {
		base = s.HeadSHA
	}
	s, err = CompleteWork(s, WorkerResult{WorkItem: id, BaseSHA: base, ResultSHA: result, Status: st})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	if err = persist(s); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	_ = json.NewEncoder(os.Stdout).Encode(s)
	return 0
}
func main() {
	cmd := "hook"
	if len(os.Args) > 1 && !strings.HasPrefix(os.Args[1], "-") {
		cmd = os.Args[1]
	}
	switch cmd {
	case "hook":
		os.Exit(hookMain())
	case "run":
		os.Exit(runMain(false))
	case "reconcile":
		os.Exit(runMain(true))
	case "worker-result":
		os.Exit(workerMain())
	default:
		fmt.Fprintln(os.Stderr, "ralph commands: hook run reconcile worker-result")
		os.Exit(2)
	}
}
