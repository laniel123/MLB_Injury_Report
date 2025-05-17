

import requests
import sqlite3

def fetch_and_store_player_stats(player_id, season="2024", db_path="/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/mlb_players.db"):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {
        "stats": "season,career,gameLog",
        "group": "hitting,pitching,fielding",
        "season": season
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Failed to fetch stats for player {player_id}")
        return

    data = response.json()
    stats_entries = data.get("stats", [])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            player_id INTEGER,
            type TEXT,
            group_type TEXT,
            stat_type TEXT,
            season TEXT,
            data TEXT,
            PRIMARY KEY (player_id, type, group_type, stat_type, season)
        );
    ''')

    for entry in stats_entries:
        stat_type = entry.get("type", {}).get("displayName", "")
        group_type = entry.get("group", {}).get("displayName", "")
        splits = entry.get("splits", [])
        for split in splits:
            season_value = split.get("season", "N/A")
            stat_data = str(split.get("stat", {}))
            cursor.execute('''
                INSERT OR REPLACE INTO player_stats (player_id, type, group_type, stat_type, season, data)
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (player_id, entry.get("type", {}).get("code", ""), entry.get("group", {}).get("code", ""), stat_type, season_value, stat_data))

    conn.commit()
    conn.close()
    print(f"✅ Stats stored for player {player_id}")