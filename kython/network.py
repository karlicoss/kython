import time

from kython import numbers


# we should only log as error if ran out of attempts
def backoff_network_errors(method, logger, *args, **kwargs):
    if logger is None:
        class DummyLogger:
            def error(self, *args, **kwargs):
                pass

            def debug(self, *args, **kwargs):
                pass

            def info(self, *args, **kwargs):
                pass
        logger = DummyLogger()

    # TODO how to log?
    def get_backoff_s(attempt: int) -> int:
        first = [1, 5, 10, 60, 100]
        if attempt < len(first):
            return first[attempt]
        return first[-1]

    # TODO do kinda bt wifi style?
    # TODO also got something in zoopla
    max_attempt = 5
    for attempt in numbers(0):
        # method has to be idempotent!
        try:
            return method(*args, **kwargs)
        except Exception as e: # TODO FIXME only catch network errors!
            logger.error(e)
            if attempt >= max_attempt:
                # TODO log
                logger.error("Max attempts exceeeded, bailing!")
                raise e

            # TODO log
            backoff = get_backoff_s(attempt)
            # TODO a bit annoying that it will be filtered as error by thunderbird..
            logger.error(f"Error while executing {method.__name__}({args}, {kwargs}) (attempt {attempt}/{max_attempt}), sleeping for {backoff}s")
            time.sleep(backoff)

    raise RuntimeError("Can't happen")
