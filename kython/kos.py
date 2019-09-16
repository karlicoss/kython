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
    # TODO handle windows properly? https://www.notthewizard.com/2014/06/17/are-files-appends-really-atomic/
    if len(enc) > 4096:
        logging.warning("writing out %s might be non-atomic (see https://stackoverflow.com/a/1154599/706389)", data)
    with path.open('ab') as fo:
        fo.write(enc)
