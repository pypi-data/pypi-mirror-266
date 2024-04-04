def with_dateformat_oper(columns=None,
                         oper_columns=None):
    """
    This transformations that are performed for date operations
    :param columns: Array
    :param oper_columns: Array
        [
           {
              "function": "datediff",
              "as": "datediff"
           }
        ]
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if oper_columns is None:
        oper_columns = []
    if columns is None:
        columns = []

    to_type_func_agg = ["datediff", "monthdiff", "weekdiff", "quarterdiff", "yeardiff"]

    for agg in oper_columns:
        _func = agg.get("function", None)

        if _func is None:
            raise Exception(f'The function in oper_columns is invalid: ("Is required function")')
        if _func not in to_type_func_agg:
            raise Exception(f'The function in oper_columns is invalid: (functions_agg)')

        _as = agg.get("as", None)
        if _as is None:
            raise Exception(f'The as in extract_columns is invalid: ("Not Empty")')

    def oper_dateformat(df):
        _df_columns = df.columns
        new_func = list()
        fields_agg = list()
        date_one = columns[0]
        date_two = columns[1]

        for _ in oper_columns:
            _func = _["function"]
            _alias = _["as"]
            date_one1 = str(date_one).replace("_", "").replace("-", "")
            date_two1 = str(date_two).replace("_", "").replace("-", "")
            _alias2 = f"{_alias}_{date_one1}_{date_two1}"

            if _func == "datediff":
                new_func = func.round(func.datediff(func.col(f"{date_one}"), func.col(f"{date_two}")), 0).alias(_alias2)
            elif _func == "monthdiff":
                new_func = func.round(func.months_between(func.col(f"{date_one}"), func.col(f"{date_two}")), 0).alias(_alias2)
            elif _func == "weekdiff":
                new_func = func.round((func.datediff(func.col(f"{date_one}"), func.col(f"{date_two}")) / func.lit(52)), 0).alias(_alias2)
            elif _func == "quarterdiff":
                new_func = func.round((func.months_between(func.col(f"{date_one}"), func.col(f"{date_two}")) / func.lit(4)), 0).alias(_alias2)
            elif _func == "yeardiff":
                new_func = func.round((func.months_between(func.col(f"{date_one}"), func.col(f"{date_two}")) / func.lit(12)), 0).alias(_alias2)
            fields_agg.append(new_func)
        df = df.select(columns + [col_name for col_name in fields_agg])
        return df

    gc.collect()
    return oper_dateformat
