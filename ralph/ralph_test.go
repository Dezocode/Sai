package main

import (
	"bytes"
	"crypto/ed25519"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func base(head string) State {
	return State{
		ProgramID: "pr68-ralph", PR: 68, HeadSHA: head,
		ExpectedUnits: []string{"ralph"}, RequirementsOpen: 1,
		Workers: []WorkItem{{ID: "w1", Objective: "kernel", BaseSHA: head, Scope: []string{"ralph/"}, Status: "OPEN"}},
		CI: StMissing, Sai: StMissing,
	}
}

func passReview(head string) Review {
	return Review{
		SHA: head, Trusted: true,
		Shards: []Shard{{ID: "ralph", Status: StPass}},
		LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass,
	}
}

func TestAuthorizeAllowDeny(t *testing.T) {
	h := "aaa"
	s := base(h)
	s.CI, s.CIAt = StPass, h
	s.Saul = passReview(h)
	s.Sai, s.SaiSHA = StPass, h
	d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"})
	if d.Decision != DecisionAllow || d.NextAction != string(ActImplement) {
		t.Fatalf("allow: %+v", d)
	}
	stale := s
	stale.Workers = []WorkItem{{ID: "w1", Objective: "kernel", BaseSHA: "old", Scope: []string{"ralph/"}, Status: "OPEN"}}
	if d := Authorize(stale, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}); d.Decision != DecisionDeny || d.Reason != "STALE_SHA" {
		t.Fatalf("stale: %+v", d)
	}
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "nope"}); d.Reason != "UNAUTHORIZED_WORK_ITEM" {
		t.Fatalf("unauth: %+v", d)
	}
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "scripts/x", WorkItem: "w1"}); d.Reason != "OUT_OF_SCOPE" {
		t.Fatalf("scope: %+v", d)
	}
}

func TestPhaseRedirects(t *testing.T) {
	h := "aaa"
	s := base(h)
	s.CI, s.CIAt = StPending, h
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}); d.Reason != "WAIT_CI_REQUIRED" {
		t.Fatalf("ci: %+v", d)
	}
	s.CI, s.CIAt = StPass, h
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}); d.Reason != "WAIT_SAUL_REQUIRED" {
		t.Fatalf("saul: %+v", d)
	}
	s.Saul = passReview(h)
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}); d.Reason != "WAIT_SAI_REQUIRED" {
		t.Fatalf("sai: %+v", d)
	}
}

func TestHeadChangeInvalidatesAuth(t *testing.T) {
	s := base("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	s.Saul = passReview("aaa")
	s.Sai, s.SaiSHA = StPass, "aaa"
	d := Authorize(s, AuthReq{HeadSHA: "aaa", Path: "ralph/ralph.go", WorkItem: "w1"})
	if d.Decision != DecisionAllow {
		t.Fatal(d)
	}
	s2 := Observe("bbb", s)
	if s2.Saul.Trusted || s2.CI != StStale || s2.Sai != StStale {
		t.Fatalf("stale fields: %+v", s2)
	}
	d2 := Authorize(s2, AuthReq{HeadSHA: "bbb", Path: "ralph/ralph.go", WorkItem: "w1"})
	if d2.Decision != DecisionDeny {
		t.Fatalf("auth after head: %+v", d2)
	}
}

func TestBlockersSteerObjective(t *testing.T) {
	h := "aaa"
	s := base(h)
	s.CI, s.CIAt = StPass, h
	s.Saul = Review{SHA: h, Trusted: true, Shards: []Shard{{ID: "ralph", Status: StFail}}, LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass,
		Findings: []Finding{{ID: "B1", Source: "saul", Objective: "fix B1", Scope: []string{"ralph/"}, Blocking: true}}}
	s.Blockers = blocking(s.Saul.Findings)
	s.Workers = []WorkItem{{ID: "B1", Objective: "fix B1", BaseSHA: h, Scope: []string{"ralph/"}, Status: "OPEN"}}
	d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "B1"})
	if d.Decision != DecisionAllow || d.Objective != "fix B1" || d.NextAction != string(ActRemediate) {
		t.Fatalf("%+v", d)
	}
	if d := Authorize(s, AuthReq{HeadSHA: h, Path: "ralph/ralph.go", WorkItem: "w1"}); d.Reason != "UNAUTHORIZED_WORK_ITEM" {
		t.Fatalf("unrelated: %+v", d)
	}
}

func TestReadyPredicate(t *testing.T) {
	h := "aaa"
	s := base(h)
	s.RequirementsOpen = 0
	s.Workers = nil
	if Ready(s) || Decide(s) == ActReady {
		t.Fatal("empty work is not ready")
	}
	s.CI, s.CIAt = StPass, h
	if Decide(s) != ActWaitSaul {
		t.Fatalf("wait saul: %s", Decide(s))
	}
	s.Saul = passReview(h)
	if Decide(s) != ActWaitSai {
		t.Fatalf("wait sai: %s", Decide(s))
	}
	s.Sai, s.SaiSHA = StPass, h
	if !Ready(s) || Decide(s) != ActReady {
		t.Fatalf("want ready: %+v %s", s, Decide(s))
	}
	s.Blockers = []Finding{{ID: "x", Blocking: true}}
	if Ready(s) {
		t.Fatal("blocker")
	}
	s.Blockers = nil
	s.CI = StFail
	if Ready(s) {
		t.Fatal("ci fail")
	}
	s.CI = StPass
	s.Saul.Trusted = false
	if Ready(s) {
		t.Fatal("saul untrusted")
	}
}

func TestSaulExactSHAAndCoverage(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	s := base("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	good := passReview("aaa")
	good.Trusted = false
	e := SignEvidence(priv, "aaa", good)
	s = IntegrateSaul(s, e, pub)
	if !saulConverged(s) {
		t.Fatal("valid should converge")
	}
	sB := Observe("bbb", s)
	if saulConverged(sB) {
		t.Fatal("A must not authorize B")
	}
	onB := IntegrateSaul(base("bbb"), SignEvidence(priv, "aaa", passReview("aaa")), pub)
	onB.ExpectedUnits = []string{"ralph"}
	if saulConverged(onB) || onB.Saul.Trusted {
		t.Fatal("review A cannot become current on B")
	}
	s2 := IntegrateSaul(base("aaa"), SignEvidence(priv, "aaa", Review{SHA: "aaa", Shards: []Shard{{ID: "ralph", Status: StPass}}}), pub)
	s2.ExpectedUnits = []string{"ralph"}
	if saulConverged(s2) {
		t.Fatal("missing arch")
	}
	_, priv2, _ := ed25519.GenerateKey(nil)
	if IntegrateSaul(base("aaa"), SignEvidence(priv2, "aaa", passReview("aaa")), pub).Saul.Trusted {
		t.Fatal("wrong key")
	}
	incomplete := passReview("aaa")
	incomplete.Shards = nil
	s3 := IntegrateSaul(base("aaa"), SignEvidence(priv, "aaa", incomplete), pub)
	s3.ExpectedUnits = []string{"ralph"}
	if saulConverged(s3) {
		t.Fatal("incomplete shards")
	}
	find := passReview("aaa")
	find.Findings = []Finding{{ID: "B", Blocking: true, Objective: "x", Scope: []string{"ralph/"}}}
	s4 := IntegrateSaul(base("aaa"), SignEvidence(priv, "aaa", find), pub)
	s4.CI, s4.CIAt = StPass, "aaa"
	if saulConverged(s4) || Decide(s4) != ActRemediate {
		t.Fatalf("finding: conv=%v act=%s", saulConverged(s4), Decide(s4))
	}
	s5 := IntegrateSaul(base("aaa"), Evidence{SHA: "aaa", Review: passReview("aaa"), Sig: "00"}, pub)
	if s5.Saul.Trusted {
		t.Fatal("untrusted")
	}
}

func TestSaiOrdering(t *testing.T) {
	s := base("aaa")
	s.CI, s.CIAt = StPass, "aaa"
	s = SetSai(s, StPass, "aaa")
	if s.Sai == StPass {
		t.Fatal("sai pass before saul")
	}
	s.Saul = passReview("aaa")
	s = SetSai(s, StPass, "aaa")
	if s.Sai != StPass {
		t.Fatal("sai after saul")
	}
	s = SetSai(s, StFail, "aaa")
	if Decide(s) != ActRemediate || findItem(s, "SAI") == nil {
		t.Fatal("sai fail remediates")
	}
}

func TestRecoveryAndWorker(t *testing.T) {
	h := "aaa"
	s := Observe(h, base(h))
	if Decide(s) != ActImplement {
		t.Fatal(Decide(s))
	}
	s = SetCI(s, StPending, h)
	if Decide(s) != ActWaitCI {
		t.Fatal(Decide(s))
	}
	_, err := CompleteWork(s, WorkerResult{WorkItem: "w1", BaseSHA: h, SetsReady: true})
	if err == nil {
		t.Fatal("worker ready")
	}
	s, err = CompleteWork(s, WorkerResult{WorkItem: "w1", BaseSHA: h, Status: "COMPLETE"})
	if err != nil {
		t.Fatal(err)
	}
	if Ready(s) {
		t.Fatal("complete work != program complete")
	}
	s = SetCI(s, StPass, "zzz")
	if s.CI != StStale {
		t.Fatal("ci other sha")
	}
}

func TestHookProtocol(t *testing.T) {
	dir := t.TempDir()
	h := "aaa"
	s := base(h)
	s.CI, s.CIAt = StPass, h
	s.Saul = passReview(h)
	s.Sai, s.SaiSHA = StPass, h
	p := filepath.Join(dir, "state.json")
	if err := saveState(p, s); err != nil {
		t.Fatal(err)
	}
	os.Setenv("RALPH_STATE", p)
	os.Setenv("RALPH_WORK_ITEM", "w1")
	t.Cleanup(func() { os.Unsetenv("RALPH_STATE"); os.Unsetenv("RALPH_WORK_ITEM") })
	loaded, _ := loadState(p)
	in := hookIn{ToolName: "Write", ToolInput: map[string]any{"path": "ralph/ralph.go"}}
	out := hookDecision(loaded, in)
	if out["permission"] != "allow" {
		t.Fatalf("%v", out)
	}
	in.ToolInput["path"] = "secrets.env"
	out = hookDecision(loaded, in)
	if out["permission"] != "deny" {
		t.Fatalf("deny scope %v", out)
	}
	in = hookIn{ToolName: "Shell", ToolInput: map[string]any{"command": "go test ./ralph"}}
	if hookDecision(loaded, in)["permission"] != "allow" {
		t.Fatal("non-mut shell")
	}
	raw, _ := json.Marshal(hookIn{ToolName: "StrReplace", ToolInput: map[string]any{"path": "ralph/ralph.go"}})
	_ = bytes.NewReader(raw)
}

func TestWaitingNonterminal(t *testing.T) {
	s := State{HeadSHA: "h", ExpectedUnits: []string{"ralph"}}
	if Ready(s) || Decide(s) == ActReady {
		t.Fatal("waiting is not ready")
	}
	s.Workers = nil
	s.RequirementsOpen = 0
	if Ready(s) {
		t.Fatal("empty work is not ready")
	}
	s.CI, s.CIAt, s.Saul, s.Sai, s.SaiSHA = StPass, "h", passReview("h"), StPass, "h"
	if !Ready(s) {
		t.Fatal("only full current state is ready")
	}
}
