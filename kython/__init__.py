from itertools import groupby

from datetime import datetime, timedelta
from dateutil.parser import parse as __parse_date
import pytz

import json
from json import load as json_load, loads as json_loads

import logging

import os
from os.path import isfile

import sys

from pprint import pprint

from typing import List, Set, Dict, Iterable, TypeVar, Callable, Tuple, Optional

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')
K = TypeVar('K')


_KYTHON_LOGLEVEL_VAR = "KYTHON_LOGLEVEL"

def debug(s):
    sys.stderr.write(s + "\n")

def parse_date(s):
    RTM_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    try:
        return datetime.strptime(s, RTM_FORMAT)
    except ValueError as e:
        # ok, carry on and use smart parser
        pass
    return __parse_date(s, dayfirst=True)
    # TODO FIXME ok gonna need something smarter...
    # RTM dates are interpreted weirdly.
    # Maybe, hardcode rtm format and let other be interpreted with dateparser

def TODO():
    raise RuntimeError("TODO")

def IMPOSSIBLE(value = None):
    raise AssertionError("Can't happen! " + str(value) if value is not None else '')


def lzip(*iters):
    return list(zip(*iters))


def assert_increasing(l: List[T]):
    for a, b in zip(l, l[1:]):
        if a > b:
            raise AssertionError("Expected {} < {}".format(a, b))


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


def chunks(l: List[T], n: int):
    for i in range(0, len(l), n):
        yield l[i:i + n]

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
