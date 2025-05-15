from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import sqlite3
import unicodedata

# Setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
conn = sqlite3.connect('/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite')
cursor = conn.cursor()

# Normalize player name for URL
def normalize_name(name):
    nfkd_form = unicodedata.normalize('NFKD', name)
    return nfkd_form.encode('ASCII', 'ignore').decode('ASCII').lower().replace(' ', '-')

# Extract one cell
def extract(col_class, row):
    cell = row.find('td', class_=col_class)
    return cell.get_text(strip=True) if cell else None

# Scrape game log for one player
def scrape_player(player_name, mlb_player_id):
    norm_name = normalize_name(player_name)
    url = f'https://www.mlb.com/player/{norm_name}-{mlb_player_id}'
    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.select('.gamelogs-table table tbody tr')
    rows = [r for r in rows if 'total' not in r.get('class', []) and 'header-repeat' not in r.get('class', [])]

    for row in rows:
        game_date = extract('col-0', row)
        team = extract('col-1', row)
        opponent = extract('col-2', row)
        ab = int(extract('col-3', row) or 0)
        r = int(extract('col-4', row) or 0)
        h = int(extract('col-5', row) or 0)
        tb = int(extract('col-6', row) or 0)
        doubles = int(extract('col-7', row) or 0)
        triples = int(extract('col-8', row) or 0)
        hr = int(extract('col-9', row) or 0)
        rbi = int(extract('col-10', row) or 0)
        bb = int(extract('col-11', row) or 0)
        ibb = int(extract('col-12', row) or 0)
        so = int(extract('col-13', row) or 0)
        sb = int(extract('col-14', row) or 0)
        cs = int(extract('col-15', row) or 0)
        avg = float(extract('col-16', row) or 0)
        obp = float(extract('col-17', row) or 0)
        slg = float(extract('col-18', row) or 0)
        hbp = int(extract('col-19', row) or 0)
        sac = int(extract('col-20', row) or 0)
        sf = int(extract('col-21', row) or 0)

        cursor.execute('SELECT COUNT(*) FROM game_logs WHERE mlb_player_id = ? AND game_date = ?', (mlb_player_id, game_date))
        exists = cursor.fetchone()[0] > 0

        if exists:
            cursor.execute('''
                UPDATE game_logs SET team = ?, opponent = ?, ab = ?, r = ?, h = ?, tb = ?, doubles = ?, triples = ?,
                    hr = ?, rbi = ?, bb = ?, ibb = ?, so = ?, sb = ?, cs = ?, avg = ?, obp = ?, slg = ?,
                    hbp = ?, sac = ?, sf = ? WHERE mlb_player_id = ? AND game_date = ?
            ''', (
                team, opponent, ab, r, h, tb, doubles, triples, hr, rbi, bb, ibb, so, sb, cs,
                avg, obp, slg, hbp, sac, sf, mlb_player_id, game_date
            ))
            print(f"🔄 Updated: {player_name} | {game_date} vs {opponent}")
        else:
            cursor.execute('''
                INSERT INTO game_logs (
                    mlb_player_id, game_date, team, opponent, ab, r, h, tb, doubles, triples,
                    hr, rbi, bb, ibb, so, sb, cs, avg, obp, slg, hbp, sac, sf
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                mlb_player_id, game_date, team, opponent, ab, r, h, tb, doubles, triples,
                hr, rbi, bb, ibb, so, sb, cs, avg, obp, slg, hbp, sac, sf
            ))
            print(f"✅ Inserted: {player_name} | {game_date} vs {opponent}")

# 🔁 Example usage:
scrape_player("Shohei Ohtani", 660271)

# Finalize
conn.commit()
conn.close()
driver.quit()

print("\n✅ Game logs updated and stored.\n")