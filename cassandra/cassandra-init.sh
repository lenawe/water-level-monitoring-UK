#!/usr/bin/env bash

until printf "" 2>>/dev/null >>/dev/tcp/cassandra/9042; do
    sleep 5;
    echo "Waiting for cassandra...";
done

echo "Creating keyspace in Cassandra."
cqlsh cassandra -u cassandra -p cassandra -e "CREATE KEYSPACE IF NOT EXISTS WATER_LEVEL_MONITORING_UK WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};"

echo "Creating tables in Cassandra."
cqlsh cassandra -u cassandra -p cassandra -e "CREATE TABLE IF NOT EXISTS water_level_monitoring_uk.stations(uuid uuid primary key, rloiid text, label text, measures_id text, notation text, rivername text, typicalrangehigh float, typicalrangelow float, town text, lat float, long float);"
cqlsh cassandra -u cassandra -p cassandra -e "CREATE TABLE IF NOT EXISTS water_level_monitoring_uk.measures(uuid uuid primary key, id text, stationreference text, datetime text, value float, unit text);"