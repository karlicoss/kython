#!/usr/bin/env python3
import sys
from subprocess import check_call, run, check_output, PIPE
from pathlib import Path
from os.path import join
from shutil import copy
from tempfile import TemporaryDirectory
from typing import List, Dict

standalone: List[str] = [
    'cannon.py',
    'kompress.py',
    'kjson.py',
    'kjq.py',
    'kerror.py',
    'konsume.py',
    'kimport.py',
    'state.py',
]

def check(p: Path) -> List[str]:
    checks = []

    def check(*args, **kwargs):
        print(' '.join(args))
        checks.append(run(args, **kwargs))

    with TemporaryDirectory() as tdir:
    # TODO how to make sure they won't autoimport
        tmp = join(tdir, p.name)
        copy(p, tmp)

        check(
            'pytest',
            '--doctest-modules',
            '-s',
            tmp,
        )

        check(
            'mypy',
            '--strict-optional',
            '--check-untyped-defs',
            tmp,
        )

        check(
            'pylint',
            '-E',
            tmp,
        )

    errs = []
    for c in checks:
        if c.returncode == 0:
            continue
        errs.append(f'ERROR WHILE CHECKING {p}')
    return errs

def main():
    errors: List[str] = []

    for s in standalone:
        errors.extend(check(Path('kython').joinpath(s)))


    if len(errors) > 0:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("All good!")


if __name__ == '__main__':
    main()
