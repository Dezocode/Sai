package graph

import "fmt"

const (
	REUSE          = "REUSE"
	PROMOTE        = "PROMOTE"
	EXPORT         = "EXPORT"
	REMOTE         = "REMOTE"
	PROMOTE_SHARED = "PROMOTE_SHARED"
	DROP           = "DROP"
	UNKNOWN        = "UNKNOWN"
)

func validateClassification(c string) error {
	switch c {
	case REUSE, PROMOTE, EXPORT, REMOTE, PROMOTE_SHARED, DROP:
		return nil
	case UNKNOWN, "":
		return fmt.Errorf("classification unresolved: %q", c)
	default:
		return fmt.Errorf("unknown classification: %q", c)
	}
}
