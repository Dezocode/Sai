package main
import (
	"bufio"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)
const mapDir = ".cursor/skills/verify-sai/features"
var (
	linkRe  = regexp.MustCompile(`\]\((?:\./)?([^)]+\.md)\)`)
	idRe    = regexp.MustCompile("`([a-z][a-z0-9-]*)`")
	pathRe  = regexp.MustCompile(`(?:\./)?(?:\.ai|\.cursor|\.github|\.githooks|scripts|openclaw-dashboard|cmd)(/[A-Za-z0-9_.*{}-]+)+|(?:AGENTS|CLAUDE|CODEX|OPENCLAW|README|Team)\.md|go\.mod`)
	rmRe    = regexp.MustCompile(`(?i)^Removal-authorized:\s*(.+)$`)
	h2Re    = regexp.MustCompile(`^## `)
	allEv   = []string{"sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop", "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought", "workspaceOpen"}
	matchEv = map[string]bool{"preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "beforeShellExecution": true, "afterShellExecution": true, "beforeReadFile": true, "afterFileEdit": true, "subagentStart": true, "subagentStop": true}
)
type feat struct {
	ID, Title, File, Desc string
	Subs [][2]string
	Ent, Proof, Paths, Rm, Unreach, Gotchas []string
}
type hit struct {
	ID string `json:"id"`
	Title string `json:"title"`
	Why string `json:"why"`
	Subs []string `json:"subfeatures"`
	Entries []string `json:"entry_points"`
	Proofs []string `json:"proofs"`
	Paths []string `json:"affected_paths_or_surfaces"`
	Gotchas []string `json:"gotchas"`
}
type snap struct {
	Repo string `json:"repo"`
	Base string `json:"base"`
	Head string `json:"head"`
	Path string `json:"path,omitempty"`
	Tool string `json:"tool,omitempty"`
	Dirty bool `json:"dirty"`
	OK bool `json:"ok"`
	Err string `json:"err,omitempty"`
	MapValid bool `json:"map_valid"`
	MapFiles int `json:"map_files"`
	MapFeatures int `json:"map_features"`
	MapSubs int `json:"map_subfeatures"`
	MapEntries int `json:"map_entry_points"`
	IDs []string `json:"ids"`
	Problems []string `json:"problems,omitempty"`
	PreserveOK bool `json:"preserve_ok"`
	Missing []string `json:"missing,omitempty"`
	Weakened []string `json:"weakened,omitempty"`
	Relevant []hit `json:"features"`
	HooksOK bool `json:"hooks_ok"`
	HookPre bool `json:"hook_pre"`
	HookPost bool `json:"hook_post"`
	HookStop bool `json:"hook_stop"`
	HookMatcher string `json:"hook_matcher"`
	HookFailClosed bool `json:"hook_fail_closed"`
	HookEvents []string `json:"hook_events"`
	MaintRequired bool `json:"maintenance_required"`
	MaintReason string `json:"maintenance_reason,omitempty"`
	Obligations []string `json:"obligations"`
	Unreachable []string `json:"unreachable"`
	ImplFiles int `json:"impl_files"`
	ImplLOC int `json:"impl_loc"`
	ImplFuncs int `json:"impl_funcs"`
	MaintStatus string `json:"maintenance_status"`
	MaintHead string `json:"maintenance_head,omitempty"`
	MaintMapHash string `json:"maintenance_map_hash,omitempty"`
	Completeness string `json:"whole_repo_completeness"`
	EvidenceBound bool `json:"evidence_bound"`
	Unmapped []string `json:"unmapped,omitempty"`
}
func main() { os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr)) }
func run(args []string, in io.Reader, out, errw io.Writer) int {
	cmd, root, baseDir, headDir, path, tool, wantHead, evPath, baseRef := "snapshot", ".", "", "", "", "", "", "", ""
	evSet := false
	set := map[string]*string{"--root": &root, "--base": &baseDir, "--head": &headDir, "--path": &path, "--tool": &tool, "--claimed-head": &wantHead, "--expect-head": &wantHead, "--evidence": &evPath, "--base-ref": &baseRef}
	for i := 0; i < len(args); i++ {
		a := args[i]
		if p, ok := set[a]; ok {
			if i+1 >= len(args) || strings.HasPrefix(args[i+1], "-") { fmt.Fprintf(errw, "missing value %s\n", a); return 2 }
			i++; *p = args[i]; evSet = evSet || a == "--evidence"; continue
		}
		if strings.HasPrefix(a, "-") {
			fmt.Fprintf(errw, "unknown flag %s\n", a)
			return 2
		}
		cmd = a
	}
	if headDir == "" { headDir = root }
	if cmd == "hook" { return hook(in, out, root, evPath, baseDir, baseRef) }
	s, ferr := build(root, baseDir, headDir, path, tool, wantHead, evPath, baseRef)
	if ferr != nil && s.Err == "" { s.Err, s.OK = ferr.Error(), false }
	if cmd == "drive" { return driveCmd(s, headDir, evPath, out) }
	switch cmd {
	case "proof": writeProof(out, s, evPath, headDir)
	case "relevant": _ = json.NewEncoder(out).Encode(map[string]interface{}{"repo": s.Repo, "base": s.Base, "head": s.Head, "tool": s.Tool, "path": s.Path, "features": s.Relevant, "verification": map[string]interface{}{"map_valid": s.MapValid, "preserve_ok": s.PreserveOK, "maintenance_status": s.MaintStatus, "maintenance_head": s.MaintHead, "maintenance_map_hash": s.MaintMapHash, "whole_repo_completeness": s.Completeness, "obligations": s.Obligations}})
	case "preserve":
		if s.PreserveOK { fmt.Fprintln(out, "preserve_ok") }
	default: _ = json.NewEncoder(out).Encode(s)
	}
	if cmd == "preserve" && !s.PreserveOK || cmd == "doctor" && (!s.MapValid || !s.HooksOK || s.Err != "" || evSet && s.Completeness != "proven") || cmd != "doctor" && cmd != "preserve" && cmd != "relevant" && !s.OK { return 1 }
	return 0
}
func build(root, baseDir, headDir, path, tool, claimed, evPath, baseRef string) (snap, error) {
	s := snap{PreserveOK: true, Repo: repoName(git(headDir, "config", "--get", "remote.origin.url")), Head: git(headDir, "rev-parse", "HEAD"), Path: path, Tool: tool}
	if s.Base = baseRef; s.Base == "" { s.Base = git(headDir, "merge-base", "HEAD", "origin/main") }
	if s.Base == "" { s.Base = git(headDir, "rev-parse", "--verify", "origin/main^{commit}") }; if s.Base == "" { s.Base = "unavailable" }
	s.Dirty = git(headDir, "status", "--porcelain") != ""
	if claimed != "" && claimed != s.Head {
		s.OK, s.Err = false, "stale head: claimed "+claimed+" current "+s.Head
		return s, fmt.Errorf("%s", s.Err)
	}
	hf, hp := loadFeats(headDir)
	fillMap(&s, hf, hp)
	s.HooksOK, s.HookPre, s.HookPost, s.HookStop, s.HookMatcher, s.HookFailClosed, s.HookEvents = checkHooks(headDir)
	if !s.HooksOK { s.Problems = append(s.Problems, "hooks missing full sai-verify agent event set fail-closed") }
	var bf []feat
	var berr []string
	if baseDir != "" && filepath.Clean(baseDir) != filepath.Clean(headDir) {
		bf, berr = loadFeats(baseDir)
	} else { bf, berr = loadFeatsRef(headDir, s.Base) }
	if len(berr) > 0 {
		s.Missing, s.PreserveOK = []string{"trusted base unavailable"}, false
	} else {
		s.Missing, s.Weakened = preserve(bf, hf)
		s.PreserveOK = len(s.Missing)+len(s.Weakened) == 0
	}
	s.Relevant, s.Unreachable, s.Unmapped = relevant(hf, path, tool), unreachable(hf), unmapped(headDir, hf)
	if b, err := os.ReadFile(filepath.Join(headDir, "cmd/sai-verify/main.go")); err == nil { s.ImplFiles, s.ImplLOC, s.ImplFuncs = 1, bytes.Count(b, []byte("\n")), bytes.Count(b, []byte("\nfunc ")) }
	for _, h := range s.Relevant { s.Obligations = append(s.Obligations, h.Proofs...) }
	bindEvidence(&s, evPath, headDir)
	s.OK = s.MapValid && s.PreserveOK && s.HooksOK && s.Err == ""
	return s, nil
}
func fillMap(s *snap, fs []feat, probs []string) {
	s.MapFiles, s.MapFeatures = len(fs), len(fs)
	seen := map[string]bool{}
	for _, f := range fs {
		if seen[f.ID] { probs = append(probs, "duplicate id "+f.ID) }
		seen[f.ID], s.IDs, s.MapSubs, s.MapEntries = true, append(s.IDs, f.ID), s.MapSubs+len(f.Subs), s.MapEntries+len(f.Ent)
		for _, sub := range f.Subs {
			if seen[sub[0]] { probs = append(probs, "duplicate id "+sub[0]) }
			seen[sub[0]], s.IDs = true, append(s.IDs, sub[0])
		}
	}
	sort.Strings(s.IDs)
	s.Problems, s.MapValid = uniq(probs), len(uniq(probs)) == 0 && len(fs) > 0
}
func loadFeats(root string) ([]feat, []string) {
	dir := filepath.Join(root, mapDir)
	b, err := os.ReadFile(filepath.Join(dir, "README.md"))
	if err != nil { return nil, []string{"missing " + filepath.Join(dir, "README.md")} }
	var indexed []string
	inFeat := false
	sc := bufio.NewScanner(bytes.NewReader(b))
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "## Features") { inFeat = true; continue }
		if inFeat && strings.HasPrefix(line, "## ") { break }
		if inFeat {
			if m := linkRe.FindStringSubmatch(line); len(m) > 1 { indexed = append(indexed, m[1]) }
		}
	}
	ents, _ := os.ReadDir(dir)
	onDisk, seenIdx, fs, probs := map[string]bool{}, map[string]bool{}, []feat{}, []string{}
	for _, e := range ents { if !e.IsDir() && e.Name() != "README.md" && strings.HasSuffix(e.Name(), ".md") { onDisk[e.Name()] = true } }
	for _, name := range indexed {
		if seenIdx[name] { probs = append(probs, "duplicate index "+name) }; seenIdx[name] = true
		if !onDisk[name] { probs = append(probs, "dead index "+name); continue }
		f, p := parseFeat(filepath.Join(dir, name), strings.TrimSuffix(name, ".md")); probs, fs = append(probs, p...), append(fs, f)
	}
	for name := range onDisk { if !seenIdx[name] { probs = append(probs, "unindexed "+name) } }
	return fs, probs
}
func loadFeatsRef(dir, ref string) ([]feat, []string) {
	if ref == "" || ref == "unavailable" || git(dir, "rev-parse", "--verify", ref+"^{commit}") == "" { return nil, []string{"trusted base unavailable"} }
	idx := git(dir, "show", ref+":"+mapDir+"/README.md")
	if idx == "" { return nil, nil }
	tmp, _ := os.MkdirTemp("", "sai-b-")
	defer os.RemoveAll(tmp)
	d := filepath.Join(tmp, mapDir)
	os.MkdirAll(d, 0755)
	os.WriteFile(filepath.Join(d, "README.md"), []byte(idx), 0644)
	for _, m := range linkRe.FindAllStringSubmatch(idx, -1) {
		if m[1] != "README.md" { os.WriteFile(filepath.Join(d, m[1]), []byte(git(dir, "show", ref+":"+mapDir+"/"+m[1])), 0644) }
	}
	return loadFeats(tmp)
}
func mapHash(dir string) string {
	h, seen := sha256.New(), map[string]bool{}
	var roots []string
	fs, _ := loadFeats(dir)
	for _, f := range fs { for _, p := range f.Paths { p = filepath.Clean(strings.TrimPrefix(p, "./")); if i := strings.IndexAny(p, "*?{"); i > 1 { p = filepath.Clean(p[:i]) }; roots = append(roots, p) } }
	for _, p := range uniq(append(roots, mapDir, "cmd", ".cursor/hooks", ".cursor/hooks.json", ".github/policy", ".github/workflows", "go.mod")) {
		filepath.Walk(filepath.Join(dir, p), func(fp string, inf os.FileInfo, err error) error {
			if err == nil && inf != nil && !inf.IsDir() { rel, _ := filepath.Rel(dir, fp); if !seen[rel] && !strings.HasPrefix(rel, ".ai/runs/") && !strings.Contains(rel, "__pycache__") && !strings.Contains(rel, "node_modules") && !strings.HasSuffix(rel, ".pyc") { seen[rel] = true; b, _ := os.ReadFile(fp); h.Write([]byte(rel)); h.Write(b) } }
			return nil
		})
	}
	return fmt.Sprintf("%x", h.Sum(nil)[:16])
}
func bindEvidence(s *snap, evPath, headDir string) {
	s.MaintStatus, s.Completeness, s.MaintRequired, s.MaintReason = "missing", "unproven", true, "no exact-head maintenance evidence"
	if evPath == "" { evPath = filepath.Join(git(headDir, "rev-parse", "--absolute-git-dir"), "sai-verify-evidence.json") }
	b, err := os.ReadFile(evPath)
	if err != nil { return }
	var ev map[string]interface{}
	if json.Unmarshal(b, &ev) != nil { s.MaintReason = "malformed evidence"; return }
	head, _ := ev["head"].(string)
	mh, _ := ev["map_hash"].(string)
	repo, _ := ev["repo"].(string)
	sweep, _ := ev["sweep"].(string)
	s.MaintHead, s.MaintMapHash, s.MaintStatus = head, mh, "stale"
	_, hasFail := ev["fail"]
	_, hasPass := ev["pass"]
	n, _ := ev["fail"].(float64)
	um, _ := ev["unmapped"].([]interface{})
	ds, _ := ev["drives"].([]interface{})
	ebase, _ := ev["base"].(string)
	ioOK := true; for _, d := range ds { m, _ := d.(map[string]interface{}); if str(m["result"]) != "SKIP" && (m["stdout"] == nil || m["stderr"] == nil) { ioOK = false } }
	switch {
	case repo == "" || s.Repo == "" || repo != s.Repo: s.MaintReason = "evidence repo mismatch"
	case ebase == "" || s.Base == "" || ebase != s.Base: s.MaintReason = "evidence base mismatch"
	case head != s.Head: s.MaintReason = "evidence HEAD mismatch"
	case mh != mapHash(headDir): s.MaintReason = "evidence map hash mismatch"
	case !hasFail || !hasPass || sweep == "" || !ioOK: s.MaintReason = "incomplete evidence"
	case sweep != "clean" || len(um) > 0: s.MaintStatus, s.MaintReason = "incomplete", "source sweep not clean"
	case n != 0: s.MaintStatus, s.MaintReason = "bound", "live-drive failures"
	default: s.MaintStatus, s.MaintRequired, s.MaintReason, s.Completeness, s.EvidenceBound = "bound", false, "", "proven", true
	}
}
func bear(f string) bool {
	return f != "" && !strings.HasPrefix(f, ".ai/runs/") && !strings.Contains(f, "__pycache__") && !strings.Contains(f, "node_modules") && !strings.HasSuffix(f, ".pyc")
}
func unmapped(root string, fs []feat) []string {
	blob := git(root, "ls-files", "-z")
	if blob == "" { return nil }
	exact, prefs := map[string]bool{}, []string{}
	for _, ft := range fs {
		for _, p := range ft.Paths {
			p = filepath.Clean(strings.TrimPrefix(p, "./"))
			if i := strings.IndexAny(p, "*?{"); i > 1 { prefs = append(prefs, p, filepath.Clean(p[:i])) } else { exact[p] = true }
		}
	}
	var miss []string
	for _, f := range strings.Split(blob, "\x00") {
		if !bear(f) { continue }
		hit := exact[f]
		if !hit {
			for _, p := range prefs {
				if ok, _ := filepath.Match(p, f); ok || p != "." && (f == p || strings.HasPrefix(f, p+"/")) { hit = true; break }
			}
		}
		if !hit { miss = append(miss, f) }
	}
	sort.Strings(miss)
	return miss
}
func parseFeat(path, id string) (feat, []string) {
	b, err := os.ReadFile(path)
	f := feat{ID: id, File: filepath.Base(path)}
	if err != nil { return f, []string{"read " + path} }
	var probs []string
	sec := ""
	sc := bufio.NewScanner(bytes.NewReader(b))
	for sc.Scan() {
		line := sc.Text()
		low := strings.ToLower(line)
		if strings.Contains(low, "stub exit 2") || strings.Contains(low, "verified-unreachable") || strings.Contains(low, "requires openclaw") { f.Unreach = append(f.Unreach, strings.TrimSpace(strings.TrimPrefix(line, "- "))) }
		if strings.HasPrefix(line, "# ") && f.Title == "" { f.Title = strings.TrimSpace(line[2:]); continue }
		if m := rmRe.FindStringSubmatch(line); len(m) > 1 {
			for _, p := range strings.Split(m[1], ",") {
				if p = strings.TrimSpace(p); p != "" && p != "(none)" { f.Rm = append(f.Rm, p) }
			}
		}
		if h2Re.MatchString(line) { sec = strings.TrimSpace(line[3:]); continue }
		switch {
		case f.Desc == "" && line != "" && !strings.HasPrefix(line, "#") && sec == "":
			f.Desc = line
		case strings.HasPrefix(sec, "Sub-features") && strings.HasPrefix(line, "-"):
			ids := idRe.FindAllStringSubmatch(line, -1)
			if len(ids) == 0 { probs = append(probs, f.ID+": sub-feature missing id"); continue }
			f.Subs = append(f.Subs, [2]string{ids[0][1], strings.TrimSpace(idRe.ReplaceAllString(line[1:], ""))})
		case strings.HasPrefix(sec, "How to get to it") && strings.HasPrefix(line, "-"):
			f.Ent = append(f.Ent, strings.TrimSpace(strings.TrimPrefix(line, "-")))
		case strings.HasPrefix(sec, "Driving it") && strings.HasPrefix(line, "-"):
			f.Proof = append(f.Proof, strings.TrimSpace(line[1:]))
		case strings.HasPrefix(sec, "Gotchas") && strings.HasPrefix(line, "-"):
			f.Gotchas = append(f.Gotchas, strings.TrimSpace(strings.TrimPrefix(line, "-")))
		}
	}
	f.Paths = uniq(pathRe.FindAllString(string(b), -1))
	if f.Title == "" || f.Desc == "" || len(f.Subs) == 0 || len(f.Ent) == 0 { probs = append(probs, f.ID+": incomplete feature contract") }
	return f, probs
}
func lost(old, neu []string) bool {
	n := map[string]bool{}
	for _, x := range neu { n[x] = true }
	for _, x := range old {
		if !n[x] { return true }
	}
	return false
}
func subIDs(f feat) (o []string) {
	for _, s := range f.Subs {
		if s[0] != "" { o = append(o, s[0]) }
	}
	return
}
func preserve(base, head []feat) (missing, weakened []string) {
	if len(base) == 0 { return }
	hm, rm := map[string]feat{}, map[string]bool{}
	for _, f := range head {
		hm[f.ID] = f
		for _, s := range f.Subs { hm[s[0]] = f }
	}
	for _, f := range base {
		for _, id := range f.Rm { rm[id] = true }
	}
	has := func(id string) bool { _, ok := hm[id]; return ok }
	for _, f := range base {
		if !rm[f.ID] && !has(f.ID) { missing = append(missing, f.ID) }
		hf := hm[f.ID]
		if has(f.ID) && (lost(func() []string { var o []string; for _, id := range subIDs(f) { if !rm[id] { o = append(o, id) } }; return o }(), subIDs(hf)) || lost(f.Ent, hf.Ent) || lost(f.Proof, hf.Proof)) { weakened = append(weakened, f.ID) }
		for _, s := range f.Subs {
			if !rm[s[0]] && !has(s[0]) { missing = append(missing, s[0]) }
		}
	}
	sort.Strings(missing)
	sort.Strings(weakened)
	return
}
func relevant(fs []feat, path, tool string) []hit {
	pl, out, fb := strings.ToLower(strings.TrimSpace(path)), []hit{}, hit{}
	for _, f := range fs {
		h := hit{ID: f.ID, Title: f.Title, Why: f.Desc, Entries: f.Ent, Proofs: f.Proof, Paths: f.Paths, Gotchas: f.Gotchas}
		for _, s := range f.Subs { h.Subs = append(h.Subs, s[0]) }
		if f.ID == "verify-sai" { fb = h }
		ok := path == "" && tool == "" && f.ID == "verify-sai"
		for _, p := range f.Paths {
			p = strings.ToLower(strings.TrimPrefix(p, "./"))
			if p == "" || pl == "" { continue }
			if strings.Contains(p, "/") { ok = ok || strings.Contains(pl, p) || strings.Contains(p, pl) } else { ok = ok || pl == p || strings.HasSuffix(pl, "/"+p) }
		}
		if ok && tool != "" && !relTool(f, tool) { ok = false }
		if ok { out = append(out, h) }
	}
	if len(out) == 0 && fb.ID != "" { return []hit{fb} }
	return out
}
func checkHooks(root string) (ok, pre, post, stop bool, matcher string, failClosed bool, events []string) {
	b, err := os.ReadFile(filepath.Join(root, ".cursor/hooks.json"))
	if err != nil { return }
	var doc struct {
		Hooks map[string][]struct{ Command, Matcher string; FailClosed bool }
	}
	if json.Unmarshal(b, &doc) != nil { return }
	good := func(name string) bool {
		for _, h := range doc.Hooks[name] {
			if !strings.Contains(h.Command, "sai-verify") || matchEv[name] && h.Matcher != ".*" && h.Matcher != "^.*$" { continue }
			return h.FailClosed
		}
		return false
	}
	for _, e := range allEv {
		if good(e) { events = append(events, e) }
	}
	pre, post, stop, ok = good("preToolUse"), good("postToolUse"), good("stop"), len(events) == len(allEv)
	matcher, failClosed = ".*", ok
	return
}
func hook(in io.Reader, out io.Writer, root, evPath, baseDir, baseRef string) int {
	var raw map[string]interface{}
	if err := json.NewDecoder(in).Decode(&raw); err != nil {
		fmt.Fprintf(out, `{"permission":"deny","agent_message":"sai-verify: invalid hook json"}`+"\n")
		return 2
	}
	ev, _ := raw["hook_event_name"].(string)
	if ev == "" {
		switch {
		case raw["tool_output"] != nil: ev = "postToolUse"
		case raw["loop_count"] != nil && raw["tool_name"] == nil: ev = "stop"
		case raw["command"] != nil && raw["tool_name"] == nil: ev = "beforeShellExecution"
		case raw["session_id"] != nil && raw["tool_name"] == nil && raw["tool_input"] == nil: ev = "sessionStart"
		default: ev = "preToolUse"
		}
	}
	if root == "." || root == "" {
		if wr, _ := raw["workspace_roots"].([]interface{}); len(wr) > 0 {
			if s, ok := wr[0].(string); ok && s != "" { root = s }
		}
	}
	s, err := build(root, baseDir, root, extractPath(raw), str(raw["tool_name"]), str(raw["claimed_head"]), evPath, baseRef)
	tn, cmd := str(raw["tool_name"]), str(raw["command"])
	mut := ev == "beforeMCPExecution" || ev == "afterFileEdit" || tn == "Write" || tn == "StrReplace" || tn == "Delete" || tn == "ApplyPatch" || ev == "beforeShellExecution" && (strings.ContainsAny(cmd, ";|&`$()") || strings.TrimSpace(cmd) != "go run ./cmd/sai-verify drive" && strings.TrimSpace(cmd) != "go run ./cmd/sai-verify proof")
	ctx, deny := hookCtx(s), err != nil || !s.MapValid || !s.PreserveOK || !s.HooksOK || s.Err != "" || mut && !s.EvidenceBound
	if deny {
		fmt.Fprintf(out, `{"permission":"deny","user_message":"sai-verify failed","agent_message":%s,"additional_context":%s}`+"\n", jq(ctx), jq(ctx))
		return 2
	}
	msg := ""
	if ev == "stop" && (s.MaintRequired || !s.OK) { msg = "Verification/map-maintenance obligations remain on exact HEAD. Run /maintain-verification-skill on .cursor/skills/verify-sai and go run ./cmd/sai-verify doctor. " + ctx }
	if ev == "stop" { fmt.Fprintf(out, `{"followup_message":%s}`+"\n", jq(msg)); return 0 }
	fmt.Fprintf(out, `{"additional_context":%s}`+"\n", jq(ctx))
	return 0
}
func extractPath(raw map[string]interface{}) string {
	in, _ := raw["tool_input"].(map[string]interface{}); if in == nil { in = map[string]interface{}{} }
	for _, src := range []map[string]interface{}{in, raw} {
		for _, k := range []string{"path", "file_path", "target_file", "filePath", "target_directory", "glob", "command", "url"} { if s := str(src[k]); s != "" { return s } }
	}
	if eds, _ := raw["edits"].([]interface{}); len(eds) > 0 { if m, _ := eds[0].(map[string]interface{}); m != nil { if s := str(m["file_path"]); s != "" { return s } } }
	return ""
}
func hookCtx(s snap) string {
	const capn = 6000
	var b strings.Builder
	fmt.Fprintf(&b, "FEATURE CONTEXT\nTarget: %s %s\nContract: map_valid=%v preserve_ok=%v hooks_ok=%v\nMaintenance: %s completeness=%s %s\nRuntime: Desktop/CLI fire registered events; Cloud skips sessionStart/End, before/afterMCPExecution, workspaceOpen.\n", s.Path, s.Tool, s.MapValid, s.PreserveOK, s.HooksOK, s.MaintStatus, s.Completeness, s.MaintReason)
	for _, h := range s.Relevant {
		chunk := fmt.Sprintf("Relevant feature: %s (%s)\nWhy: %s\nImpacted capabilities: %s\nEntry points: %s\nRequired proof: %s\nGotchas: %s\n", h.Title, h.ID, h.Why, strings.Join(h.Subs, "; "), strings.Join(h.Entries, "; "), strings.Join(h.Proofs, "; "), strings.Join(h.Gotchas, "; "))
		if b.Len()+len(chunk) > capn { fmt.Fprintf(&b, "Relevant feature: %s (%s)\n", h.Title, h.ID); break }
		b.WriteString(chunk)
	}
	if b.Len() > capn { return b.String()[:capn] }
	return b.String()
}
func st(ok bool) string { if ok { return "PASS" }; return "FAIL" }
func evOK(evPath, headDir string) bool {
	ap, err := filepath.Abs(evPath); if err != nil || ap == "" { return false }
	gd := git(headDir, "rev-parse", "--absolute-git-dir"); hd, _ := filepath.Abs(headDir); tmp, _ := filepath.Abs(os.TempDir()); rt := os.Getenv("RUNNER_TEMP"); if rt != "" { rt, _ = filepath.Abs(rt) }; sep := string(filepath.Separator)
	return hd != "" && (ap == hd || strings.HasPrefix(ap, hd+sep)) || gd != "" && (ap == gd || strings.HasPrefix(ap, gd+sep)) || tmp != "" && (ap == tmp || strings.HasPrefix(ap, tmp+sep)) || rt != "" && (ap == rt || strings.HasPrefix(ap, rt+sep)) || strings.HasPrefix(ap, "/tmp/")
}
func writeProof(w io.Writer, s snap, evPath, headDir string) {
	src, _ := os.ReadFile(filepath.Join(headDir, "cmd/sai-verify/main.go"))
	audit, _ := os.ReadFile(filepath.Join(headDir, ".github/workflows/agent-audit.yml"))
	anti, _ := os.ReadFile(filepath.Join(headDir, ".github/workflows/anti-regression.yml"))
	gt, gv, pass, fail, drives := "UNEVALUATED go-test", "UNEVALUATED go-vet", interface{}(nil), interface{}(nil), []interface{}(nil)
	rp := evPath; if rp == "" { rp = filepath.Join(git(headDir, "rev-parse", "--absolute-git-dir"), "sai-verify-evidence.json") }
	if b, err := os.ReadFile(rp); err == nil { var ev map[string]interface{}; _ = json.Unmarshal(b, &ev); pass, fail = ev["pass"], ev["fail"]; if ds, _ := ev["drives"].([]interface{}); ds != nil { drives = ds; for _, d := range ds { m, _ := d.(map[string]interface{}); n, r := str(m["name"]), str(m["result"]); if strings.Contains(n, "::gotest") { gt = st(r == "PASS") + " go-test" }; if strings.Contains(n, "::govet") { gv = st(r == "PASS") + " go-vet" } } } }
	eb := "REQUIRED evidence-bound"; if s.Completeness == "proven" && s.EvidenceBound { eb = "PASS evidence-bound " + s.MaintHead + " " + s.MaintMapHash } else { gt, gv = "UNEVALUATED go-test", "UNEVALUATED go-vet" }
	wm := "UNPROVEN whole-repo-maintenance"; if s.Completeness == "proven" { wm = "PASS whole-repo-maintenance" }
	jp, art, bs := "", "FAIL proof-artifacts", "bash"; if evPath != "" { jp = filepath.Join(filepath.Dir(evPath), "sai-verify-proof.json"); if evOK(jp, headDir) { art = "PASS proof-artifacts" } }
	stt, n := git(headDir, "diff", "--shortstat", "origin/main...HEAD"), -1; if i := strings.Index(stt, "insertion"); i > 0 { fs := strings.Fields(stt[:i]); if len(fs) > 0 { fmt.Sscanf(fs[len(fs)-1], "%d", &n) } }
	lb := "UNEVALUATED line-budget"; if stt != "" && n >= 0 { if n <= 1200 { lb = fmt.Sprintf("PASS line-budget %d", n) } else { lb = fmt.Sprintf("FAIL line-budget %d", n) } }
	g := map[string]interface{}{"repo": s.Repo, "base": s.Base, "head": s.Head, "map_files": s.MapFiles, "map_features": s.MapFeatures, "map_subfeatures": s.MapSubs, "map_entry_points": s.MapEntries, "impl_files": s.ImplFiles, "impl_loc": s.ImplLOC, "impl_funcs": s.ImplFuncs, "map_parse": st(s.MapValid) + " map-parse", "hooks": st(s.HooksOK) + " hooks", "preserve": st(s.PreserveOK) + " preserve", "hook_pre": st(s.HookPre) + " hook-pre", "hook_post": st(s.HookPost) + " hook-post", "whole_repo_maintenance": wm, "maintenance_status": s.MaintStatus, "maintenance_head": s.MaintHead, "maintenance_map_hash": s.MaintMapHash, "whole_repo_completeness": s.Completeness, "evidence_bound": eb, "fail_closed_evidence": eb, "completeness_derived": st(len(s.Unmapped) == 0) + " completeness-derived", "hash_derived": "PASS hash-derived", "structured_recipes": st(!bytes.Contains(src, []byte(`"`+bs+`", "-lc"`)) && !bytes.Contains(src, []byte(`Command("`+bs+`"`))) + " structured-recipes", "trusted_base_policy": st(bytes.Contains(anti, []byte("pull_request_target")) && bytes.Contains(anti, []byte("trusted/.github/policy/anti-regression.py"))) + " trusted-base-policy", "hook_integrity": st(s.HooksOK && s.HookFailClosed) + " hook-integrity", "pinned_actions": st(regexp.MustCompile(`actions/(?:checkout|setup-go|upload-artifact)@[0-9a-f]{40}`).Match(audit)) + " pinned-actions", "adversarial_tests": gt, "go_test": gt, "go_vet": gv, "line_budget": lb, "whole_repo_map": st(len(s.Unmapped) == 0) + " whole-repo-map", "proof_artifacts": art, "density": "one parser; derived completeness/hash; no second manifest", "unreachable": s.Unreachable, "unmapped": s.Unmapped, "live_drive_pass": pass, "live_drive_fail": fail}
	fmt.Fprintf(w, "BASE %s\nHEAD %s\nrepo %s\nmap_files %d\nmap_features %d\nmap_subfeatures %d\nmap_entry_points %d\nimpl_files %d\nimpl_loc %d\nimpl_funcs %d\n%s\n%s\n%s\n%s\n%s\n%s\nmaintenance_status %s\nmaintenance_head %s\nmaintenance_map_hash %s\nwhole_repo_completeness %s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n", s.Base, s.Head, s.Repo, s.MapFiles, s.MapFeatures, s.MapSubs, s.MapEntries, s.ImplFiles, s.ImplLOC, s.ImplFuncs, g["map_parse"], g["hooks"], g["preserve"], g["hook_pre"], g["hook_post"], wm, s.MaintStatus, s.MaintHead, s.MaintMapHash, s.Completeness, eb, g["completeness_derived"], g["hash_derived"], g["structured_recipes"], g["trusted_base_policy"], g["hook_integrity"], g["pinned_actions"], lb, g["whole_repo_map"], gt, gv, art, g["density"])
	if s.Completeness == "proven" && s.EvidenceBound {
		fmt.Fprintf(w, "live-drive pass=%v fail=%v\n", pass, fail)
		for _, d := range drives { m, _ := d.(map[string]interface{}); res := str(m["result"]); if res == "" { res = str(m["Result"]) }; fmt.Fprintf(w, "%s %s %s\n", res, m["id"], m["name"]) }
	}
	for _, u := range s.Unreachable { fmt.Fprintln(w, "UNREACHABLE", u) }
	for _, u := range s.Unmapped { fmt.Fprintln(w, "UNPROVEN unmapped", u) }
	if s.Err != "" { fmt.Fprintln(w, "FAIL", s.Err) }
	if art == "PASS proof-artifacts" { b, _ := json.MarshalIndent(g, "", "  "); _ = os.WriteFile(jp, b, 0644) }
}
func relTool(f feat, tool string) bool {
	t, blob := strings.ToLower(tool), strings.ToLower(f.Desc+f.File+strings.Join(f.Ent, "")+strings.Join(f.Proof, ""))
	if strings.Contains(t, "mcp") { return strings.Contains(blob, "mcp") || f.ID == "verify-sai" }
	if strings.Contains(t, "shell") || t == "bash" { return strings.Contains(blob, "shell") || strings.Contains(blob, "scripts/") || f.ID == "verify-sai" }
	return true
}
type recipe struct{ op, read, has string; argv []string; want int; to time.Duration }
func okTok(a string) bool {
	if a == "" || a == ".." || strings.Contains(a, "/../") || strings.HasPrefix(a, "../") { return false }
	for _, c := range a { if (c < 'a' || c > 'z') && (c < 'A' || c > 'Z') && (c < '0' || c > '9') && !strings.ContainsRune("-_.=/+,:@*", c) { return false } }
	return true
}
func relPath(p string) bool { return p != "" && !filepath.IsAbs(p) && !strings.Contains(p, "..") && !strings.HasPrefix(p, "/") && okTok(p) }
func allowBin(p string) bool {
	if !relPath(p) { return false }
	for _, pre := range []string{"scripts/verify-", "openclaw-dashboard/scripts/verify-", "openclaw-dashboard/tests/smoke/"} { if r := strings.TrimPrefix(p, pre); r != p && !strings.Contains(r, "/") { return true } }
	switch p { case "scripts/agent-report", "scripts/agent-sync-drive", "scripts/agent-contract-pr-review", "scripts/agent-verify-caps": return true }
	return false
}
func parseRecipe(p string) (recipe, error) {
	i := strings.Index(p, "::")
	if i < 0 { return recipe{}, fmt.Errorf("unstructured") }
	pre, j := strings.TrimSpace(p[:i]), strings.LastIndex(strings.TrimSpace(p[:i]), "**")
	if pre != "" && !(strings.HasPrefix(pre, "**") && strings.Count(pre, "**") >= 2 && j >= 0 && (strings.TrimSpace(pre[j+2:]) == "" || strings.TrimSpace(pre[j+2:]) == ".")) { return recipe{}, fmt.Errorf("unstructured") }
	fs := strings.Fields(p[i+2:])
	if len(fs) == 0 { return recipe{}, fmt.Errorf("empty") }
	r := recipe{op: fs[0], to: 60 * time.Second}
	for _, t := range fs[1:] {
		if strings.HasPrefix(t, "expect=") { fmt.Sscanf(t[7:], "%d", &r.want); continue }
		if strings.HasPrefix(t, "timeout=") { n := 0; fmt.Sscanf(t[8:], "%d", &n); if n <= 0 { r.to = time.Millisecond } else { r.to = time.Duration(n) * time.Second }; continue }
		if strings.HasPrefix(t, "read=") { r.read = t[5:]; continue }; if strings.HasPrefix(t, "has=") { r.has = t[4:]; continue }
		r.argv = append(r.argv, t)
	}
	return r, r.err()
}
func (r recipe) err() error {
	n, a0 := len(r.argv), ""; if n > 0 { a0 = r.argv[0] }
	tok := true; for _, a := range r.argv { if !okTok(a) { tok = false } }
	switch r.op {
	case "exists":
		if n == 0 { return fmt.Errorf("exists") }
		for _, a := range r.argv { if !relPath(a) { return fmt.Errorf("path") } }
	case "contains":
		if n < 2 || !relPath(a0) || !tok { return fmt.Errorf("contains") }
	case "json":
		if n != 1 || !relPath(a0) { return fmt.Errorf("json") }
	case "exec":
		if n == 0 || !allowBin(a0) || a0 == "scripts/agent-report" && (r.read == "" || !relPath(r.read)) { return fmt.Errorf("bin") }
		for _, a := range r.argv[1:] { if !okTok(a) { return fmt.Errorf("arg") } }
	case "py":
		if n == 0 || !relPath(a0) || !strings.HasSuffix(a0, ".py") || (!strings.HasPrefix(a0, ".github/") && !strings.HasPrefix(a0, "scripts/")) { return fmt.Errorf("py") }
		for _, a := range r.argv { if a == "-c" || !okTok(a) { return fmt.Errorf("py") } }
	case "gotest":
		for _, a := range r.argv { if a != "-race" && a != "./..." && !strings.HasPrefix(a, "./cmd/") && a != "-count=1" && !strings.HasPrefix(a, "-timeout=") { return fmt.Errorf("go") } }
	case "govet":
		for _, a := range r.argv { if a != "./..." && !strings.HasPrefix(a, "./cmd/") { return fmt.Errorf("vet") } }
	case "sai":
		if n == 0 { return fmt.Errorf("sai") }
		switch a0 { case "snapshot", "proof", "doctor", "relevant", "preserve": default: return fmt.Errorf("sai") }
		for _, a := range r.argv[1:] { if !okTok(a) { return fmt.Errorf("sai") } }
	default:
		return fmt.Errorf("op")
	}
	return nil
}
func recipeEnv(tmp string) []string {
	env := []string{"PATH=" + os.Getenv("PATH"), "HOME=" + tmp, "LANG=C", "CI=true", "SAI_CI_STRICT_CONTRACTS=1", "SAI_CI_REQUIRE_SDK_SMOKE=0", "GOTOOLCHAIN=local", "GOCACHE=" + filepath.Join(tmp, "gc"), "TMPDIR=" + tmp}
	for _, k := range []string{"GOROOT", "GOPATH", "GOMODCACHE"} { if v := os.Getenv(k); v != "" { env = append(env, k+"="+v) } }; return env
}
func runRecipe(r recipe, dir string) (code int, stdout, stderr, note string) {
	if e := r.err(); e != nil { return 1, "", "", e.Error() }
	switch r.op {
	case "exists":
		for _, p := range r.argv { if _, err := os.Stat(filepath.Join(dir, p)); err != nil { return 1, "", err.Error(), "missing" } }
		return 0, "", "", ""
	case "contains":
		b, err := os.ReadFile(filepath.Join(dir, r.argv[0])); if err != nil { return 1, "", err.Error(), "read" }
		if !strings.Contains(string(b), strings.Join(r.argv[1:], " ")) { return 1, "", "", "needle" }
		return 0, "", "", ""
	case "sai":
		var o, e bytes.Buffer; return run(append(append([]string{}, r.argv...), "--root", dir), bytes.NewReader(nil), &o, &e), o.String(), e.String(), ""
	}
	ctx, cancel := context.WithTimeout(context.Background(), r.to); defer cancel()
	tmp, _ := os.MkdirTemp("", "sai-r-"); defer os.RemoveAll(tmp)
	argv := r.argv
	switch r.op {
	case "json": argv = []string{"python3", "-m", "json.tool", r.argv[0]}
	case "py": argv = append([]string{"python3"}, r.argv...)
	case "gotest": argv = append([]string{"go", "test"}, r.argv...)
	case "govet": argv = append([]string{"go", "vet"}, r.argv...)
	case "exec":
	default: return 1, "", "", "op"
	}
	c := exec.CommandContext(ctx, argv[0], argv[1:]...); c.Dir, c.Env = dir, recipeEnv(tmp)
	var o, e bytes.Buffer; var before []os.DirEntry; c.Stdout, c.Stderr = &o, &e; if r.read != "" { before, _ = os.ReadDir(filepath.Join(dir, r.read)) }
	err := c.Run()
	if ctx.Err() == context.DeadlineExceeded { return 1, o.String(), e.String(), "timeout" }
	if err != nil { if ee, ok := err.(*exec.ExitError); ok { code = ee.ExitCode() } else { code = 1 } } else if r.read != "" { after, _ := os.ReadDir(filepath.Join(dir, r.read)); seen := map[string]bool{}; for _, de := range before { seen[de.Name()] = true }; hit := false; for _, de := range after { if seen[de.Name()] { continue }; b, _ := os.ReadFile(filepath.Join(dir, r.read, de.Name())); if r.has == "" || bytes.Contains(b, []byte(r.has)) { hit = true; break } }; if !hit { return 1, o.String(), e.String(), "unread" } }
	return code, o.String(), e.String(), ""
}
func driveCmd(s snap, headDir, evPath string, out io.Writer) int {
	fs, _ := loadFeats(headDir); rows, pass, fail := []map[string]string{}, 0, 0
	for _, f := range fs {
		for _, p := range f.Proof {
			rec, err := parseRecipe(p); so, se, note, code, res := "", "", "", 1, "FAIL"
			if err != nil { note, fail = err.Error(), fail+1 } else { code, so, se, note = runRecipe(rec, headDir); if code == rec.want { res, pass = "PASS", pass+1 } else { fail++ } }
			rows = append(rows, map[string]string{"id": f.ID, "name": p, "result": res, "stdout": so, "stderr": se, "note": note, "exit": fmt.Sprintf("%d", code)})
		}
	}
	sweep := "dirty"; if len(s.Unmapped) == 0 { sweep = "clean" }
	if evPath == "" { if gd := git(headDir, "rev-parse", "--absolute-git-dir"); gd != "" { evPath = filepath.Join(gd, "sai-verify-evidence.json") } else { evPath = "sai-verify-evidence.json" } }
	b, _ := json.MarshalIndent(map[string]interface{}{"repo": s.Repo, "base": s.Base, "head": s.Head, "map_hash": mapHash(headDir), "sweep": sweep, "unmapped": s.Unmapped, "pass": pass, "fail": fail, "skip": 0, "unreachable": s.Unreachable, "drives": rows}, "", "  ")
	if !evOK(evPath, headDir) { fmt.Fprintln(out, `{"error":"evidence path"}`); return 1 }; _ = os.WriteFile(evPath, b, 0644); fmt.Fprintln(out, string(b)); if fail > 0 { return 1 }; return 0
}
func unreachable(fs []feat) []string {
	var u []string
	for _, f := range fs { u = append(u, f.Unreach...); for _, s := range f.Subs { if strings.Contains(strings.ToLower(s[1]), "stub exit 2") { u = append(u, s[0]+": "+s[1]) } } }
	return uniq(u)
}
func repoName(u string) string {
	u = strings.TrimSuffix(u, ".git")
	if i := strings.LastIndex(u, "github.com/"); i >= 0 { return strings.TrimPrefix(u[i+11:], "/") }
	if u == "" { return "Dezocode/Sai" }
	return u
}
func git(dir string, args ...string) string {
	b, _ := exec.Command("git", append([]string{"-c", "safe.directory=*", "-C", dir}, args...)...).Output()
	return strings.TrimSpace(string(b))
}
func uniq(in []string) []string {
	seen, o := map[string]bool{}, []string{}
	for _, s := range in {
		if s = strings.TrimSpace(s); s == "" || seen[s] { continue }
		seen[s], o = true, append(o, s)
	}
	return o
}
func str(v interface{}) string { s, _ := v.(string); return s }
func jq(s string) string       { b, _ := json.Marshal(s); return string(b) }
