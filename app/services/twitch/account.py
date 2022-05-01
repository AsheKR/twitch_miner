import json
import typing
import asyncio
import urllib
from base64 import b64encode

import aiohttp

from .channel import PubSub, Channel


CLIENT_ID = 'kimne78kx3ncx6brgo4mv6wki5h1ko'

operations = {}
query = """query findChannel($login: String!) {
  user(login: $login) {
    id
    login
    displayName
    description
    createdAt
    roles {
      isPartner
    }
    stream {
      id
      title
      type
      viewersCount
      createdAt
      game {
        name
      }
    }
  }
}"""
operations['find_channel'] = "\n".join([
    line
    for line
    in query.strip().splitlines()
    if not line.startswith("#")
])

hashes = {
    "ChannelPointsContext": "9988086babc615a918a1e9a722ff41d98847acac822645209ac7379eecb27152",
    "ClaimCommunityPoints": "46aaeebe02c99afdf4fc97c7c0cba964124bf6b0af229395f1f6d1feed05b3d0",
    "ChatRestrictions": "c951818670b7beab0f9332303f5a3824316e8d78423e6c6336f4235207b09e54",
	"FollowButton_FollowUser": "3efee1acda90efdff9fef6e6b4a29213be3ee490781c5b54469717b6131ffdfe",
}

class Account:
    def __init__(self, cookies: dict, default_headers: typing.Optional[dict] = None):
        self._cookies = cookies
        self._default_headers = default_headers

        self._websocket: typing.Optional[PubSub] = None
        self._spade_url: typing.Optional[str] = None

        self.username: typing.Optional[str] = None
        self.auth_token: typing.Optional[str] = None

        self.unique_id: typing.Optional[str] = None
        self.user_id: typing.Optional[str] = None
        self.client_id = CLIENT_ID

    async def fetch_twitch_gql(
        self,
        query_or_hash: str,
        variables: typing.Optional[dict] = None,
        is_persisted: bool = False
    ) -> dict:
        """ Perform a GraphQL request on Twitch's API. """
        data = {}

        if is_persisted:
            data.update({
                "operationName": query_or_hash,
                "extensions": {
                    "persistedQuery": {
                        "sha256Hash": hashes[query_or_hash],
                        "version": 1
                    }
                }
            })
        else:
            data["query"] = query_or_hash

        if variables:
            data["variables"] = variables

        headers = {
            "Authorization": f"OAuth {self.auth_token}",
            "Client-ID": self.client_id,
        }

        async with self.session as session:
            async with session.post("https://gql.twitch.tv/gql", json=[data], headers=headers, raise_for_status=True) as resp:
                return (await resp.json())[0]["data"]    

    @property
    def session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            headers=self._default_headers,
            cookies=self._cookies
        )
    
    async def get_spade_url(self) -> str:
        """ Get the Spade URL. If it is not set, fetch it. """
        if self._spade_url:
            return self._spade_url

        async with self.session as session:
            async with session.get("https://static.twitchcdn.net/config/settings.js", raise_for_status=True) as resp:
                data: dict = json.loads((await resp.text())[28:])

        self._spade_url = data.get("spade_url")

        return self._spade_url

    async def initialize_user(self) -> None:
        self.username = self._cookies.get('login')
        self.unique_id = self._cookies.get('unique_id')

        twilight_user_raw_data = self._cookies.get('twilight-user')
        twilight_user_parsed_data = urllib.parse.unquote(str(twilight_user_raw_data))
        twilight_user_data: dict = json.loads(twilight_user_parsed_data)
        self.auth_token = twilight_user_data.get('authToken')
        self.user_id = twilight_user_data.get('id')


    async def initialize_websocket(self, function) -> None:
        self._websocket = PubSub()

        if function:
            self._websocket.set_event_callback(function)
        
        asyncio.get_event_loop().create_task(self._websocket.run())

        while not self._websocket.initialized:
            await asyncio.sleep(1)
        
        await self._websocket.listen("stream-change-v1", self.user_id, self.auth_token)
        await self._websocket.listen("community-points-user-v1", self.user_id, self.auth_token)

    async def claim_points(self, channel: Channel, claim_id: str) -> None:
        """ Claim the 50 points with the given ID on the given channel. """
        print('Claim 50 Points from given channel')
        await self.fetch_twitch_gql("ClaimCommunityPoints", {
            "input": {
                "channelID": str(channel.id),
                "claimID": claim_id
            }
        }, is_persisted=True)

    async def available_points(self, channel: Channel) -> typing.Optional[str]:
        """ Returns the currently available reward claim's ID. """
        data = await self.fetch_twitch_gql("ChannelPointsContext", {
            "channelLogin": channel.name
        }, is_persisted=True)

        points: dict = data["community"]["channel"]["self"]["communityPoints"]

        if points.get("availableClaim") is None:
            return None
        
        return points["availableClaim"]["id"]
    

    async def watch_minute(self, channel: Channel) -> None:
        """
        Watch one minute of the given broadcast on the given channel.
        
        :param channel_id: ID of the channel.
        :param broadcast_id: ID of the specific broadcast.
        """

        data = {
            "event": "minute-watched",
            "properties": {
                "channel_id": channel.id,
                "broadcast_id": channel.stream.id,
                "user_id": self.user_id,
                "player": "site",
            }
        }

        async with self.session as session:
            await session.post(
                await self.get_spade_url(),
                data=b64encode(json.dumps([data]).encode("utf-8")),
                raise_for_status=True
            )
    
    async def fetch_channel(self, channel_name: str) -> typing.Optional[dict]:
        variables = {
            'login': channel_name
        }

        data = await self.fetch_twitch_gql(
            operations['find_channel'],
            variables
        )

        user = data['user']

        if user is None:
            return None

        return user