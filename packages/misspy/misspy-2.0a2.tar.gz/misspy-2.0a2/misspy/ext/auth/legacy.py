from typing import Union, List

import aiohttp
from mitypes.user import User

from ...core.types.internal import auth_session
from ...core.types.other import App
from ...core.exception import AuthFailed

class session:
    def __init__(self) -> None:
        pass

    async def generate(
        self,
        host: str,
        name: str,
        description: str,
        permission: List[str],
        callback: Union[str, None] = None,
    ):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://{}/api/app/create".format(host), data={"name": name, "description": description, "permission": permission, "callbackUrl": callback}) as resp:
                authApp = App(**await resp.json())
                async with session.post("https://{}/api/auth/session/generate".format(host), data={"appSecret": authApp.secret}) as resp2:
                    resp2 = await resp2.json()
                    return auth_session(host, authApp.secret, resp2["token"], resp2["url"])

    async def check(
        self,
        authSession: auth_session
    ):
        async with aiohttp.ClientSession() as session:
            async with session.post("https://{}/api/auth/session/userkey".format(authSession.host)) as resp:
                resp = await resp.json()
                if resp.get("accessToken") is not None:
                    resp_i: dict = resp["user"]
                    resp_i["accessToken"] = resp["accessToken"]
                    return User(**resp_i)
                else:
                    raise AuthFailed(resp)