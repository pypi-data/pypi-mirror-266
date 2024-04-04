def with_autocast(columns=None,
                  to_type=None,
                  format_date=None,
                  format_timestamp=None,
                  exceptions=None):
    """
    Cast the datatype for all fields with a specific datatype in the output schema to other datatype
    :param columns: Array
    :param to_type: String
    :param format_date: String (yyyy-MM-dd)
    :param format_timestamp: String (yyyy-MM-dd HH:mm:ss.SSSS)
    :param exceptions: Array
    :return: Dataframe
    """
    import gc
    from pyspark.sql import functions as func
    from pyspark.sql import types
    if exceptions is None:
        exceptions = []
    if columns is None:
        columns = []

    to_type_numeric = ("int32", "int64", "float", "string", "time", "decimal")
    to_type_date = ("date",)
    to_type_timestamp = ("timestamp",)

    if not to_type or to_type not in to_type_numeric + to_type_date + to_type_timestamp:
        raise Exception(f'require var: toType ({to_type_numeric} {to_type_date} {to_type_timestamp} )')

    to_type = str(to_type).lower()

    if to_type == "int32":
        _type = types.IntegerType()
    elif to_type == "int64":
        _type = types.LongType()
    elif to_type == "float":
        _type = types.DoubleType()
    elif to_type == "string":
        _type = types.StringType()
    elif to_type == "decimal":
        _type = types.DecimalType()
    elif to_type == "time":
        _type = types.StringType()
    elif to_type == "timestamp":
        _type = types.TimestampType()
        if not format_timestamp:
            raise Exception(f'require var: format_timestamp ("yyyy-MM-dd HH:mm:ss.SSSS")')
    elif to_type == "date":
        _type = types.DateType()
        if not format_date:
            raise Exception(f'require var: format_date ("yyyy-MM-dd")')

    def autocast(df):
        _df_columns = df.columns
        _df_excluded = list(set(_df_columns) - set(columns))

        _df_selected = df
        if to_type in to_type_numeric:
            _df_selected = df.select(
                _df_excluded + [func.col(col_name).cast(_type)
                                for col_name in columns if col_name not in exceptions])
        elif to_type in to_type_date:
            _df_selected = df.select(
                _df_excluded + [func.date_format(func.col(col_name), format_date).cast(_type).alias(col_name)
                                for col_name in columns if col_name not in exceptions])
        elif to_type in to_type_timestamp:
            _df_selected = df.select(
                _df_excluded + [func.to_timestamp(func.col(col_name), format_timestamp).alias(col_name)
                                for col_name in columns if col_name not in exceptions])
        return _df_selected.select(_df_columns)

    gc.collect()
    return autocast
