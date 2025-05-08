import sqlite3
import time
import pandas as pd
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Helper to remove accents
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Database setup
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Selenium setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Ensure table exists RS stats = regular season stats 
cursor.execute('''
CREATE TABLE IF NOT EXISTS rs_stats (
    player_id TEXT PRIMARY KEY,
    name TEXT,
    G TEXT,
    WL TEXT,
    ERA TEXT,
    IP TEXT,
    SO TEXT,
    WHIP TEXT
)
''')

def scrape_player(player_name, player_id):
    url = f'https://www.mlb.com/player/{player_name}-{player_id}'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    tables = soup.find_all('table')
    for table in tables:
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]
        if headers == ['G', 'W-L', 'ERA', 'IP', 'SO', 'WHIP']:
            row = table.find('tbody').find('tr')
            cells = [td.text.strip() for td in row.find_all('td')]
            player_data = {
                'player_id': player_id,
                'name': player_name.replace('-', ' ').title(),
                'G': cells[0],
                'W-L': cells[1],
                'ERA': cells[2],
                'IP': cells[3],
                'SO': cells[4],
                'WHIP': cells[5]
            }
            return player_data
    return None

# Query all players
df = pd.read_sql_query('SELECT name, mlb_player_id FROM players', conn)

# Convert to list of dictionaries with accents removed and hyphens added
player_list = [
    {'name': remove_accents(row['name'].lower().replace(' ', '-')), 'id': str(row['mlb_player_id'])}
    for _, row in df.iterrows()
]

# Collect data
players_data = []
for player in player_list:
    url = f'https://www.mlb.com/player/{player["name"]}-{player["id"]}'
    print(f"Scraping {player['name']} at URL: {url}...")
    driver.get(url)
    data = scrape_player(player['name'], player['id'])
    if data:
        players_data.append(data)
        print(f"✅ Collected stats for {data['name']}.")
    else:
        print(f"⚠️ No matching stats table found for {player['name']}")

# Insert data into DB
for player in players_data:
    cursor.execute('''
    INSERT OR REPLACE INTO rs_stats (player_id, name, G, WL, ERA, IP, SO, WHIP)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        player['player_id'],
        player['name'],
        player['G'],
        player['W-L'],
        player['ERA'],
        player['IP'],
        player['SO'],
        player['WHIP']
    ))

conn.commit()
print(f"✅ Inserted {len(players_data)} players into player_stats table")

# Close connections
driver.quit()
conn.close()
print("🔒 Database connection closed")