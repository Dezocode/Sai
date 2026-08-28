package integrateplanner

import "fmt"

func RenderHumanSummary(plan IntegratePlan) string {
	if plan.Ready {
		return fmt.Sprintf("Integrate plan for %s is READY with %d entries and %d proposed production path(s).", plan.PrototypeID, len(plan.Entries), len(plan.ProposedPaths))
	}
	return fmt.Sprintf("Integrate plan for %s is BLOCKED with %d blocker(s).", plan.PrototypeID, len(plan.Blockers))
}
