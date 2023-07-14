import aio_pika
import asyncio
import json
import uuid
from collections import defaultdict
from typing import MutableMapping

LOOP = asyncio.new_event_loop()

class RabbitMQ:
    def __init__(self, url: str):
        self.connection = None
        self.url: str = url
        self.q: MutableMapping[str, asyncio.Future] = {}
        self.loop = LOOP

    async def connect(self) -> "RabbitMQ":
        self.connection = await aio_pika.connect(self.url, loop=self.loop)
        self.channel = await self.connection.channel()

        self.callback_queue = await self.channel.declare_queue(exclusive=True)

        await self.callback_queue.consume(self.on_response, no_ack=True)

        return self

    async def basic_publish(self, queue_name: str, data: bytes) -> None:
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=data), routing_key=queue_name
        )

    async def basic_publish_dict(self, queue_name: str, data: dict) -> None:
        data = json.dumps(data).encode("utf-8")
        await self.basic_publish(queue_name, data)

    async def on_response(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")

            return
        
        future: asyncio.Future = self.q.pop(message.correlation_id)
        future.set_result(json.loads(message.body))

    async def call(self, queue_name: str, data: dict):
        correlation_id = str(uuid.uuid4())
        x = self.loop.create_future()
        self.q[correlation_id] = x
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                json.dumps(data).encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=queue_name,
        )
        return await asyncio.ensure_future(x)


r = RabbitMQ("amqp://guest:guest@192.168.1.28")