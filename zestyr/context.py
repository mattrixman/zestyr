from collections import namedtuple

Context = namedtuple("Context", "quiet verbose dry_run")

def default():
    return Context(False, False, False)
