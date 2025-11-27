import json
from typing import Any, Optional, Dict, Iterable, cast

# Minimal standalone extractor copied from mysql_sync._extract_team_name for testing

def extract_team_name(team_val: Any) -> Optional[str]:
    if team_val is None:
        return None

    if isinstance(team_val, str):
        s: str = team_val.strip()
        if not s:
            return None
        if s.startswith('{') or s.startswith('['):
            try:
                parsed: Any = json.loads(s)
                return extract_team_name(parsed)
            except Exception:
                return s
        return s

    if isinstance(team_val, dict):
        tdict = cast(Dict[str, Any], team_val)
        for key in ("teamName", "teamname", "teamSName", "teamSname", "name", "shortName"):
            val: Any = tdict.get(key)
            if val is None:
                continue
            if isinstance(val, str):
                v: str = val.strip()
                if v:
                    return v
                continue
            try:
                sval = str(val)
                if sval:
                    return sval
            except Exception:
                continue
        nested: Any = tdict.get("team")
        if isinstance(nested, dict):
            return extract_team_name(cast(Dict[str, Any], nested))
        return None

    if isinstance(team_val, (list, tuple)):
        for item in cast(Iterable[Any], team_val):
            nm = extract_team_name(item)
            if nm:
                return nm
        return None

    try:
        return str(team_val)
    except Exception:
        return None


if __name__ == '__main__':
    sample: Dict[str, Dict[str, Any]] = {
        "team1": {
            "teamId": 2918,
            "teamName": "Janakpur Bolts",
            "teamSName": "JAB",
            "imageId": 174284,
        },
        "team2": {
            "teamId": 2937,
            "teamName": "Kathmandu Gorkhas",
            "teamSName": "KAG",
            "imageId": 174284,
        },
    }

    print('team1 ->', extract_team_name(sample['team1']))
    print('team2 ->', extract_team_name(sample['team2']))
