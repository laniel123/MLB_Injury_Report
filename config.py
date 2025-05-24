import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mlb', 'mlb_players.db')
INJURY_MODEL_PATH = os.path.join(BASE_DIR, 'mlb', 'models', 'injury_risk_model.pkl')