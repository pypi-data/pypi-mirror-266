def with_offset_column(expressions=None):
    """
    Field using windowing.
    :param expressions: Array
            [
                {
                 "partition_columns":["field1"],
                 "order_column": [{"field1":"asc"}],
                 'new_column': "test_col",
                 "windows_functions": [{"function_name":"lag","offset":1, "column": "field2" },
                                       {"function_name":"lead","offset":1, "column": "field3" }]
                }
           ]
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func
    from pyspark.sql.window import Window

    if expressions is None:
        expressions = []

    to_type_key_cond = ['partition_columns', 'order_column', 'new_column', 'windows_functions']
    to_type_func_window_a = ['row_number', 'rank', 'percent_rank', 'dense_rank', 'cume_dist']
    to_type_func_window_b = ['lead', 'lag']
    to_type_func_window_c = ['ntile']

    if len(expressions) == 0:
        raise Exception(f'require var: expressions ("expressions Not Empty")')

    for exp in expressions[0].keys():
        if exp not in to_type_key_cond:
            raise Exception(f'Dictionary field does not exist:("is invalid")')

    _partition_col = expressions[0]["partition_columns"]
    _order_col = expressions[0]["order_column"]
    _new_col = expressions[0]["new_column"]
    _windows_functions = expressions[0]["windows_functions"]

    if not _partition_col:
        raise Exception(f'require var: partition_col Not Empty")')
    elif not _order_col:
        raise Exception(f'require var: order_col Not Empty")')
    elif not _new_col:
        raise Exception(f'require var: new_col Not Empty")')
    elif not _windows_functions:
        raise Exception(f'require var: windows_functions Not Empty")')

    for w in _windows_functions:
        _func_name = w["function_name"]
        _windows_offset = w.get("offset", None)
        _windows_column = w.get("column", None)

        if _func_name in to_type_func_window_a:
            continue
        elif _func_name in to_type_func_window_b:
            if _windows_offset in (None, ""):
                raise Exception(f'require var windows_functions Dictionary field does not exist:("offset")')
            elif _windows_column in (None, ""):
                raise Exception(f'require var windows_functions Dictionary field does not exist:("column")')
        elif _func_name in to_type_func_window_c:
            if _windows_offset in (None, ""):
                raise Exception(f'require var windows_functions Dictionary field does not exist:("offset")')

    def offset_column(df):
        global func_order
        global w_funct

        _df_columns = df.columns
        _partition_col = expressions[0]["partition_columns"]
        _order_col = expressions[0]["order_column"]
        _windows_func = expressions[0]["windows_functions"]
        _new_col = expressions[0]["new_column"]
        _order_column_keys = list(_order_col[0].keys())

        for orders in _order_column_keys:
            if _order_col[0][orders] == "desc":
                func_order = func.col(orders).desc()
            elif _order_col[0][orders] == "asc":
                func_order = func.col(orders).asc()

        window_spec = Window.partitionBy(_partition_col).orderBy(func_order)
        w_func_list = list()
        for w in _windows_func:
            _func_name = w["function_name"]
            _windows_offset = int(w.get("offset", None))
            _windows_column = w.get("column", None)

            if _func_name == "row_number":
                w_funct = func.row_number().over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "rank":
                w_funct = func.rank().over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "percent_rank":
                w_funct = func.percent_rank().over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "dense_rank":
                w_funct = func.dense_rank().over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "ntile":
                w_funct = func.ntile(_windows_offset).over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "cume_dist":
                w_funct = func.cume_dist().over(window_spec).alias(f"{_new_col}_{_func_name}")
            elif _func_name == "lag":
                w_funct = func.lag(_windows_column, _windows_offset).over(window_spec).alias(
                    f"{_new_col}_{_func_name}")
            elif _func_name == "lead":
                w_funct = func.lead(_windows_column, _windows_offset).over(window_spec).alias(
                    f"{_new_col}_{_func_name}")
            w_func_list.append(w_funct)

        df = df.select(_df_columns + [w_func for w_func in w_func_list])
        return df

    gc.collect()
    return offset_column
