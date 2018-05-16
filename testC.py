from mydb import *


sdb = SimDataDB("testC.db")
@sdb.Decorate("results1",( ("x","FLOAT"), ("y","FLOAT") ),
              ( ("z","array"), ))
def fake_sim(x,y):
    return np.array([x,2*y]),

print fake_sim(1.0,1.5)
print fake_sim(1.0,1.5)
print fake_sim(1.0,2.5)

rubs = sdb.Grab_All("results1")
print rubs
