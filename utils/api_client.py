"""
Cricbuzz API Integration Module
Handles all API calls to Cricbuzz Cricket API via RapidAPI
"""

import requests
import streamlit as st
from typing import Dict, Any, List, cast

# Treat Streamlit's dynamic members as Any so Pylance won't warn about
# unknown member types like `markdown`, `warning`, `cache_resource`, etc.
st = cast(Any, st)

class CricbuzzAPI:
    """Interface for Cricbuzz Cricket API"""

    def __init__(self, api_key: str):
        """Initialize API client with RapidAPI key"""
        self.api_key = api_key
        self.api_host = "cricbuzz-cricket.p.rapidapi.com"
        self.base_url = f"https://{self.api_host}"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": self.api_host,
        }
        self.timeout = 10

    def get_live_matches(self) -> Dict[str, Any]:
        """Fetch live matches"""
        try:
            url = f"{self.base_url}/matches/v1/live"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Use the exception variable so static analyzers see it's accessed
            st.error(f"Failed to fetch live matches: {e}")
            return {}

    def get_upcoming_matches(self) -> Dict[str, Any]:
        """Fetch upcoming matches"""
        try:
            url = f"{self.base_url}/matches/v1/upcoming"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch upcoming matches: {e}")
            return {}

    def get_recent_matches(self) -> Dict[str, Any]:
        """Fetch recent matches"""
        try:
            url = f"{self.base_url}/matches/v1/recent"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch recent matches: {e}")
            return {}

    def get_scorecard(self, match_id: str) -> Dict[str, Any]:
        """Fetch scorecard for a specific match"""
        try:
            url = f"{self.base_url}/mcenter/v1/{match_id}/scard"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.warning(f"Failed to fetch scorecard for match {match_id}: {e}")
            return {}

    def get_series(self) -> Dict[str, Any]:
        """Fetch cricket series information"""
        try:
            url = f"{self.base_url}/series/v1"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch series: {e}")
            return {}


@st.cache_resource
def get_api_client(api_key: str) -> CricbuzzAPI:
    """Get cached API client instance"""
    return CricbuzzAPI(api_key)


def normalize_matches(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize API response into a flat list of matches
    
    Args:
        data: Raw API response
        
    Returns:
        List of normalized match dictionaries
    """
    matches: List[Dict[str, Any]] = []
    
    for type_match in data.get('typeMatches', []):
        match_type = type_match.get('matchType', 'Unknown')
        
        for series in type_match.get('seriesMatches', []):
            if 'ad' in series:
                continue
                
            wrapper = series.get('seriesAdWrapper', series)
            series_name = wrapper.get('seriesName', 'N/A')
            series_id = wrapper.get('seriesId', '')
            
            for match in wrapper.get('matches', []):
                match_info = match.get('matchInfo', {})
                match_score = match.get('matchScore', {})
                
                team1 = match_info.get('team1', {})
                team2 = match_info.get('team2', {})
                venue = match_info.get('venueInfo', {})
                
                t1_score = match_score.get('team1Score', {})
                t2_score = match_score.get('team2Score', {})
                
                match_data: Dict[str, Any] = {
                    'matchType': match_type,
                    'seriesId': series_id,
                    'seriesName': series_name,
                    'matchId': match_info.get('matchId', ''),
                    'matchDesc': match_info.get('matchDesc', ''),
                    'matchFormat': match_info.get('matchFormat', ''),
                    'startDate': match_info.get('startDate'),
                    'endDate': match_info.get('endDate'),
                    'state': match_info.get('state', 'N/A'),
                    'status': match_info.get('status', 'N/A'),
                    'team1_name': team1.get('teamName', 'N/A'),
                    'team2_name': team2.get('teamName', 'N/A'),
                    'team1_short': team1.get('teamSName', ''),
                    'team2_short': team2.get('teamSName', ''),
                    'team1_id': team1.get('teamId', ''),
                    'team2_id': team2.get('teamId', ''),
                    'venue': venue.get('ground', 'N/A'),
                    'city': venue.get('city', 'N/A'),
                    'country': venue.get('country', 'N/A'),
                    'team1_score': t1_score.get('inngs1', {}).get('runs', 'N/A'),
                    'team1_wickets': t1_score.get('inngs1', {}).get('wickets', 'N/A'),
                    'team1_overs': t1_score.get('inngs1', {}).get('overs', 'N/A'),
                    'team2_score': t2_score.get('inngs1', {}).get('runs', 'N/A'),
                    'team2_wickets': t2_score.get('inngs1', {}).get('wickets', 'N/A'),
                    'team2_overs': t2_score.get('inngs1', {}).get('overs', 'N/A'),
                }
                
                matches.append(match_data)  # type: ignore[attr-defined]
    
    return matches
