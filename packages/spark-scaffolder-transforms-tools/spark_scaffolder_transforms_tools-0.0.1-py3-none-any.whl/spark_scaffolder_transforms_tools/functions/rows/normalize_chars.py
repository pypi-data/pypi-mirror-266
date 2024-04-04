def with_normalize_chars(columns=None):
    """
       normalize chars
       :param columns: Array
       :return: Dataframe
       """
    import gc
    from pyspark.sql import functions as func
    from pyspark.sql import types
    import unicodedata

    if columns is None:
        columns = []

    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    def get_normalize_chars(col):
        value = str(col)
        nfkd_str = unicodedata.normalize('NFKD', value)
        with_out_accents = u"".join([c for c in nfkd_str if not unicodedata.combining(c)])
        return with_out_accents

    udf_normalize_chars = func.udf(get_normalize_chars, types.StringType())

    def normalize_chars(df):
        _columns_left_list = [col for col in columns]
        _df_columns = df.columns
        for col in _columns_left_list:
            if col not in _df_columns:
                raise Exception(f'Dictionary field does not exist:("is invalid")')

        _df_excluded = list(set(_df_columns) - set(columns))

        df = df.select(_df_excluded + [udf_normalize_chars(func.col(col)).alias(col)
                                       for col in columns])
        df = df.select(*_df_columns)
        return df

    gc.collect()
    return normalize_chars
