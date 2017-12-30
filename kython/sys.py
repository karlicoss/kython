import os

def src_relative(path: str) -> str:
    """
       Returns absolute path w.r.t. the running python script
    """
    # a bit dodgy...
    import sys
    src_file = sys.argv[0]
    return os.path.join(os.path.dirname(os.path.abspath(src_file)), path)

def home(path: str) -> str:
    return os.path.expanduser(os.path.join("~", path))
