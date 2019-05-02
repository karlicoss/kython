from enum import Enum
from typing import List
import os
import logging

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
        res = handler(root, dirs, files) # TODO map to Path?
        if res == Go.BAIL:
            logger.info('skipping %s', root) # TODO reason would be nice?
            dirs[:] = []
