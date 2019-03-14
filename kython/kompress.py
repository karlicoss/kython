from pathlib import Path

import lzma

from .ktyping import PathIsh

def open(path: PathIsh, *args, **kwargs): # TODO is it bytes stream??
    pp = Path(path)
    suf = pp.suffix
    if suf in ('.xz',):
        return lzma.open(pp, *args, **kwargs)
    else:
        return pp.open(*args, **kwargs)

