import sqlite3
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import time

# --- Step 1: Connect to SQLite and get player data ---
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)

query = 'SELECT player_id, name FROM players'
players_df = pd.read_sql_query(query, conn)
conn.close()

# --- Step 2: Slugify names for URLs ---
def slugify(name):
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)  # Remove punctuation
    name = name.replace(' ', '-')         # Replace spaces with hyphens
    return name

players_df['name_slug'] = players_df['name'].apply(slugify)
players_df['url'] = players_df.apply(lambda row: f"https://www.mlb.com/player/{row['name_slug']}-{row['player_id']}", axis=1)

# --- Step 3: Scrape stats from each player page ---
for idx, row in players_df.iterrows():
    player_name = row['name']
    url = row['url']
    print(f'\nScraping {player_name} from {url}')

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f'❌ Failed to load {url} (Status {response.status_code})')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all tables (you can refine this with specific selectors later)
        stats_tables = soup.find_all('table')

        if not stats_tables:
            print(f'⚠ No tables found on {url}')
            continue

        for table_idx, table in enumerate(stats_tables):
            print(f'\n🔹 Table {table_idx + 1} for {player_name}')
            for row in table.find_all('tr'):
                cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
                if cells:
                    print(cells)

    except Exception as e:
        print(f'⚠ Error scraping {url}: {e}')

    time.sleep(1)  # Be polite to the server!