from typing import Any, Tuple

import sqlite3
import os
import warnings
import time, datetime

try:
    import pymysql
    HAVE_PYMYSQL = True
except:
    HAVE_PYMYSQL = False

from .adapters import *


class SimDataDB2():
    def __init__(self, dbase, table=None, memoize=True, backend='lite'):
        self.backend = backend
        self.dbase = dbase
        self.table = table
        self.memoize = memoize
        # TODO detect backend
        # TODO check for a connection and throw an error if we can't find it.
        if backend == 'lite':
            dbase_dir, _ = os.path.split(dbase)
            os.makedirs(dbase_dir, exist_ok=True)
        elif backend == 'my':
            if not HAVE_PYMYSQL:
                raise RuntimeError('MySQL requires pymysql.')
        else:
            raise RuntimeError('Unsupported database driver')
        self.meta_data = (('timestamp', 'VARCHAR(30)'), ('runtime', 'FLOAT'))

    def GetConnection(self):
        if self.backend == 'lite':
            return sqlite3.connect(self.dbase,
                                   detect_types=sqlite3.PARSE_DECLTYPES)
        elif self.backend == 'my':
            if not HAVE_PYMYSQL:
                raise RuntimeError('MySQL requires pymysql.')
            return pymysql.connect(host=self.dbase,
                                   user='root',
                                   password='',
                                   db='db',
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

    def _add_table(self, table, callsig, retsig):
        callsig = tuple(callsig)
        retsig = tuple(retsig)
        with self.GetConnection() as conn:
            c = conn.cursor()
            columns = [
                f'{name} {typename}'
                for name, typename in callsig + retsig + self.meta_data
            ]
            cols = ', '.join(columns)
            cmd = f'CREATE TABLE IF NOT EXISTS {table} ( {cols} );'
            print(cmd)
            c.execute(cmd)

    def __call__(self, f):
        """The decorator interface."""
        if self.table is None:
            self.table = f.__name__
        # TODO assert that the return type should be a Tuple
        annotations = f.__annotations__.copy()
        return_types = annotations['return'].__args__
        retsig = {f'_{i}': v for i, v in enumerate(return_types)}
        annotations.pop('return')
        callsig = annotations

        callsig = tuple([(k, type_to_sql_typestring(v))
                         for k, v in callsig.items()])
        retsig = tuple([(k, type_to_sql_typestring(v))
                        for k, v in retsig.items()])

        self._add_table(self.table, callsig, retsig)

        dictreturn = False  # TODO cleanup

        def wrapper(*args):
            conn = self.GetConnection()
            c = conn.cursor()
            # check if arguments exist already
            if self.memoize:
                # TODO: check for floating point arguments
                argcheck = " AND ".join([
                    f"{argname[0]}='{val}'"
                    for argname, val in zip(callsig, args)
                    if argname is not None
                ])
                list_of_vars = ", ".join([k[0] for k in retsig])
                c.execute(
                    f"SELECT {list_of_vars} FROM {self.table} WHERE {argcheck} LIMIT 1"
                )
                result = c.fetchone()
                if result != None:
                    conn.close()
                    # behave like the original
                    if dictreturn:
                        return {k: v for (k, tp), v in zip(retsig, result)}
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
                flattened_ret = [ret[nm] for nm, tp in retsig]
            except TypeError:
                # It better be a list
                flattened_ret = list(ret)
            # Perform our conversions
            for i, (varname, vartype) in enumerate(retsig):
                if vartype == 'pickle':
                    flattened_ret[i] = adapt_obj(flattened_ret[i])
            # push args into dbase
            values = [ v for v,sig in zip(args,callsig) if sig is not None] \
                    + list(flattened_ret)+ [start_timestamp,run_time]
            if self.backend == 'lite':
                param_fmt = "?"
            else:
                param_fmt = "%s"
            query_fmt = ",".join([
                param_fmt.format(i)
                for i, _ in enumerate(callsig + retsig + self.meta_data)
                if _ is not None
            ])

            c.execute(f"INSERT INTO {self.table} VALUES ({query_fmt})", values)
            conn.commit()
            conn.close()
            # behave like the original
            return ret

        return wrapper

    def GrabAll(self):
        with self.GetConnection() as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM {self.table}")
            rows = c.fetchall()
        return rows

    def Query(self, string):
        with self.GetConnection() as conn:
            c = conn.cursor()
            c.execute(string)
            res = c.fetchall()
        try:
            res.sort()
        except ValueError:
            print("Failed to sort.")
        except TypeError:
            print("Type doesn't support sorting.")
        return [list(k) for k in res]
