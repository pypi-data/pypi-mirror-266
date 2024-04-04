def with_init_nulls(columns=None,
                    default="0000",
                    all_columns=False):
    """
    Initialize records with NULL value with the specified one.
    :param columns: Array
    :param default: String
    :param all_columns: Boolean
    :return: Dataframe
    """
    import gc
    if columns is None:
        columns = []
    if all_columns in (False, None, ""):
        if columns in (None, "", []):
            raise Exception(f'require var: columns ([])')

    if default in (None, "", []):
        raise Exception(f'require var: default')

    def init_nulls(df):
        if all_columns in (False, None, ""):
            _df_columns = columns
        else:
            _df_columns = df.columns

        df = df.na.fill({col: default for col in _df_columns})
        return df

    gc.collect()
    return init_nulls
