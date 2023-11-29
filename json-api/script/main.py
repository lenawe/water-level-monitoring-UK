from kafka import KafkaProducer
import time

KAFKA_SETTINGS = {
    "bootstrap_servers": ["kafka:9092"],
}

def configure_kafka_producer():
    """
    Configures and returns a KafkaProducer instance.

    Returns:
        KafkaProducer: The configured KafkaProducer instance.
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_SETTINGS["bootstrap_servers"])
    return producer

def stream_data_to_kafka():
    """
    Streams data to Kafka.
    """
    producer = configure_kafka_producer()

if __name__ == "__main__":
    stream_data_to_kafka()