# # """
# # Player Statistics Page - Comprehensive Cricket Player Analytics
# # Displays all player data available in MySQL database including batting, bowling, partnerships, and format-specific stats.
# # """

# # # pyright: reportUnknownMemberType=false
# # import streamlit as st
# # import pandas as pd
# # from typing import Any, cast
# # #import pymysql

# # # Cast Streamlit to Any to avoid Pylance diagnostics
# # st = cast(Any, st)

# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # from utils.db_connection import get_db_connection, fetch_data_from_pymysql


# # def _safe_read_sql(query: str, conn: Any) -> pd.DataFrame:
# #     """Wrapper to safely read SQL from any connection type"""
# #     # Check if it's a raw pymysql connection
# #     if hasattr(conn, 'cursor') and not hasattr(conn, 'engine'):
# #         return fetch_data_from_pymysql(query, conn)
# #     else:
# #         # SQLAlchemy or other connection
# #         try:
# #             return pd.read_sql(query, conn)  # type: ignore
# #         except Exception as e:
# #             st.error(f"Error reading data: {str(e)[:100]}")
# #             return pd.DataFrame()


# # def show():
# #     """Display player statistics page with all MySQL data"""
# #     st.markdown("<h1 class='page-title'>📊 Player Statistics</h1>", unsafe_allow_html=True)

# #     db = get_db_connection()
# #     db = cast(Any, db)
# #     conn = db.connection

# #     # Tab structure
# #     tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(
# #         ["🗂️ All Players (Raw)", "🏏 All Batsmen", "🎯 All Bowlers", "🔀 Format Breakdown", "👥 Partnerships", "📈 Consistent Players"]
# #     )

# #     # ==================== TAB 0: ALL PLAYERS (RAW TABLE) ====================
# #     with tab0:
# #         st.markdown("## 🗂️ All Players (Raw Table)")
# #         try:
# #             from utils.db_connection import DatabaseConnection
# #             db_raw = DatabaseConnection()
# #             players_df = db_raw.get_players()
# #             st.dataframe(players_df, use_container_width=True, hide_index=True)
# #             st.info(f"Total players in database: {len(players_df)}")
# #         except Exception as e:
# #             st.error(f"Error loading players table: {str(e)[:100]}")
# #     # ==================== TAB 1: ALL BATSMEN ====================
# #     with tab1:
# #         st.markdown("## 🏏 All Batsmen Statistics")
        
# #         col1, col2, col3 = st.columns(3)
# #         with col1:
# #             sort_batsmen = st.selectbox(
# #                 "Sort Batsmen By",
# #                 ["Total Runs", "Batting Average", "Strike Rate", "Innings Played"],
# #                 key="batsmen_sort"
# #             )
# #         with col2:
# #             limit_batsmen = st.slider("Show Top N Batsmen", 5, 100, 20, key="batsmen_limit")
# #         with col3:
# #             search_batsman = st.text_input("Search Player Name", "", key="search_batsman")

# #         try:
# #             # Query batting_agg table for comprehensive batting stats
# #             query = "SELECT player_id, player_name, runs_scored, innings_played, batting_average, strike_rate FROM batting_agg ORDER BY"
            
# #             if sort_batsmen == "Total Runs":
# #                 query += " runs_scored DESC"
# #             elif sort_batsmen == "Batting Average":
# #                 query += " batting_average DESC"
# #             elif sort_batsmen == "Strike Rate":
# #                 query += " strike_rate DESC"
# #             else:
# #                 query += " innings_played DESC"
            
# #             query += f" LIMIT {limit_batsmen * 2}"  # Get extra rows for filtering
            
# #             batsmen_df = _safe_read_sql(query, conn)
            
# #             # Filter by search if provided
# #             if search_batsman:
# #                 batsmen_df = batsmen_df[batsmen_df['player_name'].str.contains(search_batsman, case=False, na=False)]
            
# #             batsmen_df = batsmen_df.head(limit_batsmen).reset_index(drop=True)
# #             batsmen_df['Rank'] = range(1, len(batsmen_df) + 1)
            
# #             # Rename columns for display
# #             batsmen_display = batsmen_df[['Rank', 'player_name', 'runs_scored', 'innings_played', 'batting_average', 'strike_rate']].copy()
# #             batsmen_display.columns = ['Rank', 'Player', 'Total Runs', 'Innings', 'Avg', 'SR']
            
# #             st.dataframe(batsmen_display, use_container_width=True, hide_index=True)
# #             st.info(f"📊 Total records in database: {len(_safe_read_sql('SELECT COUNT(*) as cnt FROM batting_agg', conn))}")
            
# #         except Exception as e:
# #             st.error(f"Error loading batsmen stats: {str(e)[:100]}")

# #     # ==================== TAB 2: ALL BOWLERS ====================
# #     with tab2:
# #         st.markdown("## 🎯 All Bowlers Statistics")
        
# #         col1, col2, col3 = st.columns(3)
# #         with col1:
# #             sort_bowlers = st.selectbox(
# #                 "Sort Bowlers By",
# #                 ["Wickets Taken", "Bowling Average", "Economy Rate"],
# #                 key="bowlers_sort"
# #             )
# #         with col2:
# #             limit_bowlers = st.slider("Show Top N Bowlers", 5, 100, 20, key="bowlers_limit")
# #         with col3:
# #             search_bowler = st.text_input("Search Bowler Name", "", key="search_bowler")

# #         try:
# #             # Query bowling_agg table
# #             query = "SELECT player_id, player_name, wickets_taken, bowling_average, economy_rate FROM bowling_agg ORDER BY"
            
# #             if sort_bowlers == "Wickets Taken":
# #                 query += " wickets_taken DESC"
# #             elif sort_bowlers == "Bowling Average":
# #                 query += " bowling_average ASC"
# #             else:
# #                 query += " economy_rate ASC"
            
# #             query += f" LIMIT {limit_bowlers * 2}"
            
# #             bowlers_df = _safe_read_sql(query, conn)
            
# #             # Filter by search if provided
# #             if search_bowler:
# #                 bowlers_df = bowlers_df[bowlers_df['player_name'].str.contains(search_bowler, case=False, na=False)]
            
# #             bowlers_df = bowlers_df.head(limit_bowlers).reset_index(drop=True)
# #             bowlers_df['Rank'] = range(1, len(bowlers_df) + 1)
            
# #             # Rename columns for display
# #             bowlers_display = bowlers_df[['Rank', 'player_name', 'wickets_taken', 'bowling_average', 'economy_rate']].copy()
# #             bowlers_display.columns = ['Rank', 'Player', 'Wickets', 'Average', 'Economy']
            
# #             st.dataframe(bowlers_display, use_container_width=True, hide_index=True)
# #             st.info(f"📊 Total records in database: {len(_safe_read_sql('SELECT COUNT(*) as cnt FROM bowling_agg', conn))}")
            
# #         except Exception as e:
# #             st.error(f"Error loading bowlers stats: {str(e)[:100]}")

# #     # ==================== TAB 3: FORMAT BREAKDOWN ====================
# #     with tab3:
# #         st.markdown("## 🔀 Player Performance by Format (2025)")
        
# #         format_choice = st.radio(
# #             "Select Format",
# #             ["Test", "ODI", "T20I"],
# #             horizontal=True,
# #             key="format_choice"
# #         )
        
# #         stat_type = st.radio(
# #             "Stat Type",
# #             ["Batting", "Bowling"],
# #             horizontal=True,
# #             key="format_stat_type"
# #         )
        
# #         try:
# #             if stat_type == "Batting":
# #                 query = f"""
# #                     SELECT player_id, player_name, match_format, runs_scored, innings_played, 
# #                            batting_average, strike_rate 
# #                     FROM batting_agg_format_2025 
# #                     WHERE match_format = '{format_choice}'
# #                     ORDER BY runs_scored DESC LIMIT 30
# #                 """
# #                 df = _safe_read_sql(query, conn)
# #                 df['Rank'] = range(1, len(df) + 1)
# #                 display_df = df[['Rank', 'player_name', 'runs_scored', 'innings_played', 'batting_average', 'strike_rate']].copy()
# #                 display_df.columns = ['Rank', 'Player', 'Runs', 'Innings', 'Avg', 'SR']
# #             else:
# #                 query = f"""
# #                     SELECT player_id, player_name, match_format, wickets_taken, matches_played,
# #                            bowling_average, economy_rate
# #                     FROM bowling_agg_format_2025
# #                     WHERE match_format = '{format_choice}'
# #                     ORDER BY wickets_taken DESC LIMIT 30
# #                 """
# #                 df = _safe_read_sql(query, conn)
# #                 df['Rank'] = range(1, len(df) + 1)
# #                 display_df = df[['Rank', 'player_name', 'wickets_taken', 'bowling_average', 'economy_rate']].copy()
# #                 display_df.columns = ['Rank', 'Player', 'Wickets', 'Avg', 'Economy']
            
# #             st.dataframe(display_df, use_container_width=True, hide_index=True)
# #             st.success(f"Total {stat_type.lower()} records in {format_choice}: {len(df)}")
            
# #         except Exception as e:
# #             st.error(f"Error loading format breakdown: {str(e)[:100]}")

# #     # ==================== TAB 4: PARTNERSHIPS ====================
# #     with tab4:
# #         st.markdown("## 👥 Best Batting Partnerships (2025)")
        
# #         limit_partnerships = st.slider("Show Top N Partnerships", 5, 100, 20, key="partnerships_limit")
        
# #         try:
# #             query = f"""
# #                 SELECT partnership_pair, total_partnerships, avg_partnership_runs, 
# #                        highest_partnership, fifty_plus_partnerships, success_rate
# #                 FROM best_batting_partnerships_2025
# #                 ORDER BY avg_partnership_runs DESC LIMIT {limit_partnerships}
# #             """
# #             partnerships_df = _safe_read_sql(query, conn)
# #             partnerships_df['Rank'] = range(1, len(partnerships_df) + 1)
            
# #             display_df = partnerships_df[['Rank', 'partnership_pair', 'total_partnerships', 
# #                                            'avg_partnership_runs', 'highest_partnership', 
# #                                            'fifty_plus_partnerships', 'success_rate']].copy()
# #             display_df.columns = ['Rank', 'Partnership', 'Partnerships', 'Avg Runs', 'Highest', '50+ Runs', 'Success %']
            
# #             st.dataframe(display_df, use_container_width=True, hide_index=True)
            
# #         except Exception as e:
# #             st.error(f"Error loading partnerships: {str(e)[:100]}")

# #     # ==================== TAB 5: CONSISTENT PERFORMERS ====================
# #     with tab5:
# #         st.markdown("## 📈 Most Consistent Batsmen (Low Standard Deviation)")
        
# #         limit_consistent = st.slider("Show Top N Consistent Players", 5, 100, 20, key="consistent_limit")
        
# #         try:
# #             # Use batting_agg with calculation fallback if consistent_batsmen view doesn't exist
# #             query = f"""
# #                 SELECT player_name, innings_played, AVG(runs_scored) as avg_runs
# #                 FROM batting_agg
# #                 GROUP BY player_name, innings_played
# #                 ORDER BY innings_played DESC LIMIT {limit_consistent}
# #             """
# #             consistent_df = _safe_read_sql(query, conn)
# #             consistent_df['Rank'] = range(1, len(consistent_df) + 1)
            
# #             display_df = consistent_df[['Rank', 'player_name', 'innings_played', 'avg_runs']].copy()
# #             display_df.columns = ['Rank', 'Player', 'Innings', 'Avg Runs']
            
# #             st.dataframe(display_df, use_container_width=True, hide_index=True)
# #             st.info("Showing players with most innings played")
            
# #         except Exception as e:
# #             st.error(f"Error loading consistent batsmen: {str(e)[:100]}")

# #     # ==================== ADDITIONAL INSIGHTS ====================
# #     st.markdown("---")
# #     st.markdown("## 📋 Database Summary")
    
# #     try:
# #         col1, col2, col3, col4 = st.columns(4)
        
# #         with col1:
# #             batting_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM batting_agg", conn).iloc[0, 0]
# #             st.metric("Total Batsmen", f"{batting_count:,}")
        
# #         with col2:
# #             bowling_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM bowling_agg", conn).iloc[0, 0]
# #             st.metric("Total Bowlers", f"{bowling_count:,}")
        
# #         with col3:
# #             partnership_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM best_batting_partnerships_2025", conn).iloc[0, 0]
# #             st.metric("Partnerships", f"{partnership_count:,}")
        
# #         with col4:
# #             try:
# #                 format_2025_count = _safe_read_sql("SELECT COUNT(*) as cnt FROM batting_agg_format_2025", conn).iloc[0, 0]
# #                 st.metric("2025 Format Stats", f"{format_2025_count:,}")
# #             except:
# #                 st.metric("2025 Format Stats", "N/A")
        
# #     except Exception as e:
# #         st.warning(f"Could not load summary metrics: {str(e)[:80]}")


# """
# Player Statistics Page - MySQL Database Analytics
# """

# import streamlit as st
# import pandas as pd
# from typing import Any, cast
# import pymysql

# st = cast(Any, st)


# def show():
#     """Display player statistics from MySQL database"""
#     st.markdown("<h1 class='page-title'>📊 Player Statistics (MySQL Data)</h1>", unsafe_allow_html=True)

#     # MySQL connection
#     mysql_secrets = {
#         "host": "localhost",
#         "user": "root",
#         "password": "Vasu@76652",
#         "database": "cricketdb",
#         "port": 3306,
#     }

#     try:
#         conn = pymysql.connect(
#             host=mysql_secrets["host"],
#             user=mysql_secrets["user"],
#             password=mysql_secrets["password"],
#             database=mysql_secrets["database"],
#             port=mysql_secrets["port"],
#             cursorclass=pymysql.cursors.DictCursor
#         )
        
#         # Tab structure
#         tab0, tab1, tab2, tab3 = st.tabs(
#             ["🗂️ All Players", "🏏 Top Batsmen", "🎯 Top Bowlers", "📊 Summary"]
#         )

#         # TAB 0: ALL PLAYERS
#         with tab0:
#             st.markdown("## 🗂️ All Players Database")
#             try:
#                 query = "SELECT * FROM players ORDER BY player_name LIMIT 200"
#                 players_df = pd.read_sql(query, conn)
                
#                 if not players_df.empty:
#                     st.dataframe(players_df, use_container_width=True, hide_index=True)
#                     st.info(f"Total players in database: {len(players_df)}")
#                 else:
#                     st.warning("No players found in database")
#             except Exception as e:
#                 st.error(f"Error loading players: {str(e)}")

#         # TAB 1: TOP BATSMEN
#         with tab1:
#             st.markdown("## 🏏 Top Batsmen from Matches")
            
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 sort_batsmen = st.selectbox(
#                     "Sort By",
#                     ["Total Runs", "Average Runs", "Strike Rate", "Innings"],
#                     key="batsmen_sort"
#                 )
#             with col2:
#                 limit_batsmen = st.slider("Show Top N", 5, 50, 20, key="batsmen_limit")
#             with col3:
#                 search_batsman = st.text_input("Search Player", "", key="search_batsman")

#             try:
#                 query = """
#                     SELECT 
#                         player_name,
#                         COUNT(*) as innings_played,
#                         SUM(runs) as total_runs,
#                         AVG(runs) as avg_runs,
#                         AVG(strike_rate) as avg_strike_rate,
#                         SUM(fours) as total_fours,
#                         SUM(sixes) as total_sixes,
#                         MAX(runs) as highest_score
#                     FROM batting_stats
#                     GROUP BY player_name
#                 """
                
#                 if sort_batsmen == "Total Runs":
#                     query += " ORDER BY total_runs DESC"
#                 elif sort_batsmen == "Average Runs":
#                     query += " ORDER BY avg_runs DESC"
#                 elif sort_batsmen == "Strike Rate":
#                     query += " ORDER BY avg_strike_rate DESC"
#                 else:
#                     query += " ORDER BY innings_played DESC"
                
#                 query += f" LIMIT {limit_batsmen * 2}"
                
#                 batsmen_df = pd.read_sql(query, conn)
                
#                 if search_batsman:
#                     batsmen_df = batsmen_df[batsmen_df['player_name'].str.contains(search_batsman, case=False, na=False)]
                
#                 batsmen_df = batsmen_df.head(limit_batsmen).reset_index(drop=True)
#                 batsmen_df['Rank'] = range(1, len(batsmen_df) + 1)
                
#                 # Format numeric columns
#                 batsmen_df['avg_runs'] = batsmen_df['avg_runs'].round(2)
#                 batsmen_df['avg_strike_rate'] = batsmen_df['avg_strike_rate'].round(2)
                
#                 # Reorder columns
#                 display_df = batsmen_df[[
#                     'Rank', 'player_name', 'total_runs', 'innings_played', 
#                     'avg_runs', 'avg_strike_rate', 'total_fours', 'total_sixes', 'highest_score'
#                 ]]
#                 display_df.columns = ['Rank', 'Player', 'Total Runs', 'Innings', 'Avg', 'SR', '4s', '6s', 'High Score']
                
#                 st.dataframe(display_df, use_container_width=True, hide_index=True)
#                 st.success(f"📊 Showing {len(display_df)} players from batting_stats table")
                
#             except Exception as e:
#                 st.error(f"Error loading batsmen stats: {str(e)}")

#         # TAB 2: TOP BOWLERS
#         with tab2:
#             st.markdown("## 🎯 Top Bowlers from Matches")
            
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 sort_bowlers = st.selectbox(
#                     "Sort By",
#                     ["Wickets", "Economy", "Matches"],
#                     key="bowlers_sort"
#                 )
#             with col2:
#                 limit_bowlers = st.slider("Show Top N", 5, 50, 20, key="bowlers_limit")
#             with col3:
#                 search_bowler = st.text_input("Search Bowler", "", key="search_bowler")

#             try:
#                 query = """
#                     SELECT 
#                         player_name,
#                         COUNT(*) as matches,
#                         SUM(wickets) as total_wickets,
#                         AVG(economy) as avg_economy,
#                         SUM(overs) as total_overs,
#                         SUM(maidens) as total_maidens,
#                         AVG(wickets) as avg_wickets_per_match
#                     FROM bowling_stats
#                     WHERE wickets > 0
#                     GROUP BY player_name
#                 """
                
#                 if sort_bowlers == "Wickets":
#                     query += " ORDER BY total_wickets DESC"
#                 elif sort_bowlers == "Economy":
#                     query += " ORDER BY avg_economy ASC"
#                 else:
#                     query += " ORDER BY matches DESC"
                
#                 query += f" LIMIT {limit_bowlers * 2}"
                
#                 bowlers_df = pd.read_sql(query, conn)
                
#                 if search_bowler:
#                     bowlers_df = bowlers_df[bowlers_df['player_name'].str.contains(search_bowler, case=False, na=False)]
                
#                 bowlers_df = bowlers_df.head(limit_bowlers).reset_index(drop=True)
#                 bowlers_df['Rank'] = range(1, len(bowlers_df) + 1)
                
#                 # Format numeric columns
#                 bowlers_df['avg_economy'] = bowlers_df['avg_economy'].round(2)
#                 bowlers_df['avg_wickets_per_match'] = bowlers_df['avg_wickets_per_match'].round(2)
#                 bowlers_df['total_overs'] = bowlers_df['total_overs'].round(1)
                
#                 display_df = bowlers_df[[
#                     'Rank', 'player_name', 'total_wickets', 'matches', 
#                     'avg_economy', 'total_overs', 'total_maidens', 'avg_wickets_per_match'
#                 ]]
#                 display_df.columns = ['Rank', 'Player', 'Wickets', 'Matches', 'Econ', 'Overs', 'Maidens', 'Avg W/M']
                
#                 st.dataframe(display_df, use_container_width=True, hide_index=True)
#                 st.success(f"📊 Showing {len(display_df)} bowlers from bowling_stats table")
                
#             except Exception as e:
#                 st.error(f"Error loading bowlers stats: {str(e)}")

#         # TAB 3: SUMMARY
#         with tab3:
#             st.markdown("## 📊 Database Summary")
            
#             try:
#                 col1, col2, col3, col4 = st.columns(4)
                
#                 with col1:
#                     count_query = "SELECT COUNT(*) as cnt FROM players"
#                     result = pd.read_sql(count_query, conn)
#                     st.metric("Total Players", f"{result.iloc[0]['cnt']:,}")
                
#                 with col2:
#                     count_query = "SELECT COUNT(*) as cnt FROM matches"
#                     result = pd.read_sql(count_query, conn)
#                     st.metric("Total Matches", f"{result.iloc[0]['cnt']:,}")
                
#                 with col3:
#                     count_query = "SELECT COUNT(*) as cnt FROM batting_stats"
#                     result = pd.read_sql(count_query, conn)
#                     st.metric("Batting Records", f"{result.iloc[0]['cnt']:,}")
                
#                 with col4:
#                     count_query = "SELECT COUNT(*) as cnt FROM bowling_stats"
#                     result = pd.read_sql(count_query, conn)
#                     st.metric("Bowling Records", f"{result.iloc[0]['cnt']:,}")
                
#                 st.markdown("---")
#                 st.markdown("### 🏆 Top Performers")
                
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.markdown("**🏏 Top 5 Run Scorers**")
#                     query = """
#                         SELECT 
#                             player_name as Player,
#                             SUM(runs) as 'Total Runs'
#                         FROM batting_stats
#                         GROUP BY player_name
#                         ORDER BY SUM(runs) DESC
#                         LIMIT 5
#                     """
#                     top_batsmen = pd.read_sql(query, conn)
#                     st.dataframe(top_batsmen, use_container_width=True, hide_index=True)
                
#                 with col2:
#                     st.markdown("**🎯 Top 5 Wicket Takers**")
#                     query = """
#                         SELECT 
#                             player_name as Player,
#                             SUM(wickets) as 'Total Wickets'
#                         FROM bowling_stats
#                         WHERE wickets > 0
#                         GROUP BY player_name
#                         ORDER BY SUM(wickets) DESC
#                         LIMIT 5
#                     """
#                     top_bowlers = pd.read_sql(query, conn)
#                     st.dataframe(top_bowlers, use_container_width=True, hide_index=True)
                
#                 st.markdown("---")
#                 st.markdown("### 📈 Recent Activity")
                
#                 query = """
#                     SELECT 
#                         series_name as Series,
#                         COUNT(*) as Matches,
#                         MAX(start_date) as 'Last Match'
#                     FROM matches
#                     WHERE series_name IS NOT NULL
#                     GROUP BY series_name
#                     ORDER BY MAX(start_date) DESC
#                     LIMIT 10
#                 """
#                 recent_series = pd.read_sql(query, conn)
#                 st.dataframe(recent_series, use_container_width=True, hide_index=True)
                
#             except Exception as e:
#                 st.error(f"Error loading summary: {str(e)}")

#         conn.close()
        
#     except Exception as e:
#         st.error(f"❌ MySQL Connection Error: {str(e)}")
#         st.info("""
#         **Troubleshooting:**
#         1. Ensure MySQL server is running
#         2. Verify credentials in mysql_secrets
#         3. Check that 'cricketdb' database exists
#         4. Ensure tables are created (run Live Matches sync first)
#         """)

"""
Player Statistics Page - MySQL Database Analytics (FIXED VERSION)
Fixes:
1. Removed duplicate headers in All Players tab
2. Fixed "Expected numeric dtype" error in Top Batsmen
3. Added proper error handling
4. Improved data display formatting
"""

import streamlit as st
import pandas as pd
from typing import Any, cast
import pymysql
import json

st = cast(Any, st)


def show():
    """Display player statistics from MySQL database"""
    st.markdown("<h1 class='page-title'>📊 Player Statistics (MySQL Data)</h1>", unsafe_allow_html=True)

    # MySQL connection
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }

    try:
        conn = pymysql.connect(
            host=mysql_secrets["host"],
            user=mysql_secrets["user"],
            password=mysql_secrets["password"],
            database=mysql_secrets["database"],
            port=mysql_secrets["port"],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Tab structure
        tab0, tab1, tab2, tab3 = st.tabs(
            ["🗂️ All Players", "🏏 Top Batsmen", "🎯 Top Bowlers", "📊 Summary"]
        )

        # ==================== TAB 0: ALL PLAYERS (FIXED) ====================
        with tab0:
            st.markdown("## 🗂️ All Players Database")
            try:
                query = """
                    SELECT 
                        id,
                        external_player_id,
                        player_name,
                        date_of_birth,
                        country,
                        role,
                        meta,
                        created_at
                    FROM players 
                    ORDER BY player_name 
                    LIMIT 200
                """
                players_df = pd.read_sql(query, conn)
                
                if not players_df.empty:
                    # Parse meta JSON for better display
                    def parse_meta(meta_str):
                        try:
                            if meta_str:
                                meta = json.loads(meta_str)
                                batting = meta.get('batting_style', 'N/A')
                                bowling = meta.get('bowling_style', 'N/A')
                                return f"Bat: {batting}, Bowl: {bowling}"
                            return 'N/A'
                        except:
                            return 'N/A'
                    
                    players_df['playing_style'] = players_df['meta'].apply(parse_meta)
                    
                    # Format date columns
                    if 'date_of_birth' in players_df.columns:
                        players_df['date_of_birth'] = pd.to_datetime(
                            players_df['date_of_birth'], errors='coerce'
                        ).dt.strftime('%Y-%m-%d')
                        players_df['date_of_birth'] = players_df['date_of_birth'].fillna('N/A')
                    
                    if 'created_at' in players_df.columns:
                        players_df['created_at'] = pd.to_datetime(
                            players_df['created_at'], errors='coerce'
                        ).dt.strftime('%Y-%m-%d %H:%M')
                        players_df['created_at'] = players_df['created_at'].fillna('N/A')
                    
                    # Select and rename columns for display
                    display_df = players_df[[
                        'id', 'external_player_id', 'player_name', 
                        'date_of_birth', 'country', 'role', 
                        'playing_style', 'created_at'
                    ]].copy()
                    
                    display_df.columns = [
                        'ID', 'External ID', 'Player Name', 
                        'DOB', 'Country', 'Role', 
                        'Playing Style', 'Created At'
                    ]
                    
                    # FIX: Use hide_index=True to prevent duplicate headers
                    st.dataframe(
                        display_df, 
                        use_container_width=True, 
                        hide_index=True,  # This prevents duplicate headers!
                        height=600
                    )
                    st.info(f"Total players in database: {len(players_df)}")
                else:
                    st.warning("No players found in database")
            except Exception as e:
                st.error(f"Error loading players: {str(e)}")

        # ==================== TAB 1: TOP BATSMEN (FIXED) ====================
        with tab1:
            st.markdown("## 🏏 Top Batsmen from Matches")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_batsmen = st.selectbox(
                    "Sort By",
                    ["Total Runs", "Average Runs", "Strike Rate", "Innings"],
                    key="batsmen_sort"
                )
            with col2:
                limit_batsmen = st.slider("Show Top N", 5, 50, 20, key="batsmen_limit")
            with col3:
                search_batsman = st.text_input("Search Player", "", key="search_batsman")

            try:
                # FIX: Use CAST to ensure numeric types in SQL query
                query = """
                    SELECT 
                        player_name,
                        COUNT(*) as innings_played,
                        CAST(SUM(runs) AS SIGNED) as total_runs,
                        CAST(AVG(runs) AS DECIMAL(10,2)) as avg_runs,
                        CAST(AVG(strike_rate) AS DECIMAL(10,2)) as avg_strike_rate,
                        CAST(SUM(fours) AS SIGNED) as total_fours,
                        CAST(SUM(sixes) AS SIGNED) as total_sixes,
                        CAST(MAX(runs) AS SIGNED) as highest_score
                    FROM batting_stats
                    GROUP BY player_name
                """
                
                if sort_batsmen == "Total Runs":
                    query += " ORDER BY total_runs DESC"
                elif sort_batsmen == "Average Runs":
                    query += " ORDER BY avg_runs DESC"
                elif sort_batsmen == "Strike Rate":
                    query += " ORDER BY avg_strike_rate DESC"
                else:
                    query += " ORDER BY innings_played DESC"
                
                query += f" LIMIT {limit_batsmen * 2}"
                
                batsmen_df = pd.read_sql(query, conn)
                
                # FIX: Ensure all numeric columns are properly typed
                numeric_columns = [
                    'innings_played', 'total_runs', 'avg_runs', 
                    'avg_strike_rate', 'total_fours', 'total_sixes', 'highest_score'
                ]
                for col in numeric_columns:
                    if col in batsmen_df.columns:
                        batsmen_df[col] = pd.to_numeric(batsmen_df[col], errors='coerce').fillna(0)
                
                # Search filter
                if search_batsman:
                    batsmen_df = batsmen_df[
                        batsmen_df['player_name'].str.contains(search_batsman, case=False, na=False)
                    ]
                
                batsmen_df = batsmen_df.head(limit_batsmen).reset_index(drop=True)
                batsmen_df['Rank'] = range(1, len(batsmen_df) + 1)
                
                # Format numeric columns
                batsmen_df['avg_runs'] = batsmen_df['avg_runs'].round(2)
                batsmen_df['avg_strike_rate'] = batsmen_df['avg_strike_rate'].round(2)
                
                # Reorder columns
                display_df = batsmen_df[[
                    'Rank', 'player_name', 'total_runs', 'innings_played', 
                    'avg_runs', 'avg_strike_rate', 'total_fours', 'total_sixes', 'highest_score'
                ]].copy()
                
                display_df.columns = [
                    'Rank', 'Player', 'Total Runs', 'Innings', 
                    'Avg', 'SR', '4s', '6s', 'High Score'
                ]
                
                # Display with proper formatting
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                st.success(f"📊 Showing {len(display_df)} players from batting_stats table")
                
            except Exception as e:
                st.error(f"Error loading batsmen stats: {str(e)}")
                # Show debug info
                with st.expander("Debug Information"):
                    st.code(str(e))

        # ==================== TAB 2: TOP BOWLERS (FIXED) ====================
        with tab2:
            st.markdown("## 🎯 Top Bowlers from Matches")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_bowlers = st.selectbox(
                    "Sort By",
                    ["Wickets", "Economy", "Matches"],
                    key="bowlers_sort"
                )
            with col2:
                limit_bowlers = st.slider("Show Top N", 5, 50, 20, key="bowlers_limit")
            with col3:
                search_bowler = st.text_input("Search Bowler", "", key="search_bowler")

            try:
                # FIX: Use CAST for numeric types
                query = """
                    SELECT 
                        player_name,
                        COUNT(*) as matches,
                        CAST(SUM(wickets) AS SIGNED) as total_wickets,
                        CAST(AVG(economy) AS DECIMAL(10,2)) as avg_economy,
                        CAST(SUM(overs) AS DECIMAL(10,1)) as total_overs,
                        CAST(SUM(maidens) AS SIGNED) as total_maidens,
                        CAST(AVG(wickets) AS DECIMAL(10,2)) as avg_wickets_per_match
                    FROM bowling_stats
                    WHERE wickets > 0
                    GROUP BY player_name
                """
                
                if sort_bowlers == "Wickets":
                    query += " ORDER BY total_wickets DESC"
                elif sort_bowlers == "Economy":
                    query += " ORDER BY avg_economy ASC"
                else:
                    query += " ORDER BY matches DESC"
                
                query += f" LIMIT {limit_bowlers * 2}"
                
                bowlers_df = pd.read_sql(query, conn)
                
                # FIX: Ensure numeric types
                numeric_columns = [
                    'matches', 'total_wickets', 'avg_economy', 
                    'total_overs', 'total_maidens', 'avg_wickets_per_match'
                ]
                for col in numeric_columns:
                    if col in bowlers_df.columns:
                        bowlers_df[col] = pd.to_numeric(bowlers_df[col], errors='coerce').fillna(0)
                
                if search_bowler:
                    bowlers_df = bowlers_df[
                        bowlers_df['player_name'].str.contains(search_bowler, case=False, na=False)
                    ]
                
                bowlers_df = bowlers_df.head(limit_bowlers).reset_index(drop=True)
                bowlers_df['Rank'] = range(1, len(bowlers_df) + 1)
                
                # Format numeric columns
                bowlers_df['avg_economy'] = bowlers_df['avg_economy'].round(2)
                bowlers_df['avg_wickets_per_match'] = bowlers_df['avg_wickets_per_match'].round(2)
                bowlers_df['total_overs'] = bowlers_df['total_overs'].round(1)
                
                display_df = bowlers_df[[
                    'Rank', 'player_name', 'total_wickets', 'matches', 
                    'avg_economy', 'total_overs', 'total_maidens', 'avg_wickets_per_match'
                ]].copy()
                
                display_df.columns = [
                    'Rank', 'Player', 'Wickets', 'Matches', 
                    'Econ', 'Overs', 'Maidens', 'Avg W/M'
                ]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                st.success(f"📊 Showing {len(display_df)} bowlers from bowling_stats table")
                
            except Exception as e:
                st.error(f"Error loading bowlers stats: {str(e)}")

        # ==================== TAB 3: SUMMARY ====================
        with tab3:
            st.markdown("## 📊 Database Summary")
            
            try:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    count_query = "SELECT COUNT(*) as cnt FROM players"
                    result = pd.read_sql(count_query, conn)
                    st.metric("Total Players", f"{result.iloc[0]['cnt']:,}")
                
                with col2:
                    count_query = "SELECT COUNT(*) as cnt FROM matches"
                    result = pd.read_sql(count_query, conn)
                    st.metric("Total Matches", f"{result.iloc[0]['cnt']:,}")
                
                with col3:
                    count_query = "SELECT COUNT(*) as cnt FROM batting_stats"
                    result = pd.read_sql(count_query, conn)
                    st.metric("Batting Records", f"{result.iloc[0]['cnt']:,}")
                
                with col4:
                    count_query = "SELECT COUNT(*) as cnt FROM bowling_stats"
                    result = pd.read_sql(count_query, conn)
                    st.metric("Bowling Records", f"{result.iloc[0]['cnt']:,}")
                
                st.markdown("---")
                st.markdown("### 🏆 Top Performers")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏏 Top 5 Run Scorers**")
                    query = """
                        SELECT 
                            player_name as Player,
                            CAST(SUM(runs) AS SIGNED) as 'Total Runs'
                        FROM batting_stats
                        GROUP BY player_name
                        ORDER BY SUM(runs) DESC
                        LIMIT 5
                    """
                    top_batsmen = pd.read_sql(query, conn)
                    st.dataframe(top_batsmen, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("**🎯 Top 5 Wicket Takers**")
                    query = """
                        SELECT 
                            player_name as Player,
                            CAST(SUM(wickets) AS SIGNED) as 'Total Wickets'
                        FROM bowling_stats
                        WHERE wickets > 0
                        GROUP BY player_name
                        ORDER BY SUM(wickets) DESC
                        LIMIT 5
                    """
                    top_bowlers = pd.read_sql(query, conn)
                    st.dataframe(top_bowlers, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### 📈 Recent Activity")
                
                query = """
                    SELECT 
                        series_name as Series,
                        COUNT(*) as Matches,
                        MAX(start_date) as 'Last Match'
                    FROM matches
                    WHERE series_name IS NOT NULL
                    GROUP BY series_name
                    ORDER BY MAX(start_date) DESC
                    LIMIT 10
                """
                recent_series = pd.read_sql(query, conn)
                st.dataframe(recent_series, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Error loading summary: {str(e)}")

        conn.close()
        
    except Exception as e:
        st.error(f"❌ MySQL Connection Error: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Ensure MySQL server is running
        2. Verify credentials in mysql_secrets
        3. Check that 'cricketdb' database exists
        4. Ensure tables are created (run Live Matches sync first)
        """)