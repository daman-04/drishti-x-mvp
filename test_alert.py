import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8000/ws/alerts") as websocket:
        print("Connected to alerts")
        while True:
            msg = await websocket.recv()
            print("Alert:", msg)

asyncio.run(test())
