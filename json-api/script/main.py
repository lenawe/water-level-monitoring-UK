from kafka import KafkaProducer
import time

KAFKA_SETTINGS = {
    "bootstrap_servers": ["kafka:9092"],
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

def get_json_data(api_endpoint: str) -> str:
    """
    Retrieves json data from the specified API endpoint.

    Args:
        api_endpoint (str): The URL of the API endpoint.

    Returns:
        dict: The JSON response containing the retrieved data.
    """
    response = requests.get(api_endpoint)
    return response.json()

def stream_data_to_kafka():
    """
    Streams data to Kafka.
    """
    producer = configure_kafka_producer()
    for _ in range (KAFKA_SETTINGS["streaming_duration"] // KAFKA_SETTINGS["pause_interval"]):
        station_data = get_json_data(API_ENDPOINT_STATIONS)

if __name__ == "__main__":
    stream_data_to_kafka()