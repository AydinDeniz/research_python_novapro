import requests
from bs4 import BeautifulSoup
import psycopg2
import redis
import rq
from rq.decorators import job
from urllib.parse import urljoin, urlparse
from time import sleep
import random

# PostgreSQL connection
conn = psycopg2.connect("dbname=test user=postgres password=secret")
cur = conn.cursor()

# Redis connection
redis_conn = redis.Redis()
queue = rq.Queue("crawler-queue", connection=redis_conn)

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE,
        depth INTEGER,
        metadata JSONB
    )
""")
conn.commit()

def save_page(url, depth, metadata):
    cur.execute("""
        INSERT INTO pages (url, depth, metadata)
        VALUES (%s, %s, %s)
        ON CONFLICT (url) DO UPDATE SET metadata = EXCLUDED.metadata
    """, (url, depth, metadata))
    conn.commit()

@job(queue)
def crawl_page(url, depth, max_depth):
    if depth > max_depth:
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    metadata = {
        "title": soup.title.string if soup.title else None,
        "description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else None,
    }

    save_page(url, depth, metadata)

    for link in soup.find_all("a", href=True):
        absolute_url = urljoin(url, link["href"])
        parsed_url = urlparse(absolute_url)
        if parsed_url.scheme in ["http", "https"] and parsed_url.netloc == urlparse(url).netloc:
            queue.enqueue_call(crawl_page, args=(absolute_url, depth + 1, max_depth), timeout=3600)

def start_crawler(domain, max_depth):
    initial_url = f"http://{domain}"
    queue.enqueue_call(crawl_page, args=(initial_url, 0, max_depth), timeout=3600)

if __name__ == "__main__":
    start_crawler("example.com", 2)