from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from ot import apply_op, compose, Op, inverse
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

documents = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    if room not in documents:
        documents[room] = {"content": "", "version": 0, "ops": []}
    emit("update", documents[room], room=room)
    emit("join", {"username": username}, room=room)

@socketio.on("leave")
def on_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    emit("leave", {"username": username}, room=room)

@socketio.on("edit")
def on_edit(data):
    room = data["room"]
    username = data["username"]
    start = data["start"]
    delete = data["delete"]
    insert = data["insert"]
    document = documents[room]

    op = Op(start, delete, insert)
    inverse_op = inverse(op)

    document["content"] = apply_op(document["content"], op)
    document["ops"].append(op)
    document["version"] += 1

    emit("update", document, room=room, include_self=False)

    for other_op in document["ops"][:document["version"] - 1]:
        op = compose(op, other_op)

    document["content"] = apply_op(document["content"], inverse_op)
    document["ops"] = document["ops"][:document["version"] - 1]
    document["version"] -= 1

    emit("update", document, to=request.sid)

if __name__ == "__main__":
    socketio.run(app, debug=True)