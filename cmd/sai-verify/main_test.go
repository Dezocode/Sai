package main

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func miniMap(t *testing.T, dir string, extra bool) {
	t.Helper()
	d := filepath.Join(dir, mapDir)
	os.MkdirAll(d, 0755)
	idx := "# M\n\n## Features\n\n- [Alpha](./alpha.md) a.\n"
	if extra {
		idx += "- [Beta](./beta.md) b.\n"
	}
	body := func(id string) string {
		return "# " + id + "\n\n" + id + " via scripts/" + id + ".\n\n## Sub-features\n\n- `" + id + "-run` runs `scripts/" + id + "`.\n\n## How to get to it (user POV)\n\n- Run `scripts/" + id + "`\n\n## Driving it with verify-sai\n\n- **Run.** `scripts/" + id + "`; exit 0.\n\n## Gotchas\n\n- none\n"
	}
	os.WriteFile(filepath.Join(d, "README.md"), []byte(idx), 0644)
	os.WriteFile(filepath.Join(d, "alpha.md"), []byte(body("alpha")), 0644)
	if extra {
		os.WriteFile(filepath.Join(d, "beta.md"), []byte(body("beta")), 0644)
	}
	os.MkdirAll(filepath.Join(dir, ".cursor"), 0755)
	os.WriteFile(filepath.Join(dir, ".cursor/hooks.json"), []byte(`{"version":1,"hooks":{"preToolUse":[{"command":".cursor/hooks/sai-verify.sh","matcher":".*","failClosed":true}],"postToolUse":[{"command":".cursor/hooks/sai-verify.sh","matcher":".*","failClosed":true}],"stop":[{"command":".cursor/hooks/sai-verify.sh"}]}}`), 0644)
}

func root(t *testing.T) string {
	t.Helper()
	wd, _ := os.Getwd()
	if filepath.Base(wd) == "sai-verify" {
		wd = filepath.Join(wd, "../..")
	}
	return wd
}

func hookJSON(t *testing.T, r, payload string) map[string]any {
	t.Helper()
	var out bytes.Buffer
	run([]string{"hook", "--root", r}, strings.NewReader(payload), &out, bytes.NewBuffer(nil))
	var m map[string]any
	json.Unmarshal(out.Bytes(), &m)
	return m
}

func TestRepoColdSyntheticHooks(t *testing.T) {
	r := root(t)
	s, err := build(r, r, r, ".ai/CONTEXT.md", "Read", "")
	if err != nil || !s.MapValid || s.MapFeatures < 10 || s.MapSubs < 80 || !s.HooksOK || !s.PreserveOK {
		t.Fatalf("map %v %v", s.Problems, err)
	}
	okRel := false
	for _, h := range s.Relevant {
		okRel = okRel || h.ID == "icm-workspace"
	}
	if !okRel {
		t.Fatalf("relevant %v", s.Relevant)
	}
	var out, errb bytes.Buffer
	if run([]string{"snapshot", "--root", r, "--path", ".github/workflows/agent-audit.yml"}, bytes.NewReader(nil), &out, &errb) != 0 {
		t.Fatal(out.String())
	}
	var snap snap
	json.Unmarshal(out.Bytes(), &snap)
	if !snap.OK || snap.Head == "" {
		t.Fatal("cold")
	}
	out.Reset()
	if run([]string{"proof", "--root", r}, bytes.NewReader(nil), &out, &errb) != 0 || !strings.Contains(out.String(), "head:") {
		t.Fatal(out.String())
	}
	base, head := t.TempDir(), t.TempDir()
	miniMap(t, base, true)
	miniMap(t, head, true)
	s, _ = build(head, base, head, "scripts/alpha", "Shell", "")
	if !s.PreserveOK || s.Relevant[0].ID != "alpha" {
		t.Fatal("unchanged")
	}
	head2 := t.TempDir()
	miniMap(t, head2, true)
	miniMap(t, base, false)
	s, _ = build(head2, base, head2, "scripts/beta", "Shell", "")
	if !s.PreserveOK {
		t.Fatal("add", s.Missing)
	}
	del := t.TempDir()
	miniMap(t, del, false)
	miniMap(t, base, true)
	s, _ = build(del, base, del, "", "", "")
	if s.PreserveOK || !strings.Contains(strings.Join(s.Missing, ","), "beta") {
		t.Fatal("delete", s.Missing)
	}
	if s, err = build(r, r, r, "", "", "deadbeef"); err == nil || s.OK {
		t.Fatal("stale")
	}
	d := t.TempDir()
	os.MkdirAll(filepath.Join(d, mapDir), 0755)
	os.WriteFile(filepath.Join(d, mapDir, "README.md"), []byte("# M\n\n## Features\n\n- [X](./nope.md)\n"), 0644)
	s, _ = build(d, d, d, "", "", "")
	if s.MapValid {
		t.Fatal("dead")
	}
	pre := hookJSON(t, r, `{"hook_event_name":"preToolUse","tool_name":"Read","tool_input":{"path":"README.md"}}`)
	if pre["permission"] != "allow" {
		t.Fatal(pre)
	}
	post := hookJSON(t, r, `{"hook_event_name":"postToolUse","tool_name":"StrReplace","tool_input":{"path":"scripts/agent-report"},"tool_output":"{}"}`)
	if !strings.Contains(post["additional_context"].(string), "sai-verify") {
		t.Fatal(post)
	}
	if hookJSON(t, r, `{"hook_event_name":"preToolUse","claimed_head":"0","tool_name":"Read","tool_input":{"path":"README.md"}}`)["permission"] != "deny" {
		t.Fatal("stale pre")
	}
	out.Reset()
	run([]string{"hook"}, strings.NewReader("x"), &out, bytes.NewBuffer(nil))
	if !strings.Contains(out.String(), "deny") {
		t.Fatal(out.String())
	}
}
