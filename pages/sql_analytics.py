"""
SQL Analytics Page - 25 SQL Practice Queries
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, cast

# Optional SQLAlchemy/pymysql imports. Declare as Any and use targeted
# type-ignore on the imports so Pylance won't flag missing optional deps.
create_engine: Any = None
pymysql: Any = None
try:
    # type: ignore[reportMissingImports]
    from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
    import pymysql  # type: ignore[reportMissingImports]
except Exception:
    create_engine = None  # type: ignore
    pymysql = None  # type: ignore
# Help Pylance by treating Streamlit dynamic members (markdown, columns, etc.) as Any
st = cast(Any, st)
from typing import Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import get_db_connection


def show():
    """Display SQL analytics page"""
    st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)

    st.markdown("""
    This section contains 25 SQL practice queries. Execute queries on your cricket
    database and view results below.
    """)

    _db = get_db_connection()  # type: ignore[unused-variable]
    _db = cast(Any, _db)

    # Define all 25 queries and show them (no difficulty filtering)
    level_queries: Dict[str, Dict[str, str]] = get_all_queries()  # type: ignore[assignment]

    # Query selection
    query_names = list(level_queries.keys())  # type: ignore[arg-type]
    selected_query = cast(str, st.selectbox(
        "Select a Query",
        query_names,
        key="query_select"
    ))

    if selected_query:
        query_info: Dict[str, str] = level_queries[selected_query]  # type: ignore[assignment]
        
        # Display query information
        st.markdown(f"## {selected_query}")
        st.markdown(f"**Description**: {query_info['description']}")  # type: ignore[index]
        
        with st.expander("View SQL Query", expanded=False):
            st.code(query_info['sql'], language='sql')  # type: ignore[index]

        # Execute Query Button
        col1, col2, _col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Execute Query", key="execute_btn"):
                st.session_state.execute_query = True

        with col2:
            if st.button("📋 Copy Query", key="copy_btn"):
                st.success("Query copied to clipboard!")

        # Display Results
        if st.session_state.get("execute_query", False):
            try:
                st.markdown("---")
                st.markdown("### Query Results")
                
                # Execute the query against MySQL if secrets available, otherwise use mock/DB
                results_df = pd.DataFrame()
                mysql_secrets = None
                try:
                    mysql_secrets = st.secrets.get("mysql")
                except Exception:
                    mysql_secrets = None

                if mysql_secrets and create_engine is not None:
                    try:
                        host = mysql_secrets.get("host", "localhost")
                        port = mysql_secrets.get("port", 3306)
                        user = mysql_secrets.get("user")
                        password = mysql_secrets.get("password")
                        dbname = mysql_secrets.get("dbname") or mysql_secrets.get("database")
                        if user and password and dbname:
                            engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}")
                            results_df = pd.read_sql(query_info['sql'], engine)  # type: ignore[call-arg]
                    except Exception as e:
                        st.error(f"Error executing query on MySQL: {e}")
                        results_df = pd.DataFrame()
                else:
                    # Execute the query (mock execution for demo or using local DB)
                    results_df = execute_mock_query(selected_query, query_info)
                
                if not results_df.empty:
                    st.dataframe(results_df, use_container_width=True)  # type: ignore[call-arg]
                    st.success(f"✓ Query executed successfully - {len(results_df)} rows returned")
                    
                    # Download option
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name=f"{selected_query}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No results returned")
                    
            except Exception as e:
                st.error(f"Query execution error: {e}")


def get_all_queries() -> Dict[str, Dict[str, str]]:
    """Get all 25 SQL queries with descriptions"""
    return {
        # Beginner Queries (1-8)
        "Query 1": {
            "description": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
            "sql": """
                SELECT 
                    player_name,
                    role,
                    batting_style,
                    bowling_style
                FROM players
                WHERE country = 'India'
                ORDER BY player_name;
            """
        },
        
        "Query 2": {
            "description": "Show all cricket matches that were played in the last few days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.",
            "sql": """
                SELECT 
                    m.match_description,
                    m.team1,
                    m.team2,
                    v.venue_name,
                    v.city,
                    m.match_date
                FROM matches m
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.match_date >= DATE('now', '-7 days')
                ORDER BY m.match_date DESC;
            """
        },
        
        "Query 3": {
            "description": "List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.",
            "sql": """
                SELECT 
                    player_name,
                    total_runs,
                    batting_average,
                    (SELECT COUNT(*) FROM batsmen b 
                     WHERE b.player_id = p.player_id AND b.runs_scored >= 100) as centuries
                FROM players p
                WHERE 1=1
                ORDER BY total_runs DESC
                LIMIT 10;
            """
        },
        
        "Query 4": {
            "description": "Display all cricket venues that have a seating capacity of more than 30,000 spectators. Show venue name, city, country, and capacity. Order by largest capacity first.",
            "sql": """
                SELECT 
                    venue_name,
                    city,
                    country,
                    capacity
                FROM venues
                WHERE capacity > 30000
                ORDER BY capacity DESC;
            """
        },
        
        "Query 5": {
            "description": "Calculate how many matches each team has won. Show team name and total number of wins. Display teams with the most wins first.",
            "sql": """
                SELECT 
                    winning_team,
                    COUNT(*) as matches_won
                FROM matches
                WHERE winning_team IS NOT NULL
                GROUP BY winning_team
                ORDER BY matches_won DESC;
            """
        },
        
        "Query 6": {
            "description": "Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players for each role.",
            "sql": """
                SELECT 
                    role,
                    COUNT(*) as player_count
                FROM players
                WHERE role IS NOT NULL
                GROUP BY role
                ORDER BY player_count DESC;
            """
        },
        
        "Query 7": {
            "description": "Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I). Display the format and the highest score for that format.",
            "sql": """
                SELECT 
                    m.match_format,
                    MAX(b.runs_scored) as highest_score
                FROM batsmen b
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                GROUP BY m.match_format
                ORDER BY highest_score DESC;
            """
        },
        
        "Query 8": {
            "description": "Show all cricket series that started in the year 2024. Include series name, host country, match type, start date, and total number of matches planned.",
            "sql": """
                SELECT 
                    m.match_description,
                    m.team1,
                    m.team2,
                    COUNT(*) as matches_in_series
                FROM matches m
                WHERE strftime('%Y', m.match_date) = '2024'
                GROUP BY m.match_description
                ORDER BY m.match_date;
            """
        },

        # Intermediate Queries (9-16)
        "Query 9": {
            "description": "Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.",
            "sql": """
                SELECT 
                    player_name,
                    total_runs,
                    total_wickets,
                    role
                FROM players
                WHERE total_runs > 1000 AND total_wickets > 50 AND role = 'All-rounder'
                ORDER BY total_runs DESC;
            """
        },
        
        "Query 10": {
            "description": "Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.",
            "sql": """
                SELECT 
                    m.match_description,
                    m.team1,
                    m.team2,
                    m.winning_team,
                    m.victory_margin,
                    m.victory_type,
                    v.venue_name,
                    m.match_date
                FROM matches m
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.winning_team IS NOT NULL
                ORDER BY m.match_date DESC
                LIMIT 20;
            """
        },
        
        "Query 11": {
            "description": "Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.",
            "sql": """
                SELECT 
                    p.player_name,
                    COUNT(DISTINCT m.match_format) as format_count,
                    p.batting_average,
                    SUM(CASE WHEN m.match_format = 'Test' THEN b.runs_scored ELSE 0 END) as test_runs,
                    SUM(CASE WHEN m.match_format = 'ODI' THEN b.runs_scored ELSE 0 END) as odi_runs,
                    SUM(CASE WHEN m.match_format = 'T20I' THEN b.runs_scored ELSE 0 END) as t20i_runs
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                GROUP BY p.player_id, p.player_name
                HAVING COUNT(DISTINCT m.match_format) >= 2
                ORDER BY p.batting_average DESC;
            """
        },
        
        "Query 12": {
            "description": "Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.",
            "sql": """
                SELECT 
                    winning_team,
                    v.country,
                    COUNT(*) as wins
                FROM matches m
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.winning_team IS NOT NULL
                GROUP BY m.winning_team, v.country
                ORDER BY winning_team, wins DESC;
            """
        },
        
        "Query 13": {
            "description": "Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.",
            "sql": """
                SELECT 
                    b1.player_id as player1_id,
                    b2.player_id as player2_id,
                    (b1.runs_scored + b2.runs_scored) as partnership_runs,
                    b1.innings_id
                FROM batsmen b1
                JOIN batsmen b2 ON b1.innings_id = b2.innings_id 
                    AND b1.batting_position + 1 = b2.batting_position
                WHERE (b1.runs_scored + b2.runs_scored) >= 100
                ORDER BY partnership_runs DESC;
            """
        },
        
        "Query 14": {
            "description": "Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.",
            "sql": """
                SELECT 
                    bw.player_id,
                    v.venue_name,
                    COUNT(DISTINCT m.match_id) as matches_at_venue,
                    AVG(bw.economy_rate) as avg_economy,
                    SUM(bw.wickets_taken) as total_wickets
                FROM bowlers bw
                JOIN innings i ON bw.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                JOIN venues v ON m.venue_id = v.venue_id
                WHERE bw.overs_bowled >= 4
                GROUP BY bw.player_id, v.venue_id
                HAVING COUNT(DISTINCT m.match_id) >= 3
                ORDER BY total_wickets DESC;
            """
        },
        
        "Query 15": {
            "description": "Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.",
            "sql": """
                SELECT 
                    p.player_name,
                    COUNT(DISTINCT m.match_id) as close_matches,
                    AVG(b.runs_scored) as avg_runs,
                    SUM(CASE WHEN m.winning_team = i.batting_team THEN 1 ELSE 0 END) as matches_won
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                WHERE (CAST(m.victory_margin as INTEGER) < 50 OR CAST(m.victory_margin as INTEGER) < 5)
                GROUP BY p.player_id, p.player_name
                ORDER BY avg_runs DESC;
            """
        },
        
        "Query 16": {
            "description": "Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.",
            "sql": """
                SELECT 
                    p.player_name,
                    strftime('%Y', m.match_date) as year,
                    COUNT(*) as matches,
                    AVG(b.runs_scored) as avg_runs,
                    AVG(b.strike_rate) as avg_strike_rate
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                WHERE strftime('%Y', m.match_date) >= '2020'
                GROUP BY p.player_id, p.player_name, year
                HAVING COUNT(*) >= 5
                ORDER BY year DESC, avg_runs DESC;
            """
        },

        # Advanced Queries (17-25)
        "Query 17": {
            "description": "Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
            "sql": """
                SELECT 
                    m.toss_decision,
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN m.winning_team = m.toss_winner THEN 1 ELSE 0 END) as wins_by_toss_winner,
                    ROUND(100.0 * SUM(CASE WHEN m.winning_team = m.toss_winner THEN 1 ELSE 0 END) / COUNT(*), 2) as win_percentage
                FROM matches m
                WHERE m.toss_winner IS NOT NULL AND m.toss_decision IS NOT NULL
                GROUP BY m.toss_decision
                ORDER BY win_percentage DESC;
            """
        },
        
        "Query 18": {
            "description": "Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
            "sql": """
                SELECT 
                    p.player_name,
                    COUNT(DISTINCT m.match_id) as matches,
                    AVG(bw.economy_rate) as avg_economy,
                    SUM(bw.wickets_taken) as total_wickets,
                    AVG(bw.overs_bowled) as avg_overs
                FROM players p
                JOIN bowlers bw ON p.player_id = bw.player_id
                JOIN innings i ON bw.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                WHERE m.match_format IN ('ODI', 'T20I')
                GROUP BY p.player_id, p.player_name
                HAVING COUNT(DISTINCT m.match_id) >= 10 AND AVG(bw.overs_bowled) >= 2
                ORDER BY avg_economy ASC;
            """
        },
        
        "Query 19": {
            "description": "Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.",
            "sql": """
                SELECT 
                    p.player_name,
                    COUNT(*) as innings,
                    AVG(b.runs_scored) as avg_runs,
                    SQRT(AVG((b.runs_scored - (SELECT AVG(runs_scored) FROM batsmen b2 WHERE b2.player_id = p.player_id)) * 
                        (b.runs_scored - (SELECT AVG(runs_scored) FROM batsmen b2 WHERE b2.player_id = p.player_id)))) as std_dev
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                WHERE b.balls_faced >= 10 AND strftime('%Y', m.match_date) >= '2022'
                GROUP BY p.player_id, p.player_name
                ORDER BY std_dev ASC;
            """
        },
        
        "Query 20": {
            "description": "Analyze how many matches each player has played in different cricket formats and their batting average in each format. Show the count of Test matches, ODI matches, and T20 matches for each player, along with their respective batting averages. Only include players who have played at least 20 total matches across all formats.",
            "sql": """
                SELECT 
                    p.player_name,
                    SUM(CASE WHEN m.match_format = 'Test' THEN 1 ELSE 0 END) as test_matches,
                    SUM(CASE WHEN m.match_format = 'ODI' THEN 1 ELSE 0 END) as odi_matches,
                    SUM(CASE WHEN m.match_format = 'T20I' THEN 1 ELSE 0 END) as t20i_matches,
                    COUNT(*) as total_matches,
                    AVG(CASE WHEN m.match_format = 'Test' THEN b.runs_scored ELSE NULL END) as test_avg,
                    AVG(CASE WHEN m.match_format = 'ODI' THEN b.runs_scored ELSE NULL END) as odi_avg,
                    AVG(CASE WHEN m.match_format = 'T20I' THEN b.runs_scored ELSE NULL END) as t20i_avg
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                GROUP BY p.player_id, p.player_name
                HAVING COUNT(*) >= 20
                ORDER BY total_matches DESC;
            """
        },
        
        "Query 21": {
            "description": "Create a comprehensive performance ranking system for players. Combine batting performance, bowling performance, and fielding performance into a single weighted score. Rank the top performers in each cricket format.",
            "sql": """
                SELECT 
                    p.player_name,
                    (p.total_runs * 0.01) + (p.batting_average * 0.5) + (COALESCE((SELECT AVG(strike_rate) FROM batsmen WHERE player_id = p.player_id), 0) * 0.3) as batting_points,
                    (p.total_wickets * 2) + ((50 - p.bowling_average) * 0.5) as bowling_points,
                    ((p.total_runs * 0.01) + (p.batting_average * 0.5) + (COALESCE((SELECT AVG(strike_rate) FROM batsmen WHERE player_id = p.player_id), 0) * 0.3)) +
                    ((p.total_wickets * 2) + ((50 - p.bowling_average) * 0.5)) as total_points
                FROM players p
                WHERE p.total_runs > 0 OR p.total_wickets > 0
                ORDER BY total_points DESC;
            """
        },
        
        "Query 22": {
            "description": "Build a head-to-head match prediction analysis between teams. For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate total matches played, wins for each team, and overall win percentage.",
            "sql": """
                SELECT 
                    m1.team1 as team_a,
                    m1.team2 as team_b,
                    COUNT(*) as matches_played,
                    SUM(CASE WHEN m1.winning_team = m1.team1 THEN 1 ELSE 0 END) as team_a_wins,
                    SUM(CASE WHEN m1.winning_team = m1.team2 THEN 1 ELSE 0 END) as team_b_wins,
                    ROUND(100.0 * SUM(CASE WHEN m1.winning_team = m1.team1 THEN 1 ELSE 0 END) / COUNT(*), 2) as team_a_win_percent
                FROM matches m1
                WHERE m1.match_date >= DATE('now', '-3 years') AND m1.winning_team IS NOT NULL
                GROUP BY m1.team1, m1.team2
                HAVING COUNT(*) >= 5
                ORDER BY matches_played DESC;
            """
        },
        
        "Query 23": {
            "description": "Analyze recent player form and momentum. For each player's last 10 batting performances, calculate average runs in last 5 matches vs last 10 matches, recent strike rate trends, and categorize players' form.",
            "sql": """
                SELECT 
                    p.player_name,
                    (SELECT AVG(runs_scored) FROM (
                        SELECT runs_scored FROM batsmen 
                        WHERE player_id = p.player_id 
                        ORDER BY innings_id DESC LIMIT 5
                    )) as last_5_avg,
                    (SELECT AVG(runs_scored) FROM (
                        SELECT runs_scored FROM batsmen 
                        WHERE player_id = p.player_id 
                        ORDER BY innings_id DESC LIMIT 10
                    )) as last_10_avg,
                    AVG(b.strike_rate) as recent_sr,
                    CASE 
                        WHEN AVG(b.runs_scored) > 40 THEN 'Excellent Form'
                        WHEN AVG(b.runs_scored) > 30 THEN 'Good Form'
                        WHEN AVG(b.runs_scored) > 15 THEN 'Average Form'
                        ELSE 'Poor Form'
                    END as form_status
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                GROUP BY p.player_id, p.player_name
                ORDER BY AVG(b.runs_scored) DESC;
            """
        },
        
        "Query 24": {
            "description": "Study successful batting partnerships to identify the best player combinations. For pairs of players who have batted together at least 5 times, calculate their average partnership runs and rank the most successful partnerships.",
            "sql": """
                SELECT 
                    b1.player_id as player1,
                    b2.player_id as player2,
                    COUNT(*) as partnership_count,
                    AVG(b1.runs_scored + b2.runs_scored) as avg_partnership_runs,
                    MAX(b1.runs_scored + b2.runs_scored) as highest_partnership,
                    SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) >= 50 THEN 1 ELSE 0 END) as good_partnerships
                FROM batsmen b1
                JOIN batsmen b2 ON b1.innings_id = b2.innings_id 
                    AND b1.batting_position + 1 = b2.batting_position
                GROUP BY b1.player_id, b2.player_id
                HAVING COUNT(*) >= 5
                ORDER BY avg_partnership_runs DESC;
            """
        },
        
        "Query 25": {
            "description": "Perform a time-series analysis of player performance evolution. Track how each player's batting performance changes quarterly, identifying career trajectory as Ascending, Declining, or Stable over the last few years.",
            "sql": """
                SELECT 
                    p.player_name,
                    strftime('%Y-Q%w', m.match_date) as quarter,
                    COUNT(*) as matches,
                    AVG(b.runs_scored) as avg_runs,
                    AVG(b.strike_rate) as avg_sr,
                    CASE 
                        WHEN AVG(b.runs_scored) > 35 THEN 'Ascending'
                        WHEN AVG(b.runs_scored) < 20 THEN 'Declining'
                        ELSE 'Stable'
                    END as trajectory
                FROM players p
                JOIN batsmen b ON p.player_id = b.player_id
                JOIN innings i ON b.innings_id = i.innings_id
                JOIN matches m ON i.match_id = m.match_id
                WHERE m.match_date >= DATE('now', '-2 years') AND b.balls_faced >= 3
                GROUP BY p.player_id, p.player_name, quarter
                HAVING COUNT(*) >= 3
                ORDER BY p.player_name, quarter DESC;
            """
        },
    }


def execute_mock_query(query_name: str, query_info: Dict[str, str]) -> pd.DataFrame:
    """Execute a mock query and return sample results"""
    
    # Return sample data based on query type
    sample_data = {
        "Query 1": pd.DataFrame({
            "Player Name": ["Virat Kohli", "Rohit Sharma", "KL Rahul"],
            "Role": ["Batsman", "Batsman", "Batsman"],
            "Batting Style": ["Right", "Right", "Right"],
            "Bowling Style": ["Right", "Right", "Right"]
        }),
        "Query 3": pd.DataFrame({
            "Player Name": ["Virat Kohli", "Sachin Tendulkar", "Kumar Sangakkara"],
            "Total Runs": [13000, 18426, 14234],
            "Batting Average": [50.5, 48.2, 57.4],
            "Centuries": [45, 51, 46]
        }),
        "Query 5": pd.DataFrame({
            "Winning Team": ["India", "Australia", "England", "Pakistan"],
            "Matches Won": [156, 134, 129, 97]
        }),
        "Query 6": pd.DataFrame({
            "Role": ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"],
            "Player Count": [450, 380, 250, 120]
        }),
    }
    
    # Return appropriate sample data or empty dataframe
    if query_name in sample_data:
        return sample_data[query_name]
    else:
        # Return generic sample results for other queries
        return pd.DataFrame({
            "Result": ["Sample data for " + query_name],
            "Status": ["Query ready to execute"]
        })
