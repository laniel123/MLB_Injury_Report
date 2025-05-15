import requests
from bs4 import BeautifulSoup
import sqlite3

# Path to your SQLite database
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Dodgers roster URL
url = 'https://www.mlb.com/dodgers/roster'

# Fetch and parse page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <tr> player rows
rows = soup.find_all('tr')

for row in rows:
    info_td = row.find('td', class_='info')
    name_tag = info_td.find('a', href=True) if info_td else None

    # Filter: only rows with valid /player/ href
    if not name_tag or '/player/' not in name_tag['href']:
        continue

    name = name_tag.get_text(strip=True)
    href = name_tag['href']  # e.g., /player/660271
    mlb_player_id = href.split('/')[2] if href else None

    # Grab Position
    position_tag = row.find('td', class_='pos')
    position = position_tag.get_text(strip=True) if position_tag else None

    # Grab DOB
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

    # Grab Bats/Throws
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

    # Debug print
    print(f"\nProcessing: {name}, ID: {mlb_player_id}, Position: {position}, DOB: {dob}, Weight: {weight}, Bats: {bats}, Throws: {throws}, HREF: {href}")

    # Check if player already exists
    cursor.execute('SELECT COUNT(*) FROM players WHERE mlb_player_id = ?', (mlb_player_id,))
    exists = cursor.fetchone()[0] > 0

    if exists:
        # Update existing record
        cursor.execute('''
            UPDATE players
            SET name = ?, position = ?, team = ?, dob = ?, bats = ?, throws = ?, weight = ?, href = ?
            WHERE mlb_player_id = ?
        ''', (
            name,
            position,
            'LAD',
            dob,
            bats,
            throws,
            int(weight) if weight and weight.isdigit() else None,
            href,
            mlb_player_id
        ))
        print(f"🔄 Updated: {name}")
    else:
        # Insert new record
        cursor.execute('''
            INSERT INTO players (
                mlb_player_id, name, position, team, dob, bats, throws, weight, href
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mlb_player_id,
            name,
            position,
            'LAD',
            dob,
            bats,
            throws,
            int(weight) if weight and weight.isdigit() else None,
            href
        ))
        print(f"✅ Inserted: {name}")

# Commit and close
conn.commit()
conn.close()

print("\n\n Dodgers roster scraped, updated, and inserted into the database!\n\n")