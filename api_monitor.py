"""
API Monitor — logs every Anthropic LLM call and provides aggregated stats.

Log files: research_data/api_logs/YYYY-MM-DD.json
Each file is a JSON list of call records appended after every API call.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).parent / "research_data"
LOG_DIR = DATA_DIR / "api_logs"


# ── Writing ──────────────────────────────────────────────────────────────────

def log_call(
    *,
    personality: str,
    call_type: str,          # "welcome" | "chat"
    success: bool,
    latency_ms: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
    error_type: Optional[str] = None,
    error_msg: Optional[str] = None,
    session_id: str = "",
    dialogue_id: str = "",
):
    """Append one call record to today's log file. Never raises."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOG_DIR / f"{today}.json"

        entry = {
            "ts":           datetime.now().isoformat(),
            "personality":  personality,
            "call_type":    call_type,
            "success":      success,
            "latency_ms":   round(latency_ms, 1),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "error_type":   error_type,
            "error_msg":    error_msg,
            "session_id":   session_id,
            "dialogue_id":  dialogue_id,
        }

        # Read existing entries, append, rewrite
        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                entries = []
        entries.append(entry)
        log_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")

        # GitHub sync: every 10 calls or on first call of the day
        if len(entries) == 1 or len(entries) % 10 == 0:
            try:
                from github_storage import get_storage
                get_storage().write(f"api_logs/{today}.json", entries)
            except Exception:
                pass
    except Exception:
        pass  # Monitor must never break the app


# ── Reading / Aggregation ─────────────────────────────────────────────────────

def _load_entries(hours: int = 24) -> List[Dict]:
    """Return all log entries from the last `hours` hours."""
    cutoff = datetime.now() - timedelta(hours=hours)
    entries = []

    # We may need to read today and yesterday (if hours > time since midnight)
    dates_to_check = {datetime.now().strftime("%Y-%m-%d")}
    if hours > datetime.now().hour:          # window spans into yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        dates_to_check.add(yesterday)
    if hours > 24:                           # also check further back
        for d in range(2, (hours // 24) + 2):
            dates_to_check.add((datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d"))

    for date_str in dates_to_check:
        log_file = LOG_DIR / f"{date_str}.json"
        if not log_file.exists():
            continue
        try:
            data = json.loads(log_file.read_text(encoding="utf-8"))
            for e in data:
                try:
                    ts = datetime.fromisoformat(e["ts"])
                    if ts >= cutoff:
                        entries.append(e)
                except Exception:
                    continue
        except Exception:
            continue

    entries.sort(key=lambda e: e["ts"])
    return entries


def get_stats(hours: int = 24) -> Dict:
    """
    Return aggregated API statistics for the last `hours` hours.

    Keys:
        total_calls, success_calls, fail_calls, success_rate_pct,
        avg_latency_ms, p95_latency_ms,
        total_input_tokens, total_output_tokens, total_tokens,
        calls_by_hour       — dict {hour_label: count}
        errors_by_type      — dict {error_type: count}
        recent_errors       — list of last 10 failed entries (newest first)
        health              — "green" | "yellow" | "red"
        hours               — the requested window
    """
    entries = _load_entries(hours)

    if not entries:
        return {
            "total_calls": 0,
            "success_calls": 0,
            "fail_calls": 0,
            "success_rate_pct": None,
            "avg_latency_ms": None,
            "p95_latency_ms": None,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "calls_by_hour": {},
            "errors_by_type": {},
            "recent_errors": [],
            "health": "red",
            "hours": hours,
        }

    total = len(entries)
    successes = [e for e in entries if e.get("success")]
    failures  = [e for e in entries if not e.get("success")]

    success_rate = (len(successes) / total * 100) if total else None

    latencies = [e["latency_ms"] for e in entries if isinstance(e.get("latency_ms"), (int, float))]
    latencies_sorted = sorted(latencies)
    avg_latency = sum(latencies) / len(latencies) if latencies else None
    p95_latency = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies_sorted else None

    input_tokens  = sum(e.get("input_tokens", 0) or 0 for e in entries)
    output_tokens = sum(e.get("output_tokens", 0) or 0 for e in entries)

    # Calls by hour (bucket into hour slots)
    calls_by_hour: Dict[str, int] = {}
    now = datetime.now()
    for h in range(hours - 1, -1, -1):
        slot = now - timedelta(hours=h)
        label = slot.strftime("%H:00")
        calls_by_hour[label] = 0
    for e in entries:
        try:
            ts = datetime.fromisoformat(e["ts"])
            label = ts.strftime("%H:00")
            if label in calls_by_hour:
                calls_by_hour[label] += 1
        except Exception:
            pass

    # Errors by type
    errors_by_type: Dict[str, int] = {}
    for e in failures:
        etype = e.get("error_type") or "Unknown"
        errors_by_type[etype] = errors_by_type.get(etype, 0) + 1

    # Recent errors (newest first, capped at 10)
    recent_errors = list(reversed(failures))[:10]

    # Health
    if success_rate is None or success_rate < 80:
        health = "red"
    elif success_rate < 95:
        health = "yellow"
    else:
        health = "green"

    return {
        "total_calls":       total,
        "success_calls":     len(successes),
        "fail_calls":        len(failures),
        "success_rate_pct":  round(success_rate, 1) if success_rate is not None else None,
        "avg_latency_ms":    round(avg_latency, 0) if avg_latency is not None else None,
        "p95_latency_ms":    round(p95_latency, 0) if p95_latency is not None else None,
        "total_input_tokens":  input_tokens,
        "total_output_tokens": output_tokens,
        "total_tokens":        input_tokens + output_tokens,
        "calls_by_hour":     calls_by_hour,
        "errors_by_type":    errors_by_type,
        "recent_errors":     recent_errors,
        "health":            health,
        "hours":             hours,
    }
