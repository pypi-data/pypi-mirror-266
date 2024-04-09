def getByDot(obj, ref):
    """
    Use MongoDB style 'something.by.dot' syntax to retrieve objects from Python dicts.

    This also accepts nested arrays, and accommodates the '.XX' syntax that variety.js
    produces.

    Usage:
       >>> x = {"top": {"middle" : {"nested": "value"}}}
       >>> q = 'top.middle.nested'
       >>> getByDot(x,q)
       "value"
    """
    val = obj
    tmp = ref
    ref = tmp.replace(".XX", "[0]")
    if tmp != ref:
        print("Warning: replaced '.XX' with [0]-th index")
    for key in ref.split('.'):
        idstart = key.find("[")
        embedslist = 1 if idstart > 0 else 0
        if embedslist:
            idx = int(key[idstart + 1:key.find("]")])
            kyx = key[:idstart]
            try:
                val = val[kyx][idx]
            except IndexError:
                print("Index: x['{}'][{}] does not exist.".format(kyx, idx))
                raise
        else:
            if val:
                val = val.get(key)
            else:
                val = None
    return (val)