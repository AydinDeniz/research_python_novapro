from celery import Celery
from celery.schedules import crontab
import redis
import requests
import sqlite3

# Set up Celery with Redis as the broker and backend
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Set up Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Set up SQLite database
conn = sqlite3.connect('stock_prices.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS stock_prices
                  (symbol TEXT, price REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Function to fetch real-time stock prices
def fetch_stock_price(symbol):
    response = requests.get(f"https://api.example.com/stock/{symbol}")
    if response.status_code == 200:
        return response.json()["price"]
    else:
        raise Exception("Failed to fetch stock price")

# Celery task to fetch stock prices and store in database
@app.task(bind=True, default_retry_delay=30, max_retries=3)
def fetch_and_store_stock_price(self, symbol):
    try:
        price = fetch_stock_price(symbol)
        cursor.execute("INSERT INTO stock_prices (symbol, price) VALUES (?, ?)", (symbol, price))
        conn.commit()
    except Exception as e:
        self.retry(exc=e, countdown=self.default_retry_delay)

# Schedule the task to run every minute
app.conf.beat_schedule = {
    'fetch-stock-prices': {
        'task': 'tasks.fetch_and_store_stock_price',
        'schedule': crontab(minute='*'),  # Run every minute
        'args': ('AAPL', 'GOOGL', 'MSFT')  # Example stock symbols
    },
}

# Start the Celery worker and beat scheduler
if __name__ == '__main__':
    app.start()