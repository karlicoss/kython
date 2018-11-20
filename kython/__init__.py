from .misc import *

def json_loadf(fname: str):
    import json
    with open(fname, 'r') as fo:
        return json.load(fo)
