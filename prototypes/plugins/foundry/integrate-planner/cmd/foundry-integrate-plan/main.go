package main

import (
	"flag"
	"fmt"
	"os"

	integrateplanner "github.com/Dezocode/Sai/prototypes/plugins/foundry/integrate-planner"
)

func main() {
	graphPath := flag.String("graph", "", "path to foundry.graph.v1 JSON")
	head := flag.String("head", "", "exact 40-char prototype HEAD SHA")
	out := flag.String("out", "", "optional output path for plan JSON")
	flag.Parse()

	if *graphPath == "" || *head == "" {
		fmt.Fprintln(os.Stderr, "--graph and --head are required")
		os.Exit(2)
	}
	data, err := os.ReadFile(*graphPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	g, err := integrateplanner.ParseGraphJSON(data)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	plan, err := integrateplanner.Plan(g, *head)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	encoded, err := integrateplanner.CanonicalPlanJSON(plan)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if *out != "" {
		if err := os.WriteFile(*out, encoded, 0644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	} else {
		fmt.Println(string(encoded))
	}
	if !plan.Ready {
		os.Exit(3)
	}
}
