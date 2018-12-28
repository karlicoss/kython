import json
from pathlib import Path
from typing import List, Union, Dict
import os
import sys

from kython.tui import yesno_or_fail

Pathish = Union[Path, str]

# TODO lock file or something???
# TODO local=true/false??
class JsonState:
    def __init__(
            self,
            path: Pathish,
            dryrun=False,
            default=None,
    ) -> None:
        if isinstance(path, str):
            self.path = Path(path)
        else:
            self.path = path
        self.dryrun = dryrun
        if default is None:
            default = {}

        self.default = default
        self.state = None

    def reset(self):
        if yesno_or_fail('reset the state?'):
            self._update(None)

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
                json.dump(st, fo)

