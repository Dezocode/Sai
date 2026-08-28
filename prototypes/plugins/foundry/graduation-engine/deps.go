package graduation

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

var skipDirNames = map[string]bool{
	".git":         true,
	"node_modules": true,
	"__pycache__":  true,
}

// ScanProductionDependencies walks productionRoots for textual references to prototypeRel.
func ScanProductionDependencies(repoRoot, prototypeRel string, productionRoots []string) ([]string, error) {
	needle := filepath.ToSlash(prototypeRel)
	needleAlt := strings.TrimSuffix(needle, "/")
	var hits []string
	for _, root := range productionRoots {
		abs := filepath.Join(repoRoot, root)
		if _, err := os.Stat(abs); os.IsNotExist(err) {
			continue
		}
		err := filepath.Walk(abs, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				if skipDirNames[info.Name()] {
					return filepath.SkipDir
				}
				return nil
			}
			if containsNeedle(path, needle) || (needleAlt != needle && containsNeedle(path, needleAlt)) {
				rel, _ := filepath.Rel(repoRoot, path)
				hits = append(hits, rel)
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

func AssertProductionNeverImportsPrototypes(repoRoot string, productionRoots []string) error {
	for _, root := range productionRoots {
		abs := filepath.Join(repoRoot, root)
		if _, err := os.Stat(abs); os.IsNotExist(err) {
			continue
		}
		err := filepath.Walk(abs, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if info.IsDir() {
				if skipDirNames[info.Name()] {
					return filepath.SkipDir
				}
				return nil
			}
			if !strings.HasSuffix(path, ".go") {
				return nil
			}
			b, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			s := string(b)
			if strings.Contains(s, "prototypes/") || strings.Contains(s, "/prototypes") {
				rel, _ := filepath.Rel(repoRoot, path)
				return fmt.Errorf("production imports prototypes in %s", rel)
			}
			return nil
		})
		if err != nil {
			return err
		}
	}
	return nil
}
