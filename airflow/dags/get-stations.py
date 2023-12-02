import requests
import time
import datetime
import pendulum
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator

API_ENDPOINT_STATIONS = "https://environment.data.gov.uk/flood-monitoring/id/stations?_limit=50"
KAFKA_SETTINGS = {
    "bootstrap_servers": ["kafka:9092"],
    "topic": "stations",
    "pause_interval": 10,
    "streaming_duration": 120
}

def load_connections():
    from airflow.models import Connection
    from airflow.utils import db

    db.merge_conn(
        Connection(
            conn_id="kafka-produce",
            conn_type="kafka",
            extra=json.dumps({"socket.timeout.ms": 10, "bootstrap.servers": KAFKA_SETTINGS["bootstrap_servers"]}),
        )
    )

def get_json_data(ti):
    """
    Retrieves json data from the specified API endpoint.
    """
    response = requests.get(API_ENDPOINT_STATIONS)
    ti.xcom_push(key="stations", value=response.json())

def transform_data(data):
    """
    Transforms the station data into a desired format.
    """
    data = json.loads(data.replace("\'", "\""))
    for item in data['items']:
        yield (
            json.dumps(item),
            json.dumps(
                {
                    "town": item.get("town", None), 
                    "riverName": item.get("riverName", None), 
                    "stationReference": item.get("stationReference", None), 
                    "status": item.get("status", None), 
                }
            )
        )

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

def produce_to_topic(ti):
    return ti.xcom_pull(key="transformed_stations", task_ids="transform_data")

with DAG(

    dag_id="get-stations",
    schedule_interval="*/15 * * * *",
    start_date=pendulum.datetime(2023, 12, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),

) as dag:
    
    get_json_data = PythonOperator(
        task_id="get_json_data",
        python_callable=get_json_data,
    )

    load_connections = PythonOperator(
        task_id="load_connections",
        python_callable=load_connections,
    )

    produce_to_topic = ProduceToTopicOperator(
        kafka_config_id="kafka-produce",
        task_id="produce_to_topic",
        topic="stations",
        producer_function=transform_data,
        producer_function_args=["{{ ti.xcom_pull(key='stations', task_ids='get_json_data')}}"]
    )

    get_json_data >> load_connections >> produce_to_topic