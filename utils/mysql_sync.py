"""
MySQL sync helpers

Provides functions to create the required MySQL tables (matches, batting_stats,
bowling_stats) and simple upsert helpers. Designed to work with SQLAlchemy if
installed, or fall back to pymysql for direct execution.

Usage (preferred):
    from utils.mysql_sync import get_engine_from_secrets, create_mysql_schema, upsert_match
    engine = get_engine_from_secrets({"host":..., "user":..., "password":..., "database":...})
    create_mysql_schema(engine)

Or, for a quick run (not recommended to commit credentials):
    python -c "from utils.mysql_sync import create_mysql_schema; create_mysql_schema({'host':'localhost', 'user':'root', 'password':'xxx', 'database':'cricketdb'})"

Note: This module does NOT write credentials to the repo. Use Streamlit secrets
or environment variables to keep credentials safe.
"""
from typing import Any, Dict, List, Optional, cast
from datetime import datetime
import json

# Optional SQLAlchemy/pymysql imports
create_engine: Any = None
pymysql_module: Any = None

try:
    # type: ignore[reportMissingImports]
    from sqlalchemy import create_engine as sa_create_engine, text  # type: ignore[reportMissingImports]
    create_engine = sa_create_engine
except Exception:
    create_engine = None  # type: ignore

try:
    # type: ignore[reportMissingImports]
    import pymysql as pymysql_module  # type: ignore[reportMissingImports]
except Exception as e:
    pymysql_module = None  # type: ignore
    import traceback
    print(f"Warning: Failed to import pymysql: {e}")
    traceback.print_exc()


def _get_pymysql() -> Any:
    """Lazy-load pymysql to handle Streamlit import issues."""
    global pymysql_module
    if pymysql_module is not None:
        return pymysql_module
    try:
        import pymysql as pm
        pymysql_module = pm
        return pymysql_module
    except Exception as e:
        raise RuntimeError(f"pymysql not available: {e}")
#         raise RuntimeError("pymysql is not available to execute statements")

#     conn = pymysql_module.connect(
#         host=secrets.get("host", "localhost"),
#         user=secrets.get("user"),
#         password=secrets.get("password"),
#         database=secrets.get("dbname") or secrets.get("database"),
#         port=int(secrets.get("port", 3306)),
#         charset="utf8mb4",
#         cursorclass=pymysql_module.cursors.DictCursor,
#     )
#     try:
#         with conn.cursor() as cur:
#             for stmt in statements:
#                 cur.execute(stmt)
#         conn.commit()
#     finally:
#         conn.close()


# def create_mysql_schema(engine_or_secrets: Any) -> None:
#     """Create matches, batting_stats, bowling_stats, and series tables in MySQL.

#     Accepts either a SQLAlchemy Engine (preferred) or a secrets dict for pymysql fallback.
#     """
#     statements = [
#         # Series table to store cricket series information
#         """
#         CREATE TABLE IF NOT EXISTS series (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_series_id VARCHAR(64) UNIQUE,
#             series_name VARCHAR(255) NOT NULL,
#             series_type VARCHAR(100),
#             start_date DATETIME,
#             end_date DATETIME,
#             country VARCHAR(100),
#             total_matches INT DEFAULT 0,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,

#         # Matches table with an external_match_id to store the provider's id
#         """
#         CREATE TABLE IF NOT EXISTS matches (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_match_id VARCHAR(64) UNIQUE,
#             series_id VARCHAR(64),
#             series_name VARCHAR(255),
#             match_desc VARCHAR(255),
#             match_format VARCHAR(50),
#             start_date DATETIME,
#             end_date DATETIME,
#             state VARCHAR(50),
#             status TEXT,
#             team1 VARCHAR(255),
#             team2 VARCHAR(255),
#             team1_id VARCHAR(64),
#             team2_id VARCHAR(64),
#             venue VARCHAR(255),
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,

#         # Batting stats
#         """
#         CREATE TABLE IF NOT EXISTS batting_stats (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_match_id VARCHAR(64),
#             innings_id VARCHAR(64),
#             player_name VARCHAR(255),
#             runs INT,
#             balls INT,
#             fours INT,
#             sixes INT,
#             strike_rate FLOAT,
#             dismissal TEXT,
#             meta JSON,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             INDEX (external_match_id)
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,

#         # Bowling stats
#         """
#         CREATE TABLE IF NOT EXISTS bowling_stats (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_match_id VARCHAR(64),
#             innings_id VARCHAR(64),
#             player_name VARCHAR(255),
#             overs FLOAT,
#             maidens INT,
#             runs_conceded INT,
#             wickets INT,
#             economy FLOAT,
#             meta JSON,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             INDEX (external_match_id)
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,
#         # Venues table to store venue metadata
#         """
#         CREATE TABLE IF NOT EXISTS venues (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_venue_id VARCHAR(64) UNIQUE,
#             venue_name VARCHAR(255) NOT NULL,
#             city VARCHAR(255),
#             country VARCHAR(255),
#             capacity INT,
#             meta JSON,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,

#         # Players table to store basic player info (optional, filled when available)
#         """
#         CREATE TABLE IF NOT EXISTS players (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_player_id VARCHAR(64) UNIQUE,
#             player_name VARCHAR(255) NOT NULL,
#             date_of_birth DATE,
#             country VARCHAR(100),
#             role VARCHAR(100),
#             meta JSON,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,

#         # Innings table to store high-level innings info (runs, wickets, overs, extras)
#         """
#         CREATE TABLE IF NOT EXISTS innings (
#             id BIGINT AUTO_INCREMENT PRIMARY KEY,
#             external_match_id VARCHAR(64),
#             innings_id VARCHAR(64),
#             batting_team VARCHAR(255),
#             bowling_team VARCHAR(255),
#             runs INT,
#             wickets INT,
#             overs FLOAT,
#             extras JSON,
#             meta JSON,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             INDEX (external_match_id)
#         ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#         """,
#     ]

#     # If a SQLAlchemy engine was passed
#     try:
#         if hasattr(engine_or_secrets, "connect") and create_engine is not None:
#             _execute_statements_sqlalchemy(engine_or_secrets, statements)
#             return
#     except Exception:
#         # fallback to secrets path below
#         pass

#     # Otherwise treat engine_or_secrets as secrets dict for pymysql
#     if isinstance(engine_or_secrets, dict):
#         _execute_statements_pymysql(cast(Dict[str, Any], engine_or_secrets), statements)
#         return

#     raise RuntimeError("Unsupported engine_or_secrets passed to create_mysql_schema")


# def upsert_match(engine_or_secrets: Any, match: Dict[str, Any], debug: bool = False) -> None:
#     """Insert or update a match record. Expects 'matchId' in match dict.

#     match is a dict from the API; this function maps a few fields and upserts.
#     """
#     # If caller passed a wrapper (e.g. {"matchInfo": {...}}), unwrap it
#     match_info = match.get("matchInfo")
#     if isinstance(match_info, dict):
#         match = cast(Dict[str, Any], match_info)

#     # Narrow types for commonly used fields to avoid Pylance unknown-type warnings
#     external_id = str(match.get("matchId") or match.get("match_id") or match.get("matchIdRaw") or "")
#     series_id = cast(Optional[str], match.get("seriesId") or match.get("series_id") or match.get("seriesIdRaw"))
#     series_name = cast(Optional[str], match.get("seriesName") or match.get("series_name"))
#     match_desc = cast(Optional[str], match.get("matchDesc") or match.get("matchDescText"))
#     match_format = cast(Optional[str], match.get("matchFormat"))
#     start_date = _convert_timestamp_to_datetime(match.get("startDate"))
#     end_date = _convert_timestamp_to_datetime(match.get("endDate"))
#     state = cast(Optional[str], match.get("state"))
#     status = cast(Optional[str], match.get("status"))
    
#     # Helper: robust team name extraction (prefer full name, fallback to short name)
#     def _extract_team_name(team_val: Any) -> Optional[str]:
#         if team_val is None:
#             return None

#         # If it's a JSON string containing an object, try to parse it
#         if isinstance(team_val, str):
#             s = team_val.strip()
#             if not s:
#                 return None
#             if s.startswith("{") or s.startswith("["):
#                 try:
#                     parsed = json.loads(s)
#                     return _extract_team_name(parsed)
#                 except Exception:
#                     return s or None
#             return s

#         # If it's a dict-like object, safely probe known keys
#         if isinstance(team_val, dict):
#             tdict = cast(Dict[str, Any], team_val)
#             for key in ("teamName", "teamname", "teamSName", "teamSname", "name", "shortName"):
#                 val = tdict.get(key)
#                 if val is None:
#                     continue
#                 if isinstance(val, str):
#                     v = val.strip()
#                     if v:
#                         return v
#                     continue
#                 try:
#                     sval = str(val)
#                     if sval:
#                         return sval
#                 except Exception:
#                     continue
#             # nested structures: sometimes name sits under a nested 'team' key
#             nested = tdict.get("team" or "teamName", None)
#             if isinstance(nested, dict):
#                 return _extract_team_name(nested)
#             return None

#         # If it's a list/tuple, try first element that yields a name
#         if isinstance(team_val, (list, tuple)):
#             for item in cast(Iterable[Any], team_val):
#                 nm = _extract_team_name(item)
#                 if nm:
#                     return nm
#             return None

#         # Fallback: coerce other scalar types to string
#         try:
#             return str(team_val)
#         except Exception:
#             return None

#     # Note: normalization helper removed to avoid unused-symbol diagnostics

#     # Extract team names and normalize IDs
#     team1_obj = match.get("team1") or match.get("team_1") or match.get("teamA") or match.get("team") or match.get("teamName")
#     team2_obj = match.get("team2") or match.get("team_2") or match.get("teamB") or match.get("team") or match.get("teamName")
#     team1 = _extract_team_name(team1_obj)
#     team2 = _extract_team_name(team2_obj)
    
#     # Extract team IDs
#     # Normalize team IDs to strings when present
#     if isinstance(team1_obj, dict):
#         t1dict = cast(Dict[str, Any], team1_obj)
#         t1 = t1dict.get("teamId")
#         team1_id = str(t1) if t1 is not None else None
#     else:
#         team1_id = cast(Optional[str], match.get("team1_id"))

#     if isinstance(team2_obj, dict):
#         t2dict = cast(Dict[str, Any], team2_obj)
#         t2 = t2dict.get("teamId")
#         team2_id = str(t2) if t2 is not None else None
#     else:
#         team2_id = cast(Optional[str], match.get("team2_id"))
    
#     # Extract venue (can be string or nested object)
#     venue_obj = cast(Any, match.get("venue") or match.get("venueInfo") or {})
#     if isinstance(venue_obj, dict):
#         venue = cast(Optional[str], venue_obj.get("ground") or venue_obj.get("venue"))  # type: ignore[union-attr]
#     else:
#         venue = cast(Optional[str], venue_obj)

#     insert_stmt = (
#         """
#         INSERT INTO matches (external_match_id, series_id, series_name, match_desc, match_format, start_date, end_date, state, status, team1, team2, team1_id, team2_id, venue)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         ON DUPLICATE KEY UPDATE
#             series_id = VALUES(series_id),
#             series_name = VALUES(series_name),
#             match_desc = VALUES(match_desc),
#             match_format = VALUES(match_format),
#             start_date = VALUES(start_date),
#             end_date = VALUES(end_date),
#             state = VALUES(state),
#             status = VALUES(status),
#             team1 = VALUES(team1),
#             team2 = VALUES(team2),
#             team1_id = VALUES(team1_id),
#             team2_id = VALUES(team2_id),
#             venue = VALUES(venue)
#         """
#     )

#     params: Tuple[Any, ...] = (
#         external_id,
#         series_id,
#         series_name,
#         match_desc,
#         match_format,
#         start_date,
#         end_date,
#         state,
#         status,
#         team1,
#         team2,
#         team1_id,
#         team2_id,
#         venue,
#     )

#     # If debug is enabled, print extracted values and avoid writing to DB
#     if debug:
#         try:
#             print("[upsert_match debug] external_id:", external_id)
#             print("[upsert_match debug] series_id:", series_id, "series_name:", series_name)
#             print("[upsert_match debug] team1:", team1, "team1_id:", team1_id)
#             print("[upsert_match debug] team2:", team2, "team2_id:", team2_id)
#             # show raw team objects keys/types for diagnosis
#             print("[upsert_match debug] raw team1_obj:", repr(cast(Dict[str, Any], team1_obj)))
#             print("[upsert_match debug] raw team2_obj:", repr(cast(Dict[str, Any], team2_obj)))
#             try:
#                 print("[upsert_match debug] match keys:", list(match.keys()))
#             except Exception:
#                 print("[upsert_match debug] match type:", type(match))
#         except Exception:
#             traceback.print_exc()
#         return

#     # Use SQLAlchemy if available
#     try:
#         if hasattr(engine_or_secrets, "connect") and create_engine is not None:
#             # Use raw DBAPI connection so the DB-API paramstyle ("%s") is used
#             raw_conn = engine_or_secrets.raw_connection()
#             cur = None
#             try:
#                 cur = raw_conn.cursor()
#                 cur.execute(insert_stmt, params)
#                 raw_conn.commit()
#             finally:
#                 if cur is not None:
#                     try:
#                         cur.close()
#                     except Exception:
#                         pass
#                 try:
#                     raw_conn.close()
#                 except Exception:
#                     pass
#             return
#     except Exception:
#         traceback.print_exc()

#     # Fallback to pymysql using secrets dict and parameter style
#     if isinstance(engine_or_secrets, dict):
#         secrets = cast(Dict[str, Any], engine_or_secrets)
#         if pymysql_module is None:
#             raise RuntimeError("pymysql not available for upsert")
#         # Normalize port value to an int to avoid unknown-type diagnostics
#         port_val = secrets.get("port", 3306)
#         try:
#             port = int(port_val)
#         except Exception:
#             port = 3306

#         conn = pymysql_module.connect(
#             host=secrets.get("host", "localhost"),
#             user=secrets.get("user"),
#             password=secrets.get("password"),
#             database=secrets.get("dbname") or secrets.get("database"),
#             port=port,
#             charset="utf8mb4",
#             cursorclass=pymysql_module.cursors.DictCursor,
#         )
#         try:
#             with conn.cursor() as cur:
#                 cur.execute(insert_stmt, params)
#             conn.commit()
#         finally:
#             conn.close()
#         return

#     raise RuntimeError("Unsupported engine_or_secrets for upsert_match")


# def upsert_batting(engine_or_secrets: Any, external_match_id: str, innings_id: str, batting_rows: List[Dict[str, Any]]) -> None:
#     """Insert batting rows for a match. batting_rows is a list of dicts with keys: player_name, runs, balls, fours, sixes, strike_rate, dismissal"""
#     insert_stmt = (
#         """
#         INSERT INTO batting_stats (external_match_id, innings_id, player_name, runs, balls, fours, sixes, strike_rate, dismissal, meta)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#     )

#     # Prepare rows
#     params_list: List[Tuple[Any, ...]] = []
#     for r in batting_rows:
#         meta = json.dumps({k: v for k, v in r.items() if k not in ["player_name", "runs", "balls", "fours", "sixes", "strike_rate", "dismissal"]})
#         params_list.append(
#             (
#                 external_match_id,
#                 innings_id,
#                 r.get("player_name"),
#                 r.get("runs"),
#                 r.get("balls"),
#                 r.get("fours"),
#                 r.get("sixes"),
#                 r.get("strike_rate"),
#                 r.get("dismissal"),
#                 meta,
#             )
#         )

#     try:
#         if hasattr(engine_or_secrets, "connect") and create_engine is not None:
#             # Use raw DBAPI connection to execute batched inserts with "%s" paramstyle
#             raw_conn = engine_or_secrets.raw_connection()
#             cur = None
#             try:
#                 cur = raw_conn.cursor()
#                 for p in params_list:
#                     cur.execute(insert_stmt, p)
#                 raw_conn.commit()
#             finally:
#                 if cur is not None:
#                     try:
#                         cur.close()
#                     except Exception:
#                         pass
#                 try:
#                     raw_conn.close()
#                 except Exception:
#                     pass
#             return
#     except Exception:
#         traceback.print_exc()

#     if isinstance(engine_or_secrets, dict):
#         secrets = cast(Dict[str, Any], engine_or_secrets)
#         if pymysql_module is None:
#             raise RuntimeError("pymysql not available for upsert_batting")
#         # Normalize port for pymysql
#         port_val = secrets.get("port", 3306)
#         try:
#             port = int(port_val)
#         except Exception:
#             port = 3306

#         conn = pymysql_module.connect(
#             host=secrets.get("host", "localhost"),
#             user=secrets.get("user"),
#             password=secrets.get("password"),
#             database=secrets.get("dbname") or secrets.get("database"),
#             port=port,
#             charset="utf8mb4",
#             cursorclass=pymysql_module.cursors.DictCursor,
#         )
#         try:
#             with conn.cursor() as cur:
#                 for p in params_list:
#                     cur.execute(insert_stmt, p)
#             conn.commit()
#         finally:
#             conn.close()
#         return

#     raise RuntimeError("Unsupported engine_or_secrets for upsert_batting")


# def upsert_bowling(engine_or_secrets: Any, external_match_id: str, innings_id: str, bowling_rows: List[Dict[str, Any]]) -> None:
#     """Insert bowling rows for a match. bowling_rows is a list of dicts with keys: player_name, overs, maidens, runs_conceded, wickets, economy"""
#     insert_stmt = (
#         """
#         INSERT INTO bowling_stats (external_match_id, innings_id, player_name, overs, maidens, runs_conceded, wickets, economy, meta)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#     )

#     params_list: List[Tuple[Any, ...]] = []
#     for r in bowling_rows:
#         meta = json.dumps({k: v for k, v in r.items() if k not in ["player_name", "overs", "maidens", "runs_conceded", "wickets", "economy"]})
#         params_list.append(
#             (
#                 external_match_id,
#                 innings_id,
#                 r.get("player_name"),
#                 r.get("overs"),
#                 r.get("maidens"),
#                 r.get("runs_conceded"),
#                 r.get("wickets"),
#                 r.get("economy"),
#                 meta,
#             )
#         )

#     try:
#         if hasattr(engine_or_secrets, "connect") and create_engine is not None:
#             # Use raw DBAPI connection to execute batched inserts with "%s" paramstyle
#             raw_conn = engine_or_secrets.raw_connection()
#             cur = None
#             try:
#                 cur = raw_conn.cursor()
#                 for p in params_list:
#                     cur.execute(insert_stmt, p)
#                 raw_conn.commit()
#             finally:
#                 if cur is not None:
#                     try:
#                         cur.close()
#                     except Exception:
#                         pass
#                 try:
#                     raw_conn.close()
#                 except Exception:
#                     pass
#             return
#     except Exception:
#         traceback.print_exc()

#     if isinstance(engine_or_secrets, dict):
#         secrets = cast(Dict[str, Any], engine_or_secrets)
#         if pymysql_module is None:
#             raise RuntimeError("pymysql not available for upsert_bowling")
#         # Normalize port for pymysql
#         port_val = secrets.get("port", 3306)
#         try:
#             port = int(port_val)
#         except Exception:
#             port = 3306

#         conn = pymysql_module.connect(
#             host=secrets.get("host", "localhost"),
#             user=secrets.get("user"),
#             password=secrets.get("password"),
#             database=secrets.get("dbname") or secrets.get("database"),
#             port=port,
#             charset="utf8mb4",
#             cursorclass=pymysql_module.cursors.DictCursor,
#         )
#         try:
#             with conn.cursor() as cur:
#                 for p in params_list:
#                     cur.execute(insert_stmt, p)
#             conn.commit()
#         finally:
#             conn.close()
#         return

#     raise RuntimeError("Unsupported engine_or_secrets for upsert_bowling")

"""
MySQL sync helpers (corrected)

- Fixed team extraction & insertion
- Added teams table and upsert helpers for series & teams
- Ensures matches, batting_stats and bowling_stats insert the correct data
- Works with SQLAlchemy engine (preferred) or a pymysql secrets dict
"""
from typing import Any, Dict, List, Optional, Tuple, Iterable, cast
from datetime import datetime
import traceback

def _convert_timestamp_to_datetime(timestamp_val: Any) -> Optional[str]:
    if timestamp_val is None or timestamp_val == "":
        return None
    if isinstance(timestamp_val, str):
        # If looks numeric (ms), convert; otherwise assume string datetime
        try:
            numeric = float(timestamp_val)
            timestamp_seconds = numeric / 1000.0
            dt = datetime.fromtimestamp(timestamp_seconds)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return timestamp_val
    try:
        timestamp_seconds = float(timestamp_val) / 1000.0
        dt = datetime.fromtimestamp(timestamp_seconds)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


# Optional SQLAlchemy/pymysql imports
create_engine: Any = None
pymysql: Any = None
try:
    # type: ignore[reportMissingImports]
    from sqlalchemy import create_engine, text  # type: ignore[reportMissingImports]
    from sqlalchemy.engine import Engine  # type: ignore[reportMissingImports]
except Exception:
    create_engine = None  # type: ignore
    try:
        # type: ignore[reportMissingImports]
        import pymysql  # type: ignore[reportMissingImports]
    except Exception:
        pymysql = None  # type: ignore


def get_engine_from_secrets(secrets: Dict[str, Any]) -> Optional[Any]:
    host = secrets.get("host", "localhost")
    port = secrets.get("port", 3306)
    user = secrets.get("user")
    password = secrets.get("password")
    dbname = secrets.get("dbname") or secrets.get("database")

    if not (user and password and dbname):
        raise ValueError("MySQL secrets must include user, password and database")

    if create_engine is not None:
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4"
        engine = create_engine(url)
        return engine

    return None


def _execute_statements_sqlalchemy(engine: Any, statements: List[str]) -> None:
    from sqlalchemy import text  # type: ignore[reportMissingImports]
    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()


def _execute_statements_pymysql(secrets: Dict[str, Any], statements: List[str]) -> None:
    pm = _get_pymysql()

    conn = pm.connect(
        host=secrets.get("host", "localhost"),
        user=secrets.get("user"),
        password=secrets.get("password"),
        database=secrets.get("dbname") or secrets.get("database"),
        port=int(secrets.get("port", 3306)),
        charset="utf8mb4",
        cursorclass=pm.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def create_mysql_schema(engine_or_secrets: Any) -> None:
    """Create required tables including teams (added)."""
    statements = [
        # Series table
        """
        CREATE TABLE IF NOT EXISTS series (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_series_id VARCHAR(64) UNIQUE,
            series_name VARCHAR(255) NOT NULL,
            series_type VARCHAR(100),
            start_date DATETIME,
            end_date DATETIME,
            country VARCHAR(100),
            total_matches INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Teams table (NEW)
        """
        CREATE TABLE IF NOT EXISTS teams (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_team_id VARCHAR(64) UNIQUE,
            team_name VARCHAR(255) NOT NULL,
            country VARCHAR(100),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Matches table
        """
        CREATE TABLE IF NOT EXISTS matches (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(64) UNIQUE,
            series_id VARCHAR(64),
            series_name VARCHAR(255),
            match_desc VARCHAR(255),
            match_format VARCHAR(50),
            start_date DATETIME,
            end_date DATETIME,
            state VARCHAR(50),
            status TEXT,
            team1 VARCHAR(255),
            team2 VARCHAR(255),
            team1_id VARCHAR(64),
            team2_id VARCHAR(64),
            venue VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Batting stats
        """
        CREATE TABLE IF NOT EXISTS batting_stats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(64),
            innings_id VARCHAR(64),
            player_name VARCHAR(255),
            runs INT,
            balls INT,
            fours INT,
            sixes INT,
            strike_rate FLOAT,
            dismissal TEXT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (external_match_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Bowling stats
        """
        CREATE TABLE IF NOT EXISTS bowling_stats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(64),
            innings_id VARCHAR(64),
            player_name VARCHAR(255),
            overs FLOAT,
            maidens INT,
            runs_conceded INT,
            wickets INT,
            economy FLOAT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (external_match_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Venues
        """
        CREATE TABLE IF NOT EXISTS venues (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_venue_id VARCHAR(64) UNIQUE,
            venue_name VARCHAR(255) NOT NULL,
            city VARCHAR(255),
            country VARCHAR(255),
            capacity INT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Players
        """
        CREATE TABLE IF NOT EXISTS players (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_player_id VARCHAR(64) UNIQUE,
            player_name VARCHAR(255) NOT NULL,
            date_of_birth DATE,
            country VARCHAR(100),
            role VARCHAR(100),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        # Innings
        """
        CREATE TABLE IF NOT EXISTS innings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(64),
            innings_id VARCHAR(64),
            batting_team VARCHAR(255),
            bowling_team VARCHAR(255),
            runs INT,
            wickets INT,
            overs FLOAT,
            extras JSON,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (external_match_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ]

    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            _execute_statements_sqlalchemy(engine_or_secrets, statements)
            return
    except Exception:
        # fall back to pymysql path
        pass

    if isinstance(engine_or_secrets, dict):
        _execute_statements_pymysql(cast(Dict[str, Any], engine_or_secrets), statements)
        return

    raise RuntimeError("Unsupported engine_or_secrets passed to create_mysql_schema")


# -------------------------
# Helper: robust team name extraction
# -------------------------
def _extract_team_name(team_val: Any) -> Optional[str]:
    if team_val is None:
        return None

    if isinstance(team_val, str):
        s = team_val.strip()
        if not s:
            return None
        # maybe JSON in string
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = json.loads(s)
                return _extract_team_name(parsed)
            except Exception:
                return s
        return s

    if isinstance(team_val, dict):
        tdict = cast(Dict[str, Any], team_val)
        for key in ("teamName", "teamname", "teamSName", "teamSname", "name", "shortName", "displayName"):
            val = tdict.get(key)
            if val:
                return str(val).strip()
        # nested checks
        for nested_key in ("team", "teamInfo"):
            nested = tdict.get(nested_key)
            if isinstance(nested, dict):
                nm = _extract_team_name(nested)
                if nm:
                    return nm
        return None

    if isinstance(team_val, (list, tuple)):
        for item in cast(Iterable[Any], team_val):
            nm = _extract_team_name(item)
            if nm:
                return nm
        return None

    try:
        if isinstance(team_val, (dict, list, tuple)):
            return json.dumps(team_val)
        return str(cast(object, team_val))
    except Exception:
        return None


def _extract_team_id(team_val: Any, fallback: Optional[str] = None) -> Optional[str]:
    if team_val is None:
        return None
    if isinstance(team_val, str):
        s = team_val.strip()
        if s:
            return s
        return None
    if isinstance(team_val, dict):
        tdict = cast(Dict[str, Any], team_val)
        for key in ("teamId", "id", "team_id", "externalId", "external_team_id"):
            val = tdict.get(key)
            if val is not None:
                return str(val)
    try:
        if isinstance(team_val, (dict, list, tuple)):
            return json.dumps(team_val)
        return str(team_val)
    except Exception:
        return None


# -------------------------
# Upsert helpers for series & teams
# -------------------------
def upsert_series(engine_or_secrets: Any, external_series_id: Optional[str], series_name: Optional[str]) -> Optional[str]:
    """Insert or update a series row. Requires external_series_id as it's the PRIMARY KEY."""
    if not external_series_id:
        # Can't insert without a series_id since it's the PRIMARY KEY
        return None

    # Parse series_id as integer if possible
    try:
        series_id = int(external_series_id)
    except (ValueError, TypeError):
        # If it's not numeric, we still can't use it as PRIMARY KEY
        return None

    insert_stmt = """
        INSERT INTO series (series_id, series_name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE series_name = VALUES(series_name)
    """
    params = (series_id, series_name)

    # SQLAlchemy path
    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            raw_conn = engine_or_secrets.raw_connection()
            cur = None
            try:
                cur = raw_conn.cursor()
                cur.execute(insert_stmt, params)
                raw_conn.commit()
            finally:
                if cur:
                    try:
                        cur.close()
                    except Exception:
                        pass
                try:
                    raw_conn.close()
                except Exception:
                    pass
            return external_series_id
    except Exception:
        traceback.print_exc()

    if isinstance(engine_or_secrets, dict):
        pm = _get_pymysql()
        secrets = cast(Dict[str, Any], engine_or_secrets)
        port_val = secrets.get("port", 3306)
        try:
            port = int(port_val)
        except Exception:
            port = 3306
        conn = pm.connect(
            host=secrets.get("host", "localhost"),
            user=secrets.get("user"),
            password=secrets.get("password"),
            database=secrets.get("dbname") or secrets.get("database"),
            port=port,
            charset="utf8mb4",
            cursorclass=pm.cursors.DictCursor,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(insert_stmt, params)
            conn.commit()
        finally:
            conn.close()
        return external_series_id

    raise RuntimeError("Unsupported engine_or_secrets for upsert_series")


def upsert_team(engine_or_secrets: Any, external_team_id: Optional[str], team_name: Optional[str]) -> Optional[str]:
    """Insert or update a team row. Requires external_team_id as it's the PRIMARY KEY."""
    if not external_team_id:
        # Can't insert without a teamId since it's the PRIMARY KEY
        return None

    # Parse teamId as integer if possible
    try:
        team_id = int(external_team_id)
    except (ValueError, TypeError):
        # If it's not numeric, we still can't use it as PRIMARY KEY
        return None

    insert_stmt = """
        INSERT INTO teams (teamId, teamName)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE teamName = VALUES(teamName)
    """
    params = (team_id, team_name)

    # SQLAlchemy
    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            raw_conn = engine_or_secrets.raw_connection()
            cur = None
            try:
                cur = raw_conn.cursor()
                cur.execute(insert_stmt, params)
                raw_conn.commit()
            finally:
                if cur:
                    try:
                        cur.close()
                    except Exception:
                        pass
                try:
                    raw_conn.close()
                except Exception:
                    pass
            return external_team_id
    except Exception:
        traceback.print_exc()

    # pymysql
    if isinstance(engine_or_secrets, dict):
        pm = _get_pymysql()
        secrets = cast(Dict[str, Any], engine_or_secrets)
        port_val = secrets.get("port", 3306)
        try:
            port = int(port_val)
        except Exception:
            port = 3306
        conn = pm.connect(
            host=secrets.get("host", "localhost"),
            user=secrets.get("user"),
            password=secrets.get("password"),
            database=secrets.get("dbname") or secrets.get("database"),
            port=port,
            charset="utf8mb4",
            cursorclass=pm.cursors.DictCursor,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(insert_stmt, params)
            conn.commit()
        finally:
            conn.close()
        return external_team_id

    raise RuntimeError("Unsupported engine_or_secrets for upsert_team")


# -------------------------
# Main upsert_match (fixed)
# -------------------------
def upsert_match(engine_or_secrets: Any, match: Dict[str, Any], debug: bool = False) -> None:
    """Insert or update a match record. Expects 'matchId' (or similar) in match dict."""
    # Unwrap wrapper if present
    match_info = match.get("matchInfo")
    if isinstance(match_info, dict):
        match = cast(Dict[str, Any], match_info)

    external_id = str(match.get("matchId") or match.get("match_id") or match.get("matchIdRaw") or match.get("id") or "")
    series_id_raw = match.get("seriesId") or match.get("series_id") or match.get("seriesIdRaw") or match.get("seriesExternalId")
    series_name = cast(Optional[str], match.get("seriesName") or match.get("series_name"))

    # Convert dates
    start_date = _convert_timestamp_to_datetime(match.get("startDate"))
    end_date = _convert_timestamp_to_datetime(match.get("endDate"))
    state = cast(Optional[str], match.get("state"))
    status = cast(Optional[str], match.get("status"))
    match_desc = cast(Optional[str], match.get("matchDesc") or match.get("matchDescText"))
    match_format = cast(Optional[str], match.get("matchFormat"))

    # -----------------------
    # Team extraction (robust)
    # -----------------------
    # Try many common key names, including nested teamInfo structures.
    team1_obj = cast(Any, (
        match.get("team1")
        or match.get("team_1")
        or match.get("teamA")
        or match.get("teamOne")
        or cast(Dict[str, Any], (match.get("teamInfo") or {})).get("team1")
        or match.get("teamName")
        or match.get("homeTeam")
    ))
    team2_obj = cast(Any, (
        match.get("team2")
        or match.get("team_2")
        or match.get("teamB")
        or match.get("teamTwo")
        or cast(Dict[str, Any], (match.get("teamInfo") or {})).get("team2")
        or match.get("teamName")
        or match.get("awayTeam")
    ))

    # Extract readable names. Support both raw API shapes (team1/team2 dicts)
    # and normalized shapes produced by `normalize_matches` (team1_name/team2_name).
    team1 = _extract_team_name(team1_obj) or cast(Optional[str], match.get("team1_name") or match.get("team1_short") or match.get("team1SName"))
    team2 = _extract_team_name(team2_obj) or cast(Optional[str], match.get("team2_name") or match.get("team2_short") or match.get("team2SName"))

    # Extract team external IDs (if provided)
    team1_ext_id = _extract_team_id(team1_obj) or (match.get("team1_id") or match.get("team1Id"))
    team2_ext_id = _extract_team_id(team2_obj) or (match.get("team2_id") or match.get("team2Id"))

    # Venue extraction
    venue_obj = cast(Any, match.get("venue") or match.get("venueInfo") or {})
    if isinstance(venue_obj, dict):
        vdict = cast(Dict[str, Any], venue_obj)
        venue = cast(Optional[str], vdict.get("ground") or vdict.get("venue") or vdict.get("name"))
    else:
        venue = cast(Optional[str], venue_obj)

    # If debug, print extracted values and don't write
    if debug:
        try:
            print("[upsert_match debug] external_id:", external_id)
            print("[upsert_match debug] raw_series_id:", series_id_raw, "series_name:", series_name)
            print("[upsert_match debug] team1:", team1, "team1_ext_id:", team1_ext_id)
            print("[upsert_match debug] team2:", team2, "team2_ext_id:", team2_ext_id)
            print("[upsert_match debug] venue:", venue)
            try:
                print("[upsert_match debug] match keys:", list(match.keys()))
            except Exception:
                print("[upsert_match debug] match type:", type(match))
        except Exception:
            traceback.print_exc()
        return

    # Upsert series and teams first, so foreign keys/ids are present
    try:
        series_ext_id = upsert_series(engine_or_secrets, str(series_id_raw) if series_id_raw else None, series_name)
    except Exception:
        traceback.print_exc()
        series_ext_id = series_id_raw or None

    try:
        team1_saved_ext = upsert_team(engine_or_secrets, team1_ext_id, team1)
    except Exception:
        traceback.print_exc()
        team1_saved_ext = team1_ext_id or team1

    try:
        team2_saved_ext = upsert_team(engine_or_secrets, team2_ext_id, team2)
    except Exception:
        traceback.print_exc()
        team2_saved_ext = team2_ext_id or team2

    # Finally insert / update match row
    insert_stmt = (
        """
        INSERT INTO matches (external_match_id, series_id, series_name, match_desc, match_format, start_date, end_date, state, status, team1, team2, team1_id, team2_id, venue)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            series_id = VALUES(series_id),
            series_name = VALUES(series_name),
            match_desc = VALUES(match_desc),
            match_format = VALUES(match_format),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date),
            state = VALUES(state),
            status = VALUES(status),
            team1 = VALUES(team1),
            team2 = VALUES(team2),
            team1_id = VALUES(team1_id),
            team2_id = VALUES(team2_id),
            venue = VALUES(venue)
        """
    )
    params: Tuple[Any, ...] = (
        external_id,
        series_ext_id,
        series_name,
        match_desc,
        match_format,
        start_date,
        end_date,
        state,
        status,
        team1,
        team2,
        team1_saved_ext,
        team2_saved_ext,
        venue,
    )

    # SQLAlchemy raw connection
    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            raw_conn = engine_or_secrets.raw_connection()
            cur = None
            try:
                cur = raw_conn.cursor()
                cur.execute(insert_stmt, params)
                raw_conn.commit()
            finally:
                if cur is not None:
                    try:
                        cur.close()
                    except Exception:
                        pass
                try:
                    raw_conn.close()
                except Exception:
                    pass
            return
    except Exception:
        traceback.print_exc()

    # pymysql fallback
    if isinstance(engine_or_secrets, dict):
        secrets = cast(Dict[str, Any], engine_or_secrets)
        pm = _get_pymysql()
        port_val = secrets.get("port", 3306)
        try:
            port = int(port_val)
        except Exception:
            port = 3306

        conn = pm.connect(
            host=secrets.get("host", "localhost"),
            user=secrets.get("user"),
            password=secrets.get("password"),
            database=secrets.get("dbname") or secrets.get("database"),
            port=port,
            charset="utf8mb4",
            cursorclass=pm.cursors.DictCursor,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(insert_stmt, params)
            conn.commit()
        finally:
            conn.close()
        return

    raise RuntimeError("Unsupported engine_or_secrets for upsert_match")


# -------------------------
# Batting & Bowling upserts (unchanged aside from robust param usage)
# -------------------------
def upsert_batting(engine_or_secrets: Any, external_match_id: str, innings_id: str, batting_rows: List[Dict[str, Any]]) -> None:
    insert_stmt = (
        """
        INSERT INTO batting_stats (external_match_id, innings_id, player_name, runs, balls, fours, sixes, strike_rate, dismissal, meta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    )
    params_list: List[Tuple[Any, ...]] = []
    for r in batting_rows:
        meta = json.dumps({k: v for k, v in r.items() if k not in ["player_name", "runs", "balls", "fours", "sixes", "strike_rate", "dismissal"]})
        params_list.append(
            (
                external_match_id,
                innings_id,
                r.get("player_name"),
                r.get("runs"),
                r.get("balls"),
                r.get("fours"),
                r.get("sixes"),
                r.get("strike_rate"),
                r.get("dismissal"),
                meta,
            )
        )

    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            raw_conn = engine_or_secrets.raw_connection()
            cur = None
            try:
                cur = raw_conn.cursor()
                for p in params_list:
                    cur.execute(insert_stmt, p)
                raw_conn.commit()
            finally:
                if cur is not None:
                    try:
                        cur.close()
                    except Exception:
                        pass
                try:
                    raw_conn.close()
                except Exception:
                    pass
            return
    except Exception:
        traceback.print_exc()

    if isinstance(engine_or_secrets, dict):
        secrets = cast(Dict[str, Any], engine_or_secrets)
        pm = _get_pymysql()
        port_val = secrets.get("port", 3306)
        try:
            port = int(port_val)
        except Exception:
            port = 3306
        conn = pm.connect(
            host=secrets.get("host", "localhost"),
            user=secrets.get("user"),
            password=secrets.get("password"),
            database=secrets.get("dbname") or secrets.get("database"),
            port=port,
            charset="utf8mb4",
            cursorclass=pm.cursors.DictCursor,
        )
        try:
            with conn.cursor() as cur:
                for p in params_list:
                    cur.execute(insert_stmt, p)
            conn.commit()
        finally:
            conn.close()
        return

    raise RuntimeError("Unsupported engine_or_secrets for upsert_batting")


def upsert_bowling(engine_or_secrets: Any, external_match_id: str, innings_id: str, bowling_rows: List[Dict[str, Any]]) -> None:
    insert_stmt = (
        """
        INSERT INTO bowling_stats (external_match_id, innings_id, player_name, overs, maidens, runs_conceded, wickets, economy, meta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    )
    params_list: List[Tuple[Any, ...]] = []
    for r in bowling_rows:
        meta = json.dumps({k: v for k, v in r.items() if k not in ["player_name", "overs", "maidens", "runs_conceded", "wickets", "economy"]})
        params_list.append(
            (
                external_match_id,
                innings_id,
                r.get("player_name"),
                r.get("overs"),
                r.get("maidens"),
                r.get("runs_conceded"),
                r.get("wickets"),
                r.get("economy"),
                meta,
            )
        )

    try:
        if hasattr(engine_or_secrets, "connect") and create_engine is not None:
            raw_conn = engine_or_secrets.raw_connection()
            cur = None
            try:
                cur = raw_conn.cursor()
                for p in params_list:
                    cur.execute(insert_stmt, p)
                raw_conn.commit()
            finally:
                if cur is not None:
                    try:
                        cur.close()
                    except Exception:
                        pass
                try:
                    raw_conn.close()
                except Exception:
                    pass
            return
    except Exception:
        traceback.print_exc()

    if isinstance(engine_or_secrets, dict):
        secrets = cast(Dict[str, Any], engine_or_secrets)
        pm = _get_pymysql()
        port_val = secrets.get("port", 3306)
        try:
            port = int(port_val)
        except Exception:
            port = 3306
        conn = pm.connect(
            host=secrets.get("host", "localhost"),
            user=secrets.get("user"),
            password=secrets.get("password"),
            database=secrets.get("dbname") or secrets.get("database"),
            port=port,
            charset="utf8mb4",
            cursorclass=pm.cursors.DictCursor,
        )
        try:
            with conn.cursor() as cur:
                for p in params_list:
                    cur.execute(insert_stmt, p)
            conn.commit()
        finally:
            conn.close()
        return

    raise RuntimeError("Unsupported engine_or_secrets for upsert_bowling")
