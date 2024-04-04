def with_dateformat(columns=None,
                    format="yyyy-MM-dd"):
    """
     Set current date
    :param columns: Array
    :param format: String
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if columns in (None, "", []):
        raise Exception(f'require var: columns ')

    def date_format(df):
        _df_columns = df.columns
        df = df.select(_df_columns + [func.date_format(col_name, format).alias(col_name) for col_name in columns])
        return df

    gc.collect()
    return date_format
