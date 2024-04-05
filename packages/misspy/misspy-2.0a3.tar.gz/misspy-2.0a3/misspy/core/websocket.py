import traceback

import websockets
import orjson
#from tenacity import retry, TryAgain, wait_random


class MiWS_V2:
    """
    Version 2 of "MiWS". Speeds may be slower than MSC, but relatively stable.
    """

    def __init__(
        self,
        address: str,
        i: str,
        handler,
        reconnect: bool=False,
        ssl: bool=True
    ) -> None:
        """Version 2 of "MiWS". Speeds may be slower than MSC, but relatively stable.

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
        self.urlfmt = "://"
        if ssl:
            self.urlfmt = "s://"

    #@retry(wait=wait_random(min=1, max=5))
    async def start(self):
        async with websockets.connect('ws{}{}/streaming?i={}'.format(self.urlfmt, self.address, self.i)) as self.ws:
            await self.handler({"type": "__internal", "body": {"type": "ready"}})
            recv = orjson.loads(await self.ws.recv())
            await self.handler(recv)
            while True:
                try:
                    recv = orjson.loads(await self.ws.recv())
                    await self.handler(recv)
                except Exception as e:
                    await self.handler({"type": "__internal", "body": {"type": "exception", "errorType": e.__class__.__name__, "exc": traceback.format_exc(), "exc_obj": e}})
                """
                try:
                    recv = orjson.loads(await self.ws.recv())
                    await self.handler(recv)
                except:
                    if self.reconnect:
                        raise TryAgain
                    else:
                        raise websockets.ConnectionClosed
                """

    async def connect_channel(self, channel: str, id: str=None): 
        if id is None:
            id = channel
        await self.ws.send(orjson.dumps({"type": 'connect', "body": {"channel": channel, "id": id, "params": {}}}).decode('utf-8'))