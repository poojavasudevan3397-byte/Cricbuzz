

"""
Database Connection and Schema Management
Supports SQLite, PostgreSQL, and MySQL
"""

# pyright: reportUnknownMemberType=false
import sqlite3
import pymysql
# `pymysql` is optional at runtime; avoid importing it unconditionally so the
# module can be imported when the package is not installed. A runtime try/except
# below will attempt to import it and otherwise leave `pymysql` as None.
from typing import Dict, Any, cast, Sequence
from collections.abc import Mapping
import pandas as pd
import streamlit as st
import json
from typing import cast

# Treat Streamlit's dynamic members as Any for Pylance (markdown, warning, error, etc.)
st = cast(Any, st)

# Optional MySQL support
pymysql = None
try:
    # type: ignore[reportMissingImports]
    import pymysql  # type: ignore[reportMissingImports]
except Exception:
    pymysql = None  # type: ignore

# Optional SQLAlchemy support for better pandas compatibility with MySQL
sqlalchemy = None
try:
    from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
    sqlalchemy = True  # type: ignore
except Exception:
    sqlalchemy = None  # type: ignore


def fetch_data_from_pymysql(query: str, conn: Any) -> pd.DataFrame:
    """
    Helper function to safely fetch data from pymysql connection.
    Converts cursor results to DataFrame, handling column names properly.
    """
    try:
        if hasattr(conn, 'cursor'):
            # Raw pymysql connection
            cursor = conn.cursor()
            cursor.execute(query)
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]
            # Fetch all data
            data = cursor.fetchall()
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=columns)
            cursor.close()
            return df
        else:
            # SQLAlchemy engine or other connection
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)[:100]}")
        return pd.DataFrame()

try:
    # type: ignore[reportMissingImports]
    from utils.mysql_sync import create_mysql_schema  # type: ignore[reportMissingImports]
except Exception:
    create_mysql_schema = None  # type: ignore

class DatabaseConnection:
    """Handle database operations for Cricbuzz analytics"""

    def __init__(self, db_type: str = "sqlite", db_path: str = "cricbuzz.db"):
        """Initialize database connection"""
        self.db_type = db_type
        self.db_path = db_path
        self.connection = None

        if db_type == "sqlite":
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        else:
            raise NotImplementedError("PostgreSQL/MySQL support coming soon")

    def init_schema(self) -> None:
        """Initialize database schema"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]

        # Create tables
        cursor.execute("DROP TABLE IF EXISTS players")
        cursor.execute(
            """
            CREATE TABLE players (
                team_id INTEGER,
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                country TEXT,
                role TEXT,
                batting_style TEXT,
                bowling_style TEXT,
                meta TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_description TEXT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                match_format TEXT,
                venue_id INTEGER,
                match_date TIMESTAMP,
                winning_team TEXT,
                victory_margin TEXT,
                victory_type TEXT,
                toss_winner TEXT,
                toss_decision TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                capacity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS series (
                series_id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_name TEXT NOT NULL UNIQUE,
                series_type TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                country TEXT,
                total_matches INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS innings (
                innings_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                batting_team TEXT NOT NULL,
                bowling_team TEXT NOT NULL,
                total_runs INTEGER,
                total_wickets INTEGER,
                total_overs FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS batsmen (
                batsman_id INTEGER PRIMARY KEY AUTOINCREMENT,
                innings_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                batting_position INTEGER,
                runs_scored INTEGER,
                balls_faced INTEGER,
                fours INTEGER,
                sixes INTEGER,
                strike_rate FLOAT,
                dismissal_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (innings_id) REFERENCES innings(innings_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bowlers (
                bowler_id INTEGER PRIMARY KEY AUTOINCREMENT,
                innings_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                overs_bowled FLOAT,
                maidens INTEGER,
                runs_conceded INTEGER,
                wickets_taken INTEGER,
                economy_rate FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (innings_id) REFERENCES innings(innings_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
            """
        )

        self.connection.commit()  # type: ignore[attr-defined]

    def insert_player(
        self,
        team_id: int,
        player_name: str,
        country: str,
        role: str,
        batting_style: str,
        bowling_style: str,
        meta: str = ""
    ) -> int:
        """Insert a new player"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        if getattr(self, "db_type", "sqlite") == "mysql":
            placeholders = "%s, %s, %s, %s, %s, %s, %s"
            sql = (
                """
                INSERT INTO players (team_id, player_name, country, role, batting_style, bowling_style, meta)
                VALUES (""" + placeholders + ")"
            )
            params = (team_id, player_name, country, role, batting_style, bowling_style, meta)
        else:
            placeholders = "?, ?, ?, ?, ?, ?, ?"
            sql = (
                """
                INSERT INTO players (team_id, player_name, country, role, batting_style, bowling_style, meta)
                VALUES (""" + placeholders + ")"
            )
            params = (team_id, player_name, country, role, batting_style, bowling_style, meta)

        cursor.execute(sql, params)
        try:
            print("[db] insert_player executing (db_type=", getattr(self, "db_type", None), ")")
            print("[db] SQL:", sql)
            print("[db] params:", params)
            print("[db] param types:", tuple(type(p) for p in params))
        except Exception:
            pass

        self.connection.commit()  # type: ignore[attr-defined]
        return cursor.lastrowid or 0  # type: ignore[attr-defined]
    
    def update_player(self, player_id: int, **kwargs: Any) -> None:
        """Update player record"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        allowed_fields = [
            "player_name",
            "country",
            "role",
            "batting_style",
            "bowling_style",
            "total_runs",
            "total_wickets",
            "batting_average",
            "bowling_average",
        ]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if updates:
            if getattr(self, "db_type", "sqlite") == "mysql":
                ph = "%s"
            else:
                ph = "?"

            set_clause = ", ".join([f"{k} = {ph}" for k in updates.keys()])
            values: list[Any] = list(updates.values()) + [player_id]  # type: ignore[assignment]
            query = f"UPDATE players SET {set_clause} WHERE player_id = {ph}"
            cursor.execute(query, tuple(values))
            self.connection.commit()  # type: ignore[attr-defined]

    def sync_players_from_match(self, match_data: dict[str, Any]) -> None:
        """
        Extract all player details from a match API response and insert/update them in the players table.
        """
        from typing import List, Dict, Any, cast
        for team_key in ['team1', 'team2', 'teams']:
            team = match_data.get(team_key)
            if team is None:
                continue
            if isinstance(team, dict):
                teams: List[Dict[str, Any]] = [cast(Dict[str, Any], team)]
            elif isinstance(team, list):
                teams = [cast(Dict[str, Any], t) for t in team if isinstance(t, dict)] # type: ignore
            else:
                continue
            for t in teams:  # type: ignore
                team_id = int(t.get('id', 0)) if 'id' in t else 0
                # Handle team API response structure
                players = t.get('player')
                if not isinstance(players, list):
                    continue
                for p in players:  # type: ignore
                    if not isinstance(p, dict):
                        continue
                    # Skip role header entries (e.g., 'BATSMEN', 'BOWLER', etc.)
                    if 'id' not in p:
                        continue
                    player_name = str(p.get('name', ''))  # type: ignore
                    country = ""
                    role = ""
                    batting_style = str(p.get('battingStyle', ''))  # type: ignore
                    bowling_style = str(p.get('bowlingStyle', ''))  # type: ignore
                    #meta = str(p.get('imageId', ''))  # Store imageId as meta
                    if player_name:
                        query = (
                            "SELECT player_id FROM players WHERE player_name = %s"
                            if getattr(self, "db_type", "sqlite") == "mysql"
                            else "SELECT player_id FROM players WHERE player_name = ?"
                        )
                        params: tuple[str, ...] = (player_name,)
                        existing = self.execute_query(query, params)
                        if not existing.empty:
                            pid_value = existing.iloc[0]['player_id']  # type: ignore[index]
                            player_id_val: int = int(pid_value) if pid_value is not None else 0
                            self.update_player(
                                player_id_val,
                                country=str(country),
                                role=str(role),
                                batting_style=str(batting_style),
                                bowling_style=str(bowling_style)
                            )
                        else:
                            self.insert_player(team_id, player_name, country, role, batting_style, bowling_style)

    def delete_player(self, player_id: int) -> None:
        """Delete a player"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("DELETE FROM players WHERE player_id = ?", (player_id,))  # type: ignore[attr-defined]
        self.connection.commit()  # type: ignore[attr-defined]

    def get_players(self) -> pd.DataFrame:
        """Fetch all players"""
        query = "SELECT * FROM players"
        return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

    def get_player_by_id(self, player_id: int) -> Dict[str, Any] | None:
        """Get a specific player"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))  # type: ignore[attr-defined]
        row = cursor.fetchone()  # type: ignore[attr-defined]
        return dict(row) if row else None

    def insert_match(
        self,
        match_description: str,
        team1: str,
        team2: str,
        match_format: str,
        venue_id: int,
        match_date: str,
    ) -> int:
        """Insert a new match"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        cursor.execute(
            """
            INSERT INTO matches 
            (match_description, team1, team2, match_format, venue_id, match_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (match_description, team1, team2, match_format, venue_id, match_date),
        )
        self.connection.commit()  # type: ignore[attr-defined]
        return cursor.lastrowid or 0  # type: ignore[attr-defined]

    def get_matches(self) -> pd.DataFrame:
        """Fetch all matches"""
        query = """
        SELECT m.*, v.venue_name, v.city, v.country 
        FROM matches m 
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        ORDER BY m.match_date DESC
        """
        return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

    def insert_venue(
        self, venue_name: str, city: str, country: str, capacity: int
    ) -> int:
        """Insert a new venue"""
        cursor = self.connection.cursor()  # type: ignore[attr-defined]
        cursor.execute(
            """
            INSERT INTO venues (venue_name, city, country, capacity)
            VALUES (?, ?, ?, ?)
            """,
            (venue_name, city, country, capacity),
        )
        self.connection.commit()  # type: ignore[attr-defined]
        return cursor.lastrowid or 0  # type: ignore[attr-defined]

    def get_venues(self) -> pd.DataFrame:
        """Fetch all venues"""
        query = "SELECT * FROM venues ORDER BY capacity DESC"
        return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

    def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:
        """Execute a custom SQL query and return results as DataFrame"""
        try:
            if params:
                return pd.read_sql(query, self.connection, params=params)  # type: ignore[call-arg]
            return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
        except Exception as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()

    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()


# Top-level MySQL-backed connection that implements same interface as DatabaseConnection
class MySQLDatabaseConnection(DatabaseConnection):
    def __init__(self, secrets: Dict[str, Any]):
        # Do not call super() init to avoid sqlite setup
        self.db_type = "mysql"
        self.db_path = "mysql"
        self.secrets = secrets
        # mypy/pylance: secrets values are dynamic; cast to known types
        host = cast(str, secrets.get("host", "localhost"))
        user = cast(str, secrets.get("user"))
        password = cast(str, secrets.get("password"))
        database = cast(str, secrets.get("dbname") or secrets.get("database"))
        try:
            port = int(secrets.get("port", 3306))
        except Exception:
            port = 3306

        # Use SQLAlchemy engine for proper pandas.read_sql() support (if available)
        try:
            if sqlalchemy:
                # Properly escape special characters in password
                from urllib.parse import quote_plus
                escaped_password = quote_plus(password)
                connection_string = f"mysql+pymysql://{user}:{escaped_password}@{host}:{port}/{database}?charset=utf8mb4"
                self.connection = create_engine(connection_string)  # type: ignore[attr-defined]
            else:
                # Fallback to raw pymysql if SQLAlchemy not available
                assert pymysql is not None
                self.connection = pymysql.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port,
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                )
        except Exception:
            # Fallback to raw pymysql if anything fails
            assert pymysql is not None
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )

    def init_schema(self) -> None:  # type: ignore[override]
        # Use the mysql_sync helper if available to create tables for MySQL
        if create_mysql_schema is not None:
            try:
                create_mysql_schema(self.secrets)
            except Exception:
                # If table creation fails, continue — individual operations will report errors
                pass

    def get_players(self) -> pd.DataFrame:  # type: ignore[override]
        try:
            return pd.read_sql("SELECT * FROM players ORDER BY total_runs DESC", self.connection)  # type: ignore[call-arg]
        except Exception:
            return pd.DataFrame()

    def insert_player(self, player_name: str, country: str, role: str, batting_style: str, bowling_style: str) -> int:  # type: ignore[override]
        """Insert player using MySQL-backed connection (handles SQLAlchemy engine or raw pymysql)."""
        # Raw pymysql connection path
        if hasattr(self.connection, 'cursor') and not hasattr(self.connection, 'engine'):
            cur = self.connection.cursor()  # type: ignore[attr-defined]
            # Inspect players table columns to handle schema differences
            try:
                cur.execute("SHOW COLUMNS FROM players")
                # fetchall() may return a sequence of dicts (DictCursor) or
                # sequences/tuples (regular cursor). Provide precise local
                # typing so static checkers understand the types here.
                raw_cols = cast(Sequence[Any] | None, cur.fetchall())
                # normalize to a sequence so static type-checkers can reason about it
                cols_info: Sequence[Any] = list(raw_cols) if raw_cols else []
                # rows may be tuple or dict depending on cursorclass
                cols: set[str] = set()
                for r in cols_info:
                    try:
                        # r can be a dict-like mapping or a sequence/tuple
                        if isinstance(r, dict):
                            r_map = cast(Mapping[str, Any], r)
                            # try common field name keys returned by different cursor types
                            for key in ("Field", "field", "COLUMN_NAME", "column_name", "Column_name"):
                                if key in r_map and r_map[key] is not None:
                                    cols.add(str(r_map[key]))
                                    break
                            else:
                                # fallback to first non-None value in the dict
                                for v in r_map.values():
                                    if v is not None:
                                        cols.add(str(v))
                                        break
                        else:
                            # tuple/list response: first element is typically the column name
                            seq = cast(Sequence[Any], r)
                            if len(seq) > 0:
                                cols.add(str(seq[0]))
                    except Exception:
                        # ignore malformed rows
                        continue
            except Exception:
                cols = set()

            insert_cols = []
            params = []

            if 'player_name' in cols or not cols:
                insert_cols.append('player_name')
                params.append(player_name)
            if 'country' in cols or not cols:
                insert_cols.append('country')
                params.append(country)
            if 'role' in cols or not cols:
                insert_cols.append('role')
                params.append(role)
            # If table has explicit batting/bowling style columns, insert them
            if 'batting_style' in cols:
                insert_cols.append('batting_style')
                params.append(batting_style)
            if 'bowling_style' in cols:
                insert_cols.append('bowling_style')
                params.append(bowling_style)

            # If there's a `meta` JSON column, store styles there as fallback
            if 'meta' in cols and ('batting_style' not in cols and 'bowling_style' not in cols):
                insert_cols.append('meta')
                try:
                    params.append(json.dumps({'batting_style': batting_style, 'bowling_style': bowling_style}))
                except Exception:
                    params.append('{}')

            if not insert_cols:
                # fallback to basic insert
                insert_cols = ['player_name', 'country', 'role']
                params = [player_name, country, role]

            placeholders = ', '.join(['%s'] * len(insert_cols))
            cols_sql = ', '.join(insert_cols)
            sql = f"INSERT INTO players ({cols_sql}) VALUES ({placeholders})"

            # Debug: print SQL and params before executing
            try:
                print('[db.mysql] raw pymysql path: executing SQL:', sql)
                print('[db.mysql] params:', tuple(params))
                print('[db.mysql] param types:', tuple(type(p) for p in params))
            except Exception:
                pass

            cur.execute(sql, tuple(params))
            try:
                self.connection.commit()  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                return int(cur.lastrowid)  # type: ignore[attr-defined]
            except Exception:
                return 0

        # SQLAlchemy engine path
        try:
            # type: ignore[reportMissingImports]
            from sqlalchemy import text
        except Exception:
            text = None  # type: ignore

        if text is not None:
            stmt = text(
                "INSERT INTO players (player_name, country, role, batting_style, bowling_style)"
                " VALUES (:player_name, :country, :role, :batting_style, :bowling_style)"
            )
            params = {
                "player_name": player_name,
                "country": country,
                "role": role,
                "batting_style": batting_style,
                "bowling_style": bowling_style,
            }
            try:
                with self.connection.begin() as conn:  # type: ignore[attr-defined]
                    conn.execute(stmt, params)
                    # MySQL: fetch last insert id
                    res = conn.execute(text("SELECT LAST_INSERT_ID() as id"))
                    row = res.fetchone()
                    if row:
                        return int(row[0] if len(row) > 0 else row["id"])  # type: ignore[index]
            except Exception:
                pass

        # Fallback: unable to determine ID
        return 0

    def get_matches(self) -> pd.DataFrame:  # type: ignore[override]
        try:
            query = "SELECT * FROM matches ORDER BY start_date DESC"
            return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
        except Exception:
            return pd.DataFrame()

    def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:  # type: ignore[override]
        try:
            # Check if it's a raw pymysql connection (has cursor method)
            if hasattr(self.connection, 'cursor') and not hasattr(self.connection, 'engine'):
                return fetch_data_from_pymysql(query, self.connection)
            else:
                # SQLAlchemy engine
                if params:
                    return pd.read_sql(query, self.connection, params=params)  # type: ignore[call-arg]
                return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
        except Exception as e:
            try:
                st.error(f"MySQL query error: {e}")
            except Exception:
                pass
            return pd.DataFrame()


def get_db_connection() -> DatabaseConnection:
    """Return a DatabaseConnection instance.

    Try to connect to MySQL using (in order):
    1. Streamlit secrets (if available)
    2. Hardcoded credentials (from demo1.py)
    3. Fall back to local SQLite file
    """
    # Safely read secrets at call time (avoids referencing undefined globals at import)
    mysql_secrets: Dict[str, Any] | None = None
    try:
        secrets = getattr(st, "secrets", None)
        # Prefer Mapping check so type-checkers understand .get
        if isinstance(secrets, Mapping):
            mapping = cast(Mapping[str, Any], secrets)
            # use mapping.get with an explicit cast so type-checkers see a concrete Mapping
            val = mapping.get("mysql")
            if val:
                mysql_secrets = cast(Dict[str, Any], val)
        else:
            # Fallback: if secrets provides a callable `get`, use it safely
            getter = getattr(secrets, "get", None)
            if callable(getter):
                val = getter("mysql")
                if val:
                    mysql_secrets = cast(Dict[str, Any], val)
    except Exception:
        mysql_secrets = None

    # If no secrets, use hardcoded credentials from demo1.py
    if mysql_secrets is None:
        mysql_secrets = {
            "host": "localhost",
            "user": "root",
            "password": "Vasu@76652",
            "database": "cricketdb",
            "port": 3306,
        }

    if mysql_secrets:
        # Ensure pymysql is available
        if pymysql is None:
            try:
                st.warning("pymysql is not installed; falling back to SQLite database")
            except Exception:
                pass
        else:
            try:
                conn = MySQLDatabaseConnection(mysql_secrets)
                # Initialize schema (creates tables if helper present)
                conn.init_schema()
                return conn
            except Exception as e:
                try:
                    st.error(f"Unable to connect to MySQL: {e}")
                except Exception:
                    pass

    # Fallback to local SQLite
    db = DatabaseConnection(db_type="sqlite", db_path="cricbuzz.db")
    db.init_schema()
    return db
