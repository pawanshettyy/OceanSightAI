import streamlit as st
import pandas as pd
from services.supabase_client import get_supabase_client

st.title("🚨 Environmental Alerts - Indian Marine Biodiversity Platform")

supabase = get_supabase_client()

alerts_df = supabase.table("environmental_alerts").select("*").execute().data
if alerts_df:
    df = pd.DataFrame(alerts_df)
    st.dataframe(df)
else:
    st.info("No alerts data available. Connect Supabase and add records.")
