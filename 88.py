# Prompt 88

import asyncio
import websockets
from collections import defaultdict

# In-memory storage for users and rooms
users = {}
rooms = defaultdict(list)
matches = []

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        action = data.get("action")
        
        if action == "login":
            username = data.get("username")
            ranking = data.get("ranking")
            users[username] = {"websocket": websocket, "ranking": ranking}
            await websocket.send(json.dumps({"status": "logged_in"}))
        
        elif action == "create_room":
            username = data.get("username")
            room_name = data.get("room_name")
            rooms[room_name].append(username)
            await websocket.send(json.dumps({"status": "room_created"}))
        
        elif action == "join_room":
            username = data.get("username")
            room_name = data.get("room_name")
            if room_name in rooms:
                rooms[room_name].append(username)
                await websocket.send(json.dumps({"status": "joined_room"}))
            else:
                await websocket.send(json.dumps({"status": "room_not_found"}))
        
        elif action == "chat":
            username = data.get("username")
            room_name = data.get("room_name")
            message = data.get("message")
            for user in rooms[room_name]:
                if user!= username:
                    await users[user]["websocket"].send(json.dumps({"chat": f"{username}: {message}"}))
        
        elif action == "find_match":
            username = data.get("username")
            ranking = users[username]["ranking"]
            matches.append((username, ranking))
            await websocket.send(json.dumps({"status": "searching_for_match"}))
            
            # Simple matchmaking based on ranking
            matches.sort(key=lambda x: x[1])
            if len(matches) >= 2:
                match = matches[:2]
                matches = matches[2:]
                await users[match[0][0]]["websocket"].send(json.dumps({"match": match[1][0]}))
                await users[match[1][0]]["websocket"].send(json.dumps({"match": match[0][0]}))

start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()