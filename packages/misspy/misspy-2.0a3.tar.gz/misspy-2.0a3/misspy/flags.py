from .core.websocket import MiWS_V2

class misspy_flag:
    CacheUser: bool = False
    engine = MiWS_V2 # misspy.MiWS_V2 or misspy.MSC
    ssl = True