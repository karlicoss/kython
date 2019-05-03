def keq(j, *keys) -> bool:
    return list(sorted(j.keys())) == list(sorted(keys))

def akeq(j, *keys):
    if keq(j, *keys):
        return
    raise RuntimeError(f'expected dict to have keys {keys}, got {j.keys()}')


def dell(dd, *keys):
    for k in keys:
        del dd[k]


def zoom(dd, *keys):
    akeq(dd, *keys)
    vals = [dd[k] for k in keys]
    if len(keys) == 1:
        return vals[0] # eh, not sure...
    else:
        return vals


def dict_wrap(d):
    pass


    if isinstance(j, dict):
        pass
    pass

class Wrapper:
    pass

    # def consumed():
    #     # TODO start with dicts??
    #     # TODO unwrap method or value property?
    #     # TODO if we use value, it's consumed?
    #     pass
from typing import Any

class Zoomable:
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    # TODO not sure, maybe do it via del??
    # TODO need to make sure they are in proper order? object should be last..
    @property
    def dependants(self):
        raise NotImplementedError

    def consume_all(self):
        for d in self.dependants:
            d.consume_all()
            d.consume()

    def consume(self):
        assert self.parent is not None
        self.parent._remove(self)

    def zoom(self):
        self.consume()
        return self

    def _remove(self, xx):
        raise NotImplementedError

    def iter_nonempty(self):
        raise NotImplementedError

    def this_consumed(self):
        raise NotImplementedError

    @property
    def nonempty(self):
        return list(self.iter_nonempty())

from collections import OrderedDict
class Wdict(Zoomable, OrderedDict):
    def iter_nonempty(self):
        for k, v in self.items():
            yield from v.iter_nonempty()
        if len(self) > 0:
            yield self

    def _remove(self, xx):
        keys = [k for k, v in self.items() if v is xx]
        assert len(keys) == 1
        del self[keys[0]]

    @property
    def dependants(self):
        return list(self.values())

    def this_consumed(self):
        return len(self) == 0

    def consumed(self):
        return len(self.nonempty) == 0

class Wvalue(Zoomable):
    def __init__(self, parent, value: Any) -> None:
        super().__init__(parent)
        self.value = value

    @property
    def dependants(self):
        return []

    def this_consumed(self):
        return True # TODO not sure..

    def iter_nonempty(self):
        yield self
        # TODO shit inheritance doesn't work..
# class Wint(Zoomable, int):
#     def __new__(cls, *args, **kwargs):
#         print(cls)
#         print(args)
#         print(kwargs)
#         return super().__new__(cls, 5)
    # def __init__(self, *args, **kwargs):
    #     super().__init__()
    #     print("HI")

def _wrap(j, parent=None):
    # TODO the very top level is kinda special, it needs to assert that all the children are consumed...
    if isinstance(j, dict):
        # TODO need to make wdict first, then populate it with values? wonder if should inherit from ordered dict??
        res = Wdict(parent)
        cc = [res]
        for k, v in j.items():
            vv, c  = _wrap(v, parent=res)
            res[k] = vv
            cc.extend(c)
        # res.dependants = cc + [res]
        return res, cc
    if isinstance(j, (int, float, str, type(None))):
        res = Wvalue(parent, j)
        # res.dependants = [res] # TODO not sure if including self is too confusing
        return res, [res]
    raise RuntimeError(str(j))

from contextlib import contextmanager

class UnconsumedError(Exception):
    pass

@contextmanager
def wrap(j):
    w, children = _wrap(j)

    yield w

    # from pprint import pprint
    # pprint(children)
    for c in children:
        if not c.this_consumed(): # TODO hmm. how does it figure out if it's consumed???
            raise UnconsumedError(str(c))

def test_unconsumed():
    import pytest # type: ignore
    with pytest.raises(UnconsumedError):
        with wrap({'a': 1234}) as w:
            pass

    with pytest.raises(UnconsumedError):
        with wrap({'c': {'d': 2222}}) as w:
            d = w['c']['d'].zoom()

def test_consumed():
    with wrap({'a': 1234}) as w:
        a = w['a'].zoom()

    with wrap({'c': {'d': 2222}}) as w:
        c = w['c'].zoom()
        d = c['d'].zoom()

def test_types():
    # (string, number, object, array, boolean or nul
    with wrap({'string': 'string', 'number': 3.14, 'boolean': True, 'null': None}) as w:
        w['string'].zoom()
        w['number'].consume()
        w['boolean'].zoom()
        w['null'].zoom()

def test_consume_all():
    with wrap({'aaa': {'bbb': {'hi': 123}}}) as w:
        aaa = w['aaa'].zoom()
        aaa.consume_all()
# def test():
#     with wrap({'a': {'xx': 123}, 'b': 222}) as w:
#         # w, a, b, xx
#         # TODO not sure about nonempty...
#         # assert len(w.nonempty) == 4
#         a = w['a'].zoom()
#         b = w['b'].zoom()
#         # TODO b obj is not consumed yet
#         # TODO nonempty method?
#         print(w.nonempty)
#         pass
#     # TODO
