package graduation

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// ScanProductionDependencies walks productionRoots for textual references to prototypeRel.
func ScanProductionDependencies(repoRoot, prototypeRel string, productionRoots []string) ([]string, error) {
	needle := filepath.ToSlash(prototypeRel)
	var hits []string
	for _, root := range productionRoots {
		abs := filepath.Join(repoRoot, root)
		if _, err := os.Stat(abs); os.IsNotExist(err) {
			continue
		}
		err := filepath.Walk(abs, func(path string, info os.FileInfo, err error) error {
			if err != nil || info.IsDir() {
				return nil
			}
			if strings.HasSuffix(path, ".go") || strings.HasSuffix(path, ".md") || strings.HasSuffix(path, ".yaml") {
				if containsNeedle(path, needle) {
					rel, _ := filepath.Rel(repoRoot, path)
						 hits = append(hits, rel)
				}
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	return hits, nil
}

func containsNeedle(path, needle string) bool {
	f, err := os.Open(path)
	if err != nil {
		return false
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		if strings.Contains(sc.Text(), needle) {
			return true
		}
	}
	return false
}

func AssertNoProductionDependency(repoRoot, prototypeRel string, productionRoots []string) error {
	hits, err := ScanProductionDependencies(repoRoot, prototypeRel, productionRoots)
	if err != nil {
		return err
	}
	if len(hits) > 0 {
		return fmt.Errorf("production depends on prototype via: %s", strings.Join(hits, ", "))
	}
	return nil
}
