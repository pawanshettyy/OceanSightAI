import streamlit as st
import pandas as pd
from services.supabase_client import get_supabase_client

st.title("📊 Biodiversity Analytics - Indian Marine Biodiversity Platform")

supabase = get_supabase_client()

biodiversity_df = supabase.table("biodiversity_indices").select("*").execute().data
if biodiversity_df:
    df = pd.DataFrame(biodiversity_df)
    st.dataframe(df)
else:
    st.info("No biodiversity data available. Connect Supabase and add records.")
