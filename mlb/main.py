"""
This is the main pipeline that will: 

 1. scrape data for known players that have been injured in the past. 
 2. train a model to predict injury risk based on player stats.
 3. Predict injury risk for current players based on their stats.
 4. (Opiional) Save data to csv files for future use.
 
    
"""

from scrapers.injury_stats import scrape_and_store_injuries_for_all_players
from scrapers.mlb_player_stats import scrape_and_store_stats_for_all_players
from ml.train import get_injury_risk_ranking


if __name__ == "__main__":
    # Step 1: Scrape and store injury data from MLB API for each player
    #scrape_and_store_injuries_for_all_players()
    
    
    print("Injury data scraped and stored successfully.")
    
    # Step 2: Scrape and store player stats from MLB API for each player
    #scrape_and_store_stats_for_all_players()
    
    print("Player stats scraped and stored successfully.")
    
    # Step 3: Train the model and get injury risk ranking
    get_injury_risk_ranking()
    
    
    
    