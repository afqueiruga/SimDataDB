from __future__ import print_function
import unittest as ut
import tempfile, shutil

from SimDataDB import *

class B_test(ut.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    def test(self):
        sdb = SimDataDB(self.tmpdir+"/testB.db")
        sdb.Add_Table("results1",
                      ( ("x","FLOAT"), ("y","FLOAT") ),
                      ( ("z","array"), )
                      )

        @sdb.Decorate("results1")
        def fake_sim(x,y):
            return np.array([x,2*y]),

        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,2.5))

        rubs = sdb.Grab_All("results1")
        print(rubs)
