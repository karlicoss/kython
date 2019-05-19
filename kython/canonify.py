#!/usr/bin/env python3
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

from typing import NamedTuple, Collection, Optional


default_qremove = {
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',
}

class Spec(NamedTuple):
    qkeep  : Optional[Collection[str]] = None
    qremove: Optional[Collection[str]] = None

    def keep_query(self, q: str):
        keep = False
        remove = False
        if self.qkeep is not None and q in self.qkeep:
            keep = True
        if self.qremove is not None and q in self.qremove:
            remove = True
        if keep and remove:
            return True # TODO need a warning
        if keep:
            return True
        if remove:
            return False
        return True

    def make(qremove=None, **kwargs):
        qr = default_qremove.union(qremove or {})
        return Spec(qremove=qr, **kwargs)

S = Spec.make

specs = {
    'youtube.com': S(
        qkeep={'v'}, # TODO FIXME frozenset
        qremove={'list', 'index', 't'} # TODO not so sure about t
    ),
    'github.com': S(
        qkeep={'q'},
        qremove={'o', 's', 'type'},
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

    qq = parse_qsl(query)
    qq = [(k, v) for k, v in qq if spec.keep_query(k)]
    query = urlencode(qq)

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
    , "80000hours.org/career-decision/article",
    ),
])
def test(url, expected):
    assert canonify(url) == expected
    # TODO github queries
    # TODO hackernews?
    # TODO scott aaronson
    # TODO  again, for that actually sequence would be good...


def main():
    pass

if __name__ == '__main__':
    main()