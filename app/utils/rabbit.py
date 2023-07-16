import aio_pika
import asyncio
import json
import uuid
from collections import defaultdict
from typing import MutableMapping
from .enums import Queues, EmailTypes
from .exceptions import UserAlreadyExsistsException, UserNotFoundException

LOOP = asyncio.new_event_loop()


class Communicator:
    """class responsible for handling connections with microservices"""

    def __init__(self, url: str):
        self.url: str = url
        self.q: MutableMapping[str, asyncio.Future] = dict()
        self.loop = LOOP
        self.connection = None
        self.callback_queue = None
        self.channel = None

    async def connect(self) -> "Communitcator":
        """connects class with rabbit server"""
        self.connection = await aio_pika.connect(self.url, loop=self.loop)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_massage, no_ack=True)

    async def publish(self, queue_name: str, data: dict | str | bytes | int) -> None:
        """sends basic message to queue"""
        if type(data) is dict:
            data = json.dumps(data)
        else:
            data = str(data)
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=data.encode("utf-8")),
            routing_key=queue_name
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
                reply_to=self.callback_queue.name,
            ),
            routing_key=queue_name,
        )
        return await asyncio.ensure_future(future)

    async def close(
        self,
    ):
        """closes connection to rabbit"""
        await self.connection.close()

    @staticmethod
    def _parse_message_body(body: bytes) -> str | dict | int:
        """parses the message body (of type bytes) into str, dict or int."""
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            try:
                return int(body)
            except ValueError:
                return body.decode("utf-8")

    @staticmethod
    def _encode_data(data: str | int | dict) -> bytes:
        """parses data (of type str, int or dict) into bytes"""
        if type(data) is dict:
            return json.dumps(data).encode("utf-8")
        elif type(data) is int:
            return str(data).encode("utf-8")
        else:
            return data.encode("utf-8")

    def createSessioner(self) -> "Sessioner":
        """factory method to create sessioner"""
        return Communicator.Sessioner(self)

    def createMajor(self) -> "Mayor":
        """factory method to create mayor"""
        return Communicator.Mayor(self)

    def createEmailer(self) -> "Emailer":
        """factory method to create emailer"""
        return Communicator.Emailer(self)

    class _BaseSubClass:
        def __init__(self, communicator_instance: "Communicator"):
            self.communicator = communicator_instance

        def create(
            self,
        ) -> NotImplemented:
            raise NotImplementedError()

    class Sessioner(_BaseSubClass):
        """class to manage sessions"""

        async def create(self, identifier: str, password: str, **kwargs) -> str | None:
            """creates a new session"""
            user_profile = await self.communicator._call(Queues.User.FIND, identifier)
            if user_profile.get("status") == 404:
                raise UserNotFoundException(**user_profile)
            session_id: str = await self.communicator._call(
                Queues.Auth.LOGIN,
                {"id": str(user_profile["id"]), "password": password, **kwargs},
            )
            return session_id

    class Mayor(_BaseSubClass):
        """class to manage user profiles"""

        async def create(
            self, username: str, email: str, password: str
        ) -> tuple[None, None] | tuple[str, dict]:
            """creates a new user profile and returns verification id"""
            user_profile = await self.communicator._call(
                Queues.User.CREATE, {"username": username, "email": email}
            )
            if user_profile.get("status") == 409:
                raise UserAlreadyExsistsException(**user_profile)
            vid = await self.communicator._call(
                Queues.Auth.CREATE, {"password": password, "id": user_profile["id"]}
            )
            return vid, user_profile

        async def get_by_id(self, uid: str) -> dict:
            """returns user based on its id else none"""
            user_profile = await self.communicator._call(Queues.User.FIND_BY_ID, uid)
            if user_profile.get("status") == 404:
                raise UserNotFoundException(**user_profile)
            return user_profile

    class Emailer(_BaseSubClass):
        async def _send(self, recipient: str, typ: EmailTypes, **kwargs):
            await self.communicator.publish(
                Queues.EMAIL,
                {
                    "type": typ,
                    "recipient": recipient,
                    "subject": kwargs.pop("subject"),
                    "payload": {**kwargs},
                }
            )

        async def send_verification_mail(self, recipient: str, username: str, vid: str):
            await self._send(
                recipient,
                EmailTypes.VERIFY,
                subject="Verify your E-Mail",
                link="http://localhost:8000/auth/verify?token=" + vid,
                username=username,
            )


r = Communicator("amqp://guest:guest@192.168.1.28")
sessioner = r.createSessioner()
mayor = r.createMajor()
emailer = r.createEmailer()
