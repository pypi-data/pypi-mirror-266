from typing import Any

from pydantic import dataclasses

@dataclasses.dataclass(config=dict(extra="allow", arbitrary_types_allowed=True))
class reactions: # 以下同理由
    create: Any
    delete: Any

@dataclasses.dataclass(config=dict(extra="allow", arbitrary_types_allowed=True))
class APIAction: # anyは一時的。misspy.notes系を読み込むと循環インポートになって動かないからどうにかして解決したい
    reply: Any
    renote: Any
    reactions: reactions