from scraper.injury_scraper import scrape_injuries
from stats.game_stats_fetcher import fetch_game_stats
from ml.predict_risk import predict_risk

def run_pipeline():
    print("Scraping injuries...")
    scrape_injuries('data/dodgers_injury_db.sqlite')
    print("Fetching game stats...")
    fetch_game_stats('data/dodgers_injury_db.sqlite')
    print("Predicting injury risk...")
    predict_risk('data/dodgers_injury_db.sqlite')
    print("✅ Pipeline complete!")

if __name__ == '__main__':
    run_pipeline() 