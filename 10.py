import json
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Simulate database connection
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables based on configuration
for table in config['tables']:
    cursor.execute(table['create_query'])
    conn.commit()

# Define endpoints dynamically
for endpoint in config['endpoints']:
    method = endpoint['method'].lower()
    path = endpoint['path']

    @app.route(path, methods=[method.upper()])
    def dynamic_endpoint():
        if method == 'get':
            cursor.execute(endpoint['query'])
            rows = cursor.fetchall()
            return jsonify(rows)
        elif method == 'post':
            data = request.json
            cursor.execute(endpoint['query'], tuple(data.values()))
            conn.commit()
            return jsonify({"message": "Data inserted successfully"})
        elif method == 'put':
            data = request.json
            cursor.execute(endpoint['query'], tuple(data.values()))
            conn.commit()
            return jsonify({"message": "Data updated successfully"})
        elif method == 'delete':
            data = request.json
            cursor.execute(endpoint['query'], tuple(data.values()))
            conn.commit()
            return jsonify({"message": "Data deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)