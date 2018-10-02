from datetime import datetime, date
from typing import List, Dict, Optional, Any, Union
from functools import lru_cache


import PyOrgMode # type: ignore

Dateish = Union[datetime, date]

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

class OrgNote:
    def __init__(self, node):
        assert isinstance(node, PyOrgMode.OrgNode.Element)
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
    def _get_datestr(self) -> Optional[str]:
        return extract_org_datestr(self.node.heading)

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
        def helper(n):
            if isinstance(n, str):
                c.append(n)
            elif isinstance(n, list):
                for x in n:
                    helper(x)
            elif hasattr(n, 'heading'):
                c.append(getattr(n, 'heading'))
            if hasattr(n, 'content'):
                helper(getattr(n, 'content'))

        # for ch in self.node.content:
        #     if isinstance(ch, str):
        #         c.append(ch)
        helper(self.node.content)
        return ''.join(c) # newlines are handled by PyOrgMode...

    @property
    def comment(self) -> str:
        return self.content

    @property
    def simple(self) -> str:
        return self.node.heading + self.content

    @property
    def tags(self):
        return set(self.node.get_all_tags())

    @property
    def name(self):
        return self.node.heading.strip()

    @property
    def heading(self) -> str:
        # TODO eh, strip off date string later?
        res = self.node.heading
        ds = self._get_datestr()
        if ds is not None:
            res = res.replace(ds, '') # meh, but works?
        return res

    @property
    def date(self) -> Optional[Dateish]:
        created = self._get_props().get('CREATED', None)
        if created is None:
            created = self._get_datestr()
        if created is not None:
            created = created[1:-1].strip() # cut off square brackets
            return parse_org_date(created)
        # last desperate attempt...
        # TODO maybe we need a fuzzy_date setting or something?..
        dd = extract_date_fuzzy(self.heading)
        return dd

    def __repr__(self):
        return f"OrgNote{{{self.date} {self.name}}}"

from typing import Iterator, Union
def iter_org_file(fname: str) -> Iterator[Union[OrgNote, Exception]]:
    pass

# TODO eh. ok, so looks like I want an actual tree, and then
# if node was a proper and contributing, then just render it
# otherwise, it contributes to parent
# a bit tedious...
def load_org_file(fname: str) -> List[OrgNote]:
    import PyOrgMode
    ofile = PyOrgMode.OrgDataStructure()
    ofile.load_from_file(fname)
    cont = ofile.root.content # type: ignore

    while len(cont) > 0 and isinstance(cont[0], str):
        cont = cont[1:] # skip header and endlines after it
    onotes = [OrgNote(x) for x in cont]
    return onotes
