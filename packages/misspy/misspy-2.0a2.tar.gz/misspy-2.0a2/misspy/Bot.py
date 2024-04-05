import asyncio
from functools import partial
from typing import Union
import logging

from .core.http import AsyncHttpHandler, HttpHandler
from .core.types.note import Note
from .core.types.user import User
from .core.types.internal import error
from .core.exception import MisskeyAPIError, ClientException

from .endpoints.drive import drive
from .endpoints.notes import notes
from .endpoints.reaction import reactions

from .settings import extension

from .flags import misspy_flag

class Bot:
    def __init__(
        self,
        address: str,
        i: Union[str, None]
    ) -> None:
        self.apierrors = []
        # self.Flag = misspy_flag()
        self.logger = logging.getLogger("misspy")
        self.address = address
        self.i = i
        self.flag = misspy_flag
        self.ssl = self.flag.ssl
        self.ext = extension
        self.http = AsyncHttpHandler(self.address, self.i, self.ssl, logger=self.logger)
        self.http_sync = HttpHandler(self.address, self.i, self.ssl)
        self.user: User = User(**self.__i())


        self.endpoint_list = self.endpoints()

        # ---------- endpoints ------------
        self.notes = notes(self.address, self.i, self.ssl, endpoints=self.endpoint_list, handler=self.http)
        self.drive = drive(self.address, self.i, self.ssl, endpoints=self.endpoint_list, handler=self.http)
        self.reactions = reactions(self.address, self.i, self.ssl, endpoints=self.endpoint_list, handler=self.http)
        # ---------------------------------

    def __i(self):
        return self.http_sync.send("i", data={})


    def endpoints(self):
        return self.http_sync.send("endpoints", data={})

    def run(self, reconnect=False):
        self.ws = self.flag.engine(
            self.address, self.i, self.handler, reconnect, self.ssl
        )
        asyncio.run(self.ws.start())

    async def connect(self, channel, id=None):
        await self.ws.connect_channel(channel, id)

    async def handler(self, json: dict):
        if json["type"] == "channel":
            if json["body"]["type"] == "note":
                json["body"]["body"]["api"] = {}
                json["body"]["body"]["api"]["reactions"] = {}
                json["body"]["body"]["api"]["reactions"]["create"] = partial(self.reactions.create, noteId=json["body"]["body"]["id"])
                json["body"]["body"]["api"]["reactions"]["delete"] = partial(self.reactions.delete, noteId=json["body"]["body"]["id"])
                json["body"]["body"]["api"]["reply"] = partial(self.notes.create, replyId=json["body"]["body"]["id"])
                json["body"]["body"]["api"]["renote"] = partial(self.notes.create, renoteId=json["body"]["body"]["id"])
                pnote = Note(**json["body"]["body"])
                for func in extension.exts["note"]:
                    await func(pnote)
            if json["body"]["type"] == "followed":
                for func in extension.exts["followed"]:
                    await func()
        elif json["type"] == "__internal":
            if json["body"]["type"] == "ready":
                for func in extension.exts["ready"]:
                    await func()
            elif json["body"]["type"] == "exception":
                if not extension.exts["error"] == []:
                    eb = {
                        "type": json["body"]["errorType"],
                        "exc": json["body"]["exc"],
                        "exc_obj": json["body"]["exc_obj"]
                    }
                    for func in extension.exts["error"]:
                        await func(error(**eb))
                else:
                    if json["body"]["errorType"] in self.apierrors:
                        raise MisskeyAPIError(json["body"]["exc"])
                    else:
                        raise ClientException(json["body"]["exc"])