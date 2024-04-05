from typing import List

from pydantic import dataclasses

@dataclasses.dataclass(config=dict(extra="allow"))
class App:
    id: str
    name: str
    callbackUrl: str
    permission: List[str]
    secret: str