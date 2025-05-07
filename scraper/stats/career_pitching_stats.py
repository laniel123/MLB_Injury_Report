import sqlite3
import requests
from bs4 import BeautifulSoup
import os

# Database path
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure the table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS career_pitching_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mlb_player_id TEXT,
    season TEXT,
    team TEXT,
    league TEXT,
    wins INTEGER,
    losses INTEGER,
    earned_run_average TEXT,
    games INTEGER,
    games_started INTEGER,
    saves INTEGER,
    save_opportunities INTEGER,
    innings_pitched REAL,
    hits INTEGER,
    runs INTEGER,
    earned_runs INTEGER,
    home_runs INTEGER,
    walks INTEGER,
    strikeouts INTEGER,
    whip TEXT,
    opposing_batting_average TEXT
)
''')

# Target URL
url = 'https://www.mlb.com/player/shohei-ohtani-660271'  # ← replace with the actual page link
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table body
table = soup.find('table')
if table:
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')

        for row in rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]

            if len(cells) < 19:
                print("⚠️ Skipping row with insufficient data")
                continue

            try:
                (
                    season, team, league, wins, losses, era, games, games_started,
                    complete_games, saves, save_opportunities, innings_pitched,
                    hits, runs, earned_runs, home_runs, walks, strikeouts,
                    whip, opp_avg
                ) = cells[:20]

                mlb_player_id = 'UNKNOWN'  # You may replace or extract if available

                # Check for duplicates (season + team + league)
                cursor.execute('''
                    SELECT COUNT(*) FROM career_pitching_stats
                    WHERE mlb_player_id = ? AND season = ? AND team = ? AND league = ?
                ''', (mlb_player_id, season, team, league))

                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO career_pitching_stats (
                            mlb_player_id, season, team, league, wins, losses,
                            earned_run_average, games, games_started, saves,
                            save_opportunities, innings_pitched, hits, runs,
                            earned_runs, home_runs, walks, strikeouts, whip,
                            opposing_batting_average
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        mlb_player_id, season, team, league, int(wins), int(losses),
                        era, int(games), int(games_started), int(saves), int(save_opportunities),
                        float(innings_pitched), int(hits), int(runs), int(earned_runs),
                        int(home_runs), int(walks), int(strikeouts), whip, opp_avg
                    ))
                    print(f"✅ Inserted stats for {season} | {team} | {league}")
                else:
                    print(f"⏩ Skipping duplicate for {season} | {team} | {league}")

            except Exception as e:
                print(f"⚠️ Error inserting row: {e}")

    else:
        print("❌ No <tbody> found in the table")
else:
    print("❌ No <table> found on the page")

conn.commit()
conn.close()

print('✅ All pitching stats scraped and inserted!')