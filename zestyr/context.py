from collections import namedtuple
import urllib3

Context = namedtuple("Context", "quiet verbose dry_run http_lib")

def default():
    return Context(False, False, False, urllib3)
