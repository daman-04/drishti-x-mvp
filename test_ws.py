import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8000/ws/stream") as websocket:
        print("Connected to stream")
        msg = await websocket.recv()
        data = json.loads(msg)
        print("Received frame. Size:", len(data['frame']))
        print("Detections:", data['detections'])

asyncio.run(test())
