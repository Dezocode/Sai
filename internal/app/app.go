package app

import (
	"context"
	"errors"
	"net/http"
	"os"
	"time"
)

const DefaultAddr = "127.0.0.1:8080"

func Addr() string {
	if a := os.Getenv("SAI_ADDR"); a != "" {
		return a
	}
	return DefaultAddr
}

func Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", probe)
	mux.HandleFunc("/ready", probe)
	return mux
}

func probe(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.Header().Set("Allow", http.MethodGet)
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

type App struct {
	server *http.Server
}

func New() *App {
	return &App{server: &http.Server{
		Addr:              Addr(),
		Handler:           Handler(),
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}}
}

func (a *App) Addr() string          { return a.server.Addr }
func (a *App) Handler() http.Handler { return a.server.Handler }

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
