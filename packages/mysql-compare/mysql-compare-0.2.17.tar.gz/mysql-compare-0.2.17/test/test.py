import mysql.connector
from config import args_source_dsn
import time
from typing import Union

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=None,
    pool_size=2,
    pool_reset_session=True,
    **args_source_dsn,
)


def get_full_table_orderby_keys(con: mysql.connector.MySQLConnection, database, table, fetch_size: int, keycols: list[tuple[str, str]], keyval: dict = None):
    _keyval = keyval
    # select * from where 1 = 1 and a >= xxx and b >= yyy and c > zzz order by a,b,c limit checksize
    # select * from where 1 = 1 and ((a > xxx) or (a = xxx and b > yyy) or (a = xxx and b = yyy and c > zzz)) order by a,b,c limit checksize

    while True:
        key_colns = ", ".join(list(map(lambda c: c[0], keycols)))
        if _keyval is None:
            statement = f"SELECT {key_colns} FROM {database}.{table} ORDER BY {key_colns} limit {fetch_size}"
        else:
            whereval = []
            col_cnt = len(keycols)
            for i in range(0, col_cnt):
                coln, colt = keycols[i]
                symbol = ">=" if i == col_cnt - 1 else ">="
                if colt in ["int", "bigint"]:
                    whereval.append(f"{coln} {symbol} {_keyval[coln]}")
                elif colt == "varchar":
                    whereval.append(f'{coln} {symbol} "{_keyval[coln]}"')
                else:
                    raise Exception(f"data type: {colt} not suppert yet.")
            statement = f"SELECT {key_colns} FROM {database}.{table} WHERE {' AND '.join(whereval)} ORDER BY {key_colns} limit {fetch_size}"
            print(statement, _keyval)
        with con.cursor(dictionary=True) as cur:
            cur.execute(statement)
            _cnt = 0
            for row in cur.fetchall():
                _keyval = row
                _cnt += 1
                yield row
            if _cnt != fetch_size or _cnt == 0:
                return
