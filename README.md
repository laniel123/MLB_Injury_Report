
# ⚾ Dodgers Injury Risk Prediction Project

This project is a machine learning pipeline designed to predict MLB player injury risks, initially focusing on the Dodgers but not currently extensible to any MLB team.

## 📂 Components

### 🗂️ Data Sources

- **`mlb_player_info.py`**: Retrieves player metadata.
- **`mlb_player_stats.py`**: Scrapes game log statistics.
- **`injury_stats.py`**: Scrapes injury records from the MLB API and updates the local database (`injury_stats` table) without overwriting prior data.

### 🗃️ Database

- **SQLite database (`mlb_players.db`)** stores:
  - Player information
  - Player game logs
  - Injury history (with columns for player, date, season, team, and injury description)

### 🧹 Data Preprocessing

- Calculates 5-game and 10-game rolling averages for player workload and performance metrics.
- Merges game logs with injury data to label records as injured or not.
- Ensures consistent feature preparation across teams (e.g., Dodgers, Phillies).

### 🤖 Model

- The XGBoost classifier was trained on resampled (SMOTE-balanced) data.
- Predicts the probability of injury (scaled to % for readability).
- Outputs a ranked list of players most at risk.

### ⚙️ Usage

- Filter by team and season (example: Dodgers, 2025).
- Generate ranked injury risk predictions with player names and readable risk percentages.
- Extendable: swap team names to analyze other MLB teams.

### 🔄 Safety & Updates

- `injury_stats.py` updates the injury database by **inserting or ignoring duplicates**, ensuring past data is preserved.
- Requirements can be exported using:
  ```bash
  pip freeze > requirements.txt
  ```

## 📋 Requirements

- Python 3.x
- pandas
- numpy
- xgboost
- imbalanced-learn
- scikit-learn
- matplotlib
- seaborn
- sqlite3
- requests

## 🚀 How to Run

1. Run data scraping scripts to populate the database.
2. Train the model using `Model Training.ipynb`.
3. Use `Risk Predictor.ipynb` or Python scripts to generate injury predictions.

## 📤 Outputs

- Top-ranked player injury risk tables per team.
- CSV exports of injury risk predictions for further analysis.

## Future improvements: 

- Improve model accuracy by implementing more features.
- Change file paths so they aren't hardcoded to my computer to promote ease across different machines. 

---

This project helps MLB analysts, data scientists, and sports teams monitor player fatigue and anticipate injury risks using machine learning tools.
