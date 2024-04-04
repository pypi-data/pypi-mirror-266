def with_rename_columns(columns=None):
    """
    Rename fields in the dataframe.
    :param columns: Array
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func
    if columns is None:
        columns = dict()

    if len(columns.keys()) == 0:
        raise Exception(f'The columnsToRename is invalid: ("Dict Not Empty")')

    def rename_columns(df):
        _columns_rename_list = [col for col, rename_col in columns.items()]
        _df_columns = df.columns
        for col in columns:
            if col not in _df_columns:
                raise Exception(f'Dictionary field does not exist:("is invalid")')

        columns_rename_order_list = list()
        for col in _df_columns:
            col_rename = columns.get(col, None)
            if col_rename is None:
                columns_rename_order_list.append((col, col))
            else:
                columns_rename_order_list.append((col, col_rename))

        df = df.select(*[func.col(col[0]).alias(col[1]) for col in columns_rename_order_list])
        return df

    gc.collect()
    return rename_columns
