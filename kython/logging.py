# TODO move to kython?
def setup_logzero(logger, logfile: str = None, level = None):
    import logging

    stream_fmt = None
    file_fmt = None
    try:
        import logzero # type: ignore
        FMT='%(color)s[%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
        stream_fmt = logzero.LogFormatter(fmt=FMT, color=True)
        file_fmt = logzero.LogFormatter(fmt=FMT, color=False)
    except ImportError:
        logging.warn("logzero is not available! Fallback to default")

    # ugh.. https://stackoverflow.com/a/21127526/706389
    logger.propagate = False

    if level is not None:
        logger.setLevel(level)

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


def setup_coloredlogs(logger, level=None):
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
