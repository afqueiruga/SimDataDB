from __future__ import print_function
import unittest as ut
import tempfile, shutil

from SimDataDB import *


class mysql_test(ut.TestCase):
    def setUp(self):
        # Start a new database
        print('Starting a temporary sql server...')
        #self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        # Kill the database
        print('Successfully kill the sql server.')

    def test(self):
        sdb = SimDataDB('127.0.0.1', backend='my')
        self.assertEqual(sdb.backend, 'my')
        try:

            @sdb.Decorate('results', (('x', 'FLOAT'), ), (('y', 'FLOAT'), ))
            def foo(x):
                return 1 + x,
        except:
            print("Error: SQL server isn't running. Ok if not testing mysql.")
            return

        foo(1)
        rubs = sdb.Grab_All('results')
        self.assertEqual(len(rubs), 1)
