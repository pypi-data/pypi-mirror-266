def with_current_date(new_column=None):
    """
     Set current date
    :param new_column: String
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func

    if new_column in (None, "", []):
        raise Exception(f'require var: new_column ')

    def current_date(df):
        _df_columns = df.columns
        df = df.select(_df_columns + [func.current_date().alias(new_column)])
        return df

    gc.collect()
    return current_date
