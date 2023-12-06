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

def get_input_df(topic):
  return spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .load()
