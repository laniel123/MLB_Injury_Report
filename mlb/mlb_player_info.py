import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

DB_PATH = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/mlb_players.db'

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mlb_player_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mlb_player_id INTEGER UNIQUE,
        fullName TEXT,
        firstName TEXT,
        lastName TEXT,
        birthDate TEXT,
        currentAge INTEGER,
        birthCity TEXT,
        birthStateProvince TEXT,
        birthCountry TEXT,
        height TEXT,
        weight INTEGER,
        primaryPosition TEXT,
        batSide TEXT,
        pitchHand TEXT,
        debutDate TEXT,
        active INTEGER
    )
    ''')
    conn.commit()

def get_all_mlb_player_ids():
    url = "https://www.mlb.com/players"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    player_links = soup.select('a.p-related-links__link')
    player_ids = []

    for link in player_links:
        href = link.get('href')
        match = re.search(r'/player/[^/]+-(\d+)', href)
        if match:
            mlb_id = int(match.group(1))
            player_ids.append(mlb_id)

    return player_ids

def get_all_mlb_player_ids_with_selenium(limit=None):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.mlb.com/players"
    driver.get(url)
    time.sleep(5)  # Allow JS to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    player_links = soup.select('a.p-related-links__link')
    player_ids = []

    for link in player_links:
        href = link.get('href')
        match = re.search(r'/player/[^/]+-(\d+)', href)
        if match:
            mlb_id = int(match.group(1))
            player_ids.append(mlb_id)

    if limit is not None:
        player_ids = player_ids[:limit]

    return player_ids

def fetch_player_data(mlb_id):
    url = f"https://statsapi.mlb.com/api/v1/people/{mlb_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    if "people" not in data or not data["people"]:
        return None

    person = data["people"][0]
    return (
        mlb_id,
        person.get("fullName"),
        person.get("firstName"),
        person.get("lastName"),
        person.get("birthDate"),
        person.get("currentAge"),
        person.get("birthCity"),
        person.get("birthStateProvince"),
        person.get("birthCountry"),
        person.get("height"),
        person.get("weight"),
        person.get("primaryPosition", {}).get("name"),
        person.get("batSide", {}).get("description"),
        person.get("pitchHand", {}).get("description"),
        person.get("mlbDebutDate"),
        int(person.get("active", False))
    )

def insert_player_data(conn, player_info):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO mlb_player_info (
            mlb_player_id, fullName, firstName, lastName, birthDate,
            currentAge, birthCity, birthStateProvince, birthCountry,
            height, weight, primaryPosition, batSide, pitchHand,
            debutDate, active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', player_info)
    conn.commit()

def scrape_and_store_all_players():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS mlb_player_info")
    conn.commit()
    create_table(conn)

    player_ids = get_all_mlb_player_ids_with_selenium()
    print(f"Found {len(player_ids)} player IDs")

    for mlb_id in player_ids:
        try:
            player_info = fetch_player_data(mlb_id)
            if player_info:
                insert_player_data(conn, player_info)
                print(f"✅ Stored player {mlb_id}")
            else:
                print(f"⚠️ Skipped player {mlb_id} (no data)")
            time.sleep(0.3)
        except Exception as e:
            print(f"❌ Error for {mlb_id}: {e}")

    conn.close()

# === Run Script ===
if __name__ == "__main__":
    scrape_and_store_all_players()