def with_conditional(expressions=None):
    """
    The transformation conditional provides a manner to output column values row-wisely
    if some condition is acomplished. The condition must be related to some column.
    This transformation uses the own schema dataframe
    :param expressions: Array
        [
            {
             "condition":
                [
                 {
                     "when":"test_1=550",
                     "then": "si",
                     "apply_column":False
                 }
                ],
              "otherwise": "test_2",
              "apply_column":False,
              "as":"test_alias"
            }
       ]
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if expressions is None:
        expressions = []

    key_cond = ['condition', 'otherwise', 'apply_column', 'as']
    if len(expressions) == 0:
        raise Exception(f'require var: expressions ("expressions Not Empty")')

    for exp in expressions[0].keys():
        if exp not in key_cond:
            raise Exception(f'Dictionary field does not exist:("is invalid")')

    def conditional(df):
        _df_columns = df.columns
        columns = [_["as"] for _ in expressions]
        exist_columns = [col for col in _df_columns if col in columns]
        _df_excluded = list(set(_df_columns) - set(columns))

        sql_cond = ""
        for exp in expressions:
            _case_condition = exp["condition"]
            _otherwise = exp["otherwise"]
            _as = exp["as"]
            _apply_columns = exp["apply_column"]
            if not _apply_columns:
                _otherwise = f"'{_otherwise}'"

            for cond in _case_condition:
                _case_when = cond["when"]
                _case_then = cond["then"]
                _case_apply_column = cond["apply_column"]
                if not _case_apply_column:
                    _case_then = f"'{_case_then}'"
                sql_cond += f"WHEN {_case_when} THEN {_case_then} "

            sql_cond = f"CASE {sql_cond} ELSE {_otherwise} END AS {_as}"

        df = df.select(*_df_excluded, func.expr(f"{sql_cond}"))
        if len(exist_columns) > 0:
            df = df.select(*_df_columns)
        return df

    gc.collect()
    return conditional
