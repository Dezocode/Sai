package graduation

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type journalEntry struct {
	IdempotencyKey string      `json:"idempotency_key"`
	PlanHash       string      `json:"plan_hash"`
	Result         AuditRecord `json:"result"`
	RecordedAt     time.Time   `json:"recorded_at"`
}

type journalFile struct {
	Entries []journalEntry `json:"entries"`
}

type Journal struct {
	path string
	mu   sync.Mutex
}

func OpenJournal(path string) (*Journal, error) {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return nil, err
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		if err := writeJournal(path, journalFile{}); err != nil {
			return nil, err
		}
	}
	return &Journal{path: path}, nil
}

func writeJournal(path string, j journalFile) error {
	b, err := json.MarshalIndent(j, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0644)
}

func (j *Journal) load() (journalFile, error) {
	b, err := os.ReadFile(j.path)
	if err != nil {
		return journalFile{}, err
	}
	var f journalFile
	if err := json.Unmarshal(b, &f); err != nil {
		return journalFile{}, err
	}
	return f, nil
}

func (j *Journal) Lookup(idempotencyKey, planHash string) (*AuditRecord, bool, error) {
	j.mu.Lock()
	defer j.mu.Unlock()
	f, err := j.load()
	if err != nil {
		return nil, false, err
	}
	for _, e := range f.Entries {
		if e.IdempotencyKey == idempotencyKey {
			if e.PlanHash != planHash {
				return nil, false, fmt.Errorf("idempotency key reused with different plan hash")
			}
			cp := e.Result
			return &cp, true, nil
		}
	}
	return nil, false, nil
}

func (j *Journal) Record(idempotencyKey, planHash string, rec AuditRecord) error {
	j.mu.Lock()
	defer j.mu.Unlock()
	f, err := j.load()
	if err != nil {
		return err
	}
	for _, e := range f.Entries {
		if e.IdempotencyKey == idempotencyKey {
			if e.PlanHash != planHash {
				return fmt.Errorf("idempotency key reused with different plan hash")
			}
			return nil
		}
	}
	f.Entries = append(f.Entries, journalEntry{
		IdempotencyKey: idempotencyKey,
		PlanHash:       planHash,
		Result:         rec,
		RecordedAt:     time.Now().UTC(),
	})
	return writeJournal(j.path, f)
}
