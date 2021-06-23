
# FastAPI websocket-producer-consumer flow

> “If curiosity killed the cat, it was satisfaction that brought it back.”
― Holly Black, Tithe

Have you ever had to forward a websocket connection to another websocket connection (in FastAPI)? Sounds like streaming from
one websocket to another websocket (in real-time). HOW TO DO THAT???

At small level people from [Golang](https://golang.org/) use [channels](https://gobyexample.com/channels), but at scale they
use workers and a message queue like [RabbitMQ](https://www.rabbitmq.com/)/[Redis](https://redis.io/). 

For us in Python community, we don't have the luxury of golang-like-channels. One day I found out how [Scala people use channels (a hack)](https://stackoverflow.com/a/20206475/6905674), they use Queues!!!. And that's when it clicked we have [`asyncio.Queue`](https://docs.python.org/3/library/asyncio-queue.html) too!. I had to try channels-like impelementation with Queues after seeing this.

<br>
<br>
<p align="center">
  <img src="https://i.postimg.cc/2SkGQ1Ty/nishinoya-trial.jpg" width="500" height="500" />
</p>
<br>
<br>


## Demonstration:

a websocket-client (producer, in our situation `ws_producer_client.py`) can keep sending payloads to the server, at the same time another websocket client (consumer, in our situation `ws_consumer_client.py`) can keep getting those updates. 

In the code below `server.py`, `producer_endpoint` coroutine takes care of the producer-websocket-client and `consumer_endpoint` coroutine takes care of the consumer-websocket-client. In between their communication is happening over asyncio.Queue (thus a producer-consumer workflow). 


```python
# server.py, run it with 
# λ uvicorn server:app

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
```

## Caveats

* `await queue.get()` in `consumer_endpoint` coroutine can block the server from shutting down. FastAPI throws: `INFO:     Waiting for background tasks to complete. (CTRL+C to force quit)`, even when the consumer-websocket-client had quit.


## Other information

* this is a very plain bland example, if you want to control which payloads should reach which consumer over websockets (meaning you don't want to broadcast). Then you can try the custom [`ConnectionManager` example](https://fastapi.tiangolo.com/advanced/websockets/?h=connection+manager#handling-disconnections-and-multiple-clients) from FastAPI docs, or even a dictionary based approach I recently made. [declaration](https://github.com/greed2411/central_electric/blob/c2f16f54987936b45902532dec467a0375e5a13d/app/main.py#L14) & [usage](https://github.com/greed2411/central_electric/blob/c2f16f54987936b45902532dec467a0375e5a13d/app/main.py#L89) of very own `websocket_connection_manager`.
* If not for a FastAPI, and just a pure producer-consumer model with asyncio runtime it is compeletely possible. I made a [gist on it](https://gist.github.com/greed2411/2ee4a723c6d67e874ed35525e87b2f30).
