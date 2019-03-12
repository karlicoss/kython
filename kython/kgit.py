from datetime import datetime
import logging
from subprocess import check_output
import json
from typing import List, Tuple, Optional, NamedTuple, Union, Dict, Any
from pathlib import Path


PathIsh = Union[Path, str]

Sha = str

class Rev(NamedTuple):
    sha: Sha
    when: datetime

    def __str__(self) -> Sha:
        return self.sha

RevIsh = Union[Rev, Sha]


def _parse_date(line):
    ds = ' '.join(line.split()[1:])
    return datetime.strptime(ds, '%a %b %d %H:%M:%S %Y %z')


class RepoHandle:
    def __init__(self, repo: str, logger: Optional[logging.Logger]=None) -> None:
        self.repo = repo
        if logger is None:
            logger = logging.getLogger('RepoHandle')
        self.logger = logger

    def _check_output(self, *args):
        cmd = [
            'git', f'--git-dir={self.repo}/.git', *args
        ]
        self.logger.debug(' '.join(cmd))
        return check_output(cmd)

    def revisions(self):
        return self.get_revisions()


    def get_revisions(self) -> List[Rev]:
        ss = list(reversed(self._check_output(
            'log',
            '--pretty=format:%h %ad',
            '--no-patch',
        ).decode('utf8').splitlines()))
        return [Rev(sha=l.split()[0], when=_parse_date(l)) for l in ss]

    def read_text(self, rev: RevIsh, path: PathIsh) -> str:
        sha: Sha = str(rev)
        path = Path(path)
        assert not path.is_absolute(), f"{path} can't be absolute!"

        return self._check_output(
            'show',
            f'{sha}:{path}',
        ).decode('utf8')

    # def get_all_versions(self):
    #     revs = self.get_revisions()
    #     jsons = []
    #     for rev, dd in revs:
    #         cc = self.get_content(rev)
    #         j: Dict[str, Any] # TODO jsontype??
    #         if len(cc.strip()) == 0:
    #             j = {}
    #         else:
    #             j = json.loads(cc)
    #         jsons.append((rev, dd, j))
    #     return jsons
