import streamlit as st
import plotly.express as px

def show_bar_chart(df, x, y, title):
    fig = px.bar(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)
