import json
from pathlib import Path
from typing import List, Union, Dict
import logging
import os
import sys

from kython.tui import yesno_or_fail

from kython.ktyping import PathIsh

from atomicwrites import atomic_write

# TODO test it..
# TODO lock file or something???
# TODO local=true/false??
class JsonState:
    def __init__(
            self,
            path: PathIsh,
            dryrun=False,
            default=None,
            logger=logging.getLogger('kython-json-state'),
    ) -> None:
        self.path = Path(path)
        self.dryrun = dryrun
        if default is None:
            default = {}

        self.default = default
        self.state = None
        self.logger = logger
        # TODO for simplicity, write empty if file doesn't exist??

    def reset(self):
        if yesno_or_fail('reset the state?'):
            self._update(None)

    def __contains__(self, key: str) -> bool:
        return key in self.get()
        # TODO hmm. maybe make it append only?

    def __setitem__(self, key: str, value) -> None:
        current = self.get()
        assert key not in current # just in case
        current[key] = value
        with atomic_write(str(self.path), overwrite=True) as fo:
            json.dump(current, fo, indent=1, sort_keys=True)

    # TODO shit. get and reset interact in weird ways. it's way more complicated than i wanted
    def get(self):
        if self.state is None:
            if not self.path.exists():
                self.state = self.default # TODO deepcopy??
            else:
                with self.path.open('r') as fo:
                    self.state = json.load(fo)
        return self.state

    def update(self, st):
        assert st is not None
        return self._update(st)

    def _update(self, st):
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
        print(f'adding new item {key}: {value}')
        action()
        # TODO FIXME check for lock files here?
        self[key] = repr(value)



