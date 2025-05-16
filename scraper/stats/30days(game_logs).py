import requests
import pandas as pd
import unicodedata
from bs4 import BeautifulSoup as bs
import sqlite3
import time

# Setup DB connection
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to extract data from a specific column in a row
def extract(col_class, row):
    try:
        for td in row.find_all('td'):
            if col_class in td.get('class', []):
                return td.get_text(strip=True)
    except Exception:
        return None
    return None

# Query all players
df = pd.read_sql_query('SELECT name, mlb_player_id FROM players', conn)
player_list = [{'name': row['name'], 'id': str(row['mlb_player_id'])} for _, row in df.iterrows()]

# Normalize player name (remove accents, lowercase, hyphenate)
def normalize_name(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower().replace(' ', '-')

# Query all players and build the normalized list
df = pd.read_sql_query('SELECT name, mlb_player_id FROM players', conn)
players = [
    {'name': normalize_name(row['name']), 'id': str(row['mlb_player_id'])}
    for _, row in df.iterrows()
]

for player in players:
    player_name = player['name']
    mlb_player_id = player['id']
    url = f'https://www.mlb.com/player/{player_name}-{mlb_player_id}?stats=gamelogs'
    print(f"Scraping {player_name.title().replace('-', ' ')} at URL: {url}...")

    try:
        res = requests.get(url)
        soup = bs(res.text, 'html.parser')
        table = soup.find('table')

        if not table:
            print(f"⚠️ No game log table found for {player_name}")
            continue

        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            ab_raw = extract('col-3', row)
            try:
                ab = int(float(ab_raw))
            except ValueError:
                print(f"⚠️ Skipping row due to non-numeric AB: {ab_raw}")
                continue

            game_date = extract('col-1', row)
            team = extract('col-2', row)
            opponent = extract('col-22', row)

            try:
                stats = {
                    'ab': ab,
                    'r': int(float(extract('col-4', row) or 0)),
                    'h': int(float(extract('col-5', row) or 0)),
                    'tb': int(float(extract('col-6', row) or 0)),
                    'doubles': int(float(extract('col-7', row) or 0)),
                    'triples': int(float(extract('col-8', row) or 0)),
                    'hr': int(float(extract('col-9', row) or 0)),
                    'rbi': int(float(extract('col-10', row) or 0)),
                    'bb': int(float(extract('col-11', row) or 0)),
                    'ibb': int(float(extract('col-12', row) or 0)),
                    'so': int(float(extract('col-13', row) or 0)),
                    'sb': int(float(extract('col-14', row) or 0)),
                    'cs': int(float(extract('col-15', row) or 0)),
                    'avg': float(extract('col-16', row) or 0),
                    'obp': float(extract('col-17', row) or 0),
                    'slg': float(extract('col-18', row) or 0),
                    'hbp': int(float(extract('col-19', row) or 0)),
                    'sac': int(float(extract('col-20', row) or 0)),
                    'sf': int(float(extract('col-21', row) or 0))
                }
            except (ValueError, TypeError):
                print(f"⚠️ Skipping malformed row for {player_name}: {[td.text.strip() for td in row.find_all('td')]}")
                continue

            cursor.execute(
                'SELECT COUNT(*) FROM game_logs WHERE mlb_player_id = ? AND game_date = ?',
                (mlb_player_id, game_date)
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                cursor.execute('''
                    UPDATE game_logs
                    SET team = ?, opponent = ?, ab = ?, r = ?, h = ?, tb = ?, doubles = ?, triples = ?,
                        hr = ?, rbi = ?, bb = ?, ibb = ?, so = ?, sb = ?, cs = ?, avg = ?, obp = ?, slg = ?,
                        hbp = ?, sac = ?, sf = ?
                    WHERE mlb_player_id = ? AND game_date = ?
                ''', (
                    team, opponent, stats['ab'], stats['r'], stats['h'], stats['tb'], stats['doubles'],
                    stats['triples'], stats['hr'], stats['rbi'], stats['bb'], stats['ibb'], stats['so'],
                    stats['sb'], stats['cs'], stats['avg'], stats['obp'], stats['slg'], stats['hbp'],
                    stats['sac'], stats['sf'], mlb_player_id, game_date
                ))
                print(f"🔄 Updated: {player_name} | {game_date} vs {opponent}")
            else:
                cursor.execute('''
                    INSERT INTO game_logs (
                        mlb_player_id, game_date, team, opponent, ab, r, h, tb, doubles, triples,
                        hr, rbi, bb, ibb, so, sb, cs, avg, obp, slg, hbp, sac, sf
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mlb_player_id, game_date, team, opponent, stats['ab'], stats['r'], stats['h'],
                    stats['tb'], stats['doubles'], stats['triples'], stats['hr'], stats['rbi'],
                    stats['bb'], stats['ibb'], stats['so'], stats['sb'], stats['cs'], stats['avg'],
                    stats['obp'], stats['slg'], stats['hbp'], stats['sac'], stats['sf']
                ))
                print(f"✅ Inserted: {player_name} | {game_date} vs {opponent}")

        time.sleep(3)

    except Exception as e:
        print(f"❌ Error scraping {player_name}: {e}")

conn.commit()
conn.close()
print("\n✅ Game logs updated and stored.") 