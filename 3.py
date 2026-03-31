import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, average_precision_score

# Load data
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')

# Merge ratings and movies dataframes
data = pd.merge(ratings, movies, on='movieId')

# Pivot the data to create a user-item matrix
user_item_matrix = data.pivot(index='userId', columns='title', values='rating').fillna(0)

# Compute cosine similarity between items
item_similarity = cosine_similarity(user_item_matrix.T)
item_similarity_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

# Function to get recommendations for a user
def get_recommendations(user_id, user_item_matrix, item_similarity_df, n_recommendations=5):
    user_ratings = user_item_matrix.loc[user_id].dropna()
    similar_items = []

    for item in user_ratings.index:
        similar_items.append(item_similarity_df[item].drop(user_ratings.index).sort_values(ascending=False).head(n_recommendations))

    similar_items = pd.concat(similar_items).sort_values(ascending=False)
    recommendations = similar_items.index.tolist()[:n_recommendations]
    return recommendations

# Split data into train and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Create user-item matrices for train and test sets
train_matrix = train_data.pivot(index='userId', columns='title', values='rating').fillna(0)
test_matrix = test_data.pivot(index='userId', columns='title', values='rating').fillna(0)

# Evaluate the recommendation system using MAP
def evaluate_map(train_matrix, test_matrix, item_similarity_df, n_recommendations=5):
    map_scores = []

    for user_id in test_matrix.index:
        if user_id not in train_matrix.index:
            continue

        recommendations = get_recommendations(user_id, train_matrix, item_similarity_df, n_recommendations)
        actual_ratings = test_matrix.loc[user_id].dropna().index.tolist()

        if not actual_ratings:
            continue

        relevance = [1 if movie in actual_ratings else 0 for movie in recommendations]
        precision_at_k = precision_score([1] * len(recommendations), relevance, average='micro')
        map_score = average_precision_score([1] * len(recommendations), relevance)
        map_scores.append(map_score)

    return np.mean(map_scores)

# Evaluate the system
map_score = evaluate_map(train_matrix, test_matrix, item_similarity_df)
print(f'Mean Average Precision (MAP): {map_score}')

# Example recommendation
user_id = 1
recommendations = get_recommendations(user_id, user_item_matrix, item_similarity_df)
print(f'Recommendations for user {user_id}: {recommendations}')