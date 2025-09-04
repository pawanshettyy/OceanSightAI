import streamlit as st
import plotly.express as px
from services.supabase_client import get_supabase_client

st.title("🌊 Ocean Data - Indian Marine Biodiversity Platform")

supabase = get_supabase_client()

# Fetch ocean data from Supabase
response = supabase.table("ocean_data").select("*").execute()
ocean_data = response.data if response.data else []

if ocean_data:
    st.write("### Ocean Monitoring Stations")
    df = st.DataFrame(ocean_data)
    st.dataframe(df)
    if "latitude" in df and "longitude" in df:
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="temperature",
            hover_name="location_name",
            mapbox_style="carto-positron",
            zoom=4,
            title="Indian Ocean Monitoring Stations"
        )
        st.plotly_chart(fig)
else:
    st.info("No ocean data available. Connect Supabase and add records.")
