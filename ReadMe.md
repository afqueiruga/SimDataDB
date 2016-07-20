SimDataDB
=======

A library for saving simulation results to a database.

Intro
-----
I find myself often running a parameter study of a script file using a for loop, or a parallel.map operation. This is nice and easy, but after post-processing I always want to run more parameter sets! So, I kludgily modify the script and run again, but I have to manage the files and make sure I don't waste work redoing results, and then merge them later. Then, I have to write complicated post processing code.

Fortunately, managing data is a solved problem. SimDataDB wraps a simulation with sqlite3 querying/inserting to effectively persistently memoize the simulation.

Requirements
-----------

- Numpy for saving arrays

Usage
-------

TODO

License
--------

IDGAF
