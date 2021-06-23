"""
websocket client which keeps consuming payload from the server.
"""


import asyncio
import json

import websockets

URI = "ws://localhost:8000/ws/consumer"


async def show_live_stream():

    try:

        async with websockets.connect(URI) as websocket:

            while True:

                recv_payload = await websocket.recv()
                recv_payload = json.loads(recv_payload)
                yield recv_payload

    except websockets.exceptions.ConnectionClosedError as e:
        print(e, "websocket unexpectedly closed!")


async def main():

    async for payload in show_live_stream():
        print(f"-> payload_received :: ", payload)


if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(main())
