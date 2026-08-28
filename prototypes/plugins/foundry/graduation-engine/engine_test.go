package graduation

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func runGit(t *testing.T, dir string, args ...string) string {
	t.Helper()
	cmd := exec.Command("git", append([]string{"-C", dir}, args...)...)
	cmd.Env = append(os.Environ(), "GIT_AUTHOR_NAME=test", "GIT_AUTHOR_EMAIL=t@test", "GIT_COMMITTER_NAME=test", "GIT_COMMITTER_EMAIL=t@test")
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git %v: %v\n%s", args, err, out)
	}
	return strings.TrimSpace(string(out))
}

func setupRepo(t *testing.T) (root, head, graph string) {
	t.Helper()
	root = t.TempDir()
	runGit(t, root, "init")
	runGit(t, root, "config", "user.email", "t@test")
	runGit(t, root, "config", "user.name", "test")
	mustWrite(t, filepath.Join(root, "production", "app.go"), "package production\n// clean production tree\n")
	proto := filepath.Join(root, "prototypes", "plugins", "foundry", "test-widget")
	mustWrite(t, filepath.Join(proto, "manifest.json"), "{\"name\":\"test-widget\"}\n")
	mustWrite(t, filepath.Join(proto, "widget.txt"), "hello\n")
	runGit(t, root, "add", ".")
	runGit(t, root, "commit", "-m", "seed")
	head = runGit(t, root, "rev-parse", "HEAD")
	graph, err := ComputeGraphHash(root, "prototypes/plugins/foundry/test-widget")
	if err != nil {
		t.Fatal(err)
	}
	return root, head, graph
}

func mustWrite(t *testing.T, path, body string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(body), 0644); err != nil {
		t.Fatal(err)
	}
}

func basePlan(head, graph string, ops []Operation) Plan {
	p := Plan{
		SchemaVersion: SchemaVersion,
		Repo:          "https://github.com/Dezocode/Sai",
		Base:          head,
		PrototypeHead: head,
		GraphHash:     graph,
		Dispositions: []NodeDisposition{{
			Path: "prototypes/plugins/foundry/test-widget", Disposition: DispositionDrop,
		}},
		Operations: ops,
	}
	if err := ValidatePlan(&p); err != nil {
		panic(err)
	}
	return p
}

func TestIntegrateCreatesDraftPRCandidate(t *testing.T) {
	root, head, graph := setupRepo(t)
	work := t.TempDir()
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: work, Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpIntegrate, IdempotencyKey: "int-1", OwnerConfirmed: true,
		PrototypePath: "prototypes/plugins/foundry/test-widget", TargetBranch: "foundry/candidate",
	}})
	res, err := eng.Execute(plan)
	if err != nil {
		t.Fatal(err)
	}
	if len(res) != 1 || res[0].Audit.Operation != OpIntegrate {
		t.Fatalf("unexpected result: %+v", res)
	}
	prPath := res[0].Audit.FileMap["pr_candidate"]
	b, err := os.ReadFile(prPath)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(b), `"ready": false`) == false || strings.Contains(string(b), `"draft": true`) == false {
		t.Fatalf("expected draft not-ready PR candidate, got %s", b)
	}
}

func TestSpinoffMaterializesProvenance(t *testing.T) {
	root, head, graph := setupRepo(t)
	work := t.TempDir()
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: work, Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpSpinoff, IdempotencyKey: "spin-1", OwnerConfirmed: true,
		PrototypePath: "prototypes/plugins/foundry/test-widget", SpinoffName: "widget-app",
	}})
	res, err := eng.Execute(plan)
	if err != nil {
		t.Fatal(err)
	}
	prov := res[0].Audit.FileMap["provenance"]
	if _, err := os.Stat(prov); err != nil {
		t.Fatal(err)
	}
}

func TestDeleteArchiveRemovesPrototype(t *testing.T) {
	root, head, graph := setupRepo(t)
	work := t.TempDir()
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: work, Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpDeleteArchive, IdempotencyKey: "del-1", OwnerConfirmed: true,
		PrototypePath: "prototypes/plugins/foundry/test-widget",
	}})
	if _, err := eng.Execute(plan); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(root, "prototypes/plugins/foundry/test-widget")); !os.IsNotExist(err) {
		t.Fatalf("prototype should be removed, err=%v", err)
	}
}

func TestStalePlanFailsClosed(t *testing.T) {
	root, head, graph := setupRepo(t)
	mustWrite(t, filepath.Join(root, "production", "note.txt"), "change\n")
	runGit(t, root, "add", ".")
	runGit(t, root, "commit", "-m", "advance")
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: t.TempDir(), Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpIntegrate, IdempotencyKey: "stale", OwnerConfirmed: true,
	}})
	if _, err := eng.Execute(plan); err == nil || !strings.Contains(err.Error(), "stale prototype_head") {
		t.Fatalf("expected stale failure, got %v", err)
	}
}

func TestIdempotentReExecution(t *testing.T) {
	root, head, graph := setupRepo(t)
	work := t.TempDir()
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: work, Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpSpinoff, IdempotencyKey: "idem-1", OwnerConfirmed: true,
	}})
	first, err := eng.Execute(plan)
	if err != nil {
		t.Fatal(err)
	}
	second, err := eng.Execute(plan)
	if err != nil {
		t.Fatal(err)
	}
	if !second[0].Idempotent || second[0].Audit.Outputs[0] != first[0].Audit.Outputs[0] {
		t.Fatalf("expected idempotent replay, first=%+v second=%+v", first, second)
	}
}

func TestProductionDependencyBlocksDelete(t *testing.T) {
	root, head, graph := setupRepo(t)
	mustWrite(t, filepath.Join(root, "production", "ref.go"), "// imports prototypes/plugins/foundry/test-widget\n")
	runGit(t, root, "add", ".")
	runGit(t, root, "commit", "-m", "bad dep")
	head = runGit(t, root, "rev-parse", "HEAD")
	eng, err := NewEngine(BindState{RepoRoot: root, WorkDir: t.TempDir(), Production: []string{"production"}})
	if err != nil {
		t.Fatal(err)
	}
	plan := basePlan(head, graph, []Operation{{
		Kind: OpDeleteArchive, IdempotencyKey: "del-block", OwnerConfirmed: true,
	}})
	if _, err := eng.Execute(plan); err == nil || !strings.Contains(err.Error(), "production depends") {
		t.Fatalf("expected dependency block, got %v", err)
	}
}

func TestUnknownDispositionFailsPlanValidation(t *testing.T) {
	p := Plan{
		SchemaVersion: SchemaVersion,
		Repo: "x", Base: strings.Repeat("a", 40), PrototypeHead: strings.Repeat("b", 40),
		GraphHash: strings.Repeat("c", 64),
		Operations: []Operation{{Kind: OpIntegrate, IdempotencyKey: "k", OwnerConfirmed: true}},
		Dispositions: []NodeDisposition{{Path: "p", Disposition: Disposition("UNKNOWN")}},
	}
	if err := ValidatePlan(&p); err == nil {
		t.Fatal("expected UNKNOWN disposition failure")
	}
}
