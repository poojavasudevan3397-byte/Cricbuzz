"""
🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A comprehensive cricket analytics dashboard integrating live data from the Cricbuzz API
with SQL database for real-time match updates, player statistics, and advanced analytics.

Author: Cricket Analytics Team
Version: 1.0
"""

import streamlit as st  # type: ignore[reportUnknownMemberType]
from typing import Any, cast

# Cast Streamlit to Any to avoid Pylance "unknown member type" diagnostics
st = cast(Any, st)
try:
    from streamlit_option_menu import option_menu  # type: ignore[import-untyped]
except Exception:
    # Lightweight fallback when streamlit_option_menu isn't installed.
    # This preserves basic behavior by returning the selected option using a radio.
    from typing import Any

    def option_menu(menu_title: str | None = None,
                    options: list[str] | None = None,
                    icons: list[str] | None = None,
                    menu_icon: str | None = None,
                    default_index: int = 0,
                    styles: dict[str, Any] | None = None,
                    **kwargs: Any) -> str:
        # If a title is provided, show it; otherwise keep compact control
        if menu_title:
            try:
                st.markdown(f"## {menu_title}")
            except Exception:
                pass
        opts: list[str] = list(options) if options else []
        # Use a stable key to avoid collisions; include provided menu_title when possible
        title_snip = (menu_title or "")[:50]
        key = f"option_menu_fallback_{title_snip}"
        try:
            return cast(str, st.radio("", opts, index=default_index, key=key))
        except Exception:
            # As a last resort, return the default selected option
            return opts[default_index] if opts else ""

# Configure page layout
st.set_page_config(
    page_title="🏏 Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 20px;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab-list"] button:focus {
        color: #1f77b4;
    }
    .page-title {
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title
st.markdown(
    """
    <div class="main-header">
    <h1>🏏 Cricbuzz LiveStats</h1>
    <p>Real-Time Cricket Insights & SQL-Based Analytics</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar Navigation
with st.sidebar:
    st.markdown("## Navigation")
    selected: str = option_menu(  # type: ignore[assignment]
        menu_title=None,
        options=[
            "⚡ Live Matches",
            "📊 Player Stats",
            "🔍 SQL Analytics",
            "🛠️ CRUD Operations",
        ],
        icons=["lightning-fill", "bar-chart", "search", "tools"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#1f77b4", "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#1f77b4"},
        },
    )

# Route to appropriate page
if selected == "⚡ Live Matches":
    from pages import live_matches
    live_matches.show()
elif selected == "📊 Player Stats":
    from pages import player_stats
    player_stats.show()
elif selected == "🔍 SQL Analytics":
    from pages import sql_analytics
    sql_analytics.show()
elif selected == "🛠️ CRUD Operations":
    from pages import crud_operations
    crud_operations.show()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
    <p>🏏 Cricbuzz LiveStats © 2025 | Cricket Analytics Dashboard</p>
    <p>Built with Python • Streamlit • SQL • REST API</p>
    </div>
    """,
    unsafe_allow_html=True,
)
