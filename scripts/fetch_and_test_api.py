"""
Fetch Cricbuzz RapidAPI endpoints, save JSON responses, and provide a dry-run pipeline
that maps responses to DB insert parameters for manual verification or optional inserts.

Usage (PowerShell):

# Activate your virtualenv
& D:/test/.venv/Scripts/Activate.ps1

# Run the script
python scripts/fetch_and_test_api.py

To enable actual DB writes set these environment variables before running:
- DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT (optional)
- RUN_DB=1 (to enable writing)

The script defaults to saving responses under `data/api_responses`.
"""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
import os
import json
import pathlib
import sys
from typing import Any, Dict, List, cast

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "data" / "api_responses"
OUTDIR.mkdir(parents=True, exist_ok=True)
# Ensure local package imports work when running the script from the repo root
sys.path.insert(0, str(ROOT))

# Prefer API key from environment for safety; fall back to alternate env var
API_KEY = (
    os.environ.get("CRICBUZZ_RAPIDAPI_KEY")
    or os.environ.get("RAPIDAPI_KEY")
    or os.environ.get("RAPIDAPI_KEY_LITERAL")
)

HEADERS = {
    "x-rapidapi-key": API_KEY or "",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
}

ENDPOINTS = {
    "live": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live",
    "upcoming": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming",
    "recent": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent",
    # Example scorecard for match id 40381. Replace the id if you want other matches.
    "scard_40381": "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/scard",
}


def fetch_and_save(name: str, url: str) -> Any:
    print(f"Fetching {name} -> {url}")
    if not API_KEY:
        print("WARNING: No API key found in env (CRICBUZZ_RAPIDAPI_KEY). Requests may fail.")
    r = requests.get(url, headers=HEADERS, timeout=30)
    try:
        data: Any = r.json()
    except Exception:
        data = {"status_code": r.status_code, "text": r.text}
    out_path = OUTDIR / f"{name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {name} -> {out_path}")
    return data


# --- Dry-run mappers ---------------------------------------------------------
# These functions map API JSON to the parameter tuples expected by mysql_sync.upsert_*.
# They do not perform DB writes unless RUN_DB=1 is set and DB secrets are present.


def map_scard_to_batting_rows(scard: Any) -> List[Dict[str, Any]]:
    """Extract a conservative list of batting rows from a scorecard JSON.
    The exact JSON schema may vary; this mapper uses common keys like 'batting' or 'batsmen'.
    """
    rows: List[Dict[str, Any]] = []
    # This is defensive: the API returns either a `scorecard` list (Cricbuzz)
    # or an `innings` list depending on endpoint/version. Support both.
    raw = scard if isinstance(scard, dict) else {}
    innings_any = raw.get("scorecard") or raw.get("innings") or raw.get("inningsData") or []
    innings = cast(List[Dict[str, Any]], innings_any) if isinstance(innings_any, list) else []
    for inn in innings:
        inn_id = inn.get("inningsid") or inn.get("id") or inn.get("innings_id") or str(len(rows) + 1)
        # batsmen list could be under 'batsman' or 'batsmen' or 'batting'
        batsmen_any = inn.get("batsman") or inn.get("batsmen") or inn.get("batting") or inn.get("batting_display") or []
        batsmen = cast(List[Dict[str, Any]], batsmen_any) if isinstance(batsmen_any, list) else []
        for b in batsmen:
            name = b.get("name") or b.get("batsman") or b.get("player_name")
            if not name:
                continue
            runs = _safe_int(b.get("runs") or b.get("score") or b.get("r"))
            balls = _safe_int(b.get("balls") or b.get("b"))
            fours = _safe_int(b.get("fours") or b.get("4s"))
            sixes = _safe_int(b.get("sixes") or b.get("6s"))
            # Strike-rate key differs across responses: 'strkrate', 'strike_rate', 'sr'
            sr = _safe_float(b.get("strkrate") or b.get("strike_rate") or b.get("sr"))
            dismissal = b.get("dismissal") or b.get("out") or b.get("outdec") or ""
            meta = {k: v for k, v in b.items() if k not in ("name", "runs", "balls", "fours", "sixes", "strike_rate", "dismissal")}
            rows.append({
                "player_name": name,
                "runs": runs,
                "balls": balls,
                "fours": fours,
                "sixes": sixes,
                "strike_rate": sr,
                "dismissal": dismissal,
                "meta": meta,
                "innings_id": inn_id,
            })
    return rows


def _safe_int(v: Any) -> Any:
    try:
        if v is None or v == "":
            return None
        return int(v)
    except Exception:
        return None


def _safe_float(v: Any) -> Any:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


# --- Optional DB write -----------------------------------------------------

def maybe_write_to_db(sample_match_id: str, batting_rows: List[Dict[str, Any]], external_match_id: str):
    run_db = os.environ.get("RUN_DB") in ("1", "true", "True")
    if not run_db:
        print("RUN_DB not set; skipping DB writes. Set RUN_DB=1 to enable.")
        return

    # Import local helper
    from utils import mysql_sync

    secrets = {
        "host": os.environ.get("DB_HOST"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "dbname": os.environ.get("DB_NAME") or os.environ.get("DB_DATABASE"),
        "port": int(os.environ.get("DB_PORT") or 3306),
    }
    missing = [k for k, v in secrets.items() if not v and k in ("host", "user", "password", "dbname")]
    if missing:
        print("Missing DB secrets; cannot write to DB:", missing)
        return

    print(f"Writing {len(batting_rows)} batting rows for match {external_match_id} (dry-run disabled)")
    try:
        mysql_sync.upsert_batting(secrets, external_match_id, "1", batting_rows)
        print("DB write completed")
    except Exception as e:
        print("DB write failed:", e)


# --- Main ------------------------------------------------------------------

def main():
    saved = {}
    for name, url in ENDPOINTS.items():
        try:
            saved[name] = fetch_and_save(name, url)
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")

    # If scorecard response is present, attempt to map to batting rows and show a sample
    scard = saved.get("scard_40381") or {}
    if scard:
        batting_rows = map_scard_to_batting_rows(scard)
        sample = batting_rows[:5]
        print(f"Mapped {len(batting_rows)} batting rows; sample:")
        print(json.dumps(sample, indent=2, ensure_ascii=False))

        # Optionally write to DB if RUN_DB=1 and DB credentials are present
        maybe_write_to_db("40381", batting_rows, external_match_id="40381")

    print("Done.")


if __name__ == "__main__":
    main()
