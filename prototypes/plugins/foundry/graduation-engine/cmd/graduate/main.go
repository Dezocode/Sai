package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	grad "github.com/Dezocode/Sai/prototypes/plugins/foundry/graduation-engine"
)

func main() {
	planPath := flag.String("plan", "", "path to validated plan JSON")
	repoRoot := flag.String("repo", ".", "repository root")
	workDir := flag.String("workdir", "", "working directory for journal/candidates")
	dryRun := flag.Bool("dry-run", false, "validate plan bindings only")
	flag.Parse()
	if *planPath == "" {
		fmt.Fprintln(os.Stderr, "usage: graduate --plan plan.json [--repo .] [--workdir dir]")
		os.Exit(2)
	}
	b, err := os.ReadFile(*planPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var plan grad.Plan
	if err := json.Unmarshal(b, &plan); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := grad.ValidatePlan(&plan); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	wd := *workDir
	if wd == "" {
		wd = filepath.Join(*repoRoot, ".foundry", "work")
	}
	state := grad.BindState{RepoRoot: *repoRoot, WorkDir: wd, Production: []string{"production", "cmd", "internal"}}
	if *dryRun {
		if err := grad.VerifyBindings(state, plan); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Println("dry-run ok:", plan.PlanID)
		return
	}
	eng, err := grad.NewEngine(state)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	res, err := eng.Execute(plan)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	_ = enc.Encode(res)
}
