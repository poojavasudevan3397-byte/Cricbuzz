"""
Live Matches Page - Real-time Match Updates
"""

import streamlit as st
from typing import Any, cast

# Help Pylance by treating Streamlit as Any for dynamic members (markdown, columns, etc.)
st = cast(Any, st)
import pandas as pd
from typing import Any, Dict, List, cast
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import get_api_client, normalize_matches
from utils.mysql_sync import upsert_match, upsert_batting, upsert_bowling, create_mysql_schema


def show():
    """Display live matches page"""
    st.markdown("<h1 class='page-title'>⚡ Real-Time Match Updates</h1>", unsafe_allow_html=True)

    # API Configuration
    api_key = st.secrets.get("RAPIDAPI_KEY", "5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863")

    # Match Type Selection
    col1, col2 = st.columns(2)
    with col1:
        match_type = st.radio(
            "Select Match Type",
            ["Live", "Upcoming", "Recent"],
            horizontal=True,
            key="match_type_radio"
        )
        # Match Category (All / International / Domestic / Women)
        match_category = st.selectbox(
            "Match Category",
            ["All", "International", "Domestic", "Women"],
            index=0,
            key="match_category_select"
        )

    # Initialize session state
    if "matches_cache" not in st.session_state:
        st.session_state.matches_cache = {}
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = {}

    # Auto-refresh settings
    with col2:
        _refresh_interval = st.selectbox(
            "Auto-refresh",
            ["Manual", "30 seconds", "1 minute", "5 minutes"],
            index=0,
            key="refresh_select"
        )
        # Toggle to automatically send fetched matches to MySQL
        st.session_state.setdefault("auto_send_mysql", False)
        auto_send = st.checkbox(
            "Auto-send matches to MySQL",
            value=st.session_state.get("auto_send_mysql", False),
            key="auto_send_mysql_checkbox",
        )
        st.session_state["auto_send_mysql"] = auto_send

        # If enabled, optionally include fetching scorecards for each match (may be many API calls)
        st.session_state.setdefault("auto_send_scorecards", False)
        include_scorecards = st.checkbox(
            "Include scorecards (may cause many API calls)",
            value=st.session_state.get("auto_send_scorecards", False),
            key="auto_send_scorecards_checkbox",
        )
        st.session_state["auto_send_scorecards"] = include_scorecards

    # Fetch matches based on type
    api_client = get_api_client(api_key)

    matches_data = {}
    try:
        with st.spinner(f"Fetching {match_type} matches..."):
            if match_type == "Live":
                matches_data = api_client.get_live_matches()
            elif match_type == "Upcoming":
                matches_data = api_client.get_upcoming_matches()
            else:
                matches_data = api_client.get_recent_matches()

        matches: List[Dict[str, Any]] = normalize_matches(matches_data)

        # If user enabled auto-send, create schema and upsert matches (and optionally scorecards)
        if st.session_state.get("auto_send_mysql", False):
            mysql_secrets: Dict[str, Any] = {
                "host": "localhost",
                "user": "root",
                "password": "Vasu@76652",
                "database": "cricketdb",
                "port": 3306,
            }
            try:
                # ensure tables exist
                create_mysql_schema(mysql_secrets)
            except Exception as e:
                st.warning(f"Could not create MySQL schema: {e}")

            # Upsert each match; optionally fetch and save scorecards (may cause many API calls)
            for m in matches:
                try:
                    print(f"DEBUG: Processing match {m.get('matchId', m.get('match_id'))}")
                    upsert_match(mysql_secrets, m)
                    print(f"DEBUG: upsert_match succeeded")
                    # --- Auto-sync players for each match (to MySQL database) ---
                    new_players_count = 0
                    for team_key in ["team1_id", "team2_id"]:
                        team_id = m.get(team_key)
                        if team_id:
                            import requests
                            url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
                            headers = {
                                "x-rapidapi-key": "7d43f4bd53msh4abaa77fb5edf80p14c624jsn6982e9f7e18b",
                                "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
                            }
                            try:
                                resp = requests.get(url, headers=headers)
                                team_data = resp.json()
                                print(f"DEBUG: Got team {team_id} data, keys: {list(team_data.keys()) if isinstance(team_data, dict) else 'N/A'}")
                                # Insert players to MySQL database directly
                                import pymysql
                                conn = pymysql.connect(
                                    host=mysql_secrets['host'],
                                    user=mysql_secrets['user'],
                                    password=mysql_secrets['password'],
                                    database=mysql_secrets['database'],
                                    port=mysql_secrets['port']
                                )
                                cursor = conn.cursor()
                                players = team_data.get('player', [])
                                print(f"DEBUG: Found {len(players) if isinstance(players, list) else '?'} players for team {team_id}")
                                if isinstance(players, list):
                                    for p in players:  # type: ignore
                                        if isinstance(p, dict) and 'id' in p and 'name' in p:
                                            external_player_id = str(p.get('id', ''))  # type: ignore
                                            player_name = str(p.get('name', ''))  # type: ignore
                                            country = ''
                                            role = ''
                                            batting_style = str(p.get('battingStyle', ''))  # type: ignore
                                            bowling_style = str(p.get('bowlingStyle', ''))  # type: ignore
                                            image_id = str(p.get('imageId', ''))  # type: ignore
                                            
                                            # Store batting and bowling styles in meta JSON
                                            import json
                                            meta = json.dumps({
                                                "batting_style": batting_style,
                                                "bowling_style": bowling_style,
                                                "image_id": image_id
                                            })
                                            
                                            try:
                                                cursor.execute(
                                                    "INSERT IGNORE INTO players (external_player_id, player_name, country, role, meta) VALUES (%s, %s, %s, %s, %s)",
                                                    (external_player_id, player_name, country, role, meta)
                                                )
                                                new_players_count += cursor.rowcount
                                                print(f"Inserted: {player_name}")
                                            except Exception as insert_err:
                                                print(f"Error inserting {player_name}: {insert_err}")
                                conn.commit()
                                cursor.close()
                                conn.close()
                            except Exception as e:
                                st.warning(f"Could not sync players for team {team_id}: {e}")
                    if new_players_count > 0:
                        st.success(f"✅ {new_players_count} new player(s) inserted into MySQL database for match {m.get('matchId', '')}.")
                    # --- End player sync ---
                    if st.session_state.get("auto_send_scorecards", False):
                        # Only attempt scorecards for matches with an id
                        mid = m.get("matchId") or m.get("match_id")
                        if mid:
                            try:
                                sc = api_client.get_scorecard(str(mid))
                                if sc:
                                    for inning in sc.get("scorecard", []):
                                        innings_id = inning.get("inningsId") or inning.get("inningsid") or ""
                                        if innings_id:
                                            bats = inning.get("batsman", inning.get("batsmen", []))
                                            if bats:
                                                upsert_batting(mysql_secrets, str(mid), str(innings_id), bats)
                                            bowls = inning.get("bowler", inning.get("bowlers", []))
                                            if bowls:
                                                upsert_bowling(mysql_secrets, str(mid), str(innings_id), bowls)
                            except Exception as e:
                                # Log error but continue with next match
                                import traceback
                                print(f"ERROR fetching scorecard for match {mid}: {e}")
                                traceback.print_exc()
                except Exception as e:
                    # Log DB errors instead of silently swallowing them
                    import traceback
                    error_msg = f"ERROR processing match {m.get('matchId', m.get('match_id'))}: {str(e)[:200]}"
                    print(error_msg)
                    traceback.print_exc()
                    st.error(f"⚠️ {error_msg}")

        # Apply match category filter (All, International, Domestic, Women)
        try:
            if match_category and match_category.lower() != "all":
                sel = match_category.lower()

                def _cat_ok(m: Dict[str, Any]) -> bool:
                    mt = str(m.get("matchType", "")).lower()
                    if sel == "women":
                        return "women" in mt
                    if sel == "international":
                        return "international" in mt
                    if sel == "domestic":
                        return "domestic" in mt
                    return True

                matches = [m for m in matches if _cat_ok(m)]
        except Exception:
            # If any unexpected structure, leave matches as-is
            pass

        if not matches:
            st.info(f"No {match_type.lower()} matches available at the moment.")
            return

        # Group matches by series
        st.markdown("---")
        st.markdown(f"## {match_type} Matches by Series")

        series_dict: Dict[str, List[Dict[str, Any]]] = {}
        for match in matches:
            series_name = match.get("seriesName", "Unknown")
            if series_name not in series_dict:
                series_dict[series_name] = []
            series_dict[series_name].append(match)

        # Display each series
        for series_name, series_matches in series_dict.items():
            with st.expander(
                f"📊 {series_name} ({len(series_matches)} matches)",
                expanded=True
            ):
                for idx, match in enumerate(series_matches):
                    display_match_card(match, match_type, idx)
                    st.markdown("---")

        # Summary Table
        st.markdown("---")
        st.markdown("## Match Summary Table")

        summary_df = pd.DataFrame([
            {
                "Series": m.get("seriesName", "N/A"),
                "Team 1": m.get("team1_name", "N/A"),
                "Team 2": m.get("team2_name", "N/A"),
                "Format": m.get("matchFormat", "N/A"),
                "Status": m.get("status", "N/A"),
                "Venue": m.get("venue", "N/A"),
            }
            for m in matches
        ])

        # Use the newer Streamlit width argument
        try:
            st.dataframe(summary_df, width="stretch")  # type: ignore[call-arg]
        except Exception:
            # Fallback for older Streamlit
            st.dataframe(summary_df)  # type: ignore[call-arg]

    except Exception as e:
        st.error(f"Error fetching matches: {e}")


def display_match_card(match: Dict[str, Any], match_type: str, idx: int) -> None:
    """Display a single match card"""
    col1, col2 = st.columns((3, 1))

    with col1:
        # Match Header
        team1 = match.get("team1_name", "N/A")
        team2 = match.get("team2_name", "N/A")
        st.markdown(f"### {team1} vs {team2}")

        # Match Details
        col1_details, col2_details = st.columns(2)
        with col1_details:
            st.write(f"**Format**: {match.get('matchFormat', 'N/A')}")
            st.write(f"**Status**: {match.get('status', 'N/A')}")
            # Format timestamp if available
            start_date = match.get('startDate', 'N/A')
            if start_date != 'N/A' and str(start_date).isdigit():
                try:
                    # Convert milliseconds timestamp to datetime
                    date_obj = datetime.fromtimestamp(int(start_date) / 1000)
                    formatted_date = date_obj.strftime("%d %b %Y, %H:%M")
                    st.write(f"**Date**: {formatted_date}")
                except:
                    st.write(f"**Date**: {start_date}")
            else:
                st.write(f"**Date**: {start_date}")

        with col2_details:
            st.write((f"**Venue**: {match.get('venue', 'N/A')}"), (f"**City**: {match.get('city', 'N/A')}"))
            #st.write(f"**Country**: {match.get('country', 'N/A')}")

        # Score Information (for Live and Recent matches)
        if match_type in ["Live", "Recent"]:
            st.markdown("### Match Score")
            score_col1, score_col2 = st.columns(2)

            with score_col1:
                t1_runs = match.get("team1_score", "N/A")
                t1_wickets = match.get("team1_wickets", "N/A")
                t1_overs = match.get("team1_overs", "N/A")
                if str(t1_runs) != "N/A":
                    st.write(f"**{team1}**: {t1_runs}/{t1_wickets} ({t1_overs} ov)")
                else:
                    st.write(f"**{team1}**: Score not available")

            with score_col2:
                t2_runs = match.get("team2_score", "N/A")
                t2_wickets = match.get("team2_wickets", "N/A")
                t2_overs = match.get("team2_overs", "N/A")
                if str(t2_runs) != "N/A":
                    st.write(f"**{team2}**: {t2_runs}/{t2_wickets} ({t2_overs} ov)")
                else:
                    st.write(f"**{team2}**: Score not available")
            
            # Display scorecard button
            if st.button(
                "📋 View Scorecard",
                key=f"scard_{match.get('matchId')}_{idx}",
            ):
                st.session_state[f"show_scorecard_{idx}"] = True
            
            # Display scorecard only if button was clicked
            if st.session_state.get(f"show_scorecard_{idx}", False):
                display_scorecard(match)

        # Match Description
        if match.get("matchDesc"):
            st.info(f"📝 {match.get('matchDesc')}")

    with col2:
        pass


def display_scorecard(match: Dict[str, Any]) -> None:
    """Display full scorecard for a match"""
    st.markdown("---")
    st.markdown("### 📊 Full Scorecard")

    match_id = match.get("matchId")
    if not match_id:
        st.warning("Match ID not available")
        return

    try:
        api_key = st.secrets.get("RAPIDAPI_KEY", "5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863")
        api_client = get_api_client(api_key)

        with st.spinner("Loading scorecard..."):
            scorecard_data = api_client.get_scorecard(str(match_id))

        if not scorecard_data:
            st.warning("Unable to fetch scorecard")
            return

        # === Store match data in MySQL ===
        try:
            # Get MySQL secrets from db_connection (hardcoded by default)
            mysql_secrets: Dict[str, Any] = {
                "host": "localhost",
                "user": "root",
                "password": "Vasu@76652",
                "database": "cricketdb",
                "port": 3306,
            }
            # Step 1: Create all necessary tables in MySQL (idempotent - safe to call repeatedly)
            create_mysql_schema(mysql_secrets)
            # Step 2: Upsert match record
            upsert_match(mysql_secrets, match)
            # Step 3: Upsert batting and bowling data for each inning
            innings_list_for_db = scorecard_data.get("scorecard", [])
            for inning in innings_list_for_db:
                innings_id = inning.get("inningsId", "")
                if innings_id:
                    batsmen = inning.get("batsman", inning.get("batsmen", []))
                    if batsmen:
                        upsert_batting(mysql_secrets, str(match_id), str(innings_id), batsmen)
                    bowlers = inning.get("bowler", inning.get("bowlers", []))
                    if bowlers:
                        upsert_bowling(mysql_secrets, str(match_id), str(innings_id), bowlers)
            # --- Sync players for this match ---
            from utils.db_connection import DatabaseConnection
            db = DatabaseConnection()
            db.init_schema()
            for team_key in ["team1_id", "team2_id"]:
                team_id = match.get(team_key)
                if team_id:
                    import requests
                    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
                    headers = {
                        "x-rapidapi-key": "7d43f4bd53msh4abaa77fb5edf80p14c624jsn6982e9f7e18b",
                        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
                    }
                    try:
                        resp = requests.get(url, headers=headers)
                        team_data = resp.json()
                        db.sync_players_from_match({"teams": [team_data]})
                    except Exception as e:
                        st.warning(f"Could not sync players for team {team_id}: {e}")
            # --- End player sync ---
            st.success("✅ Match data saved to MySQL (tables: players, matches, series, venues, innings, batsmen, bowlers, players)")
        except Exception as e:
            # Log but don't block the UI
            st.warning(f"Note: Could not save to MySQL: {e}")

        # Display innings
        innings_list = scorecard_data.get("scorecard", [])
        if innings_list:
            for inning in innings_list:
                inning_desc = inning.get(
                    "inningDescription",
                    f"Innings {inning.get('inningsid', 'N/A')}"
                )
                st.markdown(f"#### {inning_desc}")

                # Batting Table (explicit typing to help static analyzers)
                batting_data: List[Dict[str, Any]] = []
                batsmen = inning.get("batsman", inning.get("batsmen", []))
                if batsmen:
                    for raw_batter in batsmen:
                        batter = cast(Dict[str, Any], raw_batter)

                        # compute SR defensively: try common keys and format if numeric
                        sr_raw = (
                            batter.get("strkrate")
                            or batter.get("sr")
                            or batter.get("strikerate")
                            or ""
                        )
                        if sr_raw is None or sr_raw == "":
                            sr = ""
                        else:
                            try:
                                sr = f"{float(sr_raw):.2f}"
                            except Exception:
                                sr = str(sr_raw)

                        # Dismissal chain (use provided preferred pattern) with wicketInfo guard
                        wicket_info = batter.get('wicketInfo')
                        wicket_dict = cast(Dict[str, Any], wicket_info) if isinstance(wicket_info, dict) else {}
                        dismissal = (
                            batter.get('outdec', '')
                            or batter.get('dismissalText', '')
                            or wicket_dict.get('dismissalText', 'not out')
                        )

                        batting_data.append({
                            "Batter": batter.get("name", ""),
                            "Runs": batter.get("runs", ""),
                            "Balls": batter.get("balls", ""),
                            "4s": batter.get("fours", ""),
                            "6s": batter.get("sixes", ""),
                            "SR": sr,
                            "Dismissal": dismissal,
                        })

                # extras may be a dict with totals, not an iterable of dicts; normalize defensively
                extras_any = inning.get('extras')
                extras: Dict[str, Any] = cast(Dict[str, Any], extras_any) if isinstance(extras_any, dict) else {}
                if extras:
                    batting_data.append({
                        'Batter': 'Extras',
                        'Runs': str(extras.get('total', 0)),
                        'Balls': '-',
                        '4s': '-',
                        '6s': '-',
                        'SR': '',
                        'Dismissal': f"w {extras.get('wides', 0)}, nb {extras.get('noballs', 0)}, b {extras.get('byes', 0)}, lb {extras.get('legbyes', 0)}"
                    })
                try:
                    st.dataframe(batting_data, width="stretch")  # type: ignore[call-arg]
                except Exception:
                    st.dataframe(batting_data)  # type: ignore[call-arg]

                # Bowling Table
                bowlers = inning.get("bowler", inning.get("bowlers", []))
                if bowlers:
                    st.markdown("**Bowling**")
                    bowling_rows = [
                        {
                            "Bowler": bw.get("name", ""),
                            "Overs": bw.get("overs", ""),
                            "Maidens": bw.get("maidens", ""),
                            "Runs": bw.get("runs", ""),
                            "Wickets": bw.get("wickets", ""),
                            "Economy": bw.get("economy", ""),
                        }
                        for bw in bowlers
                    ]
                    try:
                        st.dataframe(bowling_rows, width="stretch")  # type: ignore[call-arg]
                    except Exception:
                        st.dataframe(bowling_rows)  # type: ignore[call-arg]
        else:
            st.info("Detailed scorecard not available yet")

    except Exception as e:
        st.error(f"Error loading scorecard: {e}")
