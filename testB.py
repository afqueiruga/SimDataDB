from mydb import *


sdb = SimDataDB("testB.db")
sdb.Add_Table("results1",
              ( ("x","FLOAT"), ("y","FLOAT") ),
              ( ("z","array"), )
              )

@sdb.Decorate("results1")
def fake_sim(x,y):
    return np.array([x,2*y])

fake_sim(1.0,1.5)
fake_sim(1.0,1.5)
fake_sim(1.0,2.5)

rubs = sdb.Grab_All("results1")
print rubs
