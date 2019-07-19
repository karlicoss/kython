from collections import OrderedDict

from datetime import datetime, timedelta, date

import re

from pathlib import Path
import functools
from itertools import groupby, islice
import json
from json import load as json_load, loads as json_loads
from enum import Enum
import os
from os.path import isfile
from pprint import pprint
import sys
from typing import List, Set, Dict, Iterable, TypeVar, Callable, Tuple, Optional, NamedTuple, NewType, Any, Union, Iterator, Collection, Sequence, cast

NAN = float('nan')

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

NUMERIC_CONST_PATTERN =  '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'

def the(l: Iterable[A]) -> A:
    it = iter(l)
    try:
        first = next(it)
    except StopIteration as ee:
        raise RuntimeError(ee)
    assert all(e == first for e in it)
    return first

def import_relative(___name___: str, mname: str):
    import importlib
    parent_name = '.'.join(___name___.split('.')[:-1])
    module = importlib.import_module(mname, parent_name)
    return module

def module_items(module) -> "OrderedDict[str, Any]":
    return OrderedDict((name, getattr(module, name)) for name in dir(module))

def import_from(path, name):
    import sys
    try:
        sys.path.append(path)
        import importlib
        return importlib.import_module(name)
    finally:
        sys.path.remove(path)



def listdir_abs(d: str):
    from os.path import join
    from os import listdir
    return [join(d, n) for n in sorted(listdir(d))]

def _identity(v: T) -> V:
    return cast(V, v)

def make_dict(l: Iterable[T], key: Callable[[T], K], value: Callable[[T], V]=_identity) -> Dict[K, V]:
    # pylint: disable=unsubscriptable-object
    res: OrderedDict[K, V] = OrderedDict()
    for i in l:
        k = key(i)
        v = value(i)
        pv = res.get(k, None) # type: ignore
        if pv is not None:
            raise RuntimeError(f"Duplicate key: {k}. Previous value: {pv}, new value: {v}")
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

def get_networks() -> Optional[Iterable[str]]:
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


DatetimeIsh = Union[datetime, str, int]

# TODO deprecate all these..
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

def parse_timestamp(ts: DatetimeIsh) -> datetime: # TODO return??
    if isinstance(ts, datetime):
        return ts
    elif isinstance(ts, str):
        return parse_date(ts)
    elif isinstance(ts, int):
        return datetime.fromtimestamp(ts)
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
        return sum(res) / len(res) # type: ignore # TODO ugh, need protocol for 'divisible by int?'
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


def concat(*lists: Iterable[T]):
    res: List[T] = []
    for l in lists:
        res.extend(l)
    return res

lconcat = concat

def flatten(lists):
    return lconcat(*lists)

# pylint: disable=unsubscriptable-object
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

    def dump_group():
        nonlocal group
        if len(group) > 0:
            groups.append(group)
            group = []

    for i in range(len(l)):
        if handled[i]:
            continue

        assert len(group) == 0
        group = [l[i]]
        last = i
        cur = i + 1
        while cur < len(l) and cur - last <= dist:
            if similar(l[last], l[cur]):
                add_to_group(cur)
                last = cur
            cur += 1
        dump_group()
    return groups


# TODO careful about using the function above..
def group_by_comparator(l, similar):
    return group_by_cmp(l, similar, dist=1)


def test_group_by_cmp():
    l = [
        -5, 1, 2, 3, 6, 8, 5, 11, 13, 19
    ]
    groups = list(group_by_comparator(l, similar=lambda a, b: abs(a - b) <= 2))
    assert groups == [
        [-5],
        [1, 2, 3],
        [6, 8],
        [5],
        [11, 13],
        [19],
    ]


def numbers(from_=0) -> Iterator[int]:
    i = from_
    while True:
        yield i
        i += 1

def first(iterable):
    return next(iter(iterable))

def ichunks(l: Iterator[T], n: int):
    # TODO FIXME on mypy level
    if hasattr(l, '__iter__'):
        it = iter(l)
    else:
        it = l
    while True:
        ch = list(islice(it, 0, n))
        if len(ch) == 0:
            break
        yield ch


def chunks(l: Sequence[T], n: int): # no return type, fucking mypy can't handle str
    # TODO rewrite in terms of ichunks?
    for i in range(0, len(l), n):
        yield l[i:i + n]

def load_json_file(fname: str) -> JSONType:
    bb: bytes
    if fname.endswith('.xz'):
        import lzma
        with lzma.open(fname, 'r') as fo:
            bb = fo.read()
    else: # must be plaintext..
        with open(fname, 'rb') as fo:
            bb = fo.read()
    return json.loads(bb, encoding='utf8')





def json_dump_pretty(fo, j, indent=4):
    json.dump(j, fo, indent=indent, sort_keys=True, ensure_ascii=False)

def json_dumps_pretty(fo, j, indent=4):
    return json.dumps(j, indent=indent, sort_keys=True, ensure_ascii=False)

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
def setup_logging(level=None):
    import logging
    if level is None:
        level=logging.DEBUG

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

# TODO remove??
def memoize(f):
    cache = None
    def helper():
        nonlocal cache
        if not cache:
            cache = f()
        return cache
    return helper

def oset(*values):
    import collections
    return collections.OrderedDict([(v, None) for v in values])


# TODO fixme how to do this properly?
cache = functools.lru_cache(maxsize=1000)
cproperty = lambda f: property(cache(f))


# just to trick mypy
def fget(prop):
    assert isinstance(prop, property)
    return prop.fget

from .ktyping import PathIsh

from contextlib import contextmanager
@contextmanager
def extra_path(p: PathIsh):
    try:
        sys.path.append(str(p))
        yield
    finally:
        sys.path.pop()


def import_file(p: PathIsh, name=None):
    p = Path(p)
    if name is None:
        name = p.stem
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, p) # type: ignore
    foo = importlib.util.module_from_spec(spec)

    with extra_path(p.parent):
        # needed for local (same dir) imports
        # might not be enough for non top level imports..
        spec.loader.exec_module(foo) # type: ignore
    return foo


from functools import wraps
import time
import logging

def timed(func):
    lfunc = logging.warning
    @wraps(func)
    def wrapper(*args, **kwargs):
        fname = func.__name__
        start = time.time()
        lfunc('%s: running', fname)
        result = func(*args, **kwargs)
        end = time.time()
        lfunc("%s ran in %s", fname, round(end - start, 2))
        return result
    return wrapper

import traceback
def checkpoint():
    xx = traceback.extract_stack()[-2]
    tt = time.time()
    logging.warning('%s %s', xx, tt)


from .ktyping import NoneType

_C = TypeVar('_C')
_R = TypeVar('_R')

class classproperty:
    # https://stackoverflow.com/a/5192374/706389
    def __init__(self, f: Callable[[_C], _R]) -> None:
        self.f = f

    def __get__(self, obj: NoneType, cls: _C) -> _R:
        assert obj is None
        return self.f(cls)


def test_classproperty() -> None:
    class A:
        @classproperty
        # pylint: disable=no-self-argument
        def something(cls) -> str:
            return 'HELLO'

    assert A.something == 'HELLO'

