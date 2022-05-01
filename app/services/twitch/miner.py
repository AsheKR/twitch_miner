import json
import typing
import asyncio

from .account import Account
from .channel import Channel

class TwitchMiner:
    def __init__(self, cookies: typing.List[str], channel_names: typing.List[str]):
        self.cookies = cookies
        self.account: Account = Account(cookies)
        self.channels: typing.List[Channel] = []

        self._channel_names: typing.List[str] = channel_names

    async def _find_channel_by_id(self, channel_id: int) -> typing.Optional[Channel]:
        for channel in self.channels:
            if channel.id == int(channel_id):
                return channel
    
    async def _update_event(self, event: dict) -> None:
        data: dict = event.get('data', {})

        if not data.get('topic') or not data.get('message'):
            return
        
        topic, user_id = data['topic'].rsplit('.', 1)
        message = json.loads(data['message'])

        if topic == 'stream-change-v1':
            channel = await self._find_channel_by_id(message['channel_id'])

            if not channel:
                return

            if message['type'] == 'stream_up' and not channel.is_streaming:
                channel.update(await self.account.fetch_channel(channel.name))
            elif message['type'] == 'stream_down' and channel.is_streaming:
                channel.stream = None
        elif topic == 'community-points-user-v1':
            if message['type'] == 'points-earned':
                channel = await self._find_channel_by_id(message['data']['balance']['channel_id'])
                print(
                    f"Gained {message['data']['point_gain']['total_points']} points "
                    f"({message['data']['balance']['balance']} total)",
                )
            elif message['type'] == 'claim-available':
                claim = message['data']['claim']
                channel = await self._find_channel_by_id(claim['channel_id'])

                await self.account.claim_points(channel, claim['id'])

    
    async def run(self) -> None:
        print('run TwitchMiner')
        await self.account.initialize_user()
        await self.account.initialize_websocket(self._update_event)

        for channel_name in self._channel_names:
            channel_data = await self.account.fetch_channel(channel_name)

            if not channel_data:
                continue

            self.channels.append(Channel(channel_data))
        
        if (len(self.channels)) < 1:
            raise Exception('No Valid Channels Were Found')
        
        for channel in self.channels:
            claim_id = await self.account.available_points(channel)

            if claim_id is not None:
                await self.account.claim_points(channel, claim_id)
        
        while True:
            await asyncio.sleep(60)

            tasks = []

            for channel in self.channels:
                if channel.is_streaming:
                    tasks.append(self.account.watch_minute(channel))
            
            await asyncio.gather(*tasks)