def with_replace(columns=None,
                 replace_items=None):
    """
    Replace fields in the dataframe.
    :param columns: Array
    :param replace_items:  Dict
            {
               "campo1" : value1,
            }
    :return: DataFrame
    """
    import gc
    if replace_items is None:
        replace_items = dict()
    if columns is None:
        columns = []
    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    if len(replace_items.keys()) == 0:
        raise Exception(f'The replace is invalid: ("Dict Not Empty")')

    def replace(df):
        _df_columns = df.columns
        for col in columns:
            if col not in _df_columns:
                raise Exception(f'required the selected field does not exist')

        _value_list = list()
        _value_replace_list = list()
        for value, value_replace in replace_items.items():
            _value_list.append(value)
            _value_replace_list.append(value_replace)

        df = df.na.replace(_value_list, _value_replace_list, columns)
        return df

    gc.collect()
    return replace
