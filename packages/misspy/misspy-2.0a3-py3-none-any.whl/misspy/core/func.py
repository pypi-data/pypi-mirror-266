def to(address: str, protocol: str, ssl=True):
    http = protocol + "://"
    https = protocol + "s://"
    if not address.startswith(http) and not address.startswith(https):
        address = http + address
        if ssl:
            address = https + address
        address_raw = address
    else:
        address = address
        address_raw = address.replace(https, "").replace(http, "")
    return {"address": address, "raw": address_raw}