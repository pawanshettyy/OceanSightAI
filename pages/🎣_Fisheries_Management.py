import streamlit as st
import pandas as pd
from services.supabase_client import get_supabase_client

st.title("🎣 Fisheries Management - Indian Marine Biodiversity Platform")

supabase = get_supabase_client()

fisheries_df = supabase.table("fisheries_data").select("*").execute().data
if fisheries_df:
    df = pd.DataFrame(fisheries_df)
    st.dataframe(df)
else:
    st.info("No fisheries data available. Connect Supabase and add records.")
