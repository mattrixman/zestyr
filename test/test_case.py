import sys, os
sys.path.insert(0, os.path.abspath('..'))

import ipdb
import IPython
def undebug():
    def f() : pass
    ipdb.set_trace = f
    IPython.embed = f

import unittest
import zestyr
import urllib3-mock

class Case(unittest.TestCase):

    def test_mock(self):



