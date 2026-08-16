package main

import (
	"bytes"
	"crypto/ed25519"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
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
	ID, Source, Objective string
	Scope                 []string
	Blocking              bool
}
type WorkItem struct {
	ID, Objective, BaseSHA, Status string
	Scope                          []string
}
type Grant struct {
	WorkItem, HeadSHA, Objective string
	Scope                        []string
}
type Shard struct {
	ID     string
	Status Status
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
	SHA, Sig, ImplementationHead string
	Review                       Review
	Synthetic, CodexInvoked      bool
}
type hookIn struct {
	ToolName  string         `json:"tool_name"`
	ToolInput map[string]any `json:"tool_input"`
}
type ghCheck struct {
	Name, HeadSHA, Status, Conclusion string
	Output                            struct{ Summary string } `json:"output"`
}

func gitOut(args ...string) (string, error) {
	cmd := exec.Command("git", args...)
	if rootOverride != "" {
		cmd.Dir = rootOverride
	}
	out, err := cmd.Output()
	return strings.TrimSpace(string(out)), err
}

func gitHead() (string, error) {
	if headOverride != "" {
		return headOverride, nil
	}
	h, err := gitOut("rev-parse", "HEAD")
	if err != nil || len(h) < 7 {
		return "", fmt.Errorf("git HEAD")
	}
	return h, nil
}

func gitRoot() (string, error) {
	if rootOverride != "" {
		return rootOverride, nil
	}
	r, err := gitOut("rev-parse", "--show-toplevel")
	if err != nil || r == "" {
		return "", fmt.Errorf("git root")
	}
	return r, nil
}

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
		return []string{"ralph"}
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
		if res, err := filepath.EvalSymlinks(clean); err != nil {
			return "", fmt.Errorf("symlink")
		} else {
			clean = res
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
	if Ready(s) {
		return ActReady
	}
	ciOK := s.CI == StPass && s.CIAt == s.HeadSHA
	if !ciOK {
		if (s.CI == StFail && s.CIAt == s.HeadSHA) || len(blocking(s.Blockers)) > 0 {
			return ActRemediate
		}
		if s.CI == StPending && s.CIAt == s.HeadSHA {
			return ActWaitCI
		}
		return ActImplement
	}
	if !saulConverged(s) {
		if len(blocking(s.Blockers)) > 0 || len(blocking(s.Saul.Findings)) > 0 {
			return ActRemediate
		}
		return ActWaitSaul
	}
	if s.Sai != StPass || s.SaiSHA != s.HeadSHA {
		if s.Sai == StFail && s.SaiSHA == s.HeadSHA {
			return ActRemediate
		}
		return ActWaitSai
	}
	return ActObserve
}

func Observe(head string, s State) State {
	if head == "" {
		head = s.HeadSHA
	}
	if s.HeadSHA != "" && head != s.HeadSHA {
		if s.CIAt != head {
			s.CI = StStale
		}
		if s.Saul.SHA != head {
			s.Saul.Trusted = false
		}
		if s.SaiSHA != head {
			s.Sai = StStale
		}
		s.Grant = Grant{}
		for i := range s.Workers {
			if s.Workers[i].BaseSHA != head {
				s.Workers[i].Status = "STALE"
			}
		}
	}
	s.HeadSHA = head
	s.NextAction = Decide(s)
	s.Phase = s.NextAction
	if s.NextAction != ActImplement && s.NextAction != ActRemediate {
		s.Grant = Grant{}
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
	return json.Marshal(struct {
		SHA                     string
		Review                  Review
		Synthetic, CodexInvoked bool
	}{e.SHA, e.Review, e.Synthetic, e.CodexInvoked})
}

func IntegrateSaul(s State, e Evidence, pub ed25519.PublicKey) State {
	head := e.ImplementationHead
	if head == "" {
		head = e.SHA
	}
	fail := func() State {
		if head == s.HeadSHA {
			s.Saul = Review{SHA: head, Trusted: false}
		}
		return Observe(s.HeadSHA, s)
	}
	msg, err := signMsg(e)
	sig, err2 := hex.DecodeString(e.Sig)
	if e.Synthetic || !e.CodexInvoked || head != s.HeadSHA || e.SHA != s.HeadSHA || err != nil || err2 != nil || len(pub) == 0 || !ed25519.Verify(pub, msg, sig) {
		return fail()
	}
	r := e.Review
	r.Trusted, r.SHA = true, e.SHA
	s.Saul, s.Blockers = r, blocking(r.Findings)
	if len(s.Blockers) > 0 {
		s.Workers = workFrom(s.Blockers, s.HeadSHA)
	}
	return Observe(s.HeadSHA, s)
}

func workFrom(fs []Finding, head string) []WorkItem {
	var ws []WorkItem
	for _, f := range fs {
		sc := f.Scope
		if len(sc) == 0 {
			sc = defaultScope()
		}
		ws = append(ws, WorkItem{ID: f.ID, Objective: f.Objective, BaseSHA: head, Scope: sc, Status: "OPEN"})
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
		s.Blockers = append(blocking(s.Blockers), fs...)
		s.Workers = workFrom(fs, s.HeadSHA)
	}
	return Observe(s.HeadSHA, s)
}

func CompleteWork(s State, r WorkerResult) (State, error) {
	if r.SetsReady || r.Status == "READY_FOR_HUMAN_REVIEW" || r.Status == "done" || r.Status == "approved" {
		return s, fmt.Errorf("worker cannot set terminal state")
	}
	w := findItem(s, r.WorkItem)
	if w == nil {
		return s, fmt.Errorf("unknown work item")
	}
	if r.BaseSHA != s.HeadSHA || w.BaseSHA != s.HeadSHA {
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
		s.Grant = Grant{}
		return s
	}
	if b := blocking(s.Blockers); len(b) > 0 {
		s.Workers = workFrom(b, s.HeadSHA)
		sc := b[0].Scope
		if len(sc) == 0 {
			sc = defaultScope()
		}
		s.Grant = Grant{WorkItem: b[0].ID, HeadSHA: s.HeadSHA, Objective: b[0].Objective, Scope: sc}
		return s
	}
	id, obj := "kernel", "advance Ralph control kernel"
	if s.CI == StFail {
		id, obj = "CI", "remediate deterministic CI failure"
	}
	s.Workers = []WorkItem{{ID: id, Objective: obj, BaseSHA: s.HeadSHA, Scope: defaultScope(), Status: "OPEN"}}
	s.Grant = Grant{WorkItem: id, HeadSHA: s.HeadSHA, Objective: obj, Scope: defaultScope()}
	return s
}

func localOnly() bool { return os.Getenv("RALPH_LOCAL_ONLY") == "1" }

func loadState(path string) (State, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return State{}, err
	}
	var s State
	return s, json.Unmarshal(b, &s)
}

func saveState(path string, s State) error {
	b, err := json.MarshalIndent(s, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(b, '\n'), 0644)
}

func statePath() string {
	if p := os.Getenv("RALPH_STATE"); p != "" {
		return p
	}
	return ".ralph-state.json"
}

func shellOK(cmd string) bool {
	c := strings.TrimSpace(cmd)
	low := strings.ToLower(c)
	if c == "" || strings.ContainsAny(c, "|;$()<>") || strings.Contains(c, "&&") || strings.Contains(c, "../") {
		return false
	}
	if strings.Contains(low, "-x post") || strings.Contains(low, "-x put") || strings.Contains(low, "-x patch") || strings.Contains(low, "-x delete") {
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
	if in.ToolName == "" {
		return deny("MALFORMED")
	}
	if readOnly[in.ToolName] {
		return allow()
	}
	if in.ToolName == "Shell" {
		cmd, _ := in.ToolInput["command"].(string)
		if shellOK(cmd) {
			return allow()
		}
		return deny("SHELL_MUTATION")
	}
	if !mutate[in.ToolName] {
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
	out, err := exec.Command("gh", "auth", "token").Output()
	if err != nil {
		return ""
	}
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
	req.Header.Set("Authorization", "Bearer "+tok)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("Content-Type", "application/json")
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
	if err := saveState(statePath(), s); err != nil {
		return err
	}
	if localOnly() {
		return nil
	}
	sum, err := json.Marshal(s)
	if err != nil {
		return err
	}
	conc := "neutral"
	if Ready(s) {
		conc = "success"
	}
	return ghJSON("POST", "/repos/"+ghRepo()+"/check-runs", map[string]any{
		"name": checkRalph, "head_sha": s.HeadSHA, "status": "completed", "conclusion": conc,
		"output": map[string]string{"title": string(s.NextAction), "summary": string(sum)},
	}, nil)
}

func recoverState(head string) (State, error) {
	boot := State{ProgramID: "pr68-ralph", PR: 68, HeadSHA: head, CI: StMissing, Sai: StMissing}
	local, lerr := loadState(statePath())
	if localOnly() {
		if lerr != nil {
			return boot, nil
		}
		return Observe(head, local), nil
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
	ci := map[string]string{}
	for _, c := range runs {
		if c.HeadSHA != "" && c.HeadSHA != s.HeadSHA {
			continue
		}
		if c.Name == checkSaul && c.Output.Summary != "" {
			var e Evidence
			if json.Unmarshal([]byte(c.Output.Summary), &e) != nil {
				s.Saul = Review{SHA: s.HeadSHA, Trusted: false}
			} else if pub, perr := loadPub(); perr != nil {
				s.Saul = Review{SHA: s.HeadSHA, Trusted: false}
			} else {
				s = IntegrateSaul(s, e, pub)
			}
		}
		for _, n := range ciNames {
			if c.Name == n {
				switch {
				case c.Status != "completed":
					ci[n] = "pending"
				case c.Conclusion == "success":
					ci[n] = "pass"
				default:
					ci[n] = "fail"
				}
			}
		}
	}
	st := Status(StPass)
	for _, n := range ciNames {
		switch ci[n] {
		case "fail":
			st = StFail
		case "", "pending":
			if st != StFail {
				st = StPending
			}
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
		if !strings.Contains(r.Body, "[SAI Governance Review]") {
			continue
		}
		if r.CommitID != "" && r.CommitID != s.HeadSHA && !strings.HasPrefix(s.HeadSHA, r.CommitID) {
			continue
		}
		if strings.Contains(r.Body, "Classification: APPROVE") {
			return SetSai(s, StPass, s.HeadSHA, nil), nil
		}
		fs := []Finding{{ID: "SAI", Source: "sai", Objective: "remediate Sai governance finding", Blocking: true, Scope: defaultScope()}}
		return SetSai(s, StFail, s.HeadSHA, fs), nil
	}
	return s, nil
}

func dispatch(s State) State {
	s = ensureWorkItem(s)
	if s.NextAction == ActWaitSaul {
		if _, err := os.Stat("/opt/sai/trusted-reviewer/scripts/saul-hostinger-bootstrap-review"); err == nil {
			_ = exec.Command("/opt/sai/trusted-reviewer/scripts/saul-hostinger-bootstrap-review", "--head", s.HeadSHA).Run()
		} else {
			_ = ghJSON("POST", "/repos/"+ghRepo()+"/dispatches", map[string]any{
				"event_type":     "saul-review",
				"client_payload": map[string]string{"sha": s.HeadSHA, "pr": fmt.Sprint(s.PR)},
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
		if st, err := os.Stat(p); err == nil && !st.IsDir() {
			b, err := os.ReadFile(p)
			if err != nil {
				return nil, err
			}
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
	e := Evidence{SHA: sha, Review: r, CodexInvoked: true, ImplementationHead: sha}
	msg, _ := signMsg(e)
	e.Sig = hex.EncodeToString(ed25519.Sign(priv, msg))
	return e
}

func hookMain() int {
	raw, err := io.ReadAll(os.Stdin)
	out := deny("MALFORMED")
	if err == nil {
		var in hookIn
		if json.Unmarshal(raw, &in) != nil || in.ToolName == "" {
			var m map[string]any
			_ = json.Unmarshal(raw, &m)
			if t, ok := m["toolName"].(string); ok {
				in.ToolName = t
			}
		}
		if in.ToolInput == nil {
			in.ToolInput = map[string]any{}
		}
		cmd, _ := in.ToolInput["command"].(string)
		head, herr := gitHead()
		root, rerr := gitRoot()
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
			if lerr != nil {
				out = deny("NO_STATE")
			} else {
				out = hookDecision(s, in, head, root)
			}
		}
	}
	_ = json.NewEncoder(os.Stdout).Encode(out)
	return 0
}

func runMain(once bool) int {
	deadline, delay := time.Now().Add(8*time.Minute), 5*time.Second
	if v := os.Getenv("RALPH_POLL_MS"); v != "" {
		var n int
		fmt.Sscanf(v, "%d", &n)
		delay = time.Duration(n) * time.Millisecond
	}
	for {
		s, err := Cycle()
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		_ = enc.Encode(s)
		if err != nil {
			fmt.Fprintln(os.Stderr, "ralph:", err)
			return 2
		}
		if Ready(s) {
			return 0
		}
		fmt.Fprintf(os.Stderr, "NONTERMINAL head=%s phase=%s action=%s\n", s.HeadSHA, s.Phase, s.NextAction)
		if once || time.Now().After(deadline) || s.NextAction == ActImplement || s.NextAction == ActRemediate {
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
