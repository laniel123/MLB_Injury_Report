import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_injuries(db_path):
    url = 'https://www.mlb.com/news/dodgers-injuries-and-roster-moves'

    # Set up Selenium driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all <p> blocks that contain injuries
    injury_blocks = soup.find_all('p')

    for block in injury_blocks:
        # Must contain a player <a> tag
        player_tag = block.find('a')
        if not player_tag:
            continue  # skip if no player

        player_name = player_tag.text.strip()

        # Extract all <strong> tags (Injury, IL date, etc.)
        strongs = block.find_all('strong')

        injury_type = ''
        il_date = ''
        expected_return = ''
        status = ''

        for s in strongs:
            label = s.text.strip().lower()
            if 'injury' in label:
                injury_type = s.next_sibling.strip()
            elif 'il date' in label:
                il_date = s.next_sibling.strip()
            elif 'expected return' in label:
                expected_return = s.next_sibling.strip()
            elif 'status' in label:
                # Get everything after the <strong>Status:</strong>
                status_text = ''
                for elem in s.next_siblings:
                    if elem.name == 'br':
                        break
                    if isinstance(elem, str):
                        status_text += elem.strip()
                    elif hasattr(elem, 'text'):
                        status_text += elem.text.strip()
                status = status_text

        print(f"Player: {player_name}")
        print(f"Injury: {injury_type}")
        print(f"IL Date: {il_date}")
        print(f"Expected Return: {expected_return}")
        print(f"Status: {status}")
        print("-" * 40)

        # Save to DB
        cursor.execute('''
            INSERT INTO injuries (
                player_name, injury_type, il_type, injury_start, notes
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            player_name,
            injury_type,
            il_date,
            expected_return,
            status
        ))

    conn.commit()
    conn.close()
    print("✅ Scraping + saving complete.")

if __name__ == '__main__':
    scrape_injuries('data/dodgers_injury_db.sqlite') 