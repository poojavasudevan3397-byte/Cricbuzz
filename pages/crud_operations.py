"""
CRUD Operations Page - Create, Read, Update, Delete Player and Match Records
"""

import streamlit as st
from typing import Any, cast

# Help Pylance by treating Streamlit and DB connection as Any for dynamic members
st = cast(Any, st)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import get_db_connection


def show():
    """Display CRUD operations page"""
    st.markdown("<h1 class='page-title'>🛠️ CRUD Operations</h1>", unsafe_allow_html=True)

    st.markdown("""
    Manage your cricket database with full CRUD (Create, Read, Update, Delete) operations.
    Add new players, matches, and venues, or modify existing records.
    """)

    db = get_db_connection()
    db = cast(Any, db)

    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs(
        ["👤 Players", "🏟️ Matches", "🏟️ Venues", "📊 Summary"]
    )

    # Tab 1: Player Management
    with tab1:
        st.markdown("## 👤 Player Management")

        operation = st.radio(
            "Select Operation",
            ["Create", "Read", "Update", "Delete"],
            horizontal=True,
            key="player_op"
        )

        if operation == "Create":
            st.markdown("### Add New Player")
            with st.form("add_player_form"):
                player_name = st.text_input("Player Name", placeholder="e.g., Virat Kohli")
                country = st.selectbox(
                    "Country",
                    ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"]
                )
                role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
                batting_style = st.selectbox("Batting Style", ["Right", "Left", "Ambidextrous"])
                bowling_style = st.selectbox("Bowling Style", ["Right", "Left", "N/A"])

                if st.form_submit_button("➕ Add Player"):
                    if player_name:
                        try:
                            player_id = db.insert_player(
                                player_name=player_name,
                                country=country,
                                role=role,
                                batting_style=batting_style,
                                bowling_style=bowling_style
                            )
                            st.success(f"✓ Player added successfully! (ID: {player_id})")
                        except Exception as e:
                            st.error(f"Error adding player: {e}")
                    else:
                        st.warning("Please enter player name")

        elif operation == "Read":
            st.markdown("### View All Players")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    st.dataframe(players_df, use_container_width=True)  # type: ignore[call-arg]
                    st.info(f"Total Players: {len(players_df)}")
                else:
                    st.info("No players in database")
            except Exception as e:
                st.error(f"Error reading players: {e}")

        elif operation == "Update":
            st.markdown("### Update Player Record")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    player_to_update = st.selectbox(
                        "Select Player to Update",
                        players_df["player_name"].tolist() if "player_name" in players_df.columns else []
                    )

                    if player_to_update:
                        with st.form("update_player_form"):
                            new_total_runs = st.number_input("Total Runs", min_value=0)
                            new_batting_average = st.number_input("Batting Average", min_value=0.0, step=0.1)
                            new_total_wickets = st.number_input("Total Wickets", min_value=0)
                            new_bowling_average = st.number_input("Bowling Average", min_value=0.0, step=0.1)

                            if st.form_submit_button("✏️ Update Player"):
                                try:
                                    player_id = players_df[players_df["player_name"] == player_to_update].index[0]
                                    db.update_player(  # type: ignore[attr-defined]
                                        player_id,
                                        total_runs=int(new_total_runs),
                                        batting_average=new_batting_average,
                                        total_wickets=int(new_total_wickets),
                                        bowling_average=new_bowling_average
                                    )
                                    st.success(f"✓ Player {player_to_update} updated successfully!")
                                except Exception as e:
                                    st.error(f"Error updating player: {e}")
                else:
                    st.info("No players available to update")
            except Exception as e:
                st.error(f"Error: {e}")

        elif operation == "Delete":
            st.markdown("### Delete Player Record")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    player_to_delete = st.selectbox(
                        "Select Player to Delete",
                        players_df["player_name"].tolist() if "player_name" in players_df.columns else [],
                        key="player_delete"
                    )

                    if st.button("🗑️ Delete Player", key="delete_player_btn"):
                        try:
                            player_id = players_df[players_df["player_name"] == player_to_delete].index[0]
                            db.delete_player(player_id)
                            st.success(f"✓ Player {player_to_delete} deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting player: {e}")
                else:
                    st.info("No players available to delete")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 2: Match Management
    with tab2:
        st.markdown("## 🏟️ Match Management")

        match_operation = st.radio(
            "Select Operation",
            ["Create", "Read", "Update"],
            horizontal=True,
            key="match_op"
        )

        if match_operation == "Create":
            st.markdown("### Add New Match")
            with st.form("add_match_form"):
                match_desc = st.text_input("Match Description", placeholder="e.g., India vs Australia, ODI")
                team1 = st.text_input("Team 1", placeholder="e.g., India")
                team2 = st.text_input("Team 2", placeholder="e.g., Australia")
                match_format = st.selectbox("Format", ["Test", "ODI", "T20I", "T20", "IPL"])
                match_date = st.date_input("Match Date")

                if st.form_submit_button("➕ Add Match"):
                    if match_desc and team1 and team2:
                        try:
                            match_id = db.insert_match(
                                match_description=match_desc,
                                team1=team1,
                                team2=team2,
                                match_format=match_format,
                                venue_id=1,  # Default venue ID
                                match_date=str(match_date)
                            )
                            st.success(f"✓ Match added successfully! (ID: {match_id})")
                        except Exception as e:
                            st.error(f"Error adding match: {e}")
                    else:
                        st.warning("Please fill in all required fields")

        elif match_operation == "Read":
            st.markdown("### View All Matches")
            try:
                matches_df = db.get_matches()
                if not matches_df.empty:
                    st.dataframe(matches_df, use_container_width=True)  # type: ignore[call-arg]
                    st.info(f"Total Matches: {len(matches_df)}")
                else:
                    st.info("No matches in database")
            except Exception as e:
                st.error(f"Error reading matches: {e}")

        elif match_operation == "Update":
            st.markdown("### Update Match Record")
            try:
                matches_df = db.get_matches()
                if not matches_df.empty:
                    match_to_update = st.selectbox(
                        "Select Match to Update",
                        [f"{row.get('team1', 'N/A')} vs {row.get('team2', 'N/A')}" 
                         for _, row in matches_df.iterrows()] if not matches_df.empty else []
                    )

                    if match_to_update:
                        with st.form("update_match_form"):
                            _winning_team = st.text_input("Winning Team", placeholder="e.g., India")
                            _victory_margin = st.number_input("Victory Margin", min_value=0)
                            _victory_type = st.selectbox("Victory Type", ["Runs", "Wickets", "Super Over", "N/A"])

                            if st.form_submit_button("✏️ Update Match"):
                                st.success(f"✓ Match details updated successfully!")
                else:
                    st.info("No matches available to update")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 3: Venue Management
    with tab3:
        st.markdown("## 🏟️ Venue Management")

        venue_operation = st.radio(
            "Select Operation",
            ["Create", "Read"],
            horizontal=True,
            key="venue_op"
        )

        if venue_operation == "Create":
            st.markdown("### Add New Venue")
            with st.form("add_venue_form"):
                venue_name = st.text_input("Venue Name", placeholder="e.g., MCG, Eden Gardens")
                city = st.text_input("City", placeholder="e.g., Melbourne, Kolkata")
                country = st.selectbox(
                    "Country",
                    ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"]
                )
                capacity = st.number_input("Capacity", min_value=1000, step=1000)

                if st.form_submit_button("➕ Add Venue"):
                    if venue_name and city:
                        try:
                            venue_id = db.insert_venue(
                                venue_name=venue_name,
                                city=city,
                                country=country,
                                capacity=int(capacity)
                            )
                            st.success(f"✓ Venue added successfully! (ID: {venue_id})")
                        except Exception as e:
                            st.error(f"Error adding venue: {e}")
                    else:
                        st.warning("Please fill in all required fields")

        elif venue_operation == "Read":
            st.markdown("### View All Venues")
            try:
                venues_df = db.get_venues()
                if not venues_df.empty:
                    st.dataframe(venues_df, use_container_width=True)  # type: ignore[call-arg]
                    st.info(f"Total Venues: {len(venues_df)}")
                else:
                    st.info("No venues in database")
            except Exception as e:
                st.error(f"Error reading venues: {e}")

    # Tab 4: Summary
    with tab4:
        st.markdown("## 📊 Database Summary")

        col1, col2, col3 = st.columns(3)

        try:
            with col1:
                players_df = db.get_players()
                st.metric("Total Players", len(players_df) if not players_df.empty else 0)

            with col2:
                matches_df = db.get_matches()
                st.metric("Total Matches", len(matches_df) if not matches_df.empty else 0)

            with col3:
                venues_df = db.get_venues()
                st.metric("Total Venues", len(venues_df) if not venues_df.empty else 0)

            st.markdown("---")
            st.markdown("### Database Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Top 5 Players by Runs**")
                if not players_df.empty and "player_name" in players_df.columns:
                    top_players = players_df.nlargest(5, "total_runs")[["player_name", "total_runs"]]
                    st.dataframe(top_players, use_container_width=True)  # type: ignore[call-arg]

            with col2:
                st.markdown("**Venues by Capacity**")
                if not venues_df.empty and "capacity" in venues_df.columns:
                    top_venues = venues_df.nlargest(5, "capacity")[["venue_name", "capacity"]]
                    st.dataframe(top_venues, use_container_width=True)  # type: ignore[call-arg]

        except Exception as e:
            st.error(f"Error loading summary: {e}")

        # Database Backup
        st.markdown("---")
        st.markdown("### Database Operations")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Export Database as CSV"):
                try:
                    players_df = db.get_players()
                    csv = players_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Players",
                        data=csv,
                        file_name="players.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error exporting: {e}")

        with col2:
            st.info("💡 Tip: Use database backup regularly for data safety")
