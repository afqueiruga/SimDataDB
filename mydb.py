import sqlite3

class SimDataDB():
    def __init__(self,dbase):
        self.dbase = dbase
        self.conn = sqlite3.connect(dbase)
        self.dbs = {}
        
    def Add_Table(self, table, callsig):
        c = self.conn.cursor()
        columns = [ '{0} {1}'.format(k[0],k[1]) for k in callsig ]
        c.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, ', '.join(columns)) )

        # save the argument list to this table
        self.dbs[table] = callsig
        self.conn.commit()
        
    def Decorate(self,table):
        def wrap(f):
            def wrapper(*args):
                c = self.conn.cursor()
                # check if arguments exist already
                argcheck = " AND ".join([ "{0}={1}".format(argname[0],val)
                             for argname,val in zip(self.dbs[table], args) ])
                c.execute("SELECT EXISTS(SELECT 1 FROM {0} WHERE {1} LIMIT 1)".format(table, argcheck) )
                
                if c.fetchall()[0][0]==1:
                    return None # TODO: act like a memoizer
                # call the simulation
                ret = f(*args)
                # push args into dbase
                c.execute("INSERT INTO {0} VALUES ({1})".format(table, ", ".join([ str(a) for a in args]) ) )
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


        
def scripter(dbase, table):
    def wrap(f):
        def wrapper(*args):
            # check if args already in dbase
            conn = sqlite3.connect(dbase)
            c = conn.cursor()
            # c.execute("SELECT EXISTS(SELECT 1 FROM {0} WHERE {1} LIMIT 1)".fromat(table),)
            # call the simulation
            ret = f(*args)
            # push args into dbase
            
            c.execute("INSERT INTO {0} VALUES ({1})".format(table, ", ".join([ str(a) for a in args]) ) )
            conn.commit()
            conn.close()
        
            # save results
        
            # behave like the original
            return ret
        return wrapper
    return wrap

