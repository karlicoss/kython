# TODO move to kython?
def setup_logzero(logger, logfile: str = None, level = None):
    import logging
    import logzero # type: ignore
    FMT='%(color)s[%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'

    # ugh.. https://stackoverflow.com/a/21127526/706389
    logger.propagate = False

    if level is not None:
        logger.setLevel(level)

# TODO  datefmt='%Y-%m-%d %H:%M:%S'
    shandler = logging.StreamHandler()
    shandler.setFormatter(logzero.LogFormatter(fmt=FMT, color=True))
    logger.addHandler(shandler)

    if logfile is not None:
        fhandler = logging.FileHandler(logfile) # TODO rewrite? not sure ...
        fhandler.setFormatter(logzero.LogFormatter(fmt=FMT, color=False))
        logger.addHandler(fhandler)
