from pathlib import Path

import lzma
from zipfile import ZipFile

from .ktyping import PathIsh

def open(path: PathIsh, *args, **kwargs): # TODO is it bytes stream??
    pp = Path(path)
    suf = pp.suffix
    if suf in ('.xz',):
        return lzma.open(pp, *args, **kwargs)
    elif suf in ('.zip',):
        return ZipFile(pp).open(*args, **kwargs)
    else:
        return pp.open(*args, **kwargs)

