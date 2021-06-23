"""
websocket client which keeps sending payload to the server.
"""

import asyncio
import datetime
import json
import random

import websockets

URI = "ws://localhost:8000/ws/producer"


async def initiate_production():

    try:

        async with websockets.connect(URI) as websocket:

            while True:

                payload = {
                    "timestamp": str(datetime.datetime.now()),
                    "value": random.randint(0, 100),
                }

                payload = json.dumps(payload)

                await websocket.send(payload)
                print(f"-> payload_sent :: {payload}")

                recv_payload = await websocket.recv()
                recv_payload = json.loads(recv_payload)

                await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosedError as e:
        print(e, "websocket unexpectedly closed!")


if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(initiate_production())
