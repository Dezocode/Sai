// Package app assembles the production Sai backend.
// Domain behavior belongs in focused internal packages; this package owns process lifecycle.
package app

import (
	"context"
	"errors"
	"net/http"
	"os"
	"time"
)

type App struct {
	server *http.Server
}

func New() *App {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", health)
	mux.HandleFunc("/ready", ready)
	addr := os.Getenv("SAI_ADDR")
	if addr == "" {
		addr = "127.0.0.1:8080"
	}
	return &App{server: &http.Server{
		Addr:              addr,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}}
}

func (a *App) Run(ctx context.Context) error {
	errCh := make(chan error, 1)
	go func() { errCh <- a.server.ListenAndServe() }()
	select {
	case <-ctx.Done():
		shutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return a.server.Shutdown(shutdown)
	case err := <-errCh:
		if errors.Is(err, http.ErrServerClosed) {
			return nil
		}
		return err
	}
}

func health(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) }

// ready is process-ready today; dependency readiness will be added as dependencies exist.
func ready(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(http.StatusNoContent) }
