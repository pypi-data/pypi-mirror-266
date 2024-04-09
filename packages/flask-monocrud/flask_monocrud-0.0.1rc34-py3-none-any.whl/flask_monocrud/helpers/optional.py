def optional(obj, key=None):
    if not obj:
        return None
    if not key:
        return obj
    if key:
        return obj[key]
