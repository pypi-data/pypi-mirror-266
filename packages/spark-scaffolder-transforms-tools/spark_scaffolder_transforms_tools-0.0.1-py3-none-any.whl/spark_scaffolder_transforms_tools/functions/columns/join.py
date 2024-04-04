def with_join(join_df=None,
              columns_left=None,
              columns_right=None,
              join_type="inner"):
    """
        A JOIN is used to combine rows from two or more dataframes, based on a related column between them.
    """
    import random
    from pyspark.sql import DataFrame
    from pyspark.sql import SparkSession

    spark = SparkSession.getActiveSession()

    if len(columns_left) != len(columns_right):
        raise Exception(f'columns_left and columns_right they are different')

    if not isinstance(join_df, DataFrame):
        raise Exception(f'require var: join_df is Dataframe Not Empty")')

    join_type = str(join_type).lower()
    if join_type == "full":
        join_string = "FULL OUTER"
    elif join_type == "cross":
        join_string = "CROSS"
    elif join_type == "left":
        join_string = "LEFT OUTER"
    elif join_type == "right":
        join_string = "RIGHT OUTER"
    else:
        join_string = "INNER"

    join_df = join_df
    columns_left = columns_left
    columns_right = columns_right

    def join(df):
        val_tb1 = random.randint(100, 200)
        val_tb2 = random.randint(100, 200)
        view_tb1 = f"TB{val_tb1}"
        view_tb2 = f"TB{val_tb2}"
        join_new_df = join_df

        df.createOrReplaceTempView(view_tb1)
        join_new_df.createOrReplaceTempView(view_tb2)

        repeated_columns = [c for c in df.columns if c in list(set(join_new_df.columns).difference(set(columns_right)))]
        for col in repeated_columns:
            join_new_df = join_new_df.drop(join_new_df[col])
        sql = f"SELECT e.*, d.* FROM {view_tb1} e {join_string} JOIN {view_tb2} d ON "
        for i in range(0, len(columns_left)):
            if i > 0:
                sql += f" and "
            sql += f"e.{columns_left[i]} == d.{columns_right[i]}"
        df = spark.sql(sql)
        return df

    return join
