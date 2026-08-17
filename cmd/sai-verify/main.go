package main

import (
	"bufio"
	"bytes"
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
	permEv  = map[string]bool{"preToolUse": true, "beforeShellExecution": true, "beforeMCPExecution": true, "beforeReadFile": true, "subagentStart": true, "beforeSubmitPrompt": true}
	matchEv = map[string]bool{"preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "beforeShellExecution": true, "afterShellExecution": true, "beforeReadFile": true, "afterFileEdit": true, "subagentStart": true, "subagentStop": true}
	failEv  = map[string]bool{"sessionStart": true, "preToolUse": true, "postToolUse": true, "postToolUseFailure": true, "subagentStart": true, "beforeShellExecution": true, "beforeMCPExecution": true, "beforeReadFile": true, "beforeSubmitPrompt": true, "workspaceOpen": true}
)

type feat struct {
	ID, Title, File, Desc          string
	Subs                           [][2]string
	Ent, Proof, Paths, Rm, Unreach []string
}
type hit struct {
	ID      string   `json:"id"`
	Subs    []string `json:"subs"`
	Entries []string `json:"entries"`
	Proofs  []string `json:"proofs"`
}
type snap struct {
	Repo           string   `json:"repo"`
	Base           string   `json:"base"`
	Head           string   `json:"head"`
	Dirty          bool     `json:"dirty"`
	OK             bool     `json:"ok"`
	Err            string   `json:"err,omitempty"`
	MapValid       bool     `json:"map_valid"`
	MapFiles       int      `json:"map_files"`
	MapFeatures    int      `json:"map_features"`
	MapSubs        int      `json:"map_subfeatures"`
	MapEntries     int      `json:"map_entry_points"`
	IDs            []string `json:"ids"`
	Problems       []string `json:"problems,omitempty"`
	PreserveOK     bool     `json:"preserve_ok"`
	Missing        []string `json:"missing,omitempty"`
	Weakened       []string `json:"weakened,omitempty"`
	Relevant       []hit    `json:"relevant"`
	HooksOK        bool     `json:"hooks_ok"`
	HookPre        bool     `json:"hook_pre"`
	HookPost       bool     `json:"hook_post"`
	HookStop       bool     `json:"hook_stop"`
	HookMatcher    string   `json:"hook_matcher"`
	HookFailClosed bool     `json:"hook_fail_closed"`
	HookEvents     []string `json:"hook_events"`
	MaintRequired  bool     `json:"maintenance_required"`
	MaintReason    string   `json:"maintenance_reason,omitempty"`
	Obligations    []string `json:"obligations"`
	Unreachable    []string `json:"unreachable"`
	ImplFiles      int      `json:"impl_files"`
	ImplLOC        int      `json:"impl_loc"`
	ImplFuncs      int      `json:"impl_funcs"`
}

func main() { os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr)) }

func run(args []string, in io.Reader, out, errw io.Writer) int {
	cmd, root, baseDir, headDir, path, tool, wantHead := "snapshot", ".", "", "", "", "", ""
	set := map[string]*string{"--root": &root, "--base": &baseDir, "--head": &headDir, "--path": &path, "--tool": &tool, "--claimed-head": &wantHead}
	for i := 0; i < len(args); i++ {
		a := args[i]
		if p, ok := set[a]; ok {
			if i+1 < len(args) {
				i++
				*p = args[i]
			}
			continue
		}
		if strings.HasPrefix(a, "-") {
			fmt.Fprintf(errw, "unknown flag %s\n", a)
			return 2
		}
		cmd = a
	}
	if headDir == "" {
		headDir = root
	}
	if baseDir == "" {
		baseDir = headDir
	}
	if cmd == "hook" {
		return hook(in, out, root)
	}
	if cmd != "snapshot" && cmd != "proof" && cmd != "doctor" && cmd != "relevant" && cmd != "preserve" {
		fmt.Fprintf(errw, "usage: sai-verify snapshot|proof|doctor|relevant|preserve|hook\n")
		return 2
	}
	s, ferr := build(root, baseDir, headDir, path, tool, wantHead)
	if ferr != nil && s.Err == "" {
		s.Err, s.OK = ferr.Error(), false
	}
	if cmd == "proof" {
		writeProof(out, s)
	} else {
		_ = json.NewEncoder(out).Encode(s)
	}
	if !s.OK || cmd == "doctor" && (!s.MapValid || !s.HooksOK) || cmd == "preserve" && !s.PreserveOK {
		return 1
	}
	return 0
}

func build(root, baseDir, headDir, path, tool, claimed string) (snap, error) {
	s := snap{PreserveOK: true, Repo: repoName(git(headDir, "config", "--get", "remote.origin.url")), Head: git(headDir, "rev-parse", "HEAD")}
	s.Base = git(headDir, "merge-base", "HEAD", "origin/main")
	if s.Base == "" {
		s.Base = git(headDir, "rev-parse", "HEAD^")
	}
	if s.Base == "" {
		s.Base = s.Head
	}
	s.Dirty = git(headDir, "status", "--porcelain") != ""
	if claimed != "" && claimed != s.Head {
		s.OK, s.Err = false, "stale head: claimed "+claimed+" current "+s.Head
		return s, fmt.Errorf("%s", s.Err)
	}
	hf, hp := loadFeats(headDir)
	fillMap(&s, hf, hp)
	s.HooksOK, s.HookPre, s.HookPost, s.HookStop, s.HookMatcher, s.HookFailClosed, s.HookEvents = checkHooks(headDir)
	if !s.HooksOK {
		s.Problems = append(s.Problems, "hooks missing full sai-verify agent event set fail-closed")
	}
	bf, _ := loadFeats(baseDir)
	s.Missing, s.Weakened = preserve(bf, hf)
	s.PreserveOK = len(s.Missing)+len(s.Weakened) == 0
	s.Relevant, s.Unreachable = relevant(hf, path, tool), unreachable(hf)
	if b, err := os.ReadFile(filepath.Join(headDir, "cmd/sai-verify/main.go")); err == nil {
		s.ImplFiles, s.ImplLOC, s.ImplFuncs = 1, bytes.Count(b, []byte("\n")), bytes.Count(b, []byte("\nfunc "))
	}
	s.Obligations = obligations(s)
	s.MaintRequired = !s.MapValid || !s.PreserveOK || !s.HooksOK || s.Dirty && strings.Contains(git(headDir, "status", "--porcelain"), "verify-sai")
	if s.MaintRequired {
		s.MaintReason = strings.Join(s.Problems, "; ")
		if s.MaintReason == "" {
			s.MaintReason = map[bool]string{true: "preserve failed", false: "map or hooks need maintenance"}[!s.PreserveOK]
		}
	}
	s.OK = s.MapValid && s.PreserveOK && s.HooksOK && s.Err == ""
	return s, nil
}

func fillMap(s *snap, fs []feat, probs []string) {
	s.MapFiles, s.MapFeatures = len(fs), len(fs)
	seen := map[string]bool{}
	for _, f := range fs {
		if seen[f.ID] {
			probs = append(probs, "duplicate id "+f.ID)
		}
		seen[f.ID], s.IDs, s.MapSubs, s.MapEntries = true, append(s.IDs, f.ID), s.MapSubs+len(f.Subs), s.MapEntries+len(f.Ent)
		for _, sub := range f.Subs {
			if seen[sub[0]] {
				probs = append(probs, "duplicate id "+sub[0])
			}
			seen[sub[0]], s.IDs = true, append(s.IDs, sub[0])
		}
	}
	sort.Strings(s.IDs)
	s.Problems, s.MapValid = uniq(probs), len(uniq(probs)) == 0 && len(fs) > 0
}

func loadFeats(root string) ([]feat, []string) {
	dir := filepath.Join(root, mapDir)
	b, err := os.ReadFile(filepath.Join(dir, "README.md"))
	if err != nil {
		return nil, []string{"missing " + filepath.Join(dir, "README.md")}
	}
	var indexed []string
	inFeat := false
	sc := bufio.NewScanner(bytes.NewReader(b))
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "## Features") {
			inFeat = true
			continue
		}
		if inFeat && strings.HasPrefix(line, "## ") {
			break
		}
		if inFeat {
			if m := linkRe.FindStringSubmatch(line); len(m) > 1 {
				indexed = append(indexed, m[1])
			}
		}
	}
	ents, _ := os.ReadDir(dir)
	onDisk, seenIdx, fs, probs := map[string]bool{}, map[string]bool{}, []feat{}, []string{}
	for _, e := range ents {
		if !e.IsDir() && e.Name() != "README.md" && strings.HasSuffix(e.Name(), ".md") {
			onDisk[e.Name()] = true
		}
	}
	for _, name := range indexed {
		if seenIdx[name] {
			probs = append(probs, "duplicate index "+name)
		}
		seenIdx[name] = true
		if !onDisk[name] {
			probs = append(probs, "dead index "+name)
			continue
		}
		f, p := parseFeat(filepath.Join(dir, name), strings.TrimSuffix(name, ".md"))
		probs, fs = append(probs, p...), append(fs, f)
	}
	for name := range onDisk {
		if !seenIdx[name] {
			probs = append(probs, "unindexed "+name)
		}
	}
	return fs, probs
}

func parseFeat(path, id string) (feat, []string) {
	b, err := os.ReadFile(path)
	f := feat{ID: id, File: filepath.Base(path)}
	if err != nil {
		return f, []string{"read " + path}
	}
	var probs []string
	sec := ""
	sc := bufio.NewScanner(bytes.NewReader(b))
	for sc.Scan() {
		line := sc.Text()
		low := strings.ToLower(line)
		if strings.Contains(low, "stub exit 2") || strings.Contains(low, "verified-unreachable") || strings.Contains(low, "requires openclaw") {
			f.Unreach = append(f.Unreach, strings.TrimSpace(strings.TrimPrefix(line, "- ")))
		}
		if strings.HasPrefix(line, "# ") && f.Title == "" {
			f.Title = strings.TrimSpace(line[2:])
			continue
		}
		if m := rmRe.FindStringSubmatch(line); len(m) > 1 {
			for _, p := range strings.Split(m[1], ",") {
				if p = strings.TrimSpace(p); p != "" && p != "(none)" {
					f.Rm = append(f.Rm, p)
				}
			}
		}
		if h2Re.MatchString(line) {
			sec = strings.TrimSpace(line[3:])
			continue
		}
		switch {
		case f.Desc == "" && line != "" && !strings.HasPrefix(line, "#") && sec == "":
			f.Desc = line
		case strings.HasPrefix(sec, "Sub-features") && strings.HasPrefix(line, "-"):
			ids := idRe.FindAllStringSubmatch(line, -1)
			if len(ids) == 0 {
				probs = append(probs, f.ID+": sub-feature missing id")
				continue
			}
			f.Subs = append(f.Subs, [2]string{ids[0][1], strings.TrimSpace(idRe.ReplaceAllString(line[1:], ""))})
		case strings.HasPrefix(sec, "How to get to it") && strings.HasPrefix(line, "-"):
			f.Ent = append(f.Ent, strings.TrimSpace(strings.TrimPrefix(line, "-")))
		case strings.HasPrefix(sec, "Driving it"):
			for _, m := range tickRe.FindAllStringSubmatch(line, -1) {
				if strings.ContainsAny(m[1], " /") || strings.HasPrefix(m[1], "go ") || strings.HasPrefix(m[1], "scripts/") {
					f.Proof = append(f.Proof, m[1])
				}
			}
		}
	}
	f.Paths = uniq(pathRe.FindAllString(string(b), -1))
	if f.Title == "" || f.Desc == "" || len(f.Subs) == 0 || len(f.Ent) == 0 {
		probs = append(probs, f.ID+": incomplete feature contract")
	}
	return f, probs
}

func preserve(base, head []feat) (missing, weakened []string) {
	hm, rm := map[string]feat{}, map[string]bool{}
	for _, f := range head {
		hm[f.ID] = f
		for _, s := range f.Subs {
			hm[s[0]] = f
		}
	}
	for _, f := range base {
		for _, id := range f.Rm {
			rm[id] = true
		}
	}
	has := func(id string) bool { _, ok := hm[id]; return ok }
	for _, f := range base {
		if !rm[f.ID] && !has(f.ID) {
			missing = append(missing, f.ID)
		}
		hf := hm[f.ID]
		if has(f.ID) && len(hf.Ent) < len(f.Ent) {
			weakened = append(weakened, f.ID+" entries")
		}
		if has(f.ID) && len(hf.Proof) < len(f.Proof) {
			weakened = append(weakened, f.ID+" proofs")
		}
		for _, s := range f.Subs {
			if !rm[s[0]] && !has(s[0]) {
				missing = append(missing, s[0])
			}
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
		for _, s := range f.Subs {
			h.Subs = append(h.Subs, s[0])
		}
		if f.ID == "verify-sai" {
			fb = h
		}
		ok := path == "" && tool == "" && f.ID == "verify-sai"
		for _, p := range f.Paths {
			p = strings.ToLower(strings.TrimPrefix(p, "./"))
			if p == "" {
				continue
			}
			if strings.Contains(p, "/") {
				ok = ok || strings.Contains(pl, p) || strings.Contains(p, pl)
			} else {
				ok = ok || pl == p || strings.HasSuffix(pl, "/"+p)
			}
		}
		if ok {
			out = append(out, h)
		}
	}
	if len(out) == 0 && fb.ID != "" {
		return []hit{fb}
	}
	return out
}

func checkHooks(root string) (ok, pre, post, stop bool, matcher string, failClosed bool, events []string) {
	b, err := os.ReadFile(filepath.Join(root, ".cursor/hooks.json"))
	if err != nil {
		return
	}
	var doc struct {
		Hooks map[string][]struct {
			Command, Matcher string
			FailClosed       bool
		}
	}
	if json.Unmarshal(b, &doc) != nil {
		return
	}
	good := func(name string) bool {
		for _, h := range doc.Hooks[name] {
			if !strings.Contains(h.Command, "sai-verify") || matchEv[name] && !(h.Matcher == ".*" || h.Matcher == "^.*$" || h.Matcher == "") {
				continue
			}
			return !failEv[name] || h.FailClosed
		}
		return false
	}
	for _, e := range allEv {
		if good(e) {
			events = append(events, e)
		}
	}
	pre, post, stop, ok = good("preToolUse"), good("postToolUse"), good("stop"), len(events) == len(allEv)
	matcher, failClosed = ".*", ok
	return
}

func hook(in io.Reader, out io.Writer, root string) int {
	var raw map[string]interface{}
	if err := json.NewDecoder(in).Decode(&raw); err != nil {
		fmt.Fprintf(out, `{"permission":"deny","agent_message":"sai-verify: invalid hook json"}`+"\n")
		return 0
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
			if s, ok := wr[0].(string); ok && s != "" {
				root = s
			}
		}
	}
	s, err := build(root, root, root, extractPath(raw), str(raw["tool_name"]), str(raw["claimed_head"]))
	ctx, deny := hookCtx(s), err != nil || !s.MapValid || !s.PreserveOK
	if permEv[ev] {
		if deny {
			fmt.Fprintf(out, `{"permission":"deny","user_message":"sai-verify failed","agent_message":%s}`+"\n", jq(ctx))
			return 0
		}
		fmt.Fprintf(out, `{"permission":"allow","agent_message":%s}`+"\n", jq(ctx))
		return 0
	}
	msg := ""
	if ev == "stop" && (s.MaintRequired || !s.OK) {
		msg = "Verification/map-maintenance obligations remain on exact HEAD. Run /maintain-verification-skill on .cursor/skills/verify-sai and go run ./cmd/sai-verify doctor. " + ctx
	}
	if ev == "stop" {
		fmt.Fprintf(out, `{"followup_message":%s}`+"\n", jq(msg))
		return 0
	}
	fmt.Fprintf(out, `{"additional_context":%s}`+"\n", jq(ctx))
	return 0
}

func extractPath(raw map[string]interface{}) string {
	in, _ := raw["tool_input"].(map[string]interface{})
	if in == nil {
		in = map[string]interface{}{}
	}
	for _, src := range []map[string]interface{}{in, raw} {
		for _, k := range []string{"path", "file_path", "target_file", "filePath", "target_directory", "glob", "command", "url"} {
			if s := str(src[k]); s != "" {
				return s
			}
		}
	}
	if eds, _ := raw["edits"].([]interface{}); len(eds) > 0 {
		if m, _ := eds[0].(map[string]interface{}); m != nil {
			if s := str(m["file_path"]); s != "" {
				return s
			}
		}
	}
	return ""
}

func hookCtx(s snap) string {
	rel := make([]string, 0, len(s.Relevant))
	for _, h := range s.Relevant {
		rel = append(rel, h.ID)
	}
	b, _ := json.Marshal(map[string]interface{}{
		"repo": s.Repo, "base": s.Base, "head": s.Head, "ok": s.OK, "map_valid": s.MapValid, "preserve_ok": s.PreserveOK, "hooks_ok": s.HooksOK,
		"hook_pre": s.HookPre, "hook_post": s.HookPost, "hook_stop": s.HookStop, "hook_fail_closed": s.HookFailClosed, "hook_events": s.HookEvents,
		"maintenance_required": s.MaintRequired, "map_files": s.MapFiles, "map_subfeatures": s.MapSubs, "map_entry_points": s.MapEntries,
		"relevant": rel, "obligations": s.Obligations, "missing": s.Missing, "unreachable": s.Unreachable, "impl_loc": s.ImplLOC, "impl_funcs": s.ImplFuncs,
	})
	return string(b)
}

func writeProof(w io.Writer, s snap) {
	fmt.Fprintf(w, "Sai verification proof\nrepo: %s\nbase: %s\nhead: %s\ndirty: %v\nok: %v\nmap: files=%d features=%d subfeatures=%d entry_points=%d valid=%v\npreserve: %v missing=%v weakened=%v\nhooks: ok=%v pre=%v post=%v stop=%v matcher=%s failClosed=%v events=%s\nmaintenance: %s required=%v %s\ngo: test -race ./... ; vet ./... ; hook transcripts in go test (all agent events + stale deny)\nunreachable: %s\nkernel: files=%d loc=%d funcs=%d\ndensity: one parser/model; CLI+hooks+CI share build(); every Cursor agent hook emits the same snapshot fields.\n",
		s.Repo, s.Base, s.Head, s.Dirty, s.OK, s.MapFiles, s.MapFeatures, s.MapSubs, s.MapEntries, s.MapValid, s.PreserveOK, s.Missing, s.Weakened, s.HooksOK, s.HookPre, s.HookPost, s.HookStop, s.HookMatcher, s.HookFailClosed, strings.Join(s.HookEvents, ","), map[bool]string{false: "clean", true: "blocked"}[s.MaintRequired], s.MaintRequired, s.MaintReason, strings.Join(s.Unreachable, " | "), s.ImplFiles, s.ImplLOC, s.ImplFuncs)
	if s.Err != "" {
		fmt.Fprintf(w, "error: %s\n", s.Err)
	}
}

func unreachable(fs []feat) []string {
	var u []string
	for _, f := range fs {
		u = append(u, f.Unreach...)
		for _, s := range f.Subs {
			if strings.Contains(strings.ToLower(s[1]), "stub exit 2") {
				u = append(u, s[0]+": "+s[1])
			}
		}
	}
	return uniq(u)
}

func obligations(s snap) (o []string) {
	for _, p := range []struct {
		ok bool
		m  string
	}{{s.MapValid, "fix map structure"}, {s.PreserveOK, "restore protected IDs"}, {s.HooksOK, "restore full sai-verify Cursor agent hook set failClosed"}} {
		if !p.ok {
			o = append(o, p.m)
		}
	}
	for _, h := range s.Relevant {
		o = append(o, h.Proofs...)
		if len(o) > 8 {
			return o[:8]
		}
	}
	return
}

func repoName(u string) string {
	u = strings.TrimSuffix(u, ".git")
	if i := strings.LastIndex(u, "github.com/"); i >= 0 {
		return strings.TrimPrefix(u[i+11:], "/")
	}
	if u == "" {
		return "Dezocode/Sai"
	}
	return u
}

func git(dir string, args ...string) string {
	b, _ := exec.Command("git", append([]string{"-c", "safe.directory=*", "-C", dir}, args...)...).Output()
	return strings.TrimSpace(string(b))
}

func uniq(in []string) []string {
	seen, o := map[string]bool{}, []string{}
	for _, s := range in {
		if s = strings.TrimSpace(s); s == "" || seen[s] {
			continue
		}
		seen[s], o = true, append(o, s)
	}
	return o
}

func str(v interface{}) string { s, _ := v.(string); return s }
func jq(s string) string       { b, _ := json.Marshal(s); return string(b) }

func hooksJSON() []byte {
	h := map[string][]map[string]interface{}{}
	for _, e := range allEv {
		item := map[string]interface{}{"command": ".cursor/hooks/sai-verify.sh", "timeout": 60, "failClosed": true}
		if matchEv[e] {
			item["matcher"] = ".*"
		}
		if e == "stop" {
			item["loop_limit"] = 2
		}
		h[e] = []map[string]interface{}{item}
	}
	b, _ := json.Marshal(map[string]interface{}{"version": 1, "hooks": h})
	return b
}
