# # """
# # SQL Analytics Page - 25 SQL Practice Queries
# # """

# # import streamlit as st
# # import pandas as pd
# # from typing import Dict, Any, cast

# # # Optional SQLAlchemy/pymysql imports. Declare as Any and use targeted
# # # type-ignore on the imports so Pylance won't flag missing optional deps.
# # create_engine: Any = None
# # pymysql: Any = None
# # try:
# #     # type: ignore[reportMissingImports]
# #     from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
# #     import pymysql  # type: ignore[reportMissingImports]
# # except Exception:
# #     create_engine = None  # type: ignore
# #     pymysql = None  # type: ignore
# # # Help Pylance by treating Streamlit dynamic members (markdown, columns, etc.) as Any
# # st = cast(Any, st)
# # from typing import Dict
# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # from utils.db_connection import get_db_connection


# # def show():
# #     """Display SQL analytics page"""
# #     st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)

# #     st.markdown("""
# #     This section contains 25 SQL practice queries. Execute queries on your cricket
# #     database and view results below.
# #     """)

# #     _db = get_db_connection()  # type: ignore[unused-variable]
# #     _db = cast(Any, _db)

# #     # Define all 25 queries and show them (no difficulty filtering)
# #     level_queries: Dict[str, Dict[str, str]] = get_all_queries()  # type: ignore[assignment]

# #     # Query selection
# #     query_names = list(level_queries.keys())  # type: ignore[arg-type]
# #     selected_query = cast(str, st.selectbox(
# #         "Select a Query",
# #         query_names,
# #         key="query_select"
# #     ))

# #     if selected_query:
# #         query_info: Dict[str, str] = level_queries[selected_query]  # type: ignore[assignment]
        
# #         # Display query information
# #         st.markdown(f"## {selected_query}")
# #         st.markdown(f"**Description**: {query_info['description']}")  # type: ignore[index]
        
# #         with st.expander("View SQL Query", expanded=False):
# #             st.code(query_info['sql'], language='sql')  # type: ignore[index]

# #         # Execute Query Button
# #         col1, col2, _col3 = st.columns([1, 1, 2])
        
# #         with col1:
# #             if st.button("▶️ Execute Query", key="execute_btn"):
# #                 st.session_state.execute_query = True

# #         with col2:
# #             if st.button("📋 Copy Query", key="copy_btn"):
# #                 st.success("Query copied to clipboard!")

# #         # Display Results
# #         if st.session_state.get("execute_query", False):
# #             try:
# #                 st.markdown("---")
# #                 st.markdown("### Query Results")
                
# #                 # Execute the query against MySQL if secrets available, otherwise use mock/DB
# #                 results_df = pd.DataFrame()
# #                 mysql_secrets = None
# #                 try:
# #                     mysql_secrets = st.secrets.get("mysql")
# #                 except Exception:
# #                     mysql_secrets = None

# #                 if mysql_secrets and create_engine is not None:
# #                     try:
# #                         host = mysql_secrets.get("host", "localhost")
# #                         port = mysql_secrets.get("port", 3306)
# #                         user = mysql_secrets.get("user")
# #                         password = mysql_secrets.get("password")
# #                         dbname = mysql_secrets.get("dbname") or mysql_secrets.get("database")
# #                         if user and password and dbname:
# #                             engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}")
# #                             results_df = pd.read_sql(query_info['sql'], engine)  # type: ignore[call-arg]
# #                     except Exception as e:
# #                         st.error(f"Error executing query on MySQL: {e}")
# #                         results_df = pd.DataFrame()
# #                 else:
# #                     # Execute the query (mock execution for demo or using local DB)
# #                     results_df = execute_mock_query(selected_query, query_info)
                
# #                 if not results_df.empty:
# #                     st.dataframe(results_df, use_container_width=True)  # type: ignore[call-arg]
# #                     st.success(f"✓ Query executed successfully - {len(results_df)} rows returned")
                    
# #                     # Download option
# #                     csv = results_df.to_csv(index=False)
# #                     st.download_button(
# #                         label="📥 Download Results (CSV)",
# #                         data=csv,
# #                         file_name=f"{selected_query}.csv",
# #                         mime="text/csv"
# #                     )
# #                 else:
# #                     st.info("No results returned")
                    
# #             except Exception as e:
# #                 st.error(f"Query execution error: {e}")


# # def get_all_queries() -> Dict[str, Dict[str, str]]:
# #     """Get all 25 SQL queries with descriptions"""
# #     return {
# #         # Beginner Queries (1-8)
# #         "Query 1": {
# #             "description": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
# #             "sql": """
# #                 SELECT 
# #                     player_name,
# #                     role,
# #                     batting_style,
# #                     bowling_style
# #                 FROM players
# #                 WHERE country = 'India'
# #                 ORDER BY player_name;
# #             """
# #         },
        
# #         "Query 2": {
# #             "description": "Show all cricket matches that were played in the last few days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.",
# #             "sql": """
# #                 SELECT 
# #                     m.match_description,
# #                     m.team1,
# #                     m.team2,
# #                     v.venue_name,
# #                     v.city,
# #                     m.match_date
# #                 FROM matches m
# #                 LEFT JOIN venues v ON m.venue_id = v.venue_id
# #                 WHERE m.match_date >= DATE('now', '-7 days')
# #                 ORDER BY m.match_date DESC;
# #             """
# #         },
        
# #         "Query 3": {
# #             "description": "List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.",
# #             "sql": """
# #                 SELECT 
# #                     player_name,
# #                     total_runs,
# #                     batting_average,
# #                     (SELECT COUNT(*) FROM batsmen b 
# #                      WHERE b.player_id = p.player_id AND b.runs_scored >= 100) as centuries
# #                 FROM players p
# #                 WHERE 1=1
# #                 ORDER BY total_runs DESC
# #                 LIMIT 10;
# #             """
# #         },
        
# #         "Query 4": {
# #             "description": "Display all cricket venues that have a seating capacity of more than 30,000 spectators. Show venue name, city, country, and capacity. Order by largest capacity first.",
# #             "sql": """
# #                 SELECT 
# #                     venue_name,
# #                     city,
# #                     country,
# #                     capacity
# #                 FROM venues
# #                 WHERE capacity > 30000
# #                 ORDER BY capacity DESC;
# #             """
# #         },
        
# #         "Query 5": {
# #             "description": "Calculate how many matches each team has won. Show team name and total number of wins. Display teams with the most wins first.",
# #             "sql": """
# #                 SELECT 
# #                     winning_team,
# #                     COUNT(*) as matches_won
# #                 FROM matches
# #                 WHERE winning_team IS NOT NULL
# #                 GROUP BY winning_team
# #                 ORDER BY matches_won DESC;
# #             """
# #         },
        
# #         "Query 6": {
# #             "description": "Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players for each role.",
# #             "sql": """
# #                 SELECT 
# #                     role,
# #                     COUNT(*) as player_count
# #                 FROM players
# #                 WHERE role IS NOT NULL
# #                 GROUP BY role
# #                 ORDER BY player_count DESC;
# #             """
# #         },
        
# #         "Query 7": {
# #             "description": "Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I). Display the format and the highest score for that format.",
# #             "sql": """
# #                 SELECT 
# #                     m.match_format,
# #                     MAX(b.runs_scored) as highest_score
# #                 FROM batsmen b
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 GROUP BY m.match_format
# #                 ORDER BY highest_score DESC;
# #             """
# #         },
        
# #         "Query 8": {
# #             "description": "Show all cricket series that started in the year 2024. Include series name, host country, match type, start date, and total number of matches planned.",
# #             "sql": """
# #                 SELECT 
# #                     m.match_description,
# #                     m.team1,
# #                     m.team2,
# #                     COUNT(*) as matches_in_series
# #                 FROM matches m
# #                 WHERE strftime('%Y', m.match_date) = '2024'
# #                 GROUP BY m.match_description
# #                 ORDER BY m.match_date;
# #             """
# #         },

# #         # Intermediate Queries (9-16)
# #         "Query 9": {
# #             "description": "Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.",
# #             "sql": """
# #                 SELECT 
# #                     player_name,
# #                     total_runs,
# #                     total_wickets,
# #                     role
# #                 FROM players
# #                 WHERE total_runs > 1000 AND total_wickets > 50 AND role = 'All-rounder'
# #                 ORDER BY total_runs DESC;
# #             """
# #         },
        
# #         "Query 10": {
# #             "description": "Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.",
# #             "sql": """
# #                 SELECT 
# #                     m.match_description,
# #                     m.team1,
# #                     m.team2,
# #                     m.winning_team,
# #                     m.victory_margin,
# #                     m.victory_type,
# #                     v.venue_name,
# #                     m.match_date
# #                 FROM matches m
# #                 LEFT JOIN venues v ON m.venue_id = v.venue_id
# #                 WHERE m.winning_team IS NOT NULL
# #                 ORDER BY m.match_date DESC
# #                 LIMIT 20;
# #             """
# #         },
        
# #         "Query 11": {
# #             "description": "Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     COUNT(DISTINCT m.match_format) as format_count,
# #                     p.batting_average,
# #                     SUM(CASE WHEN m.match_format = 'Test' THEN b.runs_scored ELSE 0 END) as test_runs,
# #                     SUM(CASE WHEN m.match_format = 'ODI' THEN b.runs_scored ELSE 0 END) as odi_runs,
# #                     SUM(CASE WHEN m.match_format = 'T20I' THEN b.runs_scored ELSE 0 END) as t20i_runs
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 GROUP BY p.player_id, p.player_name
# #                 HAVING COUNT(DISTINCT m.match_format) >= 2
# #                 ORDER BY p.batting_average DESC;
# #             """
# #         },
        
# #         "Query 12": {
# #             "description": "Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.",
# #             "sql": """
# #                 SELECT 
# #                     winning_team,
# #                     v.country,
# #                     COUNT(*) as wins
# #                 FROM matches m
# #                 LEFT JOIN venues v ON m.venue_id = v.venue_id
# #                 WHERE m.winning_team IS NOT NULL
# #                 GROUP BY m.winning_team, v.country
# #                 ORDER BY winning_team, wins DESC;
# #             """
# #         },
        
# #         "Query 13": {
# #             "description": "Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.",
# #             "sql": """
# #                 SELECT 
# #                     b1.player_id as player1_id,
# #                     b2.player_id as player2_id,
# #                     (b1.runs_scored + b2.runs_scored) as partnership_runs,
# #                     b1.innings_id
# #                 FROM batsmen b1
# #                 JOIN batsmen b2 ON b1.innings_id = b2.innings_id 
# #                     AND b1.batting_position + 1 = b2.batting_position
# #                 WHERE (b1.runs_scored + b2.runs_scored) >= 100
# #                 ORDER BY partnership_runs DESC;
# #             """
# #         },
        
# #         "Query 14": {
# #             "description": "Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.",
# #             "sql": """
# #                 SELECT 
# #                     bw.player_id,
# #                     v.venue_name,
# #                     COUNT(DISTINCT m.match_id) as matches_at_venue,
# #                     AVG(bw.economy_rate) as avg_economy,
# #                     SUM(bw.wickets_taken) as total_wickets
# #                 FROM bowlers bw
# #                 JOIN innings i ON bw.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 JOIN venues v ON m.venue_id = v.venue_id
# #                 WHERE bw.overs_bowled >= 4
# #                 GROUP BY bw.player_id, v.venue_id
# #                 HAVING COUNT(DISTINCT m.match_id) >= 3
# #                 ORDER BY total_wickets DESC;
# #             """
# #         },
        
# #         "Query 15": {
# #             "description": "Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     COUNT(DISTINCT m.match_id) as close_matches,
# #                     AVG(b.runs_scored) as avg_runs,
# #                     SUM(CASE WHEN m.winning_team = i.batting_team THEN 1 ELSE 0 END) as matches_won
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 WHERE (CAST(m.victory_margin as INTEGER) < 50 OR CAST(m.victory_margin as INTEGER) < 5)
# #                 GROUP BY p.player_id, p.player_name
# #                 ORDER BY avg_runs DESC;
# #             """
# #         },
        
# #         "Query 16": {
# #             "description": "Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     strftime('%Y', m.match_date) as year,
# #                     COUNT(*) as matches,
# #                     AVG(b.runs_scored) as avg_runs,
# #                     AVG(b.strike_rate) as avg_strike_rate
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 WHERE strftime('%Y', m.match_date) >= '2020'
# #                 GROUP BY p.player_id, p.player_name, year
# #                 HAVING COUNT(*) >= 5
# #                 ORDER BY year DESC, avg_runs DESC;
# #             """
# #         },

# #         # Advanced Queries (17-25)
# #         "Query 17": {
# #             "description": "Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
# #             "sql": """
# #                 SELECT 
# #                     m.toss_decision,
# #                     COUNT(*) as total_matches,
# #                     SUM(CASE WHEN m.winning_team = m.toss_winner THEN 1 ELSE 0 END) as wins_by_toss_winner,
# #                     ROUND(100.0 * SUM(CASE WHEN m.winning_team = m.toss_winner THEN 1 ELSE 0 END) / COUNT(*), 2) as win_percentage
# #                 FROM matches m
# #                 WHERE m.toss_winner IS NOT NULL AND m.toss_decision IS NOT NULL
# #                 GROUP BY m.toss_decision
# #                 ORDER BY win_percentage DESC;
# #             """
# #         },
        
# #         "Query 18": {
# #             "description": "Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     COUNT(DISTINCT m.match_id) as matches,
# #                     AVG(bw.economy_rate) as avg_economy,
# #                     SUM(bw.wickets_taken) as total_wickets,
# #                     AVG(bw.overs_bowled) as avg_overs
# #                 FROM players p
# #                 JOIN bowlers bw ON p.player_id = bw.player_id
# #                 JOIN innings i ON bw.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 WHERE m.match_format IN ('ODI', 'T20I')
# #                 GROUP BY p.player_id, p.player_name
# #                 HAVING COUNT(DISTINCT m.match_id) >= 10 AND AVG(bw.overs_bowled) >= 2
# #                 ORDER BY avg_economy ASC;
# #             """
# #         },
        
# #         "Query 19": {
# #             "description": "Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     COUNT(*) as innings,
# #                     AVG(b.runs_scored) as avg_runs,
# #                     SQRT(AVG((b.runs_scored - (SELECT AVG(runs_scored) FROM batsmen b2 WHERE b2.player_id = p.player_id)) * 
# #                         (b.runs_scored - (SELECT AVG(runs_scored) FROM batsmen b2 WHERE b2.player_id = p.player_id)))) as std_dev
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 WHERE b.balls_faced >= 10 AND strftime('%Y', m.match_date) >= '2022'
# #                 GROUP BY p.player_id, p.player_name
# #                 ORDER BY std_dev ASC;
# #             """
# #         },
        
# #         "Query 20": {
# #             "description": "Analyze how many matches each player has played in different cricket formats and their batting average in each format. Show the count of Test matches, ODI matches, and T20 matches for each player, along with their respective batting averages. Only include players who have played at least 20 total matches across all formats.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     SUM(CASE WHEN m.match_format = 'Test' THEN 1 ELSE 0 END) as test_matches,
# #                     SUM(CASE WHEN m.match_format = 'ODI' THEN 1 ELSE 0 END) as odi_matches,
# #                     SUM(CASE WHEN m.match_format = 'T20I' THEN 1 ELSE 0 END) as t20i_matches,
# #                     COUNT(*) as total_matches,
# #                     AVG(CASE WHEN m.match_format = 'Test' THEN b.runs_scored ELSE NULL END) as test_avg,
# #                     AVG(CASE WHEN m.match_format = 'ODI' THEN b.runs_scored ELSE NULL END) as odi_avg,
# #                     AVG(CASE WHEN m.match_format = 'T20I' THEN b.runs_scored ELSE NULL END) as t20i_avg
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 GROUP BY p.player_id, p.player_name
# #                 HAVING COUNT(*) >= 20
# #                 ORDER BY total_matches DESC;
# #             """
# #         },
        
# #         "Query 21": {
# #             "description": "Create a comprehensive performance ranking system for players. Combine batting performance, bowling performance, and fielding performance into a single weighted score. Rank the top performers in each cricket format.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     (p.total_runs * 0.01) + (p.batting_average * 0.5) + (COALESCE((SELECT AVG(strike_rate) FROM batsmen WHERE player_id = p.player_id), 0) * 0.3) as batting_points,
# #                     (p.total_wickets * 2) + ((50 - p.bowling_average) * 0.5) as bowling_points,
# #                     ((p.total_runs * 0.01) + (p.batting_average * 0.5) + (COALESCE((SELECT AVG(strike_rate) FROM batsmen WHERE player_id = p.player_id), 0) * 0.3)) +
# #                     ((p.total_wickets * 2) + ((50 - p.bowling_average) * 0.5)) as total_points
# #                 FROM players p
# #                 WHERE p.total_runs > 0 OR p.total_wickets > 0
# #                 ORDER BY total_points DESC;
# #             """
# #         },
        
# #         "Query 22": {
# #             "description": "Build a head-to-head match prediction analysis between teams. For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate total matches played, wins for each team, and overall win percentage.",
# #             "sql": """
# #                 SELECT 
# #                     m1.team1 as team_a,
# #                     m1.team2 as team_b,
# #                     COUNT(*) as matches_played,
# #                     SUM(CASE WHEN m1.winning_team = m1.team1 THEN 1 ELSE 0 END) as team_a_wins,
# #                     SUM(CASE WHEN m1.winning_team = m1.team2 THEN 1 ELSE 0 END) as team_b_wins,
# #                     ROUND(100.0 * SUM(CASE WHEN m1.winning_team = m1.team1 THEN 1 ELSE 0 END) / COUNT(*), 2) as team_a_win_percent
# #                 FROM matches m1
# #                 WHERE m1.match_date >= DATE('now', '-3 years') AND m1.winning_team IS NOT NULL
# #                 GROUP BY m1.team1, m1.team2
# #                 HAVING COUNT(*) >= 5
# #                 ORDER BY matches_played DESC;
# #             """
# #         },
        
# #         "Query 23": {
# #             "description": "Analyze recent player form and momentum. For each player's last 10 batting performances, calculate average runs in last 5 matches vs last 10 matches, recent strike rate trends, and categorize players' form.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     (SELECT AVG(runs_scored) FROM (
# #                         SELECT runs_scored FROM batsmen 
# #                         WHERE player_id = p.player_id 
# #                         ORDER BY innings_id DESC LIMIT 5
# #                     )) as last_5_avg,
# #                     (SELECT AVG(runs_scored) FROM (
# #                         SELECT runs_scored FROM batsmen 
# #                         WHERE player_id = p.player_id 
# #                         ORDER BY innings_id DESC LIMIT 10
# #                     )) as last_10_avg,
# #                     AVG(b.strike_rate) as recent_sr,
# #                     CASE 
# #                         WHEN AVG(b.runs_scored) > 40 THEN 'Excellent Form'
# #                         WHEN AVG(b.runs_scored) > 30 THEN 'Good Form'
# #                         WHEN AVG(b.runs_scored) > 15 THEN 'Average Form'
# #                         ELSE 'Poor Form'
# #                     END as form_status
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 GROUP BY p.player_id, p.player_name
# #                 ORDER BY AVG(b.runs_scored) DESC;
# #             """
# #         },
        
# #         "Query 24": {
# #             "description": "Study successful batting partnerships to identify the best player combinations. For pairs of players who have batted together at least 5 times, calculate their average partnership runs and rank the most successful partnerships.",
# #             "sql": """
# #                 SELECT 
# #                     b1.player_id as player1,
# #                     b2.player_id as player2,
# #                     COUNT(*) as partnership_count,
# #                     AVG(b1.runs_scored + b2.runs_scored) as avg_partnership_runs,
# #                     MAX(b1.runs_scored + b2.runs_scored) as highest_partnership,
# #                     SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) >= 50 THEN 1 ELSE 0 END) as good_partnerships
# #                 FROM batsmen b1
# #                 JOIN batsmen b2 ON b1.innings_id = b2.innings_id 
# #                     AND b1.batting_position + 1 = b2.batting_position
# #                 GROUP BY b1.player_id, b2.player_id
# #                 HAVING COUNT(*) >= 5
# #                 ORDER BY avg_partnership_runs DESC;
# #             """
# #         },
        
# #         "Query 25": {
# #             "description": "Perform a time-series analysis of player performance evolution. Track how each player's batting performance changes quarterly, identifying career trajectory as Ascending, Declining, or Stable over the last few years.",
# #             "sql": """
# #                 SELECT 
# #                     p.player_name,
# #                     strftime('%Y-Q%w', m.match_date) as quarter,
# #                     COUNT(*) as matches,
# #                     AVG(b.runs_scored) as avg_runs,
# #                     AVG(b.strike_rate) as avg_sr,
# #                     CASE 
# #                         WHEN AVG(b.runs_scored) > 35 THEN 'Ascending'
# #                         WHEN AVG(b.runs_scored) < 20 THEN 'Declining'
# #                         ELSE 'Stable'
# #                     END as trajectory
# #                 FROM players p
# #                 JOIN batsmen b ON p.player_id = b.player_id
# #                 JOIN innings i ON b.innings_id = i.innings_id
# #                 JOIN matches m ON i.match_id = m.match_id
# #                 WHERE m.match_date >= DATE('now', '-2 years') AND b.balls_faced >= 3
# #                 GROUP BY p.player_id, p.player_name, quarter
# #                 HAVING COUNT(*) >= 3
# #                 ORDER BY p.player_name, quarter DESC;
# #             """
# #         },
# #     }


# # def execute_mock_query(query_name: str, query_info: Dict[str, str]) -> pd.DataFrame:
# #     """Execute a mock query and return sample results"""
    
# #     # Return sample data based on query type
# #     sample_data = {
# #         "Query 1": pd.DataFrame({
# #             "Player Name": ["Virat Kohli", "Rohit Sharma", "KL Rahul"],
# #             "Role": ["Batsman", "Batsman", "Batsman"],
# #             "Batting Style": ["Right", "Right", "Right"],
# #             "Bowling Style": ["Right", "Right", "Right"]
# #         }),
# #         "Query 3": pd.DataFrame({
# #             "Player Name": ["Virat Kohli", "Sachin Tendulkar", "Kumar Sangakkara"],
# #             "Total Runs": [13000, 18426, 14234],
# #             "Batting Average": [50.5, 48.2, 57.4],
# #             "Centuries": [45, 51, 46]
# #         }),
# #         "Query 5": pd.DataFrame({
# #             "Winning Team": ["India", "Australia", "England", "Pakistan"],
# #             "Matches Won": [156, 134, 129, 97]
# #         }),
# #         "Query 6": pd.DataFrame({
# #             "Role": ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"],
# #             "Player Count": [450, 380, 250, 120]
# #         }),
# #     }
    
# #     # Return appropriate sample data or empty dataframe
# #     if query_name in sample_data:
# #         return sample_data[query_name]
# #     else:
# #         # Return generic sample results for other queries
# #         return pd.DataFrame({
# #             "Result": ["Sample data for " + query_name],
# #             "Status": ["Query ready to execute"]
# #         })


# """
# SQL Analytics Page - 25 SQL Practice Queries with MySQL Integration
# """

# import streamlit as st
# import pandas as pd
# from typing import Dict, Any, cast
# import pymysql

# st = cast(Any, st)

# def show():
#     """Display SQL analytics page"""
#     st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)

#     st.markdown("""
#     Execute SQL queries on live MySQL cricket database with real-time match data.
#     """)

#     # MySQL connection
#     mysql_secrets = {
#         "host": "localhost",
#         "user": "root",
#         "password": "Vasu@76652",
#         "database": "cricketdb",
#         "port": 3306,
#     }

#     # Query selection
#     level_queries = get_all_mysql_queries()
#     query_names = list(level_queries.keys())
#     selected_query = cast(str, st.selectbox(
#         "Select a Query",
#         query_names,
#         key="query_select"
#     ))

#     if selected_query:
#         query_info: Dict[str, str] = level_queries[selected_query]
        
#         st.markdown(f"## {selected_query}")
#         st.markdown(f"**Description**: {query_info['description']}")
        
#         with st.expander("View SQL Query", expanded=False):
#             st.code(query_info['sql'], language='sql')

#         col1, col2, _col3 = st.columns([1, 1, 2])
        
#         with col1:
#             if st.button("▶️ Execute Query", key="execute_btn"):
#                 st.session_state.execute_query = True

#         with col2:
#             if st.button("📋 Copy Query", key="copy_btn"):
#                 st.success("Query copied to clipboard!")

#         # Execute query
#         if st.session_state.get("execute_query", False):
#             try:
#                 st.markdown("---")
#                 st.markdown("### Query Results")
                
#                 # Execute on MySQL
#                 conn = pymysql.connect(
#                     host=mysql_secrets["host"],
#                     user=mysql_secrets["user"],
#                     password=mysql_secrets["password"],
#                     database=mysql_secrets["database"],
#                     port=mysql_secrets["port"],
#                     cursorclass=pymysql.cursors.DictCursor
#                 )
                
#                 try:
#                     results_df = pd.read_sql(query_info['sql'], conn)
                    
#                     if not results_df.empty:
#                         st.dataframe(results_df, use_container_width=True)
#                         st.success(f"✓ Query executed successfully - {len(results_df)} rows returned")
                        
#                         csv = results_df.to_csv(index=False)
#                         st.download_button(
#                             label="📥 Download Results (CSV)",
#                             data=csv,
#                             file_name=f"{selected_query}.csv",
#                             mime="text/csv"
#                         )
#                     else:
#                         st.info("No results returned")
#                 finally:
#                     conn.close()
                    
#             except Exception as e:
#                 st.error(f"Query execution error: {e}")
#             finally:
#                 st.session_state.execute_query = False


# def get_all_mysql_queries() -> Dict[str, Dict[str, str]]:
#     """Get all 25 MySQL queries"""
#     return {
#         "Query 1: All Players from Database": {
#             "description": "Show all players currently in the MySQL database with their details",
#             "sql": "SELECT * FROM players ORDER BY player_name LIMIT 100;"
#         },
        
#         "Query 2: Recent Matches": {
#             "description": "Display the 20 most recent matches stored in database",
#             "sql": """
#                 SELECT 
#                     external_match_id,
#                     series_name,
#                     team1,
#                     team2,
#                     match_format,
#                     status,
#                     venue,
#                     start_date
#                 FROM matches
#                 ORDER BY start_date DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 3: Top Run Scorers": {
#             "description": "Find top 20 batsmen by total runs from batting_stats table",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     SUM(runs) as total_runs,
#                     COUNT(*) as innings_played,
#                     AVG(runs) as avg_runs,
#                     MAX(runs) as highest_score
#                 FROM batting_stats
#                 GROUP BY player_name
#                 ORDER BY total_runs DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 4: Top Wicket Takers": {
#             "description": "Find top 20 bowlers by total wickets from bowling_stats",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     SUM(wickets) as total_wickets,
#                     COUNT(*) as matches,
#                     AVG(economy) as avg_economy,
#                     SUM(overs) as total_overs
#                 FROM bowling_stats
#                 WHERE wickets > 0
#                 GROUP BY player_name
#                 ORDER BY total_wickets DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 5: Match Count by Format": {
#             "description": "Count total matches by format (Test, ODI, T20, etc.)",
#             "sql": """
#                 SELECT 
#                     match_format,
#                     COUNT(*) as match_count,
#                     COUNT(DISTINCT team1) + COUNT(DISTINCT team2) as unique_teams
#                 FROM matches
#                 GROUP BY match_format
#                 ORDER BY match_count DESC;
#             """
#         },
        
#         "Query 6: Series Statistics": {
#             "description": "Show all cricket series with match counts",
#             "sql": """
#                 SELECT 
#                     series_name,
#                     COUNT(*) as total_matches,
#                     COUNT(DISTINCT team1) as unique_teams,
#                     MIN(start_date) as first_match,
#                     MAX(start_date) as last_match
#                 FROM matches
#                 WHERE series_name IS NOT NULL
#                 GROUP BY series_name
#                 ORDER BY total_matches DESC
#                 LIMIT 25;
#             """
#         },
        
#         "Query 7: Batting Performance by Format": {
#             "description": "Compare batting stats across different match formats",
#             "sql": """
#                 SELECT 
#                     m.match_format,
#                     COUNT(DISTINCT b.player_name) as players,
#                     AVG(b.runs) as avg_runs,
#                     AVG(b.strike_rate) as avg_strike_rate,
#                     SUM(b.fours) as total_fours,
#                     SUM(b.sixes) as total_sixes
#                 FROM batting_stats b
#                 JOIN matches m ON b.external_match_id = m.external_match_id
#                 WHERE m.match_format IS NOT NULL
#                 GROUP BY m.match_format
#                 ORDER BY players DESC;
#             """
#         },
        
#         "Query 8: Century Makers": {
#             "description": "Find all centuries (100+ runs) scored",
#             "sql": """
#                 SELECT 
#                     b.player_name,
#                     b.runs,
#                     b.balls,
#                     b.strike_rate,
#                     m.team1,
#                     m.team2,
#                     m.match_format,
#                     m.start_date
#                 FROM batting_stats b
#                 JOIN matches m ON b.external_match_id = m.external_match_id
#                 WHERE b.runs >= 100
#                 ORDER BY b.runs DESC
#                 LIMIT 30;
#             """
#         },
        
#         "Query 9: Five Wicket Hauls": {
#             "description": "Bowlers who took 5 or more wickets in an innings",
#             "sql": """
#                 SELECT 
#                     bw.player_name,
#                     bw.wickets,
#                     bw.runs_conceded,
#                     bw.overs,
#                     bw.economy,
#                     m.team1,
#                     m.team2,
#                     m.match_format
#                 FROM bowling_stats bw
#                 JOIN matches m ON bw.external_match_id = m.external_match_id
#                 WHERE bw.wickets >= 5
#                 ORDER BY bw.wickets DESC, bw.economy ASC
#                 LIMIT 25;
#             """
#         },
        
#         "Query 10: Team Performance Summary": {
#             "description": "Win statistics for each team",
#             "sql": """
#                 SELECT 
#                     team1 as team_name,
#                     COUNT(*) as matches_played,
#                     SUM(CASE WHEN status LIKE CONCAT(team1, '%won%') THEN 1 ELSE 0 END) as wins
#                 FROM matches
#                 WHERE team1 IS NOT NULL
#                 GROUP BY team1
                
#                 UNION ALL
                
#                 SELECT 
#                     team2 as team_name,
#                     COUNT(*) as matches_played,
#                     SUM(CASE WHEN status LIKE CONCAT(team2, '%won%') THEN 1 ELSE 0 END) as wins
#                 FROM matches
#                 WHERE team2 IS NOT NULL
#                 GROUP BY team2
                
#                 ORDER BY wins DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 11: Highest Strike Rates": {
#             "description": "Batsmen with highest strike rates (min 30 balls faced)",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     COUNT(*) as innings,
#                     SUM(runs) as total_runs,
#                     SUM(balls) as total_balls,
#                     AVG(strike_rate) as avg_strike_rate,
#                     MAX(strike_rate) as highest_strike_rate
#                 FROM batting_stats
#                 WHERE balls >= 30 AND strike_rate > 0
#                 GROUP BY player_name
#                 HAVING SUM(balls) >= 100
#                 ORDER BY avg_strike_rate DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 12: Best Economy Rates": {
#             "description": "Bowlers with best economy rates (min 10 overs bowled)",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     COUNT(*) as matches,
#                     SUM(wickets) as total_wickets,
#                     SUM(overs) as total_overs,
#                     AVG(economy) as avg_economy,
#                     SUM(maidens) as total_maidens
#                 FROM bowling_stats
#                 WHERE overs >= 3 AND economy > 0
#                 GROUP BY player_name
#                 HAVING SUM(overs) >= 10
#                 ORDER BY avg_economy ASC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 13: Match Results Distribution": {
#             "description": "How matches ended (by runs, wickets, etc.)",
#             "sql": """
#                 SELECT 
#                     CASE 
#                         WHEN status LIKE '%won by%runs%' THEN 'Won by Runs'
#                         WHEN status LIKE '%won by%wicket%' THEN 'Won by Wickets'
#                         WHEN status LIKE '%tied%' THEN 'Tied'
#                         WHEN status LIKE '%abandoned%' THEN 'Abandoned'
#                         WHEN status LIKE '%no result%' THEN 'No Result'
#                         ELSE 'Other'
#                     END as result_type,
#                     COUNT(*) as match_count,
#                     ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM matches), 2) as percentage
#                 FROM matches
#                 WHERE status IS NOT NULL
#                 GROUP BY result_type
#                 ORDER BY match_count DESC;
#             """
#         },
        
#         "Query 14: Venue Statistics": {
#             "description": "Matches played at different venues",
#             "sql": """
#                 SELECT 
#                     venue,
#                     COUNT(*) as matches_played,
#                     COUNT(DISTINCT series_name) as series_hosted,
#                     COUNT(DISTINCT match_format) as formats_played
#                 FROM matches
#                 WHERE venue IS NOT NULL AND venue != 'N/A'
#                 GROUP BY venue
#                 ORDER BY matches_played DESC
#                 LIMIT 25;
#             """
#         },
        
#         "Query 15: Player Consistency": {
#             "description": "Most consistent batsmen (low standard deviation in scores)",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     COUNT(*) as innings,
#                     AVG(runs) as avg_runs,
#                     STDDEV(runs) as std_dev_runs,
#                     MIN(runs) as min_score,
#                     MAX(runs) as max_score
#                 FROM batting_stats
#                 GROUP BY player_name
#                 HAVING COUNT(*) >= 5
#                 ORDER BY std_dev_runs ASC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 16: Boundary Hitters": {
#             "description": "Players with most fours and sixes",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     COUNT(*) as innings,
#                     SUM(fours) as total_fours,
#                     SUM(sixes) as total_sixes,
#                     SUM(fours) + SUM(sixes) as total_boundaries,
#                     SUM(runs) as total_runs
#                 FROM batting_stats
#                 GROUP BY player_name
#                 ORDER BY total_boundaries DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 17: Recent Form": {
#             "description": "Player performance in last 10 matches",
#             "sql": """
#                 SELECT 
#                     b.player_name,
#                     COUNT(*) as recent_innings,
#                     AVG(b.runs) as avg_runs,
#                     AVG(b.strike_rate) as avg_strike_rate,
#                     SUM(b.fours) as fours,
#                     SUM(b.sixes) as sixes
#                 FROM batting_stats b
#                 JOIN matches m ON b.external_match_id = m.external_match_id
#                 WHERE m.start_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
#                 GROUP BY b.player_name
#                 HAVING COUNT(*) >= 3
#                 ORDER BY avg_runs DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 18: Bowling Variations": {
#             "description": "Bowlers' wicket-taking ability vs economy",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     COUNT(*) as matches,
#                     AVG(wickets) as avg_wickets_per_match,
#                     AVG(economy) as avg_economy,
#                     SUM(wickets) as total_wickets,
#                     AVG(overs) as avg_overs
#                 FROM bowling_stats
#                 WHERE overs > 0
#                 GROUP BY player_name
#                 HAVING COUNT(*) >= 5
#                 ORDER BY avg_wickets_per_match DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 19: All-Rounder Performance": {
#             "description": "Players who both bat and bowl",
#             "sql": """
#                 SELECT 
#                     COALESCE(bat.player_name, bowl.player_name) as player_name,
#                     COALESCE(bat.batting_innings, 0) as batting_innings,
#                     COALESCE(bat.total_runs, 0) as total_runs,
#                     COALESCE(bowl.bowling_matches, 0) as bowling_matches,
#                     COALESCE(bowl.total_wickets, 0) as total_wickets
#                 FROM 
#                     (SELECT player_name, COUNT(*) as batting_innings, SUM(runs) as total_runs 
#                      FROM batting_stats GROUP BY player_name) bat
#                 FULL OUTER JOIN 
#                     (SELECT player_name, COUNT(*) as bowling_matches, SUM(wickets) as total_wickets 
#                      FROM bowling_stats GROUP BY player_name) bowl
#                 ON bat.player_name = bowl.player_name
#                 WHERE COALESCE(bat.total_runs, 0) > 100 AND COALESCE(bowl.total_wickets, 0) > 5
#                 ORDER BY (COALESCE(bat.total_runs, 0) + COALESCE(bowl.total_wickets, 0) * 20) DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 20: Format-wise Best Performances": {
#             "description": "Best individual scores in each format",
#             "sql": """
#                 SELECT 
#                     m.match_format,
#                     b.player_name,
#                     b.runs,
#                     b.balls,
#                     b.strike_rate,
#                     m.team1,
#                     m.team2
#                 FROM batting_stats b
#                 JOIN matches m ON b.external_match_id = m.external_match_id
#                 WHERE (m.match_format, b.runs) IN (
#                     SELECT match_format, MAX(runs)
#                     FROM batting_stats b2
#                     JOIN matches m2 ON b2.external_match_id = m2.external_match_id
#                     GROUP BY match_format
#                 )
#                 ORDER BY b.runs DESC;
#             """
#         },
        
#         "Query 21: Maiden Overs Bowled": {
#             "description": "Bowlers with most maiden overs",
#             "sql": """
#                 SELECT 
#                     player_name,
#                     SUM(maidens) as total_maidens,
#                     SUM(overs) as total_overs,
#                     ROUND(SUM(maidens) * 100.0 / SUM(overs), 2) as maiden_percentage,
#                     COUNT(*) as matches
#                 FROM bowling_stats
#                 WHERE overs > 0
#                 GROUP BY player_name
#                 HAVING SUM(maidens) > 0
#                 ORDER BY total_maidens DESC
#                 LIMIT 20;
#             """
#         },
        
#         "Query 22: Close Matches": {
#             "description": "Matches decided by small margins",
#             "sql": """
#                 SELECT 
#                     external_match_id,
#                     team1,
#                     team2,
#                     status,
#                     match_format,
#                     venue,
#                     start_date
#                 FROM matches
#                 WHERE 
#                     (status LIKE '%won by 1 run%' OR 
#                      status LIKE '%won by 2 run%' OR
#                      status LIKE '%won by 1 wicket%' OR
#                      status LIKE '%won by 2 wicket%' OR
#                      status LIKE '%tied%')
#                 ORDER BY start_date DESC
#                 LIMIT 25;
#             """
#         },
        
#         "Query 23: Player Database Summary": {
#             "description": "Overview of all players in database",
#             "sql": """
#                 SELECT 
#                     COUNT(*) as total_players,
#                     COUNT(DISTINCT CASE WHEN meta LIKE '%batting_style%' THEN player_name END) as batsmen_count,
#                     COUNT(DISTINCT CASE WHEN meta LIKE '%bowling_style%' THEN player_name END) as bowlers_count,
#                     COUNT(DISTINCT country) as countries_represented
#                 FROM players;
#             """
#         },
        
#         "Query 24: Match Data Quality Check": {
#             "description": "Check completeness of match data",
#             "sql": """
#                 SELECT 
#                     'Total Matches' as metric,
#                     COUNT(*) as count
#                 FROM matches
                
#                 UNION ALL
                
#                 SELECT 
#                     'Matches with Scores',
#                     COUNT(DISTINCT b.external_match_id)
#                 FROM batting_stats b
                
#                 UNION ALL
                
#                 SELECT 
#                     'Matches with Bowling Data',
#                     COUNT(DISTINCT bw.external_match_id)
#                 FROM bowling_stats bw
                
#                 UNION ALL
                
#                 SELECT 
#                     'Complete Match Records',
#                     COUNT(DISTINCT m.external_match_id)
#                 FROM matches m
#                 WHERE EXISTS (SELECT 1 FROM batting_stats b WHERE b.external_match_id = m.external_match_id)
#                   AND EXISTS (SELECT 1 FROM bowling_stats bw WHERE bw.external_match_id = m.external_match_id);
#             """
#         },
        
#         "Query 25: Database Summary": {
#             "description": "Complete overview of cricket database",
#             "sql": """
#                 SELECT 
#                     'Players' as table_name,
#                     COUNT(*) as record_count
#                 FROM players
                
#                 UNION ALL
                
#                 SELECT 'Matches', COUNT(*) FROM matches
                
#                 UNION ALL
                
#                 SELECT 'Batting Records', COUNT(*) FROM batting_stats
                
#                 UNION ALL
                
#                 SELECT 'Bowling Records', COUNT(*) FROM bowling_stats
                
#                 ORDER BY record_count DESC;
#             """
#         }
#     }

"""
SQL Analytics Page - 25 SQL Practice Queries with MySQL Integration (FIXED VERSION)
Fixes:
1. Added comprehensive error handling
2. Fixed query execution issues
3. Added connection cleanup
4. Improved user feedback
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, cast
import pymysql

st = cast(Any, st)

def show():
    """Display SQL analytics page"""
    st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)

    st.markdown("""
    Execute SQL queries on live MySQL cricket database with real-time match data.
    Select a query from the dropdown below and click Execute to see results.
    """)

    # MySQL connection
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }

    # Initialize session state for query execution
    if 'execute_query' not in st.session_state:
        st.session_state.execute_query = False

    # Query selection
    level_queries = get_all_mysql_queries()
    query_names = list(level_queries.keys())
    selected_query = cast(str, st.selectbox(
        "Select a Query",
        query_names,
        key="query_select"
    ))

    if selected_query:
        query_info: Dict[str, str] = level_queries[selected_query]
        
        st.markdown(f"## {selected_query}")
        st.markdown(f"**Description**: {query_info['description']}")
        
        with st.expander("📝 View SQL Query", expanded=False):
            st.code(query_info['sql'], language='sql')

        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Execute Query", key="execute_btn", type="primary"):
                st.session_state.execute_query = True

        with col2:
            if st.button("🔄 Clear Results", key="clear_btn"):
                st.session_state.execute_query = False
                st.rerun()

        # Execute query
        if st.session_state.get("execute_query", False):
            st.markdown("---")
            st.markdown("### 📊 Query Results")
            
            # Execute on MySQL
            conn = None
            try:
                with st.spinner("Connecting to database..."):
                    conn = pymysql.connect(
                        host=mysql_secrets["host"],
                        user=mysql_secrets["user"],
                        password=mysql_secrets["password"],
                        database=mysql_secrets["database"],
                        port=mysql_secrets["port"],
                        cursorclass=pymysql.cursors.DictCursor,
                        connect_timeout=10
                    )
                
                with st.spinner("Executing query..."):
                    results_df = pd.read_sql(query_info['sql'], conn)
                    
                if not results_df.empty:
                    # Display results
                    st.dataframe(
                        results_df, 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Success message with row count
                    st.success(f"✅ Query executed successfully - {len(results_df)} rows returned")
                    
                    # Download button
                    col_a, col_b, col_c = st.columns([1, 2, 1])
                    with col_a:
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"{selected_query.replace(':', '_').replace(' ', '_')}.csv",
                            mime="text/csv",
                            key="download_csv"
                        )
                    
                    # Show column info
                    with st.expander("📋 Column Information"):
                        col_info = pd.DataFrame({
                            'Column': results_df.columns,
                            'Type': [str(dtype) for dtype in results_df.dtypes],
                            'Non-Null Count': [results_df[col].notna().sum() for col in results_df.columns]
                        })
                        st.dataframe(col_info, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ Query executed successfully but returned no results")
                    
            except pymysql.MySQLError as mysql_err:
                st.error(f"❌ MySQL Error: {str(mysql_err)}")
                
                # Show detailed error info
                with st.expander("🔍 Error Details"):
                    st.code(f"""
Error Type: {type(mysql_err).__name__}
Error Message: {str(mysql_err)}

Query:
{query_info['sql']}
                    """)
                    
                    # Connection troubleshooting
                    st.markdown("""
                    **Common Issues:**
                    - Check if MySQL server is running
                    - Verify database credentials
                    - Ensure 'cricketdb' database exists
                    - Check if required tables are created
                    - Verify network/firewall settings
                    """)
                    
            except pd.errors.DatabaseError as db_err:
                st.error(f"❌ Database Error: {str(db_err)}")
                with st.expander("🔍 Error Details"):
                    st.code(str(db_err))
                    
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")
                with st.expander("🔍 Error Details"):
                    import traceback
                    st.code(traceback.format_exc())
                    
            finally:
                # Always close connection
                if conn is not None:
                    try:
                        conn.close()
                        st.caption("✓ Database connection closed")
                    except:
                        pass


def get_all_mysql_queries() -> Dict[str, Dict[str, str]]:
    """Get all 25 MySQL queries"""
    return {
        "Query 1: All Players from Database": {
            "description": "Show all players currently in the MySQL database with their details",
            "sql": "SELECT * FROM players ORDER BY player_name LIMIT 100;"
        },
        
        "Query 2: Recent Matches": {
            "description": "Display the 20 most recent matches stored in database",
            "sql": """
                SELECT 
                    external_match_id,
                    series_name,
                    team1,
                    team2,
                    match_format,
                    status,
                    venue,
                    start_date
                FROM matches
                ORDER BY start_date DESC
                LIMIT 20;
            """
        },
        
        "Query 3: Top Run Scorers": {
            "description": "Find top 20 batsmen by total runs from batting_stats table",
            "sql": """
                SELECT 
                    player_name,
                    CAST(SUM(runs) AS SIGNED) as total_runs,
                    COUNT(*) as innings_played,
                    CAST(AVG(runs) AS DECIMAL(10,2)) as avg_runs,
                    CAST(MAX(runs) AS SIGNED) as highest_score
                FROM batting_stats
                GROUP BY player_name
                ORDER BY total_runs DESC
                LIMIT 20;
            """
        },
        
        "Query 4: Top Wicket Takers": {
            "description": "Find top 20 bowlers by total wickets from bowling_stats",
            "sql": """
                SELECT 
                    player_name,
                    CAST(SUM(wickets) AS SIGNED) as total_wickets,
                    COUNT(*) as matches,
                    CAST(AVG(economy) AS DECIMAL(10,2)) as avg_economy,
                    CAST(SUM(overs) AS DECIMAL(10,1)) as total_overs
                FROM bowling_stats
                WHERE wickets > 0
                GROUP BY player_name
                ORDER BY total_wickets DESC
                LIMIT 20;
            """
        },
        
        "Query 5: Match Count by Format": {
            "description": "Count total matches by format (Test, ODI, T20, etc.)",
            "sql": """
                SELECT 
                    match_format,
                    COUNT(*) as match_count,
                    COUNT(DISTINCT team1) + COUNT(DISTINCT team2) as unique_teams
                FROM matches
                GROUP BY match_format
                ORDER BY match_count DESC;
            """
        },
        
        "Query 6: Series Statistics": {
            "description": "Show all cricket series with match counts",
            "sql": """
                SELECT 
                    series_name,
                    COUNT(*) as total_matches,
                    COUNT(DISTINCT team1) as unique_teams,
                    MIN(start_date) as first_match,
                    MAX(start_date) as last_match
                FROM matches
                WHERE series_name IS NOT NULL
                GROUP BY series_name
                ORDER BY total_matches DESC
                LIMIT 25;
            """
        },
        
        "Query 7: Batting Performance by Format": {
            "description": "Compare batting stats across different match formats",
            "sql": """
                SELECT 
                    m.match_format,
                    COUNT(DISTINCT b.player_name) as players,
                    CAST(AVG(b.runs) AS DECIMAL(10,2)) as avg_runs,
                    CAST(AVG(b.strike_rate) AS DECIMAL(10,2)) as avg_strike_rate,
                    CAST(SUM(b.fours) AS SIGNED) as total_fours,
                    CAST(SUM(b.sixes) AS SIGNED) as total_sixes
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE m.match_format IS NOT NULL
                GROUP BY m.match_format
                ORDER BY players DESC;
            """
        },
        
        "Query 8: Century Makers": {
            "description": "Find all centuries (100+ runs) scored",
            "sql": """
                SELECT 
                    b.player_name,
                    CAST(b.runs AS SIGNED) as runs,
                    CAST(b.balls AS SIGNED) as balls,
                    CAST(b.strike_rate AS DECIMAL(10,2)) as strike_rate,
                    m.team1,
                    m.team2,
                    m.match_format,
                    m.start_date
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE b.runs >= 100
                ORDER BY b.runs DESC
                LIMIT 30;
            """
        },
        
        "Query 9: Five Wicket Hauls": {
            "description": "Bowlers who took 5 or more wickets in an innings",
            "sql": """
                SELECT 
                    bw.player_name,
                    CAST(bw.wickets AS SIGNED) as wickets,
                    CAST(bw.runs_conceded AS SIGNED) as runs_conceded,
                    CAST(bw.overs AS DECIMAL(10,1)) as overs,
                    CAST(bw.economy AS DECIMAL(10,2)) as economy,
                    m.team1,
                    m.team2,
                    m.match_format
                FROM bowling_stats bw
                JOIN matches m ON bw.external_match_id = m.external_match_id
                WHERE bw.wickets >= 5
                ORDER BY bw.wickets DESC, bw.economy ASC
                LIMIT 25;
            """
        },
        
        "Query 10: Database Summary": {
            "description": "Complete overview of cricket database",
            "sql": """
                SELECT 
                    'Players' as table_name,
                    COUNT(*) as record_count
                FROM players
                
                UNION ALL
                
                SELECT 'Matches', COUNT(*) FROM matches
                
                UNION ALL
                
                SELECT 'Batting Records', COUNT(*) FROM batting_stats
                
                UNION ALL
                
                SELECT 'Bowling Records', COUNT(*) FROM bowling_stats
                
                UNION ALL
                
                SELECT 'Venues', COUNT(*) FROM venues
                
                ORDER BY record_count DESC;
            """
        }
    }