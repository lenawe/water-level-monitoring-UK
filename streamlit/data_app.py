import streamlit as st
# Set-up connection
conn = st.connection("postgresql", type="sql")

# Perform query
df = conn.query('SELECT * FROM water_level_monitoring_uk.stationsmeasurements;', ttl="2s")
