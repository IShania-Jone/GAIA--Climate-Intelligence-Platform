"""
Global Climate Heatmap for GAIA-∞ Climate Intelligence Platform.

This page provides real-time global climate data visualization
through interactive heatmaps and maps.
"""

import streamlit as st
import folium
from folium import plugins
import ee
import geemap.foliumap as geemap
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_folium import folium_static

from utils.earth_engine import initialize_earth_engine
from utils.climate_data.heatmap_generator import GlobalHeatmapGenerator
from utils.climate_data.climate_data_source import ClimateDataSource

# Page configuration
st.set_page_config(
    page_title="GAIA-∞ | Global Climate Heatmap",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Earth Engine
ee_initialized = initialize_earth_engine()

# Initialize heatmap generator
heatmap_generator = GlobalHeatmapGenerator(earth_engine_initialized=ee_initialized)

# Initialize climate data source
data_source = ClimateDataSource()

# Custom CSS for the page
st.markdown("""
<style>
    .heatmap-header {
        background: linear-gradient(90deg, rgba(0,163,224,0.2) 0%, rgba(0,75,133,0.2) 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .heatmap-header h1 {
        color: #00a3e0;
    }
    
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .control-panel {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .stat-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00a3e0;
        margin: 10px 0;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .legend-color {
        width: 20px;
        height: 20px;
        margin-right: 10px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_heatmap_type' not in st.session_state:
    st.session_state.current_heatmap_type = 'temperature'
    
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    
if 'map_center' not in st.session_state:
    st.session_state.map_center = [20, 0]
    
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 2

# Page header
st.markdown("""
<div class="heatmap-header">
    <h1>Global Climate Heatmap</h1>
    <p>Real-time visualization of global climate data using advanced Earth observation</p>
</div>
""", unsafe_allow_html=True)

# Control panel for the heatmap
st.markdown("### Heatmap Controls")

with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
    
    with col1:
        heatmap_type = st.selectbox(
            "Data Layer",
            options=["Temperature Anomaly", "Precipitation", "Extreme Events", "Combined View"],
            index=0,
            key="heatmap_type_select"
        )
        
        # Map heatmap type to internal value
        heatmap_type_map = {
            "Temperature Anomaly": "temperature",
            "Precipitation": "precipitation",
            "Extreme Events": "extreme_events",
            "Combined View": "combined"
        }
        
        current_type = heatmap_type_map[heatmap_type]
        
        if current_type != st.session_state.current_heatmap_type:
            st.session_state.current_heatmap_type = current_type
            
    with col2:
        time_period = st.selectbox(
            "Time Period",
            options=["Last 7 Days", "Last 30 Days", "Last 90 Days"],
            index=0
        )
        
        # Convert selection to days
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        days_ago = days_map[time_period]
        
    with col3:
        map_style = st.selectbox(
            "Map Style",
            options=["Light", "Dark", "Satellite", "Terrain"],
            index=0
        )
        
        # Map selection to folium tile
        style_map = {
            "Light": "CartoDB positron",
            "Dark": "CartoDB dark_matter",
            "Satellite": "Stamen Terrain",
            "Terrain": "OpenTopoMap"
        }
        
        selected_style = style_map[map_style]
        
    with col4:
        st.write("&nbsp;")  # Spacer for alignment
        refresh_button = st.button("Refresh Data", key="refresh_heatmap", use_container_width=True)
        
        if refresh_button:
            st.session_state.last_update = datetime.now()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display the heatmap
st.markdown("### Global Climate Visualization")

# Heatmap container
map_container = st.container()

with map_container:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    
    # Show loading spinner
    with st.spinner("Loading climate data visualization..."):
        # Create the appropriate map based on selection
        if st.session_state.current_heatmap_type == "temperature":
            if ee_initialized:
                m = heatmap_generator.get_temperature_heatmap(days_ago=days_ago)
            else:
                # Create base map
                m = folium.Map(
                    location=st.session_state.map_center, 
                    zoom_start=st.session_state.map_zoom,
                    tiles=selected_style
                )
                
                # Add temperature layer from database
                m = heatmap_generator.get_temperature_heatmap(m, days_ago=days_ago)
                
        elif st.session_state.current_heatmap_type == "precipitation":
            if ee_initialized:
                m = heatmap_generator.get_precipitation_heatmap(days_ago=days_ago)
            else:
                # Create base map with message
                m = folium.Map(
                    location=st.session_state.map_center, 
                    zoom_start=st.session_state.map_zoom,
                    tiles=selected_style
                )
                # Add a message that precipitation requires Earth Engine
                title_html = '<h3 style="text-align:center;">Precipitation heatmap requires Earth Engine access</h3>'
                m.get_root().html.add_child(folium.Element(title_html))
                
        elif st.session_state.current_heatmap_type == "extreme_events":
            # Create base map
            m = folium.Map(
                location=st.session_state.map_center, 
                zoom_start=st.session_state.map_zoom,
                tiles=selected_style
            )
            
            # Add extreme events layer
            m = heatmap_generator.get_extreme_events_map(m)
            
        elif st.session_state.current_heatmap_type == "combined":
            # For combined view, use the combined map function
            m = heatmap_generator.get_combined_climate_map(
                center_lat=st.session_state.map_center[0],
                center_lon=st.session_state.map_center[1],
                zoom=st.session_state.map_zoom
            )
        
        # If we got a geemap object, convert to HTML for display
        if isinstance(m, geemap.Map):
            # Add control elements
            m.add_layer_control()
            
            # Display the map
            folium_static(m, width=1100, height=500)
            
            # Store center and zoom for future use
            if hasattr(m, 'center') and hasattr(m, 'zoom'):
                st.session_state.map_center = m.center
                st.session_state.map_zoom = m.zoom
        else:
            # For folium maps, display directly
            folium_static(m, width=1100, height=500)
            
            # Unfortunately folium doesn't provide a good way to get current center/zoom
            # So we'll just keep the last known values
    
    st.markdown('</div>', unsafe_allow_html=True)

# Show statistics about the current heatmap
stats_container = st.container()

with stats_container:
    st.markdown("### Climate Data Statistics")
    
    # Get heatmap stats and aggregated climate statistics
    heatmap_stats = heatmap_generator.get_heatmap_stats()
    climate_stats = data_source.get_aggregated_climate_stats()
    
    # Create statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">GLOBAL TEMPERATURE ANOMALY</div>', unsafe_allow_html=True)
        
        temp_value = climate_stats.get("current", {}).get("temperature")
        if temp_value is not None:
            st.markdown(f'<div class="stat-value">+{temp_value:.1f}°C</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stat-value">N/A</div>', unsafe_allow_html=True)
            
        temp_trend = climate_stats.get("trends", {}).get("temperature", {})
        if temp_trend and temp_trend.get("direction"):
            direction = temp_trend["direction"]
            change = temp_trend.get("percentage_change", 0)
            direction_color = "red" if direction == "increasing" else ("green" if direction == "decreasing" else "gray")
            st.markdown(f'<div style="color: {direction_color};">{direction.title()} {abs(change):.1f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">CO₂ CONCENTRATION</div>', unsafe_allow_html=True)
        
        co2_value = climate_stats.get("current", {}).get("co2")
        if co2_value is not None:
            st.markdown(f'<div class="stat-value">{co2_value:.1f} ppm</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stat-value">N/A</div>', unsafe_allow_html=True)
            
        co2_trend = climate_stats.get("trends", {}).get("co2", {})
        if co2_trend and co2_trend.get("direction"):
            direction = co2_trend["direction"]
            change = co2_trend.get("percentage_change", 0)
            direction_color = "red" if direction == "increasing" else ("green" if direction == "decreasing" else "gray")
            st.markdown(f'<div style="color: {direction_color};">{direction.title()} {abs(change):.1f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">ACTIVE EXTREME EVENTS</div>', unsafe_allow_html=True)
        
        events_count = climate_stats.get("active_events")
        if events_count is not None:
            st.markdown(f'<div class="stat-value">{events_count}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stat-value">N/A</div>', unsafe_allow_html=True)
            
        if heatmap_stats.get("most_common_event_type"):
            st.markdown(f'Most common: {heatmap_stats.get("most_common_event_type")}', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">MOST AFFECTED REGION</div>', unsafe_allow_html=True)
        
        region = heatmap_stats.get("most_affected_region")
        if region:
            st.markdown(f'<div class="stat-value" style="font-size: 1.5rem;">{region}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stat-value">N/A</div>', unsafe_allow_html=True)
            
        if heatmap_stats.get("average_severity"):
            st.markdown(f'Avg severity: {heatmap_stats.get("average_severity")}/5', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Additional insights and explanations
with st.expander("Understanding the Heatmap Data"):
    st.markdown("""
    ### Climate Heatmap Interpretation Guide
    
    **Temperature Anomaly**: This layer shows differences from the long-term average temperature.
    - Red areas are warmer than normal
    - Blue areas are cooler than normal
    - The intensity of color indicates the magnitude of the anomaly
    
    **Precipitation**: This layer shows recent precipitation patterns.
    - Blue areas indicate precipitation
    - Darker colors indicate higher precipitation amounts
    - Gray areas have little to no precipitation
    
    **Extreme Events**: This layer shows active extreme climate events.
    - Different colors and icons represent different event types
    - Click on markers for detailed information about each event
    - Size of markers indicates severity
    
    The data is sourced from a combination of satellite observations, ground stations, and climate models,
    providing a comprehensive view of Earth's climate system in near real-time.
    """)
    
    # Legend for temperature anomaly
    st.markdown("#### Temperature Anomaly Legend")
    legend_col1, legend_col2 = st.columns(2)
    
    with legend_col1:
        st.markdown("""
        <div class="legend-item">
            <div class="legend-color" style="background-color: blue;"></div>
            <div>-10°C (Cooler than average)</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: cyan;"></div>
            <div>-5°C</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: green;"></div>
            <div>0°C (Average)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with legend_col2:
        st.markdown("""
        <div class="legend-item">
            <div class="legend-color" style="background-color: yellow;"></div>
            <div>+5°C</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: orange;"></div>
            <div>+7.5°C</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: red;"></div>
            <div>+10°C (Warmer than average)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Legend for extreme events
    st.markdown("#### Extreme Events Legend")
    legend_col1, legend_col2 = st.columns(2)
    
    with legend_col1:
        st.markdown("""
        <div class="legend-item">
            <div class="legend-color" style="background-color: orange;"></div>
            <div>Drought</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: blue;"></div>
            <div>Flood</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: red;"></div>
            <div>Wildfire</div>
        </div>
        """, unsafe_allow_html=True)
        
    with legend_col2:
        st.markdown("""
        <div class="legend-item">
            <div class="legend-color" style="background-color: purple;"></div>
            <div>Extreme Weather</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: darkblue;"></div>
            <div>Sea Level</div>
        </div>
        """, unsafe_allow_html=True)

    # Earth Engine attribution
    st.markdown("---")
    st.markdown("Data provided via Google Earth Engine, NASA, NOAA, and other sources.")
    if not ee_initialized:
        st.warning("Earth Engine integration is limited. Some features require full Earth Engine authentication.")

# Display Earth Engine status
if not ee_initialized:
    st.sidebar.warning("Earth Engine running in limited mode. Some features may not be available.")
    st.sidebar.info("To enable full Earth Engine functionality, add your service account credentials in Settings.")
else:
    st.sidebar.success("Earth Engine initialized successfully")

# Footer with data source info
st.markdown("---")
st.markdown(f"Last data update: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
st.markdown("Data Sources: Earth Engine, MODIS Land Surface Temperature, NASA GPM Precipitation, GAIA-∞ Climate Database")
st.caption("Note: Map may show a mix of real and projected data depending on data availability and Earth Engine access.")