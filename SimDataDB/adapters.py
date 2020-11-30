import io
import numpy as np
import sqlite3
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


def type_to_sql_typestring(x):
    if type(x) is str:
        return x
    elif x==float:
        return 'FLOAT'
    elif x==int:
        return 'INT'
    elif x==str:
        return 'VARCHAR(30)'
    elif x==np.ndarray:
        return 'array'
    else:
        return 'pickle'
