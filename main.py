import time 
import random
from scraper.base_scraper.injury import injury
from scraper.base_scraper.player_info import player_info

from scraper.base_scraper.injury import injury

injury(log_path='/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/logs/injury_pipeline.log')


if __name__ == "__main__":
    
    # Call the player_info function to scrape player data
    
    player_info()
    
    time.sleep(3)

    # Call the injury function to scrape injury data    
    
    injury()
    
    