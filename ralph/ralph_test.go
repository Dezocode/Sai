package main

import (
	"crypto/ed25519"
	"encoding/hex"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"syscall"
	"testing"
	"time"
)

func tw(head string, cs []ghComment, ks []ghCheck, perms map[string]string) World {
	if perms == nil {
		perms = map[string]string{"own": "admin"}
	}
	return World{Repo: "o/r", PR: 1, Head: head, Base: "base", Comments: cs, Checks: ks, Perms: perms}
}
func std(id, src string) string {
	e := Envelope{SchemaVersion: schemaBs, Repository: "o/r", PR: 1, Blockers: []Blocker{{SchemaVersion: schemaB, ID: id, SourceID: src, Status: "OPEN", Blocking: true, Severity: "P0", ResolutionAuthority: "saul", Applicability: Appl{Mode: "sticky"}, Objective: "x", Scope: []string{"ralph/"}}}}
	b, _ := json.Marshal(e)
	return marker + "\n```json\n" + string(b) + "\n```"
}
func signV2(priv ed25519.PrivateKey, e Evidence) Evidence {
	if e.Blockers == nil {
		e.Blockers = []Blocker{}
	}
	e.BlockerSetHash = hashBlockers(e.Blockers)
	msg, _ := signMsg(e)
	e.Sig = hex.EncodeToString(ed25519.Sign(priv, msg))
	return e
}
func evOK(h string, bl []Blocker) Evidence {
	return Evidence{SchemaVersion: schemaE, Repository: "o/r", PR: 1, BaseSHA: "base", HeadSHA: h, ManifestHash: "m", ReviewerIdentity: "hostinger-saul-cto", KeyID: "k", CheckRunID: 1, CodexInvoked: true, RuntimeAttestation: "a", Shards: []Shard{{ID: "ralph", Status: StPass}}, LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass, Blockers: bl, Tests: []string{"t"}, FinalDisposition: "action_required"}
}
func ids(s State) map[string]Blocker {
	m := map[string]Blocker{}
	for _, b := range s.Blockers {
		m[b.ID] = b
	}
	return m
}
func TestCommentsChecksSaulSched(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	t.Setenv("SAI_SAUL_ATTEST_PUB", hex.EncodeToString(pub))
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	body := std("B-RALPH-CANONICAL-BLOCKER-LOOP-001", "github-comment:9")
	w := tw("h1", []ghComment{
		{ID: "9", Login: "own", Assoc: "OWNER", Body: body, HTMLURL: "http://c/9"},
		{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"},
		{ID: "2", Login: "r", Assoc: "NONE", Body: body},
		{ID: "3", Login: "w", Assoc: "COLLABORATOR", Body: "**BLOCKING x"},
		{ID: "4", Login: "own", Assoc: "OWNER", Body: "## BLOCKING not legacy"},
	}, nil, map[string]string{"own": "admin", "r": "none", "w": "write"})
	s := applyWorld(w, State{})
	got := ids(s)
	if got["B-RALPH-CANONICAL-BLOCKER-LOOP-001"].ID == "" || got["COMMENT-1"].ID == "" || got["COMMENT-2"].ID != "" || got["COMMENT-3"].ID != "" || got["COMMENT-4"].ID != "" {
		t.Fatalf("comments %+v", s.Blockers)
	}
	if s.NextAction != ActImplement || s.Dispatch.Kind != "cursor_primary" || s.Dispatch.WorkItem.ID != "WI-B-RALPH-CANONICAL-BLOCKER-LOOP-001" {
		t.Fatalf("sched %s %s", s.NextAction, s.Dispatch.WorkItem.ID)
	}
	fake := body
	w2 := tw("h1", []ghComment{{ID: "8", Login: "r", Assoc: "NONE", Body: strings.ReplaceAll(fake, `"source_actor":`, `"source_actor":"Dezocode", "x":`)}}, nil, map[string]string{"r": "none"})
	if len(ingestTrustedComments(w2)) != 0 {
		t.Fatal("spoof")
	}
	badEnv := Envelope{SchemaVersion: schemaBs, Repository: "a/b", PR: 1, Blockers: []Blocker{{SchemaVersion: schemaB, ID: "Z", SourceID: "github-comment:9", Status: "OPEN", Blocking: true, Objective: "z"}}}
	bb, _ := json.Marshal(badEnv)
	w3 := tw("h1", []ghComment{{ID: "9", Login: "own", Assoc: "OWNER", Body: marker + "\n```json\n" + string(bb) + "\n```"}}, nil, nil)
	if len(ingestTrustedComments(w3)) != 0 {
		t.Fatal("repo")
	}
	res := std("B-RALPH-CANONICAL-BLOCKER-LOOP-001", "github-comment:9")
	res = strings.Replace(res, `"status": "OPEN"`, `"status": "RESOLVED"`, 1)
	w4 := tw("h2", []ghComment{{ID: "9", Login: "own", Assoc: "OWNER", Body: res, HTMLURL: "http://c/9"}, {ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"}}, nil, nil)
	s2 := applyWorld(w4, s)
	if ids(s2)["B-RALPH-CANONICAL-BLOCKER-LOOP-001"].Status == "RESOLVED" || ids(s2)["COMMENT-1"].ID == "" {
		t.Fatal("sticky/unauth resolve")
	}
	fail := ghCheck{Name: "icm-enforcement", HeadSHA: "h1", Status: "completed", Conclusion: "failure", App: struct {
		ID   int64  `json:"id"`
		Slug string `json:"slug"`
	}{ID: 15368, Slug: "github-actions"}}
	sf := applyWorld(tw("h1", nil, []ghCheck{fail}, nil), State{})
	if sf.NextAction != ActRemediate || len(sf.Blockers) == 0 || !sf.Blockers[0].Actionable {
		t.Fatal("ci blocker", sf.Blockers, sf.NextAction)
	}
	pass := fail
	pass.Conclusion = "success"
	sp := applyWorld(tw("h1", nil, []ghCheck{pass, {Name: checkSaul, ID: 1, HeadSHA: "h1", Status: "completed", Conclusion: "action_required"}}, nil), State{Repository: "o/r", PR: 1, BaseSHA: "base"})
	if ids(sp)["SAUL_PROTOCOL_V2"].ID == "" || sp.Saul.Trusted || sp.NextAction == ActWaitSaul && ids(sp)["SAUL_PROTOCOL_V2"].Actionable {
		t.Fatal("protocol", sp.Blockers, sp.NextAction)
	}
	text, _ := json.Marshal(signV2(priv, evOK("h1", []Blocker{{SchemaVersion: schemaB, ID: "B1", SourceKind: "saul", Status: "OPEN", Blocking: true, Severity: "P1", Objective: "b1", Scope: []string{"ralph/"}, ResolutionAuthority: "saul"}})))
	okc := []ghCheck{{Name: "icm-enforcement", HeadSHA: "h1", Status: "completed", Conclusion: "success", App: struct {
		ID   int64  `json:"id"`
		Slug string `json:"slug"`
	}{Slug: "github-actions"}}, {Name: checkSaul, ID: 1, HeadSHA: "h1", Status: "completed", Output: struct {
		Summary string `json:"summary"`
		Text    string `json:"text"`
	}{Text: string(text)}}}
	ss := applyWorld(tw("h1", []ghComment{{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"}}, okc, nil), State{Repository: "o/r", PR: 1, BaseSHA: "base"})
	m := ids(ss)
	if !ss.Saul.Trusted || m["B1"].ID == "" || m["COMMENT-1"].ID == "" {
		t.Fatal("union", ss.Blockers, ss.Saul)
	}
	text2, _ := json.Marshal(signV2(priv, evOK("h1", []Blocker{{SchemaVersion: schemaB, ID: "B1", SourceKind: "saul", Status: "RESOLVED", ResolutionAuthority: "saul"}})))
	okc[1].Output.Text = string(text2)
	sr := applyWorld(tw("h1", []ghComment{{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"}}, okc, nil), ss)
	if ids(sr)["B1"].Status != "RESOLVED" || ids(sr)["COMMENT-1"].Status != "OPEN" {
		t.Fatal("saul resolve omit", sr.Blockers)
	}
	bad := evOK("h1", nil)
	bad.CodexInvoked = false
	if verifySaul(signV2(priv, bad), State{Repository: "o/r", PR: 1, BaseSHA: "base", HeadSHA: "h1"}, pub, 1) {
		t.Fatal("codex")
	}
	dep := applyWorld(tw("h1", nil, nil, nil), State{Blockers: []Blocker{
		{ID: "P0w", SchemaVersion: schemaB, Status: "OPEN", Blocking: true, Severity: "P0", DependsOn: []string{"X"}, Scope: []string{"ralph/"}, Objective: "a"},
		{ID: "P1r", SchemaVersion: schemaB, Status: "OPEN", Blocking: true, Severity: "P1", Scope: []string{"ralph/"}, Objective: "b"},
	}})
	if dep.Grant.WorkItem != "WI-P1r" {
		t.Fatal("deps", dep.Grant)
	}
	s.NextAction, s.CI, s.CIAt = ActImplement, StPending, "h1"
	s = scheduleState(s)
	if s.NextAction == ActWaitSaul || s.NextAction == ActWaitCI {
		t.Fatal("wait with work", s.NextAction)
	}
}
func TestMutationLockRun(t *testing.T) {
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	s := applyWorld(tw("aaa", []ghComment{{ID: "9", Login: "own", Assoc: "OWNER", Body: std("B-X", "github-comment:9")}}, nil, nil), State{})
	root := t.TempDir()
	write := hookIn{ToolName: "Write", ToolInput: map[string]any{"path": "ralph/ralph.go"}}
	if hookDecision(s, write, "aaa", root)["permission"] != "allow" {
		t.Fatal("allow")
	}
	for _, cmd := range []string{"rm -rf ralph", "mv a b", "cp a b", "sed -i s/a/b/ x", "perl -pi -e s/a/b/ x", "git apply x", "git checkout HEAD -- x", "git reset --hard", "python3 -c open('x','w')", "node -e fs.write", "gofmt -w x", "go fmt -w x", "touch x", "true > x", "git status | tee x", "cat <<EOF\nX\nEOF", "git status && rm x", "git status; rm x", "$(rm x)"} {
		if hookDecision(s, hookIn{ToolName: "Shell", ToolInput: map[string]any{"command": cmd}}, "aaa", root)["permission"] != "deny" {
			t.Fatalf("shell %s", cmd)
		}
	}
	if hookDecision(s, hookIn{ToolName: "InventedMutate", ToolInput: map[string]any{"path": "ralph/ralph.go"}}, "aaa", root)["permission"] != "deny" {
		t.Fatal("unknown")
	}
	t.Setenv("RALPH_WORK_ITEM", "fake")
	if hookDecision(s, write, "aaa", root)["permission"] != "deny" {
		t.Fatal("spoof")
	}
	os.Unsetenv("RALPH_WORK_ITEM")
	if _, err := CompleteWork(s, WorkerResult{WorkItem: s.Grant.WorkItem, BaseSHA: "aaa", Status: "RESOLVED"}); err == nil {
		t.Fatal("worker resolve")
	}
	p := filepath.Join(t.TempDir(), "s.json")
	var wg sync.WaitGroup
	for i := 0; i < 6; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = saveState(p, s)
		}()
	}
	wg.Wait()
	if _, err := loadState(p); err != nil {
		t.Fatal(err)
	}
}
func TestHelperRalphRun(t *testing.T) {
	if os.Getenv("RALPH_BE_RUN") != "1" {
		return
	}
	os.Exit(runMain(false))
}
func TestRunLifetime(t *testing.T) {
	dir := t.TempDir()
	wp, sp := dir+"/w.json", dir+"/s.json"
	w := tw("h1", []ghComment{{ID: "9", Login: "own", Assoc: "OWNER", Body: std("B-X", "github-comment:9")}}, []ghCheck{{Name: "icm-enforcement", HeadSHA: "h1", Status: "in_progress", App: struct {
		ID   int64  `json:"id"`
		Slug string `json:"slug"`
	}{Slug: "github-actions"}}}, nil)
	b, _ := json.Marshal(w)
	os.WriteFile(wp, b, 0644)
	cmd := exec.Command(os.Args[0], "-test.run=TestHelperRalphRun", "--")
	cmd.Env = append(os.Environ(), "RALPH_BE_RUN=1", "RALPH_WORLD="+wp, "RALPH_STATE="+sp, "RALPH_LOCAL_ONLY=1", "RALPH_POLL_MS=40", "RALPH_WAIT_MS=4000")
	if err := cmd.Start(); err != nil {
		t.Fatal(err)
	}
	defer cmd.Process.Kill()
	dead := time.Now().Add(2 * time.Second)
	for time.Now().Before(dead) {
		if st, err := loadState(sp); err == nil && st.NextAction == ActImplement && cmd.ProcessState == nil {
			break
		}
		time.Sleep(50 * time.Millisecond)
	}
	if err := cmd.Process.Signal(syscall.Signal(0)); err != nil {
		t.Fatal("dead", err)
	}
}
