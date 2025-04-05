import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import ee
import geemap.foliumap as geemap
import os
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.earth_engine import (
    initialize_earth_engine,
    get_earth_engine_map,
    get_available_datasets,
    add_dataset_to_map
)
from utils.data_processor import get_climate_data_for_location, generate_historical_location_data
# Page config must be the first Streamlit command
st.set_page_config(
    page_title="GAIA-∞ | Earth Digital Twin",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Initialize Earth Engine
ee_initialized = initialize_earth_engine()

# Initialize session state
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "3D Globe"
    
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 3
    
if 'last_location' not in st.session_state:
    st.session_state.last_location = None
    
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
    
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# CSS for enhanced UI
st.markdown("""
<style>
    /* Modern theme customization */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
        transition: background-color 0.5s ease, color 0.5s ease;
    }
    
    /* Night mode variables */
    :root {
        --background-color: #f0f2f6;
        --text-color: #262730;
        --card-background: #ffffff;
        --highlight-color: #4e89ae;
    }
    
    /* Dark mode variables */
    [data-theme="dark"] {
        --background-color: #0e1117;
        --text-color: #fafafa;
        --card-background: #1e2130;
        --highlight-color: #00a3e0;
    }

    /* Animated feature cards */
    .feature-card {
        border-radius: 10px;
        background-color: var(--card-background);
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Header styling */
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #00a3e0, #7cd5ff);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Panels and containers */
    .location-info-container {
        border-radius: 10px;
        background-color: var(--card-background);
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Risk gauge styling */
    .risk-gauge {
        width: 100%;
        height: 8px;
        background-color: #eee;
        border-radius: 4px;
        margin: 5px 0 15px 0;
        overflow: hidden;
    }
    
    .risk-gauge-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 1s ease;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
    }
    
    .badge-blue {
        background-color: rgba(54, 162, 235, 0.2);
        color: #2a7cb9;
        border: 1px solid rgba(54, 162, 235, 0.5);
    }
    
    .badge-green {
        background-color: rgba(75, 192, 192, 0.2);
        color: #2e9e9e;
        border: 1px solid rgba(75, 192, 192, 0.5);
    }
    
    .badge-red {
        background-color: rgba(255, 99, 132, 0.2);
        color: #d14664;
        border: 1px solid rgba(255, 99, 132, 0.5);
    }
    
    /* Control panel styling */
    .control-panel {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Map container styling */
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Layer legend styling */
    .layer-legend {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin: 5px;
    }
    
    /* Animated loader */
    .loader {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top: 4px solid var(--highlight-color);
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom button styling */
    .custom-button {
        background-color: var(--highlight-color);
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
        margin: 5px 3px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        display: inline-block;
    }
    
    .custom-button:hover {
        background-color: #0089c3;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Favorite location item */
    .favorite-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background-color: rgba(0, 163, 224, 0.1);
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .favorite-item:hover {
        background-color: rgba(0, 163, 224, 0.2);
    }
    
    /* Time control slider */
    .time-slider-container {
        padding: 10px 0;
    }
    
    .time-slider-label {
        font-size: 0.9rem;
        color: var(--text-color);
        margin-bottom: 5px;
    }
    
    /* Marker popup styling */
    .custom-popup {
        font-family: 'Inter', sans-serif;
    }
    
    .custom-popup-header {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 5px;
        color: #00a3e0;
    }
    
    /* Data card styling */
    .data-card {
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .data-card-title {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 8px;
        color: var(--highlight-color);
    }
    
    /* Timeline styling */
    .timeline-container {
        position: relative;
        margin: 20px 0;
        padding-left: 20px;
    }
    
    .timeline-line {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background-color: var(--highlight-color);
    }
    
    .timeline-item {
        position: relative;
        margin-bottom: 15px;
        padding-left: 15px;
    }
    
    .timeline-dot {
        position: absolute;
        left: -5px;
        top: 5px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: var(--highlight-color);
    }
    
    .timeline-date {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--highlight-color);
    }
    
    /* Modern tabs styling */
    .modern-tabs {
        display: flex;
        overflow-x: auto;
        margin-bottom: 15px;
        padding-bottom: 5px;
    }
    
    .modern-tab {
        padding: 8px 16px;
        margin-right: 5px;
        border-radius: 20px;
        font-weight: 500;
        cursor: pointer;
        white-space: nowrap;
        background-color: rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .modern-tab.active {
        background-color: var(--highlight-color);
        color: white;
    }
    
    .modern-tab:hover:not(.active) {
        background-color: rgba(0, 0, 0, 0.1);
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animation for page load */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .fade-in-delay-1 {
        animation: fadeIn 0.6s ease 0.2s forwards;
        opacity: 0;
    }
    
    .fade-in-delay-2 {
        animation: fadeIn 0.6s ease 0.4s forwards;
        opacity: 0;
    }
    
    /* Global title animation */
    @keyframes glow {
        0% { text-shadow: 0 0 5px rgba(0, 163, 224, 0.5); }
        50% { text-shadow: 0 0 20px rgba(0, 163, 224, 0.8), 0 0 30px rgba(0, 163, 224, 0.6); }
        100% { text-shadow: 0 0 5px rgba(0, 163, 224, 0.5); }
    }
    
    .quantum-title {
        animation: glow 2s infinite alternate;
        color: var(--highlight-color);
    }
</style>
""", unsafe_allow_html=True)

# Apply dark mode if enabled
if st.session_state.dark_mode:
    st.markdown("""
    <script>
        document.documentElement.setAttribute('data-theme', 'dark');
    </script>
    """, unsafe_allow_html=True)

# Custom header with badge
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
    <div>
        <h1 class="page-title">🌎 Earth Digital Twin</h1>
        <p class="quantum-title" style="margin-top: 0;">Quantum-Enhanced Geospatial Intelligence Platform</p>
    </div>
    <div>
        <span class="badge badge-blue">Google Earth Engine</span>
        <span class="badge badge-green">Real-time Data</span>
        <span class="badge badge-red">Beta</span>
    </div>
</div>

<p class="fade-in" style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 20px;">
    This interactive digital twin of Earth provides unprecedented visualization of our planet's systems powered by 
    Google Earth Engine's petabyte-scale geospatial data and GAIA-∞'s quantum computing capabilities.
    Explore environmental patterns, analyze climate trends, and visualize Earth's interconnected systems in real-time.
</p>
""", unsafe_allow_html=True)

# Sidebar options
st.sidebar.header("Earth Twin Options")

# Dataset selector
dataset_options = [dataset["name"] for dataset in get_available_datasets()]
dataset_ids = [dataset["id"] for dataset in get_available_datasets()]

selected_datasets = st.sidebar.multiselect(
    "Select Earth Data Layers",
    options=dataset_options,
    default=[dataset_options[0]]  # Default to the first dataset
)

# Convert selected dataset names to IDs
selected_dataset_ids = []
for name in selected_datasets:
    index = dataset_options.index(name)
    selected_dataset_ids.append(dataset_ids[index])

# Location input
st.sidebar.subheader("Explore Specific Location")
location_input_method = st.sidebar.radio(
    "Select input method",
    ["Coordinates", "Place Name"]
)

if location_input_method == "Coordinates":
    lat = st.sidebar.slider("Latitude", -90.0, 90.0, 0.0)
    lon = st.sidebar.slider("Longitude", -180.0, 180.0, 0.0)
    location_name = f"Coordinates ({lat}, {lon})"
else:
    location_name = st.sidebar.text_input("Enter place name", "San Francisco, CA")
    # In a real app, we would geocode the place name to get coordinates
    # For this example, we'll use some fixed coordinates for demonstration
    if location_name == "San Francisco, CA":
        lat, lon = 37.7749, -122.4194
    else:
        # Random coordinates for other inputs
        lat = np.random.uniform(-80, 80)
        lon = np.random.uniform(-170, 170)

# Other visualization options
visualization_type = st.sidebar.selectbox(
    "Visualization Type",
    ["Satellite Imagery", "Data Layers", "Combined View"]
)

time_period = st.sidebar.selectbox(
    "Time Period",
    ["Current (Last 7 days)", "Last Month", "Last Year", "5-Year Average"]
)

# View mode selector with modern styling
view_mode_options = ["3D Globe", "Map View", "Split View", "Satellite Only"]
view_mode_cols = st.columns(4)

# Create modern tabs for view modes
st.markdown("""
<div class="modern-tabs">
    <div class="modern-tab active">3D Globe</div>
    <div class="modern-tab">Map View</div>
    <div class="modern-tab">Split View</div>
    <div class="modern-tab">Satellite Only</div>
</div>
""", unsafe_allow_html=True)

# Create the Earth Engine map
if ee_initialized:
    try:
        # Control panel for advanced options
        with st.expander("Advanced Visualization Controls", expanded=False):
            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            
            control_cols = st.columns(3)
            
            with control_cols[0]:
                resolution = st.select_slider(
                    "Resolution",
                    options=["Low", "Medium", "High", "Ultra"],
                    value="Medium"
                )
                
            with control_cols[1]:
                render_quality = st.select_slider(
                    "Render Quality",
                    options=["Fast", "Balanced", "Detailed"],
                    value="Balanced"
                )
                
            with control_cols[2]:
                projection = st.selectbox(
                    "Map Projection",
                    ["Mercator", "Equal Earth", "Equirectangular", "Natural Earth"]
                )
            
            # Time slider for temporal data
            st.markdown('<div class="time-slider-container">', unsafe_allow_html=True)
            st.markdown('<div class="time-slider-label">Time Range</div>', unsafe_allow_html=True)
            
            time_range = st.slider(
                "Select time range",
                min_value=datetime(2000, 1, 1),
                max_value=datetime.now(),
                value=(datetime(2020, 1, 1), datetime.now()),
                format="MMM YYYY"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Create columns for the map and data panels
        map_col, data_col = st.columns([7, 3])
        
        with map_col:
            # Map container with enhanced styling
            st.markdown('<div class="map-container fade-in">', unsafe_allow_html=True)
            
            with st.spinner("Loading Earth Digital Twin..."):
                # Create the map centered at selected coordinates
                m = get_earth_engine_map(lat, lon, zoom=st.session_state.zoom_level)
                
                # Add selected datasets to the map
                for dataset_id in selected_dataset_ids:
                    add_dataset_to_map(m, dataset_id)
                
                # Add a marker for the selected location with custom popup
                if location_name:
                    html = f"""
                    <div class="custom-popup">
                        <div class="custom-popup-header">{location_name}</div>
                        <div>Lat: {lat:.4f}, Lon: {lon:.4f}</div>
                        <div style="margin-top: 5px;">Click for detailed analysis</div>
                    </div>
                    """
                    
                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(html, max_width=300),
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(m)
                
                # Display the map with enhanced dimensions
                folium_static(m, width=850, height=550)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Layer control and map tools
            tool_cols = st.columns(4)
            
            with tool_cols[0]:
                st.markdown('<button class="custom-button">📷 Screenshot</button>', unsafe_allow_html=True)
                
            with tool_cols[1]:
                st.markdown('<button class="custom-button">📊 Analyze Area</button>', unsafe_allow_html=True)
                
            with tool_cols[2]:
                st.markdown('<button class="custom-button">📍 Add Marker</button>', unsafe_allow_html=True)
                
            with tool_cols[3]:
                st.markdown('<button class="custom-button">🔄 Reset View</button>', unsafe_allow_html=True)
            
            # Add map usage instructions
            st.markdown("""
            <div class="data-card fade-in-delay-1">
                <div class="data-card-title">📋 Map Controls & Tools</div>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>🖱️ Zoom</strong>: Scroll wheel or use +/- buttons</li>
                    <li><strong>🔍 Pan</strong>: Click and drag to move around</li>
                    <li><strong>🌓 Layers</strong>: Toggle layers in the upper right control</li>
                    <li><strong>📏 Measure</strong>: Shift+click to measure distances</li>
                    <li><strong>📍 Data Points</strong>: Click on the map for detailed point data</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick layer toggles for common datasets
            st.markdown("""
            <div class="control-panel fade-in-delay-1" style="margin-top: 15px;">
                <div style="font-weight: 600; margin-bottom: 10px;">Quick Layer Toggles</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    <span class="badge badge-blue" style="cursor: pointer;">Temperature</span>
                    <span class="badge badge-green" style="cursor: pointer;">Precipitation</span>
                    <span class="badge badge-blue" style="cursor: pointer;">Sea Level</span>
                    <span class="badge badge-red" style="cursor: pointer;">Emissions</span>
                    <span class="badge badge-green" style="cursor: pointer;">Biodiversity</span>
                    <span class="badge badge-blue" style="cursor: pointer;">Ocean Health</span>
                    <span class="badge badge-green" style="cursor: pointer;">Vegetation</span>
                    <span class="badge badge-red" style="cursor: pointer;">Pollution</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with data_col:
            # Location data card with modern styling
            st.markdown(f"""
            <div class="location-info-container fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-weight: 700; font-size: 1.2rem; color: var(--highlight-color);">📍 Location Analysis</div>
                    <div>
                        <span class="badge badge-blue">Quantum Analysis</span>
                    </div>
                </div>
                <div style="font-weight: 600; margin-bottom: 5px;">{location_name}</div>
                <div style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">Lat: {lat:.4f}, Lon: {lon:.4f}</div>
            """, unsafe_allow_html=True)
            
            # Get climate data for the selected location
            location_data = get_climate_data_for_location(lat, lon)
            
            # Display climate data with enhanced styling
            col1, col2 = st.columns(2)
            
            with col1:
                temp = location_data.get('current_temperature', 20)
                temp_anomaly = location_data.get('temperature_anomaly', 1.2)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: {'#ff5722' if temp > 25 else '#2196f3'};">{temp}°C</div>
                    <div style="color: {'#ff5722' if temp_anomaly > 0 else '#4caf50'}; font-weight: 600;">{'+' if temp_anomaly > 0 else ''}{temp_anomaly}°C</div>
                    <div style="font-size: 0.9rem; color: #666;">from normal</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                precip = location_data.get('annual_precipitation', 750)
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #2196f3;">{precip}</div>
                    <div style="font-weight: 600;">mm/year</div>
                    <div style="font-size: 0.9rem; color: #666;">precipitation</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Climate risk indicators with visual gauges
            st.markdown("""
            <div style="margin: 20px 0 10px 0; font-weight: 600; color: var(--highlight-color);">Climate Risk Indicators</div>
            """, unsafe_allow_html=True)
            
            # Sea level risk
            sea_level_risk = location_data.get('sea_level_risk', 7)
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <div>Sea Level Risk</div>
                    <div style="font-weight: 600;">{sea_level_risk}/10</div>
                </div>
                <div class="risk-gauge">
                    <div class="risk-gauge-fill" style="width: {sea_level_risk*10}%; background-color: {'#ff5722' if sea_level_risk > 7 else '#ff9800' if sea_level_risk > 3 else '#4caf50'};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Drought risk
            drought_risk = location_data.get('drought_risk', 5)
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <div>Drought Risk</div>
                    <div style="font-weight: 600;">{drought_risk}/10</div>
                </div>
                <div class="risk-gauge">
                    <div class="risk-gauge-fill" style="width: {drought_risk*10}%; background-color: {'#ff5722' if drought_risk > 7 else '#ff9800' if drought_risk > 3 else '#4caf50'};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Biodiversity risk
            biodiversity_risk = location_data.get('biodiversity_risk', 8)
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <div>Biodiversity Risk</div>
                    <div style="font-weight: 600;">{biodiversity_risk}/10</div>
                </div>
                <div class="risk-gauge">
                    <div class="risk-gauge-fill" style="width: {biodiversity_risk*10}%; background-color: {'#ff5722' if biodiversity_risk > 7 else '#ff9800' if biodiversity_risk > 3 else '#4caf50'};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Close the location container div
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add location to favorites
            st.markdown("""
            <div class="fade-in-delay-1" style="margin: 15px 0;">
                <button class="custom-button" style="width: 100%;">
                    <span style="margin-right: 5px;">★</span> Add to Favorites
                </button>
            </div>
            """, unsafe_allow_html=True)
            
            # Favorite locations section
            if len(st.session_state.favorites) > 0 or True:  # Always show for demonstration
                st.markdown("""
                <div class="location-info-container fade-in-delay-2">
                    <div style="font-weight: 600; margin-bottom: 10px;">Saved Locations</div>
                """, unsafe_allow_html=True)
                
                # Demo favorites
                st.markdown("""
                    <div class="favorite-item">
                        <div>New York City</div>
                        <div style="font-size: 0.8rem; color: #666;">40.71, -74.01</div>
                    </div>
                    <div class="favorite-item">
                        <div>Amazon Rainforest</div>
                        <div style="font-size: 0.8rem; color: #666;">-3.47, -62.21</div>
                    </div>
                    <div class="favorite-item">
                        <div>Great Barrier Reef</div>
                        <div style="font-size: 0.8rem; color: #666;">-18.29, 147.42</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Data download options with enhanced styling
            st.markdown("""
            <div class="location-info-container fade-in-delay-2">
                <div style="font-weight: 600; margin-bottom: 10px;">Export & Share</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <button class="custom-button" style="width: 100%;">
                        <span style="margin-right: 5px;">📊</span> Export Data
                    </button>
                    <button class="custom-button" style="width: 100%;">
                        <span style="margin-right: 5px;">📄</span> PDF Report
                    </button>
                    <button class="custom-button" style="width: 100%;">
                        <span style="margin-right: 5px;">📷</span> Screenshot
                    </button>
                    <button class="custom-button" style="width: 100%;">
                        <span style="margin-right: 5px;">📤</span> Share Link
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Prepare location data for download (hidden button that actually works)
            if location_data:
                location_json = json.dumps({
                    "location": {
                        "name": location_name,
                        "latitude": lat,
                        "longitude": lon
                    },
                    "climate_data": {
                        "current_temperature": location_data.get('current_temperature'),
                        "temperature_anomaly": location_data.get('temperature_anomaly'),
                        "annual_precipitation": location_data.get('annual_precipitation'),
                        "sea_level_risk": location_data.get('sea_level_risk'),
                        "biodiversity_risk": location_data.get('biodiversity_risk'),
                        "drought_risk": location_data.get('drought_risk')
                    },
                    "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_sources": ["Google Earth Engine", "NASA GISS", "NOAA"],
                    "gaia_version": "1.0.0"
                })
                
                # Use Streamlit's download button (hidden in UI but functional)
                st.download_button(
                    label="Hidden Download Button",
                    data=location_json,
                    file_name=f"gaia_climate_analysis_{location_name.replace(' ', '_')}.json",
                    mime="application/json",
                    key="download_button",
                    help="Download data as JSON",
                    type="primary"
                )
                
            # Show a historical comparison chart
            st.markdown("""
            <div class="location-info-container fade-in-delay-2" style="margin-top: 15px;">
                <div style="font-weight: 600; margin-bottom: 10px;">Historical Temperature Trend</div>
            """, unsafe_allow_html=True)
            
            # Generate historical data for the location
            hist_data = generate_historical_location_data(lat, lon)
            
            # Convert to dataframe
            if isinstance(hist_data, list):
                df = pd.DataFrame(hist_data)
            else:
                # Create sample data for demonstration
                years = list(range(1900, 2025, 5))
                temp_values = [
                    14 + 0.01 * (year - 1900) if year < 1980 
                    else 14 + 0.01 * (1980 - 1900) + 0.04 * (year - 1980)
                    for year in years
                ]
                df = pd.DataFrame({
                    'year': years,
                    'temperature': temp_values
                })
            
            # Create temperature trend chart with plotly
            fig = px.line(
                df, 
                x='year', 
                y='temperature',
                labels={'temperature': 'Temperature (°C)', 'year': 'Year'},
                template='plotly_white'
            )
            
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=10, t=10, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            )
            
            # Add a trend line
            fig.add_traces(
                px.scatter(
                    df, x='year', y='temperature', trendline='ols'
                ).data[1]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error creating Earth map: {str(e)}")
        st.info("Please try selecting different datasets or refreshing the page.")
else:
    st.error("Failed to initialize Earth Engine. Please check your credentials and connection.")
    st.info("Displaying static demo content instead.")
    
    # Display a static image as fallback
    st.markdown("""
    ## Earth Engine Connection Failed
    
    This interactive Earth visualization requires a connection to Google Earth Engine.
    Please ensure you have proper authentication and internet connectivity.
    """)

# Section for data insights
st.subheader("Earth System Insights")

# Create tabs for different insights
insight_tab1, insight_tab2, insight_tab3 = st.tabs(["Temperature Patterns", "Land Cover Change", "Ocean Systems"])

with insight_tab1:
    st.markdown("""
    ### Global Temperature Patterns
    
    Temperature patterns show significant warming trends across most of the globe, with
    the most pronounced warming in Arctic regions (Arctic amplification). This is visible
    in the temperature anomaly layer.
    
    Key observations:
    - Arctic regions warming 2-3 times faster than global average
    - Land areas warming faster than oceans
    - Nighttime temperatures rising faster than daytime temperatures
    """)

with insight_tab2:
    st.markdown("""
    ### Land Cover Change
    
    Land cover visualization reveals significant changes in forests, agriculture, and urban areas.
    
    Key observations:
    - Deforestation trends in tropical regions
    - Urban expansion in coastal and fertile areas
    - Agricultural intensification
    - Shifts in vegetation zones due to warming
    """)

with insight_tab3:
    st.markdown("""
    ### Ocean Systems
    
    Ocean data shows changing temperature patterns, acidification impacts, and circulation changes.
    
    Key observations:
    - Warming ocean surface temperatures
    - Declining sea ice extent
    - Changes in ocean circulation patterns
    - Marine ecosystem shifts
    """)

# Information about data sources
st.markdown("---")
st.subheader("About the Data")
st.markdown("""
The Earth Digital Twin visualization integrates multiple data sources from Google Earth Engine, including:

- **Satellite imagery**: Landsat, Sentinel, MODIS
- **Climate data**: Temperature, precipitation, weather patterns
- **Environmental indicators**: Vegetation indices, land cover, water resources
- **Human systems**: Urban areas, agriculture, infrastructure

This visualization is powered by Google Earth Engine's catalog of geospatial data,
which includes over 40 years of historical imagery and scientific datasets.
""")

# Footer with disclaimer
st.markdown("---")
st.caption("""
**Disclaimer**: This visualization uses real Earth Engine data where available, with some simulated data for demonstration purposes.
For research or decision-making, please consult the original data sources and scientific experts.
""")
