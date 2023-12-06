from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,FloatType,StringType
from pyspark.sql.functions import from_json, col

spark = SparkSession \
    .builder \
    .appName("Streaming pipeline to PostgreSQL") \
    .master("local[*]") \
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

def get_schema(topic):
    if topic == "stations":
      return StructType([
        StructField("rloiid", StringType()),
        StructField("label", StringType()),
        StructField("measures_id", StringType()),
        StructField("notation", StringType()),
        StructField("rivername", StringType()),
        StructField("typicalrangehigh", FloatType()),
        StructField("typicalrangelow", FloatType()),
        StructField("town", StringType()),
        StructField("lat", FloatType()),
        StructField("long", FloatType()),
      ])
    elif topic == "measurements":
      return StructType([
        StructField("id", StringType()),
        StructField("stationreference", StringType()),
        StructField("datetime", StringType()),
        StructField("value", FloatType()),
        StructField("unit", StringType()),
      ])
    else:
        return None

def get_expanded_df(topic):
  return get_input_df(topic) \
      .selectExpr("CAST(value AS STRING)") \
      .select(from_json(col("value"),get_schema(topic)).alias(topic)) \
      .select("{topic}.*".format(topic=topic))

def save_to_postgres(writeDF, epoch_id, topic):
  db_credentials = {
    "user": "postgres",
    "password": "postgres",
    "driver" : "org.postgresql.Driver"
  }  
  
  writeDF.write \
    .jdbc(
      url="jdbc:postgresql://postgresql:5432/WATER_LEVEL_MONITORING_DB",
      table="WATER_LEVEL_MONITORING_UK.{topic}".format(topic=topic),
      mode="append",
      properties=db_credentials
    )
  
  print(epoch_id, ": Saved messages from topic {topic} PostgreSQL.".format(topic=topic))

def save_to_postgres_stations(writeDF, epoch_id):
  save_to_postgres(writeDF, epoch_id, "stations")

def save_to_postgres_measurements(writeDF, epoch_id):
  save_to_postgres(writeDF, epoch_id, "measurements")

postgres_query_stations = get_expanded_df("stations").writeStream \
  .trigger(processingTime="15 seconds") \
  .foreachBatch(save_to_postgres_stations) \
  .outputMode("update") \
  .start()

postgres_query_measurements = get_expanded_df("measurements").writeStream \
  .trigger(processingTime="15 seconds") \
  .foreachBatch(save_to_postgres_measurements) \
  .outputMode("update") \
  .start()

postgres_query_stations.awaitTermination()
postgres_query_measurements.awaitTermination()