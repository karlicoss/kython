import functools
import logging
from typing import Union, Optional


from .klogging2 import mklevel


# TODO name a bit misleading?
# TODO allow passing setup function to it?
class LazyLogger(logging.Logger):
    """
    Doing logger = logging.getLogger() on top level is not safe because it happens before logging configuring (if you do it in main).
    Normally you get around it with defining get_logger() -> Logger, but that's annoying to do every time you want to use logger.
    This allows you to do logger = LazyLogger('my-script'), which would only be initialised on first use.
    """
    def __init__(self, name: str, level=None, cronlevel=None, logzero=True):
        self.name = name
        self.logzero = logzero
        self.level = mklevel(level)
        self.cronlevel = mklevel(cronlevel)

    @functools.lru_cache(1)
    def _instance(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        if self.logzero:
            setup_logzero(logger, level=self.level, cronlevel=self.cronlevel)
        else:
            raise NotImplementedError # TODO not sure what do we do here..
        return logger

    def __getattr__(self, attr):
        inst = self._instance()
        return getattr(inst, attr)


def setup_logzero(logger, logfile: str = None, level = None, cronlevel = None):
    if cronlevel is None:
        cronlevel = level

    import sys

    stream_fmt = None
    file_fmt = None
    try:
        from logzero import LogFormatter # type: ignore
        FMT='%(color)s[%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
        stream_fmt = LogFormatter(fmt=FMT, color=True)
        file_fmt = LogFormatter(fmt=FMT, color=False)
    except ImportError as e:
        logging.warn("logzero is not available! Fallback to default")

    # ugh.. https://stackoverflow.com/a/21127526/706389
    logger.propagate = False

    lev = level if sys.stdout.isatty() else cronlevel
    if lev is not None:
        logger.setLevel(lev)

    # TODO  datefmt='%Y-%m-%d %H:%M:%S'
    shandler = logging.StreamHandler()
    if stream_fmt is not None:
        shandler.setFormatter(stream_fmt)
    logger.addHandler(shandler)

    if logfile is not None:
        fhandler = logging.FileHandler(logfile) # TODO rewrite? not sure ...
        if file_fmt is not None:
            fhandler.setFormatter(file_fmt)
        logger.addHandler(fhandler)


# TODO remove it?
def _setup_coloredlogs(logger, level=None):
    # TODO should be same as logzero
    COLOREDLOGGER_FORMAT = "%(asctime)s [%(name)s] %(levelname)s %(message)s"
    import os
    import logging

    if level is None:
        level = logging.INFO

    try:
        import coloredlogs # type: ignore

        maybe_tty = {}
        if 'COLOREDLOGS_FORCE_COLOR' in os.environ:
            maybe_tty['isatty'] = True
        coloredlogs.install(logger=logger, fmt=COLOREDLOGGER_FORMAT, level=level, **maybe_tty)
    except ImportError as e:
        if e.name != 'coloredlogs':
            raise e
        logging.exception(e)
        logging.warning("Install coloredlogs for fancy colored logs!")

    # TODO should be common?...
    logging.getLogger('requests').setLevel(logging.CRITICAL)
