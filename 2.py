import threading
import queue
import requests
from urllib.robotparser import RobotFileParser
import time
import json

URLS = [
    'https://example.com/article1',
    'https://example.com/article2',
    'https://example.com/article3',
]
OUTPUT_FILE = 'scraped_data.json'
THROTTLE_DELAY = 2

def can_fetch(url):
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)

def scrape_url(url, results_queue):
    if can_fetch(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = {
                'url': url,
                'title': response.text.split('<title>')[1].split('</title>')[0]
            }
            results_queue.put(data)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
    else:
        print(f"Blocked by robots.txt: {url}")

def worker(url_queue, results_queue):
    while not url_queue.empty():
        url = url_queue.get()
        scrape_url(url, results_queue)
        url_queue.task_done()
        time.sleep(THROTTLE_DELAY)

def main():
    url_queue = queue.Queue()
    results_queue = queue.Queue()

    for url in URLS:
        url_queue.put(url)

    threads = []
    for _ in range(5):
        thread = threading.Thread(target=worker, args=(url_queue, results_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Scraped data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()