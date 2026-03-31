from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import ffmpeg
import os
import redis
import uuid
from PIL import Image

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# Redis for task queuing
redis_client = redis.Redis(host="localhost", port=6379, db=0)

@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    task_id = str(uuid.uuid4())
    redis_client.set(task_id, "queued")

    file.save(f"uploads/{task_id}.mp4")
    socketio.start_background_task(convert_video_to_gif, task_id)

    return jsonify({"task_id": task_id}), 202

def convert_video_to_gif(task_id):
    input_path = f"uploads/{task_id}.mp4"
    output_path = f"uploads/{task_id}.gif"

    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vf="fps=10,scale=320:-1:flags=lanczos")
            .run(overwrite_output=True)
        )

        # Optimize GIF
        with Image.open(output_path) as img:
            img.save(output_path, optimize=True)

        redis_client.set(task_id, "completed")
    except Exception as e:
        redis_client.set(task_id, f"failed: {str(e)}")

@app.route("/status/<task_id>")
def get_status(task_id):
    status = redis_client.get(task_id)
    if status:
        return jsonify({"status": status.decode("utf-8")})
    else:
        return jsonify({"status": "unknown"}), 404

@app.route("/download/<task_id>")
def download_gif(task_id):
    status = redis_client.get(task_id)
    if status and status.decode("utf-8") == "completed":
        return send_file(f"uploads/{task_id}.gif", as_attachment=True)
    else:
        return jsonify({"error": "GIF not available"}), 404

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("get_status")
def handle_get_status(task_id):
    status = redis_client.get(task_id)
    if status:
        emit("status_update", {"task_id": task_id, "status": status.decode("utf-8")})
    else:
        emit("status_update", {"task_id": task_id, "status": "unknown"})

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    socketio.run(app, debug=True)