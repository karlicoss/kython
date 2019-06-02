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

dom_subst = [
    ('m.youtube.', 'youtube.'),
]

def canonify_domain(dom: str):
    # TODO perhaps not necessary now that I'm checking suffixes??
    for st in ('www.', 'amp.'):
        dom = try_cutl(st, dom)

    for start, repl in dom_subst:
        if dom.startswith(start):
            dom = repl + dom[len(start):]
            break

    return dom

from typing import NamedTuple, Set, Optional


default_qremove = {
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',

    # https://moz.com/blog/decoding-googles-referral-string-or-how-i-survived-secure-search
    # some google referral
    'usg',

    # google language??
    'hl',
}


# TODO perhaps, decide if fragment is meaningful (e.g. wiki) or random sequence of letters?
class Spec(NamedTuple):
    qkeep  : Optional[Set[str]] = None
    qremove: Optional[Set[str]] = None
    fkeep  : bool = False

    def keep_query(self, q: str) -> bool:
        # by default drop all, only do something special in case of specs present
        # it's better choice for default since if it's too unified user would notice it, but not vice versa
        if self.qkeep is None and self.qremove is None:
            return False

        qremove = default_qremove.union(self.qremove or {})

        keep = False
        remove = False
        # pylint: disable=unsupported-membership-test
        if self.qkeep is not None and q in self.qkeep:
            keep = True
        # pylint: disable=unsupported-membership-test
        if q in qremove:
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
    def make(cls, **kwargs):
        return cls(**kwargs)

S = Spec.make

# TODO perhaps these can be machine learnt from large set of urls?
specs = {
    'youtube.com': S(
        qkeep={'v'}, # TODO FIXME frozenset
        qremove={'time_continue', 'list', 'index', 'feature', 't'} # TODO not so sure about t
    ),
    # TODO shit. for playlist don't need to remove 'list'...


    'github.com': S(
        qkeep={'q'},
        qremove={'o', 's', 'type'},
    ),
    'facebook.com': S(
        qkeep={'fbid', 'story_fbid'},
        qremove={'set', 'type', 'fref', 'locale2'},
    ),
    'physicstravelguide.com': S(fkeep=True), # TODO instead, pass fkeep marker object for shorter spec?
    'wikipedia.org': S(fkeep=True),
    'scottaaronson.com': S(qkeep={'p'}, qremove={}, fkeep=True),
    'urbandictionary.com': S(qkeep={'term'}, qremove={}),
    'ycombinator.com': S(qkeep={'id'}, qremove={}),
    'play.google.com': S(qkeep={'id'}, qremove={}),
}

_def_spec = S()
# TODO use cache?
def get_spec(dom: str) -> Spec:
    # ugh. a bit ugly way of getting stuff without subdomain...
    parts = dom.split('.')
    cur = None
    for p in reversed(parts):
        if cur is None:
            cur = p
        else:
            cur = p + '.' + cur
        sp = specs.get(cur)
        if sp is not None:
            return sp
    return _def_spec


def canonify(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme == '':
        # if scheme is missing it doesn't parse netloc properly...
        parts = urlsplit('http://' + url)

    domain = canonify_domain(parts.netloc)
    spec = get_spec(domain)

    query = parts.query

    # TODO FIXME turn this logic back on?
    # frag = parts.fragment if spec.fkeep else ''
    frag = ''

    qq = parse_qsl(query)
    qq = [(k, v) for k, v in qq if spec.keep_query(k)]
    # TODO still not sure what we should do..
    # quote_plus replaces %20 with +, not sure if we want it...
    query = urlencode(qq, quote_via=urllib.parse.quote_plus)

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
    # TODO FIXME fragment handling
    # ( "https://www.scottaaronson.com/blog/?p=3167#comment-1731882"
    # , "scottaaronson.com/blog/?p=3167#comment-1731882"
    # ),

    ( "https://www.youtube.com/watch?v=1NHbPN9pNPM&index=63&list=WL&t=491s"
    , "youtube.com/watch?v=1NHbPN9pNPM" # TODO not so sure about &t, it's sort of useful
    ),

    # TODO FIXME fragment handling
    # ( "https://en.wikipedia.org/wiki/tendon#cite_note-14"
    # , "en.wikipedia.org/wiki/tendon#cite_note-14"
    # ),
    # ( "youtube.com/embed/nyc6RJEEe0U?feature=oembed"
    # , "youtube.com/watch?v=nyc6RJEEe0U", # TODO not sure how realistic...
    # )
    ( "youtube.com/watch?v=wHrCkyoe72U&feature=share&time_continue=6"
    , "youtube.com/watch?v=wHrCkyoe72U"
    ),

    # TODO FIXME fragment handling
    # ( "https://physicstravelguide.com/experiments/aharonov-bohm#tab__concrete"
    # , "physicstravelguide.com/experiments/aharonov-bohm#tab__concrete"
    # ),

    ( "https://github.com/search?o=asc&q=track&s=stars&type=Repositories"
    , "github.com/search?q=track"
    ),
    ( "https://80000hours.org/career-decision/article/?utm_source=The+EA+Newsletter&utm_campaign=04ca3c2244-EMAIL_CAMPAIGN_2019_04_03_04_26&utm_medium=email&utm_term=0_51c1df13ac-04ca3c2244-318697649"
    , "80000hours.org/career-decision/article"
    ),
    ( "https://www.facebook.com/photo.php?fbid=24147689823424326&set=pcb.2414778905423667&type=3&theater"
    , "facebook.com/photo.php?fbid=24147689823424326"
    ),
    ( "https://play.google.com/store/apps/details?id=com.faultexception.reader&hl=en"
    , "play.google.com/store/apps/details?id=com.faultexception.reader"
    ),
    # TODO it also got &p= parameter, which refers to page... not sure how to handle this
    # news.ycombinator.com/item?id=15451442&p=2
    ( "https://news.ycombinator.com/item?id=12172351"
    , "news.ycombinator.com/item?id=12172351"
    ),
    ( "https://urbandictionary.com/define.php?term=Belgian%20Whistle"
    , "urbandictionary.com/define.php?term=Belgian+Whistle"
    ),
    ( "https://en.wikipedia.org/wiki/Dinic%27s_algorithm"
    , "en.wikipedia.org/wiki/Dinic%27s_algorithm"
    ),

    ( "zoopla.co.uk/to-rent/details/42756337#D0zlBWeD4X85odsR.97"
    , "zoopla.co.uk/to-rent/details/42756337"
    ),

    ( "withouthspec.co.uk/rooms/16867952?guests=2&adults=2&location=Berlin%2C+Germany&check_in=2017-08-16&check_out=2017-08-20"
    , "withouthspec.co.uk/rooms/16867952"
    ),

    ( "m.youtube.com/watch?v=Zn6gV2sdl38"
    , "youtube.com/watch?v=Zn6gV2sdl38"
    ),

    ( "amp.theguardian.com/technology/2017/oct/09/mark-zuckerberg-facebook-puerto-rico-virtual-reality"
    , "theguardian.com/technology/2017/oct/09/mark-zuckerberg-facebook-puerto-rico-virtual-reality",
    )

    # ( "https//youtube.com/playlist?list=PLeOfc0M-50LmJtZwyOfw6aVopmIbU1t7t"
    # , "youtube.com/playlist?list=PLeOfc0M-50LmJtZwyOfw6aVopmIbU1t7t"
    # ),

    # TODO shit. is that normal??? perhaps need to manually move fragment?
    # SplitResult(scheme='https', netloc='unix.stackexchange.com', path='/questions/171603/convert-file-contents-to-lower-case/171708', query='', fragment='171708&usg=AFQjCNEFCGqCAa4P4Zlu2x11bThJispNxQ')
    # ( "https://unix.stackexchange.com/questions/171603/convert-file-contents-to-lower-case/171708#171708&usg=AFQjCNEFCGqCAa4P4Zlu2x11bThJispNxQ"
    # , "unix.stackexchange.com/questions/171603/convert-file-contents-to-lower-case/171708#171708"
    # )
])
def test(url, expected):
    assert canonify(url) == expected
    # TODO github queries
    # TODO git+https://github.com/expectocode/telegram-export@master
    # TODO  again, for that actually sequence would be good...

    # TODO "https://twitter.com/search?q=pinboard search&src=typd"

    # TODO https://www.zalando-lounge.ch/#/
    # TODO m.facebook.com
    # TODO         [R('^(youtube|urbandictionary|tesco|scottaaronson|answers.yahoo.com|code.google.com)') , None],


# /L/data/wereyouhere/intermediate  ✔  rg 'orig_url.*#' 20190519090753.json | grep -v zoopla | grep -v 'twitter' | grep -v youtube

def main():
    pass

if __name__ == '__main__':
    main()
