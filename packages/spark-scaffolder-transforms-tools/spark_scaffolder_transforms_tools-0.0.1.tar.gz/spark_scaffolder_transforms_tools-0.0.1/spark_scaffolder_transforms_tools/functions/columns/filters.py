def with_sql_filters(sql_filter=""):
    """
    Applies a SQL filter to the dataframe.
    :param sql_filter: String
    :return: Dataframe
    """
    import gc
    if sql_filter in (None, ""):
        raise Exception(f'require var: sql_filter ("sql Not Empty")')
    sql_filter = str(sql_filter).replace('"', "'")

    def sql_filters(df):
        df = df.filter(f"{sql_filter}")
        return df

    gc.collect()
    return sql_filters
