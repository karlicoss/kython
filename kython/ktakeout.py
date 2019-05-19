from enum import Enum
import re
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser
from typing import List, Dict, Optional
from collections import OrderedDict
from urllib.parse import unquote
import pytz

# Mar 8, 2018, 5:14:40 PM
_TIME_FORMAT = "%b %d, %Y, %I:%M:%S %p"

# ugh. something is seriously wrong with datetime, it wouldn't parse timezone aware UTC timestamp :(
def parse_dt(s: str) -> datetime:
    fmt = _TIME_FORMAT
    if s.endswith('UTC'): # old takeouts didn't have timezone
        fmt += ' %Z'
    dt = datetime.strptime(s, fmt)
    if dt.tzinfo is None:
        # TODO log?
        # hopefully it was utc? Legacy, so no that much of an issue anymore..
        dt = pytz.utc.localize(dt)
    return dt


class State(Enum):
    OUTSIDE = 0
    INSIDE = 1
    PARSING_LINK = 2
    PARSING_DATE = 3



# would be easier to use beautiful soup, but ends up in a big memory footprint..
class TakeoutHTMLParser(HTMLParser):
    def __init__(self, callback) -> None:
        super().__init__()
        self.state: State = State.OUTSIDE

        self.title_parts: List[str] = []
        self.title: Optional[str] = None
        self.url: Optional[str] = None

        self.callback = callback

    # enter content cell -> scan link -> scan date -> finish till next content cell
    def handle_starttag(self, tag, attrs):
        if self.state == State.INSIDE and tag == 'a':
            self.state = State.PARSING_LINK
            attrs = OrderedDict(attrs)
            hr = attrs['href']

            # sometimes it's starts with this prefix, it's apparently clicks from google search? or visits from chrome address line? who knows...
            # TODO handle http?
            prefix = r'https://www.google.com/url?q='
            if hr.startswith(prefix + "http"):
                hr = hr[len(prefix):]
                hr = unquote(hr) # TODO not sure about that...
            assert self.url is None; self.url = hr

    def handle_endtag(self, tag):
        if self.state == State.PARSING_LINK and tag == 'a':
            assert self.title is None
            assert len(self.title_parts) > 0
            self.title = ''.join(self.title_parts)
            self.title_parts = []

            self.state = State.PARSING_DATE

    # search example:
    # Visited Emmy Noether - Wikipedia
    # Dec 17, 2018, 8:16:18 AM UTC

    # youtube example:
    # Watched Jamie xx - Gosh
    # JamiexxVEVO
    # Jun 21, 2018, 5:48:34 AM
    # Products:
    #  YouTube
    def handle_data(self, data):
        if self.state == State.OUTSIDE:
            if data[:-1].strip() in ("Watched", "Visited"):
                self.state = State.INSIDE
                return

        if self.state == State.PARSING_LINK:
            self.title_parts.append(data)
            return

        # TODO extracting channel as part of wereyouhere could be useful as well
        # need to check for regex because there might be some stuff in between
        if self.state == State.PARSING_DATE and re.search(r'\d{4}.*:.*:', data):
            time = parse_dt(data.strip())
            assert time.tzinfo is not None

            assert self.url is not None; assert self.title is not None
            self.callback(time, self.url, self.title)
            self.url = None; self.title = None

            self.state = State.OUTSIDE
            return

def _helper(archive, path):
    from kython import kompress
    collected = {}
    def callback(dt, url, title):
        collected[(dt, url)] = title

    p = TakeoutHTMLParser(callback)
    with kompress.open(archive, path) as fo:
        data = fo.read().decode('utf8')
        print("parsing...")
        p.feed(data) # TODO would be nice to do it in iterative fashion... not sure if python lib supports that

    return collected

ARCHIVES = [
    '/L/backups/takeout/karlicoss_gmail_com/takeout-20180623T190546Z-001.zip',
    '/L/backups/takeout/karlicoss_gmail_com/takeout-20190507T062236Z-001.zip',
]

def test_myactivity():
    for a in ARCHIVES:
        collected = _helper(a, 'Takeout/My Activity/Chrome/MyActivity.html')
        assert len(collected) > 100
        # TODO test timestamp

def test_youtube():
    for a in ARCHIVES:
        collected = _helper(a, 'Takeout/My Activity/YouTube/MyActivity.html')
        assert len(collected) > 100
        assert (datetime(year=2018, month=6, day=21, hour=5, minute=48, second=34, tzinfo=pytz.utc), 'https://www.youtube.com/watch?v=hTGJfRPLe08') in collected

def test_search():
    collected = _helper(ARCHIVES[1], 'Takeout/My Activity/Search/MyActivity.html')
    assert len(collected) > 100

    # Visited Emmy Noether - Wikipedia
    # Dec 17, 2018, 8:16:18 AM UTC
    found = False
    edt = datetime(year=2018, month=12, day=17, hour=8, minute=16, second=18, tzinfo=pytz.utc)
    eurl = 'https://en.wikipedia.org/wiki/Emmy_Noether'
    etitle = 'Emmy Noether - Wikipedia'
    for (dt, url), title in collected.items():
        if dt == edt and url.startswith(eurl) and title == etitle:
            found = True

    assert found
