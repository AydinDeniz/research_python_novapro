from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

app = FastAPI()

# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.chat_platform
messages_collection = db.messages

class Message(BaseModel):
    room: str
    user: str
    content: str
    timestamp: Optional[datetime] = None

class Mention(BaseModel):
    user: str

class SearchQuery(BaseModel):
    room: Optional[str] = None
    user: Optional[str] = None
    content: Optional[str] = None

@app.post("/messages/")
async def send_message(message: Message):
    message.timestamp = datetime.utcnow()
    await messages_collection.insert_one(message.dict())
    return message

@app.get("/messages/", response_model=List[Message])
async def get_messages(query: SearchQuery):
    query_filter = {}
    if query.room:
        query_filter["room"] = query.room
    if query.user:
        query_filter["user"] = query.user
    if query.content:
        query_filter["content"] = {"$regex": query.content, "$options": "i"}

    messages = await messages_collection.find(query_filter).to_list(length=100)
    return [Message(**msg) for msg in messages]

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message["room"] = room
            message["timestamp"] = datetime.utcnow()
            await messages_collection.insert_one(message)
            await websocket.send_text(f"Message text was: {message}")
    except WebSocketDisconnect:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)