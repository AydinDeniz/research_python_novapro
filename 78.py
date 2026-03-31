from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
import joblib
import time

app = FastAPI()

# Sample data for demonstration
ratings_data = pd.DataFrame({
    'user_id': [1, 1, 1, 2, 2, 3, 3, 3],
    'movie_id': [1, 2, 3, 1, 3, 2, 3, 4],
    'rating': [5, 3, 4, 4, 5, 1, 2, 5]
})

# Collaborative filtering model
class CollaborativeFilteringModel:
    def __init__(self, ratings_data):
        self.ratings_data = ratings_data
        self.user_item_matrix = self.create_user_item_matrix()
        self.user_similarity = self.compute_user_similarity()
        self.item_similarity = self.compute_item_similarity()

    def create_user_item_matrix(self):
        user_item_matrix = self.ratings_data.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
        return user_item_matrix

    def compute_user_similarity(self):
        user_similarity = cosine_similarity(self.user_item_matrix)
        return pd.DataFrame(user_similarity, index=self.user_item_matrix.index, columns=self.user_item_matrix.index)

    def compute_item_similarity(self):
        item_similarity = cosine_similarity(self.user_item_matrix.T)
        return pd.DataFrame(item_similarity, index=self.user_item_matrix.columns, columns=self.user_item_matrix.columns)

    def recommend_movies(self, user_id, top_n=5):
        if user_id not in self.user_item_matrix.index:
            raise ValueError("User not found")

        user_ratings = self.user_item_matrix.loc[user_id]
        similar_users = self.user_similarity[user_id].sort_values(ascending=False).iloc[1:]
        weighted_ratings = similar_users.mul(user_ratings, axis=0).sum()

        recommended_movies = weighted_ratings.sort_values(ascending=False).head(top_n).index.tolist()
        return recommended_movies

# Model instance
model = CollaborativeFilteringModel(ratings_data)

# API Models
class UserRating(BaseModel):
    user_id: int
    movie_id: int
    rating: float

class RecommendationRequest(BaseModel):
    user_id: int

@app.post("/add_rating/")
async def add_rating(rating: UserRating):
    new_rating = pd.DataFrame({
        'user_id': [rating.user_id],
        'movie_id': [rating.movie_id],
        'rating': [rating.rating]
    })
    global ratings_data
    ratings_data = pd.concat([ratings_data, new_rating], ignore_index=True)
    global model
    model = CollaborativeFilteringModel(ratings_data)
    return {"message": "Rating added successfully"}

@app.get("/recommendations/")
async def get_recommendations(request: RecommendationRequest):
    try:
        recommendations = model.recommend_movies(request.user_id)
        return {"user_id": request.user_id, "recommended_movies": recommendations}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)