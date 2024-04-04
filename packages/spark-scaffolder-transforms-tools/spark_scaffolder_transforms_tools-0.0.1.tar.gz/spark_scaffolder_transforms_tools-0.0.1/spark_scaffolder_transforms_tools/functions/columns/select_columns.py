def with_select_columns(columns=None):
    """
    Select fields of the dataframe
    :param columns: Array
    :return:
    """
    import gc
    from pyspark.sql import functions as func
    if columns is None:
        columns = []

    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    def select_columns(df):
        _df_columns = df.columns
        for col in columns:
            if col not in _df_columns:
                raise Exception(f'required the selected field does not exist')

        df = df.select(*[func.col(col) for col in columns])
        return df

    gc.collect()
    return select_columns
