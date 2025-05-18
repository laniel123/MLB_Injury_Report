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


def create_stats_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mlb_player_stats (
        mlb_player_id INTEGER,
        stat_type TEXT,
        stat_group TEXT,
        season TEXT,
        game_date TEXT,
        team_id INTEGER,
        team_name TEXT,
        opponent_id INTEGER,
        opponent_name TEXT,
        position TEXT,
        gamesPlayed INTEGER,
        games TEXT DEFAULT 'na',
        gamesStarted INTEGER,
        assists INTEGER,
        putOuts INTEGER,
        errors INTEGER,
        chances INTEGER,
        fielding TEXT,
        doublePlays INTEGER,
        triplePlays INTEGER,
        throwingErrors INTEGER,
        rangeFactorPerGame TEXT,
        rangeFactorPer9Inn TEXT,
        innings TEXT,
        inningsPitched TEXT,
        catcherERA TEXT,
        flyOuts INTEGER,
        groundOuts INTEGER,
        airOuts INTEGER,
        passedBall INTEGER,
        wins INTEGER,
        losses INTEGER,
        wildPitches INTEGER,
        pickoffs INTEGER,
        runs INTEGER,
        doubles INTEGER,
        triples INTEGER,
        homeRuns INTEGER,
        strikeOuts INTEGER,
        baseOnBalls INTEGER,
        intentionalWalks INTEGER,
        hits INTEGER,
        hitByPitch INTEGER,
        avg TEXT,
        atBats INTEGER,
        obp TEXT,
        slg TEXT,
        ops TEXT,
        caughtStealing INTEGER,
        stolenBases INTEGER,
        stolenBasePercentage TEXT,
        groundIntoDoublePlay INTEGER,
        groundIntoTriplePlay INTEGER,
        numberOfPitches INTEGER,
        plateAppearances INTEGER,
        totalBases INTEGER,
        rbi INTEGER,
        leftOnBase INTEGER,
        sacBunts INTEGER,
        sacFlies INTEGER,
        babip TEXT,
        groundOutsToAirouts TEXT,
        catchersInterference INTEGER,
        atBatsPerHomeRun TEXT,
        summary TEXT,
        isHome BOOLEAN,
        isWin BOOLEAN,
        game_id INTEGER,
        game_number INTEGER,
        day_night TEXT,
        era TEXT DEFAULT 'na',
        game TEXT DEFAULT 'na',
        PRIMARY KEY (mlb_player_id, stat_type, stat_group, season, game_date, position)
    )
    ''')
    conn.commit()

def reset_stats_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DROP TABLE IF EXISTS mlb_player_stats')
        conn.commit()
    finally:
        conn.close()

def scrape_and_store_stats_for_all_players():
    reset_stats_table()
    conn = create_connection()
    create_stats_table(conn)
    cursor = conn.cursor()

    player_ids = cursor.execute("SELECT mlb_player_id FROM mlb_player_info").fetchall()

    for (mlb_id,) in player_ids:
        url = f"https://statsapi.mlb.com/api/v1/people/{mlb_id}/stats"
        params = {
            "stats": "season,career,gameLog",
            "group": "hitting,pitching,fielding",
            "season": "2025"
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"❌ Failed to fetch stats for {mlb_id}")
                continue
            data = response.json()
            for stat_block in data.get("stats", []):
                stat_type = stat_block.get("type", {}).get("displayName", "")
                stat_group = stat_block.get("group", {}).get("displayName", "")
                for split in stat_block.get("splits", []):
                    values = {
                        "mlb_player_id": mlb_id,
                        "stat_type": stat_type,
                        "stat_group": stat_group,
                        "season": split.get("season"),
                        "game_date": split.get("date"),
                        "team_id": split.get("team", {}).get("id"),
                        "team_name": split.get("team", {}).get("name"),
                        "opponent_id": split.get("opponent", {}).get("id"),
                        "opponent_name": split.get("opponent", {}).get("name"),
                        "position": split.get("position", {}).get("abbreviation"),
                        "isHome": split.get("isHome"),
                        "isWin": split.get("isWin"),
                        "game_id": split.get("game", {}).get("gamePk"),
                        "game_number": split.get("game", {}).get("gameNumber"),
                        "day_night": split.get("game", {}).get("dayNight"),
                    }
                    stat_data = split.get("stat", {})
                    for stat_key in stat_data:
                        if isinstance(stat_data[stat_key], dict) or stat_data[stat_key] is None:
                            stat_data[stat_key] = "NA"
                    values.update(stat_data)

                    keys = ', '.join(values.keys())
                    placeholders = ', '.join('?' for _ in values)
                    sql = f'INSERT OR IGNORE INTO mlb_player_stats ({keys}) VALUES ({placeholders})'
                    cursor.execute(sql, tuple(values.values()))
            conn.commit()
            print(f"✅ Stats stored for player {mlb_id}")
        except Exception as e:
            print(f"❌ Error storing stats for player {mlb_id}: {e}")
            continue

    conn.close()

if __name__ == "__main__":
    scrape_and_store_stats_for_all_players()