# Prompt 92

import tweepy
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import streamlit as st

# Twitter API credentials
API_KEY = 'your_api_key'
API_SECRET_KEY = 'your_api_secret_key'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Function to collect tweets
def collect_tweets(query, count=100):
    tweets = tweepy.Cursor(api.search_tweets, q=query, lang="en", tweet_mode='extended').items(count)
    tweet_texts = [tweet.full_text for tweet in tweets]
    return tweet_texts

# Function to perform LDA topic modeling
def perform_lda(tweets, n_topics=5):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(tweets)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(dtm)
    return lda, vectorizer

# Function to display top topics and associated hashtags
def display_topics(lda, vectorizer, n_top_words=10):
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        topic_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        topics.append(topic_words)
    return topics

# Function to create word cloud for hashtags
def create_wordcloud(tweets):
    hashtags = ' '.join([word for tweet in tweets for word in tweet.split() if word.startswith('#')])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(hashtags)
    return wordcloud

# Streamlit dashboard
def main():
    st.title("Twitter Topic Modeling Dashboard")
    query = st.text_input("Enter a search query:", "Python")
    count = st.slider("Number of tweets to collect:", 100, 1000, 500)
    n_topics = st.slider("Number of topics:", 2, 10, 5)
    n_top_words = st.slider("Number of top words per topic:", 5, 20, 10)

    if st.button("Collect Tweets and Analyze"):
        tweets = collect_tweets(query, count)
        lda, vectorizer = perform_lda(tweets, n_topics)
        topics = display_topics(lda, vectorizer, n_top_words)
        wordcloud = create_wordcloud(tweets)

        st.subheader("Top Topics:")
        for topic_idx, topic_words in enumerate(topics):
            st.write(f"Topic {topic_idx + 1}: {', '.join(topic_words)}")

        st.subheader("Word Cloud of Hashtags:")
        st.image(wordcloud.to_array())

if __name__ == "__main__":
    main()