import folium
import streamlit as st
from streamlit_folium import st_folium

def show_map(df, lat_col="latitude", lon_col="longitude", popup_col=None):
    m = folium.Map(location=[15.8700, 74.1240], zoom_start=5)
    if not df.empty:
        for _, row in df.iterrows():
            popup = str(row[popup_col]) if popup_col and popup_col in row else None
            folium.Marker([row[lat_col], row[lon_col]], popup=popup).add_to(m)
    st_folium(m, width=700, height=400)
