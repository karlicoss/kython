from typing import List

def apply_on(predicate, root: str, action):
    from os import walk
    for dp, dirs, files in walk(root):
        if predicate(dp, dirs, files):
            action(dp)
    # TODO do not walk inside... ?
    # but for now it's fine, works quick enough..


