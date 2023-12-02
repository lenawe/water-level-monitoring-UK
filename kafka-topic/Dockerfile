FROM bitnami/kafka:latest

COPY ./kafka/kafka-setup.sh /kafka-setup.sh

ENV TOPIC_NAME=Order

ENV BOOTSTRAP_SERVER=172.18.0.4:9092

CMD ["/bin/bash", "-c", "/kafka-setup.sh"]