def get_df_size(spark=None, df=None):
    from pyspark.serializers import AutoBatchedSerializer, PickleSerializer
    sc = spark.sparkContext

    def _to_java_object_rdd(rdd):
        rdd = rdd._reserialize(AutoBatchedSerializer(PickleSerializer()))
        return rdd.ctx._jvm.org.apache.spark.mllib.api.python.SerDe.pythonToJava(rdd._jrdd, True)

    java_obj = _to_java_object_rdd(df.rdd)
    n_bytes = sc._jvm.org.apache.spark.util.SizeEstimator.estimate(java_obj) / 1024 ** 2
    print(f'Memory current optimization is: {n_bytes:.2f} MB')


def get_df_partitions(df):
    return df.rdd.getNumPartitions()


def get_df_partitioner(df):
    return df.rdd.get_df_partitioner


def get_df_repartition(df=None, n=None, col_name=None):
    if col_name:
        return df.get_df_repartition(n, col_name)
    else:
        return df.get_df_repartition(n)


def get_df_h_repartition(spark=None, df=None, partitions_number=None, col_name=None):
    if partitions_number is None:
        partitions_number = spark.instance.parallelism * 4

    if col_name is None:
        df = get_df_repartition(df=df, n=partitions_number)
    else:
        df = get_df_repartition(df=df, n=partitions_number, col_name=col_name)
    return df


def get_df_debug(df):
    print(df.rdd.toDebugString().decode("ascii"))


def get_df_create_key(df=None):
    from pyspark.sql import functions as func
    df_columns = df.columns
    df_new = df.select([func.monotonically_increasing_id().alias("KEY")] + df_columns)
    return df_new


def get_df_flatten_list(_2d_list):
    flat_list = list()
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def get_df_cache(df):
    if not df.is_cached:
        df.cache()
    return df


def get_df_uncache(df):
    if df.is_cached:
        df.unpersist()
    return df


def get_or_create_session_spark():
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession() or None
    if spark is None:
        spark = SparkSession.builder \
            .master("local[*]") \
            .appName("DATIO_APP") \
            .enableHiveSupport() \
            .getOrCreate()
    return spark


def config_spark(spark=None):
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    spark.conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "false")
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    spark.conf.set("spark.sql.maxPlanStringLength", 603)
    spark.conf.set('spark.sql.session.timeZone', 'America/Lima')
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
    spark.conf.set("hive.exec.dynamic.partition", "nonstrict")
    spark.conf.set("spark.sql.crossJoin.enabled", "true")
    return spark
