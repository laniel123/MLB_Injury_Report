import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def safe_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def extract(col_class, row):
    try:
        for td in row.find_all('td'):
            if col_class in td.get('class', []):
                return td.get_text(strip=True)
    except Exception:
        return None
    return None

def scrape_player(name, player_id):
    url = f"https://www.mlb.com/player/{name}-{player_id}/gamelog"
    print(f"Scraping {name} at URL: {url}...")

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')

        if not table:
            print(f"⚠️ No game log table found for {name}")
            return

        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 20:
                print(f"⚠️ Skipping malformed row for {name}: {[cell.text for cell in cells]}")
                continue

            stats = {
                'player_id': player_id,
                'date': extract('col-0', row),
                'opp': extract('col-2', row),
                'ab': safe_int(extract('col-4', row)),
                'h': safe_int(extract('col-5', row)),
                'bb': safe_int(extract('col-10', row)),
                'so': safe_int(extract('col-11', row)),
                'ibb': safe_int(extract('col-12', row)),
                'sf': safe_int(extract('col-21', row)),
                # Add more fields as needed
            }

            # Ensure all numeric values are valid (date and opp can be non-numeric)
            numeric_fields = ['ab', 'h', 'bb', 'so', 'ibb', 'sf']
            if any(stats[field] is None for field in numeric_fields):
                print(f"⚠️ Skipping malformed row for {name}: {[cell.text for cell in cells]}")
                continue

            cursor.execute('''
                INSERT INTO game_logs (player_id, date, opp, ab, h, bb, so, ibb, sf)
                VALUES (:player_id, :date, :opp, :ab, :h, :bb, :so, :ibb, :sf)
            ''', stats)

        conn.commit()

    except Exception as e:
        print(f"❌ Error scraping {name}: {e}")

# Setup DB connection
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load players
players = [
    {'name': 'luis-garcia', 'id': '472610'},
    {'name': 'clayton-kershaw', 'id': '477132'},
    # ... (add other players as needed)
]

# Scrape all players
for player in players:
    scrape_player(player['name'], player['id'])
    time.sleep(4)

print("\n✅ Game logs updated and stored.")
conn.close()