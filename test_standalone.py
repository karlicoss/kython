#!/usr/bin/env python3
import sys
from subprocess import check_call, run, check_output, PIPE
from pathlib import Path
from os.path import join
from shutil import copy
from tempfile import TemporaryDirectory
from typing import List, Dict

standalone: List[str] = [
    'kompress.py',
    'kjson.py',
    'kjq.py',
    'kerror.py',
    'konsume.py',
    'state.py',
]

def check(p: Path) -> List[str]:
    checks = []
    with TemporaryDirectory() as tdir:
    # TODO how to make sure they won't autoimport
        tmp = join(tdir, p.name)
        copy(p, tmp)

        checks.append(run([
            'pytest',
            '--doctest-modules',
            '-s',
            tmp,
        ], stdout=PIPE, cwd=tdir))

        checks.append(run([
            'mypy',
            '--strict-optional',
            '--check-untyped-defs',
            tmp
        ], stdout=PIPE, cwd=tdir))

        checks.append(run([
            'pylint',
            '-E',
            tmp,
        ], stdout=PIPE, cwd=tdir))

    errs = []
    for c in checks:
        if c.returncode == 0:
            continue
        errs.append(c.stdout.decode('utf8'))
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
