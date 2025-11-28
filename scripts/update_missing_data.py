"""
Update Missing Player Data (DOB, Country, Role)
Run this script to fetch and update missing player information from Cricbuzz API
"""

import requests
import pymysql
from datetime import datetime
import json
import time

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'database': 'cricketdb',
    'port': 3306
}
from typing import Any, Dict, List, Optional, Union, cast

# API configuration
API_KEY = "ecac4e6684msha1c5e893e7d1dd7p10b374jsn02fa652ff3d3"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}


def get_player_details(player_id):
    """Get detailed player information from API"""
    url = f"https://{API_HOST}/stats/v1/player/{player_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ✗ API Error {response.status_code} for player {player_id}")
            return None
    except Exception as e:
        print(f"  ✗ Exception for player {player_id}: {e}")
        return None


def parse_player_role(meta_json):
    """Determine player role from batting/bowling styles"""
    try:
        if isinstance(meta_json, str):
            meta = json.loads(meta_json)
        else:
            meta = meta_json
            
        bat_style = meta.get('batting_style', '')
        bowl_style = meta.get('bowling_style', '')
        
        has_batting = bat_style and bat_style.strip() and bat_style.lower() not in ['none', 'n/a', '']
        has_bowling = bowl_style and bowl_style.strip() and bowl_style.lower() not in ['none', 'n/a', '']
        
        # Check for wicket-keeper
        if bat_style and 'wicket' in bat_style.lower():
            return "Wicket-keeper"
        if bowl_style and 'wicket' in bowl_style.lower():
            return "Wicket-keeper"
        
        # Determine role
        if has_batting and has_bowling:
            return "All-rounder"
        elif has_batting:
            return "Batsman"
        elif has_bowling:
            return "Bowler"
        else:
            return "Batsman"  # Default
            
    except Exception as e:
        print(f"  ✗ Error parsing role: {e}")
        return "Batsman"


def update_players_data():
    """Update all players with missing DOB, country, and role"""
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Get all players with missing data
    query = """
        SELECT id, external_player_id, player_name, date_of_birth, country, role, meta 
        FROM players 
        WHERE date_of_birth IS NULL OR country = '' OR country IS NULL OR role = '' OR role IS NULL
        LIMIT 100
    """
    
    cursor.execute(query)
    players = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"Found {len(players)} players with missing data")
    print(f"{'='*60}\n")
    
    updated_count = 0
    failed_count = 0
    
    for idx, player in enumerate(players, 1):
        print(f"[{idx}/{len(players)}] Processing: {player['player_name']} (ID: {player['external_player_id']})")
        
        # Get player details from API
        player_data = get_player_details(player['external_player_id'])
        
        if not player_data:
            print(f"  ✗ Could not fetch data")
            failed_count += 1
            time.sleep(0.5)  # Rate limiting
            continue
        
        # Extract data
        dob = player_data.get('dateOfBirth') or player_data.get('dob') or player_data.get('birthDate')
        country = player_data.get('country') or player_data.get('nationality') or player['country']
        
        # Parse role from meta
        role = player['role']
        if not role or role == '':
            role = parse_player_role(player['meta'] if player['meta'] else '{}')
        
        # Update the database
        update_query = """
            UPDATE players 
            SET date_of_birth = %s, country = %s, role = %s
            WHERE id = %s
        """
        
        try:
            cursor.execute(update_query, (dob, country, role, player['id']))
            conn.commit()
            print(f"  ✓ Updated: DOB={dob}, Country={country}, Role={role}")
            updated_count += 1
        except Exception as e:
            print(f"  ✗ Error updating: {e}")
            conn.rollback()
            failed_count += 1
        
        # Rate limiting
        time.sleep(0.3)
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Update Complete!")
    print(f"{'='*60}")
    print(f"✓ Successfully updated: {updated_count} players")
    print(f"✗ Failed: {failed_count} players")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Player Data Update Script")
    print("Updating missing DOB, Country, and Role")
    print("="*60 + "\n")
    
    try:
        update_players_data()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()