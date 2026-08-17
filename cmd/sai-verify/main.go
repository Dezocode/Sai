package main
import (
	"bufio"
	"bytes"
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
)
const mapDir = ".cursor/skills/verify-sai/features"
var (
	linkRe  = regexp.MustCompile(`\]\((?:\./)?([^)]+\.md)\)`)
	idRe    = regexp.MustCompile("`([a-z][a-z0-9-]*)`")
	pathRe  = regexp.MustCompile(`(?:\./)?(?:\.ai|\.cursor|\.github|\.githooks|scripts|openclaw-dashboard|cmd)(/[A-Za-z0-9_.*{}-]+)+|(?:AGENTS|CLAUDE|CODEX|OPENCLAW|README|Team)\.md|go\.mod`)
	rmRe    = regexp.MustCompile(`(?i)^Removal-authorized:\s*(.+)$`)
	h2Re    = regexp.MustCompile(`^## `)
	tickRe  = regexp.MustCompile("`([^`]+)`")
	allEv   = []string{"sessionStart", "sessionEnd", "preToolUse", "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop", "beforeShellExecution", "afterShellExecution", "beforeMCPExecution", "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt", "preCompact", "stop", "afterAgentResponse", "afterAgentThought", "workspaceOpen"}
	matchEv = map[string]bool{"preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "beforeShellExecution": true, "afterShellExecution": true, "beforeReadFile": true, "afterFileEdit": true, "subagentStart": true, "subagentStop": true}
	failEv  = map[string]bool{"sessionStart": true, "preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "subagentStart": true, "beforeShellExecution": true, "beforeMCPExecution": true, "beforeReadFile": true, "beforeSubmitPrompt": true, "workspaceOpen": true}
)
type feat struct {
	ID, Title, File, Desc string
	Subs [][2]string
	Ent, Proof, Paths, Rm, Unreach []string
}
type hit struct {
	ID      string   `json:"id"`
	Subs    []string `json:"subs"`
	Entries []string `json:"entries"`
	Proofs  []string `json:"proofs"`
}
type snap struct {
	Repo string `json:"repo"`
	Base string `json:"base"`
	Head string `json:"head"`
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
	Relevant []hit `json:"relevant"`
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
			if i+1 < len(args) {
				i++
				*p = args[i]
				evSet = evSet || a == "--evidence"
			}
			continue
		}
		if strings.HasPrefix(a, "-") {
			fmt.Fprintf(errw, "unknown flag %s\n", a)
			return 2
		}
		cmd = a
	}
	if headDir == "" { headDir = root }
	if cmd == "hook" { return hook(in, out, root, evPath) }
	s, ferr := build(root, baseDir, headDir, path, tool, wantHead, evPath, baseRef)
	if ferr != nil && s.Err == "" { s.Err, s.OK = ferr.Error(), false }
	if cmd == "drive" { return driveCmd(s, headDir, evPath, out) }
	if cmd == "proof" {
		writeProof(out, s, evPath, headDir)
	} else if cmd == "relevant" {
		_ = json.NewEncoder(out).Encode(s.Relevant)
	} else if cmd != "preserve" {
		_ = json.NewEncoder(out).Encode(s)
	} else if s.PreserveOK { fmt.Fprintln(out, "preserve_ok") }
	if cmd == "preserve" && !s.PreserveOK || cmd == "doctor" && (!s.MapValid || !s.HooksOK || s.Err != "" || evSet && s.Completeness != "proven") || cmd != "doctor" && cmd != "preserve" && cmd != "relevant" && !s.OK { return 1 }
	return 0
}
func build(root, baseDir, headDir, path, tool, claimed, evPath, baseRef string) (snap, error) {
	s := snap{PreserveOK: true, Repo: repoName(git(headDir, "config", "--get", "remote.origin.url")), Head: git(headDir, "rev-parse", "HEAD")}
	if s.Base = baseRef; s.Base == "" { s.Base = git(headDir, "merge-base", "HEAD", "origin/main") }
	if s.Base == "" { s.Base = "unavailable" }
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
	for _, e := range ents {
		if !e.IsDir() && e.Name() != "README.md" && strings.HasSuffix(e.Name(), ".md") { onDisk[e.Name()] = true }
	}
	for _, name := range indexed {
		if seenIdx[name] { probs = append(probs, "duplicate index "+name) }
		seenIdx[name] = true
		if !onDisk[name] { probs = append(probs, "dead index "+name); continue }
		f, p := parseFeat(filepath.Join(dir, name), strings.TrimSuffix(name, ".md"))
		probs, fs = append(probs, p...), append(fs, f)
	}
	for name := range onDisk {
		if !seenIdx[name] { probs = append(probs, "unindexed "+name) }
	}
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
	h := sha256.New()
	filepath.Walk(filepath.Join(dir, mapDir), func(p string, inf os.FileInfo, err error) error {
		if err == nil && inf != nil && !inf.IsDir() {
			b, _ := os.ReadFile(p)
			h.Write(b)
		}
		return nil
	})
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
	s.MaintHead, s.MaintMapHash, s.EvidenceBound, s.MaintStatus = head, mh, true, "stale"
	_, hasFail := ev["fail"]
	_, hasPass := ev["pass"]
	n, _ := ev["fail"].(float64)
	um, _ := ev["unmapped"].([]interface{})
	switch {
	case repo != "" && s.Repo != "" && repo != s.Repo:
		s.MaintReason = "evidence repo mismatch"
	case head != s.Head:
		s.MaintReason = "evidence HEAD mismatch"
	case mh != mapHash(headDir):
		s.MaintReason = "evidence map hash mismatch"
	case !hasFail || !hasPass || sweep == "":
		s.MaintReason = "incomplete evidence"
	case sweep != "clean" || len(um) > 0:
		s.MaintStatus, s.MaintReason = "incomplete", "source sweep not clean"
	case n != 0:
		s.MaintStatus, s.MaintReason = "bound", "live-drive failures"
	default:
		s.MaintStatus, s.MaintRequired, s.MaintReason, s.Completeness = "bound", false, "", "proven"
	}
}
func watch(f string) bool {
	if strings.HasPrefix(f, "cmd/") { return strings.HasSuffix(f, ".go") }
	for _, p := range []string{"scripts/", ".githooks/", ".github/workflows/", ".github/policy/", ".ai/shared/schemas/", ".ai/_config/", ".ai/contracts/_templates/", ".cursor/hooks", ".cursor/rules/", "openclaw-dashboard/scripts/", "openclaw-dashboard/tests/smoke/"} {
		if strings.HasPrefix(f, p) { return true }
	}
	switch f {
	case "AGENTS.md", "CLAUDE.md", "CODEX.md", "OPENCLAW.md", "README.md", "Team.md", "go.mod", ".cursor/hooks.json", ".cursor/settings.json", ".ai/CONTEXT.md", ".ai/INITIALIZE.md", ".ai/ONBOARDING.md":
		return true
	}
	return false
}
func unmapped(root string, fs []feat) []string {
	blob := git(root, "ls-files", "-z")
	if blob == "" { return nil }
	var b strings.Builder
	var prefs []string
	for _, f := range fs {
		b.WriteString(f.Desc + strings.Join(f.Ent, "") + strings.Join(f.Proof, "") + strings.Join(f.Paths, ""))
		for _, s := range f.Subs { b.WriteString(s[1]) }
		for _, p := range f.Paths {
			if i := strings.IndexAny(p, "*?{"); i > 1 { prefs = append(prefs, filepath.Clean(p[:i])) }
		}
	}
	mapped := b.String()
	var miss []string
	for _, f := range strings.Split(blob, "\x00") {
		if f == "" || !watch(f) { continue }
		hit := strings.Contains(mapped, f) || strings.Contains(mapped, filepath.Base(f))
		if !hit {
			for _, p := range prefs {
				if p != "." && (f == p || strings.HasPrefix(f, p+"/")) { hit = true; break }
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
			if len(ticks(line)) > 0 { f.Proof = append(f.Proof, strings.TrimSpace(line[1:])) }
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
		if has(f.ID) && (lost(subIDs(f), subIDs(hf)) || lost(f.Ent, hf.Ent) || lost(f.Proof, hf.Proof)) { weakened = append(weakened, f.ID) }
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
		h := hit{ID: f.ID, Entries: f.Ent, Proofs: f.Proof}
		for _, s := range f.Subs { h.Subs = append(h.Subs, s[0]) }
		if f.ID == "verify-sai" { fb = h }
		ok := path == "" && tool == "" && f.ID == "verify-sai"
		for _, p := range f.Paths {
			p = strings.ToLower(strings.TrimPrefix(p, "./"))
			if p == "" { continue }
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
			return !failEv[name] || h.FailClosed
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
func hook(in io.Reader, out io.Writer, root, evPath string) int {
	var raw map[string]interface{}
	if err := json.NewDecoder(in).Decode(&raw); err != nil {
		fmt.Fprintf(out, `{"permission":"deny","agent_message":"sai-verify: invalid hook json"}`+"\n")
		return 2
	}
	ev, _ := raw["hook_event_name"].(string)
	if ev == "" {
		switch {
		case raw["tool_output"] != nil:
			ev = "postToolUse"
		case raw["loop_count"] != nil && raw["tool_name"] == nil:
			ev = "stop"
		case raw["command"] != nil && raw["tool_name"] == nil:
			ev = "beforeShellExecution"
		case raw["session_id"] != nil && raw["tool_name"] == nil && raw["tool_input"] == nil:
			ev = "sessionStart"
		default:
			ev = "preToolUse"
		}
	}
	if root == "." || root == "" {
		if wr, _ := raw["workspace_roots"].([]interface{}); len(wr) > 0 {
			if s, ok := wr[0].(string); ok && s != "" { root = s }
		}
	}
	s, err := build(root, "", root, extractPath(raw), str(raw["tool_name"]), str(raw["claimed_head"]), evPath, "")
	ctx, deny := hookCtx(s), err != nil || !s.MapValid || !s.PreserveOK || !s.HooksOK || s.Err != ""
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
	in, _ := raw["tool_input"].(map[string]interface{})
	if in == nil { in = map[string]interface{}{} }
	for _, src := range []map[string]interface{}{in, raw} {
		for _, k := range []string{"path", "file_path", "target_file", "filePath", "target_directory", "glob", "command", "url"} {
			if s := str(src[k]); s != "" { return s }
		}
	}
	if eds, _ := raw["edits"].([]interface{}); len(eds) > 0 {
		if m, _ := eds[0].(map[string]interface{}); m != nil {
			if s := str(m["file_path"]); s != "" { return s }
		}
	}
	return ""
}
func hookCtx(s snap) string {
	rel := make([]string, 0, len(s.Relevant))
	for _, h := range s.Relevant { rel = append(rel, h.ID) }
	b, _ := json.Marshal(map[string]interface{}{
		"repo": s.Repo, "base": s.Base, "head": s.Head, "ok": s.OK, "map_valid": s.MapValid, "preserve_ok": s.PreserveOK, "hooks_ok": s.HooksOK,
		"hook_pre": s.HookPre, "hook_post": s.HookPost, "hook_stop": s.HookStop, "hook_fail_closed": s.HookFailClosed, "hook_events": s.HookEvents,
		"maintenance_required": s.MaintRequired, "maintenance_status": s.MaintStatus, "whole_repo_completeness": s.Completeness,
		"map_files": s.MapFiles, "map_subfeatures": s.MapSubs, "map_entry_points": s.MapEntries,
		"relevant": rel, "obligations": s.Obligations, "missing": s.Missing, "unreachable": s.Unreachable, "impl_loc": s.ImplLOC, "impl_funcs": s.ImplFuncs,
	})
	return string(b)
}
func st(ok bool) string { if ok { return "PASS" }; return "FAIL" }
func writeProof(w io.Writer, s snap, evPath, headDir string) {
	fmt.Fprintf(w, "BASE %s\nHEAD %s\nrepo %s\n%s map-parse\n%s hooks\n%s preserve\n", s.Base, s.Head, s.Repo, st(s.MapValid), st(s.HooksOK), st(s.PreserveOK))
	if s.Completeness == "proven" { fmt.Fprintln(w, "PASS whole-repo-maintenance") } else { fmt.Fprintln(w, "UNPROVEN whole-repo-maintenance") }
	fmt.Fprintf(w, "maintenance_status %s\nmaintenance_head %s\nmaintenance_map_hash %s\nwhole_repo_completeness %s\n", s.MaintStatus, s.MaintHead, s.MaintMapHash, s.Completeness)
	if !s.EvidenceBound {
		fmt.Fprintln(w, "REQUIRED evidence-bound\nUNEVALUATED go-test\nUNEVALUATED go-vet")
	} else {
		fmt.Fprintf(w, "PASS evidence-bound %s %s\n", s.MaintHead, s.MaintMapHash)
		if evPath == "" { evPath = filepath.Join(git(headDir, "rev-parse", "--absolute-git-dir"), "sai-verify-evidence.json") }
		if b, err := os.ReadFile(evPath); err == nil {
			var ev map[string]interface{}
			_ = json.Unmarshal(b, &ev)
			fmt.Fprintf(w, "live-drive pass=%v fail=%v\n", ev["pass"], ev["fail"])
			if ds, _ := ev["drives"].([]interface{}); ds != nil {
				for _, d := range ds {
					m, _ := d.(map[string]interface{})
					res := str(m["result"])
					if res == "" { res = str(m["Result"]) }
					fmt.Fprintf(w, "%s %s %s\n", res, m["id"], m["name"])
				}
			}
		}
	}
	for _, u := range s.Unreachable { fmt.Fprintln(w, "UNREACHABLE", u) }
	for _, u := range s.Unmapped { fmt.Fprintln(w, "UNPROVEN unmapped", u) }
	if s.Err != "" { fmt.Fprintln(w, "FAIL", s.Err) }
}
func relTool(f feat, tool string) bool {
	t, blob := strings.ToLower(tool), strings.ToLower(f.Desc+f.File+strings.Join(f.Ent, "")+strings.Join(f.Proof, ""))
	if strings.Contains(t, "mcp") { return strings.Contains(blob, "mcp") || f.ID == "verify-sai" }
	if strings.Contains(t, "shell") || t == "bash" { return strings.Contains(blob, "shell") || strings.Contains(blob, "scripts/") || f.ID == "verify-sai" }
	return true
}
func ticks(line string) (o []string) {
	for _, m := range tickRe.FindAllStringSubmatch(line, -1) {
		s := m[1]
		if strings.Contains(s, "/") || strings.HasPrefix(s, "go ") || strings.HasPrefix(s, "test ") || strings.HasPrefix(s, "python") || strings.HasPrefix(s, "bash ") || strings.HasPrefix(s, "printf") || strings.HasPrefix(s, "grep ") || strings.HasPrefix(s, "SAI_") { o = append(o, s) }
	}
	return
}
func driveCmd(s snap, headDir, evPath string, out io.Writer) int {
	fs, _ := loadFeats(headDir)
	rows, pass, fail, skip := []map[string]string{}, 0, 0, 0
	for _, f := range fs {
		for _, p := range f.Proof {
			want, cmds := 0, ticks(p)
			if strings.Contains(strings.ToLower(p), "expect exit 2") { want = 2 }
			if len(cmds) == 0 { skip++; rows = append(rows, map[string]string{"id": f.ID, "name": p, "result": "SKIP"}); continue }
			okAll, last := true, ""
			for _, last = range cmds {
				c := exec.Command("bash", "-lc", last)
				c.Dir = headDir
				code := 0
				if err := c.Run(); err != nil {
					if ee, ok := err.(*exec.ExitError); ok { code = ee.ExitCode() } else { code = 1 }
				}
				if code != want {
					okAll, fail = false, fail+1
					rows = append(rows, map[string]string{"id": f.ID, "name": p, "cmd": last, "result": "FAIL", "note": fmt.Sprintf("exit %d", code)})
					break
				}
			}
			if okAll { pass++; rows = append(rows, map[string]string{"id": f.ID, "name": p, "cmd": last, "result": "PASS"}) }
		}
	}
	sweep := "dirty"
	if len(s.Unmapped) == 0 { sweep = "clean" }
	if evPath == "" {
		if gd := git(headDir, "rev-parse", "--absolute-git-dir"); gd != "" { evPath = filepath.Join(gd, "sai-verify-evidence.json") } else { evPath = "sai-verify-evidence.json" }
	}
	b, _ := json.MarshalIndent(map[string]interface{}{"repo": s.Repo, "base": s.Base, "head": s.Head, "map_hash": mapHash(headDir), "sweep": sweep, "unmapped": s.Unmapped, "pass": pass, "fail": fail, "skip": skip, "unreachable": s.Unreachable, "drives": rows}, "", "  ")
	_ = os.WriteFile(evPath, b, 0644)
	fmt.Fprintln(out, string(b))
	if fail > 0 { return 1 }
	return 0
}
func unreachable(fs []feat) []string {
	var u []string
	for _, f := range fs {
		u = append(u, f.Unreach...)
		for _, s := range f.Subs {
			if strings.Contains(strings.ToLower(s[1]), "stub exit 2") { u = append(u, s[0]+": "+s[1]) }
		}
	}
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
