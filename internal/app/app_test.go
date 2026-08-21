package app

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestDefaultAddr(t *testing.T) {
	if DefaultAddr != "127.0.0.1:8080" {
		t.Fatal(DefaultAddr)
	}
}

func TestAddrEnv(t *testing.T) {
	t.Setenv("SAI_ADDR", "127.0.0.1:9")
	if Addr() != "127.0.0.1:9" {
		t.Fatal(Addr())
	}
	os.Unsetenv("SAI_ADDR")
	if Addr() != DefaultAddr {
		t.Fatal(Addr())
	}
}

func TestHandlerProbes(t *testing.T) {
	h := Handler()
	for _, p := range []string{"/health", "/ready"} {
		w := httptest.NewRecorder()
		h.ServeHTTP(w, httptest.NewRequest(http.MethodGet, p, nil))
		if w.Code != http.StatusNoContent {
			t.Fatalf("GET %s %d", p, w.Code)
		}
		w = httptest.NewRecorder()
		h.ServeHTTP(w, httptest.NewRequest(http.MethodPost, p, nil))
		if w.Code != http.StatusMethodNotAllowed {
			t.Fatalf("POST %s %d", p, w.Code)
		}
	}
}

func TestRunCancels(t *testing.T) {
	t.Setenv("SAI_ADDR", "127.0.0.1:0")
	ctx, cancel := context.WithCancel(context.Background())
	errCh := make(chan error, 1)
	go func() { errCh <- New().Run(ctx) }()
	time.Sleep(40 * time.Millisecond)
	cancel()
	select {
	case err := <-errCh:
		if err != nil {
			t.Fatal(err)
		}
	case <-time.After(5 * time.Second):
		t.Fatal("timeout")
	}
}

func TestConfigConsumersAgree(t *testing.T) {
	root := filepath.Join("..", "..")
	for _, p := range []string{
		"apps/apple/Config/Development.xcconfig",
		"api/openapi.yaml",
		"apps/apple/Packages/SaiKit/Sources/SaiFoundation/SaiFoundation.swift",
	} {
		b, err := os.ReadFile(filepath.Join(root, p))
		if err != nil {
			t.Fatal(p, err)
		}
		s := string(b)
		if !strings.Contains(s, "127.0.0.1:8080") && !strings.Contains(s, "http:/$()/127.0.0.1:8080") {
			t.Fatalf("%s missing loopback", p)
		}
	}
}
