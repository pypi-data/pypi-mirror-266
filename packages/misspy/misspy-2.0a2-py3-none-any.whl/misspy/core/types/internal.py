from typing import Union, List

from pydantic import dataclasses

@dataclasses.dataclass(config=dict(extra="allow"))
class mspy:
    tlId: str

@dataclasses.dataclass(config=dict(extra="allow"))
class error:
    type: str
    exc: str
    exc_obj: Exception

@dataclasses.dataclass()
class miauth_session:
    sessionId: str
    host: str
    url: str
    name: Union[str, None] = None
    icon: Union[str, None] = None
    callback: Union[str, None] = None
    permission: Union[List[str], None] = None

@dataclasses.dataclass()
class auth_session:
    host: str
    appSecret: str
    token: str
    url: str