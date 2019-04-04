from typing import Union, TypeVar, Iterator


T = TypeVar('T')

Res = Union[T, Exception]


# TODO make it a bit more typed??
def is_error(res: Res[T]) -> bool:
    return isinstance(res, Exception)


def ytry(cb) -> Iterator[Exception]:
    try:
        cb()
    except Exception as e:
        yield e

