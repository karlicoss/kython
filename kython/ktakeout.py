from enum import Enum
import re
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser
from typing import List, Dict
from collections import OrderedDict
from urllib.parse import unquote
import pytz

# TODO wonder if that old format used to be UTC...
# Mar 8, 2018, 5:14:40 PM
_TIME_FORMAT = "%b %d, %Y, %I:%M:%S %p"
# TODO %Z?

# ugh. something is seriously wrong with datetime, it wouldn't parse timezone aware UTC timestamp :(
def parse_dt(s: str) -> datetime:
    # dt = parser.parse(s)
    dt = datetime.strptime(s, _TIME_FORMAT)
    if dt.tzinfo is None:
        # TODO log?
        # hopefully it was utc? Legacy, so no that much of an issue anymore..
        # TODO DO NOT USE IT!!
        dt = dt.replace(tzinfo=pytz.utc)
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
        self.current: Dict[str, str] = {}
        self.callback = callback

    def _reg(self, name, value):
        assert name not in self.current
        self.current[name] = value

    def _astate(self, s): assert self.state == s

    def _trans(self, f, t):
        self._astate(f)
        self.state = t

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
            # TODO should just set in PARSING_LINK?
            self._reg('url', hr)

    def handle_endtag(self, tag):
        if tag == 'html':
            pass # ??

    # youtube example:
    # Watched Jamie xx - Gosh
    # JamiexxVEVO
    # Jun 21, 2018, 5:48:34 AM
    # Products:
    #  YouTube

    def handle_data(self, data):
        if self.state == State.OUTSIDE:
            # TODO FIXME
            prefix = "Watched" # "Visited"
            if data[:-1].strip() == prefix:
                self.state = State.INSIDE
                return

        if self.state == State.PARSING_LINK:
            # self._reg(Entry.link, data)
            self.state = State.PARSING_DATE
            return

        # TODO extracting channel as part of wereyouhere could be useful as well
        # need to check for regex because there might be some stuff in between
        if self.state == State.PARSING_DATE and re.search(r'\d{4}.*:.*:', data):
            self._reg('time', data.strip()) # TODO why am I doingthat?

            url = self.current['url']
            times = self.current['time']
            time = parse_dt(times)
            assert time.tzinfo is not None

            self.callback(time, url)

            self.current = {}
            self.state = State.OUTSIDE
            return

def _helper(path):
    from kython import kompress
    collected = []
    def callback(dt, url):
        collected.append((dt, url))

    p = TakeoutHTMLParser(callback)
    with kompress.open('/L/backups/takeout/karlicoss_gmail_com/takeout-20180623T190546Z-001.zip', path) as fo:
        data = fo.read().decode('utf8')
        print("parsing...")
        p.feed(data) # TODO would be nice to do it in iterative fashion... not sure if python lib supports that

    return collected


def test_myactivity():
    collected = _helper('Takeout/My Activity/Chrome/MyActivity.html')
    assert len(collected) > 100
    # TODO test timestamp

def test_youtube():
    collected = _helper('Takeout/My Activity/YouTube/MyActivity.html')
    assert len(collected) > 100
    assert (datetime(year=2018, month=6, day=21, hour=5, minute=48, second=34, tzinfo=pytz.utc), 'https://www.youtube.com/watch?v=hTGJfRPLe08') in collected


