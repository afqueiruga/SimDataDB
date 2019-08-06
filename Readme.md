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

You can see an example usage in [PeriFlakes](https://github.com/afqueiruga/PeriFlakes/blob/master/PeriFlakes/batch.py).
First, you initialize a SimDataDB object which will load the ".db" file. Then decorate a function with a table name and a call and output signature:
```Python
from SimDataDB import SimDataDB
sdb = SimDataDB("./fractureplane.db")
@sdb.Decorate("flowrun",
              (("Dp","FLOAT"), ("h","FLOAT"), ("L","FLOAT"), ("n",'FLOAT') ),
              ( ("v","FLOAT"),),
	          memoize=False)
def solve_a_setup(Dp,h, L, n):
    RUN A SIMULATION
	return v,
```
Then just call the function. If the memoize flag is set to True, everytime the function is called, we check to see if the arguments already exist in the table. If there are values already there, they're fetched and returned instead of running the function again. If the types are 'FLOAT', it checks based on an epsilon (actually still a TODO!). The memoize flag is set to false when the simulations have random results to represent a sampling process.


Alternatively, you directly query the database with SQL at a later time from another file 
(without needing the original function definition):
```Python
from SimDataDB import SimDataDB
sdb = SimDataDB("./fractureplane.db")
data = np.array(sdb.Query("select Dp,h,n,v from flowrun"))
```
This is how I make plots for all of my papers!

License
--------

Copyright (C) Alejandro Francisco Queiruga

This library is released under version 3 of the GNU Lesser General Public License, as per LICENSE.txt.

Please mention this repository if you use this library.
