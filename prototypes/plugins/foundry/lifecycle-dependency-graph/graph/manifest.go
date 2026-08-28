package graph

import (
	"encoding/json"
	"fmt"
)

const SchemaVersion = 1

var forbiddenManifestFields = []string{
	"exemption_root",
	"trusted_base",
	"verifier_policy",
	"design_authority",
	"executor_credentials",
	"canonical_root",
	"security_authority",
	"trusted_dependency_boundary",
	"permissions",
	"grants",
	"roles",
	"capabilities",
}

type Manifest struct {
	SchemaVersion int    `json:"schema_version"`
	ID            string `json:"id"`
}

func ParseManifest(data []byte) (Manifest, error) {
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		return Manifest{}, err
	}
	for _, field := range forbiddenManifestFields {
		if _, ok := raw[field]; ok {
			return Manifest{}, fmt.Errorf("forbidden manifest field: %s", field)
		}
	}
	var m Manifest
	if err := json.Unmarshal(data, &m); err != nil {
		return Manifest{}, err
	}
	if m.SchemaVersion != SchemaVersion {
		return Manifest{}, fmt.Errorf("unsupported schema_version: %d", m.SchemaVersion)
	}
	if m.ID == "" {
		return Manifest{}, fmt.Errorf("manifest id required")
	}
	return m, nil
}
