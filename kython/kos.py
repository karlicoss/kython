import logging
from pathlib import Path

from kython.ktyping import PathIsh

def atomic_append(
        path: PathIsh,
        data: str,
):
    path = Path(path)
    # https://stackoverflow.com/a/13232181
    enc = data.encode('utf8')
    if len(enc) > 4096:
        logging.warning("writing out %s might be non-atomic", data)
    with path.open('ab') as fo:
        fo.write(enc)
