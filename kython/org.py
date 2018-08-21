from datetime import datetime
from typing import List, Dict, Optional, Any
from functools import lru_cache

import pytz

import PyOrgMode # type: ignore

# TODO do something more meaningful..
def _read_org_table(table) -> List[Dict[str, str]]:
    # TODO with_header?
    cols = [s.strip() for s in table.content[0]]
    idx = dict(enumerate(cols))
    res = []
    for row in table.content[2:]:
        d = {}
        for i, val in enumerate(row): d[idx[i]] = val.strip()
        res.append(d)
    return res

def extract_org_table(fname: str, pos: int) -> List[Dict[str, str]]:
    base = PyOrgMode.OrgDataStructure()
    # TODO assert increasing??
    base.load_from_file(fname)
    root: PyOrgMode.OrgNode.Element = base.root # type: ignore
    tbl = root.content[pos]
    assert isinstance(tbl, PyOrgMode.OrgTable.Element)
    return _read_org_table(tbl)


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

def parse_org_date(s: str):
    for fmt in ["%Y-%m-%d %a %H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    else:
        raise RuntimeError(f"Bad date string {s}")

def date2org(t: datetime) -> str:
    return t.strftime("%Y-%m-%d %a")

def datetime2orgtime(t: datetime) -> str:
    return t.strftime("%H:%M")

def datetime2org(t: datetime) -> str:
    return date2org(t) + " " + datetime2orgtime(t)

class OrgNote:
    def __init__(self, node):
        self.node = node

        # TODO collect OrgNodes recursively?
        # pyorgmode lib is weird.. easier to collect recursively
        # def helper(cur):
        #     if isinstance(cur, PyOrgMode.OrgDrawer.Property):
        #         return [cur]
        #     res = []
        #     if hasattr(cur, 'content'):
        #         for x in cur.content:
        #             res.extend(helper(x))
        #     return res

        # self.props = {h.name: h.value for h in helper(root)}

    @lru_cache()
    def _get_props(self) -> Dict[str, str]:
        dr = [c for c in self.node.content if isinstance(c, PyOrgMode.OrgDrawer.Element)]
        if len(dr) == 0:
            return {}
        [drawer] = dr
        return {p.name: p.value for p in drawer.content}

    @property
    def content(self) -> str:
        c = []
        for ch in self.node.content:
            if isinstance(ch, str):
                c.append(ch)
        return ' '.join(c)

    @property
    def comment(self) -> str:
        return self.content

    @property
    def simple(self) -> str:
        return self.node.heading + self.content

    @property
    def tags(self):
        return self.node.get_all_tags()

    @property
    def name(self):
        return self.node.heading.strip()

    @property
    def heading(self) -> str:
        # TODO eh, strip off date string later?
        return self.node.heading

    @property
    def date(self) -> Optional[datetime]:
        created = self._get_props().get('CREATED', None)
        if created is None:
            created = extract_org_datestr(self.node.heading)
        if created is None:
            return None
        created = created[1:-1] # cut off square brackets
        # TODO maybe don't localize, use location provider..
        TZ_LONDON = pytz.timezone('Europe/London')
        return TZ_LONDON.localize(parse_org_date(created))

    def __str__(self):
        return f"{self.date} {self.name}"


def load_org_file(fname: str) -> List[OrgNote]:
    import PyOrgMode
    ofile = PyOrgMode.OrgDataStructure()
    ofile.load_from_file(fname)
    onotes = [OrgNote(x) for x in ofile.root.content] #  if isinstance(x, PyOrgMode.OrgNode.Element)]
    # import ipdb; ipdb.set_trace()
    return onotes
