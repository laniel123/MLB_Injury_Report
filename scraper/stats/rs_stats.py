

import sqlite3
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import unicodedata


# Database setup
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all players
df = pd.read_sql_query('SELECT name, mlb_player_id FROM players', conn)
player_list = [{'name': row['name'], 'id': str(row['mlb_player_id'])} for _, row in df.iterrows()]

# Normalize player name (remove accents, lowercase, hyphenate)
def normalize_name(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower().replace(' ', '-')

# Selenium setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def scrape_player(player_name, mlb_player_id):
    norm_name = normalize_name(player_name)
    url = f'https://www.mlb.com/player/{norm_name}-{mlb_player_id}'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    tables = soup.find_all('table')
    for table in tables:
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]

        # Pitcher table
        if headers == ['G', 'W-L', 'ERA', 'IP', 'SO', 'WHIP']:
            row = table.find('tbody').find('tr')
            cells = [td.text.strip() for td in row.find_all('td')]
            wins, losses = cells[1].split('-') if '-' in cells[1] else (None, None)
            return {
                'mlb_player_id': mlb_player_id,
                'name': player_name.title(),
                'type': 'pitcher',
                'games': cells[0],
                'wins': wins,
                'losses': losses,
                'era': cells[2],
                'innings_pitched': cells[3],
                'strikeouts': cells[4],
                'whip': cells[5],
                'at_bats': None,
                'runs': None,
                'hits': None,
                'home_runs': None,
                'rbi': None,
                'stolen_bases': None,
                'avg': None,
                'obp': None,
                'ops': None
            }

        # Hitter table
        elif headers == ['Year', 'AB', 'R', 'H', 'HR', 'RBI', 'SB', 'AVG', 'OBP', 'OPS']:
            tbody = table.find('tbody')
            career_row = None
            for row in tbody.find_all('tr'):
                year_label = row.find_all('td')[0].text.strip()
                if 'Career Regular Season' in year_label:
                    career_row = row
                    break
            row = career_row if career_row else tbody.find('tr')
            cells = [td.text.strip() for td in row.find_all('td')]

            return {
                'mlb_player_id': mlb_player_id,
                'name': player_name.title(),
                'type': 'hitter',
                'games': cells[0],
                'wins': None,
                'losses': None,
                'era': None,
                'innings_pitched': None,
                'strikeouts': None,
                'whip': None,
                'at_bats': cells[1],
                'runs': cells[2],
                'hits': cells[3],
                'home_runs': cells[4],
                'rbi': cells[5],
                'stolen_bases': cells[6],
                'avg': cells[7],
                'obp': cells[8],
                'ops': cells[9]
            }

    print(f"⚠️ No matching stats table found for {player_name}")
    return None

# Collect and update data
for player in player_list:
    print(f"Scraping {player['name']} at URL: https://www.mlb.com/player/{normalize_name(player['name'])}-{player['id']}...")
    data = scrape_player(player['name'], player['id'])
    if data:
        cursor.execute('''
        INSERT OR REPLACE INTO player_stats (
            mlb_player_id, name, type, games, wins, losses, era, innings_pitched,
            strikeouts, whip, at_bats, runs, hits, home_runs, rbi, stolen_bases,
            avg, obp, ops
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['mlb_player_id'],
            data['name'],
            data['type'],
            data['games'],
            data['wins'],
            data['losses'],
            data['era'],
            data['innings_pitched'],
            data['strikeouts'],
            data['whip'],
            data['at_bats'],
            data['runs'],
            data['hits'],
            data['home_runs'],
            data['rbi'],
            data['stolen_bases'],
            data['avg'],
            data['obp'],
            data['ops']
        ))
        print(f"✅ Collected stats for {data['name']}")

conn.commit()
print(f"✅ Database updated with latest player stats.")

# Close resources
driver.quit()
conn.close()
print("🔒 Database connection closed.") 