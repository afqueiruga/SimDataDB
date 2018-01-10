SimDataDB
=======
Alejandro Francisco Queiruga  
2016-2017

A library for saving simulation results to a database, that is really a persistent function memoizer.

Intro
-----
I find myself often running a parameter study of a script file using a for loop, or a parallel.map operation. This is nice and easy, but after post-processing I always want to run more parameter sets! So, I kludgily modify the script and run again, but I have to manage the files and make sure I don't waste work redoing results, and then merge them later. Then, I have to write complicated post processing code.

Fortunately, managing data is a solved problem. SimDataDB wraps a simulation with sqlite3 querying/inserting to effectively persistently memoize the simulation.

Requirements
-----------

- Numpy for saving arrays

Usage
-------

First, you initialize a SimDataDB object which will load the ".db" file. Then, add a new table with a name,
and input call signature, and an output signature. Finally, decorate a function with the table name:
```Python
from SimDataDB import SimDataDB
sdb = SimDataDB("./fractureplane.db")
sdb.Add_Table("flowrun",
              (("Dp","FLOAT"), ("h","FLOAT"), ("L","FLOAT"), ("n",'FLOAT') ),
              ( ("v","FLOAT"),) )
@sdb.Decorate("flowrun", memoize=False)
def solve_a_setup(Dp,h, L, n):
    RUN A SIMULATION
	return v
```
Then just call the function. Every time the function is called, we check to see if the arguments
already exist in the table, and return the saved values if so. If the types are 'FLOAT', it checks
based on an epsilon. Or, directly query the database with SQL at a later time from another file 
(without needing the original function definition):
```Python
from SimDataDB import SimDataDB
sdb = SimDataDB("./fractureplane.db")
data = np.array(sdb.Query("select Dp,h,n,v from flowrun"))
```

License
--------

Whatever you want. Cite this repository if you use it, but there is no gauruntee it actually works.