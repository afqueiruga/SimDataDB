import sqlite3

class SimDataDB():
    def __init__(self,dbase):
        self.dbase = dbase
        self.conn = sqlite3.connect(dbase)
        self.dbs = {}
        
    def Add_Table(self, table, args):
        c = self.conn.cursor()
        columns = [ '{0} {1}'.format(k[0],k[1]) for k in args ]
        try:
            c.execute('CREATE TABLE if not exists {0} ({1})'.format(table, ', '.join(columns)) )
        except:
            pass
        # save the argument list to this table
        self.dbs[table] = args
        self.conn.commit()
        
    def Decorate(self,table):
        def wrap(f):
            def wrapper(*args):
                c = self.conn.cursor()
                # check if arguments exist already
                
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


    
def setupDB(dbase, table, args):
    conn = sqlite3.connect(dbase)
    c = conn.cursor()
    columns = [ '{0} {1}'.format(k[0],k[1]) for k in args ]
    c.execute('CREATE TABLE if not exists {0} ({1})'.format(table, ', '.join(columns)) )

    conn.commit()
    conn.close()
    
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

def grab_all(dbase,table):
    con = sqlite3.connect(dbase)

def runner(S, args):
    pass


                  
