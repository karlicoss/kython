from typing import List, Dict

from PyOrgMode import PyOrgMode # type: ignore

# TODO do something more meaningful..
def _read_org_table(table) -> List[Dict[str, str]]:
    # TODO with_header?
    cols = [s.strip() for s in table.content[0]]
    idx = dict(enumerate(cols))
    res = []
    for row in table.content[2:]:
        d = {}
        for i, val in enumerate(row):
            d[idx[i]] = val.strip()
        res.append(d)
    return res

def extract_org_table(fname: str, pos: int) -> List[Dict[str, str]]:
    base = PyOrgMode.OrgDataStructure()
    # TODO assert increasing??
    base.load_from_file(fname)
    tbl = base.root.content[pos]
    assert isinstance(tbl, PyOrgMode.OrgTable.Element)
    return _read_org_table(tbl)


from . import parse_timestamp
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
