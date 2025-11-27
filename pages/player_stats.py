"""
Player Statistics Page - Comprehensive Cricket Player Analytics
Displays all player data available in MySQL database including batting, bowling, partnerships, and format-specific stats.
"""

# pyright: reportUnknownMemberType=false
import streamlit as st
import pandas as pd
from typing import Any, cast
#import pymysql

# Cast Streamlit to Any to avoid Pylance diagnostics
st = cast(Any, st)

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import get_db_connection, fetch_data_from_pymysql


def _safe_read_sql(query: str, conn: Any) -> pd.DataFrame:
    """Wrapper to safely read SQL from any connection type"""
    # Check if it's a raw pymysql connection
    if hasattr(conn, 'cursor') and not hasattr(conn, 'engine'):
        return fetch_data_from_pymysql(query, conn)
    else:
        # SQLAlchemy or other connection
        try:
            return pd.read_sql(query, conn)  # type: ignore
        except Exception as e:
            st.error(f"Error reading data: {str(e)[:100]}")
            return pd.DataFrame()


def show():
    """Display player statistics page with all MySQL data"""
    st.markdown("<h1 class='page-title'>📊 Player Statistics</h1>", unsafe_allow_html=True)

    db = get_db_connection()
    db = cast(Any, db)
    conn = db.connection

    # Tab structure
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🗂️ All Players (Raw)", "🏏 All Batsmen", "🎯 All Bowlers", "🔀 Format Breakdown", "👥 Partnerships", "📈 Consistent Players"]
    )

    # ==================== TAB 0: ALL PLAYERS (RAW TABLE) ====================
    with tab0:
        st.markdown("## 🗂️ All Players (Raw Table)")
        try:
            from utils.db_connection import DatabaseConnection
            db_raw = DatabaseConnection()
            players_df = db_raw.get_players()
            st.dataframe(players_df, use_container_width=True, hide_index=True)
            st.info(f"Total players in database: {len(players_df)}")
        except Exception as e:
            st.error(f"Error loading players table: {str(e)[:100]}")
    # ==================== TAB 1: ALL BATSMEN ====================
    with tab1:
        st.markdown("## 🏏 All Batsmen Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_batsmen = st.selectbox(
                "Sort Batsmen By",
                ["Total Runs", "Batting Average", "Strike Rate", "Innings Played"],
                key="batsmen_sort"
            )
        with col2:
            limit_batsmen = st.slider("Show Top N Batsmen", 5, 100, 20, key="batsmen_limit")
        with col3:
            search_batsman = st.text_input("Search Player Name", "", key="search_batsman")

        try:
            # Query batting_agg table for comprehensive batting stats
            query = "SELECT player_id, player_name, runs_scored, innings_played, batting_average, strike_rate FROM batting_agg ORDER BY"
            
            if sort_batsmen == "Total Runs":
                query += " runs_scored DESC"
            elif sort_batsmen == "Batting Average":
                query += " batting_average DESC"
            elif sort_batsmen == "Strike Rate":
                query += " strike_rate DESC"
            else:
                query += " innings_played DESC"
            
            query += f" LIMIT {limit_batsmen * 2}"  # Get extra rows for filtering
            
            batsmen_df = _safe_read_sql(query, conn)
            
            # Filter by search if provided
            if search_batsman:
                batsmen_df = batsmen_df[batsmen_df['player_name'].str.contains(search_batsman, case=False, na=False)]
            
            batsmen_df = batsmen_df.head(limit_batsmen).reset_index(drop=True)
            batsmen_df['Rank'] = range(1, len(batsmen_df) + 1)
            
            # Rename columns for display
            batsmen_display = batsmen_df[['Rank', 'player_name', 'runs_scored', 'innings_played', 'batting_average', 'strike_rate']].copy()
            batsmen_display.columns = ['Rank', 'Player', 'Total Runs', 'Innings', 'Avg', 'SR']
            
            st.dataframe(batsmen_display, use_container_width=True, hide_index=True)
            st.info(f"📊 Total records in database: {len(_safe_read_sql('SELECT COUNT(*) as cnt FROM batting_agg', conn))}")
            
        except Exception as e:
            st.error(f"Error loading batsmen stats: {str(e)[:100]}")

    # ==================== TAB 2: ALL BOWLERS ====================
    with tab2:
        st.markdown("## 🎯 All Bowlers Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_bowlers = st.selectbox(
                "Sort Bowlers By",
                ["Wickets Taken", "Bowling Average", "Economy Rate"],
                key="bowlers_sort"
            )
        with col2:
            limit_bowlers = st.slider("Show Top N Bowlers", 5, 100, 20, key="bowlers_limit")
        with col3:
            search_bowler = st.text_input("Search Bowler Name", "", key="search_bowler")

        try:
            # Query bowling_agg table
            query = "SELECT player_id, player_name, wickets_taken, bowling_average, economy_rate FROM bowling_agg ORDER BY"
            
            if sort_bowlers == "Wickets Taken":
                query += " wickets_taken DESC"
            elif sort_bowlers == "Bowling Average":
                query += " bowling_average ASC"
            else:
                query += " economy_rate ASC"
            
            query += f" LIMIT {limit_bowlers * 2}"
            
            bowlers_df = _safe_read_sql(query, conn)
            
            # Filter by search if provided
            if search_bowler:
                bowlers_df = bowlers_df[bowlers_df['player_name'].str.contains(search_bowler, case=False, na=False)]
            
            bowlers_df = bowlers_df.head(limit_bowlers).reset_index(drop=True)
            bowlers_df['Rank'] = range(1, len(bowlers_df) + 1)
            
            # Rename columns for display
            bowlers_display = bowlers_df[['Rank', 'player_name', 'wickets_taken', 'bowling_average', 'economy_rate']].copy()
            bowlers_display.columns = ['Rank', 'Player', 'Wickets', 'Average', 'Economy']
            
            st.dataframe(bowlers_display, use_container_width=True, hide_index=True)
            st.info(f"📊 Total records in database: {len(_safe_read_sql('SELECT COUNT(*) as cnt FROM bowling_agg', conn))}")
            
        except Exception as e:
            st.error(f"Error loading bowlers stats: {str(e)[:100]}")

    # ==================== TAB 3: FORMAT BREAKDOWN ====================
    with tab3:
        st.markdown("## 🔀 Player Performance by Format (2025)")
        
        format_choice = st.radio(
            "Select Format",
            ["Test", "ODI", "T20I"],
            horizontal=True,
            key="format_choice"
        )
        
        stat_type = st.radio(
            "Stat Type",
            ["Batting", "Bowling"],
            horizontal=True,
            key="format_stat_type"
        )
        
        try:
            if stat_type == "Batting":
                query = f"""
                    SELECT player_id, player_name, match_format, runs_scored, innings_played, 
                           batting_average, strike_rate 
                    FROM batting_agg_format_2025 
                    WHERE match_format = '{format_choice}'
                    ORDER BY runs_scored DESC LIMIT 30
                """
                df = _safe_read_sql(query, conn)
                df['Rank'] = range(1, len(df) + 1)
                display_df = df[['Rank', 'player_name', 'runs_scored', 'innings_played', 'batting_average', 'strike_rate']].copy()
                display_df.columns = ['Rank', 'Player', 'Runs', 'Innings', 'Avg', 'SR']
            else:
                query = f"""
                    SELECT player_id, player_name, match_format, wickets_taken, matches_played,
                           bowling_average, economy_rate
                    FROM bowling_agg_format_2025
                    WHERE match_format = '{format_choice}'
                    ORDER BY wickets_taken DESC LIMIT 30
                """
                df = _safe_read_sql(query, conn)
                df['Rank'] = range(1, len(df) + 1)
                display_df = df[['Rank', 'player_name', 'wickets_taken', 'bowling_average', 'economy_rate']].copy()
                display_df.columns = ['Rank', 'Player', 'Wickets', 'Avg', 'Economy']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.success(f"Total {stat_type.lower()} records in {format_choice}: {len(df)}")
            
        except Exception as e:
            st.error(f"Error loading format breakdown: {str(e)[:100]}")

    # ==================== TAB 4: PARTNERSHIPS ====================
    with tab4:
        st.markdown("## 👥 Best Batting Partnerships (2025)")
        
        limit_partnerships = st.slider("Show Top N Partnerships", 5, 100, 20, key="partnerships_limit")
        
        try:
            query = f"""
                SELECT partnership_pair, total_partnerships, avg_partnership_runs, 
                       highest_partnership, fifty_plus_partnerships, success_rate
                FROM best_batting_partnerships_2025
                ORDER BY avg_partnership_runs DESC LIMIT {limit_partnerships}
            """
            partnerships_df = _safe_read_sql(query, conn)
            partnerships_df['Rank'] = range(1, len(partnerships_df) + 1)
            
            display_df = partnerships_df[['Rank', 'partnership_pair', 'total_partnerships', 
                                           'avg_partnership_runs', 'highest_partnership', 
                                           'fifty_plus_partnerships', 'success_rate']].copy()
            display_df.columns = ['Rank', 'Partnership', 'Partnerships', 'Avg Runs', 'Highest', '50+ Runs', 'Success %']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Error loading partnerships: {str(e)[:100]}")

    # ==================== TAB 5: CONSISTENT PERFORMERS ====================
    with tab5:
        st.markdown("## 📈 Most Consistent Batsmen (Low Standard Deviation)")
        
        limit_consistent = st.slider("Show Top N Consistent Players", 5, 100, 20, key="consistent_limit")
        
        try:
            # Use batting_agg with calculation fallback if consistent_batsmen view doesn't exist
            query = f"""
                SELECT player_name, innings_played, AVG(runs_scored) as avg_runs
                FROM batting_agg
                GROUP BY player_name, innings_played
                ORDER BY innings_played DESC LIMIT {limit_consistent}
            """
            consistent_df = _safe_read_sql(query, conn)
            consistent_df['Rank'] = range(1, len(consistent_df) + 1)
            
            display_df = consistent_df[['Rank', 'player_name', 'innings_played', 'avg_runs']].copy()
            display_df.columns = ['Rank', 'Player', 'Innings', 'Avg Runs']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.info("Showing players with most innings played")
            
        except Exception as e:
            st.error(f"Error loading consistent batsmen: {str(e)[:100]}")

    # ==================== ADDITIONAL INSIGHTS ====================
    st.markdown("---")
    st.markdown("## 📋 Database Summary")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            batting_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM batting_agg", conn).iloc[0, 0]
            st.metric("Total Batsmen", f"{batting_count:,}")
        
        with col2:
            bowling_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM bowling_agg", conn).iloc[0, 0]
            st.metric("Total Bowlers", f"{bowling_count:,}")
        
        with col3:
            partnership_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM best_batting_partnerships_2025", conn).iloc[0, 0]
            st.metric("Partnerships", f"{partnership_count:,}")
        
        with col4:
            try:
                format_2025_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM batting_agg_format_2025", conn).iloc[0, 0]
                st.metric("2025 Format Stats", f"{format_2025_count:,}")
            except:
                st.metric("2025 Format Stats", "N/A")
        
    except Exception as e:
        st.warning(f"Could not load summary metrics: {str(e)[:80]}")
