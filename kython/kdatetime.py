from datetime import datetime

import pytz


def as_utc(thing) -> datetime:
    if isinstance(thing, (float, int)):
        return as_utc(datetime.utcfromtimestamp(thing))
    elif isinstance(thing, datetime):
        assert thing.tzinfo is None
        return pytz.utc.localize(thing)
    else:
        raise RuntimeError(f'could not convert {thing} to datetime')
