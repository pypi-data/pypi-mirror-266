def with_drop_columns(columns=None):
    """
    Remove fields of a dataframe.
    :param columns: Array
    :return: Dataframe
    """
    import gc
    if columns is None:
        columns = []
    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    def drop_columns(df):
        _df_columns = df.columns
        _df_excluded = list(set(_df_columns) - set(columns))
        df = df.select(_df_excluded)
        return df

    gc.collect()
    return drop_columns
