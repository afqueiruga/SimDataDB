import sqlite3
import numpy as np
import io

##
# BEGIN CITATION:
# http://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
#
def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
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
        self.conn = sqlite3.connect(dbase, detect_types=sqlite3.PARSE_DECLTYPES)
        self.callsigs = {}
        self.retsigs = {}
        
    def Add_Table(self, table, callsig, retsig):
        c = self.conn.cursor()
        columns = [ '{0} {1}'.format(k[0],k[1]) for k in callsig + retsig ]
        
        c.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, ', '.join(columns)) )

        # save the argument list to this table
        self.callsigs[table] = callsig
        self.retsigs[table] = retsig
        self.conn.commit()
        
    def Decorate(self,table):
        def wrap(f):
            def wrapper(*args):
                c = self.conn.cursor()
                # check if arguments exist already
                argcheck = " AND ".join([ "{0}={1}".format(argname[0],val)
                             for argname,val in zip(self.callsigs[table], args) ])
                c.execute("SELECT {2} FROM {0} WHERE {1} LIMIT 1".format(
                    table, argcheck, " ".join([k[0] for k in self.retsigs[table]])) )
                result = c.fetchone()
                if result!=None:
                    return result[0]
                # call the simulation
                ret = f(*args)
                # push args into dbase
                c.execute("INSERT INTO {0} VALUES (?,?,?)".format(table),
                           [args[0],args[1],ret] )
                # commit
                self.conn.commit()
                # behave like the original
                return ret
            return wrapper
        return wrap
    
    def Grab_All(self, table):
        c = self.conn.cursor()
        c.execute("SELECT * FROM {0}".format(table))
        rows = c.fetchall()
        return rows
        
    def __del__(self):
        self.conn.commit()
        self.conn.close()
