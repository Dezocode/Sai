#!/usr/bin/env python3
"""Hermes/Saul multi-agent PR session tracking API for Origin + Pages dashboard.

Hermes-compatible schema sai-sessions-v2. Alias /api/agent-sessions/* shares handlers.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DATA = Path(os.environ.get("SESSIONS_DATA", "/data/sessions.json"))
WRITE_TOKEN = os.environ.get("SESSIONS_WRITE_TOKEN", "").strip()
LOCK = threading.Lock()
DEFAULT_MONITORS = ["dezocode", "origin-grokbot"]

# --- M17 spawn-lifecycle vocabulary -----------------------------------------
# Statuses are persisted lowercase. Anything outside KNOWN_STATUSES is still
# stored but responses carry "status_recognized": false so consumers never
# mistake an unrecognized string for a real lifecycle state.
ACTIVE_STATUSES = ("spawned", "launched", "tracked", "running", "active", "reviewing")
TERMINAL_STATUSES = ("done", "failed", "stopped", "cancelled", "merged")
KNOWN_STATUSES = ACTIVE_STATUSES + TERMINAL_STATUSES
HEARTBEAT_FRESH_S = 1800  # PR77 beatBucket contract: fresh <30m, stale >=30m, missing never stale
CLOCK_SKEW_TOLERANCE_S = 300  # API-F4: heartbeat dated >5min in the future = garbage clock -> missing
IDEMPOTENCY_TTL_S = 86400   # replay window for durable Idempotency-Key records

# --- API-F101: live CI failing pieces (paginated check-runs on exact HEAD) ---
GH_REPO_DEFAULT = "Dezocode/Sai"   # override via env SESSIONS_GH_REPO
CI_CACHE_TTL_S = 120              # fresh cache window per head sha
CI_STALE_OK_S = 900               # on fetch failure, stale cache served up to this age
PR_HEAD_TTL_S = 60                # API-F008: cached live PR-tip resolution window (success)
PR_HEAD_FAIL_TTL_S = 10           # failed tip lookups retry sooner (short negative cache)
CHECK_RUNS_MAX_PAGES = 5          # 5 * 100 runs = hard pagination cap
FAILING_CONCLUSIONS = frozenset({
    "failure", "timed_out", "action_required", "cancelled", "startup_failure", "stale",
})
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_CI_CACHE: dict = {}             # sha -> (monotonic_ts, runs, incomplete, http_status)
_PR_HEAD_CACHE: dict = {}        # pr -> (monotonic_ts, sha_or_None, ok_bool)  # API-F008
_RATE_LOCK = threading.Lock()
_RATE_COOLDOWN_UNTIL = 0.0        # monotonic ts until which GitHub fetches fail fast (429)
_RATE_LAST_REMAINING = None       # last observed X-RateLimit-Remaining (None = never seen)
_CI_CACHE_LOCK = threading.Lock()
IDEMPOTENCY_MAX_KEYS = 1000

# --- Runtime Registry (RFC 2026-08-24: closed multi-runtime vocabulary) --------
# DECIDED: agents can only BE a registered runtime; unknown species are refused
# (or auto-provisioned as flagged "provisional" when SAUL_REGISTRY_AUTOREGISTER!=0).
# Per-runtime liveness windows replace the one-size HEARTBEAT_FRESH_S default.
DEFAULT_RUNTIMES = {
    "hermes": {"fresh_s": 900},
    "atomic": {"fresh_s": 3600},
    "cursor": {"fresh_s": 7200},
    "grok":   {"fresh_s": 1800},
    "codex":  {"fresh_s": 1800},
    "human":  {"fresh_s": 86400},
}
AUTOREGISTER = os.environ.get("SAUL_REGISTRY_AUTOREGISTER", "1") != "0"
PROVISIONAL_FRESH_S = 3600
_FRESH_WINDOWS: dict = {}          # runtime -> fresh_s
_PROVISIONAL_RUNTIMES: dict = {}   # runtime -> True if status=provisional
_SLUG_RE = re.compile(r"[^a-z0-9_-]+")

def _validate_or_provision(store: dict, rt_raw) -> tuple[str | None, str | None]:
    """Returns (runtime_slug, error). Registers provisionally when enabled."""
    rt = _slugify(str(rt_raw or ""))
    if not rt or rt in ("unknown",):
        return None, None
    if rr_registered(store, rt):
        return rt, None
    if AUTOREGISTER:
        rr_register(store, rt, provisional=True)
        _refresh_windows(store)
        return rt, None
    return None, rt

def _refresh_windows(store: dict) -> None:
    """Per-runtime fresh windows from store registry (fallback: HEARTBEAT_FRESH_S)."""
    global _FRESH_WINDOWS,_PROVISIONAL_RUNTIMES
    reg = store.get("runtimes") or {}
    _FRESH_WINDOWS = {rt: int(e.get("fresh_s") or HEARTBEAT_FRESH_S)
                      for rt, e in reg.items() if isinstance(e, dict)}
    _PROVISIONAL_RUNTIMES = {rt: True for rt, e in reg.items()
                             if isinstance(e, dict) and e.get("status") == "provisional"}

class _Head40(str):
    """Exactly 40 lowercase hex chars. Unrepresentable otherwise."""
    def __new__(cls, v):
        s = str(v).strip().lower()
        if not _SHA40_RE.match(s):
            raise ValueError("ShortSha")
        return super().__new__(cls, s)

def assert_head_binding(github_head, card_head, evidence_head=None):
    """Guarantee: card, evidence, and dispatch name ONE sha — or the refusal names the divergent party."""
    try:
        gh = _Head40(github_head)
    except ValueError:
        return {"bound": False, "error": "ShortSha", "divergent": "github_head", "detail": str(github_head)[:20]}
    try:
        card = _Head40(card_head)
    except ValueError:
        return {"bound": False, "error": "ShortSha", "divergent": "card_head", "detail": str(card_head)[:20]}
    ev = None
    if evidence_head is not None:
        try:
            ev = _Head40(evidence_head)
        except ValueError:
            return {"bound": False, "error": "ShortSha", "divergent": "evidence_head"}
    if str(card) != str(gh):
        return {"bound": False, "error": "CardDiverges", "divergent": "card_head",
                "expected": str(gh), "actual": str(card)}
    if ev is not None and str(ev) != str(gh):
        return {"bound": False, "error": "EvidenceStale", "divergent": "evidence_head",
                "expected": str(gh), "actual": str(ev)}
    return {"bound": True, "head": str(gh)}

def _slugify(name: str) -> str:
    return _SLUG_RE.sub("-", (name or "").strip().lower()).strip("-") or "unknown"

def rr_ensure(store: dict) -> dict:
    reg = store.setdefault("runtimes", {})
    for k, v in DEFAULT_RUNTIMES.items():
        reg.setdefault(k, {"fresh_s": v["fresh_s"], "status": "registered"})
    return reg

def rr_registered(store: dict, rt: str) -> bool:
    e = store.get("runtimes", {}).get(rt)
    return isinstance(e, dict)

def rr_register(store: dict, rt: str, provisional: bool = False) -> None:
    rt = _slugify(rt)
    fresh = PROVISIONAL_FRESH_S if provisional else HEARTBEAT_FRESH_S
    entry = {"fresh_s": fresh, "status": "provisional" if provisional else "registered",
             "first_seen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if provisional:
        entry["caps"] = {"reports_head": True, "authoritative_for_checks": False}
    store.setdefault("runtimes", {})[rt] = entry

def infer_runtime(agent: str | None, harness: str | None) -> str | None:
    hay = f"{agent or ''} {harness or ''}".lower()
    for known in DEFAULT_RUNTIMES:
        if known in hay:
            return known
    return None


# --- PR77 flight-board telemetry (verifier-owned) ----------------------------
# Fixed Sai merge-readiness rubric: product/goals 45, CI 20, Saul 20, preservation 10, hygiene 5.
FLIGHTBOARD_WEIGHTS = {"goals": 45, "ci": 20, "saul": 20, "preservation": 10, "hygiene": 5}
REQ_STATE_SCORES = {"met": 1, "partial": 0.5, "unmet": 0, "blocked": 0}  # not_applicable excluded

REQUIRED_SESSION_FIELDS = (
    "id",
    "pr",
    "agent",
    "harness",
    "model",
    "head",
    "status",
)


def load() -> dict:
    try:
        d = json.loads(DATA.read_text()) if DATA.exists() else {}
    except Exception:
        d = {}  # corrupt store -> fresh snapshot, never crash readers
    d.setdefault("sessions", {})
    d.setdefault("updated_at", None)
    d.setdefault("schema", "sai-sessions-v2")
    rr_ensure(d)
    _refresh_windows(d)
    return d

def save(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    store["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    store["schema"] = "sai-sessions-v2"
    tmp = DATA.with_suffix(".tmp")
    with open(tmp, "w") as f:
        f.write(json.dumps(store, indent=2, sort_keys=True) + "\n")
        f.flush()
        # fsync deliberately moved out of the locked write path (CPU contract):
        # os.replace is atomic for readers; a power-cut may lose the last tick,
        # never corrupt history.
    os.replace(tmp, DATA)


def cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Sessions-Token")
    handler.send_header("Cache-Control", "no-store")


def merge_list(existing, incoming, *, replace: bool = False, defaults=None):
    if replace and incoming is not None:
        base = list(incoming)
    else:
        base = list(existing or [])
        for m in incoming or []:
            if m and m not in base:
                base.append(m)
    for m in defaults or []:
        if m not in base:
            base.append(m)
    return base


def normalize_session(body: dict, prev: dict | None = None) -> dict:
    prev = prev or {}
    body = {k: v for k, v in body.items()
            if k != "flightboard" and not k.startswith("flightboard_")}  # agents never touch verdicts
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sid = str(body.get("id") or body.get("session_id") or prev.get("id") or "").strip()
    if not sid:
        pr = body.get("pr") or prev.get("pr")
        agent = body.get("agent") or prev.get("agent") or "agent"
        sid = f"sai-pr{pr}-{agent}" if pr is not None else ""
    merged = {**prev, **{k: v for k, v in body.items() if v is not None}}
    merged["id"] = sid
    merged.setdefault("agent", body.get("agent") or prev.get("agent") or "unknown")
    merged.setdefault("harness", body.get("harness") or prev.get("harness") or merged["agent"])
    merged.setdefault("model", body.get("model") or prev.get("model") or "unknown")
    merged["status"] = str(body.get("status") or prev.get("status") or "tracked").strip().lower()
    if body.get("monitors") is not None or not prev.get("monitors"):
        merged["monitors"] = merge_list(prev.get("monitors"), body.get("monitors"), defaults=DEFAULT_MONITORS)
    tags = list(prev.get("tags") or [])
    for t in body.get("tags") or []:
        if t and t not in tags:
            tags.append(t)
    for t in (merged.get("agent"), merged.get("harness"), f"model:{merged.get('model')}"):
        if t and t not in tags:
            tags.append(str(t))
    merged["tags"] = tags
    merged["updated_at"] = now
    merged["heartbeat_at"] = body.get("heartbeat_at") or now
    merged["created_at"] = prev.get("created_at") or now
    return merged


def missing_required(sess: dict) -> list:
    miss = []
    for k in REQUIRED_SESSION_FIELDS:
        v = sess.get(k)
        if v is None or v == "":
            miss.append(k)
    try:
        int(sess.get("pr"))
    except Exception:
        if "pr" not in miss:
            miss.append("pr")
    return miss



def _fresh_s_for(sess: dict) -> int:
    return _FRESH_WINDOWS.get(str(sess.get("runtime") or ""), HEARTBEAT_FRESH_S)

def heartbeat_age_s(sess: dict):
    """Derive age from heartbeat_at. Null if missing/invalid — never invent 0 for absent.

    Honesty contract (API-F4): a timestamp that is missing, null, empty, NaN,
    non-ISO garbage, or implausibly in the future (beyond CLOCK_SKEW_TOLERANCE_S,
    i.e. a corrupted writer clock) yields None -> liveness "missing". A bad or
    future-dated timestamp must NEVER be coerced into stale OR fresh.
    """
    hb = sess.get("heartbeat_at")
    if not hb:
        return None
    try:
        from datetime import datetime, timezone
        s = str(hb).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        t = datetime.fromisoformat(s)
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        age = int((datetime.now(timezone.utc) - t).total_seconds())
        if age < -CLOCK_SKEW_TOLERANCE_S:
            # Future-dated timestamp = garbage clock, not evidence of life.
            return None
        return age
    except Exception:
        return None


def liveness(sess: dict) -> str:
    """fresh/stale/missing from heartbeat_at, judged on THIS session's runtime window."""
    age = heartbeat_age_s(sess)
    if age is None:
        return "missing"
    return "fresh" if age < _fresh_s_for(sess) else "stale"


def enrich(sess: dict) -> dict:
    """Server-side honest enrichment: computed age + liveness + status-recognition + runtime hint."""
    out = dict(sess)
    if not out.get("runtime"):
        inferred = infer_runtime(out.get("agent"), out.get("harness"))
        if inferred:
            out["runtime"] = inferred
    out["heartbeat_age_s"] = heartbeat_age_s(sess)
    out["liveness"] = liveness(sess)
    if _PROVISIONAL_RUNTIMES.get(str(out.get("runtime") or "")):
        out["registration"] = "provisional"
    st = sess.get("status")
    if st is not None and str(st).strip().lower() not in KNOWN_STATUSES:
        out["status_recognized"] = False
    else:
        out.pop("status_recognized", None)
    return out


def with_heartbeat_age(sess: dict) -> dict:
    return enrich(sess)
def _req_states(raw):
    """Normalize verifier requirement map {id: state|{state,reason}}. None = malformed authority."""
    if not isinstance(raw, dict) or not raw:
        return None
    out = {}
    for rid, v in raw.items():
        st = v.get("state") if isinstance(v, dict) else v
        st = str(st or "").strip().lower()
        if st == "not_applicable":
            reason = v.get("reason") if isinstance(v, dict) else None
            if not (reason and str(reason).strip()):
                return None  # not_applicable requires an explicit reason; malformed -> unavailable
            out[str(rid)] = "not_applicable"
        elif st in REQ_STATE_SCORES:
            out[str(rid)] = st
        else:
            return None
    return out


def _prop_component(ev, total):
    """Proportional component credit from {required:N, green:G}; None when evidence missing/malformed."""
    if not isinstance(ev, dict):
        return None
    try:
        req, green = int(ev.get("required")), int(ev.get("green"))
    except Exception:
        return None
    if req <= 0 or green < 0 or green > req:
        return None
    return round(green / req * total)


def flightboard_for_pr(pr: int, store: dict) -> dict:
    """PR77 /goal flight-board telemetry. Verifier/aggregator-OWNED computation only.

    Reads exclusively from the store-level `flightboard` namespace written via the
    authenticated /api/hermes-sessions/flightboard/{pr} endpoint. Agent session payloads
    (including self-reported progress.pct) are NEVER consulted -- no self-award path exists.
    Missing or malformed authority => null values with source 'unavailable', never invented numbers.
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    unavailable = {
        "implementation_pct": None,
        "requirements": None,
        "merge_readiness_pct": None,
        "merge_components": None,
        "head_sha": None,
        "computed_at": now,
        "source": "unavailable",
    }
    fb_ns = store.get("flightboard")
    fb = fb_ns.get(str(pr)) if isinstance(fb_ns, dict) else None  # junk namespace -> unavailable, never AttributeError
    if not isinstance(fb, dict):
        return unavailable
    head_sha = fb.get("head_sha") or None
    states = _req_states(fb.get("requirements"))
    if states is None:
        return {**unavailable, "head_sha": head_sha}
    applicable = [s for s in states.values() if s != "not_applicable"]
    earned = sum(REQ_STATE_SCORES[s] for s in applicable)
    impl_pct = round(earned / len(applicable) * 100) if applicable else None
    counts = {k: sum(1 for s in states.values() if s == k)
              for k in ("met", "partial", "unmet", "blocked", "not_applicable")}
    goals = round(impl_pct * FLIGHTBOARD_WEIGHTS["goals"] / 100) if impl_pct is not None else None
    ci = _prop_component(fb.get("ci"), FLIGHTBOARD_WEIGHTS["ci"])
    presv = _prop_component(fb.get("preservation"), FLIGHTBOARD_WEIGHTS["preservation"])
    saul_ev = fb.get("saul") if isinstance(fb.get("saul"), dict) else None
    saul = p0 = p1 = p2 = None
    if saul_ev is not None:
        try:
            genuine = bool(saul_ev.get("genuine_exact_head"))
            p0, p1, p2 = int(saul_ev.get("p0")), int(saul_ev.get("p1")), int(saul_ev.get("p2"))
            saul = FLIGHTBOARD_WEIGHTS["saul"] if (genuine and p0 == p1 == p2 == 0) else 0
        except Exception:
            saul = None
    hygiene = FLIGHTBOARD_WEIGHTS["hygiene"] if fb.get("hygiene") is True else (0 if fb.get("hygiene") is False else None)
    components = {"goals": goals, "ci": ci, "saul": saul, "preservation": presv, "hygiene": hygiene}
    readiness = None
    source = "verifier"
    if impl_pct is not None and all(v is not None for v in components.values()):
        caps = []
        if p0 > 0:
            caps.append(20)
        elif p1 > 0:
            caps.append(60)
        elif p2 > 0:
            caps.append(85)
        if components["ci"] < FLIGHTBOARD_WEIGHTS["ci"]:
            caps.append(70)
        if components["saul"] < FLIGHTBOARD_WEIGHTS["saul"]:
            caps.append(90)
        if components["hygiene"] < FLIGHTBOARD_WEIGHTS["hygiene"]:
            caps.append(90)
        readiness = min([sum(components.values())] + caps)
    else:
        source = "unavailable"  # partial evidence: full rubric not computable honestly
    return {
        "implementation_pct": impl_pct,
        "requirements": counts,
        "merge_readiness_pct": readiness,
        "merge_components": components,
        "head_sha": head_sha,
        "computed_at": fb.get("computed_at") or fb.get("updated_at") or now,
        "source": source,
    }




def _safe_int(v) -> int:
    """Non-numeric junk sums as 0; explicit numeric 0 preserved (never fabricated)."""
    try:
        return int(v)
    except Exception:
        return 0


def group_by_pr(sessions: list) -> list:
    by = {}
    for s in sessions:
        try:
            pr = int(s.get("pr"))
        except Exception:
            continue
        by.setdefault(pr, []).append(s)
    cards = []
    for pr, agents in sorted(by.items(), reverse=True):
        agents_sorted = sorted(agents, key=lambda x: (x.get("agent") or "", x.get("id") or ""))
        heads = [a.get("head") for a in agents_sorted if a.get("head")]
        usage_sum = sum(_safe_int((a.get("usage") or {}).get("total_tokens")) for a in agents_sorted if isinstance(a.get("usage"), dict))
        diff_sum = sum(
            (_safe_int((a.get("diff") or {}).get("file_count"))
             if (a.get("diff") or {}).get("file_count") is not None
             else len((a.get("diff") or {}).get("files") or []))
            for a in agents_sorted if isinstance(a.get("diff"), dict))
        cards.append({
            "pr": pr,
            "agents": agents_sorted,
            "agent_count": len(agents_sorted),
            "heads": list(dict.fromkeys(heads)),
            "updated_at": max((a.get("updated_at") or "") for a in agents_sorted),
            "usage_total_tokens": usage_sum,
            "diff_file_count": diff_sum,
        })
    return cards


def _observe_rate_headers(headers) -> None:
    """API-F007: track X-RateLimit-Remaining; on exhaustion arm a fail-fast cooldown.

    Cooldown lasts until X-RateLimit-Reset (capped at 15 min) or 60s when no
    reset header is present. Anonymous quota is 60 req/hr — honoring it keeps
    repeated /prs polls from hammering GitHub into a longer hard ban.
    """
    global _RATE_COOLDOWN_UNTIL, _RATE_LAST_REMAINING
    try:
        rem = headers.get("X-RateLimit-Remaining")
        if rem is not None:
            with _RATE_LOCK:
                _RATE_LAST_REMAINING = int(rem)
                if _RATE_LAST_REMAINING <= 0:
                    reset = headers.get("X-RateLimit-Reset")
                    until = time.monotonic() + 60.0
                    if reset is not None:
                        wait = min(max(float(reset) - time.time(), 1.0), 900.0)
                        until = max(until, time.monotonic() + wait)
                    _RATE_COOLDOWN_UNTIL = until
    except Exception:
        pass


def rate_limited_now() -> bool:
    with _RATE_LOCK:
        return time.monotonic() < _RATE_COOLDOWN_UNTIL


def _gh_get(url: str):
    """API-F101/F007: GET the PUBLIC GitHub API -> (http_status|None, json|None).

    PUBLIC DATA ONLY: never attaches any Authorization header even if tokens are
    present in the environment (repo is public; tokens must never live in this
    API process). Explicit timeout; rate-aware fail-fast while a cooldown from
    exhausted X-RateLimit is armed. Never raises.
    """
    if rate_limited_now():
        return 429, None
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-sessions-api",
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:  # explicit timeout: degrade, never hang
            raw = resp.read()
            _observe_rate_headers(dict(resp.headers))
            try:
                return resp.status, json.loads(raw.decode("utf-8"))
            except Exception:
                return resp.status, None
    except urllib.error.HTTPError as e:
        try:
            _observe_rate_headers(dict(e.headers or {}))
        except Exception:
            pass
        if e.code in (403, 429):
            # Anonymous quota/abuse limiter hit: arm cooldown so later polls back off.
            global _RATE_COOLDOWN_UNTIL
            with _RATE_LOCK:
                _RATE_COOLDOWN_UNTIL = max(_RATE_COOLDOWN_UNTIL, time.monotonic() + 60.0)
        return e.code, None
    except Exception:
        return None, None


def fetch_check_runs(repo: str, sha: str) -> dict:
    """Paginated check-runs for ONE exact HEAD sha.

    Returns {"runs": [...], "incomplete": bool, "status": int|None, "stale": bool}.
    Fresh results are cached per sha for CI_CACHE_TTL_S; on fetch failure a stale
    cache entry is served up to CI_STALE_OK_S with stale=True. Never raises.
    """
    now = time.monotonic()
    with _CI_CACHE_LOCK:
        hit = _CI_CACHE.get(sha)
        if hit and now - hit[0] <= CI_CACHE_TTL_S:
            _, runs, incomplete, status_code = hit
            return {"runs": list(runs), "incomplete": incomplete, "status": status_code, "stale": False}
    runs: list = []
    incomplete = False
    status_code = None
    ok = True
    page = 1
    while page <= CHECK_RUNS_MAX_PAGES:
        st, data = _gh_get(f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs?per_page=100&page={page}")
        if status_code is None:
            status_code = st
        if st != 200 or not isinstance(data, dict):
            ok = False
            break
        batch = data.get("check_runs") or []
        runs.extend(batch)
        if data.get("incomplete_results") is True:
            incomplete = True
        if len(batch) < 100:
            break
        if page == CHECK_RUNS_MAX_PAGES:
            incomplete = True  # stopped because of our own page cap
        page += 1
    if ok:
        with _CI_CACHE_LOCK:
            _CI_CACHE[sha] = (time.monotonic(), runs, incomplete, status_code)
        return {"runs": runs, "incomplete": incomplete, "status": status_code, "stale": False}
    with _CI_CACHE_LOCK:
        hit = _CI_CACHE.get(sha)
    if hit and time.monotonic() - hit[0] <= CI_STALE_OK_S:
        _, cruns, cincomplete, cstatus = hit
        return {"runs": list(cruns), "incomplete": cincomplete, "status": cstatus, "stale": True}
    return {"runs": [], "incomplete": False, "status": status_code, "stale": False}


def fetch_pr_head(repo: str, pr) -> str | None:
    """API-F008: current PR tip HEAD sha via the public pulls API.

    Short-TTL cached (PR_HEAD_TTL_S on success, PR_HEAD_FAIL_TTL_S on failure).
    Public-data-only: uses _gh_get (never sends auth headers). Never raises;
    returns None when the tip cannot be resolved.
    """
    try:
        pr_i = int(pr)
    except (TypeError, ValueError):
        return None
    if pr_i <= 0:
        return None
    now = time.monotonic()
    with _CI_CACHE_LOCK:
        hit = _PR_HEAD_CACHE.get(pr_i)
        if hit:
            ts, sha, ok = hit
            if now - ts <= (PR_HEAD_TTL_S if ok else PR_HEAD_FAIL_TTL_S):
                return sha
    try:
        st, data = _gh_get(f"https://api.github.com/repos/{repo}/pulls/{pr_i}")
    except Exception:
        st, data = None, None
    sha = None
    ok = False
    if st == 200 and isinstance(data, dict):
        head = data.get("head") or {}
        cand = str(head.get("sha") or "").strip().lower()
        if _SHA40_RE.match(cand):
            sha = cand
            ok = True
    with _CI_CACHE_LOCK:
        _PR_HEAD_CACHE[pr_i] = (time.monotonic(), sha, ok)
    return sha


def _saul_synthetic_pieces(saul_agents: list) -> list:
    """API-F101: Saul action_required/fail is BOTH a CI piece AND stays a Saul score component."""
    out = []
    for a in saul_agents or []:
        review = a.get("review") or {}
        concl = str(review.get("conclusion") or "").strip().lower()
        if concl not in FAILING_CONCLUSIONS:
            continue
        out.append({
            "name": f"saul-review/{a.get('id') or a.get('agent')}",
            "conclusion": concl,
            "required": None,
            "job_url": review.get("check_run_url") or review.get("html_url"),
            "head_sha": review.get("head_sha") or a.get("head_full"),
            "source": "saul-review",
        })
    return out


def build_ci_block(head_fulls, saul_agents, pr=None) -> dict:
    """Honest CI failing-pieces block from paginated check-runs on exact HEAD shas.

    API-F008 tip-exactness: when `pr` is given, the CURRENT PR tip is resolved
    live and (a) check-runs are also fetched for the tip itself and (b) every
    emitted piece's head_sha must equal the current tip. Stale-SHA pieces left
    over from a mid-window push are filtered out — never served as if current.
    """
    repo = os.environ.get("SESSIONS_GH_REPO") or GH_REPO_DEFAULT
    shas = sorted({str(h).strip().lower() for h in (head_fulls or []) if isinstance(h, str) and _SHA40_RE.match(str(h).strip().lower())})
    tip_sha = fetch_pr_head(repo, pr) if pr is not None else None
    check_shas = list(shas)
    if tip_sha and tip_sha not in check_shas:
        check_shas.append(tip_sha)
    pieces: list = []
    seen = set()

    def _add(p: dict) -> None:
        key = (p.get("name"), p.get("conclusion"), p.get("job_url"), p.get("head_sha"))
        if key not in seen:
            seen.add(key)
            pieces.append(p)

    for p in _saul_synthetic_pieces(saul_agents):
        _add(p)

    total = 0
    incomplete = False
    statuses = []
    stale_any = False
    fetched_any = False
    for sha in check_shas:
        res = fetch_check_runs(repo, sha)
        if res.get("stale"):
            stale_any = True
        st = res.get("status")
        statuses.append(st)
        if st == 200:
            fetched_any = True
        else:
            continue
        total += len(res.get("runs") or [])
        incomplete = incomplete or bool(res.get("incomplete"))
        for r in res.get("runs") or []:
            concl = str(r.get("conclusion") or "").strip().lower()
            if concl not in FAILING_CONCLUSIONS:
                continue  # pending (queued/in_progress), skipped, neutral, success: NOT failing
            _add({
                "name": r.get("name"),
                "conclusion": concl,
                "status": r.get("status"),
                "required": None,  # GitHub check-runs do not expose requiredness — honest null
                "job_url": r.get("html_url") or r.get("details_url"),
                "head_sha": sha,
                "source": "github-check-runs",
            })

    # API-F008: validate every piece against the CURRENT tip; stale-SHA pieces
    # from a mid-window push cannot leak even out of a fresh/stale cache entry.
    # (Filter BEFORE the block dict captures the list reference.)
    dropped_stale = 0
    if tip_sha:
        before = len(pieces)
        pieces = [p for p in pieces if p.get("head_sha") == tip_sha]
        dropped_stale = before - len(pieces)
    tip_unresolved = pr is not None and not tip_sha

    block = {
        "ci_available": True,
        "ci_failing_pieces": pieces,
        "ci_pieces": pieces,  # API-F007 lane alias: per exact-HEAD check facet
        "ci_failing_count": len(pieces),
        "ci_checks_total": total,
        "ci_head_shas": check_shas,
        "ci_tip_sha": tip_sha,
        "ci_incomplete": incomplete,
        "partial": bool(incomplete),   # page-cap or GitHub incomplete_results -> partial truth
        "source": "github-check-runs",
        "ci_computed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ci_source": "github-check-runs",
    }
    if not shas:
        block["ci_available"] = False
        block["ci_reason"] = "no_full_head_sha"
    elif shas and not fetched_any:
        block["ci_available"] = False
        if any(s in (403, 429) for s in statuses):
            block["ci_reason"] = "rate_limited"
            with _RATE_LOCK:
                if _RATE_LAST_REMAINING is not None:
                    block["rate_remaining_last_seen"] = _RATE_LAST_REMAINING
        else:
            block["ci_reason"] = "github_unavailable"
        http_statuses = [s for s in statuses if s is not None]
        if http_statuses:
            block["ci_http_status"] = http_statuses[0]
    if not block["ci_available"]:
        # Lane contract: authority failure degrades to {partial:true, source:unavailable}.
        block["partial"] = True
        block["source"] = "unavailable"
    if stale_any:
        block["ci_stale"] = True
    if tip_unresolved:
        # Tip could not be verified: never imply tip-exact truth we did not confirm.
        block["ci_tip_unresolved"] = True
        block["ci_tip_reason"] = "pr_tip_unresolved"
        block["partial"] = True
    elif tip_sha and tip_sha not in shas:
        block["ci_tip_ahead_of_session_heads"] = True
    if dropped_stale > 0:
        # Previously-failing set emptied/trimmed by tip movement: honest partial, never all-green.
        block["ci_tip_moved"] = True
        block["ci_tip_reason"] = "stale-SHA failing pieces filtered after PR tip movement"
        block["ci_tip_dropped_pieces"] = dropped_stale
        block["partial"] = True
    return block


def attach_ci_blocks(cards: list) -> None:
    """API-F101/F007: mutate /prs cards with live CI failing pieces. Never raises."""
    for card in cards:
        try:
            agents = card.get("agents") or []
            head_fulls = [a.get("head_full") for a in agents if a.get("head_full")]
            saul_agents = [a for a in agents if (a.get("agent") == "saul" or "saul" in str(a.get("harness") or "").lower())]
            block = build_ci_block(head_fulls, saul_agents, pr=card.get("pr"))
            prog = card.get("progress")
            if isinstance(prog, dict):
                prog_out = dict(prog)
            elif isinstance(prog, str):
                prog_out = {"state": prog}
            elif prog is None:
                prog_out = {}
            else:
                prog_out = {}
            prog_out.update(block)
            card["progress"] = prog_out
            card["ci_failing_pieces"] = block.get("ci_failing_pieces", [])
            card["ci_pieces"] = block.get("ci_pieces", [])  # API-F007 lane alias
            card["ci_failing_count"] = block.get("ci_failing_count", 0)
        except Exception:
            continue

def decorate_cards(cards: list, store: dict) -> list:
    """Shared card enrichment: verifier flightboard telemetry + head-binding assertion."""
    for c in cards:
        c["flightboard"] = flightboard_for_pr(c["pr"], store)
        gh_tip = fetch_pr_head("Dezocode/Sai", c["pr"])
        card_head = c.get("latest_head_full") or (c.get("heads") or [""])[0]
        c["head_binding"] = assert_head_binding(gh_tip or "", card_head or "", None)
    return cards


def idem_key_of(headers_get, body: dict) -> str:
    """M17 durable idempotency: Idempotency-Key header wins, body request_id/idempotency_key fallback."""
    k = (headers_get("Idempotency-Key") or "").strip()
    if not k and isinstance(body, dict):
        k = str(body.get("request_id") or body.get("idempotency_key") or "").strip()
    return k


def _idem_ts(entry: dict) -> float:
    try:
        return time.mktime(time.strptime(entry.get("created_at"), "%Y-%m-%dT%H:%M:%SZ"))
    except Exception:
        return 0.0


def idem_lookup(store: dict, key: str) -> dict | None:
    entry = (store.get("idempotency") or {}).get(key)
    if not entry:
        return None
    if time.time() - _idem_ts(entry) > IDEMPOTENCY_TTL_S:
        (store.setdefault("idempotency", {})).pop(key, None)
        return None
    return entry


def idem_remember(store: dict, key: str | None, path: str, code: int, response: dict) -> None:
    """Persist a replay record so retried writes survive process restarts. Errors are not cached."""
    if not key or code >= 400:
        return
    tab = store.setdefault("idempotency", {})
    tab[key] = {
        "path": path,
        "code": code,
        "response": response,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    for k in list(tab.keys()):
        if time.time() - _idem_ts(tab[k]) > IDEMPOTENCY_TTL_S:
            del tab[k]
    while len(tab) > IDEMPOTENCY_MAX_KEYS:
        oldest = min(tab, key=lambda k: tab[k].get("created_at") or "")
        del tab[oldest]



def normalize_api_path(path: str) -> str:
    """Map /api/agent-sessions/* to /api/hermes-sessions/* for shared handlers."""
    if path == "/api/agent-sessions" or path.startswith("/api/agent-sessions/"):
        return "/api/hermes-sessions" + path[len("/api/agent-sessions"):]
    return path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _auth_write(self) -> bool:
        if not WRITE_TOKEN:
            return False  # DECIDED: fail-closed — an unconfigured deployment refuses writes
        auth = self.headers.get("Authorization", "")
        tok = self.headers.get("X-Sessions-Token", "")
        if auth.startswith("Bearer "):
            tok = auth[7:].strip() or tok
        return tok == WRITE_TOKEN

    def _json(self, code: int, payload, headers: dict | None = None) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        cors(self)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        cors(self)
        self.end_headers()

    def do_GET(self) -> None:
        path = normalize_api_path(urlparse(self.path).path.rstrip("/") or "/")
        qs = parse_qs(urlparse(self.path).query)
        # DECIDED: reads are LOCK-FREE — os.replace atomicity guarantees a consistent
        # snapshot; writers hold the lock, readers never wait on them.
        store = load()
        sessions = [s for s in store.get("sessions", {}).values() if isinstance(s, dict)]
        rr_ensure(store)
        if path in ("/", "/health", "/api/hermes-sessions/health"):
            return self._json(200, {
                "ok": True,
                "service": "hermes-sessions",
                "schema": store.get("schema", "sai-sessions-v2"),
                "count": len(sessions),
                "required_fields": list(REQUIRED_SESSION_FIELDS),
                "card_fields": ["usage", "diff", "harness", "model", "head", "progress", "review", "progress.ci_failing_pieces"],
                "statuses": {"active": list(ACTIVE_STATUSES), "terminal": list(TERMINAL_STATUSES)},
                "heartbeat_fresh_s": HEARTBEAT_FRESH_S,
                "liveness_values": ["fresh", "stale", "missing"],
            })
        if path in ("/prs", "/api/hermes-sessions/prs"):
            status = (qs.get("status") or [None])[0]
            monitor = (qs.get("monitor") or [None])[0]
            agent = (qs.get("agent") or [None])[0]
            out = sessions
            if status:
                out = [s for s in out if s.get("status") == status]
            if monitor:
                out = [s for s in out if monitor in (s.get("monitors") or [])]
            if agent:
                out = [s for s in out if s.get("agent") == agent]
            out = [with_heartbeat_age(s) for s in out]
            cards = group_by_pr(out)
            try:
                attach_ci_blocks(cards)
            except Exception:
                pass  # CI enrichment must never 500 /prs
            decorate_cards(cards, store)
            return self._json(200, {"prs": cards, "count": len(cards), "updated_at": store.get("updated_at"), "schema": "sai-sessions-v2"})
        if path in ("/sessions", "/api/hermes-sessions", "/api/hermes-sessions/sessions"):
            status = (qs.get("status") or [None])[0]
            active_only = (qs.get("active") or ["0"])[0] in ("1", "true", "yes")
            monitor = (qs.get("monitor") or [None])[0]
            agent = (qs.get("agent") or [None])[0]
            pr_f = (qs.get("pr") or [None])[0]
            group = (qs.get("group") or ["0"])[0] in ("1", "true", "yes")
            out = sessions
            if status:
                out = [s for s in out if s.get("status") == status]
            if active_only:
                out = [s for s in out if s.get("status") in ("active", "running", "spawned", "tracked", "launched", "reviewing")]
            if monitor:
                out = [s for s in out if monitor in (s.get("monitors") or [])]
            if agent:
                out = [s for s in out if s.get("agent") == agent]
            if pr_f:
                try:
                    prn = int(pr_f)
                    out = [s for s in out if int(s.get("pr") or -1) == prn]
                except Exception:
                    pass
            if group:
                out = [with_heartbeat_age(s) for s in out]
                cards = group_by_pr(out)
                decorate_cards(cards, store)
                return self._json(200, {"prs": cards, "updated_at": store.get("updated_at"), "schema": "sai-sessions-v2"})
            def _pr_num(v):
                try:
                    return int(v)
                except Exception:
                    return -1  # garbage pr sorts last, never crashes (API-F6)
            out.sort(key=lambda s: (_pr_num(s.get("pr")), s.get("agent") or "", s.get("updated_at") or ""), reverse=True)
            out = [with_heartbeat_age(s) for s in out]
            return self._json(200, {"sessions": out, "updated_at": store.get("updated_at"), "count": len(out), "schema": "sai-sessions-v2"})
        if ("/by-pr/" not in path) and (path.startswith("/sessions/") or path.startswith("/api/hermes-sessions/sessions/")):
            sid = path.rsplit("/", 1)[-1]
            if sid in ("heartbeat", "monitors"):
                return self._json(404, {"error": "not_found"})
            with LOCK:
                s = load().get("sessions", {}).get(sid)
            if not isinstance(s, dict):
                return self._json(404, {"error": "not_found"})
            return self._json(200, with_heartbeat_age(s))
        if "/by-pr/" in path:
            try:
                pr = int(path.rsplit("/", 1)[-1])
            except ValueError:
                return self._json(400, {"error": "bad_pr"})
            out = [with_heartbeat_age(s) for s in sessions if int(s.get("pr") or 0) == pr]
            card = group_by_pr(out)[0] if out else None
            if card:
                card["flightboard"] = flightboard_for_pr(pr, store)
            return self._json(200, {
                "pr": pr,
                "sessions": out,
                "agents": out,
                "card": card,
                "flightboard": card["flightboard"] if card else flightboard_for_pr(pr, store),
                "count": len(out),
            })

        if path in ("/spawns", "/api/hermes-sessions/spawns"):
            """M17: thin, secret-free, read-only join surface for PR77's GitHub-fields plane.

            One row per PR (union partner for the GitHub pulls list): agent roster with
            head/head_full/status/liveness so the dashboard can join by PR number and
            compute session-vs-PR HEAD mismatch without any credentials.
            """
            cards = group_by_pr([enrich(s) for s in sessions])
            prs = []
            for card in cards:
                agents = [{
                    "id": a.get("id"),
                    "agent": a.get("agent"),
                    "harness": a.get("harness"),
                    "model": a.get("model"),
                    "status": a.get("status"),
                    "phase": a.get("phase"),
                    "head": a.get("head"),
                    "head_full": a.get("head_full"),
                    "heartbeat_at": a.get("heartbeat_at"),
                    "heartbeat_age_s": a.get("heartbeat_age_s"),
                    "liveness": a.get("liveness"),
                    "updated_at": a.get("updated_at"),
                } for a in card["agents"]]
                lv = {"fresh": 0, "stale": 0, "missing": 0}
                for a in card["agents"]:
                    l = a.get("liveness")
                    if l in lv:
                        lv[l] += 1
                with_heads = sorted(
                    ((a.get("updated_at") or "", a.get("head_full")) for a in card["agents"] if a.get("head_full")),
                )
                prs.append({
                    "pr": card["pr"],
                    "agents": agents,
                    "agent_count": card["agent_count"],
                    "heads": card["heads"],
                    # null = cannot determine honestly (no head_full present)
                    "session_heads_differ": len({h for _, h in with_heads}) > 1 if with_heads else None,
                    "latest_head_full": with_heads[-1][1] if with_heads else None,
                    "liveness": lv,
                    "any_active": any((a.get("status") or "") in ACTIVE_STATUSES for a in card["agents"]),
                    "updated_at": card["updated_at"],
                })
            return self._json(200, {
                "schema": "sai-sessions-v2",
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "prs": prs,
                "pr_keys": [c["pr"] for c in cards],
                "count": len(prs),
            })
        # Registry vocabulary — public read
        if path in ("/api/runtime-registry", "/runtime-registry"):
            return self._json(200, {"schema": "sai-sessions-v2", "runtimes": store.get("runtimes", {})})
        # Head-binding assertion — exact-head check per PR
        if path.startswith("/head-binding/") or path.startswith("/api/agent-sessions/head-binding/") \
           or path.startswith("/api/hermes-sessions/head-binding/"):
            try:
                prn = int(path.rstrip("/").rsplit("/", 1)[-1])
            except ValueError:
                return self._json(400, {"error": "bad_pr"})
            gh_tip = fetch_pr_head("Dezocode/Sai", prn)
            card_sessions = [s for s in sessions if int(s.get("pr") or 0) == prn]
            card_heads = {s.get("head_full") or s.get("head") for s in card_sessions if s.get("head_full") or s.get("head")}
            card_head = sorted(card_heads)[-1] if card_heads else None
            result = assert_head_binding(gh_tip or "", card_head or "", None)
            return self._json(200 if result.get("bound") else 409, result)
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self) -> None:
        if not self._auth_write():
            return self._json(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except Exception:
            return self._json(400, {"error": "invalid_json"})
        path = normalize_api_path(urlparse(self.path).path.rstrip("/") or "/")
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Reconcile pull adapter — scheduled + budget-guarded, never a busy loop
        if path in ("/api/agent-sessions/reconcile", "/api/hermes-sessions/reconcile", "/reconcile"):
            if rate_limited_now():
                return self._json(429, {"error": "RATE_BUDGET_EXHAUSTED"})
            scope = body.get("pr")
            with LOCK:
                store = load()
                rr_ensure(store)
                prs_set = sorted({int(s["pr"]) for s in store.get("sessions", {}).values() if isinstance(s, dict) and isinstance(s.get("pr"), int)} | ({int(scope)} if scope else set()))
            report = {"created": [], "updated": [], "checked_prs": prs_set}
            for pr in prs_set:
                head_full = fetch_pr_head("Dezocode/Sai", pr)
                if not _SHA40_RE.match(head_full or ""):
                    continue
                data = fetch_check_runs("Dezocode/Sai", head_full)
                for run in sorted(data.get("runs") or [], key=lambda r: str(r.get("name"))):
                    name = str(run.get("name") or "")
                    slug = _slugify(name)
                    if not slug.startswith("cursor"):
                        continue
                    status_map = {"in_progress": "running", "queued": "running"}
                    concl = run.get("conclusion")
                    status = status_map.get(run.get("status")) or status_map.get(concl) or (
                        "failed" if concl in FAILING_CONCLUSIONS else "done")
                    sid = f"sai-pr{pr}-cursor-{slug}"
                    prev = load().get("sessions", {}).get(sid) or {}
                    sess = normalize_session({
                        "id": sid, "pr": pr, "agent": f"cursor-{slug}",
                        "harness": "cursor-checks", "model": name,
                        "runtime": "cursor", "origin": "pull:github_checks",
                        "head": head_full[:8], "head_full": head_full,
                        "status": status,
                    }, prev)
                    with LOCK:
                        store2 = load()
                        store2.setdefault("sessions", {})[sid] = sess
                        save(store2)
                    (report["created"] if not prev else report["updated"]).append(sid)
            return self._json(200, {"schema": "sai-sessions-v2", **report})

        # register_runtime door — VERIFIER_TOKEN class (same secret today; split documented in spec §5.1)
        if path == "/api/runtime-registry" or path == "/runtime-registry":
            rt_raw = str(body.get("rt") or body.get("runtime") or "").strip()
            if not rt_raw:
                return self._json(422, {"error": "INVALID_SLUG"})
            rt = _slugify(rt_raw)
            fresh_s = max(1, int(body.get("fresh_s") or HEARTBEAT_FRESH_S))
            caps = body.get("caps") if isinstance(body.get("caps"), dict) else {"reports_head": True}
            with LOCK:
                store = load()
                rr_ensure(store)
                reg = store.setdefault("runtimes", {})
                existed = rt in reg
                reg[rt] = {"fresh_s": fresh_s, "caps": caps, "status": "registered",
                           "registered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                _refresh_windows(store)
                save(store)
            return self._json(201 if not existed else 200, {"runtime": rt, "fresh_s": fresh_s, "existed": existed})

        # Heartbeat door — top-level accepting {runtime, pr, status, head, model?, note?}
        if path in ("/api/agent-sessions/heartbeat", "/api/hermes-sessions/heartbeat", "/heartbeat"):
            # strip flightboard keys — agents never touch merge truth
            body = {k: v for k, v in body.items()
                    if k != "flightboard" and not k.startswith("flightboard_")}
            with LOCK:
                store = load()
                rr_ensure(store)
                _refresh_windows(store)
                rt_raw = str(body.get("runtime") or "").strip()
                if rt_raw:
                    if not rr_registered(store, rt_raw):
                        if AUTOREGISTER:
                            rr_register(store, rt_raw, provisional=True)
                            _refresh_windows(store)
                        else:
                            return self._json(422, {"error": "RUNTIME_AUTOREGISTER_DISABLED",
                                                    "runtime": rt_raw,
                                                    "registered": sorted((store.get("runtimes") or {}).keys())})
                ikey = idem_key_of(self.headers.get, body)
                hit = idem_lookup(store, ikey) if ikey else None
                if hit:
                    return self._json(int(hit.get("code") or 200), hit["response"], headers={"Idempotency-Replayed": "true"})
                prn = body.get("pr")
                agent = body.get("agent") or rt_raw or "unknown"
                sid = f"sai-pr{prn}-{agent}" if prn is not None else f"hb-{_slugify(agent)}"
                prev = store.setdefault("sessions", {}).get(sid, {})
                sess = normalize_session({**body, "id": sid, "runtime": rt_raw or infer_runtime(agent, "") or agent}, prev)
                sess["heartbeat_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                sess["updated_at"] = sess["heartbeat_at"]
                miss = missing_required(sess)
                for k in miss:
                    if prev.get(k) is not None: sess[k] = prev[k]
                miss2 = missing_required(sess)
                if miss2:
                    return self._json(400, {"error": "missing_required_fields", "missing": miss2})
                store["sessions"][sid] = sess
                idem_remember(store, ikey, path, 200, sess)
                save(store)
            return self._json(200, enrich(sess))

        # PR77 flight-board: verifier/aggregator-owned evidence endpoint. Requires write auth.
        if path.startswith("/api/hermes-sessions/flightboard/") or path.startswith("/flightboard/"):
            try:
                prn = int(path.rstrip("/").rsplit("/", 1)[-1])
            except ValueError:
                return self._json(400, {"error": "bad_pr"})
            allowed = {"head_sha", "requirements", "ci", "saul", "preservation", "hygiene"}
            rec = {k: body[k] for k in allowed if k in body}
            with LOCK:
                store = load()
                ikey = idem_key_of(self.headers.get, body)
                hit = idem_lookup(store, ikey) if ikey else None
                if hit:
                    return self._json(int(hit.get("code") or 200), hit["response"], headers={"Idempotency-Replayed": "true"})
                tab = store.setdefault("flightboard", {})
                prev_fb = tab.get(str(prn)) or {}
                merged_fb = {**prev_fb, **rec}
                merged_fb["updated_at"] = now
                merged_fb["computed_at"] = now
                tab[str(prn)] = merged_fb
                idem_remember(store, ikey, path, 200, merged_fb)
                save(store)
            return self._json(200, {"pr": prn, "flightboard": flightboard_for_pr(prn, store)})


        if path.endswith("/monitors"):
            sid = path.split("/")[-2]
            ikey = idem_key_of(self.headers.get, body)
            with LOCK:
                store = load()
                hit = idem_lookup(store, ikey) if ikey else None
                if hit:
                    return self._json(int(hit.get("code") or 200), hit["response"], headers={"Idempotency-Replayed": "true"})
                s = store.setdefault("sessions", {}).get(sid)
                if not s:
                    return self._json(404, {"error": "not_found"})
                mons = list(s.get("monitors") or [])
                if "monitors" in body and body.get("replace") is True:
                    mons = list(body.get("monitors") or [])
                else:
                    for a in body.get("add") or body.get("monitors") or []:
                        if a and a not in mons:
                            mons.append(a)
                    for r in body.get("remove") or []:
                        mons = [x for x in mons if x != r]
                if "origin-grokbot" not in (body.get("remove") or []):
                    if "origin-grokbot" not in mons:
                        mons.append("origin-grokbot")
                s["monitors"] = mons
                s["updated_at"] = now
                store["sessions"][sid] = s
                idem_remember(store, ikey, path, 200, s)
                save(store)
            return self._json(200, s)

        if path.endswith("/heartbeat") or path.endswith("/heartbeat/"):
            sid = path.split("/")[-2]
            ikey = idem_key_of(self.headers.get, body)
            with LOCK:
                store = load()
                hit = idem_lookup(store, ikey) if ikey else None
                if hit:
                    return self._json(int(hit.get("code") or 200), hit["response"], headers={"Idempotency-Replayed": "true"})
                s = store.setdefault("sessions", {}).get(sid)
                if not s:
                    return self._json(404, {"error": "not_found"})
                s["heartbeat_at"] = now
                s["updated_at"] = now
                rt_req = body.get("runtime")
                if rt_req is not None:
                    rr_ensure(store)
                    rt, err = _validate_or_provision(store, rt_req)
                    if err:
                        return self._json(422, {"error": "RUNTIME_AUTOREGISTER_DISABLED",
                                                "runtime": err,
                                                "registered": sorted((store.get("runtimes") or {}).keys())})
                        # unreachable return keeps flow explicit
                for k in ("status", "phase", "head", "head_full", "note", "harness", "model", "agent", "progress", "review", "diff", "usage", "runtime"):
                    if k == "flightboard":
                        continue  # agents may never self-award the verifier-owned namespace
                    if body.get(k) is not None:
                        s[k] = body[k]
                    s["status"] = str(s["status"]).strip().lower()
                if body.get("tags") is not None:
                    s["tags"] = merge_list(s.get("tags"), body.get("tags"))
                if body.get("monitors") is not None:
                    s["monitors"] = merge_list(s.get("monitors"), body.get("monitors"), defaults=DEFAULT_MONITORS)
                store["sessions"][sid] = s
                idem_remember(store, ikey, path, 200, s)
                save(store)
            return self._json(200, s)

        with LOCK:
            store = load()
            ikey = idem_key_of(self.headers.get, body)
            hit = idem_lookup(store, ikey) if ikey else None
            if hit:
                return self._json(int(hit.get("code") or 200), hit["response"], headers={"Idempotency-Replayed": "true"})
            body.pop("request_id", None)
            body.pop("idempotency_key", None)
            body.pop("flightboard", None)  # agents never touch verdicts (RFC 2026-08-24)
            rt_raw = body.get("runtime")
            if rt_raw is None:
                inferred = infer_runtime(body.get("agent"), body.get("harness"))
                if inferred:
                    body["runtime"] = inferred
            elif isinstance(rt_raw, str) and rt_raw.strip():
                rr_ensure(store)
                rt, err = _validate_or_provision(store, rt_raw)
                if err:
                    return self._json(422, {"error": "RUNTIME_AUTOREGISTER_DISABLED",
                                            "runtime": err,
                                            "registered": sorted((store.get("runtimes") or {}).keys()),
                                            "hint": "ask operator to register_runtime, or enable SAUL_REGISTRY_AUTOREGISTER"})
                body["runtime"] = rt
            sid = str(body.get("id") or body.get("session_id") or "").strip()
            if not sid:
                pr = body.get("pr")
                agent = body.get("agent") or "agent"
                profile = body.get("profile")
                sid = profile or (f"sai-pr{pr}-{agent}" if pr is not None else "")
            prev = store.setdefault("sessions", {}).get(sid, {})
            sess = normalize_session({**body, "id": sid}, prev)
            miss = missing_required(sess)
            if miss and not prev:
                return self._json(400, {"error": "missing_required_fields", "missing": miss, "required": list(REQUIRED_SESSION_FIELDS)})
            if miss:
                for k in miss:
                    if prev.get(k) is not None:
                        sess[k] = prev[k]
                miss = missing_required(sess)
                if miss:
                    return self._json(400, {"error": "missing_required_fields", "missing": miss, "required": list(REQUIRED_SESSION_FIELDS)})
            store["sessions"][sid] = sess
            idem_remember(store, ikey, path, 200, sess)
            save(store)
        return self._json(200, sess)

    def do_PATCH(self) -> None:
        return self.do_POST()


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8091"))
    DATA.parent.mkdir(parents=True, exist_ok=True)
    # One-time legacy migration: every stored session gets a typed runtime.
    # Known families inferred from agent/harness; unknown agents bootstrap their own
    # provisional runtime (recorded in migrated_at — never re-guessed).
    with LOCK:
        store = load()
        changed = False
        reg = rr_ensure(store)
        for sid, sess in store.get("sessions", {}).items():
            if not isinstance(sess, dict) or sess.get("runtime"):
                continue
            rt = infer_runtime(sess.get("agent"), sess.get("harness")) or _slugify(str(sess.get("agent") or "legacy"))
            if rt not in reg:
                rr_register(store, rt, provisional=False)
            sess["runtime"] = rt; sess["migrated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            store["sessions"][sid] = sess; changed = True
        _refresh_windows(store)
        if changed:
            tmp = DATA.with_suffix(".mig"); tmp.write_text(json.dumps(store, indent=2, sort_keys=True))
            os.replace(tmp, DATA)
            print(f"migration: typed {sum(1 for s_ in store['sessions'].values() if s_.get('migrated_at'))} sessions", flush=True)
    if not DATA.exists():
        save({"sessions": {}})
    # perf-lane finding: default listen backlog 5 caused ~1s reader stalls under
    # concurrent load; 128 brings p99 stall to ~32ms (A/B measured).
    ThreadingHTTPServer.request_queue_size = 128
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"hermes-sessions listening on {host}:{port} data={DATA} schema=sai-sessions-v2", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
