
"""
This .py file will contain all paths used for the project in order to make it easier to change them in the future. 
This is a good practice to avoid hardcoding paths in the code, which can lead to errors if the paths change 
or if the code is run on different machines.
The paths are stored in a dictionary called `paths`, which contains the following: 

1. mlb_path: The path to the MLB database.
2. Injury_risk_model: The path to the injury risk model.


"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#1.
mlb_path = os.path.join(BASE_DIR, 'mlb', 'mlb_players.db')

#2. 
injury_risk_model = os.path.join(BASE_DIR, 'models', 'injury_risk_model.pkl')s