package integrateplanner

import (
	"fmt"
	"strings"
)

func RenderHumanSummary(plan IntegratePlan) string {
	if plan.Ready {
		return fmt.Sprintf(
			"Integrate plan for %s is READY at HEAD %s with %d entries and %d proposed production path(s).",
			plan.PrototypeID, plan.SourceHeadSHA, len(plan.Entries), len(plan.ProposedPaths),
		)
	}
	parts := []string{
		fmt.Sprintf("Integrate plan for %s is BLOCKED at HEAD %s with %d blocker(s).", plan.PrototypeID, plan.SourceHeadSHA, len(plan.Blockers)),
	}
	for i, b := range plan.Blockers {
		if i >= 3 {
			parts = append(parts, fmt.Sprintf("... and %d more blocker(s).", len(plan.Blockers)-3))
			break
		}
		parts = append(parts, b)
	}
	return strings.Join(parts, " ")
}
