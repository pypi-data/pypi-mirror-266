from .core.exception import AlreadyRegisted, NotRegisted

class extension:
    exts = {
        "note": [],
        "followed": [],
        "ready": []
    }
    extId = {}

    def on(event, func):
        if extension.extId.get(func.__name__):
            raise AlreadyRegisted("Function {} is Already Registed in {}.".format(func.__name__, extension.extId[func.__name__]))
        else:
            if extension.exts.get(event) is None:
                extension.exts[event] = []
            extension.exts[event].append(func)
            extension.extId[func.__name__] = event
            return True

    def rm(func):
        if extension.extId.get(func.__name__) is None:
            raise NotRegisted("Function {} is Not Registed.".format(func.__name__))
        else:
            if extension.exts.get(extension.extId[func.__name__]) is None:
                return False
            extension.exts[extension.extId[func.__name__]].remove(func)
            extension.extId.pop(func.__name__)
            return True