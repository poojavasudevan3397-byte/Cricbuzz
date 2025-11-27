from cricbuzz_app.utils.db_connection import DatabaseConnection

# Use local sqlite in-memory

db = DatabaseConnection(db_type='sqlite', db_path=':memory:')
db.init_schema()
# insert sample player (provide all required arguments)
pid: int = db.insert_player(
	team_id=1,
	player_name='Test Player',
	country='India',
	role='Batsman',
	batting_style='Right-hand',
	bowling_style='Right-arm',
	meta=''
)
print('Inserted player id:', pid)
cur = db.connection.cursor()  # type: ignore[attr-defined]
cur.execute(
	'SELECT player_name, country, role, batting_style, bowling_style FROM players WHERE player_id=?',
	(pid,)
)
row = cur.fetchone()
print('Row:', row)
