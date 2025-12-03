"""
Database Diagnostic Tool - Check what's in your database
Add this as a new page to diagnose the issue
"""

import streamlit as st
import pandas as pd
import pymysql
from contextlib import contextmanager
from typing import Any, Dict, TypedDict, cast


class DBConfig(TypedDict):
    host: str
    user: str
    password: str
    database: str
    port: int

@contextmanager
def get_mysql_connection():
    mysql_config: DBConfig = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    conn = None
    try:
        conn = pymysql.connect(
            host=mysql_config["host"],
            user=mysql_config["user"],
            password=mysql_config["password"],
            database=mysql_config["database"],
            port=mysql_config["port"],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        yield conn
    finally:
        if conn:
            conn.close()


def show():
    """Diagnostic page to check database status"""
    st.title("🔍 Database Diagnostic Tool")
    
    st.markdown("""
    This tool will help diagnose why your database appears empty or shows placeholder data.
    """)
    
    try:
        with get_mysql_connection() as conn:
            st.success("✅ Successfully connected to MySQL")
            
            # Check all tables
            st.markdown("## 📊 Table Status")
            
            tables = ['players', 'matches', 'batting_stats', 'bowling_stats', 'venues']
            
            for table in tables:
                with st.expander(f"📋 Table: {table}", expanded=True):
                    # Count records
                    count_query = f"SELECT COUNT(*) as total FROM {table}"
                    count_df = pd.read_sql(count_query, cast(Any, conn))
                    total = count_df.iloc[0]['total']
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if total > 0:
                            st.success(f"✅ {total:,} records")
                        else:
                            st.error(f"❌ {total} records (EMPTY!)")
                    
                    with col2:
                        if total > 0:
                            # Show sample data
                            sample_query = f"SELECT * FROM {table} LIMIT 3"
                            sample_df = pd.read_sql(sample_query, cast(Any, conn))
                            st.dataframe(sample_df, use_container_width=True, hide_index=True)
                        else:
                            st.warning(f"⚠️ Table '{table}' is empty. You need to sync data from Live Matches page.")
            
            # Check for NULL/placeholder data
            st.markdown("---")
            st.markdown("## 🔎 Data Quality Check")
            
            # Check players table specifically
            with st.expander("Players Table Quality", expanded=True):
                query = """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN player_name IS NULL OR player_name = '' THEN 1 ELSE 0 END) as null_names,
                        SUM(CASE WHEN player_name = 'player_name' THEN 1 ELSE 0 END) as placeholder_names,
                        SUM(CASE WHEN country IS NULL OR country = '' THEN 1 ELSE 0 END) as null_country
                    FROM players
                """
                quality_df = pd.read_sql(query, cast(Any, conn))
                
                if quality_df.iloc[0]['total'] > 0:
                    st.dataframe(quality_df, use_container_width=True, hide_index=True)
                    
                    null_names = quality_df.iloc[0]['null_names']
                    placeholder_names = quality_df.iloc[0]['placeholder_names']
                    
                    if null_names > 0:
                        st.error(f"❌ Found {null_names} players with NULL/empty names")
                    if placeholder_names > 0:
                        st.error(f"❌ Found {placeholder_names} players with placeholder name 'player_name'")
                    
                    if null_names == 0 and placeholder_names == 0:
                        st.success("✅ All player names look good!")
                else:
                    st.warning("⚠️ No players in database")
            
            # Show actual sample data
            st.markdown("---")
            st.markdown("## 📄 Sample Real Data")
            
            sample_query = """
                SELECT 
                    id, player_name, country, role 
                FROM players 
                WHERE player_name IS NOT NULL 
                  AND player_name != '' 
                  AND player_name != 'player_name'
                LIMIT 10
            """
            sample_df = pd.read_sql(sample_query, cast(Any, conn))
            
            if not sample_df.empty:
                st.success(f"✅ Found {len(sample_df)} valid player records:")
                st.dataframe(sample_df, use_container_width=True, hide_index=True)
            else:
                st.error("❌ No valid player data found!")
                st.markdown("""
                ### How to Fix:
                1. Go to **Live Matches** page
                2. Click **Sync All Matches** button
                3. Wait for sync to complete
                4. Come back to Player Stats page
                """)
            
            # Check matches
            st.markdown("---")
            st.markdown("## 🏏 Match Data Status")
            
            match_query = """
                SELECT 
                    COUNT(*) as total_matches,
                    COUNT(DISTINCT series_name) as series_count,
                    MAX(start_date) as latest_match
                FROM matches
            """
            match_df = pd.read_sql(match_query, cast(Any, conn))
            st.dataframe(match_df, use_container_width=True, hide_index=True)
            
            # Check if tables were created but never populated
            st.markdown("---")
            st.markdown("## 🛠️ Recommendations")
            
            players_count = pd.read_sql("SELECT COUNT(*) as cnt FROM players", cast(Any, conn)).iloc[0]['cnt']
            matches_count = pd.read_sql("SELECT COUNT(*) as cnt FROM matches", cast(Any, conn)).iloc[0]['cnt']
            
            if players_count == 0 and matches_count == 0:
                st.error("""
                ### ❌ Database is completely empty!
                
                **Action Required:**
                1. Navigate to the **Live Matches** page
                2. Click on **"Sync All Matches"** or **"Fetch Latest Matches"**
                3. Wait for the sync process to complete
                4. You should see match data being inserted
                5. Return to Player Stats page to see the data
                
                **Note:** The tables exist but have no data. You must fetch data from the cricket API first.
                """)
            elif players_count > 0:
                st.success(f"""
                ### ✅ Database has data!
                
                You have {players_count:,} players in the database.
                If you're still seeing placeholder data, the issue might be in how the data is being queried.
                """)
    
    except pymysql.MySQLError as e:
        st.error(f"❌ MySQL Error: {str(e)}")
        st.markdown("""
        ### Troubleshooting:
        - Check if MySQL service is running
        - Verify connection credentials
        - Ensure 'cricketdb' database exists
        """)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    show()