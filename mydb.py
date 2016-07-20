import sqlite3


def setupDB(dbase, table, args):
    conn = sqlite3.connect(dbase)
    c = conn.cursor()
    columns = [ '{0} {1}'.format(k[0],k[1]) for k in args ]
    try:
        c.execute('CREATE TABLE {0} ({1})'.format(table, ', '.join(columns)) )
    except:
        pass
    conn.commit()
    conn.close()
    
def scripter(dbase, table):
    def wrap(f):
        def wrapper(*args):
            # check if args already in dbase
            conn = sqlite3.connect(dbase)
            c = conn.cursor()
 s           # c.execute("SELECT EXISTS(SELECT 1 FROM {0} WHERE {1} LIMIT 1)".fromat(table),)
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
    with con:
        c = con.cursor()
        c.execute("SELECT * FROM {0}".format(table))
        rows = c.fetchall()
        return rows
def runner(S, args):
    pass


                  
