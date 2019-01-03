# pip3 install getch
# pylint: disable=no-name-in-module
from getch import getch # type: ignore

def getch_or_fail():
    import sys
    if not sys.stdin.isatty():
        raise RuntimeError('Expected interactive shell!')
    return getch()

def yesno_or_fail(prompt: str) -> bool:
    while True:
        print(f"{prompt} [y/n]: ")
        res = getch_or_fail().lower().strip()
        if res == 'y':
            return True
        elif res == 'n':
            return False

