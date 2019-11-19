from __future__ import print_function
import unittest as ut
import tempfile, shutil
import numpy as np

from SimDataDB import *

class MyObj(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        
class pickle_test(ut.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        
    def test(self):
        print("Writing to ",self.tmpdir+"/testpick.db")
        sdb = SimDataDB(self.tmpdir+"/testpick.db")
        @sdb.Decorate("results1",( ("x","FLOAT"), ("y","FLOAT") ),
                      ( ("z","pickle"), ))
        def fake_sim(x,y):
            return MyObj(x,y),

        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,1.5))
        print(fake_sim(1.0,2.5))

        rubs = sdb.Grab_All("results1")
        print(rubs)
        self.assertTrue(True)

