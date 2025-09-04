# streamlit_app.py - Main Marine Biodiversity Platform
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import requests
from PIL import Image
import tensorflow as tf
from typing import Dict, List, Tuple
import base64
import io

# Configure page
st.set_page_config(
    page_title="🌊 Marine Biodiversity India",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# Custom CSS for Indian theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #000080;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #138808;
        margin: 1rem 0;
    }
    .alert-card {
        background: #fff5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 1rem 0;
    }
    .species-card {
        background: #f0fff4;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #90EE90;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=300)
def load_ocean_data():
    """Load recent ocean monitoring data"""
    try:
        response = supabase.table("ocean_data").select("*").order("recorded_at", desc=True).limit(1000).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading ocean data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_species_data():
    """Load Indian marine species data"""
    try:
        response = supabase.table("indian_species").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading species data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_fisheries_data():
    """Load fisheries data"""
    try:
        response = supabase.table("fisheries_data").select("*").order("recorded_date", desc=True).limit(500).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading fisheries data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_alerts():
    """Load environmental alerts"""
    try:
        response = supabase.table("environmental_alerts").select("*").eq("status", "Active").order("created_at", desc=True).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading alerts: {e}")
        return pd.DataFrame()

def create_india_map(data_df=None, data_type="ocean"):
    """Create interactive map of India's coastal areas"""
    # Center on India
    m = folium.Map(location=[15.8700, 74.1240], zoom_start=5)
    
    # Add Indian coastal boundaries
    india_coords = [
        [8.4, 77.0], [11.9, 79.8], [13.1, 80.3], [15.9, 82.2], [20.3, 85.8],
        [22.5, 88.4], [22.0, 70.2], [19.1, 72.9], [15.3, 74.1], [11.1, 75.4], [8.4, 77.0]
    ]
    
    if data_df is not None and not data_df.empty:
        if data_type == "ocean" and 'latitude' in data_df.columns:
            for idx, row in data_df.iterrows():
                color = 'blue'
                if 'temperature' in row and pd.notna(row['temperature']):
                    if row['temperature'] > 30:
                        color = 'red'
                    elif row['temperature'] > 28:
                        color = 'orange'
                
                folium.CircleMarker(
                    [row['latitude'], row['longitude']],
                    radius=8,
                    popup=f"""
                    <b>{row.get('location_name', 'Unknown')}</b><br>
                    State: {row.get('state', 'N/A')}<br>
                    Temperature: {row.get('temperature', 'N/A')}°C<br>
                    Salinity: {row.get('salinity', 'N/A')} PSU<br>
                    pH: {row.get('ph_level', 'N/A')}
                    """,
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
    
    # Add major Indian ports
    ports = [
        {"name": "Mumbai Port", "coords": [18.9220, 72.8347], "state": "Maharashtra"},
        {"name": "Chennai Port", "coords": [13.0827, 80.2707], "state": "Tamil Nadu"},
        {"name": "Kochi Port", "coords": [9.9312, 76.2673], "state": "Kerala"},
        {"name": "Visakhapatnam Port", "coords": [17.6868, 83.2185], "state": "Andhra Pradesh"},
        {"name": "Kolkata Port", "coords": [22.5726, 88.3639], "state": "West Bengal"}
    ]
    
    for port in ports:
        folium.Marker(
            port["coords"],
            popup=f"<b>{port['name']}</b><br>{port['state']}",
            icon=folium.Icon(color='green', icon='anchor', prefix='fa')
        ).add_to(m)
    
    return m

def display_main_dashboard():
    """Main dashboard with overview metrics"""
    
    st.markdown('<div class="main-header"><h1>🌊 Marine Biodiversity Platform - India</h1><p>Monitoring 7,516 km of Indian Coastline</p></div>', unsafe_allow_html=True)
    
    # Load data
    ocean_df = load_ocean_data()
    species_df = load_species_data()
    fisheries_df = load_fisheries_data()
    alerts_df = load_alerts()
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌊 Monitoring Stations", len(ocean_df) if not ocean_df.empty else 0)
    with col2:
        st.metric("🐟 Catalogued Species", len(species_df) if not species_df.empty else 0)
    with col3:
        endangered_count = len(species_df[species_df['conservation_status'].isin(['Endangered', 'Critically Endangered'])]) if not species_df.empty else 0
        st.metric("⚠️ Endangered Species", endangered_count)
    with col4:
        st.metric("🎣 Fishing Reports", len(fisheries_df) if not fisheries_df.empty else 0)
    with col5:
        st.metric("🚨 Active Alerts", len(alerts_df) if not alerts_df.empty else 0)
    
    # Map and recent alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Real-time Ocean Monitoring")
        if not ocean_df.empty:
            map_obj = create_india_map(ocean_df, "ocean")
            st_folium(map_obj, width=700, height=400)
        else:
            st.info("Loading ocean monitoring data...")
    
    with col2:
        st.subheader("🚨 Recent Alerts")
        if not alerts_df.empty:
            for idx, alert in alerts_df.head(3).iterrows():
                severity_color = {"Critical": "🔴", "High": "🟡", "Medium": "🟠", "Low": "🟢"}
                st.markdown(f"""
                <div class="alert-card">
                <h4>{severity_color.get(alert['severity'], '🔵')} {alert['title']}</h4>
                <p><strong>Severity:</strong> {alert['severity']}</p>
                <p><strong>States:</strong> {', '.join(alert['affected_states']) if alert['affected_states'] else 'Multiple'}</p>
                <p><strong>Issued by:</strong> {alert['issued_by']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active alerts")
    
    # Charts section
    st.subheader("📊 Ocean Health Trends")
    
    if not ocean_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature trends by state
            temp_by_state = ocean_df.groupby('state')['temperature'].mean().sort_values(ascending=False)
            fig_temp = px.bar(
                x=temp_by_state.index,
                y=temp_by_state.values,
                title="Average Sea Temperature by State",
                labels={'x': 'State', 'y': 'Temperature (°C)'},
                color=temp_by_state.values,
                color_continuous_scale='Reds'
            )
            fig_temp.update_layout(showlegend=False)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # pH levels distribution
            fig_ph = px.histogram(
                ocean_df,
                x='ph_level',
                title="pH Level Distribution in Indian Waters",
                nbins=20,
                labels={'ph_level': 'pH Level', 'count': 'Frequency'}
            )
            fig_ph.add_vline(x=8.1, line_dash="dash", line_color="red", annotation_text="Ideal pH")
            st.plotly_chart(fig_ph, use_container_width=True)

def display_species_page():
    """Species identification and catalog page"""
    st.title("🐟 Marine Species Catalog & Identification")
    
    tab1, tab2, tab3 = st.tabs(["🔍 AI Species Identification", "📚 Species Database", "🌍 Distribution Map"])
    
    with tab1:
        st.subheader("Upload Fish Image for AI Identification")
        
        uploaded_file = st.file_uploader(
            "Choose a fish image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of a marine species for identification"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                if st.button("🔍 Identify Species"):
                    with st.spinner("Analyzing image with AI..."):
                        # Simulate ML model prediction (replace with actual model)
                        predicted_species = simulate_species_prediction(image)
                        
                        with col2:
                            st.success("Species Identified!")
                            display_species_info(predicted_species)
    
    with tab2:
        st.subheader("Indian Marine Species Database")
        
        species_df = load_species_data()
        if not species_df.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                species_type = st.selectbox("Species Type", ["All"] + list(species_df['species_type'].unique()))
            with col2:
                conservation_status = st.selectbox("Conservation Status", ["All"] + list(species_df['conservation_status'].unique()))
            with col3:
                state_filter = st.selectbox("Found in State", ["All"] + get_unique_states(species_df))
            
            # Filter data
            filtered_df = species_df.copy()
            if species_type != "All":
                filtered_df = filtered_df[filtered_df['species_type'] == species_type]
            if conservation_status != "All":
                filtered_df = filtered_df[filtered_df['conservation_status'] == conservation_status]
            if state_filter != "All":
                filtered_df = filtered_df[filtered_df['found_in_regions'].apply(lambda x: state_filter in x if x else False)]
            
            # Display species cards
            for idx, species in filtered_df.head(10).iterrows():
                display_species_card(species)
    
    with tab3:
        st.subheader("Species Distribution Across Indian Waters")
        
        species_df = load_species_data()
        if not species_df.empty:
            # Create distribution chart
            distribution_data = []
            for _, species in species_df.iterrows():
                if species['found_in_regions']:
                    for region in species['found_in_regions']:
                        distribution_data.append({
                            'state': region,
                            'species': species['common_name'],
                            'type': species['species_type'],
                            'conservation_status': species['conservation_status']
                        })
            
            if distribution_data:
                dist_df = pd.DataFrame(distribution_data)
                
                # Species count by state
                fig_dist = px.bar(
                    dist_df.groupby('state').size().reset_index(name='count'),
                    x='state',
                    y='count',
                    title="Number of Marine Species by Indian State",
                    labels={'count': 'Number of Species'}
                )
                fig_dist.update_xaxes(tickangle=45)
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Conservation status distribution
                fig_conservation = px.pie(
                    dist_df,
                    names='conservation_status',
                    title="Conservation Status Distribution"
                )
                st.plotly_chart(fig_conservation, use_container_width=True)

def display_fisheries_page():
    """Fisheries management and sustainability page"""
    st.title("🎣 Fisheries Management & Sustainability")
    
    fisheries_df = load_fisheries_data()
    
    if not fisheries_df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_catch = fisheries_df['catch_volume'].sum() / 1000  # Convert to tons
        avg_sustainability = fisheries_df['sustainability_score'].mean()
        active_vessels = fisheries_df['vessel_count'].sum()
        top_port = fisheries_df.groupby('port_name')['catch_volume'].sum().idxmax()
        
        with col1:
            st.metric("🐟 Total Catch", f"{total_catch:.1f} tons")
        with col2:
            st.metric("📈 Avg Sustainability", f"{avg_sustainability:.1f}/100")
        with col3:
            st.metric("🚢 Active Vessels", f"{active_vessels:,}")
        with col4:
            st.metric("🏆 Top Port", top_port)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Catch by state
            catch_by_state = fisheries_df.groupby('state')['catch_volume'].sum().sort_values(ascending=False)
            fig_catch = px.bar(
                x=catch_by_state.index,
                y=catch_by_state.values / 1000,  # Convert to tons
                title="Fish Catch by State (Tons)",
                labels={'x': 'State', 'y': 'Catch Volume (Tons)'}
            )
            st.plotly_chart(fig_catch, use_container_width=True)
        
        with col2:
            # Sustainability scores by fishing method
            sustainability_by_method = fisheries_df.groupby('fishing_method')['sustainability_score'].mean().sort_values(ascending=False)
            fig_sustainability = px.bar(
                x=sustainability_by_method.values,
                y=sustainability_by_method.index,
                orientation='h',
                title="Sustainability Score by Fishing Method",
                labels={'x': 'Sustainability Score', 'y': 'Fishing Method'}
            )
            st.plotly_chart(fig_sustainability, use_container_width=True)
        
        # Seasonal trends
        st.subheader("🌪️ Seasonal Fishing Patterns")
        if 'monsoon_season' in fisheries_df.columns:
            seasonal_data = fisheries_df.groupby(['monsoon_season', 'state'])['catch_volume'].sum().reset_index()
            fig_seasonal = px.bar(
                seasonal_data,
                x='monsoon_season',
                y='catch_volume',
                color='state',
                title="Catch Volume by Monsoon Season",
                labels={'catch_volume': 'Catch Volume (kg)', 'monsoon_season': 'Season'}
            )
            st.plotly_chart(fig_seasonal, use_container_width=True)

def display_alerts_page():
    """Environmental alerts and monitoring page"""
    st.title("🚨 Environmental Alerts & Monitoring")
    
    alerts_df = load_alerts()
    
    if not alerts_df.empty:
        # Alert summary
        col1, col2, col3 = st.columns(3)
        
        critical_alerts = len(alerts_df[alerts_df['severity'] == 'Critical'])
        high_alerts = len(alerts_df[alerts_df['severity'] == 'High'])
        total_alerts = len(alerts_df)
        
        with col1:
            st.metric("🔴 Critical Alerts", critical_alerts)
        with col2:
            st.metric("🟡 High Alerts", high_alerts)
        with col3:
            st.metric("📊 Total Active", total_alerts)
        
        # Alert types distribution
        alert_types = alerts_df['alert_type'].value_counts()
        fig_types = px.pie(
            values=alert_types.values,
            names=alert_types.index,
            title="Distribution of Alert Types"
        )
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Recent alerts table
        st.subheader("📋 Recent Environmental Alerts")
        
        display_cols = ['title', 'alert_type', 'severity', 'affected_states', 'issued_by', 'created_at']
        if all(col in alerts_df.columns for col in display_cols):
            alerts_display = alerts_df[display_cols].copy()
            alerts_display['created_at'] = pd.to_datetime(alerts_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            alerts_display['affected_states'] = alerts_display['affected_states'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else str(x)
            )
            st.dataframe(alerts_display, use_container_width=True)

def simulate_species_prediction(image):
    """Simulate ML model prediction (replace with actual model)"""
    # This is a mock function - replace with actual ML model inference
    import random
    
    sample_species = [
        {
            "scientific_name": "Rastrelliger kanagurta",
            "common_name": "Indian Mackerel",
            "local_names": {"hindi": "छोटी चूड़ी मछली", "tamil": "காவல்"},
            "confidence": 0.85,
            "conservation_status": "Least Concern",
            "commercial_value": "High"
        },
        {
            "scientific_name": "Hilsa ilisha",
            "common_name": "Hilsa Shad",
            "local_names": {"bengali": "ইলিশ", "hindi": "इलीश"},
            "confidence": 0.78,
            "conservation_status": "Near Threatened",
            "commercial_value": "High"
        }
    ]
    
    return random.choice(sample_species)

def display_species_info(species_info):
    """Display species information card"""
    st.markdown(f"""
    <div class="species-card">
    <h3>🐟 {species_info['common_name']}</h3>
    <p><strong>Scientific Name:</strong> <em>{species_info['scientific_name']}</em></p>
    <p><strong>Confidence:</strong> {species_info['confidence']:.1%}</p>
    <p><strong>Conservation Status:</strong> {species_info['conservation_status']}</p>
    <p><strong>Commercial Value:</strong> {species_info['commercial_value']}</p>
    <p><strong>Local Names:</strong></p>
    <ul>
    """, unsafe_allow_html=True)
    
    for lang, name in species_info['local_names'].items():
        st.markdown(f"<li><strong>{lang.title()}:</strong> {name}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)

def display_species_card(species):
    """Display individual species card"""
    local_names = ""
    if species['local_names']:
        try:
            names_dict = json.loads(species['local_names']) if isinstance(species['local_names'], str) else species['local_names']
            local_names = " | ".join([f"{lang}: {name}" for lang, name in names_dict.items()])
        except:
            local_names = str(species['local_names'])
    
    regions = ", ".join(species['found_in_regions']) if species['found_in_regions'] else "Unknown"
    
    st.markdown(f"""
    <div class="species-card">
    <h4>🐟 {species['common_name']}</h4>
    <p><strong>Scientific Name:</strong> <em>{species['scientific_name']}</em></p>
    <p><strong>Type:</strong> {species['species_type']}</p>
    <p><strong>Conservation Status:</strong> {species['conservation_status']}</p>
    <p><strong>Found in:</strong> {regions}</p>
    <p><strong>Commercial Value:</strong> {species['commercial_value']}</p>
    <p><strong>Local Names:</strong> {local_names}</p>
    </div>
    """, unsafe_allow_html=True)

def get_unique_states(species_df):
    """Extract unique states from found_in_regions column"""
    states = set()
    for regions in species_df['found_in_regions'].dropna():
        if isinstance(regions, list):
            states.update(regions)
    return sorted(list(states))

def main():
    """Main application logic"""
    # Sidebar navigation
    st.sidebar.title("🌊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "🐟 Species Catalog", "🎣 Fisheries", "🚨 Alerts", "📊 Analytics", "ℹ️ About"]
    )
    
    # Page routing
    if page == "🏠 Dashboard":
        display_main_dashboard()
    elif page == "🐟 Species Catalog":
        display_species_page()
    elif page == "🎣 Fisheries":
        display_fisheries_page()
    elif page == "🚨 Alerts":
        display_alerts_page()
    elif page == "📊 Analytics":
        display_analytics_page()
    else:
        display_about_page()
    
    # Sidebar additional info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Quick Stats")
    st.sidebar.info("🌊 Coastline: 7,516 km\n🏝️ Islands: 1,382\n🎣 Fishermen: 4+ million")
    
    st.sidebar.markdown("### 🔗 Data Sources")
    st.sidebar.markdown("""
    - [INCOIS](https://incois.gov.in/) - Ocean Data
    - [CMFRI](https://cmfri.org.in/) - Fisheries Research  
    - [IMD](https://mausam.imd.gov.in/) - Weather Data
    - [ISRO](https://isro.gov.in/) - Satellite Data
    """)

def display_analytics_page():
    """Advanced analytics and insights page"""
    st.title("📊 Marine Biodiversity Analytics")
    
    tab1, tab2, tab3 = st.tabs(["🌊 Ocean Health", "🐟 Species Trends", "🎣 Fisheries Analytics"])
    
    with tab1:
        st.subheader("Ocean Health Index")
        
        # Simulate ocean health data
        ocean_health_data = pd.DataFrame({
            'State': ['Kerala', 'Tamil Nadu', 'Karnataka', 'Goa', 'Maharashtra', 'Gujarat'],
            'Water Quality': [78, 72, 81, 85, 69, 74],
            'Biodiversity Score': [82, 76, 88, 91, 71, 77],
            'Pollution Level': [25, 35, 20, 15, 45, 32],
            'Overall Health': [78, 71, 83, 87, 65, 73]
        })
        
        fig_health = px.scatter(
            ocean_health_data,
            x='Water Quality',
            y='Biodiversity Score',
            size='Overall Health',
            color='Pollution Level',
            hover_name='State',
            title="Ocean Health Assessment by State",
            labels={'Water Quality': 'Water Quality Score', 'Biodiversity Score': 'Biodiversity Score'}
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    with tab2:
        st.subheader("Species Population Trends")
        
        # Simulate species trend data
        years = list(range(2020, 2025))
        species_trends = pd.DataFrame({
            'Year': years * 4,
            'Species': ['Indian Mackerel', 'Hilsa Shad', 'Kingfish', 'Pomfret'] * 5,
            'Population_Index': [100, 95, 88, 92, 85, 105, 98, 89, 87, 82, 110, 102, 91, 89, 78, 115, 108, 95, 92, 75]
        })
        
        fig_trends = px.line(
            species_trends,
            x='Year',
            y='Population_Index',
            color='Species',
            title="Species Population Trends (2020-2024)",
            markers=True
        )
        fig_trends.add_hline(y=100, line_dash="dash", annotation_text="Baseline (2020)")
        st.plotly_chart(fig_trends, use_container_width=True)
    
    with tab3:
        st.subheader("Fisheries Sustainability Metrics")
        
        # Load and display fisheries analytics
        fisheries_df = load_fisheries_data()
        if not fisheries_df.empty:
            # Monthly catch trends
            if 'recorded_date' in fisheries_df.columns:
                fisheries_df['recorded_date'] = pd.to_datetime(fisheries_df['recorded_date'])
                fisheries_df['month'] = fisheries_df['recorded_date'].dt.to_period('M')
                
                monthly_catch = fisheries_df.groupby('month')['catch_volume'].sum().reset_index()
                monthly_catch['month'] = monthly_catch['month'].astype(str)
                
                fig_monthly = px.line(
                    monthly_catch,
                    x='month',
                    y='catch_volume',
                    title="Monthly Catch Volume Trends",
                    labels={'catch_volume': 'Catch Volume (kg)', 'month': 'Month'}
                )
                st.plotly_chart(fig_monthly, use_container_width=True)

def display_about_page():
    """About page with project information"""
    st.title("ℹ️ About Marine Biodiversity Platform")
    
    st.markdown("""
    ## 🎯 Mission
    To create a comprehensive platform for monitoring and conserving India's marine biodiversity 
    through advanced technology, real-time data analysis, and community engagement.
    
    ## 🌊 Focus Areas
    - **Ocean Monitoring**: Real-time tracking of water quality, temperature, and marine conditions
    - **Species Conservation**: AI-powered species identification and population monitoring
    - **Sustainable Fisheries**: Data-driven insights for responsible fishing practices
    - **Environmental Alerts**: Early warning system for marine environmental threats
    
    ## 🔬 Technology Stack
    - **Frontend**: Streamlit for interactive web application
    - **Database**: Supabase with PostGIS for geospatial data
    - **Machine Learning**: TensorFlow for species identification
    - **Visualization**: Plotly and Folium for charts and maps
    
    ## 📊 Coverage
    - **Coastline**: 7,516 km across 9 coastal states
    - **Marine Species**: 500+ catalogued species
    - **Fishing Communities**: Supporting 4+ million fishermen
    - **Protected Areas**: Monitoring 50+ marine reserves
    
    ## 🤝 Partners
    - Indian National Centre for Ocean Information Services (INCOIS)
    - Central Marine Fisheries Research Institute (CMFRI)
    - India Meteorological Department (IMD)
    - Indian Space Research Organisation (ISRO)
    
    ## 📞 Contact
    For research collaborations, data contributions, or technical support:
    - Email: marine.biodiversity@india.gov.in
    - GitHub: [Marine Biodiversity Platform](https://github.com/marine-biodiversity-india)
    """)
    
    # Add Indian flag colors footer
    st.markdown("""
    ---
    <div style="text-align: center; padding: 20px;">
    <p style="color: #FF9933;">🇮🇳</p>
    <p><strong>Developed for Indian Marine Conservation</strong></p>
    <p style="color: #138808;">Preserving our blue heritage for future generations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()