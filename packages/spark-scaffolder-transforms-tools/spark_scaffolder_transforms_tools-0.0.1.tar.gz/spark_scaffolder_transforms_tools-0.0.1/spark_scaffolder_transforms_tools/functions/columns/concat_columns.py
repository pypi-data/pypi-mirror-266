def with_concat_columns(columns=None,
                        new_column=None,
                        separator=" ",
                        convert_nulls=""):
    """
    Concatenates two or more columns into a new one.
    :param columns: Array
    :param new_column: String
    :param separator: String
    :param convert_nulls: String
    :return: DataFrame
    """
    import gc
    from pyspark.sql import functions as func
    if columns is None:
        columns = []

    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')
    if new_column in (None, ""):
        raise Exception(f'require var: columnName ("")')

    def concat_columns(df):
        _df_columns = df.columns
        df = df.fillna(convert_nulls, subset=columns)
        df = df.select(_df_columns + [func.concat_ws(separator, *columns).alias(new_column)])
        return df

    gc.collect()
    return concat_columns
