import streamlit as st
import pandas as pd
from services.supabase_client import get_supabase_client

st.title("🐟 Species Tracking - Indian Marine Biodiversity Platform")

supabase = get_supabase_client()

species_df = supabase.table("indian_species").select("*").execute().data
if species_df:
    df = pd.DataFrame(species_df)
    st.dataframe(df)
    st.map(df[['latitude', 'longitude']]) if 'latitude' in df and 'longitude' in df else None
else:
    st.info("No species data available. Connect Supabase and add records.")
