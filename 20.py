# Prompt 20

import asyncio
import websockets

connected_clients = set()

async def chat_server(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            await broadcast(message)
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

start_server = websockets.serve(chat_server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()