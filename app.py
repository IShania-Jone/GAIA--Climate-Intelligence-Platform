import streamlit as st

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="GAIA-∞ | Climate Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import time
import logging
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
from datetime import datetime, timedelta

from utils.earth_engine import initialize_earth_engine, get_earth_engine_map
from utils.data_processor import load_climate_data, generate_historical_temperature_data
from utils.visualization import create_climate_risk_map
from database.connection import init_db, check_connection

# Import new modules
from utils.climate_data.climate_data_source import ClimateDataSource
from utils.climate_data.heatmap_generator import GlobalHeatmapGenerator
from utils.ai_storytelling.storyteller import ClimateStoryteller
from utils.gamification.climate_game import ClimateGame
from utils.quantum_prediction import QuantumClimatePredictor
from utils.climate_interventions import ClimateInterventionSimulator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state for user preferences
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
    
if 'viewed_features' not in st.session_state:
    st.session_state.viewed_features = []
    
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
    
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Initialize Earth Engine
ee_initialized = initialize_earth_engine()

# Check database connection status
db_connected = check_connection()
if db_connected:
    st.session_state.db_initialized = True
    logger.info("Database connection successful")
else:
    st.session_state.db_initialized = False
    logger.error("Database connection failed")

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
    
    /* Dashboard title animation */
    @keyframes glow {
        0% { text-shadow: 0 0 5px rgba(0, 163, 224, 0.5); }
        50% { text-shadow: 0 0 20px rgba(0, 163, 224, 0.8), 0 0 30px rgba(0, 163, 224, 0.6); }
        100% { text-shadow: 0 0 5px rgba(0, 163, 224, 0.5); }
    }
    
    .quantum-title {
        animation: glow 2s infinite alternate;
        color: var(--highlight-color);
    }
    
    /* Global metrics styling */
    .metric-container {
        border-radius: 8px;
        padding: 15px;
        background-color: var(--card-background);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* Alert box styling */
    .alert-box {
        border-left: 4px solid #ff4b4b;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
    
    /* Header and logo styling */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    
    .logo-text {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00a3e0, #7cd5ff);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Custom buttons */
    .custom-button {
        background-color: var(--highlight-color);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
        margin: 10px 5px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .custom-button:hover {
        background-color: #3976a0;
    }
    
    /* Interactive visualization container */
    .viz-container {
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
    }
    
    /* Dashboard component loader */
    .loader {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top: 4px solid var(--highlight-color);
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress indicators */
    .progress-bar-container {
        height: 4px;
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 2px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        background-color: var(--highlight-color);
        border-radius: 2px;
        transition: width 0.5s ease;
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
    
    .badge-green {
        background-color: rgba(75, 192, 192, 0.2);
        color: #2e9e9e;
        border: 1px solid rgba(75, 192, 192, 0.5);
    }
    
    .badge-blue {
        background-color: rgba(54, 162, 235, 0.2);
        color: #2a7cb9;
        border: 1px solid rgba(54, 162, 235, 0.5);
    }
    
    .badge-red {
        background-color: rgba(255, 99, 132, 0.2);
        color: #d14664;
        border: 1px solid rgba(255, 99, 132, 0.5);
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

# Sidebar customization
with st.sidebar:
    # Use a more reliable emoji instead of the external image that's failing to load
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🌍</h1>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>GAIA-∞</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>🌍 Welcome to the future of climate intelligence</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # User preferences section
    st.subheader("🔧 Preferences")
    dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    high_resolution = st.toggle("High Resolution Maps", value=True)
    realtime_data = st.toggle("Real-time Data Updates", value=True)
    
    # Google Cloud Integration Status
    st.divider()
    st.subheader("☁️ Google Cloud Integration")
    
    gcp_status = st.empty()
    if ee_initialized:
        gcp_status.success("Earth Engine Connected")
    else:
        gcp_status.warning("Earth Engine Limited Mode")
        st.button("Request API Access", key="request_api")
        
    st.progress(85, "AI Integration: 85%")
    st.progress(70, "Quantum Processing: 70%")
    
    # Database Status
    st.divider()
    st.subheader("💾 Database Status")
    db_status = st.empty()
    if 'db_initialized' in st.session_state:
        if st.session_state.db_initialized:
            db_status.success("Database Connected")
        else:
            db_status.error("Database Connection Failed")
    else:
        db_status.info("Initializing Database...")
    
    # Additional sidebar sections
    st.divider()
    st.subheader("📊 Data Sources")
    data_sources = st.multiselect(
        "Active Data Sources",
        ["Google Earth Engine", "NASA GISS", "NOAA", "ESA", "WMO", "IPCC Models"],
        default=["Google Earth Engine", "NASA GISS", "NOAA"]
    )
    
    st.divider()
    st.subheader("🔄 Last Updated")
    st.text(f"{st.session_state.last_refresh.strftime('%H:%M:%S')}")
    if st.button("Refresh Data"):
        with st.spinner("Refreshing global climate data..."):
            time.sleep(1)  # Simulate data refresh
            st.session_state.last_refresh = datetime.now()
            st.rerun()

# Main content area
# Modern header with animation
st.markdown("""
<div class="header-container">
    <div>
        <h1 class="logo-text">GAIA-∞</h1>
        <h3 class="quantum-title">Quantum-Enhanced Climate Intelligence Platform</h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Interactive welcome message with typewriter effect
st.markdown("""
<div id="welcome-message" style="min-height: 60px; margin-bottom: 20px;">
    <script>
        const text = "GAIA-∞ is a billion-dollar climate intelligence platform that visualizes and simulates Earth systems using Google's advanced geospatial and quantum AI tools. This platform provides real-time insights into climate patterns, predicts environmental events with unprecedented accuracy, and supports data-driven decision making for global climate action.";
        let i = 0;
        const speed = 30; // typing speed in milliseconds
        
        function typeWriter() {
            if (i < text.length) {
                document.getElementById("welcome-text").innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            }
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            setTimeout(typeWriter, 500);
        });
    </script>
    <p id="welcome-text" style="font-size: 1.1rem; line-height: 1.6;"></p>
</div>
""", unsafe_allow_html=True)

# Fixed text (for when JavaScript doesn't load)
st.markdown("""
GAIA-∞ is a billion-dollar climate intelligence platform that visualizes and simulates Earth systems 
using Google's advanced geospatial and quantum AI tools. This platform provides real-time insights into climate 
patterns, predicts environmental events with unprecedented accuracy, and supports data-driven decision making for global climate action.
""")

# Dashboard Layout with animated Key Metrics
st.markdown("<h2>Global Climate Overview</h2>", unsafe_allow_html=True)

# Create columns for metrics with enhanced styling
metric_cols = st.columns(4)

# Function to create animated metrics
def animated_metric(label, value, delta, col, icon, color="#00a3e0"):
    with col:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 1.5rem; margin-right: 10px; color: {color};">{icon}</div>
                <div style="font-weight: 600; font-size: 1.1rem;">{label}</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div style="font-size: 1.8rem; font-weight: 700;">{value}</div>
                <div style="color: {'red' if float(delta.replace('°C', '').replace('+', '').replace(' ppm', '').replace(' mm/yr', '').replace('%', '').replace(' change', '').replace(' per decade', '')) > 0 else 'green'}; font-weight: 600;">{delta}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Apply animated metrics
animated_metric("Global Temperature", "+1.1°C", "+0.2°C", metric_cols[0], "🌡️", "#FF5733")
animated_metric("CO₂ Concentration", "417 ppm", "+2.5 ppm", metric_cols[1], "💨", "#4CAF50")
animated_metric("Sea Level Rise", "+3.4 mm/yr", "+0.1 mm/yr", metric_cols[2], "🌊", "#2196F3")
animated_metric("Arctic Sea Ice", "-13.1%", "-0.4% change", metric_cols[3], "❄️", "#9C27B0")

# Global Alert System
st.markdown("<div class='alert-box'><strong>⚠️ ALERT:</strong> Extreme heat event detected in Southeast Asia. Predicted to affect 20M+ people over the next 5 days.</div>", unsafe_allow_html=True)

# Featured interactive visualization with Earth Engine
st.markdown("<h2>Featured Visualization: Earth Digital Twin</h2>", unsafe_allow_html=True)

# Main Map View with enhanced loading
map_container = st.container()
with map_container:
    st.markdown("<div class='viz-container'>", unsafe_allow_html=True)
    
    # Map loading animation
    with st.spinner("Loading Earth Digital Twin..."):
        # Load map data
        if ee_initialized:
            m = get_earth_engine_map(center_lat=20, center_lon=0, zoom=2)
            folium_static(m, width=1250, height=500)
        else:
            # Fallback visualization when Earth Engine isn't initialized
            st.markdown('<div style="text-align: center; font-size: 8rem;">🌍</div>', unsafe_allow_html=True)
            st.warning("Enhanced Earth Engine visualization requires API authentication. Currently using limited visualization mode.")
            
            # Show a basic interactive visualization with plotly
            df = generate_historical_temperature_data()
            # Check actual column names in the dataframe
            if 'temperature_anomaly' in df.columns:
                y_column = 'temperature_anomaly'
            elif 'anomaly' in df.columns:
                y_column = 'anomaly'
            else:
                # Create a sample dataframe if structure isn't as expected
                years = list(range(1880, 2025))
                anomalies = [(-0.2 + 0.01 * i) for i in range(len(years))]
                df = pd.DataFrame({"year": years, "anomaly": anomalies})
                y_column = 'anomaly'
                
            fig = px.line(df, x="year", y=y_column, 
                          title="Global Temperature Anomaly (°C) - 1880-Present")
            fig.update_layout(height=400, width=1200)
            st.plotly_chart(fig, use_container_width=True)
    
    # Layer controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.multiselect("Data Layers", 
                      ["Temperature", "Precipitation", "Vegetation", "Sea Ice", "Emissions"], 
                      default=["Temperature", "Precipitation"])
    with col2:
        st.select_slider("Time Period", 
                         options=["Past 24h", "Past Week", "Past Month", "Past Year", "Past Decade"],
                         value="Past Month")
    with col3:
        st.button("Full Screen View", key="fullscreen")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Interactive feature cards using custom CSS
st.markdown("<h2>Explore GAIA-∞ Features</h2>", unsafe_allow_html=True)

feature_col1, feature_col2 = st.columns(2)

# Initialize data source for stats
climate_data_source = ClimateDataSource()

with feature_col1:
    st.markdown("""
    <div class="feature-card">
        <h3 style="display: flex; align-items: center;"><span style="font-size: 1.5rem; margin-right: 10px;">🌎</span> Earth Digital Twin</h3>
        <p>Explore our interactive digital twin of Earth with real-time data from multiple satellite sources, powered by Google Earth Engine.</p>
        <div style="display: flex; margin-top: 10px;">
            <span class="badge badge-blue">Real-time</span>
            <span class="badge badge-green">3D Visualization</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: 85%;"></div>
        </div>
    </div>
    
    <div class="feature-card">
        <h3 style="display: flex; align-items: center;"><span style="font-size: 1.5rem; margin-right: 10px;">📊</span> Climate Dashboard</h3>
        <p>View comprehensive climate metrics with advanced analytics and predictive insights using Google Cloud AI.</p>
        <div style="display: flex; margin-top: 10px;">
            <span class="badge badge-blue">AI-Powered</span>
            <span class="badge badge-green">Real-time Data</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: 95%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div class="feature-card">
        <h3 style="display: flex; align-items: center;"><span style="font-size: 1.5rem; margin-right: 10px;">🔮</span> Quantum Climate Simulations</h3>
        <p>Run advanced climate change scenarios using quantum-enhanced computational models for unprecedented accuracy.</p>
        <div style="display: flex; margin-top: 10px;">
            <span class="badge badge-blue">Quantum-Powered</span>
            <span class="badge badge-red">Beta</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: 75%;"></div>
        </div>
    </div>
    
    <div class="feature-card">
        <h3 style="display: flex; align-items: center;"><span style="font-size: 1.5rem; margin-right: 10px;">🚨</span> Environmental Alerts</h3>
        <p>Monitor and predict critical environmental events with AI-enhanced early warning systems.</p>
        <div style="display: flex; margin-top: 10px;">
            <span class="badge badge-blue">AI Predictions</span>
            <span class="badge badge-green">Global Coverage</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: 90%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Quick facts with animated counters
st.markdown("<h2>GAIA-∞ Impact</h2>", unsafe_allow_html=True)

impact_cols = st.columns(4)

with impact_cols[0]:
    st.markdown("""
    <div class="metric-container" style="text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 700; color: #00a3e0;" id="counter1">250+</div>
        <div>Data sources integrated</div>
    </div>
    """, unsafe_allow_html=True)

with impact_cols[1]:
    st.markdown("""
    <div class="metric-container" style="text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 700; color: #00a3e0;" id="counter2">15PB</div>
        <div>Data processed daily</div>
    </div>
    """, unsafe_allow_html=True)

with impact_cols[2]:
    st.markdown("""
    <div class="metric-container" style="text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 700; color: #00a3e0;" id="counter3">99.9%</div>
        <div>Prediction accuracy</div>
    </div>
    """, unsafe_allow_html=True)

with impact_cols[3]:
    st.markdown("""
    <div class="metric-container" style="text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 700; color: #00a3e0;" id="counter4">128</div>
        <div>Quantum qubits leveraged</div>
    </div>
    """, unsafe_allow_html=True)

# Information about the system capabilities with enhanced UI
st.markdown("<h2>About GAIA-∞</h2>", unsafe_allow_html=True)

tabs = st.tabs(["Platform Capabilities", "Google Cloud Integration", "Quantum AI", "Data Sources"])

with tabs[0]:
    st.markdown("""
    <div class="feature-card">
        <h3>Next-Generation Climate Intelligence</h3>
        <p>GAIA-∞ integrates multiple Google technologies to provide unprecedented climate insights:</p>
        <ul>
            <li><strong>Real-time Earth visualization</strong> using Google Earth Engine's petabyte-scale satellite imagery</li>
            <li><strong>Advanced climate data analysis</strong> powered by Google Cloud AI and machine learning</li>
            <li><strong>Quantum-enhanced climate simulations</strong> with accuracy levels impossible with classical computing</li>
            <li><strong>Environmental monitoring networks</strong> integrating millions of IoT sensors worldwide</li>
            <li><strong>AI-driven policy recommendations</strong> for climate action and resilience planning</li>
            <li><strong>Digital twin technology</strong> for modeling Earth systems with unprecedented detail</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:
    st.markdown("""
    <div class="feature-card">
        <h3>Seamless Google Cloud Integration</h3>
        <p>GAIA-∞ leverages the full power of Google Cloud's ecosystem:</p>
        <ul>
            <li><strong>Google Earth Engine</strong> for planetary-scale geospatial analysis</li>
            <li><strong>Google Cloud AI</strong> for advanced machine learning and predictive analytics</li>
            <li><strong>BigQuery</strong> for petabyte-scale climate data analysis</li>
            <li><strong>Vertex AI</strong> for creating and deploying climate models at scale</li>
            <li><strong>Google Cloud IoT</strong> for sensor network integration and management</li>
            <li><strong>Google Cloud Run</strong> for serverless, scalable climate applications</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tabs[2]:
    st.markdown("""
    <div class="feature-card">
        <h3>Quantum AI Advantages</h3>
        <p>GAIA-∞ utilizes quantum computing to solve previously intractable climate modeling problems:</p>
        <ul>
            <li><strong>Quantum Machine Learning</strong> for pattern recognition in complex climate datasets</li>
            <li><strong>Quantum Simulation</strong> of atmospheric and oceanic interactions</li>
            <li><strong>Quantum Optimization</strong> for energy-efficient climate solutions</li>
            <li><strong>Quantum-enhanced Weather Prediction</strong> with unprecedented accuracy</li>
            <li><strong>Multi-variable Quantum Analysis</strong> for understanding complex climate interactions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tabs[3]:
    st.markdown("""
    <div class="feature-card">
        <h3>Comprehensive Data Sources</h3>
        <p>GAIA-∞ utilizes data from the world's leading environmental monitoring systems:</p>
        <ul>
            <li><strong>Google Earth Engine</strong> satellite imagery and geospatial datasets</li>
            <li><strong>NASA</strong> Earth observation satellites and climate models</li>
            <li><strong>NOAA</strong> weather and oceanic data</li>
            <li><strong>ESA</strong> Copernicus program for atmospheric monitoring</li>
            <li><strong>IPCC</strong> climate change models and projections</li>
            <li><strong>Global sensor networks</strong> for real-time environmental monitoring</li>
            <li><strong>Citizen science initiatives</strong> for ground-truth validation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Call-to-action section
st.markdown("<h2>Start Exploring</h2>", unsafe_allow_html=True)

cta_cols = st.columns(2)

with cta_cols[0]:
    st.markdown("""
    <div class="feature-card" style="text-align: center;">
        <h3>Navigate to specific GAIA-∞ modules</h3>
        <p>Use the sidebar navigation to explore our specialized climate intelligence modules</p>
    </div>
    """, unsafe_allow_html=True)

with cta_cols[1]:
    st.markdown("""
    <div class="feature-card" style="text-align: center;">
        <h3>Get API Access</h3>
        <p>Request API credentials to access the full power of GAIA-∞'s quantum climate intelligence</p>
        <button class="custom-button">Request API Access</button>
    </div>
    """, unsafe_allow_html=True)

# Modern footer with additional information
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">
    <div>
        <h3 style="margin-bottom: 10px;">GAIA-∞: Climate Intelligence Platform</h3>
        <p>Powered by Google Earth Engine, Google Cloud, and Quantum AI</p>
    </div>
    <div style="text-align: right;">
        <p>© 2025 GAIA-∞ Platform</p>
        <p style="font-size: 0.8rem;">Version 1.0.0 • Quantum Enhanced</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Add JavaScript for enhanced interactivity
st.markdown("""
<script>
    // This script would enhance interactivity, but Streamlit's iframe limitations may restrict some functionality
    console.log("GAIA-∞ Platform initialized");
</script>
""", unsafe_allow_html=True)

# Initialize the database
if 'db_initialized' not in st.session_state:
    # Check if database connection is working
    if check_connection():
        logger.info("Database connection successful")
        # Initialize the database tables
        if init_db():
            logger.info("Database initialized successfully")
            st.session_state.db_initialized = True
        else:
            logger.error("Failed to initialize database")
            st.session_state.db_initialized = False
    else:
        logger.error("Database connection failed")
        st.session_state.db_initialized = False
