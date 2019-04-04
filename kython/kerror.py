from typing import Union, TypeVar, Iterator


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


def ytry(cb) -> Iterator[Exception]:
    try:
        cb()
    except Exception as e:
        yield e

