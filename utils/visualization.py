import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import json

def plot_global_temperature_trend(data):
    """
    Plot the global temperature anomaly trend.
    
    Args:
        data: DataFrame with temperature anomaly data
    """
    if data.empty:
        st.error("No temperature data available.")
        return
    
    # Create a Plotly figure
    fig = px.line(
        data, 
        x='year', 
        y='anomaly', 
        title='Global Temperature Anomaly (°C) Relative to 1880-1900 Average',
        labels={'anomaly': 'Temperature Anomaly (°C)', 'year': 'Year'}
    )
    
    # Add a horizontal line at 1.5°C (Paris Agreement target)
    fig.add_shape(
        type="line",
        x0=data['year'].min(),
        y0=1.5,
        x1=data['year'].max(),
        y1=1.5,
        line=dict(color="red", width=2, dash="dash"),
    )
    
    # Add annotation for the Paris Agreement line
    fig.add_annotation(
        x=data['year'].min() + 5,
        y=1.5,
        text="Paris Agreement Target (1.5°C)",
        showarrow=False,
        yshift=10
    )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    # Add a 10-year moving average
    if len(data) > 10:
        data['moving_avg'] = data['anomaly'].rolling(window=10).mean()
        fig.add_scatter(
            x=data['year'], 
            y=data['moving_avg'], 
            mode='lines', 
            name='10-Year Moving Average',
            line=dict(color='orange', width=3)
        )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def plot_co2_concentration(data):
    """
    Plot the CO2 concentration trend.
    
    Args:
        data: DataFrame with CO2 concentration data
    """
    if data.empty:
        st.error("No CO2 concentration data available.")
        return
    
    # Create a Plotly figure
    fig = px.line(
        data, 
        x='year', 
        y='mean', 
        title='Atmospheric CO₂ Concentration (ppm)',
        labels={'mean': 'CO₂ Concentration (ppm)', 'year': 'Year'}
    )
    
    # Add a horizontal line at 350 ppm (often cited as a "safe" level)
    fig.add_shape(
        type="line",
        x0=data['year'].min(),
        y0=350,
        x1=data['year'].max(),
        y1=350,
        line=dict(color="green", width=2, dash="dash"),
    )
    
    # Add annotation for the 350 ppm line
    fig.add_annotation(
        x=data['year'].min() + 5,
        y=350,
        text="350 ppm (Safe Level)",
        showarrow=False,
        yshift=10
    )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def plot_sea_level_rise(data):
    """
    Plot the sea level rise trend.
    
    Args:
        data: DataFrame with sea level data
    """
    if data.empty:
        st.error("No sea level data available.")
        return
    
    # Create a Plotly figure
    fig = px.line(
        data, 
        x='year', 
        y='gmsl', 
        title='Global Mean Sea Level Rise (mm)',
        labels={'gmsl': 'Sea Level Rise (mm)', 'year': 'Year'}
    )
    
    # Add error bars if uncertainty is available
    if 'gmsl_uncertainty' in data.columns:
        fig.add_scatter(
            x=data['year'],
            y=data['gmsl'] + data['gmsl_uncertainty'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        )
        fig.add_scatter(
            x=data['year'],
            y=data['gmsl'] - data['gmsl_uncertainty'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(68, 149, 209, 0.3)',
            name='Uncertainty Range'
        )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def plot_arctic_sea_ice(data):
    """
    Plot the Arctic sea ice extent trend.
    
    Args:
        data: DataFrame with Arctic sea ice extent data
    """
    if data.empty:
        st.error("No Arctic sea ice data available.")
        return
    
    # Create a Plotly figure
    fig = px.line(
        data, 
        x='year', 
        y='ice_extent', 
        title='Arctic Sea Ice Extent (million sq km)',
        labels={'ice_extent': 'Sea Ice Extent (million sq km)', 'year': 'Year'}
    )
    
    # Add trend line
    # Calculate linear regression
    x = data['year']
    y = data['ice_extent']
    coeffs = np.polyfit(x, y, 1)
    trend_line = np.poly1d(coeffs)
    
    # Add trend line to the plot
    fig.add_scatter(
        x=data['year'],
        y=trend_line(data['year']),
        mode='lines',
        name=f'Trend: {coeffs[0]:.2f} million sq km per year',
        line=dict(color='red', dash='dash')
    )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def create_climate_risk_map(risk_data):
    """
    Create a map visualization of climate risks.
    
    Args:
        risk_data: DataFrame with latitude, longitude, and risk values
    
    Returns:
        Folium map object
    """
    # Create a base map centered on the equator
    m = folium.Map(location=[0, 0], zoom_start=2, tiles='CartoDB positron')
    
    # Check if we have valid data
    if risk_data.empty:
        return m
    
    # Extract data for the heatmap
    heat_data = [[row['lat'], row['lon'], row['risk']] for _, row in risk_data.iterrows()]
    
    # Create a heatmap layer
    HeatMap(
        heat_data,
        radius=15,
        blur=10,
        gradient={
            0.0: 'blue',
            0.25: 'green',
            0.5: 'yellow',
            0.75: 'orange',
            1.0: 'red'
        }
    ).add_to(m)
    
    # Add markers for high-risk areas (risk > 7)
    high_risk = risk_data[risk_data['risk'] > 7]
    for _, row in high_risk.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            color='black',
            fill=True,
            fill_color='red',
            fill_opacity=0.6,
            popup=f"Risk: {row['risk']}<br>"
                  f"Temperature Risk: {row['temperature_risk']}<br>"
                  f"Sea Level Risk: {row['sea_level_risk']}<br>"
                  f"Drought Risk: {row['drought_risk']}"
        ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                border:2px solid grey; z-index:9999; 
                background-color:white;
                padding: 10px;
                border-radius: 5px;
                ">
    <div style="font-size: 16px;"><b>Climate Risk Index</b></div>
    <div style="display: flex; align-items: center;">
        <div style="background-color: blue; width: 20px; height: 20px; margin-right: 5px;"></div>
        <div>Low Risk (0-2)</div>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="background-color: green; width: 20px; height: 20px; margin-right: 5px;"></div>
        <div>Moderate Risk (2-4)</div>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="background-color: yellow; width: 20px; height: 20px; margin-right: 5px;"></div>
        <div>Medium Risk (4-6)</div>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="background-color: orange; width: 20px; height: 20px; margin-right: 5px;"></div>
        <div>High Risk (6-8)</div>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="background-color: red; width: 20px; height: 20px; margin-right: 5px;"></div>
        <div>Critical Risk (8-10)</div>
    </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def plot_simulation_results(results, title="Climate Simulation Results"):
    """
    Plot the results of a climate simulation.
    
    Args:
        results: DataFrame with simulation results
        title: Title for the plot
    """
    if results.empty:
        st.error("No simulation results available.")
        return
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "CO₂ Concentration", "Sea Level Rise", "Arctic Sea Ice"])
    
    with tab1:
        fig = px.line(
            results, 
            x='year', 
            y='temperature', 
            title=f'Projected Global Temperature (°C)',
            labels={'temperature': 'Temperature (°C)', 'year': 'Year'}
        )
        
        # Add a horizontal line at 1.5°C above pre-industrial
        preindustrial_temp = DEFAULT_PARAMS['initial_temperature'] - 0.8  # Approximate pre-industrial temperature
        paris_target = preindustrial_temp + 1.5
        
        fig.add_shape(
            type="line",
            x0=results['year'].min(),
            y0=paris_target,
            x1=results['year'].max(),
            y1=paris_target,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=results['year'].min() + 5,
            y=paris_target,
            text="Paris Agreement Target (1.5°C above pre-industrial)",
            showarrow=False,
            yshift=10
        )
        
        # Customize layout
        fig.update_layout(
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(
            results, 
            x='year', 
            y='co2', 
            title=f'Projected CO₂ Concentration (ppm)',
            labels={'co2': 'CO₂ (ppm)', 'year': 'Year'}
        )
        
        # Add a horizontal line at 350 ppm (often cited as a "safe" level)
        fig.add_shape(
            type="line",
            x0=results['year'].min(),
            y0=350,
            x1=results['year'].max(),
            y1=350,
            line=dict(color="green", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=results['year'].min() + 5,
            y=350,
            text="350 ppm (Safe Level)",
            showarrow=False,
            yshift=10
        )
        
        # Customize layout
        fig.update_layout(
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(
            results, 
            x='year', 
            y='sea_level_rise', 
            title=f'Projected Sea Level Rise (cm)',
            labels={'sea_level_rise': 'Sea Level Rise (cm)', 'year': 'Year'}
        )
        
        # Customize layout
        fig.update_layout(
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = px.line(
            results, 
            x='year', 
            y='arctic_ice', 
            title=f'Projected Arctic Sea Ice Extent (million sq km)',
            labels={'arctic_ice': 'Sea Ice Extent (million sq km)', 'year': 'Year'}
        )
        
        # Highlight ice-free summer threshold
        fig.add_shape(
            type="line",
            x0=results['year'].min(),
            y0=1.0,
            x1=results['year'].max(),
            y1=1.0,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=results['year'].min() + 5,
            y=1.0,
            text="Ice-free summer threshold",
            showarrow=False,
            yshift=10
        )
        
        # Customize layout
        fig.update_layout(
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def plot_comparative_simulations(scenario_results, metric='temperature', title="Scenario Comparison"):
    """
    Plot comparative results of multiple climate scenarios.
    
    Args:
        scenario_results: Dictionary of DataFrames with simulation results for different scenarios
        metric: The metric to compare ('temperature', 'co2', 'sea_level_rise', or 'arctic_ice')
        title: Title for the plot
    """
    if not scenario_results:
        st.error("No simulation results available for comparison.")
        return
    
    # Define labels for the metrics
    metric_labels = {
        'temperature': 'Temperature (°C)',
        'co2': 'CO₂ Concentration (ppm)',
        'sea_level_rise': 'Sea Level Rise (cm)',
        'arctic_ice': 'Arctic Sea Ice Extent (million sq km)',
        'extreme_weather_index': 'Extreme Weather Index (0-100)'
    }
    
    # Create the plot
    fig = go.Figure()
    
    # Add traces for each scenario
    for scenario_name, results in scenario_results.items():
        fig.add_trace(go.Scatter(
            x=results['year'],
            y=results[metric],
            mode='lines',
            name=scenario_name.replace('_', ' ').title()
        ))
    
    # Add special markers for intervention points
    for scenario_name, results in scenario_results.items():
        if 'intervention' in results.columns:
            intervention_points = results[results['intervention'] == True]
            if not intervention_points.empty:
                fig.add_trace(go.Scatter(
                    x=intervention_points['year'],
                    y=intervention_points[metric],
                    mode='markers',
                    marker=dict(size=10, color='black', symbol='star'),
                    name=f'{scenario_name.title()} Intervention',
                    hovertemplate='Intervention at %{x}: %{y:.2f}'
                ))
    
    # Add critical thresholds if applicable
    if metric == 'temperature':
        # Paris Agreement threshold
        preindustrial_temp = DEFAULT_PARAMS['initial_temperature'] - 0.8  # Approximate pre-industrial temperature
        paris_target = preindustrial_temp + 1.5
        
        fig.add_shape(
            type="line",
            x0=min(results['year'].min() for results in scenario_results.values()),
            y0=paris_target,
            x1=max(results['year'].max() for results in scenario_results.values()),
            y1=paris_target,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=min(results['year'].min() for results in scenario_results.values()) + 5,
            y=paris_target,
            text="Paris Agreement Target (1.5°C above pre-industrial)",
            showarrow=False,
            yshift=10
        )
    
    elif metric == 'co2':
        # Safe CO2 level
        fig.add_shape(
            type="line",
            x0=min(results['year'].min() for results in scenario_results.values()),
            y0=350,
            x1=max(results['year'].max() for results in scenario_results.values()),
            y1=350,
            line=dict(color="green", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=min(results['year'].min() for results in scenario_results.values()) + 5,
            y=350,
            text="350 ppm (Safe Level)",
            showarrow=False,
            yshift=10
        )
    
    elif metric == 'arctic_ice':
        # Ice-free summer threshold
        fig.add_shape(
            type="line",
            x0=min(results['year'].min() for results in scenario_results.values()),
            y0=1.0,
            x1=max(results['year'].max() for results in scenario_results.values()),
            y1=1.0,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=min(results['year'].min() for results in scenario_results.values()) + 5,
            y=1.0,
            text="Ice-free summer threshold",
            showarrow=False,
            yshift=10
        )
    
    # Set title and labels
    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title=metric_labels.get(metric, metric),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def create_location_climate_dashboard(location_data, title="Local Climate Impact Dashboard"):
    """
    Create a dashboard for climate impacts at a specific location.
    
    Args:
        location_data: Dictionary with climate data for the location
        title: Title for the dashboard
    """
    if not location_data:
        st.error("No location data available.")
        return
    
    st.subheader(title)
    
    # Create metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Temperature", 
            f"{location_data.get('current_temperature', 'N/A')}°C", 
            f"{location_data.get('temperature_anomaly', 'N/A')}°C",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Annual Precipitation", 
            f"{location_data.get('annual_precipitation', 'N/A')} mm"
        )
    
    with col3:
        st.metric(
            "Sea Level Rise Risk", 
            f"{location_data.get('sea_level_risk', 'N/A')}/10"
        )
    
    # Create risk gauge charts
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    
    with risk_col1:
        create_gauge_chart("Sea Level Risk", location_data.get('sea_level_risk', 0))
    
    with risk_col2:
        create_gauge_chart("Biodiversity Risk", location_data.get('biodiversity_risk', 0))
    
    with risk_col3:
        create_gauge_chart("Drought Risk", location_data.get('drought_risk', 0))
    
    # Plot historical data if available
    if 'historical_data' in location_data and not location_data['historical_data'].empty:
        st.subheader("Historical Climate Trends")
        
        hist_tab1, hist_tab2 = st.tabs(["Temperature", "Precipitation"])
        
        with hist_tab1:
            fig = px.line(
                location_data['historical_data'], 
                x='year', 
                y='temperature', 
                title='Historical Temperature (°C)',
                labels={'temperature': 'Temperature (°C)', 'year': 'Year'}
            )
            
            # Add trend line
            x = location_data['historical_data']['year']
            y = location_data['historical_data']['temperature']
            coeffs = np.polyfit(x, y, 1)
            trend_line = np.poly1d(coeffs)
            
            fig.add_scatter(
                x=x,
                y=trend_line(x),
                mode='lines',
                name=f'Trend: {coeffs[0]:.3f}°C/year',
                line=dict(color='red', dash='dash')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with hist_tab2:
            fig = px.line(
                location_data['historical_data'], 
                x='year', 
                y='precipitation', 
                title='Historical Precipitation (mm)',
                labels={'precipitation': 'Precipitation (mm)', 'year': 'Year'}
            )
            
            # Add trend line
            x = location_data['historical_data']['year']
            y = location_data['historical_data']['precipitation']
            coeffs = np.polyfit(x, y, 1)
            trend_line = np.poly1d(coeffs)
            
            fig.add_scatter(
                x=x,
                y=trend_line(x),
                mode='lines',
                name=f'Trend: {coeffs[0]:.1f} mm/year',
                line=dict(color='blue', dash='dash')
            )
            
            st.plotly_chart(fig, use_container_width=True)

def create_gauge_chart(title, value, min_val=0, max_val=10):
    """
    Create a gauge chart for risk visualization.
    
    Args:
        title: Title for the gauge
        value: Value to display (0-10)
        min_val: Minimum value
        max_val: Maximum value
    """
    # Define colors for risk levels
    colors = {
        'low': "green",
        'medium': "yellow",
        'high': "orange",
        'critical': "red"
    }
    
    # Determine color based on value
    if value < 3:
        color = colors['low']
    elif value < 5:
        color = colors['medium']
    elif value < 7:
        color = colors['high']
    else:
        color = colors['critical']
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 3], 'color': 'rgba(0, 128, 0, 0.2)'},
                {'range': [3, 5], 'color': 'rgba(255, 255, 0, 0.2)'},
                {'range': [5, 7], 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range': [7, 10], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    # Customize layout
    fig.update_layout(
        height=200,
        margin=dict(l=30, r=30, t=30, b=30)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def create_alert_dashboard(alerts):
    """
    Create a dashboard for environmental alerts.
    
    Args:
        alerts: List of alert dictionaries
    """
    if not alerts:
        st.info("No active environmental alerts at this time.")
        return
    
    # Sort alerts by severity (highest first)
    sorted_alerts = sorted(alerts, key=lambda x: x.get('severity', 0), reverse=True)
    
    # Display alerts
    for alert in sorted_alerts:
        # Determine alert color based on severity
        if alert.get('severity') == 'critical':
            alert_color = "red"
        elif alert.get('severity') == 'high':
            alert_color = "orange"
        elif alert.get('severity') == 'medium':
            alert_color = "yellow"
        else:
            alert_color = "blue"
        
        # Create alert box
        st.markdown(
            f"""
            <div style="border-left: 5px solid {alert_color}; padding: 10px; margin-bottom: 10px; background-color: rgba(0,0,0,0.05);">
                <h4 style="margin-top: 0;">{alert.get('title', 'Alert')}</h4>
                <p><strong>Location:</strong> {alert.get('location', 'Global')}</p>
                <p><strong>Time:</strong> {alert.get('time', 'N/A')}</p>
                <p>{alert.get('description', '')}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Import necessary climate simulation constants
from utils.climate_simulator import DEFAULT_PARAMS
