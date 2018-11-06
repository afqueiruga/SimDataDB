from __future__ import print_function
import sqlite3
import numpy as np
import io
import warnings
import time, datetime

##
# BEGIN CITATION:
# http://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
#
def adapt_array(arr):
    """
    citation: http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())
def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)
#
# end citation
##

class SimDataDB():

    def __init__(self,dbase):
        self.dbase = dbase
        self.meta_data = (('timestamp','STRING'),('run_time','FLOAT'))
        self.callsigs = {}
        self.retsigs = {}

    def Add_Table(self, table, callsig, retsig):
        " Deprecated; do not call directly anymore "
        warnings.warn("Add the call signature using the decorator.", DeprecationWarning)
        self._add_table(table,callsig,retsig)

    def _add_table(self, table, callsig, retsig):
        conn = sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)

        with conn:
            c = conn.cursor()
            columns = [ '{0} {1}'.format(k[0],k[1]) for k in callsig + retsig + self.meta_data if k is not None]
            c.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, ', '.join(columns)) )
            # save the argument list to this table
            self.callsigs[table] = callsig
            self.retsigs[table] = retsig

    def Decorate(self,table, callsig=None,retsig=None, memoize=True):
        if not callsig is None and not retsig is None:
            self._add_table(table,callsig,retsig)
        else:
            callsig = self.callsigs[table]
            retsig = self.retsigs[table]
        def wrap(f):
            def wrapper(*args):
                conn = sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)
                c = conn.cursor()
                # check if arguments exist already
                if memoize:
                    # TODO: check for floating point arguments
                    argcheck = " AND ".join([ "{0}='{1}'".format(argname[0],val)
                                for argname,val in zip(self.callsigs[table], args)
                                              if argname is not None])
                    c.execute("SELECT {2} FROM {0} WHERE {1} LIMIT 1".format(
                        table, argcheck, ", ".join([k[0] for k in self.retsigs[table]])) )
                    result = c.fetchone()
                    if result!=None:
                        conn.close()
                        return result[0]
                # call the simulation
                start_timestamp = datetime.datetime.utcnow()
                start_time = time.time()
                ret = f(*args)
                end_time = time.time()
                run_time = end_time - start_time
                # Sanitize possible dictionary args
                try:
                    # Convert the dict to a dictionary
                    ret = [ret[nm] for nm,tp in self.retsigs[table]]
                except TypeError:
                    # It better be a list
                    pass
                # push args into dbase
                c.execute("INSERT INTO {0} VALUES ({1})".format(
                    table,",".join(["?" for _ in self.callsigs[table] + self.retsigs[table] + self.meta_data
                                   if _ is not None])),
                          [ v for v,sig in zip(args,callsig) if sig is not None]+list(ret)+ [start_time,run_time] )
                # commit
                conn.commit()
                conn.close()
                # behave like the original
                return ret
            return wrapper
        return wrap

    def Get_Connection(self):
        return sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)

    def Grab_All(self, table):
        conn = sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("SELECT * FROM {0}".format(table))
        rows = c.fetchall()
        return rows

    def Query(self,string):
        conn = sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute(string)
        res = c.fetchall()
        try:
            res.sort()
        except ValueError:
            print("Failed to sort. The keys were ", res)
        conn.close()
        return [ list(k) for k in res  ]

    def __del__(self):
        pass
