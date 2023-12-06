import streamlit as st
import pandas as pd
# Set-up connection
conn = st.connection("postgresql", type="sql")

# Perform query
df = conn.query('SELECT * FROM water_level_monitoring_uk.stationsmeasurements;', ttl="2s")

# Adjust date format
df['last_update'] = pd.to_datetime(df['last_update'])
df['last_update'] = df['last_update'].dt.tz_convert('Europe/Vienna')
df['last_update'] = df['last_update'].dt.strftime('%Y-%m-%d %H:%M')

# Adjust unit
df['unit'] = df['unit'].replace('http://qudt.org/1.1/vocab/unit#Meter', 'm')

# Round numerical values
df['typical_range_high'] = df['typical_range_high'].round(2)
df['typical_range_low'] = df['typical_range_low'].round(2)
