import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# STEP 1: Load your newly saved merged injury stats
df = pd.read_csv("/Users/daniellarson/Desktop/Code/Projects/dodgers_injtrkr/data/injury_player_stats.csv")
print("After loading:", df.shape)

# STEP 2: Drop irrelevant/non-numeric columns
cols_to_drop = [
    'GameDate', 'injury_date', 'injury_description',
    'StatType', 'StatGroup', 'Team', 'Opponent', 'Position',
    'Games', 'summary', 'game_id', 'season'
]
df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
print("After dropping columns:", df.shape)

# STEP 3: Drop rows with missing values
\
# ✅ Use this instead:
df = df.fillna(0)
print("After filledna:", df.shape)

# STEP 4: Convert categorical columns (if any) to numeric
df = pd.get_dummies(df)
print("After get_dummies:", df.shape)

# STEP 4.5: Correlation heatmap of top features
corr_matrix = df.corr(numeric_only=True)
top_features = corr_matrix['injured'].abs().sort_values(ascending=False).head(15).index
corr_subset = corr_matrix.loc[top_features, top_features]

plt.figure(figsize=(12, 10))
sns.heatmap(corr_subset, annot=True, cmap='coolwarm', fmt=".2f", square=True, linewidths=0.5)
plt.title("🔗 Correlation Between Top Features and Injury")
plt.tight_layout()
plt.show()

# STEP 5: Ensure the target column 'injured' is present
if 'injured' not in df.columns:
    df['injured'] = 1  # Since this file only contains injured players

# STEP 6: Separate features and target
X = df.drop('injured', axis=1)
y = df['injured']

# STEP 7: Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# STEP 8: Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# STEP 9: Evaluate
y_pred = model.predict(X_test)
print("🔍 Classification Report:")
print(classification_report(y_test, y_pred))

# STEP 10: Feature importance plot
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
top_n = 15

plt.figure(figsize=(10, 6))
plt.title("Top 15 Injury-Predictive Features")
plt.bar(range(top_n), importances[indices[:top_n]], align="center")
plt.xticks(range(top_n), X.columns[indices[:top_n]], rotation=45, ha='right')
plt.tight_layout()
plt.show()