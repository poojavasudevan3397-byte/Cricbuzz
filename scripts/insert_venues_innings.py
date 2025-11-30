# """
# Insert Venues and Innings Data
# Run this script to populate venues and innings tables from matches
# """

# import requests
# import pymysql
# from datetime import datetime
# import json
# import time

# # Database configuration
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'Vasu@76652',
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


# def get_venue_details(venue_id):
#     """Get venue details from API"""
#     url = f"https://{API_HOST}/venues/v1/{venue_id}"
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         return None
#     except Exception as e:
#         print(f"  ✗ Exception for venue {venue_id}: {e}")
#         return None


# def get_match_scorecard(match_id):
#     """Get match scorecard from API"""
#     url = f"https://{API_HOST}/mcenter/v1/{match_id}/scard"
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#         return None
#     except Exception as e:
#         print(f"  ✗ Exception for match {match_id}: {e}")
#         return None


# def parse_overs(overs_str):
#     """Convert overs string to decimal"""
#     if not overs_str:
#         return 0.0
    
#     try:
#         if '.' in str(overs_str):
#             parts = str(overs_str).split('.')
#             overs = int(parts[0])
#             balls = int(parts[1]) if len(parts) > 1 else 0
#             return float(f"{overs}.{balls}")
#         return float(overs_str)
#     except:
#         return 0.0


# def insert_venues():
#     """Insert venues from matches into venues table"""
    
#     conn = pymysql.connect(**DB_CONFIG)
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
    
#     # Get unique venue IDs from matches
#     cursor.execute("""
#         SELECT DISTINCT 
#             SUBSTRING_INDEX(SUBSTRING_INDEX(venue, ',', -1), ',', 1) as venue_name,
#             venue as full_venue
#         FROM matches 
#         WHERE venue IS NOT NULL AND venue != 'N/A'
#         LIMIT 50
#     """)
    
#     venues = cursor.fetchall()
    
#     print(f"\n{'='*60}")
#     print(f"Found {len(venues)} unique venues")
#     print(f"{'='*60}\n")
    
#     inserted_count = 0
    
#     for idx, venue in enumerate(venues, 1):
#         venue_name = venue['venue_name'].strip() if venue['venue_name'] else 'Unknown'
#         full_venue = venue['full_venue']
        
#         # Parse city and country from full venue string
#         parts = [p.strip() for p in full_venue.split(',')]
#         city = parts[1] if len(parts) > 1 else ''
#         country = parts[2] if len(parts) > 2 else ''
        
#         print(f"[{idx}/{len(venues)}] Processing: {venue_name}")
        
#         # Check if venue exists
#         cursor.execute(
#             "SELECT id FROM venues WHERE venue_name = %s",
#             (venue_name,)
#         )
        
#         if cursor.fetchone():
#             print(f"  ⊙ Already exists")
#             continue
        
#         # Insert venue
#         insert_query = """
#             INSERT INTO venues (venue_name, city, country, created_at)
#             VALUES (%s, %s, %s, %s)
#         """
        
#         try:
#             cursor.execute(insert_query, (
#                 venue_name,
#                 city,
#                 country,
#                 datetime.now()
#             ))
#             conn.commit()
#             print(f"  ✓ Inserted: {venue_name}, {city}, {country}")
#             inserted_count += 1
#         except Exception as e:
#             print(f"  ✗ Error inserting: {e}")
#             conn.rollback()
    
#     cursor.close()
#     conn.close()
    
#     print(f"\n{'='*60}")
#     print(f"Venue Insert Complete!")
#     print(f"✓ Successfully inserted: {inserted_count} venues")
#     print(f"{'='*60}\n")


# def insert_innings():
#     """Insert innings data from matches"""
    
#     conn = pymysql.connect(**DB_CONFIG)
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
    
#     # Get all matches
#     cursor.execute("""
#         SELECT external_match_id, team1, team2 
#         FROM matches 
#         LIMIT 20
#     """)
    
#     matches = cursor.fetchall()
    
#     print(f"\n{'='*60}")
#     print(f"Processing innings for {len(matches)} matches")
#     print(f"{'='*60}\n")
    
#     inserted_count = 0
#     failed_count = 0
    
#     for idx, match in enumerate(matches, 1):
#         match_id = match['external_match_id']
#         print(f"[{idx}/{len(matches)}] Processing match: {match_id}")
        
#         # Get scorecard
#         scorecard = get_match_scorecard(match_id)
        
#         if not scorecard or 'scoreCard' not in scorecard:
#             print(f"  ✗ No scorecard available")
#             failed_count += 1
#             time.sleep(0.5)
#             continue
        
#         innings_list = scorecard.get('scoreCard', [])
        
#         for inning in innings_list:
#             innings_id = inning.get('inningsId', 0)
#             batting_team = inning.get('batTeamDetails', {}).get('batTeamName', '')
#             bowling_team = inning.get('bowlTeamDetails', {}).get('bowlTeamName', '')
            
#             # Get score details
#             score_details = inning.get('scoreDetails', {})
#             runs = score_details.get('runs', 0)
#             wickets = score_details.get('wickets', 0)
#             overs_str = score_details.get('overs', '0')
#             overs = parse_overs(overs_str)
            
#             # Calculate extras
#             extras_data = inning.get('extrasData', {})
#             extras = json.dumps(extras_data)
            
#             # Create meta JSON
#             meta = json.dumps({
#                 'run_rate': score_details.get('runRate', 0),
#                 'declared': score_details.get('isDeclared', False),
#                 'follow_on': score_details.get('isFollowOn', False)
#             })
            
#             # Check if innings exists
#             cursor.execute(
#                 "SELECT id FROM innings WHERE external_match_id = %s AND innings_id = %s",
#                 (match_id, innings_id)
#             )
            
#             if cursor.fetchone():
#                 continue
            
#             # Insert innings
#             insert_query = """
#                 INSERT INTO innings 
#                 (external_match_id, innings_id, batting_team, bowling_team, runs, wickets, overs, extras, meta, created_at)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
            
#             try:
#                 cursor.execute(insert_query, (
#                     match_id,
#                     innings_id,
#                     batting_team,
#                     bowling_team,
#                     runs,
#                     wickets,
#                     overs,
#                     extras,
#                     meta,
#                     datetime.now()
#                 ))
#                 conn.commit()
#                 print(f"  ✓ Innings {innings_id}: {batting_team} - {runs}/{wickets} in {overs} overs")
#                 inserted_count += 1
#             except Exception as e:
#                 print(f"  ✗ Error inserting innings: {e}")
#                 conn.rollback()
#                 failed_count += 1
        
#         time.sleep(0.5)  # Rate limiting
    
#     cursor.close()
#     conn.close()
    
#     print(f"\n{'='*60}")
#     print(f"Innings Insert Complete!")
#     print(f"✓ Successfully inserted: {inserted_count} innings")
#     print(f"✗ Failed: {failed_count} innings")
#     print(f"{'='*60}\n")


# def main():
#     """Main execution"""
#     print("\n" + "="*60)
#     print("Venues and Innings Data Insert Script")
#     print("="*60 + "\n")
    
#     choice = input("Select operation:\n1. Insert Venues\n2. Insert Innings\n3. Both\n\nChoice (1/2/3): ")
    
#     if choice in ['1', '3']:
#         insert_venues()
    
#     if choice in ['2', '3']:
#         insert_innings()


# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\n\n⚠️  Script interrupted by user")
#     except Exception as e:
#         print(f"\n\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()