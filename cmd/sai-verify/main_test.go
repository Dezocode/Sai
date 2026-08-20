package main
import (
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)
func hooksJSON() []byte {
	h := map[string][]map[string]interface{}{}
	for _, e := range allEv {
		item := map[string]interface{}{"command": ".cursor/hooks/sai-verify.sh", "timeout": 60, "failClosed": true}
		if matchEv[e] { item["matcher"] = ".*" }
		if e == "stop" { item["loop_limit"] = 2 }
		h[e] = []map[string]interface{}{item}
	}
	b, _ := json.Marshal(map[string]interface{}{"version": 1, "hooks": h})
	return b
}
func mini(t *testing.T, dir string, files map[string]string) {
	d := filepath.Join(dir, mapDir)
	os.MkdirAll(d, 0755)
	idx := "# M\n\n## Features\n\n"
	for name, body := range files {
		idx += "- [" + strings.TrimSuffix(name, ".md") + "](./" + name + ") x.\n"
		os.WriteFile(filepath.Join(d, name), []byte(body), 0644)
	}
	os.WriteFile(filepath.Join(d, "README.md"), []byte(idx), 0644)
	os.MkdirAll(filepath.Join(dir, ".cursor"), 0755)
	os.WriteFile(filepath.Join(dir, ".cursor/hooks.json"), hooksJSON(), 0644)
}
func featBody(title, extra, proof, ent string) string {
	if proof == "" { proof = "::exists .cursor/hooks.json" }
	if ent == "" { ent = "Run `scripts/" + title + "`" }
	return "# " + title + "\n\n" + title + " via scripts/" + title + extra + ".\n\n## Sub-features\n\n- `" + title + "-run` runs `scripts/" + title + "`.\n\n## How to get to it (user POV)\n\n- " + ent + "\n\n## Driving it with verify-sai\n\n- **Run.** " + proof + "\n\n## Gotchas\n\n- none\n"
}
func root(t *testing.T) string {
	for d, _ := os.Getwd(); ; d = filepath.Dir(d) {
		if _, e := os.Stat(filepath.Join(d, mapDir, "README.md")); e == nil {
			if _, e = os.Stat(filepath.Join(d, "go.mod")); e == nil { return d }
		}
		if n := filepath.Dir(d); n == d { t.Fatal("repo root") }
	}
}
func hk(t *testing.T, r, base, payload string) (int, map[string]interface{}) {
	var out bytes.Buffer
	code := run([]string{"hook", "--root", r, "--base", base, "--evidence", filepath.Join(t.TempDir(), "none.json")}, strings.NewReader(payload), &out, bytes.NewBuffer(nil))
	var m map[string]interface{}
	json.Unmarshal(out.Bytes(), &m)
	return code, m
}
func TestFuturePRAndHooks(t *testing.T) {
	r, empty := root(t), t.TempDir(); mini(t, empty, map[string]string{})
	s, err := build(r, empty, r, ".ai/CONTEXT.md", "Read", "", "", "")
	if err != nil || !s.MapValid || s.MapFeatures < 10 || s.MapSubs < 80 || !s.HooksOK || !s.PreserveOK { t.Fatalf("cold map err=%v MapValid=%v MapFeatures=%d MapSubs=%d HooksOK=%v PreserveOK=%v Problems=%v Missing=%v Weakened=%v Base=%q Head=%q", err, s.MapValid, s.MapFeatures, s.MapSubs, s.HooksOK, s.PreserveOK, s.Problems, s.Missing, s.Weakened, s.Base, s.Head) }
	if s.Completeness == "proven" && !s.EvidenceBound { t.Fatal("completeness without evidence") }
	okRel := false
	for _, h := range s.Relevant {
		okRel = okRel || h.ID == "icm-workspace"
		if h.ID == "icm-workspace" && (h.Title == "" || h.Why == "" || len(h.Gotchas) == 0) { t.Fatalf("enriched %+v", h) }
	}
	if !okRel { t.Fatalf("relevant %v", s.Relevant) }
	sh, _ := build(r, "", r, "scripts/agent-report", "Shell", "", "", "")
	mcp, _ := build(r, "", r, "scripts/agent-report", "MCP", "", "", "")
	rd, _ := build(r, "", r, "scripts/agent-report", "Read", "", "", "")
	if sh.Relevant[0].ID != "coordination-reporting" || mcp.Relevant[0].ID != "verify-sai" || rd.Relevant[0].ID != "coordination-reporting" || rd.Tool != "Read" { t.Fatalf("tool relevant %v %v %v", sh.Relevant[0].ID, mcp.Relevant[0].ID, rd.Relevant[0].ID) }
	c0, m0 := hk(t, r, empty, `{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"scripts/agent-report"}}`)
	ctx0, _ := m0["additional_context"].(string)
	if c0 != 0 || !strings.Contains(ctx0, "FEATURE CONTEXT") || !strings.Contains(ctx0, "coordination-reporting") || !strings.Contains(ctx0, "Why:") { t.Fatal("68 pre", ctx0) }
	c1, m1 := hk(t, r, empty, `{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":"scripts/agent-report"},"tool_output":"{}"}`)
	if c1 != 0 || !strings.Contains(m1["additional_context"].(string), "Required proof:") { t.Fatal("68 post", c1, m1) }
	var rout bytes.Buffer
	run([]string{"relevant", "--root", r, "--path", ".ai/CONTEXT.md", "--tool", "Read"}, bytes.NewReader(nil), &rout, bytes.NewBuffer(nil))
	if !strings.Contains(rout.String(), `"title"`) || !strings.Contains(rout.String(), `"why"`) || !strings.Contains(rout.String(), "icm-workspace") { t.Fatal(rout.String()) }
	alpha, beta := featBody("alpha", "", "", ""), featBody("beta", "", "", "")
	base, head := t.TempDir(), t.TempDir()
	mini(t, base, map[string]string{"alpha.md": alpha, "beta.md": beta})
	mini(t, head, map[string]string{"alpha.md": alpha, "beta.md": beta})
	if s, _ = build(head, base, head, "scripts/alpha", "Shell", "", "", ""); !s.PreserveOK || s.Relevant[0].ID != "alpha" { t.Fatal("A unchanged", s.Missing, s.Relevant) }
	add := t.TempDir(); mini(t, add, map[string]string{"alpha.md": alpha, "beta.md": beta, "gamma.md": featBody("gamma", "", "", "")})
	if s, _ = build(add, base, add, "scripts/gamma", "Shell", "", "", ""); !s.PreserveOK { t.Fatal("B additive", s.Missing) }
	del := t.TempDir(); mini(t, del, map[string]string{"alpha.md": alpha})
	if s, _ = build(del, base, del, "", "", "", "", ""); s.PreserveOK || !strings.Contains(strings.Join(s.Missing, ","), "beta") { t.Fatal("C delete", s.Missing) }
	pr := t.TempDir(); mini(t, pr, map[string]string{"alpha.md": featBody("alpha", "", "`scripts/alpha-other`; exit 0.", ""), "beta.md": beta})
	if s, _ = build(pr, base, pr, "", "", "", "", ""); s.PreserveOK || len(s.Weakened) == 0 { t.Fatal("D proof replace", s.Weakened) }
	er := t.TempDir(); mini(t, er, map[string]string{"alpha.md": featBody("alpha", "", "", "Run `scripts/alpha-new`"), "beta.md": beta})
	if s, _ = build(er, base, er, "", "", "", "", ""); s.PreserveOK || len(s.Weakened) == 0 { t.Fatal("D entry replace", s.Weakened) }
	auth := t.TempDir(); mini(t, auth, map[string]string{"alpha.md": strings.Replace(alpha, "- none", "- Removal-authorized: beta", 1)})
	if s, _ = build(auth, base, auth, "", "", "", "", ""); s.PreserveOK { t.Fatal("E candidate Removal-authorized") }; ba, hd := t.TempDir(), t.TempDir(); mini(t, ba, map[string]string{"alpha.md": strings.Replace(alpha, "- none", "Removal-authorized: alpha-run", 1), "beta.md": beta}); mini(t, hd, map[string]string{"alpha.md": strings.Replace(alpha, "- `alpha-run` runs `scripts/alpha`.\n\n", "", 1), "beta.md": beta}); if s, _ = build(hd, ba, hd, "", "", "", "", ""); !s.PreserveOK { t.Fatal("F auth sub", s.Missing, s.Weakened) }
	if s, _ = build(head, "", head, "", "", "", "", "deadbeef"); s.PreserveOK || strings.Join(s.Missing, "") != "trusted base unavailable" { t.Fatal("missing base", s.Missing, s.PreserveOK) }
	if s, err = build(r, "", r, "", "", "deadbeef", "", ""); err == nil || s.OK { t.Fatal("stale HEAD") }
	d := t.TempDir()
	os.MkdirAll(filepath.Join(d, mapDir), 0755)
	os.WriteFile(filepath.Join(d, mapDir, "README.md"), []byte("# M\n\n## Features\n\n- [X](./nope.md)\n"), 0644)
	os.WriteFile(filepath.Join(d, ".cursor/hooks.json"), hooksJSON(), 0644)
	s, _ = build(d, d, d, "", "", "", "", "")
	if s.MapValid { t.Fatal("malformed map") }
	for _, tc := range []struct{ p, want string; deny bool }{
		{`{"hook_event_name":"sessionStart"}`, `verify-sai`, false},
		{`{"hook_event_name":"afterFileEdit","edits":[{"file_path":"README.md"}]}`, `map_valid`, false},
		{`{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":"scripts/agent-report"},"tool_output":"{}"}`, `preserve_ok`, false},
		{`{"hook_event_name":"preToolUse","tool_name":"Grep","tool_input":{"path":".ai/CONTEXT.md"}}`, `icm-workspace`, false},
		{`{"hook_event_name":"beforeShellExecution","command":"scripts/agent-report"}`, `coordination-reporting`, false},
		{`{"hook_event_name":"beforeMCPExecution","tool_name":"MCP","tool_input":{"command":"scripts/agent-report"}}`, `verify-sai`, false},
		{`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"/tmp/unrelated"}}`, `verify-sai`, false},
		{`{"hook_event_name":"preToolUse","claimed_head":"0","tool_name":"Read","tool_input":{"path":"README.md"}}`, ``, true},
		{`{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":".ai/CONTEXT.md"},"tool_output":"ok"}`, `icm-workspace`, false},
	} {
		c, m := hk(t, r, empty, tc.p)
		if tc.deny {
			if c != 2 || m["permission"] != "deny" { t.Fatal("deny", tc.p, c, m) }
			continue
		}
		if c != 0 || m["permission"] != nil || !strings.Contains(m["additional_context"].(string), tc.want) || strings.Contains(tc.p, "sessionStart") && strings.Count(m["additional_context"].(string), "Relevant feature:") != 1 { t.Fatal(tc.want, c, m) }
	}
	ev := filepath.Join(t.TempDir(), "ev.json")
	os.WriteFile(ev, []byte(`{"head":"nope","map_hash":"x","sweep":"clean","fail":0,"unmapped":[]}`), 0644)
	var out bytes.Buffer
	run([]string{"hook", "--root", r, "--base", empty, "--evidence", ev}, strings.NewReader(`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}`), &out, bytes.NewBuffer(nil))
	if strings.Contains(out.String(), `"permission":"allow"`) || !strings.Contains(out.String(), "mismatch") && !strings.Contains(out.String(), "unproven") { t.Fatal("stale evidence", out.String()) }
	out.Reset()
	run([]string{"hook"}, strings.NewReader("x"), &out, bytes.NewBuffer(nil))
	if !strings.Contains(out.String(), "deny") { t.Fatal(out.String()) }
	proof := bytes.Buffer{}
	run([]string{"proof", "--root", r}, bytes.NewReader(nil), &proof, bytes.NewBuffer(nil))
	ps := proof.String()
	if !strings.Contains(ps, "HEAD ") || strings.Contains(ps, "PASS evidence-bound") || !strings.Contains(ps, "REQUIRED evidence-bound") || !strings.Contains(ps, "UNEVALUATED go-test") { t.Fatal("dishonest proof", ps) }
	weak := t.TempDir()
	mini(t, weak, map[string]string{"alpha.md": alpha})
	os.MkdirAll(filepath.Join(weak, "cmd/sai-verify"), 0755); os.WriteFile(filepath.Join(weak, "cmd/sai-verify/main.go"), []byte("package main\nfunc init() { os.WriteFile(\"SENTINEL\", []byte(\"x\"), 0644) }\nfunc main() {}\n"), 0644)
	s, _ = build(weak, base, weak, "", "", "", "", "")
	if s.PreserveOK { t.Fatal("G trusted preserve still sees delete even if candidate kernel gutted") }
	src, _ := os.ReadFile(filepath.Join(r, "cmd/sai-verify/main.go"))
	if bytes.Contains(src, []byte(`"bash", "-lc"`)) || bytes.Contains(src, []byte(`Command("bash"`)) || bytes.Contains(src, []byte(`Command("sh"`)) { t.Fatal("shell evaluator") }
	drive := func(dir, proof string) (int, string) {
		mini(t, dir, map[string]string{"alpha.md": featBody("alpha", "", proof, "e")})
		o := bytes.Buffer{}; c := run([]string{"drive", "--root", dir, "--head", dir, "--base", dir, "--evidence", filepath.Join(t.TempDir(), "e.json")}, bytes.NewReader(nil), &o, bytes.NewBuffer(nil)); return c, o.String()
	}
	if c, o := drive(t.TempDir(), "::exists .cursor/hooks.json"); c != 0 || !strings.Contains(o, `"result": "PASS"`) { t.Fatal("drive", o) }; dabs := t.TempDir(); mini(t, dabs, map[string]string{"alpha.md": featBody("alpha", "", "::exists .cursor/hooks.json", "e")}); rt, e2 := os.MkdirTemp("/var/tmp", "sai-rt-"); if e2 != nil { t.Fatal(e2) }; os.Setenv("RUNNER_TEMP", rt); if run([]string{"drive", "--root", dabs, "--head", dabs, "--evidence", "/etc/passwd"}, bytes.NewReader(nil), bytes.NewBuffer(nil), bytes.NewBuffer(nil)) == 0 { t.Fatal("abs evidence") }; if run([]string{"drive", "--root", dabs, "--head", dabs, "--evidence", filepath.Join(rt, "e.json")}, bytes.NewReader(nil), bytes.NewBuffer(nil), bytes.NewBuffer(nil)) != 0 { t.Fatal("runner temp") }; os.Unsetenv("RUNNER_TEMP"); os.RemoveAll(rt)
	for _, bad := range []string{"::exec scripts/x; echo pwned", "::exec scripts/verify-semantic-hierarchy && echo pwned", "::exec scripts/verify-semantic-hierarchy | cat", "::exec scripts/verify-semantic-hierarchy > /tmp/x", "::exec python3 -c echo", "FOO=1 ::exec scripts/agent-report", "scripts/verify-semantic-hierarchy", "::exec /bin/true", "::exec ../scripts/verify-semantic-hierarchy", "::nope x", "`/bin/true`; expect exit 2.", "::exec scripts/agent-report emit INTAKE --task-id t --purpose t --result t --no-deliver"} {
		if c, o := drive(t.TempDir(), bad); c == 0 || strings.Contains(o, `"result": "PASS"`) { t.Fatal(bad, o) }
	}
	mq := t.TempDir(); os.MkdirAll(filepath.Join(mq, "scripts"), 0755); os.MkdirAll(filepath.Join(mq, ".git/agent-events/queue"), 0755); os.WriteFile(filepath.Join(mq, ".git/agent-events/queue/old.json"), []byte("20990101-fixture\n"), 0644); os.WriteFile(filepath.Join(mq, "scripts/agent-report"), []byte("#!/bin/sh\necho x > .git/agent-events/queue/new.json\n"), 0755); rec, _ := parseRecipe("::exec scripts/agent-report emit INTAKE --task-id t --purpose t --result t --no-deliver read=.git/agent-events/queue has=20990101-fixture"); if code, _, _, note := runRecipe(rec, mq); code == rec.want { t.Fatal("old queue", note) }; os.WriteFile(filepath.Join(mq, "scripts/agent-report"), []byte("#!/bin/sh\necho 20990101-fixture > .git/agent-events/queue/ok.json\n"), 0755); if code, _, _, note := runRecipe(rec, mq); code != rec.want { t.Fatal("new queue", note, code) }
	mix := t.TempDir(); mini(t, mix, map[string]string{"alpha.md": featBody("alpha", "", "::exec scripts/verify-hang timeout=0", "e"), "beta.md": featBody("beta", "", "::exec scripts/verify-envcheck", "e")})
	os.MkdirAll(filepath.Join(mix, "scripts"), 0755)
	os.WriteFile(filepath.Join(mix, "scripts/verify-hang"), []byte("#!/bin/sh\nexec sleep 30\n"), 0755)
	os.WriteFile(filepath.Join(mix, "scripts/verify-envcheck"), []byte("#!/bin/sh\nif [ -n \"$GITHUB_TOKEN\" ]; then echo LEAK; exit 1; fi\necho OK\n"), 0755)
	os.Setenv("GITHUB_TOKEN", "secret"); defer os.Unsetenv("GITHUB_TOKEN")
	mo := bytes.Buffer{}; if run([]string{"drive", "--root", mix, "--head", mix, "--base", mix, "--evidence", filepath.Join(t.TempDir(), "m.json")}, bytes.NewReader(nil), &mo, bytes.NewBuffer(nil)) == 0 || !strings.Contains(mo.String(), `"note": "timeout"`) || strings.Contains(mo.String(), "LEAK") { t.Fatal("timeout/env", mo.String()) }
	run([]string{"preserve", "--root", weak, "--base", base, "--head", weak}, bytes.NewReader(nil), bytes.NewBuffer(nil), bytes.NewBuffer(nil))
	if _, err := os.Stat(filepath.Join(weak, "SENTINEL")); err == nil { t.Fatal("candidate kernel executed") }
	stale := filepath.Join(t.TempDir(), "stale.json"); os.WriteFile(stale, []byte(`{"repo":"Dezocode/Sai","base":"x","head":"deadbeef","map_hash":"x","sweep":"clean","fail":0,"pass":1,"unmapped":[],"drives":[{"result":"PASS","stdout":"","stderr":""}]}`), 0644)
	prb, mout := bytes.Buffer{}, bytes.Buffer{}
	run([]string{"proof", "--root", r, "--evidence", stale}, bytes.NewReader(nil), &prb, bytes.NewBuffer(nil))
	if strings.Contains(prb.String(), "PASS evidence-bound") || !strings.Contains(prb.String(), "REQUIRED evidence-bound") { t.Fatal("stale proof", prb.String()) }
	if c, m := hk(t, r, empty, `{"hook_event_name":"beforeShellExecution","command":"true"}`); c != 0 { t.Fatal("missing evidence mut", c, m) }
	if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"beforeShellExecution","command":"true"}`), &mout, bytes.NewBuffer(nil)) == 0 || !strings.Contains(mout.String(), `"permission":"deny"`) { t.Fatal("stale mut", mout.String()) }; mout.Reset(); if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"beforeShellExecution","command":"go run ./cmd/sai-verify drive"}`), &mout, bytes.NewBuffer(nil)) != 0 || strings.Contains(mout.String(), `"permission":"deny"`) { t.Fatal("drive recov", mout.String()) }; mout.Reset(); if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"beforeShellExecution","command":"go run ./cmd/sai-verify drive; echo pwned"}`), &mout, bytes.NewBuffer(nil)) == 0 || !strings.Contains(mout.String(), `"permission":"deny"`) { t.Fatal("drive inject", mout.String()) }; mout.Reset(); if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"beforeShellExecution","command":"go run ./cmd/sai-verify drive --evidence /tmp/pwn"}`), &mout, bytes.NewBuffer(nil)) == 0 || !strings.Contains(mout.String(), `"permission":"deny"`) { t.Fatal("drive evidence flag", mout.String()) }
	mout.Reset(); if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"preToolUse","tool_name":"Write","tool_input":{"path":"README.md"}}`), &mout, bytes.NewBuffer(nil)); !strings.Contains(mout.String(), "deny") { t.Fatal("write mut", mout.String()) }; mout.Reset(); if run([]string{"hook", "--root", r, "--base", empty, "--evidence", stale}, strings.NewReader(`{"hook_event_name":"afterFileEdit","edits":[{"file_path":"README.md"}]}`), &mout, bytes.NewBuffer(nil)); !strings.Contains(mout.String(), "deny") { t.Fatal("afterFileEdit mut", mout.String()) }
	cBroad, mBroad := hk(t, r, empty, `{"hook_event_name":"beforeShellExecution","command":"scripts"}`); ctxb, _ := mBroad["additional_context"].(string)
	if cBroad != 0 || len(ctxb) > 6000 || !strings.Contains(ctxb, "FEATURE CONTEXT") || !strings.Contains(ctxb, "Relevant feature:") { t.Fatal("ctx cap", cBroad, len(ctxb)) }
}
func TestLinkedWorktreeHook(t *testing.T) {
	r, wt := root(t), t.TempDir()
	if b, err := exec.Command("git", "-C", r, "worktree", "add", "--detach", wt, "HEAD").CombinedOutput(); err != nil { t.Skip(string(b)) }
	defer exec.Command("git", "-C", r, "worktree", "remove", "--force", wt).Run()
	for _, rel := range []string{".cursor/hooks/sai-verify.sh", "cmd/sai-verify/main.go", "go.mod"} { b, _ := os.ReadFile(filepath.Join(r, rel)); os.MkdirAll(filepath.Join(wt, filepath.Dir(rel)), 0755); os.WriteFile(filepath.Join(wt, rel), b, 0755) }
	head, _ := exec.Command("git", "-C", wt, "rev-parse", "HEAD").Output(); gd, _ := exec.Command("git", "-C", wt, "rev-parse", "--absolute-git-dir").Output(); gds, hs := strings.TrimSpace(string(gd)), strings.TrimSpace(string(head)); glob := filepath.Join(gds, "sai-verify-"+hs+"-*"); ms, _ := filepath.Glob(glob); for _, m := range ms { os.Remove(m) }
	if st, err := os.Stat(filepath.Join(wt, ".git")); err != nil || st.IsDir() { t.Fatalf(".git file: %v %v", st, err) }
	hook := func() { h := exec.Command("bash", filepath.Join(wt, ".cursor/hooks/sai-verify.sh")); h.Dir, h.Stdin = wt, strings.NewReader(`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}`); b, err := h.CombinedOutput(); if strings.Contains(string(b), `"permission":"allow"`) || !strings.Contains(string(b), "map_valid") { t.Fatal(err, string(b)) } }
	hook(); a, _ := filepath.Glob(glob); if len(a) != 1 { t.Fatal("cache", a) }
	s0, _ := build(wt, "", wt, "", "", "", "", ""); evp := filepath.Join(t.TempDir(), "bound.json"); os.WriteFile(evp, []byte(`{"repo":"`+s0.Repo+`","base":"`+s0.Base+`","head":"`+s0.Head+`","map_hash":"`+mapHash(wt)+`","sweep":"clean","fail":0,"pass":1,"unmapped":[],"drives":[{"result":"PASS","stdout":"","stderr":""}]}`), 0644); if s1, _ := build(wt, "", wt, "", "", "", evp, ""); !s1.EvidenceBound { t.Fatal("clean evidence", s1.MaintReason) }; sp := filepath.Join(wt, "scripts/verify-semantic-hierarchy"); sb, _ := os.ReadFile(sp); os.WriteFile(sp, append(sb, []byte("\n#DIRTY\n")...), 0644); if s3, _ := build(wt, "", wt, "", "", "", evp, ""); s3.EvidenceBound { t.Fatal("dirty script still bound") }; os.WriteFile(sp, sb, 0644)
	src, _ := os.ReadFile(filepath.Join(wt, "cmd/sai-verify/main.go")); os.WriteFile(filepath.Join(wt, "cmd/sai-verify/main.go"), append([]byte("//DIRTY\n"), src...), 0644); hook(); b2, _ := filepath.Glob(glob)
	if len(b2) < 2 { t.Fatal("dirty HEAD cache reused", a, b2) }; if s2, _ := build(wt, "", wt, "", "", "", evp, ""); s2.EvidenceBound { t.Fatal("dirty kernel still bound") }
	pref := t.TempDir(); mini(t, pref, map[string]string{"alpha.md": featBody("alpha", "", "::exists scripts/verify-agent-setup", "e")}); os.MkdirAll(filepath.Join(pref, "scripts"), 0755); os.WriteFile(filepath.Join(pref, "scripts/verify-agent-setup"), []byte("x"), 0755); os.WriteFile(filepath.Join(pref, "scripts/verify-agent"), []byte("x"), 0755); exec.Command("git", "init", "-q", pref).Run(); exec.Command("git", "-C", pref, "config", "user.email", "t@t").Run(); exec.Command("git", "-C", pref, "config", "user.name", "t").Run(); exec.Command("git", "-C", pref, "add", "-A").Run(); exec.Command("git", "-C", pref, "commit", "-q", "-m", "t").Run(); if su, _ := build(pref, pref, pref, "", "", "", "", ""); !strings.Contains(strings.Join(su.Unmapped, ","), "scripts/verify-agent") || strings.Contains(strings.Join(su.Unmapped, ","), "scripts/verify-agent-setup") { t.Fatal("prefix sweep", su.Unmapped) }
}
