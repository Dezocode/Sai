// Ralph: executable control kernel. Exact HEAD is reality.
// logical_program_terminal == READY_FOR_HUMAN_REVIEW only.
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
)

type Phase string
type Action string
type Status string

const (
	PhaseImplement Phase = "IMPLEMENT"
	PhaseCI        Phase = "WAIT_CI"
	PhaseSaul      Phase = "WAIT_SAUL"
	PhaseSai       Phase = "WAIT_SAI"
	PhaseReady     Phase = "READY_FOR_HUMAN_REVIEW"
	PhaseObserve   Phase = "OBSERVE"

	ActImplement Action = "IMPLEMENT"
	ActWaitCI    Action = "WAIT_CI"
	ActWaitSaul  Action = "WAIT_SAUL"
	ActWaitSai   Action = "WAIT_SAI"
	ActRemediate Action = "REMEDIATE"
	ActReady     Action = "READY_FOR_HUMAN_REVIEW"
	ActObserve   Action = "OBSERVE"

	StMissing Status = "missing"
	StPending Status = "pending"
	StPass    Status = "pass"
	StFail    Status = "fail"
	StStale   Status = "stale"

	DecisionAllow = "ALLOW"
	DecisionDeny  = "DENY"
)

type Finding struct {
	ID, Source, Objective string
	Scope                 []string
	Blocking              bool
}

type WorkItem struct {
	ID, Objective, BaseSHA, Authz, Status string
	Scope                                 []string
}

type Shard struct {
	ID     string
	Status Status
}

type Review struct {
	SHA                                 string
	Trusted                             bool
	Shards                              []Shard
	LocalArch, ImpactArch, SystemArch   Status
	Findings                            []Finding
}

type State struct {
	ProgramID                    string
	PR                           int
	HeadSHA                      string
	Phase                        Phase
	RequirementsOpen             int
	ExpectedUnits                []string
	Blockers                     []Finding
	Workers                      []WorkItem
	CI   Status
	CIAt string
	Saul                         Review
	Sai                          Status
	SaiSHA                       string
	NextAction                   Action
	AuthHead                     string
}

type Decision struct {
	Decision, Reason, HeadSHA, WorkItem, Objective, NextAction string
	Scope                                                      []string
}

type AuthReq struct {
	HeadSHA, Path, WorkItem, Tool string
}

type WorkerResult struct {
	WorkItem, BaseSHA, ResultSHA, Status string
	SetsReady                            bool
}

type Evidence struct {
	SHA    string
	Review Review
	Sig    string
}

type hookIn struct {
	ToolName  string         `json:"tool_name"`
	ToolInput map[string]any `json:"tool_input"`
}

func gitHead() string {
	out, err := exec.Command("git", "rev-parse", "HEAD").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
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
	if len(s.ExpectedUnits) == 0 {
		return false
	}
	got := map[string]Status{}
	for _, sh := range r.Shards {
		got[sh.ID] = sh.Status
	}
	for _, id := range s.ExpectedUnits {
		if got[id] != StPass {
			return false
		}
	}
	if r.LocalArch != StPass || r.ImpactArch != StPass || r.SystemArch != StPass {
		return false
	}
	return len(blocking(r.Findings)) == 0
}

func Ready(s State) bool {
	return s.RequirementsOpen == 0 &&
		len(blocking(s.Blockers)) == 0 &&
		s.CI == StPass && s.CIAt == s.HeadSHA &&
		saulConverged(s) &&
		s.Sai == StPass && s.SaiSHA == s.HeadSHA
}

func hasOpenWork(s State) bool {
	for _, w := range s.Workers {
		if w.Status != "COMPLETE" && w.ID != "" {
			return true
		}
	}
	return false
}

func Decide(s State) Action {
	if Ready(s) {
		return ActReady
	}
	ciCurrentPass := s.CI == StPass && s.CIAt == s.HeadSHA
	if !ciCurrentPass {
		if s.CI == StFail && s.CIAt == s.HeadSHA {
			return ActRemediate
		}
		if s.CI == StMissing && s.CIAt == "" && hasOpenWork(s) {
			if len(blocking(s.Blockers)) > 0 {
				return ActRemediate
			}
			return ActImplement
		}
		return ActWaitCI
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
	if s.RequirementsOpen > 0 {
		return ActImplement
	}
	return ActObserve
}

func phaseOf(a Action) Phase {
	switch a {
	case ActImplement, ActRemediate:
		return PhaseImplement
	case ActWaitCI:
		return PhaseCI
	case ActWaitSaul:
		return PhaseSaul
	case ActWaitSai:
		return PhaseSai
	case ActReady:
		return PhaseReady
	default:
		return PhaseObserve
	}
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
		s.AuthHead = ""
		for i := range s.Workers {
			if s.Workers[i].BaseSHA != head {
				s.Workers[i].Authz = ""
			}
		}
	}
	s.HeadSHA = head
	s.NextAction = Decide(s)
	s.Phase = phaseOf(s.NextAction)
	if s.NextAction == ActReady {
		s.Phase = PhaseReady
	}
	return s
}

func token(head, id string) string {
	sum := sha256.Sum256([]byte(head + "|" + id))
	return hex.EncodeToString(sum[:8])
}

func inScope(path string, scope []string) bool {
	if path == "" || len(scope) == 0 {
		return false
	}
	path = filepath.ToSlash(path)
	for _, s := range scope {
		s = filepath.ToSlash(s)
		if s == path || strings.HasPrefix(path, strings.TrimSuffix(s, "/")+"/") || (strings.HasSuffix(s, "/**") && strings.HasPrefix(path, strings.TrimSuffix(s, "/**")+"/")) {
			return true
		}
		if strings.HasSuffix(s, "/") && strings.HasPrefix(path, s) {
			return true
		}
	}
	return false
}

func findItem(s State, id string) *WorkItem {
	for i := range s.Workers {
		if s.Workers[i].ID == id && s.Workers[i].Status != "COMPLETE" {
			return &s.Workers[i]
		}
	}
	return nil
}

func Authorize(s State, req AuthReq) Decision {
	s = Observe(req.HeadSHA, s)
	next := s.NextAction
	d := Decision{HeadSHA: s.HeadSHA, NextAction: string(next), Decision: DecisionDeny}
	if next == ActReady {
		d.Reason = "PROGRAM_READY"
		return d
	}
	if next != ActImplement && next != ActRemediate {
		d.Reason = string(next) + "_REQUIRED"
		return d
	}
	if req.WorkItem == "" && len(s.Workers) == 1 {
		req.WorkItem = s.Workers[0].ID
	}
	w := findItem(s, req.WorkItem)
	if w == nil {
		d.Reason = "UNAUTHORIZED_WORK_ITEM"
		return d
	}
	if w.BaseSHA != s.HeadSHA || req.HeadSHA != s.HeadSHA {
		d.Reason = "STALE_SHA"
		return d
	}
	if req.Path != "" && !inScope(req.Path, w.Scope) {
		d.Reason = "OUT_OF_SCOPE"
		return d
	}
	w.Authz = token(s.HeadSHA, w.ID)
	return Decision{
		Decision: DecisionAllow, HeadSHA: s.HeadSHA, WorkItem: w.ID,
		Scope: w.Scope, Objective: w.Objective, NextAction: string(next),
	}
}

func IntegrateSaul(s State, e Evidence, pub ed25519.PublicKey) State {
	msg, _ := json.Marshal(struct {
		SHA    string
		Review Review
	}{e.SHA, e.Review})
	sig, err := hex.DecodeString(e.Sig)
	if err != nil || len(pub) == 0 || !ed25519.Verify(pub, msg, sig) {
		if e.SHA == s.HeadSHA {
			s.Saul = Review{SHA: e.SHA, Trusted: false}
		}
		return Observe(s.HeadSHA, s)
	}
	r := e.Review
	r.Trusted = true
	r.SHA = e.SHA
	if r.SHA != s.HeadSHA {
		return s
	}
	s.Saul = r
	s.Blockers = blocking(r.Findings)
	if len(s.Blockers) > 0 {
		var ws []WorkItem
		for _, f := range s.Blockers {
			ws = append(ws, WorkItem{ID: f.ID, Objective: f.Objective, BaseSHA: s.HeadSHA, Scope: f.Scope, Status: "OPEN"})
		}
		s.Workers = ws
	}
	return Observe(s.HeadSHA, s)
}

func SetCI(s State, st Status, sha string) State {
	if sha != s.HeadSHA {
		s.CI = StStale
		return Observe(s.HeadSHA, s)
	}
	s.CI, s.CIAt = st, sha
	return Observe(s.HeadSHA, s)
}

func SetSai(s State, st Status, sha string) State {
	if st == StPass && !saulConverged(s) {
		return Observe(s.HeadSHA, s)
	}
	if sha != s.HeadSHA {
		s.Sai = StStale
		return Observe(s.HeadSHA, s)
	}
	s.Sai, s.SaiSHA = st, sha
	if st == StFail {
		s.Blockers = append(s.Blockers, Finding{ID: "SAI", Source: "sai", Objective: "remediate Sai governance blocker", Blocking: true, Scope: []string{"ralph/"}})
		s.Workers = []WorkItem{{ID: "SAI", Objective: "remediate Sai governance blocker", BaseSHA: s.HeadSHA, Scope: []string{"ralph/"}, Status: "OPEN"}}
	}
	return Observe(s.HeadSHA, s)
}

func CompleteWork(s State, r WorkerResult) (State, error) {
	if r.SetsReady {
		return s, fmt.Errorf("worker cannot set terminal state")
	}
	w := findItem(s, r.WorkItem)
	if w == nil {
		return s, fmt.Errorf("unknown work item")
	}
	if r.BaseSHA != s.HeadSHA || w.BaseSHA != s.HeadSHA {
		return s, fmt.Errorf("stale work item")
	}
	w.Status = r.Status
	if r.Status == "" {
		w.Status = "COMPLETE"
	}
	if r.ResultSHA != "" && r.ResultSHA != s.HeadSHA {
		return Observe(r.ResultSHA, s), nil
	}
	return Observe(s.HeadSHA, s), nil
}

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

func pathOf(in hookIn) string {
	for _, k := range []string{"path", "file_path", "target_notebook"} {
		if v, ok := in.ToolInput[k].(string); ok && v != "" {
			return v
		}
	}
	return ""
}

func shellMut(cmd string) bool {
	return strings.Contains(cmd, ">") || strings.Contains(cmd, " tee ")
}

func hookDecision(s State, in hookIn) map[string]any {
	tool := in.ToolName
	path := pathOf(in)
	if tool == "Shell" {
		cmd, _ := in.ToolInput["command"].(string)
		if !shellMut(cmd) {
			return map[string]any{"permission": "allow"}
		}
	}
	item, _ := os.LookupEnv("RALPH_WORK_ITEM")
	d := Authorize(s, AuthReq{HeadSHA: s.HeadSHA, Path: path, WorkItem: item, Tool: tool})
	out := map[string]any{
		"permission":    strings.ToLower(d.Decision),
		"agent_message": fmt.Sprintf("ralph %s %s next=%s", d.Decision, d.Reason, d.NextAction),
	}
	if d.Decision == DecisionAllow {
		out["permission"] = "allow"
		delete(out, "agent_message")
	} else {
		out["permission"] = "deny"
		out["user_message"] = out["agent_message"]
	}
	return out
}

func postCheck(s State) {
	tok, repo := os.Getenv("GITHUB_TOKEN"), os.Getenv("GITHUB_REPOSITORY")
	if tok == "" || repo == "" || s.HeadSHA == "" {
		return
	}
	sum, _ := json.Marshal(s)
	conc := "neutral"
	if Ready(s) {
		conc = "success"
	}
	payload, _ := json.Marshal(map[string]any{
		"name": "Ralph / Program State", "head_sha": s.HeadSHA, "status": "completed", "conclusion": conc,
		"output": map[string]string{"title": string(s.NextAction), "summary": string(sum)},
	})
	req, err := http.NewRequest("POST", "https://api.github.com/repos/"+repo+"/check-runs", bytes.NewReader(payload))
	if err != nil {
		return
	}
	req.Header.Set("Authorization", "Bearer "+tok)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return
	}
	resp.Body.Close()
}

func loadPub() ed25519.PublicKey {
	b, err := os.ReadFile("saul.pub")
	if err != nil {
		b, err = os.ReadFile("ralph/saul.pub")
	}
	if err != nil {
		return nil
	}
	raw, err := hex.DecodeString(strings.TrimSpace(string(b)))
	if err != nil || len(raw) != ed25519.PublicKeySize {
		return nil
	}
	return ed25519.PublicKey(raw)
}

func SignEvidence(priv ed25519.PrivateKey, sha string, r Review) Evidence {
	e := Evidence{SHA: sha, Review: r}
	msg, _ := json.Marshal(struct {
		SHA    string
		Review Review
	}{sha, r})
	e.Sig = hex.EncodeToString(ed25519.Sign(priv, msg))
	return e
}

func main() {
	cmd := "hook"
	if len(os.Args) > 1 && !strings.HasPrefix(os.Args[1], "-") {
		cmd = os.Args[1]
	}
	sp := statePath()
	head := gitHead()
	switch cmd {
	case "hook":
		raw, _ := io.ReadAll(os.Stdin)
		var in hookIn
		_ = json.Unmarshal(raw, &in)
		s, err := loadState(sp)
		out := map[string]any{"permission": "deny", "agent_message": "ralph: no program state"}
		if err == nil {
			s = Observe(head, s)
			out = hookDecision(s, in)
		}
		enc := json.NewEncoder(os.Stdout)
		_ = enc.Encode(out)
	case "authorize":
		path, item := "", ""
		for i, a := range os.Args {
			if a == "-path" && i+1 < len(os.Args) {
				path = os.Args[i+1]
			}
			if a == "-item" && i+1 < len(os.Args) {
				item = os.Args[i+1]
			}
		}
		s, err := loadState(sp)
		if err != nil {
			fmt.Fprintf(os.Stderr, "ralph: %v\n", err)
			os.Exit(1)
		}
		s = Observe(head, s)
		d := Authorize(s, AuthReq{HeadSHA: s.HeadSHA, Path: path, WorkItem: item})
		_ = json.NewEncoder(os.Stdout).Encode(d)
		if d.Decision != DecisionAllow {
			os.Exit(2)
		}
	case "tick":
		s, err := loadState(sp)
		if err != nil {
			fmt.Fprintf(os.Stderr, "ralph: %v\n", err)
			os.Exit(1)
		}
		s = Observe(head, s)
		_ = saveState(sp, s)
		postCheck(s)
		_ = json.NewEncoder(os.Stdout).Encode(s)
	case "ingest-saul":
		s, err := loadState(sp)
		if err != nil {
			os.Exit(1)
		}
		var e Evidence
		_ = json.NewDecoder(os.Stdin).Decode(&e)
		s = Observe(head, s)
		s = IntegrateSaul(s, e, loadPub())
		_ = saveState(sp, s)
		_ = json.NewEncoder(os.Stdout).Encode(s)
	case "complete":
		s, err := loadState(sp)
		if err != nil {
			os.Exit(1)
		}
		var r WorkerResult
		_ = json.NewDecoder(os.Stdin).Decode(&r)
		s, err = CompleteWork(Observe(head, s), r)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		_ = saveState(sp, s)
		_ = json.NewEncoder(os.Stdout).Encode(s)
	case "ready":
		s, err := loadState(sp)
		if err != nil {
			os.Exit(1)
		}
		s = Observe(head, s)
		_ = json.NewEncoder(os.Stdout).Encode(map[string]any{"ready": Ready(s), "action": s.NextAction})
		if !Ready(s) {
			os.Exit(1)
		}
	default:
		fmt.Fprintf(os.Stderr, "ralph commands: hook authorize tick ingest-saul complete ready\n")
		os.Exit(2)
	}
}
