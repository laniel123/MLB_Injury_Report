

def get_injury_risk_ranking(
    db_path='/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/mlb_players.db',
    injury_model_path='/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/mlb/models/injury_risk_model.pkl'
):
    import sys
    import os
    import joblib
    import pandas as pd
    import sqlite3
    from datetime import timedelta

    # Add the project root directory to Python path
    project_root = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
    sys.path.append(project_root)

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Game Logs for all players in the MLB 
    query = """
    SELECT mlb_player_stats.* , mlb_player_info.*
    FROM mlb_player_stats
    INNER JOIN mlb_player_info ON mlb_player_stats.mlb_player_id = mlb_player_info.mlb_player_id
    WHERE stat_type = 'gameLog'
    """
    game_log_pre = pd.read_sql_query(query, conn)
    game_log_pre = game_log_pre.loc[:, ~game_log_pre.columns.duplicated()]

    selected_columns = [
        'fullName', 'mlb_player_id', 'game_date', 'team_name', 'opponent_name',
        'gamesPlayed', 'gamesStarted', 'innings', 'plateAppearances', 'numberOfPitches',
        'game_number', 'atBatsPerHomeRun',
        'atBats', 'runs', 'hits', 'totalBases', 'doubles', 'triples', 'homeRuns', 'rbi',
        'baseOnBalls', 'intentionalWalks', 'strikeOuts', 'stolenBases', 'caughtStealing',
        'hitByPitch', 'sacBunts', 'sacFlies', 'avg', 'obp', 'slg',
        'primaryPosition', 'pitchHand', 'batSide',
        'height', 'weight', 'currentAge', 'birthDate', 'debutDate'
    ]
    game_logs_df = game_log_pre[selected_columns]
    game_logs_df = game_logs_df.fillna(0)
    game_logs_df = game_logs_df.rename(columns={
        'fullName': 'Name',
        'mlb_player_id': 'PlayerID',
        'game_date': 'Date',
        'team_name': 'Team',
        'opponent_name': 'OPP',
        'gamesPlayed': 'GP',
        'gamesStarted': 'GS',
        'innings': 'INN',
        'plateAppearances': 'PA',
        'numberOfPitches': 'NP',
        'game_number': 'Game#',
        'atBatsPerHomeRun': 'AB/HR',
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
        'groundIntoDoublePlay': 'GIDP',
        'leftOnBase': 'LOB',
        'position': 'POS',
        'primaryPosition': 'PrimaryPOS',
        'pitchHand': 'Throw',
        'batSide': 'Bat',
        'height': 'Height',
        'weight': 'Weight',
        'currentAge': 'Age',
        'birthDate': 'BirthDate',
        'debutDate': 'Debut'
    })

    game_logs_df.rename(columns={"PlayerID": "mlb_player_id"}, inplace=True)
    game_logs = game_logs_df
    injury_stats = pd.read_sql_query('SELECT * from injury_stats', conn)
    game_logs["Date"] = pd.to_datetime(game_logs["Date"])
    injury_stats["injury_date"] = pd.to_datetime(injury_stats["injury_date"])
    game_logs["Injured"] = 0
    
    for _, row in injury_stats.iterrows():
        player_id = row["mlb_player_id"]
        injury_date = row["injury_date"]
        mask = (
            (game_logs["mlb_player_id"] == player_id) &
            (game_logs["Date"] <= injury_date) &
            (game_logs["Date"] >= injury_date - timedelta(days=30))
        )
        game_logs.loc[mask, "Injured"] = 1

    game_logs.rename(columns={"mlb_player_id": "PlayerID"}, inplace=True)

    # Load trained model and feature names
    xgb_model = joblib.load(injury_model_path)
    feature_names = xgb_model.get_booster().feature_names

    new_game_logs = game_logs.copy()
    new_game_logs["Date"] = pd.to_datetime(new_game_logs["Date"])
    new_game_logs = new_game_logs.drop(columns=["Name", "Date", "Team", "OPP"])
    
    stats_cols = new_game_logs.drop(columns=["PlayerID", "Injured"]).columns
    new_game_logs_numeric = new_game_logs[stats_cols].apply(pd.to_numeric, errors='coerce')
    
    roll5 = new_game_logs_numeric.groupby(new_game_logs["PlayerID"]).rolling(5, min_periods=1).mean().reset_index(level=0, drop=True).add_suffix('_roll5')
    roll10 = new_game_logs_numeric.groupby(new_game_logs["PlayerID"]).rolling(10, min_periods=1).mean().reset_index(level=0, drop=True).add_suffix('_roll10')
    new_game_logs = pd.concat([new_game_logs, roll5, roll10], axis=1)
    new_game_logs = new_game_logs.drop(columns=list(stats_cols) + ["PlayerID"])
    new_game_logs = new_game_logs.fillna(0)
    uninjured_players = new_game_logs[new_game_logs['Injured'] == 0]
    
    X_uninjured = uninjured_players.drop(columns=['Injured'])
    X_uninjured = X_uninjured[feature_names]
    
    injury_probs = xgb_model.predict_proba(X_uninjured)[:, 1]
    
    uninjured_players = uninjured_players.copy()
    uninjured_players['Injury_Risk'] = injury_probs
    uninjured_players['PlayerID'] = game_logs.loc[uninjured_players.index, 'PlayerID']
    uninjured_players['Name'] = game_logs.loc[uninjured_players.index, 'Name']
    
    ranked_risk = (
        uninjured_players[['PlayerID', 'Name', 'Injury_Risk']]
        .sort_values(by='Injury_Risk', ascending=False)
        .drop_duplicates(subset='PlayerID', keep='first')
    )
    ranked_risk['Injury_Risk_Percent'] = (ranked_risk['Injury_Risk'] * 100).round(2).astype(str) + '%'
    ranked_risk['Rank'] = ranked_risk['Injury_Risk'].rank(method='first', ascending=False).astype(int)
    ranked_risk = ranked_risk[['Rank', 'Name', 'PlayerID', 'Injury_Risk_Percent']]
    
    conn.close()
    
    print("\n\nTop 30 Players by Injury Risk:")
    print("--------------------------------------------------")
    print(ranked_risk.head(30))
    print("\n\n")
    
    return ranked_risk

if __name__ == "__main__":
    
    ranked_risk = get_injury_risk_ranking()
    
    #ranked_risk.to_csv('injury_risk_rankings.csv', index=False)
    #print("Injury risk rankings saved to 'injury_risk_rankings.csv'")