from itertools import groupby
from datetime import datetime
from dateutil.parser import parse as parse_date
import json
from json import load as json_load, loads as json_loads
import logging
import os
from os.path import isfile
from pprint import pprint
from typing import List, Set, Dict, Iterable, TypeVar, Callable, Tuple, Optional

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')
K = TypeVar('K')


_KYTHON_LOGLEVEL_VAR = "KYTHON_LOGLEVEL"


def TODO():
    raise RuntimeError("TODO")


def lmap(f: Callable[[A], B], l: Iterable[A]) -> List[B]:
    return [f(i) for i in l]


def group_by_key(l: Iterable[T], key: Callable[[T], K]) -> Dict[K, List[T]]:
    res = {} # type: Dict[K, List[T]]
    for i in l:
        kk = key(i)
        lst = res.get(kk, [])
        lst.append(i)
        res[kk] = lst
    return res


def json_dumps(fo, j):
    json.dump(j, fo, indent=4, sort_keys=True, ensure_ascii=False)


def setup_logging(level=logging.DEBUG):
    if _KYTHON_LOGLEVEL_VAR in os.environ:
        level = getattr(logging, os.environ[_KYTHON_LOGLEVEL_VAR]) # TODO ugh a bit ugly, but whatever..

    logging.basicConfig(level=level)
    try:
        import coloredlogs # type: ignore
        coloredlogs.install(fmt="%(asctime)s [%(name)s] %(levelname)s %(message)s")
        coloredlogs.set_level(level)
    except ImportError as e:
        if e.name == 'coloredlogs':
            logging.exception(e)
            logging.warning("Install coloredlogs for fancy colored logs!")
        else:
            raise e
    logging.getLogger('requests').setLevel(logging.CRITICAL)
