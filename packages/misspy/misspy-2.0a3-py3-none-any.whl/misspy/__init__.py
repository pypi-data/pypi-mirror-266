from importlib.metadata import version

from mitypes.drive import DriveFolder, df_property, DriveFile
from mitypes.user import AvatarDecorations, User, UserLite
from mitypes.poll import Poll

from .Bot import Bot

from .core import websocket
from .core.experimental import aiows
from .core.types import *  # noqa: F403
from .core.types.note import Note
from .settings import Option, extension  # noqa: F401

__version__ = version("misspy")

MSC = aiows.MSC  # Misskey
MIWS_V2 = websocket.MiWS_V2

homeTimeline = "homeTimeline"
localTimeline = "localTimeline"
socialTimeline = "hybridTimeline"
hybridTimeline = "hybridTimeline"
globalTimeline = "globalTimeline"

class visibility:
    public = "public"
    home = "home"
    followers = "followers"
    specified = "specified"
