"""
Home Page - Project Overview and Navigation
"""

import streamlit as st
from typing import Any, cast

# Help Pylance by treating Streamlit as Any for dynamic members like `markdown`
st = cast(Any, st)


def show():
    """Display home page"""
    st.markdown("<h1 class='page-title'>🏏 Welcome to Cricbuzz LiveStats</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """
        Welcome to the Cricket Analytics Dashboard!
        
        Use the sidebar menu to navigate through different sections.
        """
    )


