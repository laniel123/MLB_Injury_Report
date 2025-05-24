"""This script predicts the injury risk of MLB players based on their game logs and injury history using a pre-trained XGBoost model.
It includes the following steps:
1. Load game logs and injury data from a database.
2. Preprocess the data to create features for the model.
3. Load the pre-trained model.
4. Predict injury risk probabilities for current players."""

# Import necessary libraries

import joblib
import pandas as pd
import numpy as np
import sqlite3
from datetime import timedelta
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE 
from xgboost import plot_importance
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
injury_risk_model_path = os.path.join(BASE_DIR, 'models', 'injury_risk_model.pkl')

injury_risk_model = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/models/injury_risk_model.pkl'

# Connect to the SQLite database

db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/mlb_players.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Set up your DB path
base_dir = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr'
db_path = os.path.join(base_dir, 'data', 'mlb_players.db')  
pd.set_option('display.max_columns', None)

query = """
SELECT mlb_player_stats.* , mlb_player_info.*
FROM mlb_player_stats
INNER JOIN mlb_player_info ON mlb_player_stats.mlb_player_id = mlb_player_info.mlb_player_id
WHERE stat_type = 'gameLog'
"""

game_log_pre = pd.read_sql_query(query, conn)

game_log_pre = game_log_pre.loc[:, ~game_log_pre.columns.duplicated()]

selected_columns = [
    # Identity and basic game info
    'fullName', 'mlb_player_id', 'game_date', 'team_name', 'opponent_name',

    # Workload & fatigue
    'gamesPlayed', 'gamesStarted', 'innings', 'plateAppearances', 'numberOfPitches',
    'game_number', 'atBatsPerHomeRun',

    # Performance (extended)
    'atBats', 'runs', 'hits', 'totalBases', 'doubles', 'triples', 'homeRuns', 'rbi',
    'baseOnBalls', 'intentionalWalks', 'strikeOuts', 'stolenBases', 'caughtStealing',
    'hitByPitch', 'sacBunts', 'sacFlies', 'avg', 'obp', 'slg',

    # Performance trends / condition indicators
    #'groundIntoDoublePlay', 'leftOnBase',

    # Positional & biomechanical stress factors
     'primaryPosition', 'pitchHand', 'batSide',

    # Biometric and career timeline
    'height', 'weight', 'currentAge', 'birthDate', 'debutDate'
]

game_logs_df = game_log_pre[selected_columns]

# Fill rows with missing values
game_logs_df = game_logs_df.fillna(0)

game_logs_df = game_logs_df.rename(columns={
    # Identity and team info
    'fullName': 'Name',
    'mlb_player_id': 'PlayerID',
    'game_date': 'Date',
    'team_name': 'Team',
    'opponent_name': 'OPP',

    # Workload & fatigue
    'gamesPlayed': 'GP',
    'gamesStarted': 'GS',
    'innings': 'INN',
    'plateAppearances': 'PA',
    'numberOfPitches': 'NP',
    'game_number': 'Game#',
    'atBatsPerHomeRun': 'AB/HR',

    # Batting performance
    'atBats': 'AB',
    'runs': 'R',
    'hits': 'H',
    'totalBases': 'TB',
    'doubles': '2B',
    'triples': '3B',
    'homeRuns': 'HR',
    'rbi': 'RBI',
    'baseOnBalls': 'BB',
    'intentionalWalks': 'IBB',
    'strikeOuts': 'SO',
    'stolenBases': 'SB',
    'caughtStealing': 'CS',
    'hitByPitch': 'HBP',
    'sacBunts': 'SAC',
    'sacFlies': 'SF',
    'avg': 'AVG',
    'obp': 'OBP',
    'slg': 'SLG',

    # Performance trends
    'groundIntoDoublePlay': 'GIDP',
    'leftOnBase': 'LOB',

    # Positional & biomechanics
    'position': 'POS',
    'primaryPosition': 'PrimaryPOS',
    'pitchHand': 'Throw',
    'batSide': 'Bat',

    # Biometric & career data
    'height': 'Height',
    'weight': 'Weight',
    'currentAge': 'Age',
    'birthDate': 'BirthDate',
    'debutDate': 'Debut'
})

# STEP 1: Load data
game_logs_df.rename(columns={"PlayerID": "mlb_player_id"}, inplace=True)
game_logs = game_logs_df # must include 'mlb_player_id' and 'Date'
injury_stats = pd.read_sql_query('SELECT * from injury_stats', conn)  # must include 'mlb_player_id' and 'injury_date'

# STEP 2: Convert date columns
game_logs["Date"] = pd.to_datetime(game_logs["Date"])
injury_stats["injury_date"] = pd.to_datetime(injury_stats["injury_date"])

# STEP 3: Initialize all as not injured
game_logs["Injured"] = 0

# STEP 4: Iterate over each injury record
for _, row in injury_stats.iterrows():
    player_id = row["mlb_player_id"]
    injury_date = row["injury_date"]

    # Mark all games within 30 days before the injury as Injured = 1
    mask = (
        (game_logs["mlb_player_id"] == player_id) &
        (game_logs["Date"] <= injury_date) &
        (game_logs["Date"] >= injury_date - timedelta(days=30))
    )
    game_logs.loc[mask, "Injured"] = 1

game_logs.rename(columns={"mlb_player_id": "PlayerID"}, inplace=True)

# Load trained model and feature names
xgb_model = joblib.load(injury_risk_model)
feature_names = xgb_model.get_booster().feature_names

# STEP 1: Load current player data (replace this with your data source)
# Example: new_game_logs = pd.read_csv('game_logs.csv')

new_game_logs = game_logs.copy()

# STEP 2: Preprocess data (same as training)
new_game_logs["Date"] = pd.to_datetime(new_game_logs["Date"])
new_game_logs = new_game_logs.drop(columns=["Name", "Date", "Team", "OPP"])

# Identify stat columns
stats_cols = new_game_logs.drop(columns=["PlayerID", "Injured"]).columns

new_game_logs_numeric = new_game_logs[stats_cols].apply(pd.to_numeric, errors='coerce')

# Prepare rolling DataFrames
roll5 = new_game_logs_numeric.groupby(new_game_logs["PlayerID"]).rolling(5, min_periods=1).mean().reset_index(level=0, drop=True).add_suffix('_roll5')
roll10 = new_game_logs_numeric.groupby(new_game_logs["PlayerID"]).rolling(10, min_periods=1).mean().reset_index(level=0, drop=True).add_suffix('_roll10')

# Concatenate once to avoid fragmentation
new_game_logs = pd.concat([new_game_logs, roll5, roll10], axis=1)

# Drop raw stats and player ID
new_game_logs = new_game_logs.drop(columns=list(stats_cols) + ["PlayerID"])
new_game_logs = new_game_logs.fillna(0)

# STEP 3: Filter for active, uninjured players
uninjured_players = new_game_logs[new_game_logs['Injured'] == 0]

# Drop label before prediction and ensure feature order matches training
X_uninjured = uninjured_players.drop(columns=['Injured'])
X_uninjured = X_uninjured[feature_names]

# STEP 4: Predict injury risk probabilities
injury_probs = xgb_model.predict_proba(X_uninjured)[:, 1]

# STEP 5: Attach predictions back to player records
uninjured_players = uninjured_players.copy()
uninjured_players['Injury_Risk'] = injury_probs

# STEP 6: Rank players by predicted injury risk (highest to lowest)
ranked_risk = uninjured_players.sort_values(by='Injury_Risk', ascending=False)

# STEP 7: Display top N risky players

top_n = 30
print(f"\n🚨 Top {top_n} Players at Risk of Injury:")
print(ranked_risk[['Injury_Risk']].head(top_n))

# Optional: Save results to CSV
ranked_risk[['Injury_Risk']].to_csv('predicted_injury_risks.csv', index=False)

print("\n✅ Injury risk predictions saved to 'predicted_injury_risks.csv'.")