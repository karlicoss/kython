from .misc import json_load

def get_last_json(d: str):
    import os
    # TODO FIXME pattern, etc
    # TODO broken symlinks?, log warnings?
    last = max(os.listdir(d))
    with open(os.path.join(d, last), 'r') as fo:
        return json_load(fo)


def iter_files(d: str, regex: str='.*'):
    import re
    import os
    rr = re.compile(regex)
    for f in sorted(os.listdir(d)):
        if rr.search(f): # TODO search??
            yield os.path.join(d, f)

def get_all_files(*args, **kwargs):
    return list(iter_files(*args, **kwargs))

def get_last_file(*args, **kwargs):
    return max(iter_files(*args, **kwargs))

