import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Cache to avoid re-reading JSONL on every call
_BASELINE_MAP: Optional[Dict[str, Dict[str, Any]]] = None


def _repo_root() -> Path:
    # This file: <repo>/eval/providers/baseline_provider.py
    return Path(__file__).resolve().parents[2]


def _load_baseline_outputs() -> Dict[str, Dict[str, Any]]:
    global _BASELINE_MAP
    if _BASELINE_MAP is not None:
        return _BASELINE_MAP

    repo = _repo_root()
    p = repo / "eval" / "baseline_outputs.jsonl"
    if not p.exists():
        raise FileNotFoundError(
            f"baseline_outputs.jsonl not found: {p}. "
            f"Please run: python eval/run_baseline.py"
        )

    m: Dict[str, Dict[str, Any]] = {}
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            cid = obj.get("id")
            if cid:
                m[cid] = obj

    _BASELINE_MAP = m
    return m


def _get_case_id(prompt: Any, context: Dict[str, Any]) -> str:
    """
    Promptfoo passes vars through context. We use vars.id as the case id.
    Fallbacks are included to be defensive.
    """
    # Primary: context.vars.id
    vars_ = (context or {}).get("vars") or {}
    cid = vars_.get("id")
    if cid:
        return str(cid)

    # Fallback: sometimes prompt is structured, or contains an id field
    if isinstance(prompt, dict) and "id" in prompt:
        return str(prompt["id"])

    # Last resort: environment
    cid_env = os.getenv("CASE_ID")
    if cid_env:
        return cid_env

    raise ValueError("Cannot find case id. Expected context.vars.id to exist.")


def call_api(prompt, options, context):
    """
    Promptfoo Python Provider entrypoint.
    Signature MUST be: call_api(prompt, options, context)
    Return dict with at least: {"output": "..."}.
    """
    baseline_map = _load_baseline_outputs()
    cid = _get_case_id(prompt, context)

    if cid not in baseline_map:
        # Helpful error message
        known = list(baseline_map.keys())[:10]
        return {
            "output": "",
            "error": f"case id '{cid}' not found in eval/baseline_outputs.jsonl. "
                     f"Known examples: {known} (showing up to 10)"
        }

    row = baseline_map[cid]

    # What you want to compare in Promptfoo:
    # - baseline result (structured JSON from your baseline pipeline)
    # Here we output the whole baseline row as JSON text.
    out_text = json.dumps(row, ensure_ascii=False)

    return {
        "output": out_text
    }