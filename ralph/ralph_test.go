package main

import (
	"bytes"
	"crypto/ed25519"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func base(h string) State {
	return State{ProgramID: "pr68-ralph", PR: 68, HeadSHA: h,
		Workers: []WorkItem{{ID: "w1", Objective: "kernel", BaseSHA: h, Scope: []string{"ralph/"}, Status: "OPEN"}},
		Grant:   Grant{WorkItem: "w1", HeadSHA: h, Objective: "kernel", Scope: []string{"ralph/"}},
		CI:      StMissing, Sai: StMissing}
}
func passReview(h string) Review {
	return Review{SHA: h, Trusted: true, Shards: []Shard{{ID: "ralph", Status: StPass}}, LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass}
}
func impl(h string) State { return Observe(h, base(h)) }

func TestAHLoopAndTerminal(t *testing.T) {
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	headOverride = "aaa"
	t.Cleanup(func() { headOverride = "" })
	t.Setenv("RALPH_STATE", filepath.Join(t.TempDir(), "s.json"))
	s, err := step(impl("aaa"))
	if err != nil || Ready(s) || s.NextAction != ActImplement || s.Grant.WorkItem == "" {
		t.Fatalf("A continue %+v %v", s, err)
	}
	s = SetCI(s, StPending, "aaa")
	s, err = step(s)
	if err != nil || Ready(s) || s.NextAction != ActWaitCI {
		t.Fatalf("A wait %s", s.NextAction)
	}
	empty := State{HeadSHA: "h"}
	empty.CI, empty.CIAt, empty.Saul = StPass, "h", passReview("h")
	if Decide(State{HeadSHA: "h", CI: StPass, CIAt: "h"}) != ActWaitSaul || Decide(empty) != ActWaitSai {
		t.Fatal("H wait")
	}
	full := State{HeadSHA: "aaa", CI: StPass, CIAt: "aaa", Saul: passReview("aaa"), Sai: StPass, SaiSHA: "aaa"}
	if !Ready(full) || Decide(full) != ActReady {
		t.Fatal("H complete")
	}
}

func TestBMutation(t *testing.T) {
	root, h, s := t.TempDir(), "aaa", ensureWorkItem(impl("aaa"))
	write := hookIn{ToolName: "Write", ToolInput: map[string]any{"path": "ralph/ralph.go"}}
	if hookDecision(s, write, h, root)["permission"] != "allow" {
		t.Fatal("allow")
	}
	stale := s
	stale.Grant.HeadSHA = "old"
	for _, in := range []hookIn{
		write,
		{ToolName: "Write", ToolInput: map[string]any{"path": "secrets.env"}},
		{ToolName: "Write", ToolInput: map[string]any{"path": "ralph/../secrets.env"}},
		{ToolName: "", ToolInput: map[string]any{}},
		{ToolName: "Shell", ToolInput: map[string]any{"command": "rm -rf ralph"}},
		{ToolName: "Shell", ToolInput: map[string]any{"command": "sed -i s/a/b/ x"}},
		{ToolName: "InventedMutate", ToolInput: map[string]any{"path": "ralph/ralph.go"}},
	} {
		st := s
		if in.ToolName == "Write" && in.ToolInput["path"] == "ralph/ralph.go" {
			st = stale
		}
		if hookDecision(st, in, h, root)["permission"] != "deny" {
			t.Fatalf("want deny %+v", in)
		}
	}
	if hookDecision(State{}, write, h, root)["permission"] != "deny" {
		t.Fatal("no state")
	}
	t.Setenv("RALPH_WORK_ITEM", "fake")
	if hookDecision(s, write, h, root)["permission"] != "deny" {
		t.Fatal("spoof")
	}
	os.Unsetenv("RALPH_WORK_ITEM")
	if !shellOK("git status") || !shellOK("go test ./ralph") {
		t.Fatal("shell ok")
	}
	rel, err := repoRel("ralph/ralph.go", root)
	if err != nil || rel != "ralph/ralph.go" {
		t.Fatal(rel, err)
	}
	if _, err = repoRel("../outside", root); err == nil {
		t.Fatal("escape")
	}
	rel, _ = repoRel("ralph/../outside", root)
	if rel != "outside" {
		t.Fatal(rel)
	}
}

func TestBHookMain(t *testing.T) {
	run := func(body string) []byte {
		cmd := exec.Command("go", "run", ".", "hook")
		cmd.Dir, cmd.Stdin = ".", strings.NewReader(body)
		cmd.Env = append(os.Environ(), "RALPH_STATE=/no/ralph-state.json", "RALPH_LOCAL_ONLY=1")
		out, err := cmd.Output()
		if err != nil {
			t.Fatal(err, string(out))
		}
		return out
	}
	if !bytes.Contains(run(`{"tool_name":"Shell","tool_input":{"command":"git status"}}`), []byte(`"permission":"allow"`)) {
		t.Fatal("read")
	}
	if bytes.Contains(run(`{"tool_name":"Write","tool_input":{"path":"ralph/ralph.go"}}`), []byte(`"permission":"allow"`)) {
		t.Fatal("write")
	}
}

func TestCGoals(t *testing.T) {
	h := "aaa"
	s := impl(h)
	s = SetCI(s, StFail, h)
	s.Blockers = []Finding{{ID: "CIX", Source: "ci", Objective: "fix test X", Scope: []string{"ralph/"}, Blocking: true}}
	s = ensureWorkItem(Observe(h, s))
	if s.Grant.WorkItem != "CIX" {
		t.Fatal(s.Grant)
	}
	s.CI, s.CIAt = StPass, h
	s.Saul = Review{SHA: h, Trusted: true, Shards: []Shard{{ID: "ralph", Status: StFail}}, LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass,
		Findings: []Finding{{ID: "B1", Source: "saul", Objective: "fix B1", Scope: []string{"ralph/ralph.go"}, Blocking: true}}}
	s.Blockers = blocking(s.Saul.Findings)
	s = ensureWorkItem(Observe(h, s))
	if s.Grant.WorkItem != "B1" || s.NextAction != ActRemediate {
		t.Fatal(s.Grant, s.NextAction)
	}
	if Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}).Reason != "UNAUTHORIZED_WORK_ITEM" {
		t.Fatal("unrelated")
	}
	g := impl(h)
	g.CI, g.CIAt, g.Saul = StPass, h, passReview(h)
	g = ensureWorkItem(SetSai(g, StFail, h, []Finding{{ID: "G1", Source: "sai", Objective: "fix G1", Scope: []string{".cursor/"}, Blocking: true}}))
	if g.Grant.WorkItem != "G1" || !inScope(".cursor/hooks.json", g.Grant.Scope) {
		t.Fatal(g.Grant)
	}
}

func TestDExactSHA(t *testing.T) {
	s := impl("aaa")
	s.CI, s.CIAt, s.Saul, s.Sai, s.SaiSHA = StPass, "aaa", passReview("aaa"), StPass, "aaa"
	s2 := Observe("bbb", s)
	if s2.Saul.Trusted || s2.CI != StStale || s2.Sai != StStale || s2.Grant.WorkItem != "" {
		t.Fatal(s2)
	}
	if Authorize(s2, AuthReq{HeadSHA: "bbb", Path: "ralph/ralph.go"}).Decision != DecisionDeny {
		t.Fatal("auth B")
	}
	headOverride = "aaa"
	t.Cleanup(func() { headOverride = "" })
	got, err := CompleteWork(impl("aaa"), WorkerResult{WorkItem: "w1", BaseSHA: "aaa", ResultSHA: "bbb"})
	if err != nil || got.HeadSHA != "aaa" {
		t.Fatal(got, err)
	}
	if _, err = CompleteWork(impl("aaa"), WorkerResult{WorkItem: "w1", BaseSHA: "aaa", SetsReady: true}); err == nil {
		t.Fatal("ready")
	}
}

func TestERecovery(t *testing.T) {
	h, orig := "aaa", ensureWorkItem(impl("aaa"))
	sum, _ := json.Marshal(orig)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			_ = json.NewEncoder(w).Encode(map[string]any{"check_runs": []map[string]any{{"name": checkRalph, "head_sha": h, "output": map[string]string{"summary": string(sum)}}}})
			return
		}
		w.WriteHeader(201)
	}))
	t.Cleanup(srv.Close)
	ghAPI = srv.URL
	t.Cleanup(func() { ghAPI = "https://api.github.com" })
	t.Setenv("GITHUB_TOKEN", "t")
	t.Setenv("GITHUB_REPOSITORY", "Dezocode/Sai")
	os.Unsetenv("RALPH_LOCAL_ONLY")
	t.Setenv("RALPH_STATE", filepath.Join(t.TempDir(), "missing.json"))
	headOverride = h
	t.Cleanup(func() { headOverride = "" })
	got, err := recoverState(h)
	if err != nil || got.Grant.WorkItem != orig.Grant.WorkItem || got.NextAction != orig.NextAction {
		t.Fatal(got, err)
	}
}

func TestFGSaulSai(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	s := impl("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	good := passReview("aaa")
	good.Trusted = false
	s = IntegrateSaul(s, SignEvidence(priv, "aaa", good), pub)
	if !saulConverged(s) || saulConverged(Observe("bbb", s)) {
		t.Fatal("sha bind")
	}
	if IntegrateSaul(impl("bbb"), SignEvidence(priv, "aaa", passReview("aaa")), pub).Saul.Trusted {
		t.Fatal("wrong sha")
	}
	if saulConverged(IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", Review{SHA: "aaa", Shards: []Shard{{ID: "ralph", Status: StPass}}}), pub)) {
		t.Fatal("arch")
	}
	_, priv2, _ := ed25519.GenerateKey(nil)
	if IntegrateSaul(impl("aaa"), SignEvidence(priv2, "aaa", passReview("aaa")), pub).Saul.Trusted {
		t.Fatal("key")
	}
	inc := passReview("aaa")
	inc.Shards = nil
	if saulConverged(IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", inc), pub)) {
		t.Fatal("shards")
	}
	find := passReview("aaa")
	find.Findings = []Finding{{ID: "B", Blocking: true, Objective: "x", Scope: []string{"ralph/"}}}
	s4 := IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", find), pub)
	s4.CI, s4.CIAt = StPass, "aaa"
	if saulConverged(s4) || Decide(s4) != ActRemediate {
		t.Fatal("blocker")
	}
	if IntegrateSaul(impl("aaa"), Evidence{SHA: "aaa", Review: passReview("aaa"), Sig: "00", CodexInvoked: true}, pub).Saul.Trusted {
		t.Fatal("sig")
	}
	if IntegrateSaul(impl("aaa"), Evidence{SHA: "aaa", Review: good, CodexInvoked: true, Synthetic: true, Sig: SignEvidence(priv, "aaa", good).Sig}, pub).Saul.Trusted {
		t.Fatal("syn")
	}
	noc := SignEvidence(priv, "aaa", good)
	noc.CodexInvoked = false
	if IntegrateSaul(impl("aaa"), noc, pub).Saul.Trusted {
		t.Fatal("codex")
	}
	s = impl("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	if SetSai(s, StPass, "aaa", nil).Sai == StPass {
		t.Fatal("order")
	}
	s.Saul = passReview("aaa")
	s = SetSai(s, StPass, "aaa", nil)
	s = ensureWorkItem(SetSai(s, StFail, "aaa", []Finding{{ID: "G1", Source: "sai", Objective: "gov", Scope: []string{".github/"}, Blocking: true}}))
	if s.Grant.Scope[0] != ".github/" {
		t.Fatal(s.Grant)
	}
	s2 := Observe("bbb", s)
	if saulConverged(s2) || s2.Sai != StStale || Decide(s2) == ActWaitSai {
		t.Fatal("restale")
	}
}
