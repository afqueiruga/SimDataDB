import mydb


mydb.setupDB("testA.db", "results1",( ("x","FLOAT"), ("y","FLOAT") ))

@mydb.scripter("testA.db", "results1")
def fake_sim(x,y):
    return x+2.0*y

fake_sim(1.0,1.5)

runs = mydb.grab_all("testA.db", "results1")
