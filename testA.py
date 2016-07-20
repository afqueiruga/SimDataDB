from mydb import *


sdb = SimDataDB("testA.db")
sdb.Add_Table("results1",
              ( ("x","FLOAT"), ("y","FLOAT") ),
              ( ("z","FLOAT"), )
              )

@sdb.Decorate("results1")
def fake_sim(x,y):
    return x+2.0*y

fake_sim(1.0,1.5)
fake_sim(1.0,1.5)
fake_sim(1.0,2.5)

rubs = sdb.Grab_All("results1")
print rubs
