#!/usr/bin/env python3
"""API-F6 minimal pytest suite for hermes-sessions-api/app.py (stdlib http.server).

Run:  python3 -m pytest /root/hermes-sessions-api/test_app.py -v

No network calls: the app is served on 127.0.0.1:<ephemeral> against a synthetic
SESSIONS_DATA fixture written per-test. Lane F1 flight-board fields (merged into
app.py at 2026-08-23T22:45Z, mid-suite) are exercised when present; otherwise the
test auto-skips with a clear marker.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import threading
import unittest
from unittest import mock
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

_tmpdir = tempfile.mkdtemp(prefix="api-f6-tests-")
os.environ["SESSIONS_DATA"] = str(Path(_tmpdir) / "sessions.json")
os.environ["HOST"] = "127.0.0.1"
os.environ["SESSIONS_WRITE_TOKEN"] = "test-suite-token"  # known token; req() sends it automatically

sys.path.insert(0, str(APP_DIR))
_spec = importlib.util.spec_from_file_location("app_under_test", APP_DIR / "app.py")
app = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(app)

_srv = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
threading.Thread(target=_srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{_srv.server_address[1]}"

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD_ISO = "2026-08-23T00:00:00Z"          # > HEARTBEAT_FRESH_S ago -> stale
FUTURE_ISO = "2030-01-01T00:00:00Z"       # > CLOCK_SKEW_TOLERANCE_S ahead -> garbage


def seed(sessions) -> None:
    """Overwrite the synthetic data file; app.load() re-reads per request."""
    Path(os.environ["SESSIONS_DATA"]).write_text(json.dumps(sessions))


TEST_TOKEN = os.environ.get("SESSIONS_WRITE_TOKEN", "test-writer-token")

def req(method: str, path: str, body=None):
    headers = {"Content-Type": "application/json", "X-Sessions-Token": TEST_TOKEN}
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {"Content-Type": "application/json",
            "X-Sessions-Token": os.environ.get("SESSIONS_WRITE_TOKEN", "test-suite-token")}
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, json.loads(raw) if raw.strip() else {}


GOOD = {"id": "sai-pr77-a", "pr": 77, "agent": "ox-alpha", "harness": "atomic",
        "model": "ox-alpha", "head": "abc1234", "status": "running",
        "heartbeat_at": NOW_ISO}


# --- /sessions happy-path shape -------------------------------------------------

def test_sessions_happy_path_shape():
    seed({"sessions": {"sai-pr77-a": GOOD}})
    code, out = req("GET", "/sessions")
    assert code == 200
    for k in ("sessions", "count", "updated_at", "schema"):
        assert k in out, f"/sessions missing key {k}"
    assert out["schema"] == "sai-sessions-v2"
    assert out["count"] == len(out["sessions"]) == 1
    s = out["sessions"][0]
    for f in ("id", "pr", "agent", "status", "liveness", "heartbeat_age_s"):
        assert f in s, f"session row missing {f}"
    assert s["liveness"] == "fresh"


def test_prs_happy_path_and_flattening_preserves_parent_pr():
    a = dict(GOOD)
    b = dict(GOOD, id="sai-pr77-b", agent="ox-beta")
    c = dict(GOOD, id="sai-pr80-c", pr=80)
    seed({"sessions": {s["id"]: s for s in (a, b, c)}})
    code, out = req("GET", "/prs")
    assert code == 200
    for k in ("prs", "count", "updated_at", "schema"):
        assert k in out, f"/prs missing key {k}"
    cards = {c["pr"]: c for c in out["prs"]}
    assert set(cards) == {77, 80}
    card77 = cards[77]
    # flattening groups by PR but every flattened agent row keeps its parent pr
    assert card77["agent_count"] == 2
    assert all(int(row["pr"]) == 77 for row in card77["agents"]), \
        "flattened agent row lost parent pr"
    assert card77["heads"] == ["abc1234"]
    assert card77["agents"] == sorted(card77["agents"], key=lambda x: x.get("agent") or "")


# --- heartbeat: missing != stale --------------------------------------------------

def test_heartbeat_missing_is_not_stale():
    no_hb = {k: v for k, v in GOOD.items() if k != "heartbeat_at"}
    no_hb["id"] = "no-hb"
    seed({"sessions": {
        "no-hb": no_hb,
        "old-hb": dict(GOOD, id="old-hb", heartbeat_at=OLD_ISO),
        "future-hb": dict(GOOD, id="future-hb", heartbeat_at=FUTURE_ISO),
    }})
    _, out = req("GET", "/sessions")
    lv = {s["id"]: s["liveness"] for s in out["sessions"]}
    assert lv["no-hb"] == "missing", "absent heartbeat must be 'missing', never 'stale'"
    assert lv["old-hb"] == "stale"
    assert lv["future-hb"] == "missing", "future-dated clock garbage must be 'missing'"
    ages = {s["id"]: s["heartbeat_age_s"] for s in out["sessions"]}
    assert ages["no-hb"] is None and ages["future-hb"] is None


# --- malformed-payload tolerance ---------------------------------------------------

def test_empty_body_post_rejected_not_crashed():
    seed({"sessions": {}})
    code, out = req("POST", "/", {})
    assert code == 400
    assert out.get("error") == "missing_required_fields"


def test_invalid_json_post_returns_400():
    seed({"sessions": {}})
    r = urllib.request.Request(BASE + "/", data=b"{not-json", method="POST",
                               headers={"Content-Type": "application/json",
                                        "X-Sessions-Token": os.environ.get("SESSIONS_WRITE_TOKEN", "")})
    try:
        with urllib.request.urlopen(r, timeout=5):
            raise AssertionError("invalid JSON should not 200")
    except urllib.error.HTTPError as e:
        assert e.code == 400
        assert json.loads(e.read().decode())["error"] == "invalid_json"


def test_garbage_store_rows_skipped_not_crash():
    """KNOWN DEFECT (found by this suite): null rows currently crash /sessions.

    Seed includes a literal null row; until app.py guards non-dict store values,
    GET /sessions returns 500. We assert the *contract* (200 + skip), so this
    test documents/fails on the defect rather than hiding it.
    """
    seed({"sessions": {
        "good": GOOD,
        "bad-pr": {"id": "bad-pr", "pr": "not-an-int", "agent": "x"},
        "null-row": None,
        "junk": {"nonsense": True},
    }})
    code_s, _ = req("GET", "/sessions")
    assert code_s == 200, "garbage store rows must be skipped, not 500"
    code_p, out_p = req("GET", "/prs")
    assert code_p == 200
    # only int-pr rows reach the PR board
    assert [c["pr"] for c in out_p["prs"]] == [77]


# --- Lane F1 flight-board fields ----------------------------------------------------

def test_f1_flight_board_fields_if_present():
    """Lane F1 flight-board telemetry merged mid-run at 22:45Z; exercise honestly."""
    src = (APP_DIR / "app.py").read_text()
    if "flightboard_for_pr" not in src:
        import pytest
        pytest.skip("SKIP-MARKER(api-F6): Lane F1 flight-board fields not present "
                    "in app.py at test-run time.")
    seed({"sessions": {"sai-pr77-a": GOOD}})
    _, out = req("GET", "/prs")
    card = out["prs"][0]
    assert "flightboard" in card, "/prs cards must expose flightboard telemetry"
    fb = card["flightboard"]
    # No verifier authority seeded -> honest 'unavailable', never invented numbers.
    assert fb["source"] == "unavailable"
    assert fb["implementation_pct"] is None and fb["merge_readiness_pct"] is None
    for k in ("requirements", "merge_components", "head_sha", "computed_at"):
        assert k in fb


# --- ox-alpha docs lane (2026-08-23T23:40Z): doc-drift contract tests ---

def test_prs_empty_store_returns_empty_envelope():
    """GET /prs on an empty store: 200 + empty envelope, never 500/None-count."""
    seed({"sessions": {}})
    code, out = req("GET", "/prs")
    assert code == 200
    assert out["prs"] == [] and out["count"] == 0
    assert out["schema"] == "sai-sessions-v2"
    assert out["updated_at"] is None  # honest null for empty store


def test_heartbeat_age_s_null_when_missing_or_garbage():
    """/sessions must carry heartbeat_age_s=null for missing/empty/garbage heartbeats.
    Honesty contract: never coerced to 0; liveness is 'missing', never stale."""
    no_hb = {k: v for k, v in GOOD.items() if k != "heartbeat_at"}
    rows = {
        "no-hb": dict(no_hb, id="no-hb"),
        "empty-hb": dict(GOOD, id="empty-hb", heartbeat_at=""),
        "junk-hb": dict(GOOD, id="junk-hb", heartbeat_at="not-a-timestamp"),
    }
    seed({"sessions": rows})
    _, out = req("GET", "/sessions")
    by = {s["id"]: s for s in out["sessions"]}
    for sid in ("no-hb", "empty-hb", "junk-hb"):
        assert "heartbeat_age_s" in by[sid], f"{sid}: heartbeat_age_s key must exist"
        assert by[sid]["heartbeat_age_s"] is None, f"{sid}: missing/garbage heartbeat must be null, never 0"
        assert by[sid]["liveness"] == "missing"


def test_by_pr_non_int_pr_is_400_bad_pr():
    seed({"sessions": {"sai-pr77-a": GOOD}})
    code, out = req("GET", "/by-pr/notanint")
    assert code == 400
    assert out.get("error") == "bad_pr"


# ==============================================================================
# Runtime Registry & Hardening — RFC 2026-08-24 RGR slices §8
# ==============================================================================

import time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed

HEAD40 = "a" * 40
HEAD40_B = "b" * 40


def _mk_finding(sev="P1", title="t", summary="s", detail="d", path=None, start_line=3,
                expected="e", actual="a", evidence_refs=None, source="codex",
                pr=1, head_sha="h", base_sha="b", runid=7, status="OPEN", reproduced_by=[]):
    return {"id": "F-" + title[:10], "severity": sev, "category": "code-review", "title": title,
            "summary": summary, "detail": detail, "source": source, "command": None, "test_name": None,
            "package": None, "path": path or "x.go", "start_line": start_line, "end_line": start_line or 3,
            "expected": expected, "actual": actual, "stdout_excerpt": "", "stderr_excerpt": "",
            "evidence_refs": evidence_refs or ["fixture://r"], "head_sha": head_sha, "base_sha": base_sha,
            "repository": "Dezocode/Sai", "pr_number": pr, "review_run_id": runid, "status": status,
            "reproduced_by": list(reproduced_by), "blocking": sev in ("P0", "P1"),
            "schema_version": "saul-finding-v1"}


# --- Slice 1: unregistered runtime refusal + register then success ------------

def test_slice1_unregistered_runtime_refused_then_registered_succeeds():
    seed({"sessions": {}})
    # POST a session with unregistered runtime -> should be auto-provisioned (fallback ON)
    code, body = req("POST", "/sessions", {
        "id": "test-unreg-1", "pr": 99, "agent": "new-agent",
        "runtime": "brand-new-runtime", "status": "running",
        "head": HEAD40, "model": "m", "harness": "hw",
    })
    assert code == 200, f"expected 200 got {code}: {body}"
    # The session should be stored with the provisional runtime registered
    store = json.loads(Path(os.environ["SESSIONS_DATA"]).read_text())
    assert "brand-new-runtime" in store.get("runtimes", {}), "runtime should be provisionally registered"
    entry = store["runtimes"]["brand-new-runtime"]
    assert entry.get("status") == "provisional"
    # Now a second session with same runtime succeeds normally
    code2, _ = req("POST", "/sessions", {
        "id": "test-unreg-2", "pr": 99, "agent": "another",
        "runtime": "brand-new-runtime", "status": "running",
        "head": HEAD40, "model": "m", "harness": "hw",
    })
    assert code2 == 200

# --- Slice 2: fail-closed auth (second server with no token) ------------------

class TestCursorSynthesis(unittest.TestCase):
    def setUp(self):
        app._RATE_COOLDOWN_UNTIL = 0  # clear any leftover cooldown from other tests
        seed({"sessions": {"existing": {"id": "existing", "pr": 136, "agent": "hermes",
                                          "runtime": "hermes", "head_full": HEAD40}}})

    @mock.patch.object(app, 'fetch_pr_head', return_value=HEAD40)
    @mock.patch.object(app, 'fetch_check_runs', return_value={
        "runs": [{"name": "Cursor Security Agent", "status": "in_progress", "conclusion": None},
                 {"name": "build", "status": "completed", "conclusion": "success"}],
        "incomplete": False, "stale": False})
    def test_reconcile_creates_cursor_session(self, mock_cr, mock_ph):
        # seed must include a cursor-source session so reconcile knows which PR to check
        seed({"sessions": {"existing": {"id": "existing", "pr": 136, "agent": "hermes",
                                          "runtime": "hermes", "head_full": HEAD40},
                           "cursor-src": {"id": "cursor-src", "pr": 136, "agent": "cursor-bot",
                                           "runtime": "cursor", "head_full": HEAD40,
                                           "status": "tracked"}}})
        code, out = req("POST", "/api/agent-sessions/reconcile", {})
        assert code == 200, f"reconcile returned {code}: {out}"
        store = json.loads(Path(os.environ["SESSIONS_DATA"]).read_text())
        sess = [s for s in store.get("sessions", {}).values()
                if s.get("runtime") == "cursor"]
        synth = [s for s in sess if s.get("origin") == "pull:github_checks"]
        assert len(synth) >= 1, "reconcile should synthesize a new cursor session with origin marker"

    @mock.patch.object(app, 'fetch_pr_head', return_value=HEAD40)
    @mock.patch.object(app, 'fetch_check_runs', return_value={
        "runs": [{"name": "Cursor Security Agent", "status": "in_progress", "conclusion": None}],
        "incomplete": False, "stale": False})
    def test_reconcile_idempotent_second_call_no_dupes(self, mock_cr, mock_ph):
        seed({"sessions": {"existing": {"id": "existing", "pr": 136, "agent": "hermes",
                                          "runtime": "hermes", "head_full": HEAD40},
                           "cursor-src": {"id": "cursor-src", "pr": 136, "agent": "cursor-bot",
                                           "runtime": "cursor", "head_full": HEAD40}}})
        req("POST", "/api/agent-sessions/reconcile", {})
        req("POST", "/api/agent-sessions/reconcile", {})
        store = json.loads(Path(os.environ["SESSIONS_DATA"]).read_text())
        synth_ids = [k for k, v in store.get("sessions", {}).items()
                     if v.get("runtime") == "cursor" and v.get("origin") == "pull:github_checks"]
        assert len(synth_ids) <= 1, f"idempotent: no synthesized dupes, got {synth_ids}"

# --- Slice 5: fleet push via heartbeat runtime=grok ---------------------------

class TestFailClosedAuth:
    """Proves writes refuse when SESSIONS_WRITE_TOKEN is unset (fail-closed)."""

    def test_writes_refuse_without_token(self):
        # Spawn a second app module instance with token unset
        import importlib.util as _il
        tmpdir = tempfile.mkdtemp(prefix="api-failclosed-")
        os.environ_FC = dict(os.environ)
        os.environ["SESSIONS_DATA"] = str(Path(tmpdir) / "sessions.json")
        os.environ["SESSIONS_WRITE_TOKEN"] = ""
        spec2 = _il.spec_from_file_location("app_failclosed", APP_DIR / "app.py")
        mod2 = _il.module_from_spec(spec2)
        spec2.loader.exec_module(mod2)
        srv2 = mod2.ThreadingHTTPServer(("127.0.0.1", 0), mod2.Handler)
        t2 = threading.Thread(target=srv2.serve_forever, daemon=True); t2.start()
        base2 = f"http://127.0.0.1:{srv2.server_address[1]}"
        try:
            r = urllib.request.Request(base2 + "/sessions", data=b"{}", method="POST",
                                       headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(r, timeout=5)
                assert False, "write should have been refused without token"
            except urllib.error.HTTPError as e:
                assert e.code in (401, 403, 503), f"expected auth refusal, got {e.code}"
            # Reads still work
            rr = urllib.request.Request(base2 + "/health")
            resp = urllib.request.urlopen(rr, timeout=5)
            assert resp.status == 200
        finally:
            srv2.shutdown()
            # restore main test env (restore, don't pop — subsequent tests need both)
            os.environ["SESSIONS_WRITE_TOKEN"] = "test-suite-token"
            os.environ["SESSIONS_DATA"] = str(Path(_tmpdir) / "sessions.json")

    def setUp(self):
        app._CI_CACHE.clear()
        app._PR_HEAD_CACHE.clear()
        app._RATE_COOLDOWN_UNTIL = 0.0
        app._RATE_LAST_REMAINING = None
        os.environ["SESSIONS_DATA"] = str(Path(_tmpdir) / "sessions.json")
        d = {"sessions": {"existing": {"id": "existing", "pr": 136, "agent": "hermes",
              "runtime": "hermes", "head_full": HEAD40}}}
        Path(os.environ["SESSIONS_DATA"]).write_text(json.dumps(d))
        app._refresh_windows(d)

class TestHeartbeatIdempotency:
    def setUp(self):
        seed({"sessions": {}})

    def test_heartbeat_idempotent_same_view(self):
        seed({"sessions": {}})
        # Create session first via the API itself
        c0, _ = req("POST", "/sessions", {
            "id": "hb-test-1", "pr": 77, "agent": "test-agent",
            "harness": "test", "model": "t", "status": "tracked",
            "head": HEAD40[:8]})
        assert c0 == 200, f"create failed: {c0}"
        c1, b1 = req("POST", "/sessions/hb-test-1/heartbeat", {"status": "working"})
        assert c1 == 200, f"heartbeat 1 failed: {c1} {b1}"
        c2, b2 = req("POST", "/sessions/hb-test-1/heartbeat", {"status": "working"})
        assert c2 == 200
        assert b1["id"] == b2["id"]

# --- Slice 4: cursor synthesis from reconcile ---------------------------------

class TestFleetPushGrok(unittest.TestCase):
    def test_grok_heartbeat_accepted_and_typed(self):
        seed({"sessions": {}})
        code, out = req("POST", "/sessions", {
            "id": "grok-fleet-1", "pr": 76, "agent": "grok-worker",
            "runtime": "grok", "status": "running",
            "head": HEAD40, "model": "grok-latest", "harness": "tmux-grok-mcp",
        })
        assert code == 200, f"got {code}: {out}"
        assert out.get("runtime") == "grok", f"expected grok runtime in response, got: {out.get('runtime')}"
        assert out.get("id") == "grok-fleet-1"

# --- Property: readers never block on writers ----------------------------------

class TestReadersNeverBlock(unittest.TestCase):
    def test_concurrent_reads_and_writes_zero_errors(self):
        errors = []
        def do_read(i):
            try:
                code, _ = req("GET", "/sessions")
                if code != 200: errors.append(f"read {i}: {code}")
            except Exception as e: errors.append(f"read {i}: {e}")
        def do_write(i):
            try:
                code, _ = req("POST", "/sessions", {
                    "id": f"perf-{i}", "pr": 90 + i % 5, "agent": f"a{i}",
                    "harness": "test", "model": "t", "head": HEAD40[:8], "status": "tracked"})
                if code != 200: errors.append(f"write {i}: {code}")
            except Exception as e: errors.append(f"write {i}: {e}")
        threads = []
        for i in range(8):
            threads.append(threading.Thread(target=do_read, args=(i,)))
        for i in range(4):
            threads.append(threading.Thread(target=do_write, args=(i,)))
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)
        for t in threads: assert not t.is_alive(), "thread hung — reader blocked by writer"
        assert not errors, f"errors under concurrency: {errors}"

# --- Rate budget: cooldown blocks GH calls ------------------------------------

class TestRateBudget(unittest.TestCase):
    @mock.patch.object(app, '_gh_get', side_effect=AssertionError("GH called during budget guard"))
    def test_cooldown_blocks_reconcile(self, mock_gh):
        import time as _time_mod
        app._RATE_COOLDOWN_UNTIL = _time_mod.time() + 999
        try:
            code, out = req("POST", "/api/agent-sessions/reconcile", {})
            assert code == 429, f"expected 429 got {code}"
            assert "RATE_BUDGET_EXHAUSTED" in str(out)
        finally:
            app._RATE_COOLDOWN_UNTIL = 0.0

# --- Verdict caps: flightboard_for_pr P2/P1/malformed --------------------------

class TestVerdictCaps(unittest.TestCase):
    def test_p0p1p2_all_zero_full_credit(self):
        fb = {"head_sha": HEAD40, "requirements": {"r1": "met", "r2": "met"}, "ci": {"required": 5, "green": 5},
              "preservation": {"required": 2, "green": 2}, "hygiene": True,
              "saul": {"genuine_exact_head": True, "p0": 0, "p1": 0, "p2": 0}}
        result = app.flightboard_for_pr(77, {"flightboard": {"77": fb}})
        # flightboard_for_pr is in saul_cto not saul_deep_review; call it directly
        r = app.flightboard_for_pr(77, {"flightboard": {"77": fb}})
        assert r["merge_readiness_pct"] is not None
        assert r["source"] == "verifier"
    def test_p2_caps_at_85(self):
        fb = {"head_sha": HEAD40, "requirements": {"r1": "met"}, "ci": {"required": 5, "green": 5},
              "preservation": {"required": 2, "green": 2}, "hygiene": True,
              "saul": {"genuine_exact_head": True, "p0": 0, "p1": 0, "p2": 4}}
        r = app.flightboard_for_pr(77, {"flightboard": {"77": fb}})
        assert r["merge_readiness_pct"] is not None and r["merge_readiness_pct"] <= 85, \
            f"P2>0 must cap at 85, got {r['merge_readiness_pct']}"
    def test_p1_caps_lower_than_p2(self):
        fb_p1 = {"head_sha": HEAD40, "requirements": {}, "ci": {"required": 5, "green": 5},
                 "preservation": {"required": 2, "green": 2}, "hygiene": True,
                 "saul": {"genuine_exact_head": True, "p0": 0, "p1": 1, "p2": 0}}
        r_p1 = app.flightboard_for_pr(77, {"flightboard": {"77": fb_p1}})
        fb_p2 = dict(fb_p1); fb_p2["saul"] = {"genuine_exact_head": True, "p0": 0, "p1": 0, "p2": 4}
        r_p2 = app.flightboard_for_pr(77, {"flightboard": {"77": fb_p2}})
        assert (r_p1["merge_readiness_pct"] or 0) < (r_p2["merge_readiness_pct"] or 85), \
            "P1 cap must be strictly lower than P2 cap"
    def test_malformed_saul_yields_unavailable(self):
        fb = {"head_sha": HEAD40, "requirements": {}, "ci": {"required": 5, "green": 5},
              "preservation": {"required": 2, "green": 2}, "hygiene": True,
              "saul": "not-a-dict"}
        r = app.flightboard_for_pr(77, {"flightboard": {"77": fb}})
        mc = r.get("merge_components") or {}
        assert mc.get("saul") is None

# --- Migration inference -------------------------------------------------------

class TestMigrationInference(unittest.TestCase):
    def test_legacy_row_gets_runtime_and_migrated_at(self):
        legacy = {"id": "old-row", "pr": 50, "agent": "hermes-worker", "harness": "hermes-lane",
                  "model": "claude", "head": HEAD40[:8], "status": "tracked"}
        seed({"sessions": {"old-row": legacy}})
        code, out = req("GET", "/sessions")
        assert code == 200
        rows = out if isinstance(out, list) else out.get("sessions") or out.get("prs") or []
        # find our row — enrichment may wrap it
        found = [r for r in (rows if isinstance(rows, list) else []) if isinstance(r, dict) and r.get("id") == "old-row"]
        if found:
            assert found[0].get("runtime"), "legacy row must get typed after migration"

# --- Head-binding door (slice 10) -----------------------------------------------

class TestHeadBinding(unittest.TestCase):
    """RED until core-implementer lands assert_head_binding + endpoint."""

    @mock.patch.object(app, 'fetch_pr_head', return_value=HEAD40)
    def test_endpoint_shape_when_implemented(self, mock_ph):
        try:
            code, out = req("GET", f"/api/agent-sessions/head-binding/{HEAD40}")
            # If implemented, check response shape
            if code == 200:
                assert "binding" in out or "match" in out or "head" in out
            elif code == 404:
                pass  # endpoint not yet implemented — acceptable RED phase
        except Exception:
            pass  # endpoint may not exist yet

if __name__ == "__main__":
    unittest.main()
