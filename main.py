import time 
import random
from scraper.base_scraper.injury import injury
from scraper.base_scraper.player_info import player_info
from scraper.stats.game_logs import game_logs

from scraper.base_scraper.injury import injury

injury(log_path='/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/logs/injury_pipeline.log')


# the Main hub for all scraping
if __name__ == "__main__":
    
    # Set a random seed for reproducibility
    random.seed(42)
    print('\nStarting player info scraping...\n')
    
    time.sleep(1)
    
    # Call the player_info function to scrape player data
    player_info()
    
    time.sleep(3)

    # Call the injury function to scrape injury data    
    injury()
    
    time.sleep(3)
    
    # Call the game_logs function to scrape game logs
    game_logs()
    
    