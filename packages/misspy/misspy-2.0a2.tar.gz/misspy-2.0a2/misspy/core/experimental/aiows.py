"""
aiohttp Engine
"""
import traceback

import aiohttp
# from tenacity import retry, TryAgain, wait_random

class MSC:
    """
    MSC (Misskey Streaming Client) is an asynchronous client for Misskey StreamingAPI that rewrites MiWS in aiohttp.
    """

    def __init__(
        self,
        address: str,
        i: str,
        handler,
        reconnect: bool=False,
        ssl: bool=True
    ) -> None:
        """MSC (Misskey Streaming Client) is an asynchronous client for Misskey StreamingAPI that rewrites MiWS in aiohttp.

        Args:
            address (str): Misskey Server Address
            i (str): Misskey API Token
            handler (function): Function to receive json received via Websocket
            reconnect (bool, optional): If True, reconnects on disconnect. Defaults to False.
        """
        self.address = address
        self.i = i
        self.reconnect = reconnect
        self.handler = handler
        self.session = aiohttp.ClientSession()
        self.urlfmt = "://"
        if ssl:
            self.urlfmt = "s://"

    # @retry(wait=wait_random(min=1, max=5))
    async def start(self):
        async with self.session.ws_connect('ws{}{}/streaming?i={}'.format(self.urlfmt, self.address, self.i)) as self.ws:
            await self.handler({"type": "__internal", "body": {"type": "ready"}})
            recv = await self.ws.receive_json()
            await self.handler(recv)
            while True:
                try:
                    recv = await self.ws.receive_json()
                    await self.handler(recv)
                except Exception as e:
                    await self.handler({"type": "__internal", "body": {"type": "exception", "errorType": e.__class__.__name__, "exc": traceback.format_exc(), "exc_obj": e}})
                    """
                    if self.reconnect:
                        raise TryAgain
                    """

    async def connect_channel(self, channel: str, id: str=None): 
        if id is None:
            id = channel
        await self.ws.send_json({"type": 'connect', "body": {"channel": channel, "id": id, "params": {}}})