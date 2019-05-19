#!/usr/bin/env python3
from urllib.parse import urlparse, parse_qsl

# this has some benchmark, but quite a few librarires seem unmaintained, sadly
# I guess i'll stick to default for now, until it's a critical bottleneck
# https://github.com/commonsearch/urlparse4
# rom urllib.parse import urlparse


def canonify_domain(dom: str):
    return {
        'www.scottaaronson.com': 'scottaaronson.com',
    }.get(dom, dom)

def canonify(url: str) -> str:
    parts = urlparse(url)
    domain = canonify_domain(parts.netloc)
    

    return f'{domain}{parts.path}'



# TODO should actually understand 'sequences'?
# e.g.
# https://www.scottaaronson.com/blog/?p=3167#comment-1731882 is kinda hierarchy of scottaaronson.com, post 3167 and comment 1731882
# but when working with it from server, would be easier to just do multiple queries I guess..
# https://www.scottaaronson.com/blog/?p=3167 is kind ahierarchy of scottaaronson.com ; 


def test():
    C = canonify
    assert C("https://www.scottaaronson.com/blog/?p=3167#comment-1731882") == "scottaaronson.com/blog/?p=3167#comment-1731882"
    # TODO github queries
    # TODO hackernews?
    # TODO scott aaronson
    # TODO 


def main():
    pass

if __name__ == '__main__':
    main()
