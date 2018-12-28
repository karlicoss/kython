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

def date2org(t: datetime) -> str:
    return t.strftime("%Y-%m-%d %a")

def datetime2orgtime(t: datetime) -> str:
    return t.strftime("%H:%M")

def datetime2org(t: datetime) -> str:
    return date2org(t) + " " + datetime2orgtime(t)

# TODO priority maybe??
# TODO need to sanitize!
def as_org_entry(
        heading: Optional[str] = None,
        tags: List[str] = [],
        body: Optional[str] = None,
        created: Optional[datetime]=None,
        todo=True,
):
    if heading is None:
        if body is None:
            raise RuntimeError('Both heading and body are empty!!')
        heading = body.splitlines()[0] # TODO ??

    if body is None:
        body = ''

    # TODO FIXME escape everything properly!
    heading = re.sub(r'\s', ' ', heading)
    # TODO remove newlines from body

    NOW = datetime.now() # TODO tz??
    if created is None:
        created = NOW

    todo_s = 'TODO' if todo else ''
    tag_s = ':'.join(tags)

    sch = [f'  SCHEDULED: <{date2org(NOW)}>'] if todo else []

    if len(tag_s) != 0:
        tag_s = f':{tag_s}:'
    lines = [
        f"""* {todo_s} {heading} {tag_s}""",
        *sch,
        ':PROPERTIES:',
        # TODO not sure if we even need when it was appended...
        f':APPENDED: [{datetime2org(NOW)}]',
        f':CREATED: [{datetime2org(created)}]',
        ':END:',
        body,
        "",
        "",
    ]
    return '\n'.join(lines)

def append_org_entry(
        path: Path,
        *args,
        **kwargs,
):
    res = as_org_entry(*args, **kwargs)
    # https://stackoverflow.com/a/13232181
    if len(res.encode('utf8')) > 4096:
        raise RuntimeError('TODO FIXME LOGGING IS ENOUGH HERE')
        # logging.warning("writing out %s might be non-atomic", res)
    with path.open('a') as fo:
        fo.write(res)
