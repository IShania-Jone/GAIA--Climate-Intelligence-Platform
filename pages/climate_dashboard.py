import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import random

from utils.visualization import create_alert_dashboard
from utils.data_processor import get_climate_data_for_location

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="GAIA-∞ | Environmental Alerts",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Page title
st.title("🚨 Environmental Alerts")
st.markdown("""
Monitor and track critical environmental events worldwide. This module provides real-time
alerts about extreme weather, ecosystem changes, and climate anomalies.
""")

# Sidebar options
st.sidebar.header("Alert Options")

alert_types = st.sidebar.multiselect(
    "Alert Types",
    options=["Extreme Weather", "Sea Level", "Temperature Anomalies", "Ecosystem Changes", "Air Quality"],
    default=["Extreme Weather", "Temperature Anomalies"]
)

alert_regions = st.sidebar.multiselect(
    "Filter by Region",
    options=["Global", "North America", "South America", "Europe", "Africa", "Asia", "Australia/Oceania", "Arctic", "Antarctic"],
    default=["Global"]
)

alert_severity = st.sidebar.multiselect(
    "Alert Severity",
    options=["Low", "Medium", "High", "Critical"],
    default=["Medium", "High", "Critical"]
)

time_range = st.sidebar.radio(
    "Time Range",
    options=["Active Alerts", "Last 24 Hours", "Last Week", "Last Month"],
    index=0
)

# Generate sample alerts based on user filters
def generate_alerts(types, regions, severities, time_range):
    """
    Generate environmental alerts based on selected filters.
    
    In a real application, this would query an API or database for actual alerts.
    """
    alerts = []
    
    current_time = datetime.now()
    
    # Define time ranges in hours
    time_ranges = {
        "Active Alerts": 24,
        "Last 24 Hours": 24,
        "Last Week": 168,
        "Last Month": 720
    }
    
    # Convert severity strings to values for filtering
    severity_map = {
        "Low": "low",
        "Medium": "medium",
        "High": "high",
        "Critical": "critical"
    }
    severity_values = [severity_map[s] for s in severities]
    
    # Sample alert templates
    alert_templates = {
        "Extreme Weather": [
            {
                "title": "Severe Rainfall and Flooding Risk",
                "description": "Heavy rainfall exceeding 200mm expected over the next 48 hours, creating significant flood risk in low-lying areas.",
                "severity": "high"
            },
            {
                "title": "Extreme Heat Wave Warning",
                "description": "Temperatures expected to exceed historical averages by 5-8°C for the next 3-5 days. Vulnerable populations at risk.",
                "severity": "critical"
            },
            {
                "title": "Tropical Cyclone Formation",
                "description": "Tropical depression strengthening with potential to develop into category 3-4 cyclone within 72 hours.",
                "severity": "high"
            },
            {
                "title": "Severe Drought Conditions",
                "description": "Persistent precipitation deficit leading to severe drought conditions. Water restrictions advised.",
                "severity": "medium"
            }
        ],
        "Sea Level": [
            {
                "title": "Coastal Flooding Alert",
                "description": "Higher than normal tides combined with storm surge creating coastal flooding risk for the next 24-48 hours.",
                "severity": "high"
            },
            {
                "title": "Sea Level Anomaly Detected",
                "description": "Satellite measurements show sea level 15cm above seasonal average, potentially impacting coastal areas.",
                "severity": "medium"
            }
        ],
        "Temperature Anomalies": [
            {
                "title": "Record High Temperature",
                "description": "Temperature exceeding historical record by 2-4°C, indicating significant climate anomaly.",
                "severity": "high"
            },
            {
                "title": "Marine Heat Wave",
                "description": "Ocean temperatures 3-5°C above average, posing risk to marine ecosystems and coral reefs.",
                "severity": "critical"
            },
            {
                "title": "Persistent Temperature Anomaly",
                "description": "Region experiencing temperatures >2°C above average for 10+ consecutive days.",
                "severity": "medium"
            }
        ],
        "Ecosystem Changes": [
            {
                "title": "Coral Bleaching Event",
                "description": "Satellite and field observations indicate mass coral bleaching event due to elevated ocean temperatures.",
                "severity": "critical"
            },
            {
                "title": "Forest Dieback Detected",
                "description": "Satellite imagery shows significant vegetation loss in forest region, indicating potential ecosystem stress.",
                "severity": "high"
            },
            {
                "title": "Early Spring Phenology",
                "description": "Plant growth and flowering occurring 10-15 days earlier than historical average, indicating climate shift.",
                "severity": "low"
            }
        ],
        "Air Quality": [
            {
                "title": "Hazardous Air Quality Levels",
                "description": "PM2.5 concentrations exceeding 150 µg/m³, posing significant health risks. Limiting outdoor activity advised.",
                "severity": "critical"
            },
            {
                "title": "Elevated Ozone Levels",
                "description": "Ground-level ozone exceeding health standards. Those with respiratory conditions should take precautions.",
                "severity": "high"
            }
        ]
    }
    
    # Region-specific locations
    region_locations = {
        "Global": ["Global", "Multiple Regions", "Transboundary"],
        "North America": ["California, USA", "Gulf Coast, USA", "Great Lakes Region", "Colorado River Basin", "Pacific Northwest, USA"],
        "South America": ["Amazon Basin", "Andean Region", "Pantanal Wetlands", "Patagonia", "Rio de la Plata Basin"],
        "Europe": ["Mediterranean Coast", "Alpine Region", "North Sea", "Iberian Peninsula", "Danube River Basin"],
        "Africa": ["Sahel Region", "East African Highlands", "Niger Delta", "Mozambique Coast", "Cape Region, South Africa"],
        "Asia": ["Ganges-Brahmaputra Delta", "Mekong River Basin", "Yangtze River Basin", "Western Ghats, India", "Coral Triangle"],
        "Australia/Oceania": ["Great Barrier Reef", "Murray-Darling Basin", "Papua New Guinea Highlands", "New Zealand Alps", "Pacific Island Nations"],
        "Arctic": ["Greenland Ice Sheet", "Northern Alaska", "Svalbard", "Canadian Arctic Archipelago", "Siberian Arctic"],
        "Antarctic": ["Antarctic Peninsula", "West Antarctic Ice Sheet", "Ross Ice Shelf", "Weddell Sea", "East Antarctic Ice Sheet"]
    }
    
    # Create alerts based on selected filters
    for alert_type in types:
        if alert_type in alert_templates:
            templates = alert_templates[alert_type]
            
            for region in regions:
                # Skip if not relevant combination (e.g., Sea Level alerts for non-coastal regions)
                if region == "Antarctic" and alert_type == "Extreme Heat Wave Warning":
                    continue
                
                # Get locations for this region
                locations = region_locations.get(region, ["Unknown Location"])
                
                # Create 1-3 alerts for this type and region
                for _ in range(random.randint(1, 3)):
                    template = random.choice(templates)
                    
                    # Only include if severity matches filter
                    if template["severity"] not in severity_values:
                        continue
                    
                    # Random time within the selected range
                    hours_ago = random.uniform(0, time_ranges[time_range])
                    alert_time = current_time - timedelta(hours=hours_ago)
                    
                    # Create the alert
                    alert = {
                        "title": template["title"],
                        "description": template["description"],
                        "severity": template["severity"],
                        "type": alert_type,
                        "region": region,
                        "location": random.choice(locations),
                        "time": alert_time.strftime("%Y-%m-%d %H:%M"),
                        "coordinates": get_random_coordinates(region)
                    }
                    
                    alerts.append(alert)
    
    return alerts

def get_random_coordinates(region):
    """Generate random but plausible coordinates for a region"""
    region_bounds = {
        "Global": (-90, 90, -180, 180),  # Full Earth
        "North America": (25, 70, -170, -50),
        "South America": (-55, 15, -80, -35),
        "Europe": (35, 70, -10, 40),
        "Africa": (-35, 37, -20, 50),
        "Asia": (0, 70, 40, 150),
        "Australia/Oceania": (-50, 0, 110, 180),
        "Arctic": (66, 90, -180, 180),
        "Antarctic": (-90, -60, -180, 180)
    }
    
    bounds = region_bounds.get(region, (-90, 90, -180, 180))
    lat = random.uniform(bounds[0], bounds[1])
    lon = random.uniform(bounds[2], bounds[3])
    
    return (lat, lon)

# Generate alerts based on filters
alerts = generate_alerts(alert_types, alert_regions, alert_severity, time_range)

# Sort alerts by time (most recent first) and severity
alerts.sort(key=lambda x: (x["time"], x["severity"] != "critical", x["severity"] != "high"), reverse=True)

# Main dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Active Environmental Alerts")
    
    if not alerts:
        st.info("No alerts match your current filters.")
    else:
        # Display alert count
        st.markdown(f"**{len(alerts)} alerts** match your current filters.")
        
        # Create alert dashboard
        create_alert_dashboard(alerts)
        
        # Option to enable notifications
        st.markdown("---")
        st.subheader("Alert Notifications")
        
        notification_col1, notification_col2 = st.columns(2)
        
        with notification_col1:
            st.markdown("**Receive Alert Notifications**")
            email_notifications = st.checkbox("Email Notifications")
            sms_notifications = st.checkbox("SMS Notifications")
            app_notifications = st.checkbox("Mobile App Notifications")
        
        with notification_col2:
            if email_notifications or sms_notifications or app_notifications:
                if email_notifications:
                    st.text_input("Email Address", placeholder="your@email.com")
                if sms_notifications:
                    st.text_input("Phone Number", placeholder="+1 (555) 555-5555")
                
                notification_button = st.button("Set Up Notifications")
                
                if notification_button:
                    st.success("Notification preferences saved! You will receive alerts based on your current filter settings.")

with col2:
    st.subheader("Alert Map")
    
    if not alerts:
        st.info("No alerts to display on map.")
    else:
        # Create a map centered on the first alert
        center_lat, center_lon = 0, 0
        if alerts:
            center_lat, center_lon = alerts[0]["coordinates"]
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=2, tiles="CartoDB positron")
        
        # Add markers for each alert
        for alert in alerts:
            lat, lon = alert["coordinates"]
            
            # Choose marker color based on severity
            if alert["severity"] == "critical":
                color = "red"
            elif alert["severity"] == "high":
                color = "orange"
            elif alert["severity"] == "medium":
                color = "yellow"
            else:
                color = "blue"
            
            # Create popup content
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{alert['title']}</h4>
                <p><strong>Location:</strong> {alert['location']}</p>
                <p><strong>Type:</strong> {alert['type']}</p>
                <p><strong>Severity:</strong> {alert['severity'].title()}</p>
                <p><strong>Time:</strong> {alert['time']}</p>
            </div>
            """
            
            # Add marker
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)
        
        # Display the map
        folium_static(m)
    
    # Alert statistics
    st.subheader("Alert Statistics")
    
    if not alerts:
        st.info("No data available for statistics.")
    else:
        # Count alerts by type
        alert_counts = {}
        for alert in alerts:
            alert_type = alert["type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        # Create a bar chart
        alert_df = pd.DataFrame({
            "Alert Type": list(alert_counts.keys()),
            "Count": list(alert_counts.values())
        })
        
        fig = px.bar(
            alert_df,
            x="Alert Type",
            y="Count",
            title="Alerts by Type",
            color="Count",
            color_continuous_scale=["blue", "yellow", "orange", "red"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Count by severity
        severity_counts = {}
        for alert in alerts:
            severity = alert["severity"].title()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Create a pie chart
        severity_labels = list(severity_counts.keys())
        severity_values = list(severity_counts.values())
        
        fig = px.pie(
            values=severity_values,
            names=severity_labels,
            title="Alerts by Severity",
            color=severity_labels,
            color_discrete_map={
                "Critical": "red",
                "High": "orange",
                "Medium": "yellow",
                "Low": "blue"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Alert details section
st.subheader("Detailed Alert Information")

if not alerts:
    st.info("No alerts to display.")
else:
    # Create tabs for different alert types
    alert_type_tabs = {}
    
    for alert_type in alert_types:
        alert_type_tabs[alert_type] = []
    
    # Group alerts by type
    for alert in alerts:
        if alert["type"] in alert_type_tabs:
            alert_type_tabs[alert["type"]].append(alert)
    
    # Create tabs only for types that have alerts
    tabs = []
    tab_names = []
    
    for alert_type, alert_list in alert_type_tabs.items():
        if alert_list:
            tabs.append(alert_list)
            tab_names.append(alert_type)
    
    if tabs:
        # Create the tabs
        created_tabs = st.tabs(tab_names)
        
        # Display alerts in each tab
        for i, tab in enumerate(created_tabs):
            with tab:
                for alert in tabs[i]:
                    with st.expander(f"{alert['title']} - {alert['location']} ({alert['time']})"):
                        st.markdown(f"**Type:** {alert['type']}")
                        st.markdown(f"**Severity:** {alert['severity'].title()}")
                        st.markdown(f"**Location:** {alert['location']} ({alert['region']})")
                        st.markdown(f"**Time:** {alert['time']}")
                        st.markdown(f"**Description:** {alert['description']}")
                        
                        # Get some climate data for the location
                        lat, lon = alert["coordinates"]
                        location_data = get_climate_data_for_location(lat, lon)
                        
                        if location_data:
                            st.markdown("### Local Climate Context")
                            
                            context_col1, context_col2 = st.columns(2)
                            
                            with context_col1:
                                st.metric(
                                    "Local Temperature",
                                    f"{location_data.get('current_temperature', 'N/A')}°C",
                                    f"{location_data.get('temperature_anomaly', 'N/A')}°C",
                                    delta_color="inverse"
                                )
                            
                            with context_col2:
                                if alert["type"] == "Sea Level":
                                    st.metric(
                                        "Sea Level Risk",
                                        f"{location_data.get('sea_level_risk', 'N/A')}/10"
                                    )
                                elif alert["type"] == "Extreme Weather":
                                    st.metric(
                                        "Precipitation",
                                        f"{location_data.get('annual_precipitation', 'N/A')} mm"
                                    )
                                else:
                                    st.metric(
                                        "Drought Risk",
                                        f"{location_data.get('drought_risk', 'N/A')}/10"
                                    )
                        
                        # Add response guidance based on alert type and severity
                        st.markdown("### Response Guidance")
                        
                        if alert["severity"] == "critical":
                            st.error("""
                            **Critical alert requires immediate action:**
                            - Activate emergency response protocols
                            - Implement evacuation plans if necessary
                            - Deploy immediate resources to affected areas
                            - Continuous monitoring and regular updates
                            """)
                        elif alert["severity"] == "high":
                            st.warning("""
                            **High severity alert requires prompt attention:**
                            - Prepare emergency response resources
                            - Notify relevant agencies and organizations
                            - Implement precautionary measures
                            - Increase monitoring frequency
                            """)
                        else:
                            st.info("""
                            **Monitoring and preparedness recommended:**
                            - Increase awareness and monitoring
                            - Review emergency plans
                            - Prepare resources for potential escalation
                            - Continue normal operations with heightened vigilance
                            """)

# Historical alerts section
st.markdown("---")
st.subheader("Historical Alert Trends")

# Create sample historical data
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
current_month = datetime.now().month

# Generate sample historical data
historical_data = []

for i in range(12):
    month_idx = (current_month - 12 + i) % 12
    month_name = months[month_idx]
    
    # More alerts in recent months and seasonal patterns
    extreme_weather = int(10 + random.randint(-3, 8) + (i / 2))
    temperature_anomalies = int(8 + random.randint(-2, 5) + (i / 3))
    sea_level = int(5 + random.randint(-1, 3) + (i / 4))
    ecosystem = int(7 + random.randint(-2, 4) + (i / 3))
    air_quality = int(6 + random.randint(-2, 6) + (i / 5))
    
    historical_data.append({
        "Month": month_name,
        "Extreme Weather": extreme_weather,
        "Temperature Anomalies": temperature_anomalies,
        "Sea Level": sea_level,
        "Ecosystem Changes": ecosystem,
        "Air Quality": air_quality
    })

historical_df = pd.DataFrame(historical_data)

# Create a stacked area chart
fig = go.Figure()

for column in ["Extreme Weather", "Temperature Anomalies", "Sea Level", "Ecosystem Changes", "Air Quality"]:
    if column in alert_types:
        fig.add_trace(go.Scatter(
            x=historical_df["Month"],
            y=historical_df[column],
            mode='lines',
            stackgroup='one',
            name=column,
            hovertemplate="%{y} alerts"
        ))

fig.update_layout(
    title="12-Month Alert History",
    xaxis_title="Month",
    yaxis_title="Number of Alerts",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Add explanation of alert system
st.markdown("---")
st.subheader("About the Environmental Alert System")
st.markdown("""
The GAIA-∞ Environmental Alert System monitors real-time data from multiple sources to detect
and notify users about significant environmental events and anomalies.

**Alert Sources:**
- Satellite remote sensing data
- Ground-based monitoring stations
- Ocean buoy networks
- Weather station networks
- Climate model projections
- Ecosystem monitoring systems

**Alert Severity Levels:**
- **Critical**: Extreme events requiring immediate action
- **High**: Significant events with potential for serious impacts
- **Medium**: Moderate events requiring monitoring and preparation
- **Low**: Minor events with limited impacts

For emergency response, please always refer to official government alerts
and directions from local emergency management agencies.
""")

# Footer
st.markdown("---")
st.caption("""
GAIA-∞ Environmental Alert System | Real-time monitoring and notification of climate events
""")
