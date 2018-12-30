from datetime import datetime, date
import re
from typing import Union, Optional

import pytz

DatetimeIsh = Union[datetime, str, int]

# dateparser:
# capable of handling:
## endomondo-YYYY-MM-DD.json
# couldn't:
## Your Highlight on page 153 | Location 2342-2343 | Added on Thursday, October 19, 2017 1126 AM


# datefinder:
## In [9]: list(find_dates("Your Highlight on page 153 | Location 2342-2343 | Added on Thursday, October 19, 2017 1126 AM"))
## Out[9]: [datetime.datetime(153, 10, 27, 0, 0), datetime.datetime(2017, 10, 19, 11, 26)]
## right, maybe just select the most likely one?...

## hasn't been updated for few year, people on guhub claim depenencies might be old..

# TODO add some basic tests???

_DT_REGEX = re.compile(r'\D(?P<date>\d{8})\D*(?P<time>\d{6})?\D*$')

def _extract_mdatetime(s: DatetimeIsh) -> Optional[datetime]:
    if isinstance(s, datetime):
        return s
    if isinstance(s, int):
        return datetime.fromtimestamp(s) # TODO utc??
    ss = s.replace('_', '')
    ss = s.replace('-', '')

    # 1. handle simple case
    mm = _DT_REGEX.search(ss)
    if mm is not None:
        # TODO specify if it's utc somehow??
        dd = mm.group('date')
        ss = dd
        pat = "%Y%m%d"

        tt = mm.group('time')
        if tt is not None:
            ss += tt
            pat += "%H%M%S"
        return datetime.strptime(ss, pat)

    # 2. TODO fallback to more complicated parsers
    # it's pretty slow..
    import dateparser # type: ignore
    return dateparser.parse(s)
    # fuck. looks like easiest is really to recognise groups of digits

def _fix_tz(dt: datetime) -> datetime:
    tz = dt.tzinfo
    if tz is None:
        return dt
    tztype = type(tz)
    tzmod = tztype.__module__
    if tzmod.startswith('pytz'):
        return tz
    # e.g. datefinder returns its own StaticTzInfo somehow..
    if tztype.__name__ == 'StaticTzInfo':
        offset = getattr(tz, '_StaticTzInfo__offset')
        offset_mins = offset.seconds // 60
        # TODO ugh, does it have to be so hard??
        return dt.replace(tzinfo=pytz.FixedOffset(offset_mins)) # type: ignore
    else:
        raise RuntimeError(f'Bad tz for {dt}: {tzmod} {tz}')

def parse_mdatetime(s: DatetimeIsh) -> Optional[datetime]:
    res = _extract_mdatetime(s)
    if res is None:
        return res
    return _fix_tz(res)

def parse_datetime(s: DatetimeIsh) -> datetime:
    res = parse_mdatetime(s)
    if res is None:
        raise RuntimeError(f"Couldn't parse {s}")
    return res

# dateparser.parse -- capable of none of these v
def test():
    tests = [
        ('endomondo-2017-12-05.json'        , datetime(year=2017, month=12, day=5)),
        ('github-20181005'                  , datetime(year=2018, month=10, day=5)),
        ('whatever-20181112090801'          , datetime(year=2018, month=11, day=12, hour=9, minute=8, second=1)),
        ('Instagram/IMG_20140411_034425.jpg', datetime(year=2014, month=4, day=11, hour=3, minute=44, second=25)),
        ('2018-12-28T13:58:43Z'             , datetime(year=2018, month=12, day=28, hour=13, minute=58, second=43, tzinfo=pytz.UTC)), # TODO tz??  # dataparser: ok; datefinder -- couldn't
        # TODO dateparser: fails on that '20181228T13:58:43Z' ; datefinder -- couldn't 
        # TODO Wednesday, November 22, 2017 9:11:56 PM
    ]

    error = False
    for inp, res in tests:
        dt = parse_mdatetime(inp)
        if dt != res:
            print(f"'{inp}': FAILED: expected to be parsed as {res}, got {dt} instead")
            error = True
        else:
            pass
            # print(f"{inp}: OK:")
    if error:
        raise AssertionError


test()
