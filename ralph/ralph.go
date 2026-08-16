package main

import (
	"cmp"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
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
	headOverride string
	rootOverride string
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
	Actionable          bool     `json:"-"`
}
type WorkItem struct {
	ID, Objective, BaseSHA, GrantID, Status            string
	BlockerIDs, Scope, Acceptance, DependsOn, Evidence []string
	Priority                                           int
}
type Grant struct {
	WorkItem, HeadSHA, Objective string
	Scope                        []string
}
type Disp struct {
	Kind     string   `json:"kind"`
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
	SHA                               string
	Trusted                           bool
	Shards                            []Shard
	LocalArch, ImpactArch, SystemArch Status
}
type State struct {
	SchemaVersion, Repository, HeadSHA, BaseSHA, CIAt, ReconciledAt string
	PR, Generation                                                  int
	NextAction                                                      Action
	Blockers                                                        []Blocker
	Workers                                                         []WorkItem
	Grant                                                           Grant
	Dispatch                                                        Disp
	CI                                                              Status
	Saul                                                            Review
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
	SchemaVersion      string          `json:"schema_version"`
	Repository         string          `json:"repository"`
	PR                 int             `json:"pr"`
	BaseSHA            string          `json:"base_sha"`
	HeadSHA            string          `json:"head_sha"`
	ManifestHash       string          `json:"manifest_hash"`
	ReviewerIdentity   string          `json:"reviewer_identity"`
	KeyID              string          `json:"key_id"`
	CheckRunID         int64           `json:"check_run_id"`
	Synthetic          bool            `json:"synthetic"`
	RuntimeAttestation json.RawMessage `json:"runtime_attestation"`
	Shards             []Shard         `json:"shards"`
	LocalArch          Status          `json:"local_arch"`
	ImpactArch         Status          `json:"impact_arch"`
	SystemArch         Status          `json:"system_arch"`
	Blockers           []Blocker       `json:"blockers"`
	BlockerSetHash     string          `json:"blocker_set_hash"`
	Tests              json.RawMessage `json:"tests"`
	FinalDisposition   string          `json:"final_disposition"`
	Sig                string          `json:"signature,omitempty"`
}
type Envelope struct {
	SchemaVersion string    `json:"schema_version"`
	Repository    string    `json:"repository"`
	PR            int       `json:"pr"`
	HeadSHA       string    `json:"head_sha,omitempty"`
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
type ghComment struct{ ID, Body, HTMLURL, Assoc, Login string }
type World struct {
	Repo, Head, Base string
	PR               int
	Comments         []ghComment
	Checks           []ghCheck
	Perms            map[string]string
}

func gitOut(args ...string) (string, error) {
	cmd := exec.Command("git", args...)
	cmd.Dir = rootOverride
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
func now() string { return time.Now().UTC().Format(time.RFC3339) }
func hashRaw(r json.RawMessage) string {
	if len(r) == 0 {
		r = []byte("[]")
	}
	sum := sha256.Sum256(r)
	return hex.EncodeToString(sum[:])
}
func rawList(r json.RawMessage, path bool) []string {
	var a []string
	var s string
	if json.Unmarshal(r, &a) == nil {
		return a
	}
	if json.Unmarshal(r, &s) == nil && s != "" && (!path || strings.ContainsAny(s, "/.")) {
		return []string{s}
	}
	return nil
}
func evList(r json.RawMessage) []EvRef {
	var raw []map[string]any
	if json.Unmarshal(r, &raw) != nil {
		return nil
	}
	out := []EvRef{}
	for _, e := range raw {
		msg, _ := e["message"].(string)
		if msg == "" {
			msg, _ = e["test"].(string)
		}
		ref, _ := e["evidence_ref"].(string)
		if ref == "" {
			ref, _ = e["comment_url"].(string)
		}
		if msg != "" || ref != "" {
			out = append(out, EvRef{Message: msg, EvidenceRef: ref})
		}
	}
	return out
}
func (b *Blocker) UnmarshalJSON(p []byte) error {
	var m map[string]json.RawMessage
	if err := json.Unmarshal(p, &m); err != nil {
		return err
	}
	ks := []string{"schema_version", "id", "source_kind", "source_id", "source_actor", "repository", "pr", "head_sha", "applicability", "severity", "blocking", "status", "objective", "depends_on", "resolution_authority", "created_at", "updated_at"}
	ds := []any{&b.SchemaVersion, &b.ID, &b.SourceKind, &b.SourceID, &b.SourceActor, &b.Repository, &b.PR, &b.HeadSHA, &b.Applicability, &b.Severity, &b.Blocking, &b.Status, &b.Objective, &b.DependsOn, &b.ResolutionAuthority, &b.CreatedAt, &b.UpdatedAt}
	for i := range ks {
		_ = json.Unmarshal(m[ks[i]], ds[i])
	}
	var n int
	var s string
	if json.Unmarshal(m["priority"], &n) == nil {
		b.Priority = n
	} else if json.Unmarshal(m["priority"], &s) == nil && b.Severity == "" {
		b.Severity = s
	}
	b.Scope, b.Acceptance, b.Evidence = rawList(m["scope"], true), rawList(m["acceptance"], false), evList(m["evidence"])
	return nil
}
func repoRel(path, root string) (string, error) {
	if path == "" || root == "" {
		return "", fmt.Errorf("empty path")
	}
	if !filepath.IsAbs(path) {
		path = filepath.Join(root, path)
	}
	clean := filepath.Clean(path)
	if st, err := os.Lstat(clean); err == nil && st.Mode()&os.ModeSymlink != 0 {
		return "", fmt.Errorf("symlink")
	}
	rel, err := filepath.Rel(filepath.Clean(root), clean)
	if err != nil || strings.HasPrefix(rel, "..") || filepath.IsAbs(rel) {
		return "", fmt.Errorf("escape")
	}
	return filepath.ToSlash(rel), nil
}
func applicable(b Blocker, head string) bool {
	h := cmp.Or(b.Applicability.HeadSHA, b.HeadSHA)
	return b.Status == "OPEN" && b.Blocking && (b.Applicability.Mode == "sticky" || h == "" || h == head)
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
func isActionable(b Blocker, s State) bool {
	return applicable(b, s.HeadSHA) && depsReady(b, s.Blockers) && len(b.Scope) > 0
}
func saulConverged(s State) bool {
	r := s.Saul
	if !r.Trusted || r.SHA == "" || r.SHA != s.HeadSHA || len(r.Shards) == 0 || r.LocalArch != StPass || r.ImpactArch != StPass || r.SystemArch != StPass {
		return false
	}
	for _, sh := range r.Shards {
		if sh.Status != StPass {
			return false
		}
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
	var best *Blocker
	for i := range s.Blockers {
		b := &s.Blockers[i]
		if !b.Actionable {
			continue
		}
		if best == nil || b.Severity < best.Severity || b.Severity == best.Severity && (b.Priority < best.Priority || b.Priority == best.Priority && (b.CreatedAt < best.CreatedAt || b.CreatedAt == best.CreatedAt && b.ID < best.ID)) {
			best = b
		}
	}
	return best
}
func Observe(head string, s State) State {
	if head == "" {
		head = s.HeadSHA
	}
	if s.HeadSHA != "" && head != s.HeadSHA {
		if s.CIAt != head {
			s.CI = StStale
		}
		s.Saul.Trusted, s.Grant, s.Dispatch = s.Saul.Trusted && s.Saul.SHA == head, Grant{}, Disp{}
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
func signBytes(raw []byte) ([]byte, error) {
	var m map[string]json.RawMessage
	if err := json.Unmarshal(raw, &m); err != nil {
		return nil, err
	}
	delete(m, "signature")
	b, err := json.Marshal(m)
	return append([]byte(signDom), b...), err
}
func decodeSig(s string) []byte {
	if b, err := hex.DecodeString(s); err == nil && len(b) == ed25519.SignatureSize {
		return b
	}
	b, _ := base64.StdEncoding.DecodeString(s)
	return b
}
func canResolve(old, neu Blocker) bool {
	a, k := old.ResolutionAuthority, neu.SourceKind
	return a == "saul" && k == "saul" || a == "ci" && (k == "ci" || k == "check") && neu.SourceID == old.SourceID || a == "ralph" && (k == "runtime" || k == "primary") || a == "source_actor" && neu.SourceActor == old.SourceActor && k == old.SourceKind || a == "owner" && k == "comment"
}
func mergeFrontierSaul(prior, inc []Blocker, saulIDs map[string]bool, saulOK bool, head string) []Blocker {
	m, order := map[string]Blocker{}, []string{}
	put := func(b Blocker) {
		if b.ID == "" {
			return
		}
		b.SchemaVersion = cmp.Or(b.SchemaVersion, schemaB)
		old, ok := m[b.ID]
		switch {
		case !ok && b.Status == "RESOLVED":
		case !ok:
			m[b.ID], order = b, append(order, b.ID)
		case b.Status == "RESOLVED":
			if canResolve(old, b) {
				old.Status, old.UpdatedAt = "RESOLVED", b.UpdatedAt
				m[b.ID] = old
			}
		default:
			b.CreatedAt = cmp.Or(old.CreatedAt, b.CreatedAt)
			m[b.ID] = b
		}
	}
	for _, xs := range [][]Blocker{prior, inc} {
		for _, b := range xs {
			put(b)
		}
	}
	out := make([]Blocker, 0, len(order))
	for _, id := range order {
		b := m[id]
		if saulOK && b.SourceKind == "saul" && b.Applicability.Mode != "sticky" && !saulIDs[b.ID] {
			continue
		}
		h := cmp.Or(b.Applicability.HeadSHA, b.HeadSHA)
		if b.Status != "RESOLVED" && b.Applicability.Mode != "sticky" && h != "" && h != head {
			continue
		}
		out = append(out, b)
	}
	return out
}
func parseEnv(body string) (Envelope, bool) {
	s := body
	if i := strings.Index(body, marker); i >= 0 {
		rest := body[i:]
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
	return e, json.Unmarshal([]byte(strings.TrimSpace(s)), &e) == nil && e.SchemaVersion == schemaBs
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
func skipCheck(n string) bool {
	return strings.Contains("\n"+checkRalph+"\n"+checkSaul+"\ncontinue\nCursor Automation: Sai\nmerge-handoff-slack\n", "\n"+n+"\n")
}
func ciRole(c ghCheck) bool {
	return !skipCheck(c.Name) && (c.App.Slug == "github-actions" || c.App.ID == 15368 || c.App.Slug == "")
}
func checkFail(c ghCheck) bool {
	return c.Status == "completed" && (c.Conclusion == "failure" || c.Conclusion == "action_required" || c.Conclusion == "timed_out" || c.Conclusion == "cancelled")
}
func ingest(w World) []Blocker {
	var out []Blocker
	for _, c := range w.Comments {
		if c.Assoc != "OWNER" && w.Perms[c.Login] != "admin" && w.Perms[c.Login] != "maintain" {
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
				b.SourceKind, b.SourceID, b.SourceActor, b.Repository, b.PR, b.Applicability.Mode = "comment", src, c.Login, w.Repo, w.PR, cmp.Or(b.Applicability.Mode, "sticky")
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
	for _, c := range w.Checks {
		if (c.HeadSHA != "" && c.HeadSHA != w.Head) || skipCheck(c.Name) || c.Status != "completed" {
			continue
		}
		id, src := "CHECK-"+h8(fmt.Sprintf("%d/%s/%s", c.App.ID, c.App.Slug, c.Name)), fmt.Sprintf("check:%d/%s/%s", c.App.ID, c.App.Slug, c.Name)
		kind := map[bool]string{true: "ci", false: "check"}[ciRole(c)]
		if checkFail(c) {
			sc := map[bool][]string{true: {"ralph/", ".github/workflows/", "scripts/"}}[ciRole(c)]
			b := blk(id, kind, src, c.App.Slug, "P1", "ci", "Make required Check "+c.Name+" pass on exact current HEAD", sc, false, w.Head, w.Repo, w.PR)
			b.Evidence = []EvRef{{Message: c.Conclusion, EvidenceRef: c.DetailsURL}}
			out = append(out, b)
		} else if c.Conclusion == "success" {
			out = append(out, Blocker{SchemaVersion: schemaB, ID: id, SourceKind: kind, SourceID: src, Status: "RESOLVED", ResolutionAuthority: "ci"})
		}
	}
	return out
}
func verifySaul(raw []byte, e Evidence, s State, pub ed25519.PublicKey, checkID int64) string {
	var m map[string]json.RawMessage
	var tests []json.RawMessage
	idOK := e.ReviewerIdentity != "" && !strings.Contains(strings.ToLower(e.ReviewerIdentity), "candidate")
	if json.Unmarshal(raw, &m) != nil || e.SchemaVersion != schemaE || e.Repository != s.Repository || e.PR != s.PR || e.PR == 0 ||
		e.HeadSHA != s.HeadSHA || e.HeadSHA == "" || e.BaseSHA != s.BaseSHA || e.CheckRunID == 0 || (checkID != 0 && e.CheckRunID != checkID) ||
		e.Synthetic || !idOK || e.KeyID == "" || e.ManifestHash == "" || len(pub) == 0 || len(e.RuntimeAttestation) == 0 || e.RuntimeAttestation[0] != '{' ||
		json.Unmarshal(e.Tests, &tests) != nil || len(tests) == 0 || e.FinalDisposition == "" || len(e.Shards) == 0 || e.BlockerSetHash != hashRaw(m["blockers"]) {
		return "reject"
	}
	for _, x := range tests {
		if len(x) == 0 || x[0] != '{' {
			return "reject"
		}
	}
	for _, sh := range e.Shards {
		if sh.ID == "" || sh.Digest == "" || sh.Status == "" {
			return "reject"
		}
	}
	msg, err := signBytes(raw)
	sig := decodeSig(e.Sig)
	if err != nil || len(sig) != ed25519.SignatureSize || !ed25519.Verify(pub, msg, sig) {
		return "reject"
	}
	for _, b := range e.Blockers {
		if b.ID == "" || (b.Status != "OPEN" && b.Status != "RESOLVED" && b.Status != "STALE") {
			return "reject"
		}
	}
	return ""
}
func ingestSaul(w World, s State) (Review, []Blocker, bool) {
	var c *ghCheck
	for i := range w.Checks {
		if w.Checks[i].Name == checkSaul && (w.Checks[i].HeadSHA == "" || w.Checks[i].HeadSHA == w.Head) {
			c = &w.Checks[i]
		}
	}
	if c == nil || c.Status != "completed" {
		return Review{SHA: w.Head}, nil, false
	}
	raw := []byte(strings.TrimSpace(c.Output.Text))
	pub, err := loadPub()
	var e Evidence
	if len(raw) == 0 || err != nil || json.Unmarshal(raw, &e) != nil || verifySaul(raw, e, s, pub, c.ID) != "" {
		return Review{SHA: w.Head}, []Blocker{blk("SAUL_PROTOCOL_V2", "runtime", "saul-publisher", c.App.Slug, "P1", "owner", "Saul publisher protocol needs v2", nil, false, w.Head, w.Repo, w.PR)}, false
	}
	for i := range e.Blockers {
		e.Blockers[i].SourceKind = cmp.Or(e.Blockers[i].SourceKind, "saul")
		e.Blockers[i].ResolutionAuthority = cmp.Or(e.Blockers[i].ResolutionAuthority, "saul")
	}
	return Review{SHA: e.HeadSHA, Trusted: true, Shards: e.Shards, LocalArch: e.LocalArch, ImpactArch: e.ImpactArch, SystemArch: e.SystemArch}, e.Blockers, true
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
	ws, seen := s.Workers[:0], map[string]bool{}
	for _, x := range s.Workers {
		if x.Status != "STALE" && x.BaseSHA == s.HeadSHA && !seen[x.ID] {
			seen[x.ID], ws = true, append(ws, x)
		}
	}
	s.Workers = ws
	p, work := pick(s), s.NextAction == ActImplement || s.NextAction == ActRemediate
	if w := findItem(s, s.Grant.WorkItem); work && s.Grant.HeadSHA == s.HeadSHA && w != nil && w.BaseSHA == s.HeadSHA {
		s.Dispatch = Disp{Kind: "cursor_primary", Head: s.HeadSHA, WorkItem: *w}
		return s
	}
	if !work || p == nil {
		s.Grant, s.Dispatch = Grant{}, Disp{}
		return s
	}
	ev := []string{}
	for _, e := range p.Evidence {
		if e.EvidenceRef != "" {
			ev = append(ev, e.EvidenceRef)
		}
	}
	w := WorkItem{ID: "WI-" + p.ID, BlockerIDs: []string{p.ID}, BaseSHA: s.HeadSHA, Objective: p.Objective, Scope: p.Scope, Acceptance: p.Acceptance, DependsOn: p.DependsOn, Priority: p.Priority, Evidence: ev, GrantID: "G-" + h8(s.HeadSHA+"|"+p.ID), Status: "OPEN"}
	found := false
	for i := range s.Workers {
		if s.Workers[i].ID == w.ID && s.Workers[i].BaseSHA == s.HeadSHA {
			s.Workers[i], found = w, true
		}
	}
	if !found {
		s.Workers = append(s.Workers, w)
	}
	s.Grant, s.Dispatch = Grant{WorkItem: w.ID, HeadSHA: s.HeadSHA, Objective: w.Objective, Scope: w.Scope}, Disp{Kind: "cursor_primary", Head: s.HeadSHA, WorkItem: w}
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
	w.Status = cmp.Or(r.Status, awaitVal)
	head, err := r.ResultSHA, error(nil)
	if head == "" {
		head, err = gitHead()
	}
	if err != nil {
		return s, err
	}
	return Observe(head, s), nil
}
func statePath() string { return cmp.Or(os.Getenv("RALPH_STATE"), ".ralph-state.json") }
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
func writeState(path string, s *State) error {
	var cur State
	if b, err := os.ReadFile(path); err == nil {
		_ = json.Unmarshal(b, &cur)
	}
	if cur.Generation > s.Generation {
		return fmt.Errorf("stale generation")
	}
	s.Generation, s.ReconciledAt, s.SchemaVersion = cur.Generation+1, now(), "ralph-state-v1"
	b, err := json.Marshal(s)
	if err != nil {
		return err
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, append(b, '\n'), 0644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
func saveState(path string, s State) error {
	return locked(path, func() error { return writeState(path, &s) })
}
func shellKind(cmd string) int {
	c := strings.TrimSpace(cmd)
	low := strings.ToLower(c)
	if c == "" || strings.ContainsAny(c, "|;$()`<>") || strings.Contains(c, "&&") || strings.Contains(c, "../") || strings.Contains(c, "\n") || strings.Contains(c, "<<") || strings.Contains(low, "-x post") || strings.Contains(low, "-x put") || strings.Contains(low, "-x patch") || strings.Contains(low, "-x delete") {
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
func allow() map[string]any { return map[string]any{"permission": "allow"} }
func deny(reason string) map[string]any {
	msg := "ralph DENY " + reason
	return map[string]any{"permission": "deny", "agent_message": msg, "user_message": msg}
}
func hookDecision(s State, in hookIn, head, root string) map[string]any {
	sk := 0
	if in.ToolName == "Shell" {
		sk = shellKind(fmt.Sprint(in.ToolInput["command"]))
	}
	switch {
	case in.ToolName == "":
		return deny("MALFORMED")
	case readOnly[in.ToolName] || (in.ToolName == "Shell" && sk == 1):
		return allow()
	case in.ToolName == "Shell" && sk == 0:
		return deny("SHELL_MUTATION")
	case in.ToolName != "Shell" && !mutate[in.ToolName]:
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
	if d.Decision != DecisionAllow {
		return deny(d.Reason)
	}
	return allow()
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
	cmd := exec.Command("gh", "api", "-X", method, path)
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return err
		}
		cmd.Args, cmd.Stdin = append(cmd.Args, "--input", "-"), strings.NewReader(string(b))
	}
	o, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("github %s %s: %v", method, path, err)
	}
	if out == nil {
		return nil
	}
	return json.Unmarshal(o, out)
}
func publish(s State, checks []ghCheck) error {
	if os.Getenv("RALPH_LOCAL_ONLY") == "1" {
		return nil
	}
	sum, err := json.Marshal(s)
	if err != nil {
		return err
	}
	human := fmt.Sprintf("action=%s head=%s blockers=%d grant=%s", s.NextAction, s.HeadSHA, len(s.Blockers), s.Grant.WorkItem)
	body := map[string]any{"name": checkRalph, "head_sha": s.HeadSHA, "status": "completed", "conclusion": map[bool]string{true: "success", false: "neutral"}[Ready(s)], "output": map[string]string{"title": string(s.NextAction), "summary": human + "\n" + string(sum), "text": string(sum)}}
	path := "/repos/" + repoName() + "/check-runs"
	for _, c := range checks {
		if c.Name == checkRalph && (c.HeadSHA == s.HeadSHA || c.HeadSHA == "") {
			return ghJSON("PATCH", fmt.Sprintf("%s/%d", path, c.ID), body, nil)
		}
	}
	return ghJSON("POST", path, body, nil)
}
func recoverState(head string, checks []ghCheck) State {
	boot := State{SchemaVersion: "ralph-state-v1", Repository: repoName(), HeadSHA: head, CI: StMissing}
	fmt.Sscanf(os.Getenv("RALPH_PR"), "%d", &boot.PR)
	if b, err := os.ReadFile(statePath()); err == nil {
		var s State
		if json.Unmarshal(b, &s) == nil {
			return Observe(head, s)
		}
	}
	for i := len(checks) - 1; i >= 0; i-- {
		if checks[i].Name != checkRalph {
			continue
		}
		raw := cmp.Or(checks[i].Output.Text, checks[i].Output.Summary)
		if j := strings.Index(raw, "{"); j >= 0 {
			raw = raw[j:]
		}
		var s State
		if json.Unmarshal([]byte(raw), &s) == nil {
			return Observe(head, s)
		}
	}
	return Observe(head, boot)
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
	shaOf := func(k string) string {
		m, _ := prj[k].(map[string]any)
		s, _ := m["sha"].(string)
		return s
	}
	head, base := cmp.Or(shaOf("head"), head), shaOf("base")
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
		comments = append(comments, ghComment{ID: fmt.Sprint(int64(c["id"].(float64))), Body: body, HTMLURL: url, Assoc: assoc, Login: login})
		if login != "" && perms[login] == "" {
			perms[login] = map[bool]string{true: "admin", false: "none"}[assoc == "OWNER"]
		}
	}
	var wrap struct {
		CheckRuns []ghCheck `json:"check_runs"`
	}
	err = ghJSON("GET", "/repos/"+repo+"/commits/"+head+"/check-runs?per_page=100", nil, &wrap)
	return World{Repo: repo, PR: pr, Head: head, Base: base, Comments: comments, Checks: wrap.CheckRuns, Perms: perms}, err
}
func resolveWorld() (World, error) {
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
func applyWorld(w World, s State) State {
	s.Repository, s.PR, s.BaseSHA = cmp.Or(s.Repository, w.Repo), cmp.Or(s.PR, w.PR), cmp.Or(s.BaseSHA, w.Base)
	s = Observe(w.Head, s)
	rev, sb, ok := ingestSaul(w, s)
	ids := map[string]bool{}
	for _, b := range sb {
		ids[b.ID] = true
	}
	s.Saul, s.Blockers = rev, mergeFrontierSaul(s.Blockers, append(ingest(w), sb...), ids, ok, w.Head)
	st, saw := Status(StPass), false
	for _, c := range w.Checks {
		if !ciRole(c) || (c.HeadSHA != "" && c.HeadSHA != w.Head) {
			continue
		}
		saw = true
		switch {
		case c.Status != "completed" && st != StFail:
			st = StPending
		case checkFail(c):
			st = StFail
		}
	}
	if !saw {
		st = StPending
	}
	s.CI, s.CIAt = st, w.Head
	s = scheduleState(s)
	if s.NextAction == ActWaitSaul && os.Getenv("RALPH_LOCAL_ONLY") != "1" {
		_ = ghJSON("POST", "/repos/"+repoName()+"/dispatches", map[string]any{"event_type": "saul-review", "client_payload": map[string]string{"sha": s.HeadSHA, "pr": fmt.Sprint(s.PR)}}, nil)
	}
	return s
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
	var s State
	err = locked(statePath(), func() error {
		s = recoverState(w.Head, w.Checks)
		s = applyWorld(w, s)
		if err := writeState(statePath(), &s); err != nil {
			return err
		}
		return publish(s, w.Checks)
	})
	return s, err
}
func loadPub() (ed25519.PublicKey, error) {
	parse := func(p string) (ed25519.PublicKey, error) {
		raw, err := hex.DecodeString(strings.TrimSpace(p))
		if err != nil || len(raw) != ed25519.PublicKeySize {
			return nil, fmt.Errorf("saul pub")
		}
		return raw, nil
	}
	if p := os.Getenv("SAI_SAUL_ATTEST_PUB"); p != "" {
		if b, err := os.ReadFile(p); err == nil {
			p = string(b)
		}
		return parse(p)
	}
	for _, p := range []string{os.Getenv("SAI_TRUSTED_TREE") + "/.ai/authorizations/saul-attestation-ed25519.pub", "/opt/sai/trusted-reviewer/.ai/authorizations/saul-attestation-ed25519.pub"} {
		if b, err := os.ReadFile(p); err == nil {
			return parse(string(b))
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
	case readOnly[in.ToolName] || (in.ToolName == "Shell" && shellKind(cmd) == 1):
		out = allow()
	case herr != nil || rerr != nil:
		out = deny("HEAD")
	default:
		s, err := loadState(statePath())
		if err != nil || s.HeadSHA != head {
			s = recoverState(head, nil)
		}
		out = hookDecision(s, in, head, root)
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
		fmt.Fprintf(os.Stderr, "NONTERMINAL head=%s action=%s dispatch=%s blockers=%d\n", s.HeadSHA, s.NextAction, s.Dispatch.Kind, len(s.Blockers))
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
	kv := map[string]*string{"--work-item": &id, "--base": &base, "--result": &result, "--status": &st}
	for i, a := range os.Args[:max(0, len(os.Args)-1)] {
		if p, ok := kv[a]; ok {
			*p = os.Args[i+1]
		}
	}
	die := func(err error) int { fmt.Fprintln(os.Stderr, err); return 2 }
	head, err := gitHead()
	if err != nil {
		return die(err)
	}
	s := recoverState(head, nil)
	if s, err = CompleteWork(s, WorkerResult{WorkItem: id, BaseSHA: cmp.Or(base, s.HeadSHA), ResultSHA: result, Status: st}); err != nil {
		return die(err)
	}
	if err = saveState(statePath(), s); err != nil {
		return die(err)
	}
	if s, err = Cycle(); err != nil {
		return die(err)
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
	case "run", "reconcile":
		os.Exit(runMain(cmd == "reconcile"))
	case "worker-result":
		os.Exit(workerMain())
	default:
		fmt.Fprintln(os.Stderr, "ralph commands: hook run reconcile worker-result")
		os.Exit(2)
	}
}
