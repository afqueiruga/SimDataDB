from __future__ import print_function
import sqlite3
import pymysql
import numpy as np
import io, os
import warnings
import time, datetime
try:
    import cPickle as pickle
except:
    import pickle
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
# end citation
##
# TODO register with pymysql

# put pickles into blobs too
def adapt_obj(obj):

    data = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
    return sqlite3.Binary(data)
def convert_obj(text):
    obj = pickle.loads(text)
    return obj
sqlite3.register_adapter(object, adapt_obj)
sqlite3.register_converter("pickle", convert_obj)


class SimDataDB():
    def __init__(self,dbase, backend='lite'):
        """Constructs an object that references a database.
        If dbase is a file, it will use sqlite3. If it is an url, it will use mysql.

        backend will override its decision making."""
        self.backend = backend
        self.dbase = dbase
        # TODO detect backend
        # TODO check for a connection and throw an error if we can't find it.
        if backend=='lite':
            dbase_dir, _ = os.path.split(dbase)
            os.makedirs(dbase_dir, exist_ok=True)
        elif backend=='my':
            pass
        else:
            raise RuntimeError('Unsupported database driver')
        self.meta_data = (('timestamp','VARCHAR(30)'),('runtime','FLOAT'))
        self.callsigs = {}
        self.retsigs = {}


    def Get_Connection(self):
        if self.backend=='lite':
            return sqlite3.connect(self.dbase, detect_types=sqlite3.PARSE_DECLTYPES)
        elif self.backend=='my':
            return pymysql.connect(host=self.dbase, user='root', password='', db='db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
                                       
        
    def Add_Table(self, table, callsig, retsig):
        " Deprecated; do not call directly anymore "
        warnings.warn("Add the call signature using the decorator.", DeprecationWarning)
        self._add_table(table,callsig,retsig)

    def _add_table(self, table, callsig, retsig):
        conn = self.Get_Connection()
        callsig = tuple(callsig)
        retsig = tuple(retsig)
        with conn:
            c = conn.cursor()
            columns = [ '{0} {1}'.format(k[0],k[1]) for k in callsig + retsig + self.meta_data if k is not None ]
            cmd = 'CREATE TABLE IF NOT EXISTS {0} ( {1} );'.format(table, ', '.join(columns))
            print(cmd)
            c.execute(cmd)
            # save the argument list to this table
            self.callsigs[table] = callsig
            self.retsigs[table] = retsig

    def Decorate(self,table, callsig=None,retsig=None, memoize=True,dictreturn=False):
        if not callsig is None and not retsig is None:
            self._add_table(table,callsig,retsig)
        else:
            callsig = self.callsigs[table]
            retsig = self.retsigs[table]
        def wrap(f):
            def wrapper(*args):
                conn = self.Get_Connection()
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
                        # behave like the original
                        if dictreturn:
                            return { k:v for (k,tp),v in zip(self.retsigs[table],result) }
                        else:
                            return result
                # call the simulation
                start_timestamp = datetime.datetime.utcnow()
                start_time = time.time()
                ret = f(*args)
                end_time = time.time()
                run_time = end_time - start_time
                # Sanitize possible dictionary args
                try:
                    # Convert the dict into a list
                    flattened_ret = [ret[nm] for nm,tp in self.retsigs[table]]
                except TypeError:
                    # It better be a list
                    flattened_ret = list(ret)
                # Perform our conversions
                print(self.retsigs)
                for i,(varname,vartype) in enumerate(self.retsigs[table]):
                    if vartype=='pickle':
                        print("Running adapter")
                        flattened_ret[i] = adapt_obj(flattened_ret[i])
                # push args into dbase
                values = [ v for v,sig in zip(args,callsig) if sig is not None] \
                        + list(flattened_ret)+ [start_timestamp,run_time]
                if self.backend=='lite':
                    param_fmt = "?"
                else:
                    param_fmt = "%s"
                query_fmt = ",".join([
                    param_fmt.format(i) for i,_
                    in enumerate(self.callsigs[table] + self.retsigs[table] + self.meta_data)
                    if _ is not None])
                # print(values)
                # print(query_fmt)
                print(values)
                c.execute("INSERT INTO {0} VALUES ({1})".format(table,query_fmt),values)
                # commit
                conn.commit()
                conn.close()
                # behave like the original
                return ret
            return wrapper
        return wrap

    def Grab_All(self, table):
        conn = self.Get_Connection()
        c = conn.cursor()
        c.execute("SELECT * FROM {0}".format(table))
        rows = c.fetchall()
        return rows

    def Query(self,string):
        conn = self.Get_Connection()
        c = conn.cursor()
        c.execute(string)
        res = c.fetchall()
        try:
            res.sort()
        except ValueError:
            print("Failed to sort.")
        except TypeError:
            print("Type doesn't support sorting")
        conn.close()
        return [ list(k) for k in res  ]

    def __del__(self):
        pass
