# Prompt 83

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
from datetime import datetime

def get_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [headline.text for headline in soup.find_all('h2')]
    return headlines

def analyze_sentiment(headlines):
    sentiment_results = []
    for headline in headlines:
        analysis = TextBlob(headline)
        sentiment = 'positive' if analysis.sentiment.polarity > 0 else 'negative' if analysis.sentiment.polarity < 0 else 'neutral'
        sentiment_results.append({'headline': headline,'sentiment': sentiment})
    return sentiment_results

def create_dashboard(sentiment_results):
    df = pd.DataFrame(sentiment_results)
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    df.to_html(f'dashboard_{date_string}.html')

if __name__ == '__main__':
    urls = ['https://www.bbc.com/news', 'https://www.cnn.com/', 'https://www.nytimes.com/']
    all_headlines = []
    for url in urls:
        all_headlines.extend(get_headlines(url))
    sentiment_results = analyze_sentiment(all_headlines)
    create_dashboard(sentiment_results)