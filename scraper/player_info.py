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

# Find all player rows
rows = soup.find_all('tr')

for row in rows:
    # Grab name
    name_tag = row.find('a', href=True)
    name = name_tag.get_text(strip=True) if name_tag else None

    # Position is tricky - Dodgers site may not have it right in the table, so let's assume None for now
    # You can expand later if position info is added

    # DOB
    dob_tag = row.find('td', class_='birthday')
    dob = dob_tag.get_text(strip=True) if dob_tag else None

    # Weight
    weight_tag = row.find('td', class_='weight')
    weight = weight_tag.get_text(strip=True) if weight_tag else None

    # Bats/Throws (like "L/L")
    bt_tag = row.find('td', class_='bat-throw')
    bats, throws = (None, None)
    if bt_tag:
        bt_text = bt_tag.get_text(strip=True)
        if '/' in bt_text:
            bats, throws = bt_text.split('/')

    # Skip if name is missing (avoid blank inserts)
    if not name:
        continue

    print(f"Inserting: {name}, DOB: {dob}, Weight: {weight}, Bats: {bats}, Throws: {throws}")

    # Insert into the players table (skip if player already exists)
    cursor.execute('''
        INSERT OR IGNORE INTO players (name, position, team, dob, bats, throws, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, None, 'Los Angeles Dodgers', dob, bats, throws, int(weight) if weight and weight.isdigit() else None))

conn.commit()
conn.close()

print("\n\nDodgers roster scraped and inserted into the database!\n\n")