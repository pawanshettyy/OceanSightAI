import streamlit as st
from supabase import create_client, Client

# Load Supabase credentials from Streamlit secrets
def get_supabase_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)
