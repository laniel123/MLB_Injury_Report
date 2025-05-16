
import pandas as pd
import sqlite3
import numpy as np

# Connect to the SQLite database
db_path = '/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/dodgers_injury_db.sqlite'
conn = sqlite3.connect(db_path)

# Load game logs into a DataFrame
df = pd.read_sql_query("SELECT * FROM game_logs", conn)
df['game_date'] = pd.to_datetime(df['game_date'])
df = df.sort_values(by=['mlb_player_id', 'game_date'])

# 2. Feature Engineering: Calculate fatigue indicators
df['games_played'] = 1
df['rolling_so'] = df.groupby('mlb_player_id')['so'].transform(lambda x: x.rolling(5, min_periods=1).mean())
df['rolling_obp'] = df.groupby('mlb_player_id')['obp'].transform(lambda x: x.rolling(5, min_periods=1).mean())
df['rolling_slg'] = df.groupby('mlb_player_id')['slg'].transform(lambda x: x.rolling(5, min_periods=1).mean())

# Back-to-back games indicator
df['prev_date'] = df.groupby('mlb_player_id')['game_date'].shift(1)
df['days_between'] = (df['game_date'] - df['prev_date']).dt.days
df['back_to_back'] = df['days_between'].apply(lambda x: 1 if x == 1 else 0)

# 3. Bayesian Injury Risk Calculation
# Assume prior: 5% injury baseline → Beta(1, 19)
alpha_prior = 1
beta_prior = 19

# Define a fatigue score (you can tune this based on stronger metrics)
df['fatigue_score'] = (
    0.4 * df['rolling_so'].fillna(0) +
    0.3 * df['back_to_back'].fillna(0) -
    0.15 * df['rolling_obp'].fillna(0) -
    0.15 * df['rolling_slg'].fillna(0)
)

# Normalize fatigue_score to [0, 1]
df['fatigue_score'] = (df['fatigue_score'] - df['fatigue_score'].min()) / (df['fatigue_score'].max() - df['fatigue_score'].min())

# Update Beta posterior
df['alpha_post'] = alpha_prior + df['fatigue_score']
df['beta_post'] = beta_prior + (1 - df['fatigue_score'])

# Calculate injury probability as posterior mean
df['injury_risk'] = df['alpha_post'] / (df['alpha_post'] + df['beta_post'])

# 4. Final Output: Latest risk per player
# Latest risk per player
latest_logs = df.sort_values('game_date').groupby('mlb_player_id').tail(1)
risk_report = latest_logs[['mlb_player_id', 'game_date', 'injury_risk']].sort_values(by='injury_risk', ascending=False)

# Save to CSV (optional)
#risk_report.to_csv('injury_risk_report.csv', index=False)
print(risk_report)
