
import requests
import sqlite3
from datetime import datetime


def game_logs(db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'):

    # Connect to SQLite DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure game_logs table exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_logs (
        mlb_player_id TEXT,
        game_date TEXT,
        team TEXT,
        opponent TEXT,
        ab INTEGER,
        r INTEGER,
        h INTEGER,
        tb INTEGER,
        doubles INTEGER,
        triples INTEGER,
        hr INTEGER,
        rbi INTEGER,
        bb INTEGER,
        ibb INTEGER,
        so INTEGER,
        sb INTEGER,
        cs INTEGER,
        avg REAL,
        obp REAL,
        slg REAL,
        hbp INTEGER,
        sac INTEGER,
        sf INTEGER,
        PRIMARY KEY (mlb_player_id, game_date)
    );
    ''')

    # Load all players from the database
    players_df = cursor.execute("SELECT mlb_player_id FROM players").fetchall()
    players = [str(row[0]) for row in players_df]

    for mlb_id in players:
        url = f"https://statsapi.mlb.com/api/v1/people/{mlb_id}/stats?stats=gameLog&season=2025"
        print(f"Fetching game logs for player {mlb_id}...")

        try:
            response = requests.get(url)
            data = response.json()
            splits = data["stats"][0]["splits"]
        except Exception as e:
            print(f"Error fetching logs for player {mlb_id}: {e}")
            continue

        # Get the most recent game_date stored for this player
        cursor.execute("SELECT MAX(game_date) FROM game_logs WHERE mlb_player_id = ?", (mlb_id,))
        last_date = cursor.fetchone()[0]
        last_date = datetime.strptime(last_date, "%Y-%m-%d").date() if last_date else None

        new_logs = 0
        for game in splits:
            stat = game["stat"]
            date_str = game["date"]
            game_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Skip if already recorded
            if last_date and game_date <= last_date:
                continue

            team_info = game.get("team", {})
            opponent_info = game.get("opponent", {})

            team = team_info.get("abbreviation") or team_info.get("name", "")
            opponent = opponent_info.get("abbreviation") or opponent_info.get("name", "")

            cursor.execute('''
                INSERT OR IGNORE INTO game_logs (
                    mlb_player_id, game_date, team, opponent, ab, r, h, tb, doubles, triples,
                    hr, rbi, bb, ibb, so, sb, cs, avg, obp, slg, hbp, sac, sf
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mlb_id,
                date_str,
                team,
                opponent,
                stat.get("atBats", 0),
                stat.get("runs", 0),
                stat.get("hits", 0),
                stat.get("totalBases", 0),
                stat.get("doubles", 0),
                stat.get("triples", 0),
                stat.get("homeRuns", 0),
                stat.get("rbi", 0),
                stat.get("baseOnBalls", 0),
                stat.get("intentionalWalks", 0),
                stat.get("strikeOuts", 0),
                stat.get("stolenBases", 0),
                stat.get("caughtStealing", 0),
                float(stat.get("avg", 0.0)) if stat.get("avg") else None,
                float(stat.get("obp", 0.0)) if stat.get("obp") else None,
                float(stat.get("slg", 0.0)) if stat.get("slg") else None,
                stat.get("hitByPitch", 0),
                stat.get("sacBunts", 0),
                stat.get("sacFlies", 0)
            ))
            new_logs += 1

        conn.commit()
        print(f"Inserted {new_logs} new logs for player {mlb_id}")

    conn.close()