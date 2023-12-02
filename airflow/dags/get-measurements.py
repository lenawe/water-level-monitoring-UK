import requests
import time
import datetime
import pendulum
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator

"""
API for station data

Filter:
- parameter = level
- qualifier = Stage
- status = Active
- riverName = River Wye (TODO: remove for production)

Returned data:
- RLOIid
- label
- measures (for mapping to measurements)
- notation
- riverName
- stageScale
    - typicalRangeHigh
    - typicalRangeLow
- town
- lat
- long
"""
API_ENDPOINT_STATIONS = "https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=level&qualifier=Stage&status=Active&riverName=River%20Wye"
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
            extra=json.dumps(
                {   
                    "group.id": "stations-group",
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
    response = requests.get(API_ENDPOINT_STATIONS)
    ti.xcom_push(key="stations", value=response.json())

def transform_data(data):
    """
    Transforms the station data into a desired format.
    """
    data = json.loads(data.replace("\'", "\""))
    for item in data['items']:
        measure_id = '' # due to filtering, only one measure is possible
        for measure in item["measures"]:
            measure_id = measure.get("@id", None)
        yield (
            json.dumps(item),
            json.dumps(
                {
                    "RLOIid": item.get("RLOIid", None),
                    "label": item.get("label", None),
                    "measures_id": measure_id,
                    "notation": item.get("notation", None),
                    "riverName": item.get("riverName", None),
                    "stageScale": item.get("stageScale", None),
                    "town": item.get("town", None),
                    "lat": item.get("lat", None),
                    "long": item.get("long", None),
                }
            )
        )

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