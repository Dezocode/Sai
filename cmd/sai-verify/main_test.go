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
	if proof == "" { proof = "`scripts/" + title + "`; exit 0." }
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
func hk(t *testing.T, r, payload string) (int, map[string]interface{}) {
	var out bytes.Buffer
	code := run([]string{"hook", "--root", r}, strings.NewReader(payload), &out, bytes.NewBuffer(nil))
	var m map[string]interface{}
	json.Unmarshal(out.Bytes(), &m)
	return code, m
}
func TestFuturePRAndHooks(t *testing.T) {
	r := root(t)
	s, err := build(r, "", r, ".ai/CONTEXT.md", "Read", "", "", "")
	if err != nil || !s.MapValid || s.MapFeatures < 10 || s.MapSubs < 80 || !s.HooksOK || !s.PreserveOK { t.Fatalf("cold map %v %v", s.Problems, err) }
	if s.Completeness == "proven" && !s.EvidenceBound { t.Fatal("completeness without evidence") }
	okRel := false
	for _, h := range s.Relevant { okRel = okRel || h.ID == "icm-workspace" }
	if !okRel { t.Fatalf("relevant %v", s.Relevant) }
	sh, mcp, _ := func() (snap, snap, error) { a, _ := build(r, "", r, "scripts/agent-report", "Shell", "", "", ""); b, _ := build(r, "", r, "scripts/agent-report", "MCP", "", "", ""); return a, b, nil }()
	if sh.Relevant[0].ID != "coordination-reporting" || mcp.Relevant[0].ID != "verify-sai" { t.Fatalf("tool relevant %v %v", sh.Relevant, mcp.Relevant) }
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
	if s, _ = build(auth, base, auth, "", "", "", "", ""); s.PreserveOK { t.Fatal("E candidate Removal-authorized") }
	if s, _ = build(head, "", head, "", "", "", "", "deadbeef"); s.PreserveOK || strings.Join(s.Missing, "") != "trusted base unavailable" { t.Fatal("missing base", s.Missing, s.PreserveOK) }
	if s, err = build(r, "", r, "", "", "deadbeef", "", ""); err == nil || s.OK { t.Fatal("stale HEAD") }
	d := t.TempDir()
	os.MkdirAll(filepath.Join(d, mapDir), 0755)
	os.WriteFile(filepath.Join(d, mapDir, "README.md"), []byte("# M\n\n## Features\n\n- [X](./nope.md)\n"), 0644)
	os.WriteFile(filepath.Join(d, ".cursor/hooks.json"), hooksJSON(), 0644)
	s, _ = build(d, d, d, "", "", "", "", "")
	if s.MapValid { t.Fatal("malformed map") }
	for _, tc := range []struct{ p, want string; deny bool }{
		{`{"hook_event_name":"sessionStart"}`, `map_valid`, false},
		{`{"hook_event_name":"afterFileEdit","edits":[{"file_path":"README.md"}]}`, `map_valid`, false},
		{`{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":"scripts/agent-report"},"tool_output":"{}"}`, `preserve_ok`, false},
		{`{"hook_event_name":"preToolUse","tool_name":"Grep","tool_input":{"path":".ai/CONTEXT.md"}}`, `icm-workspace`, false},
		{`{"hook_event_name":"beforeShellExecution","command":"scripts/agent-report"}`, `coordination-reporting`, false},
		{`{"hook_event_name":"beforeMCPExecution","tool_name":"MCP","tool_input":{"command":"scripts/agent-report"}}`, `verify-sai`, false},
		{`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"/tmp/unrelated"}}`, `verify-sai`, false},
		{`{"hook_event_name":"preToolUse","claimed_head":"0","tool_name":"Read","tool_input":{"path":"README.md"}}`, ``, true},
		{`{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":".ai/CONTEXT.md"},"tool_output":"ok"}`, `icm-workspace`, false},
	} {
		c, m := hk(t, r, tc.p)
		if tc.deny {
			if c != 2 || m["permission"] != "deny" { t.Fatal("deny", tc.p, c, m) }
			continue
		}
		if c != 0 || m["permission"] != nil || !strings.Contains(m["additional_context"].(string), tc.want) { t.Fatal(tc.want, c, m) }
	}
	ev := filepath.Join(t.TempDir(), "ev.json")
	os.WriteFile(ev, []byte(`{"head":"nope","map_hash":"x","sweep":"clean","fail":0,"unmapped":[]}`), 0644)
	var out bytes.Buffer
	run([]string{"hook", "--root", r, "--evidence", ev}, strings.NewReader(`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}`), &out, bytes.NewBuffer(nil))
	if strings.Contains(out.String(), `"permission":"allow"`) || !strings.Contains(out.String(), "mismatch") && !strings.Contains(out.String(), "unproven") { t.Fatal("stale evidence", out.String()) }
	out.Reset()
	run([]string{"hook"}, strings.NewReader("x"), &out, bytes.NewBuffer(nil))
	if !strings.Contains(out.String(), "deny") { t.Fatal(out.String()) }
	proof := bytes.Buffer{}
	run([]string{"proof", "--root", r}, bytes.NewReader(nil), &proof, bytes.NewBuffer(nil))
	ps := proof.String()
	if !strings.Contains(ps, "HEAD ") || strings.Contains(ps, "PASS go-test") { t.Fatal("dishonest proof", ps) }
	if !strings.Contains(ps, "UNEVALUATED go-test") && !strings.Contains(ps, "PASS evidence-bound") { t.Fatal("proof statuses", ps) }
	weak := t.TempDir()
	mini(t, weak, map[string]string{"alpha.md": alpha})
	os.WriteFile(filepath.Join(weak, "cmd/sai-verify/main.go"), []byte("package main\nfunc main() {}\n"), 0644)
	s, _ = build(weak, base, weak, "", "", "", "", "")
	if s.PreserveOK { t.Fatal("G trusted preserve still sees delete even if candidate kernel gutted") }
	drv, evp, dout := t.TempDir(), filepath.Join(t.TempDir(), "ev.json"), bytes.Buffer{}
	mini(t, drv, map[string]string{"alpha.md": featBody("alpha", "", "`/bin/true`; exit 0.", "Run `/bin/true`")})
	if run([]string{"drive", "--root", drv, "--head", drv, "--base", drv, "--evidence", evp}, bytes.NewReader(nil), &dout, bytes.NewBuffer(nil)) != 0 || !strings.Contains(dout.String(), `"result": "PASS"`) { t.Fatal("drive", dout.String()) }
}
func TestLinkedWorktreeHook(t *testing.T) {
	r, wt := root(t), t.TempDir()
	if b, err := exec.Command("git", "-C", r, "worktree", "add", "--detach", wt, "HEAD").CombinedOutput(); err != nil { t.Skip(string(b)) }
	defer exec.Command("git", "-C", r, "worktree", "remove", "--force", wt).Run()
	for _, rel := range []string{".cursor/hooks/sai-verify.sh", "cmd/sai-verify/main.go", "go.mod"} {
		b, _ := os.ReadFile(filepath.Join(r, rel))
		os.MkdirAll(filepath.Join(wt, filepath.Dir(rel)), 0755)
		os.WriteFile(filepath.Join(wt, rel), b, 0755)
	}
	head, _ := exec.Command("git", "-C", wt, "rev-parse", "HEAD").Output()
	gd, _ := exec.Command("git", "-C", wt, "rev-parse", "--absolute-git-dir").Output()
	gds := strings.TrimSpace(string(gd))
	os.Remove(filepath.Join(gds, "sai-verify-"+strings.TrimSpace(string(head))))
	st, err := os.Stat(filepath.Join(wt, ".git"))
	if err != nil || st.IsDir() { t.Fatalf(".git file: %v %v", st, err) }
	h := exec.Command("bash", filepath.Join(wt, ".cursor/hooks/sai-verify.sh"))
	h.Dir, h.Stdin = wt, strings.NewReader(`{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}`)
	b, err := h.CombinedOutput()
	if err != nil || strings.Contains(string(b), `"permission":"allow"`) || !strings.Contains(string(b), "map_valid") { t.Fatal(err, string(b)) }
	if _, err := os.Stat(filepath.Join(gds, "sai-verify-"+strings.TrimSpace(string(head)))); err != nil { t.Fatal(err) }
}
