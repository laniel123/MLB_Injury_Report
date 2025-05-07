import sqlite3
import requests
from bs4 import BeautifulSoup

# Connect to your local database
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Target URL
url = 'https://www.mlb.com/news/dodgers-injuries-and-roster-moves'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all relevant <p> blocks
injury_blocks = soup.find_all('p')

for block in injury_blocks:
    player_link = block.find('a', href=True)
    if not player_link or '/player/' not in player_link['href']:
        continue  # skip if no player link

    try:
        mlb_player_id = int(player_link['href'].split('/')[-1])
        player_name = player_link.get_text(strip=True)

        injury_type = None
        expected_return = None
        status = None

        strong_tags = block.find_all('strong')
        for tag in strong_tags:
            label = tag.get_text(strip=True)
            if 'Injury:' in label:
                injury_type = tag.next_sibling.strip()
            elif 'Expected return:' in label:
                expected_return = tag.next_sibling.strip()
            elif 'Status:' in label:
                status = tag.next_sibling.strip()

        print(f"Inserting: {player_name}, MLB ID: {mlb_player_id}, Injury: {injury_type}, Expected Return: {expected_return}")

        # Insert data into the injuries table
        cursor.execute('''
            INSERT INTO injuries (mlb_player_id, injury_type, il_type, injury_start, injury_end, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            mlb_player_id,
            injury_type,
            None,       # il_type (not available)
            None,       # injury_start (not available)
            expected_return,
            status
        ))

    except Exception as e:
        print(f"⚠️ Skipping due to error: {e}")

conn.commit()
conn.close()

print('✅ All injury data scraped and inserted!')