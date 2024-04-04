def with_dateformat_extract(columns=None,
                            extract_columns=None):
    """
    This transformations that are performed to extract dates
    :param columns: Array
    :param extract_columns: Array
        [

            {
                "function": "last_day",
                "as": "lastday"
            }
        ]
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if extract_columns is None:
        extract_columns = []
    if columns is None:
        columns = []

    to_type_func_agg = ["last_day", "year", "month", "dayofmonth", "dayofyear",
                        "dayofweek", "quarter", "hour", "minute", "second"]

    for agg in extract_columns:
        _func = agg.get("function", None)

        if _func is None:
            raise Exception(f'The function in extract_columns is invalid: ("Is required function")')
        if _func not in to_type_func_agg:
            raise Exception(f'The function in extract_columns is invalid: (functions_agg)')

        _as = agg.get("as", None)
        if _as is None:
            raise Exception(f'The as in extract_columns is invalid: ("Not Empty")')

    def extract_dateformat(df):
        _df_columns = df.columns
        new_func = list()
        fields_agg = list()

        for _ in extract_columns:
            _func = _["function"]
            _alias = _["as"]

            for _fields in columns:
                _fields2 = str(_fields).replace("_", "").replace("-", "")
                _alias2 = f"{_alias}_{_fields2}"

                if _func == "last_day":
                    new_func = func.last_day(_fields).alias(_alias2)
                elif _func == "year":
                    new_func = func.year(_fields).alias(_alias2)
                elif _func == "month":
                    new_func = func.month(_fields).alias(_alias2)
                elif _func == "dayofmonth":
                    new_func = func.dayofmonth(_fields).alias(_alias2)
                elif _func == "dayofyear":
                    new_func = func.dayofyear(_fields).alias(_alias2)
                elif _func == "dayofweek":
                    new_func = func.dayofweek(_fields).alias(_alias2)
                elif _func == "quarter":
                    new_func = func.quarter(_fields).alias(_alias2)
                elif _func == "hour":
                    new_func = func.hour(_fields).alias(_alias2)
                elif _func == "minute":
                    new_func = func.minute(_fields).alias(_alias2)
                elif _func == "second":
                    new_func = func.second(_fields).alias(_alias2)
                fields_agg.append(new_func)

        df = df.select(columns + [col_name for col_name in fields_agg])
        return df

    gc.collect()
    return extract_dateformat
