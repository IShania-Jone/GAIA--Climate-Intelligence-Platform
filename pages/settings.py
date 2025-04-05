"""
Settings page for GAIA-∞ Climate Intelligence Platform
"""

import streamlit as st
import ee
import os
from utils.earth_engine import initialize_earth_engine

# Page config
st.set_page_config(
    page_title="GAIA-∞ | Settings",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
.auth-container {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 20px 0;
}
.success-box {
    background-color: #d4edda;
    color: #155724;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
.warning-box {
    background-color: #fff3cd;
    color: #856404;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ Platform Settings")

# Earth Engine Authentication Section
st.header("🌍 Google Earth Engine Authentication")

with st.expander("Earth Engine Setup Guide", expanded=True):
    st.markdown("""
    ### How to Set Up Earth Engine Authentication:
    1. Go to [Google Cloud Console](https://console.cloud.google.com)
    2. Create a new project or select existing one
    3. Enable Earth Engine API
    4. Create a service account and download the private key JSON
    5. Enter the credentials below
    """)

# Check current authentication status
ee_status = initialize_earth_engine()
if ee_status:
    st.markdown("""
    <div class="success-box">
        ✅ Earth Engine is authenticated and working properly!
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="warning-box">
        ⚠️ Earth Engine requires authentication for full functionality
    </div>
    """, unsafe_allow_html=True)

# Credentials input
with st.form("earth_engine_credentials"):
    st.subheader("Enter Earth Engine Credentials")

    service_account = st.text_input(
        "Service Account Email",
        value=st.session_state.get('earth_engine_service_account', ''),
        placeholder="your-service-account@your-project.iam.gserviceaccount.com",
        help="Enter the service account email from Google Cloud Console"
    )

    private_key = st.text_area(
        "Private Key",
        value=st.session_state.get('earth_engine_private_key', ''),
        placeholder="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
        help="Paste the entire private key including the BEGIN and END markers"
    )

    submitted = st.form_submit_button("Save and Authenticate")

    if submitted:
        if service_account and private_key:
            # Store credentials in session state
            st.session_state.earth_engine_service_account = service_account
            st.session_state.earth_engine_private_key = private_key

            # Try to initialize Earth Engine with new credentials
            if initialize_earth_engine():
                st.success("🎉 Authentication successful! Earth Engine is now fully functional.")
                st.balloons()
            else:
                st.error("❌ Authentication failed. Please check your credentials and try again.")
        else:
            st.warning("Please provide both service account email and private key.")

# Test Connection Button
if st.button("🔄 Test Earth Engine Connection"):
    with st.spinner("Testing connection..."):
        if initialize_earth_engine():
            st.success("Connection successful! All Earth Engine features are available.")
        else:
            st.error("Connection failed. Please check your credentials.")

# Advanced Settings
st.header("🛠️ Advanced Settings")

# Performance Settings
with st.expander("Performance Settings"):
    st.slider("Map Render Quality", 1, 10, 5)
    st.slider("Data Cache Size (MB)", 100, 1000, 500)
    st.checkbox("Enable High-Resolution Satellite Imagery")

# Data Settings
with st.expander("Data Settings"):
    st.selectbox("Default Temperature Unit", ["Celsius", "Fahrenheit", "Kelvin"])
    st.selectbox("Default Precipitation Unit", ["mm", "inches"])
    st.checkbox("Enable Real-time Data Updates")


# Create tabs for different settings sections (from original code)
tabs = st.tabs(["🎨 Appearance", "🌎 Maps & Visualization", "⚡ Performance"])

with tabs[0]:  # Appearance Settings
    st.header("Appearance Settings")
    st.subheader("Theme")
    theme = st.selectbox(
        "Select theme",
        ["Light", "Dark", "System default"],
        index=1 if st.session_state.get('dark_mode', False) else 0
    )

    if st.button("Apply Theme"):
        if theme == "Dark":
            st.session_state.dark_mode = True
        elif theme == "Light":
            st.session_state.dark_mode = False
        st.success(f"{theme} theme applied. Some changes may require a page refresh.")

    st.subheader("Font Settings")
    font_size = st.select_slider(
        "Font Size",
        options=["Small", "Medium", "Large", "Extra Large"],
        value=st.session_state.get('font_size', 'Medium')
    )

    if st.button("Apply Font Settings"):
        st.session_state.font_size = font_size
        st.success("Font settings applied!")

with tabs[1]:  # Maps & Visualization Settings
    st.header("Maps & Visualization Settings")
    st.subheader("Default Map View")
    map_center = st.selectbox(
        "Default Map Center",
        ["Global", "North America", "Europe", "Asia", "Africa", "South America", "Oceania", "Arctic", "Antarctic"],
        index=0
    )

    map_type = st.selectbox(
        "Default Map Type",
        ["Satellite", "Terrain", "Street", "Climate Indicators"],
        index=3
    )

    map_resolution = st.select_slider(
        "Map Resolution",
        options=["Low", "Medium", "High"],
        value=st.session_state.get('map_resolution', 'Medium'),
        help="Higher resolution may affect performance"
    )

    if st.button("Save Map Settings"):
        st.session_state.map_center = map_center
        st.session_state.map_type = map_type
        st.session_state.map_resolution = map_resolution
        st.success("Map settings saved successfully!")

    st.subheader("Data Visualization")
    color_scheme = st.selectbox(
        "Color Palette for Climate Data",
        ["Scientific (Viridis)", "Thermal", "Diverging (Red-Blue)", "Rainbow", "Terrain"],
        index=0
    )

    temperature_unit = st.radio(
        "Temperature Unit",
        ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
        index=0
    )

    if st.button("Save Visualization Settings"):
        st.session_state.color_scheme = color_scheme
        st.session_state.temperature_unit = temperature_unit
        st.success("Visualization settings saved successfully!")

with tabs[2]: #Performance settings from original code.
    st.header("Performance Settings")
    st.subheader("Data Caching")
    cache_enabled = st.toggle(
        "Enable Data Caching",
        value=st.session_state.get('cache_enabled', True),
        help="Improve performance by caching data"
    )

    cache_duration = st.slider(
        "Cache Duration (hours)",
        min_value=1,
        max_value=48,
        value=st.session_state.get('cache_duration', 24),
        help="How long to keep cached data"
    )

    st.subheader("Animation Settings")
    animations_enabled = st.toggle(
        "Enable Animations",
        value=st.session_state.get('animations_enabled', True),
        help="Disable for better performance on slower devices"
    )

    st.subheader("Auto-Refresh Data")
    auto_refresh = st.toggle(
        "Auto-Refresh Climate Data",
        value=st.session_state.get('auto_refresh', False)
    )

    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh Interval (minutes)",
            min_value=5,
            max_value=120,
            value=st.session_state.get('refresh_interval', 30)
        )

    if st.button("Save Performance Settings"):
        st.session_state.cache_enabled = cache_enabled
        st.session_state.cache_duration = cache_duration
        st.session_state.animations_enabled = animations_enabled
        st.session_state.auto_refresh = auto_refresh
        if auto_refresh:
            st.session_state.refresh_interval = refresh_interval
        st.success("Performance settings saved successfully!")

# Other API Keys (from original code)
st.header("Other API Keys")
st.markdown("""
Configure additional API keys for extended functionality.
""")

google_maps_api_key = st.text_input(
    "Google Maps API Key",
    value=st.session_state.get('google_maps_api_key', ''),
    placeholder="Enter your Google Maps API key",
    help="Used for enhanced mapping features"
)

weather_api_key = st.text_input(
    "Weather API Key",
    value=st.session_state.get('weather_api_key', ''),
    placeholder="Enter your Weather API key",
    help="Used for real-time weather data"
)

if st.button("Save API Keys"):
    if google_maps_api_key:
        st.session_state.google_maps_api_key = google_maps_api_key
    if weather_api_key:
        st.session_state.weather_api_key = weather_api_key
    st.success("API keys saved successfully!")


# Reset all settings section (from original code)
st.header("Reset Settings")
if st.button("Reset All Settings to Default", use_container_width=True, type="primary"):
    credentials = {
        'earth_engine_service_account': st.session_state.get('earth_engine_service_account', None),
        'earth_engine_private_key': st.session_state.get('earth_engine_private_key', None),
        'google_maps_api_key': st.session_state.get('google_maps_api_key', None),
        'weather_api_key': st.session_state.get('weather_api_key', None)
    }

    for key in list(st.session_state.keys()):
        if key not in ['earth_engine_service_account', 'earth_engine_private_key',
                       'google_maps_api_key', 'weather_api_key']:
            del st.session_state[key]

    st.session_state.dark_mode = False
    st.session_state.font_size = 'Medium'
    st.session_state.map_resolution = 'Medium'
    st.session_state.cache_enabled = True
    st.session_state.cache_duration = 24
    st.session_state.animations_enabled = True
    st.session_state.auto_refresh = False

    for key, value in credentials.items():
        if value:
            st.session_state[key] = value

    st.success("All settings have been reset to default values. Credentials have been preserved.")
    st.info("Please refresh the page for all changes to take effect.")

if st.button("💾 Save All Settings"):
    st.success("Settings saved successfully!")