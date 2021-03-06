from enum import Enum
from typing import List
import os
import logging
from pathlib import Path

from kython.ktyping import PathIsh

# TODO remove this (used in cgit?)
def apply_on(predicate, root: str, action):
    from os import walk
    for dp, dirs, files in walk(root):
        if predicate(dp, dirs, files):
            action(dp)
    # TODO do not walk inside... ?
    # but for now it's fine, works quick enough..


# TODO ugh. need a better name...
class Go(Enum):
    BAIL = 'bail'
    REC  = 'recurse'


def traverse(root: PathIsh, handler, logger=None):
    if logger is None:
        logger = logging.getLogger('fs-traverse')
    for root, dirs, files in os.walk(root):
        res = handler(Path(root), dirs, files) # TODO map all to Path? 
        if res == Go.BAIL:
            logger.info('skipping %s', root) # TODO reason would be nice?
            dirs[:] = []

# TODO if returns None, that means REC?
# def handler2(path: Path, is_dir: bool):
#     pass

def traverse2(root: PathIsh, handler): # TODO default handler?? just traverse all??
    root = Path(root)
    assert root.is_dir() # TODO Not sure
    for r, dirs, files in os.walk(root, followlinks=True):
        rr = Path(r)
        res = handler(rr, is_dir=True)
        if res == Go.BAIL:
            dirs[:] = []
        else:
            for f in files:
                handler(rr / f, is_dir=False)


def test(tmp_path):
    tdir = Path(tmp_path)
    a = tdir / 'a'
    aa = a / 'a'
    ab = a / 'b'
    b = tdir / 'b'
    bc = b / 'c'
    for d in [a, aa, ab, b, bc]:
        d.mkdir()

    from os.path import basename
    collected = set()
    def handler(root, dirs, files):
        if basename(root) == 'b':
            return Go.BAIL
        collected.add(root)
    traverse(tdir, handler)
    assert collected == {tdir, a, aa}
