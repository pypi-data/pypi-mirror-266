def with_remove_special_chars(columns=None):
    """
     remove special chars
    :param columns: Array
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func
    from pyspark.sql import types
    import string

    if columns is None:
        columns = []

    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    def get_remove_special_chars(col):
        s = str(col)
        with_out_special = s.translate(str.maketrans("", "", string.punctuation))
        return with_out_special

    udf_remove_special_chars = func.udf(get_remove_special_chars, types.StringType())

    def remove_special_chars(df):
        _columns_left_list = [col for col in columns]
        _df_columns = df.columns
        for col in _columns_left_list:
            if col not in _df_columns:
                raise Exception(f'Dictionary field does not exist:("is invalid")')

        _df_excluded = list(set(_df_columns) - set(columns))

        df = df.select(_df_excluded + [udf_remove_special_chars(func.col(col)).alias(col)
                                       for col in columns])
        df = df.select(*_df_columns)
        return df

    gc.collect()
    return remove_special_chars
