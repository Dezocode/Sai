package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"

	"github.com/Dezocode/Sai/prototypes/plugins/foundry/integrate-planner/planner"
)

func main() {
	graphPath := flag.String("graph", "", "path to foundry.graph.v1 JSON file")
	head := flag.String("head", "", "expected prototype HEAD SHA (40 chars)")
	out := flag.String("out", "", "optional output file (default stdout)")
	flag.Parse()

	if *graphPath == "" || *head == "" {
		fmt.Fprintln(os.Stderr, "usage: foundry-integrate-plan --graph <file> --head <sha> [--out <file>]")
		os.Exit(2)
	}
	if len(*head) != 40 {
		fmt.Fprintln(os.Stderr, "--head must be a 40-character SHA")
		os.Exit(2)
	}

	data, err := ioutil.ReadFile(*graphPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	g, err := planner.ParseGraphJSON(data)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	plan := planner.BuildPlan(&g, *head)
	encoded, err := json.MarshalIndent(plan, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	encoded = append(encoded, '\n')
	if *out == "" {
		_, _ = os.Stdout.Write(encoded)
		return
	}
	if err := ioutil.WriteFile(*out, encoded, 0644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
