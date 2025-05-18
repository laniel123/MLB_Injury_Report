import requests
import sqlite3
import time

DB_PATH = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/mlb_players.db'

def create_connection():
    return sqlite3.connect(DB_PATH)

# Create the injury_stats table with a season column
def create_injury_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS injury_stats (
        mlb_player_id INTEGER,
        player_name TEXT,
        injury_date TEXT,
        season TEXT,
        injury_description TEXT,
        team_name TEXT,
        PRIMARY KEY (mlb_player_id, injury_date)
    )
    ''')
    conn.commit()

# Scrape and store injury data from MLB API for each player
def scrape_and_store_injuries_for_all_players():
    conn = create_connection()
    create_injury_table(conn)
    cursor = conn.cursor()

    player_ids = cursor.execute("SELECT mlb_player_id FROM mlb_player_info").fetchall()

    for (mlb_id,) in player_ids:
        url = f"https://statsapi.mlb.com/api/v1/transactions?playerId={mlb_id}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ Failed to fetch injuries for {mlb_id}")
                continue

            transactions = response.json().get("transactions", [])

            for txn in transactions:
                desc = txn.get("description", "").lower()
                if txn.get("typeDesc") == "Status Change" and ("injured list" in desc or "disabled list" in desc):
                    injury_date = txn.get("date")
                    season = injury_date[:4] if injury_date else "unknown"
                    values = {
                        "mlb_player_id": txn["person"]["id"],
                        "player_name": txn["person"]["fullName"],
                        "injury_date": injury_date,
                        "season": season,
                        "injury_description": txn.get("description"),
                        "team_name": txn.get("toTeam", {}).get("name", "N/A")
                    }

                    keys = ', '.join(values.keys())
                    placeholders = ', '.join('?' for _ in values)
                    sql = f'INSERT OR IGNORE INTO injury_stats ({keys}) VALUES ({placeholders})'
                    cursor.execute(sql, tuple(values.values()))

            conn.commit()
            print(f"✅ Injuries stored for player {mlb_id}")
        except Exception as e:
            print(f"❌ Error fetching injuries for {mlb_id}: {e}")
            continue

        time.sleep(0.5)  # rate limit buffer

    conn.close()

if __name__ == "__main__":
    scrape_and_store_injuries_for_all_players()