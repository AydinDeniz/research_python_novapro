from flask import Flask, request, jsonify
import threading
import subprocess
import psutil
import signal
import time

app = Flask(__name__)

# Dictionary to store running tasks
tasks = {}

def execute_code(task_id, code, timeout, memory_limit):
    try:
        process = subprocess.Popen(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start_time = time.time()
        
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.kill()
                return jsonify(task_id=task_id, status="timeout", output="Execution timed out")
            
            mem_info = psutil.Process(process.pid).memory_info()
            if mem_info.rss > memory_limit * 1024 * 1024:
                process.kill()
                return jsonify(task_id=task_id, status="memory_limit_exceeded", output="Memory limit exceeded")
            
            time.sleep(0.1)
        
        stdout, stderr = process.communicate()
        output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
        return jsonify(task_id=task_id, status="success", output=output)
    
    except Exception as e:
        return jsonify(task_id=task_id, status="error", output=str(e))

@app.route('/submit', methods=['POST'])
def submit_code():
    code = request.json.get('code')
    timeout = request.json.get('timeout', 10)  # Default timeout is 10 seconds
    memory_limit = request.json.get('memory_limit', 100)  # Default memory limit is 100 MB
    
    if not code:
        return jsonify(error="Code is required"), 400
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = threading.Thread(target=execute_code, args=(task_id, code, timeout, memory_limit))
    tasks[task_id].start()
    
    return jsonify(task_id=task_id), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in tasks:
        return jsonify(error="Task not found"), 404
    
    if tasks[task_id].is_alive():
        return jsonify(task_id=task_id, status="running")
    
    del tasks[task_id]
    return jsonify(task_id=task_id, status="completed")

if __name__ == '__main__':
    app.run(debug=True)