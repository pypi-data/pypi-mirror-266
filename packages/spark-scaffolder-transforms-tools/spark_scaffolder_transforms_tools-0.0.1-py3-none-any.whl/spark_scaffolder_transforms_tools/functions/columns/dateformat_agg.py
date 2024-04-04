def with_dateformat_agg(columns=None,
                        agg_columns=None):
    """
    This transformation that are performed with the dates.
    :param columns: Array
    :param agg_columns: Array
        [
         {
            "function": "next_day",
            "parameters":"Mon",
            "as": "nextday"
         }
        ]
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if agg_columns is None:
        agg_columns = []
    if columns is None:
        columns = []

    to_type_func_agg = ["next_day", "date_add", "date_sub", "add_months"]
    to_type_parameters = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for agg in agg_columns:
        _func = agg.get("function", None)

        if _func is None:
            raise Exception(f'The function in agg_columns is invalid: ("Is required function")')
        if _func not in to_type_func_agg:
            raise Exception(f'The function in agg_columns is invalid: (functions_agg)')

        _parameters = agg.get("parameters", None)
        if _parameters is None:
            raise Exception(f'The as in agg_columns is invalid: ("Not Empty")')

        _as = agg.get("as", None)
        if _as is None:
            raise Exception(f'The as in agg_columns is invalid: ("Not Empty")')

        if _func == 'next_day':
            if _parameters not in to_type_parameters:
                raise Exception(f'The as in agg_columns is invalid: ("{to_type_parameters}")')

    def agg_dateformat(df):
        _df_columns = df.columns
        new_func = list()
        fields_agg = list()

        for _ in agg_columns:
            _func = _["function"]
            _parameters = _["parameters"]
            _alias = _["as"]
            for _fields in columns:
                _fields2 = str(_fields).replace("_", "").replace("-", "")
                _alias2 = f"{_alias}_{_fields2}"
                if _func == "next_day":
                    new_func = func.next_day(_fields, _parameters).alias(_alias2)
                elif _func == "date_add":
                    new_func = func.date_add(_fields, int(_parameters)).alias(_alias2)
                elif _func == "date_sub":
                    new_func = func.date_sub(_fields, int(_parameters)).alias(_alias2)
                elif _func == "add_months":
                    new_func = func.add_months(_fields, int(_parameters)).alias(_alias2)
                fields_agg.append(new_func)
        df = df.select(columns + [col_name for col_name in fields_agg])
        return df

    gc.collect()
    return agg_dateformat
