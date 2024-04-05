import urllib.parse
from typing import Union, List
import uuid

import aiohttp

from ...core.types.internal import miauth_session
from ...core.types.user import User
from ...core.exception import MiAuthFailed, NotFound

class session:
    def __init__(self) -> None:
        pass

    async def generate(
        self,
        host: str,
        name: Union[str, None] = None,
        icon: Union[str, None] = None,
        callback: Union[str, None] = None,
        permission: Union[List[str], None] = None,
    ):
        sessionId = uuid.uuid4()
        url = urllib.parse.urlparse("https://{}".format(host))
        params = urllib.parse.parse_qs(url.query)
        if name:
            params["name"] = name
        if icon:
            params["icon"] = icon
        if callback:
            params["callback"] = callback
        if permission:
            params["permission"] = ",".join(permission)
        generated_session = miauth_session(sessionId, host, urllib.parse.urlunparse(url._replace(query=urllib.parse.urlencode(params, doseq=True))), name, icon, callback, permission)
        return generated_session

    async def check(
        self,
        authSession: miauth_session
    ):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://{}/api/miauth/{}/check".format(authSession.host, authSession.sessionId)) as resp:
                try:
                    resp = await resp.json()
                except aiohttp.ContentTypeError:
                    raise NotFound('API endpoint "miauth/{}/check" does not exist. The version of Misskey you are using may be older than 12.27.0.'.format(authSession.sessionId))
                resp_i: dict = resp["user"]
                resp_i["token"] = resp["token"]
                if resp.get("token") is not None:
                    return User(**resp_i)
                else:
                    raise MiAuthFailed(resp)