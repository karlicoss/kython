import logging
from typing import Union, Optional

Level = int
LevelIsh = Optional[Union[Level, str]]


def mklevel(level: LevelIsh) -> Level:
    if level is None:
        return logging.NOTSET
    if isinstance(level, int):
        return level
    return getattr(logging, level.upper())



_FMT = '%(color)s[%(levelname)-7s %(asctime)s %(name)s %(filename)s:%(lineno)d]%(end_color)s %(message)s'

class LazyLogger(logging.Logger):
    # TODO perhaps should use __new__?

    def __new__(cls, name, level: LevelIsh = 'DEBUG'):
        logger = logging.getLogger(name)
        level = mklevel(level)

        # this is called prior to all _log calls so makes sense to do it here?
        def isEnabledFor_lazyinit(*args, logger=logger, orig=logger.isEnabledFor, **kwargs):
            att = 'lazylogger_init_done'
            if not getattr(logger, att, False): # init once, if necessary
                import logzero # type: ignore
                formatter = logzero.LogFormatter(
                    fmt=_FMT,
                    datefmt=None, # pass None to prevent logzero from messing with date format
                )
                logzero.setup_logger(logger.name, level=level, formatter=formatter)
                setattr(logger, att, True)
            return orig(*args, **kwargs)

        logger.isEnabledFor = isEnabledFor_lazyinit  # type: ignore[assignment]
        return logger


def test():
    ll = LazyLogger('test')
    ll.debug('THIS IS DEBUG')
    ll.warning('THIS IS WARNING')
    ll.exception(RuntimeError("oops"))


if __name__ == '__main__':
    test()
