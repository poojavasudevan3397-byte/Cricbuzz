# """
# Update Missing Player Data (DOB, Country, Role)
# Run this script to fetch and update missing player information from Cricbuzz API
# """

# from typing import Any, Dict, List, Optional, Union, TypedDict, cast

# import json
# import time
# import requests
# import pymysql


# class DBConfig(TypedDict):
#     host: str
#     user: str
#     password: str
#     database: str
#     port: int


# # Database configuration
# DB_CONFIG: DBConfig = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'Vasu@76652',
#     'database': 'cricketdb',
#     'port': 3306,
# }


# # API configuration
# API_KEY = "ecac4e6684msha1c5e893e7d1dd7p10b374jsn02fa652ff3d3"
# API_HOST = "cricbuzz-cricket.p.rapidapi.com"

# headers: Dict[str, str] = {
#     "x-rapidapi-key": API_KEY,
#     "x-rapidapi-host": API_HOST,
# }


# def get_player_details(player_id: Union[str, int]) -> Optional[Dict[str, Any]]:
#     """Get detailed player information from API"""
#     url = f"https://{API_HOST}/stats/v1/player/{player_id}"

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"  ✗ API Error {response.status_code} for player {player_id}")
#             return None
#     except Exception as e:
#         print(f"  ✗ Exception for player {player_id}: {e}")
#         return None


# def parse_player_role(meta_json: Any) -> str:
#     """Determine player role from batting/bowling styles

#     meta_json may be a JSON string or a dict-like object with keys
#     `batting_style` and `bowling_style`.
#     """
#     try:
#         if isinstance(meta_json, str):
#             meta = json.loads(meta_json)
#         else:
#             meta = cast(Dict[str, Any], meta_json)

#         bat_style = meta.get('batting_style', '')
#         bowl_style = meta.get('bowling_style', '')

#         bat_style_str = str(bat_style) if bat_style is not None else ''
#         bowl_style_str = str(bowl_style) if bowl_style is not None else ''

#         has_batting = bool(bat_style_str and bat_style_str.strip() and bat_style_str.lower() not in ['none', 'n/a', ''])
#         has_bowling = bool(bowl_style_str and bowl_style_str.strip() and bowl_style_str.lower() not in ['none', 'n/a', ''])

#         # Check for wicket-keeper
#         if 'wicket' in bat_style_str.lower():
#             return "Wicket-keeper"
#         if 'wicket' in bowl_style_str.lower():
#             return "Wicket-keeper"

#         # Determine role
#         if has_batting and has_bowling:
#             return "All-rounder"
#         if has_batting:
#             return "Batsman"
#         if has_bowling:
#             return "Bowler"
#         return "Batsman"

#     except Exception as e:
#         print(f"  ✗ Error parsing role: {e}")
#         return "Batsman"


# def update_players_data() -> None:
#     """Update all players with missing DOB, country, and role"""

#     conn: Any = pymysql.connect(**DB_CONFIG)
#     cursor: Any = conn.cursor(pymysql.cursors.DictCursor)

#     # Get all players with missing data
#     query = """
#         SELECT id, external_player_id, player_name, date_of_birth, country, role, meta
#         FROM players
#         WHERE date_of_birth IS NULL OR country = '' OR country IS NULL OR role = '' OR role IS NULL
#         LIMIT 100
#     """

#     cursor.execute(query)
#     players: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cursor.fetchall())

#     print(f"\n{'='*60}")
#     print(f"Found {len(players)} players with missing data")
#     print(f"{'='*60}\n")

#     updated_count = 0
#     failed_count = 0

#     for idx, player in enumerate(players, 1):
#         player = cast(Dict[str, Any], player)
#         print(f"[{idx}/{len(players)}] Processing: {player.get('player_name')} (ID: {player.get('external_player_id')})")

#         # Get player details from API
#         pid = player.get('external_player_id')
#         if pid is None:
#             print(f"  ✗ No external_player_id for record, skipping")
#             failed_count += 1
#             continue

#         player_data = get_player_details(pid)

#         if not player_data:
#             print(f"  ✗ Could not fetch data")
#             failed_count += 1
#             time.sleep(0.5)  # Rate limiting
#             continue

#         # Extract data
#         dob = player_data.get('dateOfBirth') or player_data.get('dob') or player_data.get('birthDate')
#         country = player_data.get('country') or player_data.get('nationality') or player.get('country')

#         # Parse role from meta
#         role = player.get('role') or ''
#         if not role:
#             role = parse_player_role(player.get('meta', '{}'))

#         # Update the database
#         update_query = """
#             UPDATE players
#             SET date_of_birth = %s, country = %s, role = %s
#             WHERE id = %s
#         """

#         try:
#             cursor.execute(update_query, (dob, country, role, player.get('id')))
#             conn.commit()
#             print(f"  ✓ Updated: DOB={dob}, Country={country}, Role={role}")
#             updated_count += 1
#         except Exception as e:
#             print(f"  ✗ Error updating: {e}")
#             conn.rollback()
#             failed_count += 1

#         # Rate limiting
#         time.sleep(0.3)

#     cursor.close()
#     conn.close()

#     print(f"\n{'='*60}")
#     print(f"Update Complete!")
#     print(f"{'='*60}")
#     print(f"✓ Successfully updated: {updated_count} players")
#     print(f"✗ Failed: {failed_count} players")
#     print(f"{'='*60}\n")


# if __name__ == "__main__":
#     print("\n" + "="*60)
#     print("Player Data Update Script")
#     print("Updating missing DOB, Country, and Role")
#     print("="*60 + "\n")

#     try:
#         update_players_data()
#     except KeyboardInterrupt:
#         print("\n\n⚠️  Script interrupted by user")
#     except Exception as e:
#         print(f"\n\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()
# """
# Update Missing Player Data (DOB, Country, Role)
# Run this script to fetch and update missing player information from Cricbuzz API
# """

# import requests
# import pymysql
# from datetime import datetime
# import json
# import time
# from typing import Any, Dict, List, Optional, Union, TypedDict, cast
# # Database configuration
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'database': 'cricketdb',
#     'port': 3306
# }


# # API configuration
# API_KEY = "ecac4e6684msha1c5e893e7d1dd7p10b374jsn02fa652ff3d3"
# API_HOST = "cricbuzz-cricket.p.rapidapi.com"

# headers = {
#     "x-rapidapi-key": API_KEY,
#     "x-rapidapi-host": API_HOST
# }


# def get_player_details(player_id):
#     """Get detailed player information from API"""
#     url = f"https://{API_HOST}/stats/v1/player/{player_id}"
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print(f"  ✗ API Error {response.status_code} for player {player_id}")
#             return None
#     except Exception as e:
#         print(f"  ✗ Exception for player {player_id}: {e}")
#         """
#         Update Missing Player Data (DOB, Country, Role)
#         Run this script to fetch and update missing player information from Cricbuzz API
#         """

#         from typing import Any, Dict, List, Optional, Union, cast

#         import json
#         import time
#         import requests
#         import pymysql

#         # Database configuration


#         class DBConfig(TypedDict):
#             host: str
#             user: str
#             password: str
#             database: str
#             port: int


#         DB_CONFIG: DBConfig = {
#             'host': 'localhost',
#             'user': 'root',
#             'password': 'Vasu@76652',
#             'database': 'cricketdb',
#             'port': 3306,
#         }

#         # API configuration
#         API_KEY = "ecac4e6684msha1c5e893e7d1dd7p10b374jsn02fa652ff3d3"
#         API_HOST = "cricbuzz-cricket.p.rapidapi.com"

#         headers: Dict[str, str] = {
#             "x-rapidapi-key": API_KEY,
#             "x-rapidapi-host": API_HOST,
#         }


#         def get_player_details(player_id: Union[str, int]) -> Optional[Dict[str, Any]]:
#             """Get detailed player information from API"""
#             url = f"https://{API_HOST}/stats/v1/player/{player_id}"

#             try:
#                 response = requests.get(url, headers=headers, timeout=10)
#                 if response.status_code == 200:
#                     return response.json()
#                 else:
#                     print(f"  ✗ API Error {response.status_code} for player {player_id}")
#                     return None
#             except Exception as e:
#                 print(f"  ✗ Exception for player {player_id}: {e}")
#                 return None


#         def parse_player_role(meta_json: Any) -> str:
#             """Determine player role from batting/bowling styles

#             meta_json may be a JSON string or a dict-like object with keys
#             `batting_style` and `bowling_style`.
#             """
#             try:
#                 if isinstance(meta_json, str):
#                     meta = json.loads(meta_json)
#                 else:
#                     meta = cast(Dict[str, Any], meta_json)

#                 bat_style = meta.get('batting_style', '')
#                 bowl_style = meta.get('bowling_style', '')

#                 bat_style_str = str(bat_style) if bat_style is not None else ''
#                 bowl_style_str = str(bowl_style) if bowl_style is not None else ''

#                 has_batting = bool(bat_style_str and bat_style_str.strip() and bat_style_str.lower() not in ['none', 'n/a', ''])
#                 has_bowling = bool(bowl_style_str and bowl_style_str.strip() and bowl_style_str.lower() not in ['none', 'n/a', ''])

#                 # Check for wicket-keeper
#                 if 'wicket' in bat_style_str.lower():
#                     return "Wicket-keeper"
#                 if 'wicket' in bowl_style_str.lower():
#                     return "Wicket-keeper"

#                 # Determine role
#                 if has_batting and has_bowling:
#                     return "All-rounder"
#                 if has_batting:
#                     return "Batsman"
#                 if has_bowling:
#                     return "Bowler"
#                 return "Batsman"

#             except Exception as e:
#                 print(f"  ✗ Error parsing role: {e}")
#                 return "Batsman"


#         def update_players_data() -> None:
#             """Update all players with missing DOB, country, and role"""

#             conn: Any = pymysql.connect(**DB_CONFIG)
#             cursor: Any = conn.cursor(pymysql.cursors.DictCursor)

#             # Get all players with missing data
#             query = """
#                 SELECT id, external_player_id, player_name, date_of_birth, country, role, meta
#                 FROM players
#                 WHERE date_of_birth IS NULL OR country = '' OR country IS NULL OR role = '' OR role IS NULL
#                 LIMIT 100
#             """

#             cursor.execute(query)
#             players: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cursor.fetchall())

#             print(f"\n{'='*60}")
#             print(f"Found {len(players)} players with missing data")
#             print(f"{'='*60}\n")

#             updated_count = 0
#             failed_count = 0

#             for idx, player in enumerate(players, 1):
#                 player = cast(Dict[str, Any], player)
#                 print(f"[{idx}/{len(players)}] Processing: {player.get('player_name')} (ID: {player.get('external_player_id')})")

#                 # Get player details from API
#                 player_data = get_player_details(player.get('external_player_id'))

#                 if not player_data:
#                     print(f"  ✗ Could not fetch data")
#                     failed_count += 1
#                     time.sleep(0.5)  # Rate limiting
#                     continue

#                 # Extract data
#                 dob = player_data.get('dateOfBirth') or player_data.get('dob') or player_data.get('birthDate')
#                 country = player_data.get('country') or player_data.get('nationality') or player.get('country')

#                 # Parse role from meta
#                 role = player.get('role') or ''
#                 if not role:
#                     role = parse_player_role(player.get('meta', '{}'))

#                 # Update the database
#                 update_query = """
#                     UPDATE players
#                     SET date_of_birth = %s, country = %s, role = %s
#                     WHERE id = %s
#                 """

#                 try:
#                     cursor.execute(update_query, (dob, country, role, player.get('id')))
#                     conn.commit()
#                     print(f"  ✓ Updated: DOB={dob}, Country={country}, Role={role}")
#                     updated_count += 1
#                 except Exception as e:
#                     print(f"  ✗ Error updating: {e}")
#                     conn.rollback()
#                     failed_count += 1

#                 # Rate limiting
#                 time.sleep(0.3)

#             cursor.close()
#             conn.close()

#             print(f"\n{'='*60}")
#             print(f"Update Complete!")
#             print(f"{'='*60}")
#             print(f"✓ Successfully updated: {updated_count} players")
#             print(f"✗ Failed: {failed_count} players")
#             print(f"{'='*60}\n")


#         if __name__ == "__main__":
#             print("\n" + "="*60)
#             print("Player Data Update Script")
#             print("Updating missing DOB, Country, and Role")
#             print("="*60 + "\n")

#             try:
#                 update_players_data()
#             except KeyboardInterrupt:
#                 print("\n\n⚠️  Script interrupted by user")
#             except Exception as e:
#                 print(f"\n\n❌ Fatal error: {e}")
#                 import traceback
#                 traceback.print_exc()