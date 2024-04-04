def with_clean_nulls(columns=None,
                     min_non_nulls=1,
                     is_all_columns=False):
    """
    Remove rows when some field (or all fields) in the fields attribute has value null.
    If the fields attribute is not specified, the transformation removes all rows
    that have a null value in one or more fields.
    :param columns: Array
    :param min_non_nulls: int default=1
    :param is_all_columns: boolean
    :return: Dataframe
    """
    import gc

    if columns is None:
        columns = []
    if is_all_columns in (False, None, ""):
        if columns in (None, "", []):
            raise Exception(f'require var: columns ([])')

    def clean_nulls(df):
        if is_all_columns in (False, None, ""):
            _df_columns = columns
        else:
            _df_columns = df.columns
        df_selected = df.na.drop(how='any', thresh=min_non_nulls, subset=_df_columns)
        return df_selected

    gc.collect()
    return clean_nulls
