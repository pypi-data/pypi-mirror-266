def with_union(df_unions=None):
    """
    A UNION is used to combine rows from two or more dataframes.
    :param df_unions: Array from Dataframe
    :return: Dataframe
    """
    import gc
    from typing import List
    from functools import reduce
    from pyspark.sql import DataFrame

    if df_unions is None:
        df_unions = []

    if df_unions in (None, "", []):
        raise Exception(f'require var: df_unions ([])')

    def union_multiple_df(df_list: List) -> DataFrame:
        union_with_missing_columns = lambda dfa, dfb: dfa.unionByName(dfb, allowMissingColumns=True)
        new_df = reduce(union_with_missing_columns, df_list)
        return new_df

    def union(df):
        new_list_df_union = [df] + df_unions
        new_df = union_multiple_df(new_list_df_union)
        return new_df

    gc.collect()
    return union
