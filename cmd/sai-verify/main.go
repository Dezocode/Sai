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
	linkRe = regexp.MustCompile(`\]\((?:\./)?([^)]+\.md)\)`)
	idRe   = regexp.MustCompile("`([a-z][a-z0-9-]*)`")
	pathRe = regexp.MustCompile(`(?:\./)?(?:\.ai|\.cursor|\.github|\.githooks|scripts|openclaw-dashboard|cmd)(/[A-Za-z0-9_.*{}-]+)+|(?:AGENTS|CLAUDE|CODEX|OPENCLAW|README|Team)\.md|go\.mod`)
	rmRe   = regexp.MustCompile(`(?i)^Removal-authorized:\s*(.+)$`)
	h2Re   = regexp.MustCompile(`^## `)
)

type feat struct {
	ID, Title, File, Desc string
	Subs                  [][2]string
	Ent, Proof, Paths, Rm []string
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
	for i := 0; i < len(args); i++ {
		a := args[i]
		take := func() string {
			if i+1 >= len(args) {
				return ""
			}
			i++
			return args[i]
		}
		switch {
		case a == "--root":
			root = take()
		case a == "--base":
			baseDir = take()
		case a == "--head":
			headDir = take()
		case a == "--path":
			path = take()
		case a == "--tool":
			tool = take()
		case a == "--claimed-head":
			wantHead = take()
		case strings.HasPrefix(a, "-"):
			fmt.Fprintf(errw, "unknown flag %s\n", a)
			return 2
		default:
			cmd = a
		}
	}
	if headDir == "" {
		headDir = root
	}
	if baseDir == "" {
		baseDir = headDir
	}
	if cmd == "hook" {
		return hook(in, out, errw, root)
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
	s := snap{PreserveOK: true}
	s.Repo = repoName(git(headDir, "config", "--get", "remote.origin.url"))
	s.Head = git(headDir, "rev-parse", "HEAD")
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
	s.HooksOK, s.HookPre, s.HookPost, s.HookStop, s.HookMatcher, s.HookFailClosed = checkHooks(headDir)
	if !s.HooksOK {
		s.Problems = append(s.Problems, "hooks missing full-surface pre/post fail-closed sai-verify integration")
	}
	bf, _ := loadFeats(baseDir)
	s.Missing, s.Weakened = preserve(bf, hf)
	s.PreserveOK = len(s.Missing)+len(s.Weakened) == 0
	s.Relevant = relevant(hf, path, tool)
	s.Unreachable = unreachable(hf)
	s.ImplFiles, s.ImplLOC, s.ImplFuncs = density(headDir)
	s.Obligations = obligations(s)
	s.MaintRequired = !s.MapValid || !s.PreserveOK || !s.HooksOK || s.Dirty && strings.Contains(git(headDir, "status", "--porcelain"), "verify-sai")
	if s.MaintRequired {
		s.MaintReason = strings.Join(s.Problems, "; ")
		if s.MaintReason == "" && !s.PreserveOK {
			s.MaintReason = "preserve failed"
		}
		if s.MaintReason == "" {
			s.MaintReason = "map or hooks need maintenance"
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
		seen[f.ID] = true
		s.IDs = append(s.IDs, f.ID)
		s.MapSubs += len(f.Subs)
		s.MapEntries += len(f.Ent)
		for _, sub := range f.Subs {
			if seen[sub[0]] {
				probs = append(probs, "duplicate id "+sub[0])
			}
			seen[sub[0]] = true
			s.IDs = append(s.IDs, sub[0])
		}
	}
	sort.Strings(s.IDs)
	s.Problems = uniq(probs)
	s.MapValid = len(s.Problems) == 0 && len(fs) > 0
}

func loadFeats(root string) ([]feat, []string) {
	dir := filepath.Join(root, mapDir)
	idx := filepath.Join(dir, "README.md")
	b, err := os.ReadFile(idx)
	if err != nil {
		return nil, []string{"missing " + idx}
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
	onDisk := map[string]bool{}
	var probs []string
	for _, e := range ents {
		if e.IsDir() || e.Name() == "README.md" || !strings.HasSuffix(e.Name(), ".md") {
			continue
		}
		onDisk[e.Name()] = true
	}
	seenIdx := map[string]bool{}
	var fs []feat
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
		probs = append(probs, p...)
		fs = append(fs, f)
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
		if strings.HasPrefix(line, "# ") && f.Title == "" {
			f.Title = strings.TrimSpace(line[2:])
			continue
		}
		if m := rmRe.FindStringSubmatch(line); len(m) > 1 {
			for _, p := range strings.Split(m[1], ",") {
				p = strings.TrimSpace(p)
				if p != "" && p != "(none)" {
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
			rest := strings.TrimSpace(idRe.ReplaceAllString(line[1:], ""))
			f.Subs = append(f.Subs, [2]string{ids[0][1], rest})
		case strings.HasPrefix(sec, "How to get to it") && strings.HasPrefix(line, "-"):
			f.Ent = append(f.Ent, strings.TrimSpace(strings.TrimPrefix(line, "-")))
		case strings.HasPrefix(sec, "Driving it"):
			if strings.Contains(line, "`") {
				for _, m := range regexp.MustCompile("`([^`]+)`").FindAllStringSubmatch(line, -1) {
					if strings.ContainsAny(m[1], " /") || strings.HasPrefix(m[1], "go ") || strings.HasPrefix(m[1], "scripts/") {
						f.Proof = append(f.Proof, m[1])
					}
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
	hm := map[string]feat{}
	for _, f := range head {
		hm[f.ID] = f
		for _, s := range f.Subs {
			hm[s[0]] = f
		}
	}
	rm := map[string]bool{}
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

func checkHooks(root string) (ok, pre, post, stop bool, matcher string, failClosed bool) {
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
	good := func(name string) (bool, bool) {
		for _, h := range doc.Hooks[name] {
			if strings.Contains(h.Command, "sai-verify") && (h.Matcher == ".*" || h.Matcher == "^.*$" || h.Matcher == "") {
				return true, h.FailClosed
			}
		}
		return false, false
	}
	pre, failClosed = good("preToolUse")
	post, _ = good("postToolUse")
	for _, h := range doc.Hooks["stop"] {
		stop = stop || strings.Contains(h.Command, "sai-verify")
	}
	if !failClosed {
		pre = false
	}
	matcher, ok = ".*", pre && post && stop && failClosed
	return
}

func hook(in io.Reader, out, errw io.Writer, root string) int {
	var raw map[string]any
	if err := json.NewDecoder(in).Decode(&raw); err != nil {
		fmt.Fprintf(out, `{"permission":"deny","agent_message":"sai-verify: invalid hook json"}`+"\n")
		return 0
	}
	ev, _ := raw["hook_event_name"].(string)
	if ev == "" {
		if _, ok := raw["tool_output"]; ok {
			ev = "postToolUse"
		} else if _, ok := raw["loop_count"]; ok && raw["tool_name"] == nil {
			ev = "stop"
		} else {
			ev = "preToolUse"
		}
	}
	if root == "." || root == "" {
		if wr, _ := raw["workspace_roots"].([]any); len(wr) > 0 {
			if s, ok := wr[0].(string); ok && s != "" {
				root = s
			}
		}
	}
	tool, _ := raw["tool_name"].(string)
	path := extractPath(raw)
	claimed, _ := raw["claimed_head"].(string)
	s, err := build(root, root, root, path, tool, claimed)
	ctx := brief(s)
	if err != nil || !s.MapValid {
		if ev == "preToolUse" {
			fmt.Fprintf(out, `{"permission":"deny","user_message":"sai-verify failed","agent_message":%s}`+"\n", jq(ctx))
			return 0
		}
	}
	if ev == "preToolUse" && !s.PreserveOK {
		fmt.Fprintf(out, `{"permission":"deny","user_message":"protected feature preservation failed","agent_message":%s}`+"\n", jq(ctx))
		return 0
	}
	switch ev {
	case "preToolUse":
		fmt.Fprintf(out, `{"permission":"allow","agent_message":%s}`+"\n", jq(ctx))
	case "postToolUse":
		fmt.Fprintf(out, `{"additional_context":%s}`+"\n", jq(ctx))
	case "stop":
		msg := ""
		if s.MaintRequired || !s.OK {
			msg = "Verification/map-maintenance obligations remain on exact HEAD. Run /maintain-verification-skill on .cursor/skills/verify-sai and go run ./cmd/sai-verify doctor. " + ctx
		}
		fmt.Fprintf(out, `{"followup_message":%s}`+"\n", jq(msg))
	default:
		fmt.Fprintf(out, `{"permission":"allow","agent_message":%s}`+"\n", jq(ctx))
	}
	_ = errw
	return 0
}

func extractPath(raw map[string]any) string {
	in, _ := raw["tool_input"].(map[string]any)
	if in == nil {
		in = raw
	}
	for _, k := range []string{"path", "file_path", "target_file", "filePath"} {
		if s, ok := in[k].(string); ok {
			return s
		}
	}
	if s, ok := in["command"].(string); ok {
		return s
	}
	return ""
}

func brief(s snap) string {
	var b strings.Builder
	fmt.Fprintf(&b, "sai-verify repo=%s base=%s head=%s ok=%v map=%d feats/%d subs/%d ep hooks=%v preserve=%v", s.Repo, short(s.Base), short(s.Head), s.OK, s.MapFeatures, s.MapSubs, s.MapEntries, s.HooksOK, s.PreserveOK)
	if len(s.Relevant) > 0 {
		b.WriteString(" relevant=")
		for i, h := range s.Relevant {
			if i > 0 {
				b.WriteByte(',')
			}
			b.WriteString(h.ID)
		}
	}
	if s.MaintRequired {
		fmt.Fprintf(&b, " maintenance=%s", s.MaintReason)
	}
	for _, h := range s.Relevant {
		if len(h.Proofs) > 0 {
			fmt.Fprintf(&b, " proof[%s]=%s", h.ID, h.Proofs[0])
			break
		}
	}
	return b.String()
}

func writeProof(w io.Writer, s snap) {
	fmt.Fprintf(w, "Sai verification proof\nrepo: %s\nbase: %s\nhead: %s\ndirty: %v\nok: %v\n", s.Repo, s.Base, s.Head, s.Dirty, s.OK)
	fmt.Fprintf(w, "map: files=%d features=%d subfeatures=%d entry_points=%d valid=%v\n", s.MapFiles, s.MapFeatures, s.MapSubs, s.MapEntries, s.MapValid)
	fmt.Fprintf(w, "preserve: %v missing=%v weakened=%v\n", s.PreserveOK, s.Missing, s.Weakened)
	fmt.Fprintf(w, "hooks: ok=%v pre=%v post=%v stop=%v matcher=%s failClosed=%v\n", s.HooksOK, s.HookPre, s.HookPost, s.HookStop, s.HookMatcher, s.HookFailClosed)
	fmt.Fprintf(w, "maintenance: required=%v %s\n", s.MaintRequired, s.MaintReason)
	fmt.Fprintf(w, "unreachable: %s\n", strings.Join(s.Unreachable, " | "))
	fmt.Fprintf(w, "kernel: files=%d loc=%d funcs=%d\n", s.ImplFiles, s.ImplLOC, s.ImplFuncs)
	fmt.Fprintf(w, "density: one parser/model, one core for CLI/hooks/CI; remaining types are JSON snapshot + feature record.\n")
	if s.Err != "" {
		fmt.Fprintf(w, "error: %s\n", s.Err)
	}
}

func unreachable(fs []feat) []string {
	u := []string{"oc-gateway-health live: requires openclaw CLI + loopback gateway", "oc-ingest-slo: stub exit 2 until services/activity-ingest exists", "oc-telegram-mcq: stub exit 2 until Telegram wired", "oc-smoke-run-all: stub exit 2 until tab BUILD phases exist"}
	for _, f := range fs {
		if strings.Contains(strings.ToLower(f.Desc), "stub exit 2") {
			u = append(u, f.ID)
		}
	}
	return uniq(u)
}

func obligations(s snap) (o []string) {
	if !s.MapValid {
		o = append(o, "fix map structure")
	}
	if !s.PreserveOK {
		o = append(o, "restore protected IDs")
	}
	if !s.HooksOK {
		o = append(o, "restore pre/post .* failClosed sai-verify hooks")
	}
	for _, h := range s.Relevant {
		o = append(o, h.Proofs...)
		if len(o) > 8 {
			return o[:8]
		}
	}
	return
}

func density(root string) (files, loc, fns int) {
	filepath.Walk(filepath.Join(root, "cmd/sai-verify"), func(p string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() || !strings.HasSuffix(p, ".go") || strings.HasSuffix(p, "_test.go") {
			return nil
		}
		b, _ := os.ReadFile(p)
		files, loc, fns = files+1, loc+bytes.Count(b, []byte("\n")), fns+bytes.Count(b, []byte("\nfunc "))
		return nil
	})
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
	b, _ := exec.Command("git", append([]string{"-C", dir}, args...)...).Output()
	return strings.TrimSpace(string(b))
}

func uniq(in []string) []string {
	seen, o := map[string]bool{}, []string{}
	for _, s := range in {
		s = strings.TrimSpace(s)
		if s == "" || seen[s] {
			continue
		}
		seen[s], o = true, append(o, s)
	}
	return o
}

func short(s string) string {
	if len(s) > 7 {
		return s[:7]
	}
	return s
}

func jq(s string) string { b, _ := json.Marshal(s); return string(b) }
