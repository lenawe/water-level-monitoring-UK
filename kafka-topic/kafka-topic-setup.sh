/opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists --topic $TOPIC_NAME --replication-factor 1 --partitions 1 --bootstrap-server $BOOTSTRAP_SERVER

echo "topic $TOPIC_NAME was created"