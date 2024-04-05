from typing import List, Union

from mitypes import channel

from ..core.http import AsyncHttpHandler
from ..utils.internaltool import nonecheck


class channels:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.http = handler
        if handler is None:
            self.http = AsyncHttpHandler(address, i, ssl)
        self.endpoints = endpoints

    async def create(self, name, description=None, bannerId=None):
        return channel(
            **await self.http.send(
                "channels/create",
                {"name": name, "description": description, "bannerId": bannerId},
            )
        )

    async def update(self, channelId, name, description=None, bannerId=None):
        return channel(
            **await self.http.send(
                "channels/update",
                {
                    "channelId": channelId,
                    "name": name,
                    "description": description,
                    "bannerId": bannerId,
                },
            )
        )

    async def follow(self, channelId):
        return await self.http.send("channels/follow", {"channelId": channelId})

    async def unfollow(self, channelId):
        return await self.http.send("channels/unfollow", {"channelId": channelId})

    async def show(self, channelId):
        return channel(
            **await self.http.send("channels/show", {"channelId": channelId})
        )

    async def followed(self, sinceId=None, untilId=None, limit=5):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        data = []
        chs = await self.http.send("channels/followed", base)
        for ch in chs:
            data.append(channel(**ch))
        return data

    async def owned(self, limit=5, sinceId=None, untilId=None):
        base = {"limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        data = []
        chs = await self.http.send("channels/owned", base)
        for ch in chs:
            data.append(channel(**ch))
        return data

    async def featured(self):
        data = []
        chs = await self.http.send("channels/featured", {})
        for ch in chs:
            data.append(channel(**ch))
        return data
