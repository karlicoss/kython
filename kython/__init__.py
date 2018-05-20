from collections import OrderedDict

from datetime import datetime, timedelta, date

import re

from itertools import groupby
import json
from json import load as json_load, loads as json_loads
from enum import Enum
import logging
import os
from os.path import isfile
from pprint import pprint
import sys
from typing import List, Set, Dict, Iterable, TypeVar, Callable, Tuple, Optional, NamedTuple, NewType, Any, Union, Iterator, Collection, Sequence

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

NUMERIC_CONST_PATTERN =  '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'

def import_relative(___name___: str, mname: str):
    import importlib
    parent_name = '.'.join(___name___.split('.')[:-1])
    module = importlib.import_module(mname, parent_name)
    return module

def module_items(module) -> "OrderedDict[str, Any]":
    return OrderedDict((name, getattr(module, name)) for name in dir(module))


def listdir_abs(d: str):
    from os.path import join
    from os import listdir
    return [join(d, n) for n in listdir(d)]

def make_dict(l: List[T], key: Callable[[T], K], value: Callable[[T], V]) -> Dict[K, V]:
    res: Dict[K, V] = {}
    for i in l:
        k = key(i)
        v = value(i)
        assert k not in res, f"Duplicate key: {k}"
        res[k] = v
    return res

JSONType = Union[
    Dict[str, Any],
    List[Any],
]

AList = List[Any]

def id_map(x):
    return x

from abc import abstractmethod, ABCMeta
from typing_extensions import Protocol
class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other: Any) -> bool: pass
    @abstractmethod
    def __gt__(self, other: Any) -> bool: pass


_KYTHON_LOGLEVEL_VAR = "KYTHON_LOGLEVEL"

def debug(s):
    sys.stderr.write(s + "\n")

def get_networks() -> Iterable[str]:
    import subprocess
    import re
    # ugh, occasionally iwgetid would just return error code 255 despite connection being active in NM :(
    # output = check_output(['/sbin/iwgetid', '-r']).decode()
    proc = subprocess.run(['nmcli', '-t'], stdout=subprocess.PIPE)
    if proc.returncode != 0:
        return None
    output = proc.stdout.decode()
    matches = re.findall('connected to (.*)', output)
    return set(name.strip() for name in matches)

def parse_date_new(s) -> date:
    if isinstance(s, date):
        return s
    if isinstance(s, datetime):
        return s.date()

    import dateparser # type: ignore
    return dateparser.parse(s).date()

# TODO ugh, should return date, not datetime...
def parse_date(s, dayfirst=True, yearfirst=False) -> datetime:
    from dateutil.parser import parse as __parse_date
    import pytz
    if dayfirst and yearfirst:
        raise RuntimeError("dayfirst and yearfirst can't both be set to True")

    CUSTOM = [
        "%Y-%m-%dT%H:%M:%SZ", # RTM
    ]
    for fmt in CUSTOM:
        try:
            # not sure why python can't detect it's utc..
            return datetime.strptime(s, fmt).replace(tzinfo=pytz.UTC)
        except ValueError as e:
            # ok, carry on and use smart parser
            pass

    return __parse_date(s, dayfirst=dayfirst, yearfirst=yearfirst, fuzzy=True) # TODO not sure about fuzzy..
    # TODO FIXME ok gonna need something smarter...
    # RTM dates are interpreted weirdly.
    # Maybe, hardcode rtm format and let other be interpreted with dateparser

parse_datetime = parse_date


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


from typing_extensions import NoReturn

def TODO() -> NoReturn:
    raise RuntimeError("TODO")

def IMPOSSIBLE(value = None) -> NoReturn:
    raise AssertionError("Can't happen! " + str(value) if value is not None else '')


def lzip(*iters):
    return list(zip(*iters))


TT = TypeVar('TT', bound=Comparable)
def assert_increasing(l: List[TT]):
    for a, b in zip(l, l[1:]):
        if a > b:
            raise AssertionError("Expected {} < {}".format(a, b))

# TODO kython
def enum_fields(enum_cls) -> List:
    return list(enum_cls._fields)

def lmap(f: Callable[[A], B], l: Iterable[A]) -> List[B]:
    return list(map(f, l))

Predicate = Callable[[A], bool]
def lfilter(f: Predicate, l: Iterable[A]) -> List[A]:
    return list(filter(f, l))

def sfilter(f: Predicate, l: Iterable[A]) -> Set[A]:
    res: Set[A] = set()
    for i in l:
        if f(i):
            if i in res:
                raise RuntimeError(f"Duplicate element {i}")
            res.add(i)
    return res

def filter_only(p: Callable[[A], bool], l: Iterable[A]) -> A:
    values = lfilter(p, l)
    assert len(values) == 1
    return values[0]


def concat(*lists):
    res = []
    for l in lists:
        res.extend(l)
    return res

lconcat = concat

def flatten(lists):
    return lconcat(*lists)

def lsorted(s: Collection[T]) -> List[T]:
    return list(sorted(s))

def fmap_maybe(fn: Callable[[T], K], o: Optional[T]) -> Optional[K]:
    return None if o is None else fn(o)

def map_value(f, d: Dict) -> Dict:
    return {
        k: f(v) for k, v in d.items()
    }

def filter_by_value(p, d: Dict) -> Dict:
    return {
        k: v for k, v in d.items() if p(v)
    }


# TODO order might be not great.. swap params..
def group_by_key(l: Iterable[T], key: Callable[[T], K]) -> Dict[K, List[T]]:
    res = {} # type: Dict[K, List[T]]
    for i in l:
        kk = key(i)
        lst = res.get(kk, [])
        lst.append(i)
        res[kk] = lst
    return res

# TODO not sure, maybe do something smarter?
def group_by_cmp(l, similar, dist=20):
    handled = [False for _ in l]
    groups = []
    group = []

    def add_to_group(i):
        handled[i] = True
        group.append(l[i])

    for i in range(len(l)):
        if handled[i]:
            continue

        last = i
        cur = i
        while cur < len(l) and cur - last < dist:
            if similar(l[last], l[cur]):
                add_to_group(cur)
                last = cur
            cur += 1
        if len(group) > 0:
            groups.append(group)
            group = []
    return groups


def numbers(from_=0) -> Iterator[int]:
    i = from_
    while True:
        yield i
        i += 1

def first(iterable):
    return next(iter(iterable))

def chunks(l: Sequence[T], n: int): # no return type, fucking mypy can't handle str
    for i in range(0, len(l), n):
        yield l[i:i + n]

def json_dump_pretty(fo, j):
    json.dump(j, fo, indent=4, sort_keys=True, ensure_ascii=False)

def json_dumps(fo, j):
    json_dump_pretty(fo, j)

def src_relative(src_file: str, path: str):
    return os.path.join(os.path.dirname(os.path.abspath(src_file)), path)


def setup_logzero(logger, *args, **kwargs):
    import logzero # type: ignore
    formatter = logzero.LogFormatter(
        fmt='%(color)s[%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    )
    logzero.setup_logger(
        *args,
        **kwargs,
        name=logger.name,
        formatter=formatter,
    )


def get_logzero(*args, **kwargs):
    import logzero # type: ignore
    # ugh, apparently if you get one instance with formatter and another without specifying it, you will end up with default format :(
    formatter = logzero.LogFormatter(
        fmt='%(color)s[%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    )
    return logzero.setup_logger(
        *args,
        **kwargs,
        formatter=formatter,
    )


COLOREDLOGGER_FORMAT = "%(asctime)s [%(name)s] %(levelname)s %(message)s"

# TODO deprecate...
def setup_logging(level=logging.DEBUG):
    if _KYTHON_LOGLEVEL_VAR in os.environ:
        level = getattr(logging, os.environ[_KYTHON_LOGLEVEL_VAR]) # TODO ugh a bit ugly, but whatever..

    logging.basicConfig(level=level)
    try:
        import coloredlogs # type: ignore
        coloredlogs.install(fmt=COLOREDLOGGER_FORMAT)
        coloredlogs.set_level(level)
    except ImportError as e:
        if e.name == 'coloredlogs':
            logging.exception(e)
            logging.warning("Install coloredlogs for fancy colored logs!")
        else:
            raise e
    logging.getLogger('requests').setLevel(logging.CRITICAL)


def atomic_write(fname: str, mode: str, overwrite=True):
    import atomicwrites
    return atomicwrites.atomic_write(fname, overwrite=overwrite, mode=mode)

def elvis(*items):
    for i in items:
        if i:
            return i
    else:
        return None

def safe_get(d, *args, default=None):
    for a in args:
        if isinstance(d, dict) and a in d:
            d = d[a]
        elif hasattr(d, a):
            d = getattr(d, a)
        else:
            return default
    return d


import functools

def memoize(f):
    cache = None
    def helper():
        nonlocal cache
        if not cache:
            cache = f()
        return cache
    return helper
