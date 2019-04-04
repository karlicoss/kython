def keq(j, *keys) -> bool:
    return list(sorted(j.keys())) == list(sorted(keys))

def akeq(j, *keys):
    if keq(j, *keys):
        return
    raise RuntimeError(f'expected dict to have keys {keys}, got {j.keys()}')


def dell(dd, *keys):
    for k in keys:
        del dd[k]


def zoom(dd, *keys):
    akeq(dd, *keys)
    vals = [dd[k] for k in keys]
    if len(keys) == 1:
        return vals[0] # eh, not sure...
    else:
        return vals
