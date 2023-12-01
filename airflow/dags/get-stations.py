import requests
from kafka import KafkaProducer
import time
import datetime
import pendulum
import json

from airflow import DAG
from airflow.operators.python import PythonOperator

API_ENDPOINT_STATIONS = "https://environment.data.gov.uk/flood-monitoring/id/stations?_limit=50"
KAFKA_SETTINGS = {
    "bootstrap_servers": ["kafka:9092"],
    "topic": "stations",
    "pause_interval": 10,
    "streaming_duration": 120
}

def configure_kafka_producer():
    """
    Configures and returns a KafkaProducer instance.

    Returns:
        KafkaProducer: The configured KafkaProducer instance.
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_SETTINGS["bootstrap_servers"])
    return producer

def get_json_data(ti):
    """
    Retrieves json data from the specified API endpoint.
    """
    response = requests.get(API_ENDPOINT_STATIONS)
    ti.xcom_push(key="stations", value=response.json())

def transform_station_data(data):
    """
    Transforms the station data into a desired format.

    Args:
        data (dict): The JSON response containing the station data.

    Returns:
        list: The transformed station data in a list of dictionaries.
    """
    transformed_data = []
    for item in data['items']:
        transformed_item = {
            "town": item.get("town", None), 
            "riverName": item.get("riverName", None), 
            "stationReference": item.get("stationReference", None), 
            "status": item.get("status", None), 
        }
        transformed_data.append(transformed_item)
    return transformed_data

def publish_to_kafka(producer, data):
    """
    Publishes the transformed data to Kafka.

    Args:
        producer (KafkaProducer): The KafkaProducer instance.
        data (list): The transformed station data.
    """
    data = json.dumps(data).encode('utf-8')
    producer.send(KAFKA_SETTINGS["topic"], value=data)
    producer.flush()

def stream_data_to_kafka():
    """
    Streams data to Kafka.
    """
    producer = configure_kafka_producer()
    for _ in range (KAFKA_SETTINGS["streaming_duration"] // KAFKA_SETTINGS["pause_interval"]):
        station_data = get_json_data(API_ENDPOINT_STATIONS)
        station_data_transformed = transform_station_data(station_data)
        publish_to_kafka(producer, station_data_transformed)
        time.sleep(KAFKA_SETTINGS["pause_interval"])

if __name__ == "__main__":
    stream_data_to_kafka()

with DAG(

    dag_id="get-stations",
    schedule_interval="*/15 * * * *",
    start_date=pendulum.datetime(2023, 12, 01, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    
) as dag:
    
    get_json_data = PythonOperator(
        task_id="get_json_data",
        python_callable=get_json_data,
    )

    get_json_data