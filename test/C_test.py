from __future__ import print_function
import unittest as ut
import tempfile, shutil

from mydb import *

class C_test(ut.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    def test(self):
        print("Writing to ",self.tmpdir+"/testC.db")
        sdb = SimDataDB(self.tmpdir+"/testC.db")
        @sdb.Decorate("results1",( ("x","FLOAT"), ("y","FLOAT") ),
                      ( ("z","array"), ))
        def fake_sim(x,y):
            return np.array([x,2*y]),

        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,2.5))

        rubs = sdb.Grab_All("results1")
        print(rubs)
        self.assertTrue(False)
