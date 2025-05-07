import sqlite3
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Database path
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'

# Connect to SQLite
conn = sqlite3.connect(db_path)

# Initialize Selenium driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def scrape_player(player_name, player_id):
    url = f'https://www.mlb.com/player/{player_name}-{player_id}'
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    tables = soup.find_all('table')
    for i, table in enumerate(tables):
        print(f"🔹 Found Table {i + 1}")

        headers = [th.text.strip() for th in table.find('thead').find_all('th')]
        print(headers)

        rows = []
        for row in table.find('tbody').find_all('tr'):
            cells = [td.text.strip() for td in row.find_all(['td', 'th'])]
            rows.append(cells)
            print(cells)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Save each table to SQLite with a unique table name
        table_name = f"{player_name}_table_{i+1}".replace('-', '_')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"✅ Saved table: {table_name}")

# Example player list (you can extend this)
players = [
    ('james-outman', 680776),
    ('andy-pages', 681624),
    ('alex-vesia', 681911),
    ('edgardo-henriquez', 683618),
    ('emmet-sheehan', 686218),
    ('landon-knack', 689017),
    ('river-ryan', 689981),
    ('nick-frasso', 693308),
    ('gavin-stone', 694813)
]

# Loop over players and scrape
for player_name, player_id in players:
    print(f"\nScraping {player_name} from https://www.mlb.com/player/{player_name}-{player_id}")
    scrape_player(player_name, player_id)

# Close the driver and database connection
driver.quit()
conn.close()