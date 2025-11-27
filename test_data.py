from utils.db_connection import get_db_connection
import pandas as pd

db = get_db_connection()
conn = db.connection

# Query with explicit column types
df = pd.read_sql('SELECT player_id, player_name, runs_scored FROM batting_agg LIMIT 5', conn)
print("Columns:", df.columns.tolist())
print("\nData types:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df)
print("\nData sample:")
for i, row in df.iterrows():
    print(f"Row {i}: player_id={row['player_id']}, player_name={row['player_name']}, runs={row['runs_scored']}")
