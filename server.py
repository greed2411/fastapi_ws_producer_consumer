"""
FastAPI websocket implementation, for a weird producer-consumer websocket connections.

An endpoint which accepts a websocket connection gets the input stream
and forwards it to another output stream over a different websocket connection.

This script indirectly shows how you can use asyncio.Queue as a Golang-equivalent
channel to communicate in between python coroutines. That too when these corotuines 
are active websockets.
"""

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websockets import ConnectionClosedError

app = FastAPI()
queue = asyncio.Queue()


@app.websocket("/ws/producer")
async def producer_endpoint(websocket: WebSocket):
    """
    view function which handles all the incoming payload
    over websocket and acts as producer by dumping 
    those values into a asyncio.Queue.
    """

    await websocket.accept()

    try:

        while True:
            payload_to_be_produced = await websocket.receive_json()
            await queue.put(payload_to_be_produced)
            await websocket.send_json(payload_to_be_produced)

    except WebSocketDisconnect:
        print(f"producer dropped connection!")


@app.websocket("/ws/consumer")
async def consumer_endpoint(websocket: WebSocket):
    """
    view function which sends/broadcasts the payload 
    from the queue over established websockets.
    """

    await websocket.accept()

    try:

        while True:

            payload_to_be_consumed = await queue.get() # blocking if empty tho.
            await websocket.send_json(payload_to_be_consumed)
            queue.task_done()

    except (WebSocketDisconnect, ConnectionClosedError):
        print(f"consumer dropped connection!")
