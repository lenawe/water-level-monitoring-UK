#/bin/bash

cd /home/scripts

spark-submit --packages org.apache.kafka:kafka-clients:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-streaming-kafka-0-10-assembly_2.12:3.3.0,org.apache.commons:commons-pool2:2.11.1,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,com.twitter:jsr166e:1.1.0,com.datastax.spark:spark-cassandra-connector-assembly_2.12:3.3.0,org.postgresql:postgresql:42.7.0 \
stations-cassandra.py
