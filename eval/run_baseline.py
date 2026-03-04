#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Day11 baseline runner:
- Read eval/cases.jsonl
- Call FastAPI endpoints (Render) with retries / warmup
- Write eval/baseline_outputs.jsonl

Required env:
  BASE_URL="https://xxxx.onrender.com"   # no trailing slash
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests


# -------------------------
# Config
# -------------------------
DEFAULT_BASELINE_DAYS = 2
DEFAULT_COMPARE_DAYS = 2
DEFAULT_THRESHOLD_PCT = 0.2

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 120
RETRIES = 3


# -------------------------
# Helpers
# -------------------------
def _now_ts() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _read_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _join_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def _request_json(
    method: str,
    url: str,
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
    tries: int = RETRIES,
) -> dict:
    """
    Returns dict:
      {
        "ok": bool,
        "status_code": int|None,
        "json": object|None,
        "text": str|None,
        "error": str|None,
        "url": str,
        "payload": payload
      }
    """
    last_err: Optional[str] = None
    for i in range(tries):
        try:
            resp = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=headers or {"Content-Type": "application/json"},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            out: Dict[str, Any] = {
                "ok": resp.ok,
                "status_code": resp.status_code,
                "url": url,
                "payload": payload,
            }
            # Try json first
            try:
                out["json"] = resp.json()
            except Exception:
                out["json"] = None
                out["text"] = resp.text
            if resp.ok:
                return out
            # Not ok -> still return with body
            return out
        except requests.exceptions.RequestException as e:
            last_err = f"{type(e).__name__}: {e}"
            # exponential-ish backoff
            time.sleep(2 * (i + 1))

    return {
        "ok": False,
        "status_code": None,
        "json": None,
        "text": None,
        "error": last_err or "unknown error",
        "url": url,
        "payload": payload,
    }


# -------------------------
# Date range parsing (simple baseline)
# -------------------------
def _parse_date_range_text(text: str) -> Tuple[str, str]:
    """
    Returns ISO dates: (start, end)
    We use a fixed mapping aligned with your demo dataset range (2014-10-19 ~ 2014-10-25),
    so "近7天/本周/上周/昨天/近30天" can still run against demo data.

    If you later switch to real data, replace this mapping with real date logic.
    """
    t = (text or "").strip()

    # Demo dataset anchor
    # You used 2014-10-21~2014-10-25 often, and baseline 2014-10-19~2014-10-20
    if t in ("近7天", "最近7天", "近一周", "最近一周", ""):
        return ("2014-10-19", "2014-10-25")
    if t in ("昨天", "昨日"):
        return ("2014-10-24", "2014-10-24")
    if t in ("本周",):
        return ("2014-10-19", "2014-10-25")
    if t in ("上周",):
        return ("2014-10-19", "2014-10-25")
    if t in ("近30天", "最近30天", "近一月", "最近一个月"):
        # Demo dataset only has a short window; keep it safe
        return ("2014-10-19", "2014-10-25")

    # Custom range like YYYY-MM-DD~YYYY-MM-DD
    if "~" in t:
        a, b = [x.strip() for x in t.split("~", 1)]
        # Basic validation
        datetime.fromisoformat(a)
        datetime.fromisoformat(b)
        return (a, b)

    # Fallback
    return ("2014-10-19", "2014-10-25")


def _window_split(start: str, end: str, baseline_days: int, compare_days: int) -> dict:
    """
    Use end date as anchor:
      compare window = [end-compare_days+1, end]
      baseline window = [compare_start-baseline_days, compare_start-1]
    """
    e = datetime.fromisoformat(end).date()
    c_end = e
    c_start = c_end - timedelta(days=compare_days - 1)

    b_end = c_start - timedelta(days=1)
    b_start = b_end - timedelta(days=baseline_days - 1)

    return {
        "b_start": b_start.isoformat(),
        "b_end": b_end.isoformat(),
        "c_start": c_start.isoformat(),
        "c_end": c_end.isoformat(),
    }


# -------------------------
# Case params
# -------------------------
def _normalize_metric(m: str) -> str:
    """
    Your FastAPI accepts lowercase: impressions/clicks/spend/conversions/revenue/ctr/cvr/cpa/roas/roi
    """
    if not m:
        return "roi"
    return m.strip().lower()


def _normalize_dim(dim: str) -> str:
    """
    We map dim -> group_by / dim field for APIs.
    Dify side: dimension: campaign/creative/audience/geo/device/all
    Backend allows group_by: date/campaign_id ; slice dim: campaign_id
    So baseline uses campaign_id as the only real dim.
    """
    if not dim:
        return "campaign"
    return dim.strip().lower()


# -------------------------
# Core: build evidence by calling API
# -------------------------
def build_evidence(base_url: str, metric: str, date_range_text: str, dim: str) -> dict:
    start, end = _parse_date_range_text(date_range_text)
    metric = _normalize_metric(metric)
    dim = _normalize_dim(dim)

    # Only campaign is supported in your current backend
    group_by_for_anomaly = "campaign_id" if dim in ("campaign", "all") else "campaign_id"
    slice_dim = "campaign_id"

    windows = _window_split(start, end, DEFAULT_BASELINE_DAYS, DEFAULT_COMPARE_DAYS)

    # 1) query_metrics trend by date
    trend_payload = {
        "metric": metric,
        "group_by": ["date"],
        "filters": None,
        "date_range": {"start": start, "end": end},
    }
    trend = _request_json("POST", _join_url(base_url, "/query_metrics"), trend_payload)

    # 2) detect_anomaly by campaign_id
    anomaly_payload = {
        "metric": metric,
        "group_by": group_by_for_anomaly,
        "date_range": {"start": start, "end": end},
        "baseline_days": DEFAULT_BASELINE_DAYS,
        "compare_days": DEFAULT_COMPARE_DAYS,
        "threshold_pct": DEFAULT_THRESHOLD_PCT,
    }
    anomaly = _request_json("POST", _join_url(base_url, "/detect_anomaly"), anomaly_payload)

    # 3) slice_compare (we keep metric revenue as in your workflow)
    slice_payload = {
        "metric": "revenue",
        "dim": slice_dim,
        "baseline_range": {"start": windows["b_start"], "end": windows["b_end"]},
        "compare_range": {"start": windows["c_start"], "end": windows["c_end"]},
        "top_k": 10,
    }
    slice_cmp = _request_json("POST", _join_url(base_url, "/slice_compare"), slice_payload)

    # Assemble evidence in the same shape you used in Dify
    evidence: Dict[str, Any] = {
        "trend_rows": (trend.get("json") or {}).get("rows") if trend.get("ok") else [],
        "anomalies_top3": (anomaly.get("json") or {}).get("anomalies", [])[:3] if anomaly.get("ok") else [],
        "contributions_top5": (slice_cmp.get("json") or {}).get("contributions", [])[:5] if slice_cmp.get("ok") else [],
        "compare_window": {
            "baseline": (slice_cmp.get("json") or {}).get("baseline_summary", {}),
            "compare": (slice_cmp.get("json") or {}).get("compare_summary", {}),
        } if slice_cmp.get("ok") else {"baseline": {}, "compare": {}},
    }

    debug: Dict[str, Any] = {
        "date_range": {"start": start, "end": end},
        "window_split": windows,
        "requests": {
            "trend": trend,
            "anomaly": anomaly,
            "slice_compare": slice_cmp,
        },
    }

    return {"evidence": evidence, "debug": debug}


# -------------------------
# Main
# -------------------------
def main() -> None:
    base_url = os.environ.get("BASE_URL", "").strip().rstrip("/")
    if not base_url:
        raise SystemExit('Missing env BASE_URL, e.g. export BASE_URL="https://xxx.onrender.com"')

    cases_path = os.path.join("eval", "cases.jsonl")
    out_path = os.path.join("eval", "baseline_outputs.jsonl")

    cases = _read_jsonl(cases_path)

    # Warm up Render (free plan sleep)
    _request_json("GET", _join_url(base_url, "/health"), payload=None)

    outputs: List[dict] = []
    for c in cases:
        cid = c.get("id")
        user_query = c.get("user_query", "")
        expect = c.get("expect", {}) or {}

        metric = _normalize_metric(expect.get("metric", "roi"))
        date_range_text = expect.get("date_range", "近7天")
        dim = _normalize_dim(expect.get("dim", "campaign"))

        built = build_evidence(base_url, metric, date_range_text, dim)

        outputs.append(
            {
                "id": cid,
                "ts": _now_ts(),
                "user_query": user_query,
                "expect": expect,
                "params": {
                    "metric": metric,
                    "date_range": date_range_text,
                    "dimension": dim,
                },
                # What baseline produced
                "evidence": built["evidence"],
                # Keep request/response debug (helpful when something fails)
                "debug": built["debug"],
            }
        )

    _write_jsonl(out_path, outputs)
    print(f"✅ Wrote: {out_path} (rows={len(outputs)})")


if __name__ == "__main__":
    main()