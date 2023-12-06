from pyspark.sql import SparkSession
spark = SparkSession \
    .builder \
    .appName("Streaming pipeline to PostgreSQL") \
    .master("local[*]") \
    .config("spark.driver.host", "localhost")\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
