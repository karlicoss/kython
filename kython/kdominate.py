from contextlib import contextmanager

import dominate


# TODO shit. contextmanager is bound to thread...
# https://github.com/Knio/dominate/issues/108
# TODO perhaps post on github?
# TODO FIXME implement a test or something...
# TODO generate random?
@contextmanager
def adhoc_html(uid: str):
    domtag = dominate.dom_tag # type: ignore
    prev = domtag._get_thread_context
    def hacked_thread_contex(uid=uid):
        return uid

    try:
        domtag._get_thread_context = hacked_thread_contex
        yield
    finally:
        domtag._get_thread_context = prev
