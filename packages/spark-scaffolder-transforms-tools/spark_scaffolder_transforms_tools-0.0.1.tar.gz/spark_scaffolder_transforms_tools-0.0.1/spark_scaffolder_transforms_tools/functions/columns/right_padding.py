def with_right_padding(columns=None,
                       length_dest="",
                       fill_character=""):
    """
       Cast a number to alphanumeric and prepend the fillCharacter until the length desired.
       This is useful to standardize columns between different tables
       :param columns: Array
       :param length_dest: String
       :param fill_character: String
       :return: Dataframe
       """
    import gc
    from pyspark.sql import functions as func
    from pyspark.sql import types

    if columns is None:
        columns = []

    if columns in (None, "", []):
        raise Exception(f'require var: columns ([])')

    if length_dest in (None, ""):
        raise Exception(f'require var: lengthDest ("")')

    if fill_character in (None, ""):
        raise Exception(f'require var: fillCharacter ("")')

    def get_right_text(col, length, character):
        col = str(col).rjust(int(length), character)
        return col

    udf_right_text = func.udf(get_right_text, types.StringType())

    def right_padding(df):
        _columns_left_list = [col for col in columns]
        _df_columns = df.columns
        for col in _columns_left_list:
            if col not in _df_columns:
                raise Exception(f'Dictionary field does not exist:("is invalid")')

        _df_excluded = list(set(_df_columns) - set(columns))
        df = df.select(_df_excluded + [udf_right_text(func.col(col),
                                                      func.lit(length_dest),
                                                      func.lit(fill_character)).alias(col)
                                       for col in columns])
        df = df.select(*_df_columns)
        return df

    gc.collect()
    return right_padding
