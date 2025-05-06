import requests
from bs4 import BeautifulSoup
import sqlite3

# Path to your database
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'

# Set up DB connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# URL to scrape
url = 'https://www.mlb.com/dodgers/roster'

# Fetch page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all player rows (tr elements)
rows = soup.find_all('tr')

for row in rows:
    # Grab name and href (inside <td class="info">)
    info_td = row.find('td', class_='info')
    name_tag = info_td.find('a', href=True) if info_td else None
    name = name_tag.get_text(strip=True) if name_tag else None

    # Extract MLB player ID from href
    mlb_player_id = None
    if name_tag:
        href = name_tag['href']  # e.g., '/player/660271'
        parts = href.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'player':
            try:
                mlb_player_id = int(parts[1])
            except ValueError:
                mlb_player_id = None

    # Grab DOB (first try <td>, fallback to mobile-info)
    dob_tag = row.find('td', class_='birthday')
    dob = dob_tag.get_text(strip=True) if dob_tag else None
    if not dob and info_td:
        dob_span = info_td.find('span', class_='mobile-info__birthday')
        if dob_span:
            dob = dob_span.get_text(strip=True).replace('DOB: ', '')

    # Grab Weight
    weight_tag = row.find('td', class_='weight')
    weight = weight_tag.get_text(strip=True) if weight_tag else None
    if not weight and info_td:
        weight_span = info_td.find('span', class_='mobile-info__weight')
        if weight_span:
            weight = weight_span.get_text(strip=True).replace('Wt: ', '')

    # Grab Bats/Throws (like "L/R")
    bt_tag = row.find('td', class_='bat-throw')
    bats, throws = (None, None)
    if bt_tag:
        bt_text = bt_tag.get_text(strip=True)
        if '/' in bt_text:
            bats, throws = bt_text.split('/')
    elif info_td:
        bt_span = info_td.find('span', class_='mobile-info__bat-throw')
        if bt_span:
            bt_text = bt_span.get_text(strip=True).replace('B/T: ', '')
            if '/' in bt_text:
                bats, throws = bt_text.split('/')

    # Skip if no name
    if not name:
        continue

    print(f"Inserting: {name}, MLB ID: {mlb_player_id}, DOB: {dob}, Weight: {weight}, Bats: {bats}, Throws: {throws}")

    # Insert into the players table (skip if player already exists)
    cursor.execute('''
        INSERT OR IGNORE INTO players (name, position, team, dob, bats, throws, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, None, 'Los Angeles Dodgers', dob, bats, throws, int(weight) if weight and weight.isdigit() else None))

conn.commit()
conn.close()

print("\n\nDodgers roster scraped and inserted into the database!\n\n")