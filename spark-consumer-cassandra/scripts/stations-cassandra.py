from pyspark.sql import SparkSession
spark = SparkSession \
    .builder \
    .appName("Streaming pipeline to cassandra") \
    .master("local[*]") \
    .config("spark.cassandra.connection.host","cassandra") \
    .config("spark.cassandra.connection.port","9042") \
    .config("spark.cassandra.auth.username","cassandra") \
    .config("spark.cassandra.auth.password","cassandra") \
    .config("spark.driver.host", "localhost")\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
