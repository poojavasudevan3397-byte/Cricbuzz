"""
Pages module for Cricbuzz LiveStats application
"""

from . import home
from . import live_matches
from . import player_stats
from . import sql_analytics
from . import crud_operations

__all__ = [
    "home",
    "live_matches",
    "player_stats",
    "sql_analytics",
    "crud_operations",
]
