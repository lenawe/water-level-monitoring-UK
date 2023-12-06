CREATE SCHEMA IF NOT EXISTS WATER_LEVEL_MONITORING_UK;

CREATE TABLE IF NOT EXISTS WATER_LEVEL_MONITORING_UK.STATIONS (
    "RLOIID" VARCHAR(255) PRIMARY KEY,
    "LABEL" VARCHAR(255),
    "MEASURES_ID" VARCHAR(255),
    "NOTATION" VARCHAR(255),
    "RIVERNAME" VARCHAR(255),
    "TYPICALRANGEHIGH" FLOAT,
    "TYPICALRANGELOW" FLOAT,
    "TOWN" VARCHAR(255),
    "LAT" FLOAT,
    "LONG" FLOAT
);

CREATE TABLE IF NOT EXISTS WATER_LEVEL_MONITORING_UK.MEASUREMENTS (
    "ID" VARCHAR(255),
    "STATIONREFERENCE" VARCHAR(255) PRIMARY KEY,
    "DATETIME" TIMESTAMP,
    "VALUE" FLOAT,
    "UNIT" VARCHAR(255)
);

CREATE OR REPLACE VIEW water_level_monitoring_uk.stationsmeasurements
 AS
 SELECT s."RLOIID" AS station_id,
    s."NOTATION" AS station_notation,
    s."LABEL" AS station_name,
    s."RIVERNAME" AS river_name,
    s."TOWN" AS town,
    s."LAT" AS latitude,
    s."LONG" AS longitude,
    m."DATETIME" AS last_update,
    m."VALUE",
    m."UNIT",
    s."TYPICALRANGELOW" AS typical_range_low,
    s."TYPICALRANGEHIGH" AS typical_range_high
   FROM water_level_monitoring_uk.stations s
     JOIN water_level_monitoring_uk.MEASUREMENTS m ON s."MEASURES_ID" = m."ID";