import sys
import json
from typing import Any, Dict, Optional, List, cast

# Ensure project root (d:/test) is on sys.path so package imports work
sys.path.insert(0, r'd:/test')
from cricbuzz_app.utils.mysql_sync import upsert_match

# Load a sample match from saved API response
p = r'd:/test/cricbuzz_app/data/api_responses/live.json'
with open(p, 'r', encoding='utf-8') as f:
    data: Dict[str, Any] = json.load(f)

# Drill into data to the first matchInfo we can find
match_obj: Optional[Dict[str, Any]] = None
for type_match in cast(List[Dict[str, Any]], data.get('typeMatches', []) or []):
    for series in cast(List[Dict[str, Any]], type_match.get('seriesMatches', []) or []):
        series_info = cast(Dict[str, Any], series.get('seriesAdWrapper') or series.get('series') or {})
        matches = cast(List[Dict[str, Any]], series_info.get('matches') or [])
        for m in matches:
            mi = cast(Optional[Dict[str, Any]], m.get('matchInfo'))
            if mi:
                match_obj = mi
                break
        if match_obj:
            break
    if match_obj:
        break

if not match_obj:
    print('No matchInfo found in live.json')
else:
    # Safe, non-destructive extraction checks: print raw team objects
    # and the outputs of the module's extraction helpers without touching DB.
    # Import private helpers for diagnostics only; suppress the private-usage warning.
    from cricbuzz_app.utils.mysql_sync import _extract_team_name, _extract_team_id  # type: ignore[reportPrivateUsage]

    # Guard and cast match_obj before probing keys so static analyzers know types
    if match_obj:
        mcast = match_obj
        team1_raw = mcast.get("team1") or cast(Dict[str, Any], (mcast.get("teamInfo") or {})).get("team1")
        team2_raw = mcast.get("team2") or cast(Dict[str, Any], (mcast.get("teamInfo") or {})).get("team2")
    else:
        team1_raw = None
        team2_raw = None

    # Cast to object for repr() to avoid unknown-argument diagnostics
    print('RAW team1 object:', repr(cast(object, team1_raw)))
    print('RAW team2 object:', repr(cast(object, team2_raw)))
    print('EXTRACTED team1 name:', _extract_team_name(team1_raw))
    print('EXTRACTED team2 name:', _extract_team_name(team2_raw))
    print('EXTRACTED team1 id :', _extract_team_id(team1_raw))
    print('EXTRACTED team2 id :', _extract_team_id(team2_raw))
    # Also test normalized match dict shape (as produced by normalize_matches)
    normalized: Dict[str, Any] = {
        'matchId': cast(Optional[str], match_obj.get('matchId')) if match_obj else None,
        'team1_name': _extract_team_name(team1_raw),
        'team2_name': _extract_team_name(team2_raw),
        'team1_id': _extract_team_id(team1_raw),
        'team2_id': _extract_team_id(team2_raw),
        'seriesName': cast(Optional[str], (match_obj.get('seriesName') if match_obj else None) or (match_obj.get('series') if match_obj else None)),
    }
    print('\n--- Normalized-shape test (calling upsert_match with debug=True and engine=None) ---')
    try:
        upsert_match(None, normalized, debug=True)
    except Exception as e:
        print('Normalized test raised:', e)
