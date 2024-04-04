def with_pivot(columns=None,
               pivot_column="",
               aggregation_columns=[]):
    """
        This transformation creates a new dataframe with a "group by"
        of one or more columns, and applies the specified aggregation functions.
        :param columns: Array
        :param pivot_column: String
        :param aggregation_columns: Array
            [
                {
                    "function": "concatenate",
                    "fields": ["test_1", "test_2", "test_3"],
                    "as": "concatenacion"
                }
            ]
        :return: Dataframe
        """
    import gc
    from pyspark.sql import functions as func
    from spark_scaffolder_transforms_tools import get_df_flatten_list

    if columns is None:
        columns = []
    if aggregation_columns is None:
        aggregation_columns = []

    to_type_func_agg = ["concatenate", "sum", "avg", "mean", "max", "min", "count", "first"]

    filter_array = list()
    for agg in aggregation_columns:
        _func = agg.get("function", None)

        if _func is None:
            raise Exception(f'The function in aggregationColumns is invalid: ("Is required function")')
        if _func not in to_type_func_agg:
            raise Exception(f'The function in aggregationColumns is invalid: (functions_agg)')

        _as = agg.get("as", None)
        if _as is None:
            raise Exception(f'The as in aggregationColumns is invalid: ("Not Empty")')

        _fields = agg.get("fields", None)
        if _func == "count" and _fields is None:
            _fields = "*"
        if _fields not in ("", "*"):
            filter_array.append((_func, _fields, _as))
    fields_list = get_df_flatten_list([fields_list[1] for fields_list in filter_array])

    def pivot(df):
        global new_func

        fields_agg = list()
        for _ in filter_array:
            _func = _[0]
            _fields = _[1]
            _alias = _[2]
            if _func == "concatenate":
                new_func = func.collect_list(func.struct(_fields)).alias(_alias)
            elif _func == "sum":
                new_func = func.sum(_fields).alias(_alias)
            elif _func == "avg":
                new_func = func.avg(_fields).alias(_alias)
            elif _func == "mean":
                new_func = func.mean(_fields).alias(_alias)
            elif _func == "max":
                new_func = func.max(_fields).alias(_alias)
            elif _func == "min":
                new_func = func.min(_fields).alias(_alias)
            elif _func == "count":
                new_func = func.count(_fields).alias(_alias)
            elif _func == "first":
                new_func = func.first(_fields).alias(_alias)
            fields_agg.append(new_func)

        _df_columns = columns + fields_list
        df = df.select([func.col(col_name) for col_name in _df_columns])
        df = df.groupBy(columns).pivot(pivot_column).agg(*fields_agg)
        return df

    gc.collect()
    return pivot
