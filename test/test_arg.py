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

class Args(unittest.TestCase):

    # correct callback gets called with correct repo name

    def test_parse_add_verbose(self):
        argv = ['test_arg', '-v', 'new', 'foo']
        parsed = zestyr.case.parse(argv)

        print(parsed)
        self.assertEqual('new', parsed.verb)

        self.assertTrue(hasattr(parsed, 'desc'))
        self.assertFalse(hasattr(parsed, 'id'))
        self.assertEqual('foo', parsed.desc)

        self.assertFalse(parsed.quiet)
        self.assertTrue(parsed.verbose)
        self.assertFalse(parsed.local_dry_run)
        self.assertFalse(parsed.dry_run)

    def test_parse_rm_quiet(self):
        argv = ['test_arg', '--quiet', 'rm', '123']
        parsed = zestyr.case.parse(argv)

        self.assertEqual('rm', parsed.verb)

        self.assertFalse(hasattr(parsed, 'desc'))
        self.assertTrue(hasattr(parsed, 'id'))
        self.assertEqual('123', parsed.id)

        self.assertTrue(parsed.quiet)
        self.assertFalse(parsed.verbose)
        self.assertFalse(parsed.local_dry_run)
        self.assertFalse(parsed.dry_run)

    def test_parse_push_dry(self):
        argv = ['test_arg', '-d', 'push', '123']
        parsed = zestyr.case.parse(argv)

        self.assertEqual('push', parsed.verb)

        self.assertFalse(hasattr(parsed, 'desc'))
        self.assertTrue(hasattr(parsed, 'id'))
        self.assertEqual('123', parsed.id)

        self.assertFalse(parsed.quiet)
        self.assertFalse(parsed.verbose)
        self.assertFalse(parsed.local_dry_run)
        self.assertTrue(parsed.dry_run)

    def test_parse_no_verb_exit_nonzero(self):
        argv = ['-d']
        with open(os.devnull, 'w') as null:
            backup = sys.stderr
            sys.stderr = null
            with self.assertRaises(SystemExit) as cm:
                parsed = zestyr.case.parse(argv)
            self.assertNotEqual(0, cm.exception.code)
        sys.stderr = backup
