import aio_pika
import asyncio
import json
import uuid
from collections import defaultdict
from typing import MutableMapping

LOOP = asyncio.new_event_loop()


class Communicator:
    """class responsible for handling connections with microservices"""
    def __init__(self, url: str):
        self.url: str = url
        self.q = dict[str, asyncio.Future] = dict()
        self.loop = LOOP
        self.connection = None
        self.callback_queue = None
        self.channel = None

    async def connect(self) -> "Communitcator":
        """connects class with rabbit server"""
        self.connection = await aio_pika.connect(self.url, loop=self.loop)
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_massage, no_ack=True)#
    
    async def publish(self, queue_name: str, data: dict | str | bytes | int) -> None:
        """sends basic message to queue"""
        if type(data) is dict:
            data = json.dumps(data)
        else:
            data = str(data)
        channel = await self.connect.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=data.encode("utf-8"))
        )

    async def on_massage(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        """triggert when rpc message is received"""
        if message.correlation_id is None:
            return 
        future: asyncio.Future = self.q.pop(message.correlation_id)
        future.set_result(Communicator._parse_message_body(message.body))

    async def _call(self, queue_name: str, data: str | dict | int) -> None:
        """sends rpc message to queue"""
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.q[correlation_id] = future
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                Communicator._encode_data(data),
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name
            ),
            routing_key=queue_name
        )
        return await asyncio.ensure_future(x)

    @staticmethod
    async def _parse_message_body(body: bytes) -> str | dict | int:
        """parses the message body (of type bytes) into str, dict or int."""
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            try:
                return int(body)
            except ValueError:
                return body.decode("utf-8")

    @staticmethod
    async def _encode_data(data: str | int | dict) -> bytes:
        """parses data (of type str, int or dict) into bytes"""
        if type(data) is dict:
            return json.loads(data).encode("utf-8")
        elif type(data) is int:
            return str(data).encode("utf-8")
        else:
            return data.encode("utf-8")

r = Communicator("amqp://guest:guest@192.168.1.28")