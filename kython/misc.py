import functools
import json
import os
import re
import sys
from collections import OrderedDict
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from enum import Enum
from itertools import groupby, islice
from json import load as json_load, loads as json_loads
from os.path import isfile
from pathlib import Path
from pprint import pprint
from typing import (Any, Callable, Collection, Dict, Iterable, Iterator, List,
    NamedTuple, NewType, Optional, Sequence, Set, Tuple, TypeVar, Union, cast)


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
        raise RuntimeError('Empty iterator?')
    assert all(e == first for e in it)
    return first

def import_relative(___name___: str, mname: str):
    import importlib
    parent_name = '.'.join(___name___.split('.')[:-1])
    module = importlib.import_module(mname, parent_name)
    return module

def module_items(module) -> "OrderedDict[str, Any]":
    return OrderedDict((name, getattr(module, name)) for name in dir(module))

from .kimport import import_from


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
    res: Dict[K, List[T]] = {}
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

def ichunks(l: Iterable[T], n: int) -> Iterator[List[T]]:
    it: Iterator[T] = iter(l)
    while True:
        chunk: List[T] = list(islice(it, 0, n))
        if len(chunk) == 0:
            break
        yield chunk


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
# TODO remove?
cache = functools.lru_cache(maxsize=1000)

import functools
from typing import TypeVar, Type, Callable
Cl = TypeVar('Cl')
R = TypeVar('R')

def cproperty(f: Callable[[Cl], R]) -> R:
    return property(functools.lru_cache(maxsize=1)(f)) # type: ignore

class _A:
    def __init__(self):
        self.xx = 0

    @cproperty
    def pr(self) -> str:
        self.xx += 1
        return 'value'

def test_cprop() -> None:
    a = _A()
    assert a.pr == 'value'
    assert a.pr == 'value'
    assert a.xx == 1



# just to trick mypy
def fget(prop):
    assert isinstance(prop, property)
    return prop.fget

from .ktyping import PathIsh

from .kimport import extra_path
from contextlib import contextmanager

def import_file(p: Union[str, Path], name=None):
    p = Path(p)
    if name is None:
        name = p.stem
    # TODO hmm. does it need to load parent??
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, p) # type: ignore
    foo = importlib.util.module_from_spec(spec)

    with extra_path(p.parent):
        # needed for local (same dir) imports
        # might not be enough for non top level imports..
        spec.loader.exec_module(foo) # type: ignore
    return foo


# https://stackoverflow.com/questions/653368/how-to-create-a-python-decorator-that-can-be-used-either-with-or-without-paramet
def doublewrap(f):
    '''
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec

from functools import wraps
import time
import logging


@contextmanager
def ccc(name: str, logger=None):
    if logger is None:
        logger = logging
    lfunc = logger.debug
    start = time.time()
    lfunc('%s: running', name)
    yield
    end = time.time()
    lfunc("%s ran in %s sec", name, round(end - start, 2))


def ctxmanager_magic(f):
    @wraps(f)
    def dec(*args, **kwargs):
        # TODO try to figure out how to support unnamed ctx?
        # TODO use stacktrace info from inspect??
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                # used as ctx manager
                return ccc(name=arg, **kwargs)
            elif callable(arg):
                # used as decorator
                return f(arg)
        else:
            return lambda realf: f(realf, *args, **kwargs)
    return dec


@ctxmanager_magic
def timed(func, logger=None):
    if logger is None:
        logger = logging
    lfunc = logger.debug

    @wraps(func)
    def wrapper(*args, **kwargs):
        fname = func.__name__
        start = time.time()
        lfunc('%s: running', fname)
        result = func(*args, **kwargs)
        end = time.time()
        lfunc("%s ran in %s sec", fname, round(end - start, 2))
        return result
    return wrapper


def test_timed():
    def get_logger():
        return logging.getLogger('timing-test')

    @timed
    def test_noargs():
        time.sleep(0.1)


    # pylint: disable=no-value-for-parameter
    @timed(logger=get_logger())
    def test_args():
        time.sleep(0.2)

    test_args()
    test_noargs()

    # pylint: disable=not-context-manager
    with timed('testing ', logger=get_logger()):
        time.sleep(0.3)


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
        # TODO wtf is this? not always none..
        # assert obj is None
        return self.f(cls)

class _B:
    @classproperty
    # pylint: disable=no-self-argument
    def something(cls) -> str:
        return 'HELLO'

def test_classproperty() -> None:
    assert _B.something == 'HELLO'

