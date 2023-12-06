import streamlit as st
import numpy as np
import pandas as pd
# Set-up connection
conn = st.connection("postgresql", type="sql")

# Perform query
df = conn.query('SELECT * FROM water_level_monitoring_uk.stationsmeasurements;', ttl="2s")

# Adjust date format
df['last_update'] = pd.to_datetime(df['last_update']).dt.tz_localize('UTC')
df['last_update'] = df['last_update'].dt.tz_convert('Europe/Vienna')
df['last_update'] = df['last_update'].dt.strftime('%Y-%m-%d %H:%M')

# Adjust unit
df['unit'] = df['unit'].replace('http://qudt.org/1.1/vocab/unit#Meter', 'm')

# Round numerical values
df['typical_range_high'] = df['typical_range_high'].round(2)
df['typical_range_low'] = df['typical_range_low'].round(2)

# Define colors in case of out-of-range values
df['color'] = np.where(
    (df['value'] >= df['typical_range_low']) & (df['value'] <= df['typical_range_high']), "#05a300",
        np.where(df['value'] < df['typical_range_low'], '#0033ff', '#ff0000'))

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

df['color'] = df['color'].apply(hex_to_rgb)
