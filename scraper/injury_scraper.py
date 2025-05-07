import sqlite3
import requests
from bs4 import BeautifulSoup

# Connect to your local database
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Target URL with User-Agent header
url = 'https://www.mlb.com/news/dodgers-injuries-and-roster-moves'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
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
            sibling = tag.next_sibling.strip() if tag.next_sibling else None
            if 'Injury:' in label and sibling:
                injury_type = sibling
            elif 'Expected return:' in label and sibling:
                expected_return = sibling
            elif 'Status:' in label and sibling:
                status = sibling

        # Check for duplicates
        cursor.execute('''
            SELECT COUNT(*) FROM injuries 
            WHERE mlb_player_id = ? AND injury_type = ?
        ''', (mlb_player_id, injury_type))
        if cursor.fetchone()[0] == 0:
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
            print(f"✅ Inserted: {player_name}, MLB ID: {mlb_player_id}, Injury: {injury_type}, Expected Return: {expected_return}")

            # Log to file
            with open('/logs/scraper_log.txt', 'a') as log_file:
                log_file.write(f"Inserted: {player_name}, MLB ID: {mlb_player_id}, Injury: {injury_type}, Expected Return: {expected_return}\n")
        else:
            print(f"⏩ Skipping duplicate for {player_name}")

    except Exception as e:
        print(f"Skipping due to error: {e}")

conn.commit()
conn.close()

print('All injury data scraped and inserted!')