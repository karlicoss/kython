import json
from pathlib import Path
from typing import List, Union, Dict
import logging
import os
import sys
import warnings

PathIsh = Union[str, Path]

from atomicwrites import atomic_write

# TODO test it..
# borrow tests from org-view?
# TODO lock file or something???
# TODO local=true/false??
# TODO hmm. state should be ordered ideally? so it's easy to add/remove items?
# would require storing as list of lists? or use that https://stackoverflow.com/a/6921760/706389
class JsonState:
    def __init__(
            self,
            path: PathIsh,
            dry_run=False,
            default=None,
            logger=logging.getLogger('json-state'),
    ) -> None:
        self.path = Path(path)

        # TODO dryrun is hard to implement properly because of reading from disk every time...
        self.dryrun = dry_run
        if default is None:
            default = {}

        self.default = default
        self.state = None
        self.logger = logger
        # TODO for simplicity, write empty if file doesn't exist??

    def reset(self):
        from kython.tui import yesno_or_fail
        if yesno_or_fail('reset the state?'):
            self._update(None)

    def __contains__(self, key: str) -> bool:
        return key in self.get()
        # TODO hmm. maybe make it append only?

    def __setitem__(self, key: str, value) -> None:
        current = self.get()
        assert key not in current # just in case
        current[key] = value

        if self.dryrun:
            self.logger.debug('dry run! ignoring %s: %s', key, value)
            return

        with atomic_write(str(self.path), overwrite=True) as fo:
            json.dump(current, fo, indent=1, sort_keys=True)

    # TODO shit. get and reset interact in weird ways. it's way more complicated than i wanted
    def get(self):
        if self.state is None:
            if not self.path.exists():
                self.state = self.default # TODO deepcopy?? or factory
            else:
                with self.path.open('r') as fo:
                    self.state = json.load(fo)
        return self.state

    def update(self, st):
        assert st is not None
        return self._update(st)

    def _update(self, st):
        # TODO FIXME setitem should use update?
        self.state = st
        if self.dryrun:
            return
        if st is None:
            if self.path.exists():
                self.path.unlink()
        else:
            with self.path.open('w') as fo:
                json.dump(st, fo, indent=1, sort_keys=True)

    def feed(self, key, value, action) -> None:
        if key in self:
            self.logger.debug(f'already handled: %s: %s', key, value)
            return
        self.logger.info(f'adding %s: %s', key, value)
        # TODO not sure about print...
        print(f'adding new item {key}: {value}')
        action()
        self[key] = repr(value)


# TODO FIXME try with error, make sure it's executed before action

def tes_statet(tmp_path):
    path = tmp_path / 'state.json'
    state = JsonState(path)

    assert not path.exists()

    res = []

    def feed(k, v):
        def action():
            res.append(v)
        state.feed(k, v, action=action)

    feed('a', 123)
    assert res == [123]
    feed('a', 456)
    assert res == [123]

    state = JsonState(path)

    feed('b', 'abacaba')

    assert res == [123, 'abacaba']
    feed('a', None)
    assert res == [123, 'abacaba']


