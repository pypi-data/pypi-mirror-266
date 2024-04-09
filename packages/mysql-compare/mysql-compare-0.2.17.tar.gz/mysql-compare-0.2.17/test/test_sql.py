def get_sqltext(keycols: list[tuple[str, str]], ckpt_row: dict = None):
    _keyval = ckpt_row
    _key_colns = ", ".join([f"`{col[0]}`" for col in keycols])
    params: list = []
    where_clause = ""
    src_database = "db"
    src_table = "tab1"
    limit_size = 6000
    # select * from where 1 = 1 and ((a > xxx) or (a = xxx and b > yyy) or (a = xxx and b = yyy and c > zzz)) order by a,b,c limit checksize

    if _keyval:
        where_conditions = []
        for end_idx in range(len(keycols)):
            condition_parts = []
            for i, (column_name, column_type) in enumerate(keycols[: end_idx + 1]):
                operator = ">" if i == end_idx else "="
                if column_type in ["int", "double", "char", "date", "decimal"]:
                    condition_parts.append(f"`{column_name}` {operator} %s")
                    params.append(ckpt_row[column_name])
                else:
                    raise ValueError(f"Data type: [{column_type}] is not supported yet.")

            where_conditions.append(" and ".join(condition_parts))
        where_clause = "WHERE" + "(" + ") or (".join(where_conditions) + ") "

    statement = f"SELECT {_key_colns} FROM {src_database}.{src_table} {where_clause}ORDER BY {_key_colns} LIMIT {limit_size}"
    return statement


print("11")

print(get_sqltext([("a", "int"), ("b", "int")]))
print(get_sqltext([("a", "int"), ("b", "int")], {"a": 1100, "b": 11}))
# print(get_sqltext([("a", "int"), ("b", "int"), ("c", "datetime")], {"a": 1100, "b": 11, "c": "a"}))
