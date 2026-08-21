package app

import (
	"context"
	"errors"
	"net"
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
	ln, err := net.Listen("tcp", a.server.Addr)
	if err != nil {
		return err
	}
	defer ln.Close()
	a.server.Addr = ln.Addr().String()
	shutErr := make(chan error, 1)
	go func() {
		<-ctx.Done()
		c, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		shutErr <- a.server.Shutdown(c)
	}()
	err = a.server.Serve(ln)
	if errors.Is(err, http.ErrServerClosed) {
		return <-shutErr
	}
	return err
}
