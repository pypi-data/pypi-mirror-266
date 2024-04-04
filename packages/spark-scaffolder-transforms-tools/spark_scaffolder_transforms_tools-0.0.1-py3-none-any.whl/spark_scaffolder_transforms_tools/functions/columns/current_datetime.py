def with_current_timestamp(new_column=None,
                           zone="America/Lima"):
    """'
     Set current timestamp
    :param new_column: String
    :param zone: String
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if new_column in (None, "", []):
        raise Exception(f'require var: new_column ')

    def current_timestamp(df):
        _df_columns = df.columns
        df = df.select(_df_columns + [func.to_utc_timestamp(func.current_timestamp(), zone).alias(new_column)])
        return df

    gc.collect()
    return current_timestamp
