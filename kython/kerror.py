from typing import Union, TypeVar, Iterator, Callable


T = TypeVar('T')

Res = Union[T, Exception]


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
        except Exception as e:
            return e
        else:
            return f(v)
    return cc


def ytry(cb) -> Iterator[Exception]:
    try:
        cb()
    except Exception as e:
        yield e

