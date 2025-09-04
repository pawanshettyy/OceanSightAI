import streamlit as st

def show_alert(title, severity, description):
    color = {"Critical": "red", "High": "orange", "Medium": "yellow", "Low": "green"}.get(severity, "blue")
    st.markdown(f"<div style='background:{color};padding:1rem;border-radius:10px'><h4>{title}</h4><p>{description}</p></div>", unsafe_allow_html=True)
