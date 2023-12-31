import requests
from datetime import datetime as dt
import datetime
import pendulum
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator

"""
API for measurements data

Filter:
- parameter = level
- qualifier = Stage

Returned data:
- @id (for mapping to stations)
- stationReference
- latestReading
    - dateTime
    - value
- unit
"""
API_ENDPOINT_MEASUREMENTS = """https://environment.data.gov.uk/flood-monitoring/id/measures?parameter=level&qualifier=Stage"""
KAFKA_SETTINGS = {
    "bootstrap_servers": ["kafka:9092"],
    "topic": "measurements",
    "pause_interval": 10,
    "streaming_duration": 120
}

def load_connections():
    from airflow.models import Connection
    from airflow.utils import db

    db.merge_conn(
        Connection(
            conn_id="kafka-produce-measurements",
            conn_type="kafka",
            extra=json.dumps(
                {   
                    "group.id": "measurements-group",
                    "bootstrap.servers": "kafka:9092",
                    "security.protocol": "PLAINTEXT",
                    "auto.offset.reset": "beginning"
                }
            ),
        )
    )

def get_json_data(ti):
    """
    Retrieves json data from the specified API endpoint.
    """
    response = requests.get(API_ENDPOINT_MEASUREMENTS)
    ti.xcom_push(key="measurements", value=json.dumps(response.json()))

def transform_data(data):
    """
    Transforms the measurements data into a desired format.
    """
    data = json.loads(data)
    for item in data["items"]:
        latestReading = item.get("latestReading", None)
        if latestReading is not None:
            yield (
                json.dumps(item),
                json.dumps(
                    {
                        "id": item.get("@id", None),
                        "stationreference": item.get("stationReference", None),
                        "datetime": latestReading.get("dateTime", None),
                        "value": latestReading.get("value", None),
                        "unit": item.get("unit", None),
                        "last_update": dt.now()
                    },
                    default=str
                )
            )

def produce_to_topic(ti):
    return ti.xcom_pull(key="transformed_measurements", task_ids="transform_data")

with DAG(

    dag_id="get-measurements",
    schedule_interval="*/15 * * * *", # At every 15th minute.
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
        kafka_config_id="kafka-produce-measurements",
        task_id="produce_to_topic",
        topic="measurements",
        producer_function=transform_data,
        producer_function_args=["{{ ti.xcom_pull(key='measurements', task_ids='get_json_data')}}"]
    )

    get_json_data >> load_connections >> produce_to_topic