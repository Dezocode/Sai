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
	ActWaitSai    Action = "WAIT_SAI"
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
	schemaV1             = "saul-evidence-v1"
	saulSandbox          = "clone exact HEAD; Go 1.22; python3; executable scripts/*"
)

var (
	ciNames      = []string{"icm-enforcement", "PR line budget", "Anti-regression"}
	readOnly     = fields("Read Grep Glob SemanticSearch WebSearch WebFetch GetMcpTools FetchMcpResource ReadLints AwaitShell Task TodoWrite SwitchMode CallMcpTool")
	mutate       = fields("Write StrReplace Delete EditNotebook ApplyPatch")
	shellPref    = []string{"git status", "git log", "git diff", "git show", "git rev-parse", "git merge-base", "git fetch", "git add", "git commit", "git push", "git branch", "git remote", "git rev-list", "git cat-file", "go test", "go run ./ralph", "go fmt", "go vet", "go env", "go version", "scripts/verify-", "./scripts/verify-", "gh pr view", "gh api ", "gh run ", "python3 -m json.tool", "pwd", "ls", "true"}
	ghAPI        = "https://api.github.com"
	doHTTP       = func(req *http.Request) (*http.Response, error) { return http.DefaultClient.Do(req) }
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

type Finding struct {
	ID        string   `json:"id"`
	Source    string   `json:"source"`
	Objective string   `json:"objective"`
	Scope     []string `json:"scope"`
	Blocking  bool     `json:"blocking"`
}
type WorkItem struct {
	ID, Objective, BaseSHA, Status string
	Scope                          []string
}
type Grant struct {
	WorkItem, HeadSHA, Objective string
	Scope                        []string
}
type Disp struct {
	Kind  string `json:"kind"`
	Grant Grant  `json:"grant"`
	Head  string `json:"head"`
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
	Findings                          []Finding
}
type State struct {
	ProgramID, HeadSHA, BaseSHA, CIAt, SaiSHA string
	PR                                        int
	Phase                                     Action
	Blockers                                  []Finding
	Workers                                   []WorkItem
	Grant                                     Grant
	Dispatch                                  Disp
	CI, Sai                                   Status
	Saul                                      Review
	NextAction                                Action
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
	SchemaVersion    string    `json:"schema_version"`
	Repository       string    `json:"repository"`
	PR               int       `json:"pr"`
	BaseSHA          string    `json:"base_sha"`
	HeadSHA          string    `json:"head_sha"`
	ManifestHash     string    `json:"manifest_hash"`
	ReviewerIdentity string    `json:"reviewer_identity"`
	KeyID            string    `json:"key_id"`
	CheckRunID       int64     `json:"check_run_id"`
	CodexInvoked     bool      `json:"codex_invoked"`
	Synthetic        bool      `json:"synthetic"`
	Shards           []Shard   `json:"shards"`
	LocalArch        Status    `json:"local_arch"`
	ImpactArch       Status    `json:"impact_arch"`
	SystemArch       Status    `json:"system_arch"`
	Findings         []Finding `json:"findings"`
	FindingSetHash   string    `json:"finding_set_hash"`
	Tests            []string  `json:"tests"`
	FinalDisposition string    `json:"final_disposition"`
	Sig              string    `json:"sig,omitempty"`
}
type hookIn struct {
	ToolName  string         `json:"tool_name"`
	ToolInput map[string]any `json:"tool_input"`
}
type ghCheck struct {
	ID                                             int64 `json:"id"`
	Name, HeadSHA, Status, Conclusion, CompletedAt string
	Output                                         struct{ Summary, Text string }
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
func gitHead() (string, error) { return gitPick(headOverride, "HEAD", "git HEAD", 7) }
func gitRoot() (string, error) { return gitPick(rootOverride, "--show-toplevel", "git root", 1) }
func shardUnits(s State) []string {
	if len(s.HeadSHA) != 40 {
		return []string{"ralph"}
	}
	base := s.BaseSHA
	if base == "" {
		base, _ = gitOut("merge-base", "HEAD", "origin/main")
	}
	out, err := gitOut("diff", "--name-only", base+"..."+s.HeadSHA)
	if err != nil || out == "" {
		return []string{"ralph"}
	}
	seen, u := map[string]bool{}, []string{}
	for _, n := range strings.Split(out, "\n") {
		if top := strings.Split(strings.TrimSpace(n), "/")[0]; top != "" && !seen[top] {
			seen[top] = true
			u = append(u, top)
		}
	}
	if len(u) == 0 {
		u = []string{"ralph"}
	}
	return u
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
func blocking(fs []Finding) []Finding {
	var o []Finding
	for _, f := range fs {
		if f.Blocking {
			o = append(o, f)
		}
	}
	return o
}
func product(fs []Finding) []Finding {
	var o []Finding
	for _, f := range blocking(fs) {
		if !strings.HasPrefix(f.ID, "SAUL_EVIDENCE_") {
			o = append(o, f)
		}
	}
	return o
}
func mergeFindings(a, b []Finding) []Finding {
	seen, o := map[string]int{}, []Finding{}
	for _, f := range append(append([]Finding{}, a...), b...) {
		if f.ID == "" {
			continue
		}
		if i, ok := seen[f.ID]; ok {
			o[i] = f
			continue
		}
		seen[f.ID] = len(o)
		o = append(o, f)
	}
	return o
}
func findingsHash(fs []Finding) string {
	if fs == nil {
		fs = []Finding{}
	}
	b, _ := json.Marshal(fs)
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:])
}
func saulConverged(s State) bool {
	r := s.Saul
	if !r.Trusted || r.SHA == "" || r.SHA != s.HeadSHA {
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
	return r.LocalArch == StPass && r.ImpactArch == StPass && r.SystemArch == StPass && len(blocking(r.Findings)) == 0
}
func Ready(s State) bool {
	return len(blocking(s.Blockers)) == 0 && s.CI == StPass && s.CIAt == s.HeadSHA && saulConverged(s) && s.Sai == StPass && s.SaiSHA == s.HeadSHA
}
func Decide(s State) Action {
	ciOK := s.CI == StPass && s.CIAt == s.HeadSHA
	switch {
	case Ready(s):
		return ActReady
	case !ciOK && ((s.CI == StFail && s.CIAt == s.HeadSHA) || len(product(s.Blockers)) > 0):
		return ActRemediate
	case !ciOK && s.CI == StPending && s.CIAt == s.HeadSHA:
		return ActWaitCI
	case !ciOK:
		return ActImplement
	case !saulConverged(s) && (len(product(s.Blockers)) > 0 || len(product(s.Saul.Findings)) > 0):
		return ActRemediate
	case !saulConverged(s):
		return ActWaitSaul
	case s.Sai == StFail && s.SaiSHA == s.HeadSHA:
		return ActRemediate
	case s.Sai != StPass || s.SaiSHA != s.HeadSHA:
		return ActWaitSai
	default:
		return ActObserve
	}
}
func Observe(head string, s State) State {
	if head == "" {
		head = s.HeadSHA
	}
	if s.HeadSHA != "" && head != s.HeadSHA {
		s.CI = map[bool]Status{true: s.CI, false: StStale}[s.CIAt == head]
		s.Saul.Trusted = s.Saul.Trusted && s.Saul.SHA == head
		s.Sai = map[bool]Status{true: s.Sai, false: StStale}[s.SaiSHA == head]
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
	s.NextAction = Decide(s)
	s.Phase = s.NextAction
	if s.NextAction != ActImplement && s.NextAction != ActRemediate {
		s.Grant, s.Dispatch = Grant{}, Disp{}
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
	return json.Marshal(e)
}
func untrusted(s State, extra ...Finding) State {
	if s.HeadSHA != "" {
		s.Saul = Review{SHA: s.HeadSHA, Trusted: false}
	}
	if len(extra) > 0 {
		s.Blockers = mergeFindings(s.Blockers, extra)
	}
	return Observe(s.HeadSHA, s)
}
func IntegrateSaul(s State, e Evidence, pub ed25519.PublicKey, checkID int64) State {
	if s.BaseSHA == "" {
		s.BaseSHA = e.BaseSHA
	}
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
	req := e.SchemaVersion == schemaV1 && e.Repository == ghRepo() && e.PR == s.PR && e.PR != 0 &&
		e.BaseSHA == s.BaseSHA && e.HeadSHA == s.HeadSHA && e.HeadSHA != "" && e.ManifestHash != "" &&
		idOK && e.KeyID != "" && e.CheckRunID != 0 && (checkID == 0 || e.CheckRunID == checkID) &&
		e.CodexInvoked && !e.Synthetic && cover && e.LocalArch != "" && e.ImpactArch != "" &&
		e.SystemArch != "" && e.FindingSetHash == findingsHash(e.Findings) && len(e.Tests) > 0 && e.FinalDisposition != ""
	if !req || err != nil || err2 != nil || len(pub) == 0 || !ed25519.Verify(pub, msg, sig) {
		return untrusted(s)
	}
	r := Review{SHA: e.HeadSHA, Trusted: true, Shards: e.Shards, LocalArch: e.LocalArch, ImpactArch: e.ImpactArch, SystemArch: e.SystemArch, Findings: e.Findings}
	s.Saul = r
	var keep []Finding
	for _, f := range s.Blockers {
		if !strings.HasPrefix(f.ID, "SAUL_EVIDENCE_") {
			keep = append(keep, f)
		}
	}
	s.Blockers = mergeFindings(keep, blocking(r.Findings))
	s.Workers = workMerge(s.Workers, s.Blockers, s.HeadSHA)
	return Observe(s.HeadSHA, s)
}
func workMerge(old []WorkItem, fs []Finding, head string) []WorkItem {
	st := map[string]string{}
	for _, w := range old {
		st[w.ID] = w.Status
	}
	var ws []WorkItem
	for _, f := range fs {
		sc := f.Scope
		if len(sc) == 0 {
			sc = defaultScope()
		}
		w := WorkItem{ID: f.ID, Objective: f.Objective, BaseSHA: head, Scope: sc, Status: "OPEN"}
		if x, ok := st[f.ID]; ok && x != "STALE" {
			w.Status = x
		}
		ws = append(ws, w)
	}
	return ws
}
func SetCI(s State, st Status, sha string) State {
	if sha != s.HeadSHA {
		s.CI = StStale
		return Observe(s.HeadSHA, s)
	}
	s.CI, s.CIAt = st, sha
	return Observe(s.HeadSHA, s)
}
func SetSai(s State, st Status, sha string, fs []Finding) State {
	if st == StPass && !saulConverged(s) {
		return Observe(s.HeadSHA, s)
	}
	if sha != s.HeadSHA {
		s.Sai = StStale
		return Observe(s.HeadSHA, s)
	}
	s.Sai, s.SaiSHA = st, sha
	if st == StFail {
		if len(fs) == 0 {
			fs = []Finding{{ID: "SAI", Source: "sai", Objective: "remediate Sai governance blocker", Blocking: true, Scope: defaultScope()}}
		}
		s.Blockers = mergeFindings(s.Blockers, fs)
		s.Workers = workMerge(s.Workers, s.Blockers, s.HeadSHA)
	}
	return Observe(s.HeadSHA, s)
}
func CompleteWork(s State, r WorkerResult) (State, error) {
	w := findItem(s, r.WorkItem)
	switch {
	case r.SetsReady || r.Status == "READY_FOR_HUMAN_REVIEW" || r.Status == "done" || r.Status == "approved":
		return s, fmt.Errorf("worker cannot set terminal state")
	case w == nil:
		return s, fmt.Errorf("unknown work item")
	case r.BaseSHA != s.HeadSHA || w.BaseSHA != s.HeadSHA:
		return s, fmt.Errorf("stale work item")
	}
	if r.Status == "" {
		r.Status = "COMPLETE"
	}
	w.Status = r.Status
	head, err := gitHead()
	if err != nil {
		return s, err
	}
	return Observe(head, s), nil
}
func defaultScope() []string { return []string{"ralph/", ".cursor/", ".github/"} }
func ensureWorkItem(s State) State {
	if s.NextAction != ActImplement && s.NextAction != ActRemediate {
		s.Grant, s.Dispatch = Grant{}, Disp{}
		return s
	}
	if b := blocking(s.Blockers); len(b) > 0 {
		s.Workers = workMerge(s.Workers, b, s.HeadSHA)
		sc := b[0].Scope
		if len(sc) == 0 {
			sc = defaultScope()
		}
		s.Grant = Grant{WorkItem: b[0].ID, HeadSHA: s.HeadSHA, Objective: b[0].Objective, Scope: sc}
	} else {
		id, obj := "kernel", "advance Ralph control kernel"
		if s.CI == StFail {
			id, obj = "CI", "remediate deterministic CI failure"
		}
		s.Workers = workMerge(s.Workers, []Finding{{ID: id, Objective: obj, Blocking: true, Scope: defaultScope()}}, s.HeadSHA)
		s.Grant = Grant{WorkItem: id, HeadSHA: s.HeadSHA, Objective: obj, Scope: defaultScope()}
	}
	s.Dispatch = Disp{Kind: "cursor_primary", Grant: s.Grant, Head: s.HeadSHA}
	return s
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
func shellOK(cmd string) bool {
	c := strings.TrimSpace(cmd)
	low := strings.ToLower(c)
	deny := c == "" || strings.ContainsAny(c, "|;$()`<>") || strings.Contains(c, "&&") || strings.Contains(c, "../") ||
		strings.Contains(c, "\n") || strings.Contains(c, "<<") || strings.Contains(low, "-x post") ||
		strings.Contains(low, "-x put") || strings.Contains(low, "-x patch") || strings.Contains(low, "-x delete") ||
		strings.HasPrefix(low, "git checkout") || ((strings.HasPrefix(low, "gofmt") || strings.HasPrefix(low, "go fmt")) && strings.Contains(low, "-w"))
	if deny {
		return false
	}
	for _, p := range shellPref {
		if strings.HasPrefix(c, p) {
			return true
		}
	}
	return false
}
func allow() map[string]any { return map[string]any{"permission": "allow"} }
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
	case in.ToolName == "Shell" && shellOK(fmt.Sprint(in.ToolInput["command"])):
		return allow()
	case in.ToolName == "Shell":
		return deny("SHELL_MUTATION")
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
	rel, err := repoRel(path, root)
	if err != nil {
		return deny("PATH")
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
func ghRepo() string {
	if r := os.Getenv("GITHUB_REPOSITORY"); r != "" {
		return r
	}
	return "Dezocode/Sai"
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
	err := ghJSON("GET", "/repos/"+ghRepo()+"/commits/"+sha+"/check-runs?per_page=100", nil, &wrap)
	return wrap.CheckRuns, err
}
func persist(s State) error {
	if err := saveState(statePath(), s); err != nil || localOnly() {
		return err
	}
	sum, err := json.Marshal(s)
	if err != nil {
		return err
	}
	conc := map[bool]string{true: "success", false: "neutral"}[Ready(s)]
	if err := ghJSON("POST", "/repos/"+ghRepo()+"/check-runs", map[string]any{
		"name": checkRalph, "head_sha": s.HeadSHA, "status": "completed", "conclusion": conc,
		"output": map[string]string{"title": string(s.NextAction), "summary": string(sum)},
	}, nil); err != nil {
		fmt.Fprintln(os.Stderr, "ralph persist:", err)
	}
	return nil
}
func recoverState(head string) (State, error) {
	boot := State{ProgramID: "pr68-ralph", PR: 68, HeadSHA: head, CI: StMissing, Sai: StMissing}
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
		if runs[i].Name == checkRalph && runs[i].Output.Summary != "" {
			var s State
			if err := json.Unmarshal([]byte(runs[i].Output.Summary), &s); err != nil {
				return State{}, err
			}
			return Observe(head, s), nil
		}
	}
	if lerr == nil && local.HeadSHA == head {
		return Observe(head, local), nil
	}
	return boot, nil
}
func integrateWorld(s State) (State, error) {
	if localOnly() {
		return s, nil
	}
	runs, err := listChecks(s.HeadSHA)
	if err != nil {
		return s, err
	}
	ci, sawSaul := map[string]string{}, false
	for _, c := range runs {
		if c.HeadSHA != "" && c.HeadSHA != s.HeadSHA {
			continue
		}
		if c.Name == checkSaul {
			sawSaul = true
			var e Evidence
			pub, perr := loadPub()
			switch {
			case c.Status == "completed" && strings.TrimSpace(c.Output.Text) == "":
				s = untrusted(s, Finding{ID: "SAUL_EVIDENCE_TEXT", Source: "ralph", Objective: "Hostinger must publish signed Evidence JSON in Check output.text; sandbox=" + saulSandbox, Blocking: true, Scope: defaultScope()})
			case json.Unmarshal([]byte(c.Output.Text), &e) != nil || perr != nil:
				s = untrusted(s)
			default:
				s = IntegrateSaul(s, e, pub, c.ID)
			}
		}
		for _, n := range ciNames {
			if c.Name == n {
				ci[n] = map[bool]string{true: "pending", false: map[bool]string{true: "pass", false: "fail"}[c.Conclusion == "success"]}[c.Status != "completed"]
			}
		}
	}
	if !sawSaul && s.Saul.SHA != s.HeadSHA {
		s.Saul = Review{SHA: s.HeadSHA, Trusted: false}
	}
	st := Status(StPass)
	for _, n := range ciNames {
		if ci[n] == "fail" {
			st = StFail
		} else if ci[n] != "pass" && st != StFail {
			st = StPending
		}
	}
	s = SetCI(s, st, s.HeadSHA)
	if saulConverged(s) {
		return ingestSai(s)
	}
	return s, nil
}
func ingestSai(s State) (State, error) {
	var raw []struct {
		Body     string `json:"body"`
		CommitID string `json:"commit_id"`
	}
	pr := s.PR
	if pr == 0 {
		pr = 68
	}
	if err := ghJSON("GET", fmt.Sprintf("/repos/%s/pulls/%d/reviews", ghRepo(), pr), nil, &raw); err != nil {
		return s, err
	}
	for i := len(raw) - 1; i >= 0; i-- {
		r := raw[i]
		if !strings.Contains(r.Body, "[SAI Governance Review]") || (r.CommitID != "" && r.CommitID != s.HeadSHA && !strings.HasPrefix(s.HeadSHA, r.CommitID)) {
			continue
		}
		if strings.Contains(r.Body, "Classification: APPROVE") {
			return SetSai(s, StPass, s.HeadSHA, nil), nil
		}
		return SetSai(s, StFail, s.HeadSHA, []Finding{{ID: "SAI", Source: "sai", Objective: "remediate Sai governance finding", Blocking: true, Scope: defaultScope()}}), nil
	}
	return s, nil
}
func dispatch(s State) State {
	s = ensureWorkItem(s)
	if s.NextAction == ActWaitSaul && !localOnly() {
		if _, err := os.Stat("/opt/sai/trusted-reviewer/scripts/saul-hostinger-bootstrap-review"); err == nil {
			_ = exec.Command("/opt/sai/trusted-reviewer/scripts/saul-hostinger-bootstrap-review", "--head", s.HeadSHA).Run()
		} else {
			_ = ghJSON("POST", "/repos/"+ghRepo()+"/dispatches", map[string]any{
				"event_type": "saul-review", "client_payload": map[string]string{"sha": s.HeadSHA, "pr": fmt.Sprint(s.PR)},
			}, nil)
		}
	}
	return s
}
func step(s State) (State, error) {
	head, err := gitHead()
	if err != nil {
		return s, err
	}
	s = Observe(head, s)
	s, err = integrateWorld(s)
	if err != nil {
		return s, err
	}
	s = dispatch(Observe(head, s))
	return s, persist(s)
}
func Cycle() (State, error) {
	head, err := gitHead()
	if err != nil {
		return State{}, err
	}
	s, err := recoverState(head)
	if err != nil {
		return s, err
	}
	return step(s)
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
func SignEvidence(priv ed25519.PrivateKey, sha string, r Review) Evidence {
	e := Evidence{SchemaVersion: schemaV1, Repository: ghRepo(), PR: 68, BaseSHA: sha, HeadSHA: sha, ManifestHash: "m", ReviewerIdentity: "hostinger-saul-cto", KeyID: "saul-attestation-ed25519", CheckRunID: 1, CodexInvoked: true, Shards: r.Shards, LocalArch: r.LocalArch, ImpactArch: r.ImpactArch, SystemArch: r.SystemArch, Findings: r.Findings, Tests: []string{"go test ./ralph"}, FinalDisposition: "action_required"}
	for _, p := range []*Status{&e.LocalArch, &e.ImpactArch, &e.SystemArch} {
		if *p == "" {
			*p = StFail
		}
	}
	e.FindingSetHash = findingsHash(e.Findings)
	msg, _ := signMsg(e)
	e.Sig = hex.EncodeToString(ed25519.Sign(priv, msg))
	return e
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
	case readOnly[in.ToolName] || (in.ToolName == "Shell" && shellOK(cmd)):
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
	dead, delay, n := time.Now().Add(5*time.Hour), 15*time.Second, 0
	if fmt.Sscanf(os.Getenv("RALPH_WAIT_MS"), "%d", &n); n > 0 {
		dead = time.Now().Add(time.Duration(n) * time.Millisecond)
	}
	if fmt.Sscanf(os.Getenv("RALPH_POLL_MS"), "%d", &n); n > 0 {
		delay = time.Duration(n) * time.Millisecond
	}
	for {
		s, err := Cycle()
		_ = json.NewEncoder(os.Stdout).Encode(s)
		switch {
		case err != nil:
			fmt.Fprintln(os.Stderr, "ralph:", err)
			return 2
		case Ready(s):
			return 0
		}
		fmt.Fprintf(os.Stderr, "NONTERMINAL head=%s phase=%s action=%s dispatch=%s\n", s.HeadSHA, s.Phase, s.NextAction, s.Dispatch.Kind)
		if once || s.NextAction == ActImplement || s.NextAction == ActRemediate || time.Now().After(dead) {
			return 1
		}
		time.Sleep(delay)
	}
}
func main() {
	cmd, once := "hook", false
	if len(os.Args) > 1 && !strings.HasPrefix(os.Args[1], "-") {
		cmd = os.Args[1]
	}
	for _, a := range os.Args {
		if a == "--once" {
			once = true
		}
	}
	switch cmd {
	case "hook":
		os.Exit(hookMain())
	case "run":
		os.Exit(runMain(once))
	default:
		fmt.Fprintln(os.Stderr, "ralph commands: hook run")
		os.Exit(2)
	}
}
