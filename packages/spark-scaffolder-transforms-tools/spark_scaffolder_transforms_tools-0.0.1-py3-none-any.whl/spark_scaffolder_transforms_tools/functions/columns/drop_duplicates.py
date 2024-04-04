def with_drop_duplicates(columns=None,
                         is_all_columns=False):
    """
    this transformation will delete all rows that share the same values in the subsequence set.
    Just the first row in the dataframe encountered with those values will be left,
    thereby deleting just duplicates.
    :param columns:
    :param is_all_columns:
    :return: Dataframe
    """
    import gc
    if columns is None:
        columns = []
    if is_all_columns in (False, None, ""):
        if columns in (None, "", []):
            raise Exception(f'require var: columns ([])')

    def drop_duplicates(df):
        if is_all_columns in (False, None, ""):
            _df_columns = columns
        else:
            _df_columns = df.columns
        df = df.drop_duplicates(subset=_df_columns)
        return df

    gc.collect()
    return drop_duplicates
