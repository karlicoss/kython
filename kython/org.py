from datetime import datetime, date
from typing import List, Dict, Optional, Any, Union
from functools import lru_cache
import re

from pathlib import Path

Dateish = Union[datetime, date]

from kython import parse_timestamp
import pytz

# not sure if belogs here...
def parse_london_date(s):
    d = parse_timestamp(s)
    if d.tzinfo is None:
        # TODO ugh
# london_tz = pytz.timezone('Europe/London')
# from dateutil.tz import tzoffset
# london_tz = datetime.astimezone(tzoffset(None, 3600))
        d = pytz.utc.localize(d)
    return d

def extract_org_datestr(s: str) -> Optional[str]:
    import re
    match = re.search(r'\[\d{4}-\d{2}-\d{2}.*]', s)
    if not match:
        return None
    else:
        return match.group(0)

def parse_org_date(s: str) -> Dateish:
    s = s.strip('[]')
    for fmt, cl in [
            ("%Y-%m-%d %a %H:%M", datetime),
            ("%Y-%m-%d %H:%M", datetime),
            ("%Y-%m-%d %a", date),
            ("%Y-%m-%d", date),
    ]:
        try:
            res = datetime.strptime(s, fmt)
            if cl == date:
                return res.date()
            else:
                return res
        except ValueError:
            continue
    else:
        raise RuntimeError(f"Bad date string {s}")

def extract_date_fuzzy(s: str) -> Optional[Dateish]:
    import datefinder # type: ignore
    # TODO wonder how slow it is..
    dates = list(datefinder.find_dates(s))
    if len(dates) == 0:
        return None
    if len(dates) > 1:
        raise RuntimeError
    return dates[0]

from .org_tools import *
# TODO reuse in telegram2org??
