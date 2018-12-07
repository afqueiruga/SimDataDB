from __future__ import print_function
import unittest as ut
import tempfile, shutil
import numpy as np

from SimDataDB import *

class return_type_test(ut.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_memoization_of_lists(self):
        sdb = SimDataDB(self.tmpdir+"/test_memoization_of_lists.db")
        @sdb.Decorate("results1",( ("x","FLOAT"), ("y","FLOAT") ),
                      ( ("z","FLOAT"), ),
                      memoize=True)
        def fake_sim(x,y):
            return (x+2*y),

        ret = fake_sim(1.0,2.0)
        self.assertTrue(type(ret) is tuple)
        ret2 = fake_sim(1.0,2.0)
        self.assertTrue(type(ret2) is tuple)
        self.assertTrue(ret[0]==ret2[0])

    def test_memoization_of_dicts(self):
        sdb = SimDataDB(self.tmpdir+"/test_memoization_of_dicts.db")
        @sdb.Decorate("results1",( ("x","FLOAT"), ("y","FLOAT") ),
                      ( ("z","FLOAT"), ),
                      memoize=True,dictreturn=True)
        def fake_sim(x,y):
            return {'z':x+2*y}

        ret = fake_sim(1.0,2.0)
        print(ret)
        self.assertTrue(type(ret) is dict)
        ret2 = fake_sim(1.0,2.0)
        print(ret2)
        self.assertTrue(type(ret2) is dict)
        self.assertTrue(ret['z']==ret2['z'])
