from datetime import datetime, timedelta
from dateutil.parser import parse as __parse_date
import pytz

from itertools import groupby
import json
from json import load as json_load, loads as json_loads
from enum import Enum
import logging
import os
from os.path import isfile
from pprint import pprint
import sys
from typing import List, Set, Dict, Iterable, TypeVar, Callable, Tuple, Optional, NamedTuple, NewType, Any, Union

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')
K = TypeVar('K')


_KYTHON_LOGLEVEL_VAR = "KYTHON_LOGLEVEL"

def debug(s):
    sys.stderr.write(s + "\n")

def parse_date(s, dayfirst=True, yearfirst=False) -> datetime:
    if dayfirst and yearfirst:
        raise RuntimeError("dayfirst and yearfirst can't both be set to True")

    RTM_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    try:
        return datetime.strptime(s, RTM_FORMAT)
    except ValueError as e:
        # ok, carry on and use smart parser
        pass
    return __parse_date(s, dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=True) # TODO not sure about fuzzy..
    # TODO FIXME ok gonna need something smarter...
    # RTM dates are interpreted weirdly.
    # Maybe, hardcode rtm format and let other be interpreted with dateparser


def parse_timestamp(ts) -> Optional[datetime]: # TODO return??
    if isinstance(ts, datetime):
        return ts
    elif isinstance(ts, str):
        return parse_date(ts)
    else:
        raise RuntimeError("Unexpected class: " + str(type(ts)))
    # TODO do more handling!


def mavg(timestamps: List[datetime], values: List[T], window: Union[timedelta, int]) -> List[Tuple[datetime, T]]:
    if isinstance(window, int):
        window = timedelta(window)
    # TODO make more efficient
    def avg(fr, to):
        res = [v for t, v in zip(timestamps, values) if fr <= t <= to]
        # TODO zero len
        return sum(res) / len(res)
    return [(ts, avg(ts - window, ts)) for ts in timestamps]


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

# TODO kython
def enum_fields(enum_cls) -> List:
    return list(enum_cls._fields)

def lmap(f: Callable[[A], B], l: Iterable[A]) -> List[B]:
    return list(map(f, l))

def lfilter(f: Callable[[A], bool], l: Iterable[A]) -> List[A]:
    return list(filter(f, l))

def filter_only(p: Callable[[A], bool], l: Iterable[A]) -> A:
    values = lfilter(p, l)
    assert len(values) == 1
    return values[0]


def concat(*lists):
    res = []
    for l in lists:
        res.extend(l)
    return res


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


def src_relative(src_file: str, path: str):
    return os.path.join(os.path.dirname(os.path.abspath(src_file)), path)


# TODO atomic_write

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
