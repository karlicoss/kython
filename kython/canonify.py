#!/usr/bin/env python3
from urllib.parse import urlsplit, parse_qsl, urlunsplit, parse_qs, urlencode

# this has some benchmark, but quite a few librarires seem unmaintained, sadly
# I guess i'll stick to default for now, until it's a critical bottleneck
# https://github.com/commonsearch/urlparse4
# rom urllib.parse import urlparse

def try_cut(prefix, s):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s


def canonify_domain(dom: str):
    dom = try_cut('www.', dom)
    return dom
    # return {
    #     # TODO list of domains to strip www? or rather, not strip www?
    #     'www.scottaaronson.com': 'scottaaronson.com',
    #     'www.youtube.com': 'youtube.com',
    # }.get(dom, dom)

def useless_query_params(dom: str): # TODO might be useful to pass parts as well..
    # TODO instead, have some sort of domain config?
    # TODO similar: keep useless, remove useful and warn on discrepancy?
    return {
        'youtube.com': {'v'},
    }
    pass

from typing import NamedTuple, Collection, Optional
class Spec(NamedTuple):
    query_keep  : Optional[Collection[str]] = None
    query_remove: Optional[Collection[str]] = None


specs = {
    'youtube.com': Spec(
        query_keep={'v'}, # TODO FIXME frozenset
        query_remove={'list', 'index', 't'} # TODO not so sure about t
    )
}

def canonify(url: str) -> str:
    parts = urlsplit(url)
    domain = canonify_domain(parts.netloc)

    print(parts)

    # TODO need to sort them regardless? so need a dummy spec?
    query = parts.query
    frag = parts.fragment
    spec = specs.get(domain, None)
    if spec is not None:
        qq = parse_qsl(query)
        if spec.query_keep is not None:
            qq = [(k, v) for k, v in qq if k in spec.query_keep]
        query = urlencode(qq)
        pass


    uns = urlunsplit((
        '',
        domain,
        parts.path,
        query,
        frag,
    ))
    return try_cut('//', uns) # // due to dummy protocol



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
    )
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
