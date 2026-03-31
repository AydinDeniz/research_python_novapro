from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict
import uuid

app = FastAPI()

# In-memory storage for active connections
active_connections: Dict[str, List[WebSocket]] = {}

# Simulated user authentication (replace with actual authentication logic)
users = {
    "user1": "password1",
    "user2": "password2"
}

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <input type="text" id="username" placeholder="Username"/>
        <input type="password" id="password" placeholder="Password"/>
        <button onclick="connect()">Connect</button>
        <input type="text" id="messageText" placeholder="Message"/>
        <button onclick="sendMessage()">Send</button>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            function connect() {
                var username = document.getElementById('username').value;
                var password = document.getElementById('password').value;
                if (!username || !password) {
                    alert('Please enter both username and password');
                    return;
                }
                ws = new WebSocket(`ws://localhost:8000/ws/${username}/${password}`);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
            }
            function sendMessage() {
                var input = document.getElementById('messageText')
                ws.send(input.value)
                input.value = ''
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{username}/{password}")
async def websocket_endpoint(websocket: WebSocket, username: str, password: str):
    if username not in users or users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    if username not in active_connections:
        active_connections[username] = []
    
    active_connections[username].append((session_id, websocket))
    
    try:
        while True:
            data = await websocket.receive_text()
            for session, ws in active_connections[username]:
                if ws != websocket:
                    await ws.send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        active_connections[username] = [(session, ws) for session, ws in active_connections[username] if ws != websocket]
        if not active_connections[username]:
            del active_connections[username]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)