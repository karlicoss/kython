from typing import Union, TypeVar, Iterator, Callable, Iterable, List, Tuple, Type


T = TypeVar('T')
E = TypeVar('E', bound=Exception)

ResT = Union[T, E]

Res = ResT[T, Exception]


# TODO make it a bit more typed??
def is_error(res: Res[T]) -> bool:
    return isinstance(res, Exception)


def is_ok(res: Res[T]) -> bool:
    return not is_error(res)


def unwrap(res: Res[T]) -> T:
    if isinstance(res, Exception):
        raise res
    else:
        return res

U = TypeVar('U')
def fmap(f: Callable[[T], U]) -> Callable[[Res[T]], Res[U]]:
    # TODO come up with a better name...
    def cc(r: Res[T]) -> Res[U]:
        try:
            v = unwrap(r)
        except Exception as e: # TODO also check exception against error type? not sure if possible...
            return e
        else:
            return f(v)
    return cc

# TODO ugh. perhaps function should be error aware somehow? via decorator or something?

def split_errors(l: Iterable[ResT[T, E]], ET=Exception) -> Tuple[List[T], List[E]]:
    rl: List[T] = []
    el: List[E] = []
    for x in l:
        if isinstance(x, ET):
            el.append(x)
        else:
            rl.append(x) # type: ignore
    return rl, el


def ytry(cb) -> Iterator[Exception]:
    try:
        cb()
    except Exception as e:
        yield e


# TODO experimental, not sure if I like it
def echain(ex: E, cause: Exception) -> E:
    ex.__cause__ = cause
    # TODO assert cause is none?
    # TODO copy??
    return ex
    # try:
    #     # TODO is there a awy to get around raise from?
    #     raise ex from cause
    # except Exception as e:
    #     if isinstance(e, type(ex)):
    #         return e
    #     else:
    #         raise e


class Infinity:
    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return True
INF = Infinity()


def sort_res_by(items: Iterable[ResT], key) -> List[ResT]:
    """
    The general idea is: just alaways carry errrors with the entry that precedes it
    """
    # TODO fuck. we don't really need that, but because of the way group_by_comparator
    # implemented now, we do...
    items = list(items)

    # TODO kython dependency.. not good
    from kython.misc import group_by_comparator, flatten
    def cmp(left, right) -> bool:
        return is_error(left) # if it's an error we want to attach it to the nex OK
    groups = list(group_by_comparator(items, cmp))

    def group_key(g):
        last = g[-1]
        try:
            x: ResT = unwrap(last)
        except:
            return INF
        else:
            return key(x)
    return flatten(sorted(groups, key=group_key))


def test_sort_res_by():
    class Exc(Exception):
        def __eq__(self, other):
            return self.args == other.args

    ress = [
        Exc('first'),
        Exc('second'),
        5,
        3,
        Exc('xxx'),
        2,
        1,
        Exc('last'),
    ]
    results = sort_res_by(ress, lambda x: x) # type: ignore
    assert results == [
        1,
        Exc('xxx'),
        2,
        3,
        Exc('first'),
        Exc('second'),
        5,
        Exc('last'),
    ]

