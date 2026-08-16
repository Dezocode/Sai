package main

import (
	"crypto/ed25519"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"sync"
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
func signRaw(priv ed25519.PrivateKey, e Evidence) []byte {
	if e.Blockers == nil {
		e.Blockers = []Blocker{}
	}
	bb, _ := json.Marshal(e.Blockers)
	e.BlockerSetHash, e.Sig = hashRaw(bb), ""
	raw, _ := json.Marshal(e)
	msg, _ := signBytes(raw)
	var m map[string]json.RawMessage
	_ = json.Unmarshal(raw, &m)
	m["signature"] = json.RawMessage(`"` + base64.StdEncoding.EncodeToString(ed25519.Sign(priv, msg)) + `"`)
	out, _ := json.Marshal(m)
	return out
}
func evOK(h string, bl []Blocker) Evidence {
	return Evidence{SchemaVersion: schemaE, Repository: "o/r", PR: 1, BaseSHA: "base", HeadSHA: h, ManifestHash: "m", ReviewerIdentity: "hostinger-saul-cto", KeyID: "k", CheckRunID: 1, RuntimeAttestation: json.RawMessage(`{"host_identity":"h"}`), Shards: []Shard{{ID: "shard-0001", Digest: "d", Status: StPass}}, LocalArch: StPass, ImpactArch: StPass, SystemArch: StPass, Blockers: bl, Tests: json.RawMessage(`[{"command":"t","status":"pass"}]`), FinalDisposition: "action_required"}
}
func ids(s State) map[string]Blocker {
	m := map[string]Blocker{}
	for _, b := range s.Blockers {
		m[b.ID] = b
	}
	return m
}
func ck(name, conc, text string, id int64) ghCheck {
	c := ghCheck{Name: name, ID: id, HeadSHA: "h1", Status: "completed", Conclusion: conc}
	c.App.ID, c.App.Slug, c.Output.Text = 15368, "github-actions", text
	return c
}

func TestKernel(t *testing.T) {
	pub, priv, _ := ed25519.GenerateKey(nil)
	t.Setenv("SAI_SAUL_ATTEST_PUB", hex.EncodeToString(pub))
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	body := std("B-RALPH-CANONICAL-BLOCKER-LOOP-001", "github-comment:9")
	s := applyWorld(tw("h1", []ghComment{
		{ID: "9", Login: "own", Assoc: "OWNER", Body: body, HTMLURL: "http://c/9"},
		{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"},
		{ID: "2", Login: "r", Assoc: "NONE", Body: body},
		{ID: "3", Login: "w", Assoc: "COLLABORATOR", Body: "**BLOCKING x"},
		{ID: "4", Login: "own", Assoc: "OWNER", Body: "## BLOCKING not legacy"},
	}, nil, map[string]string{"own": "admin", "r": "none", "w": "write"}), State{})
	got := ids(s)
	if got["B-RALPH-CANONICAL-BLOCKER-LOOP-001"].ID == "" || got["COMMENT-1"].ID == "" || got["COMMENT-2"].ID != "" || got["COMMENT-3"].ID != "" || got["COMMENT-4"].ID != "" || got["COMMENT-1"].Actionable {
		t.Fatalf("comments %+v", s.Blockers)
	}
	if s.NextAction != ActImplement || s.Dispatch.Kind != "cursor_primary" || s.Dispatch.WorkItem.ID != "WI-B-RALPH-CANONICAL-BLOCKER-LOOP-001" {
		t.Fatalf("sched %s", s.Dispatch.WorkItem.ID)
	}
	if applyWorld(tw("h1", nil, []ghCheck{ck("icm-enforcement", "failure", "", 0)}, nil), State{}).NextAction != ActRemediate {
		t.Fatal("ci")
	}
	sp := applyWorld(tw("h1", nil, []ghCheck{ck("icm-enforcement", "success", "", 0), ck(checkSaul, "action_required", "", 1)}, nil), State{Repository: "o/r", PR: 1, BaseSHA: "base"})
	if ids(sp)["SAUL_PROTOCOL_V2"].ID == "" || sp.Saul.Trusted || ids(sp)["CHECK-"+h8("15368/github-actions/"+checkSaul)].ID != "" {
		t.Fatal("protocol")
	}
	text := signRaw(priv, evOK("h1", []Blocker{{SchemaVersion: schemaB, ID: "B1", SourceKind: "saul", Status: "OPEN", Blocking: true, Severity: "P1", Scope: []string{"ralph/"}, ResolutionAuthority: "saul", Applicability: Appl{Mode: "exact_head", HeadSHA: "h1"}}}))
	okc := []ghCheck{ck("icm-enforcement", "success", "", 0), ck(checkSaul, "", string(text), 1)}
	ss := applyWorld(tw("h1", []ghComment{{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"}}, okc, nil), State{Repository: "o/r", PR: 1, BaseSHA: "base"})
	if !ss.Saul.Trusted || ids(ss)["B1"].ID == "" || ids(ss)["COMMENT-1"].ID == "" || ids(ss)["SAUL_PROTOCOL_V2"].ID != "" {
		t.Fatal("union")
	}
	okc[1].Output.Text = string(signRaw(priv, evOK("h1", []Blocker{{SchemaVersion: schemaB, ID: "B1", SourceKind: "saul", Status: "RESOLVED", ResolutionAuthority: "saul"}})))
	sr := applyWorld(tw("h1", []ghComment{{ID: "1", Login: "own", Assoc: "OWNER", Body: "**BLOCKING architecture", HTMLURL: "http://c/1"}}, okc, nil), ss)
	if ids(sr)["B1"].Status != "RESOLVED" || ids(sr)["COMMENT-1"].Status != "OPEN" {
		t.Fatal("resolve")
	}
	st := State{Repository: "o/r", PR: 1, BaseSHA: "base", HeadSHA: "h1"}
	for _, w := range []string{"", "repo", "pr", "head", "base", "check", "pub", "syn", "shard", "blk"} {
		e, p := evOK("h1", []Blocker{{SchemaVersion: schemaB, ID: "B1", Status: "OPEN", Blocking: true}}), pub
		switch w {
		case "repo":
			e.Repository = "x/y"
		case "pr":
			e.PR = 9
		case "head":
			e.HeadSHA = "z"
		case "base":
			e.BaseSHA = "x"
		case "check":
			e.CheckRunID = 9
		case "pub":
			p = nil
		case "syn":
			e.Synthetic = true
		case "shard":
			e.Shards = nil
		case "blk":
			e.Blockers = []Blocker{{SchemaVersion: schemaB, ID: "", Status: "OPEN"}}
		}
		raw := signRaw(priv, e)
		var got Evidence
		_ = json.Unmarshal(raw, &got)
		if why := verifySaul(raw, got, st, p, 1); (why == "") != (w == "") {
			t.Fatalf("%q got %q", w, why)
		}
	}
	var hb Blocker
	_ = json.Unmarshal([]byte(`{"id":"X","priority":"P1","scope":"PR review","acceptance":"ok","status":"OPEN","schema_version":"ralph-blocker-v1","blocking":true}`), &hb)
	if hb.Severity != "P1" || len(hb.Scope) != 0 {
		t.Fatalf("compat %+v", hb)
	}
	prior := []Blocker{{ID: "OWN", SourceKind: "comment", Status: "OPEN", Blocking: true, ResolutionAuthority: "saul", Applicability: Appl{Mode: "sticky"}}}
	open := []Blocker{{ID: "S1", SourceKind: "saul", Status: "OPEN", Blocking: true, ResolutionAuthority: "saul", Applicability: Appl{Mode: "exact_head", HeadSHA: "h1"}}}
	mg := mergeFrontierSaul(prior, open, map[string]bool{"S1": true}, true, "h1")
	if ids(State{Blockers: mg})["OWN"].ID == "" || ids(State{Blockers: mergeFrontierSaul(mg, nil, map[string]bool{}, true, "h2")})["S1"].ID != "" {
		t.Fatal("merge")
	}
	if ids(State{Blockers: mergeFrontierSaul(prior, []Blocker{{ID: "OWN", SourceKind: "ci", Status: "RESOLVED", SourceID: "x"}}, nil, false, "h1")})["OWN"].Status != "OPEN" {
		t.Fatal("ci-clear")
	}
	if _, err := CompleteWork(ss, WorkerResult{WorkItem: ss.Grant.WorkItem, BaseSHA: "h1", Status: "RESOLVED"}); err == nil {
		t.Fatal("worker")
	}
	for _, sha := range []string{"h1", "h2"} {
		cw, err := CompleteWork(s, WorkerResult{WorkItem: s.Grant.WorkItem, BaseSHA: "h1", ResultSHA: sha, Status: awaitVal})
		if err != nil {
			t.Fatal(err)
		}
		if nx := scheduleState(cw); nx.NextAction == ActWaitSaul || nx.Dispatch.Kind == "" {
			t.Fatal(sha)
		}
	}
	s.NextAction, s.CI, s.CIAt = ActImplement, StPending, "h1"
	if scheduleState(s).NextAction == ActWaitSaul {
		t.Fatal("wait")
	}
	root := t.TempDir()
	os.MkdirAll(filepath.Join(root, "ralph"), 0755)
	if hookDecision(s, hookIn{ToolName: "Write", ToolInput: map[string]any{"path": "ralph/ralph.go"}}, "h1", root)["permission"] != "allow" {
		t.Fatal("hook")
	}
	for _, cmd := range []string{"rm x", "mv a b", "cp a b", "install a", "ruby -e x", "truncate -s0 x", "sed -i s/a/b/ x", "perl -pi -e x", "git apply x", "git checkout x", "git reset --hard", "git restore x", "git clean -fd", "python3 -c open('x','w')", "gofmt -w x", "touch x", "true > x", "echo x > y", "printf x > y", "cat <<EOF\nX\nEOF", "git status && rm x"} {
		if hookDecision(s, hookIn{ToolName: "Shell", ToolInput: map[string]any{"command": cmd}}, "h1", root)["permission"] != "deny" {
			t.Fatal(cmd)
		}
	}
	if hookDecision(s, hookIn{ToolName: "Write", ToolInput: map[string]any{"path": "/etc/passwd"}}, "h1", root)["permission"] != "deny" {
		t.Fatal("abs")
	}
	link := filepath.Join(root, "ralph", "link.go")
	if os.Symlink("ralph.go", link) == nil && hookDecision(s, hookIn{ToolName: "Write", ToolInput: map[string]any{"path": link}}, "h1", root)["permission"] != "deny" {
		t.Fatal("symlink")
	}
	p := filepath.Join(t.TempDir(), "s.json")
	var wg sync.WaitGroup
	for i := 0; i < 6; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); _ = saveState(p, s) }()
	}
	wg.Wait()
	if _, err := loadState(p); err != nil {
		t.Fatal(err)
	}
}

func TestRunLifetime(t *testing.T) {
	dir := t.TempDir()
	wp, sp := dir+"/w.json", dir+"/s.json"
	w := tw("h1", []ghComment{{ID: "9", Login: "own", Assoc: "OWNER", Body: std("B-X", "github-comment:9")}}, []ghCheck{ck("icm-enforcement", "", "", 0)}, nil)
	w.Checks[0].Status = "in_progress"
	b, _ := json.Marshal(w)
	os.WriteFile(wp, b, 0644)
	t.Setenv("RALPH_WORLD", wp)
	t.Setenv("RALPH_STATE", sp)
	t.Setenv("RALPH_LOCAL_ONLY", "1")
	t.Setenv("RALPH_POLL_MS", "40")
	t.Setenv("RALPH_WAIT_MS", "4000")
	ch := make(chan int, 1)
	go func() { ch <- runMain(false) }()
	dead := time.Now().Add(2 * time.Second)
	for time.Now().Before(dead) {
		if st, err := loadState(sp); err == nil && st.NextAction == ActImplement {
			select {
			case rc := <-ch:
				t.Fatalf("exited %d", rc)
			default:
				return
			}
		}
		time.Sleep(50 * time.Millisecond)
	}
	t.Fatal("dead")
}
