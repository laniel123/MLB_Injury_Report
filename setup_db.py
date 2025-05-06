import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect('data/dodgers_injury_db.sqlite')
cursor = connection.cursor()

# Create the injuries table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS injuries (
    injury_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT,
    injury_type TEXT,
    il_type TEXT,
    injury_start DATE,
    injury_end DATE,
    notes TEXT
);
''')

# Commit changes and close the connection
connection.commit()
connection.close()

