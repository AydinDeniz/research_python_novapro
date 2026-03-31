# Prompt 93

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
data = pd.read_csv('movie_data.csv')

# Feature engineering
data['release_date'] = pd.to_datetime(data['release_date'])
data['release_year'] = data['release_date'].dt.year
data['release_month'] = data['release_date'].dt.month
data['release_day'] = data['release_date'].dt.day
data.drop(columns=['release_date'], inplace=True)

# Split data into features and target
X = data.drop(columns=['revenue'])
y = data['revenue']

# Define models
models = {
    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, random_state=42)
}

# Cross-validation and metric collection
cv = KFold(n_splits=5, shuffle=True, random_state=42)
metrics = {
   'model': [],
   'mean_score': [],
   'std_score': []
}

for model_name, model in models.items():
    scores = cross_val_score(model, X, y, scoring='neg_mean_squared_error', cv=cv)
    metrics['model'].append(model_name)
    metrics['mean_score'].append(-np.mean(scores))
    metrics['std_score'].append(np.std(scores))

# Visualize metrics
metrics_df = pd.DataFrame(metrics)
sns.barplot(x='model', y='mean_score', yerr='std_score', data=metrics_df, capsize=0.2)
plt.ylabel('Mean Squared Error')
plt.title('Model Performance Comparison')
plt.show()