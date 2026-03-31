import os
import threading
import time
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv

# SQLite database to track processed files
conn = sqlite3.connect('processed_files.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS files (filename TEXT PRIMARY KEY)''')
conn.commit()

def process_csv(file_path):
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)  # Replace with actual processing logic
        # Mark file as processed
        cursor.execute("INSERT INTO files (filename) VALUES (?)", (file_path,))
        conn.commit()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.csv'):
            if not self.is_file_processed(event.src_path):
                threading.Thread(target=process_csv, args=(event.src_path,)).start()

    def is_file_processed(self, file_path):
        cursor.execute("SELECT 1 FROM files WHERE filename = ?", (file_path,))
        return cursor.fetchone() is not None

if __name__ == "__main__":
    path = './csv_folder'  # Replace with your actual folder path
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    conn.close()