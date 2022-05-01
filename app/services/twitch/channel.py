import time
import json
import typing
import random
import string
import asyncio
import datetime

import websockets
from websockets import client


def generate_nonce(length: int) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class PubSub:
    def __init__(self):
        self._websocket: typing.Optional[websockets.client.WebSocketClientProtocol] = None

        self._initialized = False
        self._event_callback = None
    
    @property
    def initialized(self) -> bool:
        return self._initialized
    
    def set_event_callback(self, function) -> None:
        self._event_callback = function
    
    async def ping(self):
        await self._websocket.send(json.dumps({
            "type": "PING"
        }))
    
    async def listen(self, topic: str, target_id: str, auth_token: str):
        await self._websocket.send(json.dumps({
            "type": "LISTEN",
            "nonce": generate_nonce(30),
            "data": {
                "topics": [
                    f"{topic}.{target_id}"
                ],
                "auth_token": auth_token
            }
        }))

    async def initialize(self):
        await self.ping()

        self._initialized = True
    
    async def process(self, message: str):
        processed_message = message.strip()
        processed_data = json.loads(processed_message)

        if self._event_callback:
            await self._event_callback(processed_data)
    
    async def run(self):
        last_ping = time.time()
        self._websocket = await websockets.client.connect("wss://pubsub-edge.twitch.tv/v1")

        while True:
            try:
                if not self._initialized:
                    await self.initialize()
                
                message = await asyncio.wait_for(self._websocket.recv(), timeout=10)

                await self.process(message)

            except asyncio.TimeoutError:
                if last_ping + (4 * 60) < time.time():
                    await self.ping()
                    last_ping = time.time()



def process_time_string(date_string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")


class Stream:
    def __init__(self, data: dict = None):
        self.id: int = None
        self.title: typing.Optional[str] = None
        self.type: typing.Optional[str] = None
        self.viewers_count: typing.Optional[int] = None
        self.created_at: typing.Optional[datetime.datetime] = None
        self.game_name: typing.Optional[str] = None

        if data: self.update(data)
    
    def update(self, data: dict) -> None:
        self.id = int(data['id']) if data.get('id') else None
        self.viewers_count = int(data['viewersCount']) if data.get('viewersCount') else None

        self.title = data.get('title')
        self.type = data.get('type')

        if data.get('createdAt'):
            self.created_at = process_time_string(data['createdAt'])
        
        if data.get('game'):
            self.game_name = data['game']['name']


class Channel:
    def __init__(self, data: dict = None):
        self.id: int = None
        self.name: typing.Optional[str] = None
        self.display_name: typing.Optional[str] = None
        self.created_at: typing.Optional[str] = None
        self.stream: typing.Optional[Stream] = None

        if data: self.update(data)

    @property
    def is_streaming(self) -> bool:
        return self.stream is not None
    
    def update(self, data: dict) -> None:
        self.id = int(data['id']) if data.get('id') else None

        self.name = data.get('login')
        self.display_name = data.get('displayName')

        if data.get('createdAt'):
            self.created_at = process_time_string(data['createdAt'])
        
        self.is_partner = data.get('roles', {}).get('isPartner', False)

        if data.get('stream') is not None:
            self.stream = Stream(data['stream'])