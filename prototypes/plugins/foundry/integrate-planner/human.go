package integrateplanner

import (
	"fmt"
	"strings"
)

func RenderHumanSummary(plan IntegratePlan) string {
	var b strings.Builder
	fmt.Fprintf(&b, "Integrate plan for %s\n", plan.PrototypeID)
	fmt.Fprintf(&b, "Status: %s (ready=%v)\n", plan.Status, plan.Ready)
	fmt.Fprintf(&b, "Source HEAD: %s\n", plan.SourceHeadSHA)
	fmt.Fprintf(&b, "Graph hash: %s\n", plan.GraphHash)
	fmt.Fprintf(&b, "Artifacts: %d\n", len(plan.Artifacts))
	if len(plan.Blockers) > 0 {
		b.WriteString("Blockers:\n")
		for _, bl := range plan.Blockers {
			fmt.Fprintf(&b, "  - %s\n", bl)
		}
	}
	if len(plan.RequiredChecks) > 0 {
		b.WriteString("Required checks:\n")
		for _, c := range plan.RequiredChecks {
			fmt.Fprintf(&b, "  - %s\n", c)
		}
	}
	return b.String()
}
