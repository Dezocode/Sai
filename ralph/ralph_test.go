package main

import (
	"crypto/ed25519"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
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
func ghSrv(t *testing.T, checks any) {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			w.WriteHeader(201)
			return
		}
		if strings.Contains(r.URL.Path, "/reviews") {
			_ = json.NewEncoder(w).Encode([]any{})
			return
		}
		_ = json.NewEncoder(w).Encode(checks)
	}))
	t.Cleanup(srv.Close)
	ghAPI = srv.URL
	t.Cleanup(func() { ghAPI = "https://api.github.com" })
}
func ciSaul(h, summary, text string, id int64) map[string]any {
	return map[string]any{"check_runs": []map[string]any{
		{"name": "icm-enforcement", "head_sha": h, "status": "completed", "conclusion": "success"},
		{"name": "PR line budget", "head_sha": h, "status": "completed", "conclusion": "success"},
		{"name": "Anti-regression", "head_sha": h, "status": "completed", "conclusion": "success"},
		{"name": checkSaul, "id": id, "head_sha": h, "status": "completed", "conclusion": "action_required",
			"output": map[string]any{"summary": summary, "text": text}},
	}}
}

func TestAHLoopAndTerminal(t *testing.T) {
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	headOverride = "aaa"
	t.Cleanup(func() { headOverride = "" })
	t.Setenv("RALPH_STATE", filepath.Join(t.TempDir(), "s.json"))
	s, err := step(impl("aaa"))
	if err != nil || Ready(s) || s.NextAction != ActImplement || s.Grant.WorkItem == "" || s.Dispatch.Kind != "cursor_primary" {
		t.Fatalf("A continue %+v %v", s, err)
	}
	s = SetCI(s, StPending, "aaa")
	s, err = step(s)
	if err != nil || Ready(s) || s.NextAction != ActWaitCI {
		t.Fatalf("A wait %s", s.NextAction)
	}
	empty := State{HeadSHA: "h", PR: 68, CI: StPass, CIAt: "h", Saul: passReview("h")}
	if Decide(State{HeadSHA: "h", CI: StPass, CIAt: "h"}) != ActWaitSaul || Decide(empty) != ActWaitSai {
		t.Fatal("H wait")
	}
	full := State{HeadSHA: "aaa", CI: StPass, CIAt: "aaa", Saul: passReview("aaa"), Sai: StPass, SaiSHA: "aaa"}
	if !Ready(full) || Decide(full) != ActReady {
		t.Fatal("H complete")
	}
	s2 := Observe("bbb", full)
	if s2.Saul.Trusted || s2.CI != StStale || s2.Sai != StStale || s2.Grant.WorkItem != "" || Authorize(s2, AuthReq{HeadSHA: "bbb", Path: "ralph/ralph.go"}).Decision != DecisionDeny {
		t.Fatal(s2)
	}
	got, err := CompleteWork(impl("aaa"), WorkerResult{WorkItem: "w1", BaseSHA: "aaa", ResultSHA: "bbb"})
	if err != nil || got.HeadSHA != "aaa" {
		t.Fatal(got, err)
	}
	if _, err = CompleteWork(impl("aaa"), WorkerResult{WorkItem: "w1", BaseSHA: "aaa", SetsReady: true}); err == nil {
		t.Fatal("ready")
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
	for _, cmd := range []string{"rm -rf ralph", "sed -i s/a/b/ x", "gofmt -w ralph/ralph.go", "go fmt -w ralph/ralph.go", "git checkout HEAD -- ralph/ralph.go", "cat <<EOF\nX\nEOF", "git status; rm -rf /", "git status && git push", "git status | tee x"} {
		if hookDecision(s, hookIn{ToolName: "Shell", ToolInput: map[string]any{"command": cmd}}, h, root)["permission"] != "deny" {
			t.Fatalf("shell %s", cmd)
		}
	}
	for _, in := range []hookIn{write, {ToolName: "Write", ToolInput: map[string]any{"path": "secrets.env"}}, {ToolName: "Write", ToolInput: map[string]any{"path": "ralph/../secrets.env"}}, {ToolName: "", ToolInput: map[string]any{}}, {ToolName: "InventedMutate", ToolInput: map[string]any{"path": "ralph/ralph.go"}}} {
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
	if !shellOK("git status") || !shellOK("go test ./ralph") || shellOK("gofmt -w x") || shellOK("unknowncmd") {
		t.Fatal("shell ok")
	}
	rel, err := repoRel("ralph/ralph.go", root)
	if err != nil || rel != "ralph/ralph.go" {
		t.Fatal(rel, err)
	}
	if _, err = repoRel("../outside", root); err == nil {
		t.Fatal("escape")
	}
	p := filepath.Join(t.TempDir(), "s.json")
	var wg sync.WaitGroup
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			st := impl("aaa")
			st.Grant.WorkItem = string(rune('a' + i))
			if err := saveState(p, st); err != nil {
				t.Error(err)
			}
		}(i)
	}
	wg.Wait()
	b, err := os.ReadFile(p)
	if err != nil || json.Unmarshal(b, new(State)) != nil {
		t.Fatal("torn", err, string(b))
	}
}

func TestCGoals(t *testing.T) {
	h := "aaa"
	pub, priv, _ := ed25519.GenerateKey(nil)
	s := SetCI(impl(h), StFail, h)
	s.Blockers = []Finding{{ID: "CIX", Source: "ci", Objective: "fix test X", Scope: []string{"ralph/"}, Blocking: true}}
	s = ensureWorkItem(Observe(h, s))
	if s.Grant.WorkItem != "CIX" || s.Dispatch.Kind != "cursor_primary" {
		t.Fatal(s.Grant)
	}
	find := passReview(h)
	find.Findings = []Finding{{ID: "B1", Source: "saul", Objective: "fix B1", Scope: []string{"ralph/ralph.go"}, Blocking: true}}
	s.CI, s.CIAt = StPass, h
	s = ensureWorkItem(Observe(h, IntegrateSaul(s, SignEvidence(priv, h, find), pub, 0)))
	ids := map[string]bool{}
	for _, f := range s.Blockers {
		ids[f.ID] = true
	}
	if !ids["CIX"] || !ids["B1"] || s.Grant.WorkItem != "CIX" || s.NextAction != ActRemediate {
		t.Fatal(s.Blockers, s.Grant, s.NextAction)
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

func TestFGSaulSai(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	good := passReview("aaa")
	s := IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", good), pub, 0)
	s.CI, s.CIAt = StPass, "aaa"
	if !saulConverged(s) || saulConverged(Observe("bbb", s)) {
		t.Fatal("sha bind")
	}
	_, priv2, _ := ed25519.GenerateKey(nil)
	inc, find, noc := passReview("aaa"), passReview("aaa"), SignEvidence(priv, "aaa", good)
	inc.Shards, find.Findings, noc.CodexInvoked = nil, []Finding{{ID: "B", Blocking: true, Objective: "x", Scope: []string{"ralph/"}}}, false
	s4 := IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", find), pub, 0)
	s4.CI, s4.CIAt = StPass, "aaa"
	if IntegrateSaul(impl("bbb"), SignEvidence(priv, "aaa", good), pub, 0).Saul.Trusted ||
		saulConverged(IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", Review{SHA: "aaa", Shards: []Shard{{ID: "ralph", Status: StPass}}}), pub, 0)) ||
		IntegrateSaul(impl("aaa"), SignEvidence(priv2, "aaa", good), pub, 0).Saul.Trusted ||
		saulConverged(IntegrateSaul(impl("aaa"), SignEvidence(priv, "aaa", inc), pub, 0)) ||
		saulConverged(s4) || Decide(s4) != ActRemediate ||
		IntegrateSaul(impl("aaa"), Evidence{HeadSHA: "aaa", CodexInvoked: true, Sig: "00"}, pub, 0).Saul.Trusted ||
		IntegrateSaul(impl("aaa"), Evidence{HeadSHA: "aaa", CodexInvoked: true, Synthetic: true, Sig: SignEvidence(priv, "aaa", good).Sig}, pub, 0).Saul.Trusted ||
		IntegrateSaul(impl("aaa"), noc, pub, 0).Saul.Trusted {
		t.Fatal("untrusted")
	}
	s = impl("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	if SetSai(s, StPass, "aaa", nil).Sai == StPass {
		t.Fatal("order")
	}
	s.Saul = passReview("aaa")
	s = ensureWorkItem(SetSai(SetSai(s, StPass, "aaa", nil), StFail, "aaa", []Finding{{ID: "G1", Source: "sai", Objective: "gov", Scope: []string{".github/"}, Blocking: true}}))
	if s.Grant.Scope[0] != ".github/" {
		t.Fatal(s.Grant)
	}
	s2 := Observe("bbb", s)
	if saulConverged(s2) || s2.Sai != StStale || Decide(s2) == ActWaitSai {
		t.Fatal("restale")
	}
}

func TestEvidenceTextNotSummary(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	t.Setenv("SAI_SAUL_ATTEST_PUB", hex.EncodeToString(pub))
	t.Setenv("GITHUB_TOKEN", "t")
	t.Setenv("GITHUB_REPOSITORY", "Dezocode/Sai")
	os.Unsetenv("RALPH_LOCAL_ONLY")
	h := "aaa"
	headOverride = h
	t.Cleanup(func() { headOverride = "" })
	orig := ensureWorkItem(impl(h))
	sum, _ := json.Marshal(orig)
	t.Setenv("RALPH_STATE", filepath.Join(t.TempDir(), "missing.json"))
	ghSrv(t, map[string]any{"check_runs": []map[string]any{{"name": checkRalph, "head_sha": h, "output": map[string]string{"summary": string(sum)}}}})
	got, err := recoverState(h)
	if err != nil || got.Grant.WorkItem != orig.Grant.WorkItem || got.NextAction != orig.NextAction {
		t.Fatal("recover", got, err)
	}
	kv := "LOCAL_ARCH=fail\nexact head SHA=" + h
	ghSrv(t, ciSaul(h, kv, "", 1))
	got, err = integrateWorld(impl(h))
	if err != nil || got.Saul.Trusted || got.NextAction != ActWaitSaul || len(got.Blockers) == 0 || got.Blockers[0].ID != "SAUL_EVIDENCE_TEXT" {
		t.Fatal("null text", got.NextAction, got.Blockers, err)
	}
	text, _ := json.Marshal(SignEvidence(priv, h, passReview(h)))
	ghSrv(t, ciSaul(h, kv, string(text), 1))
	got, err = integrateWorld(impl(h))
	if err != nil || !got.Saul.Trusted || !saulConverged(got) {
		t.Fatal("text ingest", got.Saul, err)
	}
}
