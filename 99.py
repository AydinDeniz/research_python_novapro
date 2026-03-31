# Prompt 99

import os
import requests
import subprocess
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import schedule
import time

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Store execution logs
def store_log(script_url, args, output, return_code):
    es.index(index='script_executions', document={
       'script_url': script_url,
        'args': args,
        'output': output,
       'return_code': return_code,
        'timestamp': time.time()
    })

# Fetch and execute script
def execute_script(script_url, args=[]):
    try:
        response = requests.get(script_url)
        response.raise_for_status()
        script_content = response.text
        script_file = 'temp_script.py'
        with open(script_file, 'w') as file:
            file.write(script_content)
        result = subprocess.run(['python', script_file] + args, capture_output=True, text=True)
        os.remove(script_file)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return str(e), '', 1

# Schedule script execution
def schedule_execution(script_url, args, schedule_time):
    schedule.every().day.at(schedule_time).do(execute_and_store, script_url, args)

def execute_and_store(script_url, args):
    output, error, return_code = execute_script(script_url, args)
    store_log(script_url, args, output + error, return_code)

# REST API endpoints
@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    script_url = data.get('script_url')
    args = data.get('args', [])
    output, error, return_code = execute_script(script_url, args)
    store_log(script_url, args, output + error, return_code)
    return jsonify({'output': output, 'error': error,'return_code': return_code})

@app.route('/schedule', methods=['POST'])
def schedule_script():
    data = request.json
    script_url = data.get('script_url')
    args = data.get('args', [])
    schedule_time = data.get('schedule_time')
    schedule_execution(script_url, args, schedule_time)
    return jsonify({'message': 'Script scheduled successfully'})

@app.route('/logs', methods=['GET'])
def get_logs():
    res = es.search(index='script_executions', body={"query": {"match_all": {}}})
    logs = res['hits']['hits']
    return jsonify([hit['_source'] for hit in logs])

if __name__ == '__main__':
    schedule.run_pending()
    app.run(debug=True)