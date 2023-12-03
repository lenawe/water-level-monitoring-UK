#!/usr/bin/env bash

until printf "" 2>>/dev/null >>/dev/tcp/cassandra/9042; do
    sleep 5;
    echo "Waiting for cassandra...";
done

echo "Creating keyspace in Cassandra."
cqlsh cassandra -u cassandra -p cassandra -e "CREATE KEYSPACE IF NOT EXISTS WATER_LEVEL_MONITORING_UK WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};"