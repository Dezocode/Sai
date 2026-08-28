package graph

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
)

type hashBody struct {
	Provenance Provenance `json:"provenance"`
	ManifestID string     `json:"manifest_id"`
	Nodes      []Node     `json:"nodes"`
	Edges      []Edge     `json:"edges"`
}

func canonicalHash(o Output) (string, error) {
	body := hashBody{
		Provenance: o.Provenance,
		ManifestID: o.ManifestID,
		Nodes:      o.Nodes,
		Edges:      o.Edges,
	}
	b, err := json.Marshal(body)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:]), nil
}
