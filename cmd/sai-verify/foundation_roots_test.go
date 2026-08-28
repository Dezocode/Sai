package main

import "testing"

func TestFoundationRootsAreClaimable(t *testing.T) {
	sample := "`apps/apple/*` `api/openapi.yaml` `design/sai-design-language.json` `docs/architecture/*` `internal/*` `deploy/*` `migrations/*` `cmd/sai/*` `prototypes/plugins/foundry/graduation-engine/*` `prototypes/plugins/foundry/test-widget/*`"
	got := pathRe.FindAllString(sample, -1)
	need := []string{"apps/apple/*", "api/openapi.yaml", "design/sai-design-language.json", "docs/architecture/*", "internal/*", "deploy/*", "migrations/*", "cmd/sai/*", "prototypes/plugins/foundry/graduation-engine/*", "prototypes/plugins/foundry/test-widget/*"}
	have := map[string]bool{}
	for _, g := range got {
		have[g] = true
	}
	for _, n := range need {
		if !have[n] {
			t.Fatalf("pathRe missed %s from %v", n, got)
		}
	}
}
