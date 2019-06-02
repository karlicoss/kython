#!/usr/bin/env python3
import urllib.parse
from urllib.parse import urlsplit, parse_qsl, urlunsplit, parse_qs, urlencode

# this has some benchmark, but quite a few librarires seem unmaintained, sadly
# I guess i'll stick to default for now, until it's a critical bottleneck
# https://github.com/commonsearch/urlparse4
# rom urllib.parse import urlparse

def try_cutl(prefix, s):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s

def try_cutr(suffix, s):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s


def canonify_domain(dom: str):
    dom = try_cutl('www.', dom)
    return dom
    # return {
    #     # TODO list of domains to strip www? or rather, not strip www?
    #     'www.scottaaronson.com': 'scottaaronson.com',
    #     'www.youtube.com': 'youtube.com',
    # }.get(dom, dom)

from typing import NamedTuple, Set, Optional


default_qremove = {
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',

    # https://moz.com/blog/decoding-googles-referral-string-or-how-i-survived-secure-search
    # some google referral
    'usg',
}

class Spec(NamedTuple):
    qkeep  : Optional[Set[str]] = None
    qremove: Optional[Set[str]] = None

    def keep_query(self, q: str):
        keep = False
        remove = False
        # pylint: disable=unsupported-membership-test
        if self.qkeep is not None and q in self.qkeep:
            keep = True
        # pylint: disable=unsupported-membership-test
        if self.qremove is not None and q in self.qremove:
            remove = True
        if keep and remove:
            return True # TODO need a warning
        if keep:
            return True
        if remove:
            return False
        return True
        # TODO basically, at this point only qremove matters

    @classmethod
    def make(cls, qremove=None, **kwargs):
        qr = default_qremove.union(qremove or {})
        return cls(qremove=qr, **kwargs)

S = Spec.make

specs = {
    'youtube.com': S(
        qkeep={'v'}, # TODO FIXME frozenset
        qremove={'list', 'index', 't'} # TODO not so sure about t
    ),
    'github.com': S(
        qkeep={'q'},
        qremove={'o', 's', 'type'},
    ),
    'facebook.com': S(
        qkeep={'fbid'},
        qremove={'set', 'type'},
    )
}

_def_spec = S()
def get_spec(dom: str) -> Spec:
    return specs.get(dom, _def_spec)


def canonify(url: str) -> str:
    parts = urlsplit(url)
    domain = canonify_domain(parts.netloc)

    query = parts.query
    frag = parts.fragment
    spec = get_spec(domain)

    # print(parts)
    # print(spec)

    qq = parse_qsl(query)
    qq = [(k, v) for k, v in qq if spec.keep_query(k)]
    query = urlencode(qq, quote_via=urllib.parse.quote) # by default it replaces %20 with +; not sure if we want that...

    uns = urlunsplit((
        '',
        domain,
        parts.path,
        query,
        frag,
    ))

    uns = try_cutl('//', uns)  # // due to dummy protocol
    uns = try_cutr('/', uns) # not sure if there is a better way
    return uns



# TODO should actually understand 'sequences'?
# e.g.
# https://www.scottaaronson.com/blog/?p=3167#comment-1731882 is kinda hierarchy of scottaaronson.com, post 3167 and comment 1731882
# but when working with it from server, would be easier to just do multiple queries I guess..
# https://www.scottaaronson.com/blog/?p=3167 is kind ahierarchy of scottaaronson.com ; 


import pytest # type: ignore

@pytest.mark.parametrize("url,expected", [
    ( "https://www.scottaaronson.com/blog/?p=3167#comment-1731882"
    , "scottaaronson.com/blog/?p=3167#comment-1731882"
    ),
    ( "https://www.youtube.com/watch?v=1NHbPN9pNPM&index=63&list=WL&t=491s"
    , "youtube.com/watch?v=1NHbPN9pNPM" # TODO not so sure about &t, it's sort of useful
    ),
    ( "https://en.wikipedia.org/wiki/tendon#cite_note-14"
    , "en.wikipedia.org/wiki/tendon#cite_note-14"
    ),
    # ( "youtube.com/embed/nyc6RJEEe0U?feature=oembed"
    # , "youtube.com/watch?v=nyc6RJEEe0U", # TODO not sure how realistic...
    # )
    ( "https://physicstravelguide.com/experiments/aharonov-bohm#tab__concrete"
    , "physicstravelguide.com/experiments/aharonov-bohm#tab__concrete"
    ),
    ( "https://github.com/search?o=asc&q=track&s=stars&type=Repositories"
    , "github.com/search?q=track"
    ),
    ( "https://80000hours.org/career-decision/article/?utm_source=The+EA+Newsletter&utm_campaign=04ca3c2244-EMAIL_CAMPAIGN_2019_04_03_04_26&utm_medium=email&utm_term=0_51c1df13ac-04ca3c2244-318697649"
    , "80000hours.org/career-decision/article"
    ),
    ( "https://www.facebook.com/photo.php?fbid=24147689823424326&set=pcb.2414778905423667&type=3&theater"
    , "facebook.com/photo.php?fbid=24147689823424326"
    ),
    ( "https://play.google.com/store/apps/details?id=com.faultexception.reader&whatever"
    , "play.google.com/store/apps/details?id=com.faultexception.reader"
    ),
    ( "https://news.ycombinator.com/item?id=12172351"
    , "news.ycombinator.com/item?id=12172351"
    ),
    ( "https://urbandictionary.com/define.php?term=Belgian%20Whistle"
    , "urbandictionary.com/define.php?term=Belgian%20Whistle"
    ),
    ( "https://en.wikipedia.org/wiki/Dinic%27s_algorithm"
    , "en.wikipedia.org/wiki/Dinic%27s_algorithm"
    )

    # TODO shit. is that normal???
    # SplitResult(scheme='https', netloc='unix.stackexchange.com', path='/questions/171603/convert-file-contents-to-lower-case/171708', query='', fragment='171708&usg=AFQjCNEFCGqCAa4P4Zlu2x11bThJispNxQ')
    # ( "https://unix.stackexchange.com/questions/171603/convert-file-contents-to-lower-case/171708#171708&usg=AFQjCNEFCGqCAa4P4Zlu2x11bThJispNxQ"
    # , "unix.stackexchange.com/questions/171603/convert-file-contents-to-lower-case/171708#171708"
    # )
])
def test(url, expected):
    assert canonify(url) == expected
    # TODO github queries
    # TODO  again, for that actually sequence would be good...

    # TODO "https://twitter.com/search?q=pinboard search&src=typd"

    # TODO https://www.zalando-lounge.ch/#/

# /L/data/wereyouhere/intermediate  ✔  rg 'orig_url.*#' 20190519090753.json | grep -v zoopla | grep -v 'twitter' | grep -v youtube

def main():
    pass

if __name__ == '__main__':
    main()
