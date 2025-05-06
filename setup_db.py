import sqlite3
import os

# Make sure the 'data' folder exists
os.makedirs('data', exist_ok=True)

# Connect to the DB (creates it if it doesn't exist)
db_path = 'data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create players table
cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    position TEXT,
    team TEXT,
    dob DATE,
    bats TEXT,
    throws TEXT
    weight INTEGER
)
''')

# Create injuries table
cursor.execute('''
CREATE TABLE IF NOT EXISTS injuries (
    injury_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    injury_type TEXT,
    il_type TEXT,
    injury_start DATE,
    injury_end DATE,
    notes TEXT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
''')

# Create games table
cursor.execute('''
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    opponent TEXT,
    home_away TEXT,
    result TEXT,
    temp INTEGER,
    humidity INTEGER
)
''')

# Create player_game_stats table
cursor.execute('''
CREATE TABLE IF NOT EXISTS player_game_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    game_id INTEGER,
    pitch_count INTEGER,
    innings_pitched REAL,
    sprint_speed REAL,
    distance_run REAL,
    exit_velocity REAL,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
)
''')

# Create risk_scores table
cursor.execute('''
CREATE TABLE IF NOT EXISTS risk_scores (
    risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    game_id INTEGER,
    risk_score REAL,
    risk_level TEXT,
    date_calculated DATE,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
)
''')

conn.commit()
conn.close()

print(f"Database '{db_path}' has been set up and is ready for use!")