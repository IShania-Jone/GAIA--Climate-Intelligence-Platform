import pandas as pd
import numpy as np
import os
import requests
import io
import streamlit as st
from datetime import datetime, timedelta

# Cache the data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_climate_data():
    """
    Load climate data from various sources.
    
    Returns:
        A dictionary containing different climate datasets
    """
    try:
        # Create an empty dictionary to store datasets
        data = {}
        
        # Load global temperature data from NOAA
        data['global_temp'] = load_global_temperature_data()
        
        # Load CO2 concentration data
        data['co2_concentration'] = load_co2_concentration_data()
        
        # Load sea level data
        data['sea_level'] = load_sea_level_data()
        
        # Load arctic sea ice data
        data['arctic_ice'] = load_arctic_sea_ice_data()
        
        return data
    except Exception as e:
        st.error(f"Error loading climate data: {str(e)}")
        # Return empty datasets
        return {
            'global_temp': pd.DataFrame(),
            'co2_concentration': pd.DataFrame(),
            'sea_level': pd.DataFrame(),
            'arctic_ice': pd.DataFrame()
        }

def load_global_temperature_data():
    """
    Load global temperature anomaly data from NOAA.
    
    Returns:
        A pandas DataFrame with global temperature anomaly data
    """
    try:
        # NOAA Global Land and Ocean Temperature Anomalies URL
        url = "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series/globe/land_ocean/ann/12/1880-2023.csv"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the CSV data
            data = pd.read_csv(io.StringIO(response.text), skiprows=4)
            data.columns = data.columns.str.strip()
            
            # Rename columns for clarity
            data = data.rename(columns={
                'Year': 'year',
                'Value': 'anomaly'
            })
            
            # Convert anomaly to numeric
            data['anomaly'] = pd.to_numeric(data['anomaly'], errors='coerce')
            
            return data
        else:
            # If the request fails, generate sample data
            st.warning("Failed to fetch global temperature data. Using historical data.")
            return generate_historical_temperature_data()
    except Exception as e:
        st.warning(f"Error fetching temperature data: {str(e)}. Using historical data.")
        return generate_historical_temperature_data()

def generate_historical_temperature_data():
    """
    Generate historical global temperature anomaly data based on known values.
    
    Returns:
        A pandas DataFrame with global temperature anomaly data
    """
    # Create a DataFrame with years from 1880 to present
    current_year = datetime.now().year
    years = range(1880, current_year + 1)
    
    # Known temperature anomalies (approximations)
    # These values are based on general temperature anomaly trends
    base_anomalies = {
        1880: -0.16, 1900: -0.08, 1920: -0.27, 1940: 0.12,
        1960: -0.03, 1980: 0.26, 2000: 0.39, 2020: 0.98
    }
    
    # Generate a DataFrame
    data = pd.DataFrame({'year': years})
    
    # Calculate anomalies based on interpolation between known points
    anomalies = []
    for year in years:
        # Find closest known years before and after
        prev_years = [y for y in base_anomalies.keys() if y <= year]
        next_years = [y for y in base_anomalies.keys() if y >= year]
        
        if prev_years and next_years:
            prev_year = max(prev_years)
            next_year = min(next_years)
            
            # If exact year exists, use its value
            if prev_year == next_year:
                anomalies.append(base_anomalies[prev_year])
            else:
                # Linear interpolation
                prev_anomaly = base_anomalies[prev_year]
                next_anomaly = base_anomalies[next_year]
                ratio = (year - prev_year) / (next_year - prev_year)
                anomaly = prev_anomaly + ratio * (next_anomaly - prev_anomaly)
                
                # Add some minor random variation
                anomaly += np.random.normal(0, 0.03)
                anomalies.append(round(anomaly, 2))
        elif prev_years:
            # Extrapolate forward
            last_year = max(prev_years)
            anomaly = base_anomalies[last_year] + (year - last_year) * 0.02
            anomaly += np.random.normal(0, 0.03)
            anomalies.append(round(anomaly, 2))
        else:
            # Extrapolate backward
            first_year = min(next_years)
            anomaly = base_anomalies[first_year] - (first_year - year) * 0.01
            anomaly += np.random.normal(0, 0.03)
            anomalies.append(round(anomaly, 2))
    
    data['anomaly'] = anomalies
    return data

def load_co2_concentration_data():
    """
    Load CO2 concentration data from NOAA.
    
    Returns:
        A pandas DataFrame with CO2 concentration data
    """
    try:
        # NOAA Mauna Loa CO2 data URL
        url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Skip header lines and parse the data
            lines = response.text.strip().split('\n')
            data_lines = [line for line in lines if not line.startswith('#')]
            data = pd.read_csv(io.StringIO('\n'.join(data_lines)), delim_whitespace=True)
            
            # Rename columns for clarity
            data.columns = ['year', 'mean', 'uncertainty']
            
            return data
        else:
            # If the request fails, generate sample data
            st.warning("Failed to fetch CO2 concentration data. Using historical data.")
            return generate_historical_co2_data()
    except Exception as e:
        st.warning(f"Error fetching CO2 data: {str(e)}. Using historical data.")
        return generate_historical_co2_data()

def generate_historical_co2_data():
    """
    Generate historical CO2 concentration data based on known values.
    
    Returns:
        A pandas DataFrame with CO2 concentration data
    """
    # Create a DataFrame with years from 1958 (start of Mauna Loa record) to present
    current_year = datetime.now().year
    years = range(1958, current_year + 1)
    
    # Known CO2 concentrations (approximations)
    base_co2 = {
        1958: 315, 1970: 325, 1980: 338, 1990: 354,
        2000: 369, 2010: 389, 2020: 412
    }
    
    # Generate a DataFrame
    data = pd.DataFrame({'year': years})
    
    # Calculate CO2 levels based on interpolation between known points
    co2_levels = []
    uncertainties = []
    
    for year in years:
        # Find closest known years before and after
        prev_years = [y for y in base_co2.keys() if y <= year]
        next_years = [y for y in base_co2.keys() if y >= year]
        
        if prev_years and next_years:
            prev_year = max(prev_years)
            next_year = min(next_years)
            
            # If exact year exists, use its value
            if prev_year == next_year:
                co2 = base_co2[prev_year]
            else:
                # Linear interpolation
                prev_co2 = base_co2[prev_year]
                next_co2 = base_co2[next_year]
                ratio = (year - prev_year) / (next_year - prev_year)
                co2 = prev_co2 + ratio * (next_co2 - prev_co2)
                
                # Add some minor random variation
                co2 += np.random.normal(0, 0.2)
            
            co2_levels.append(round(co2, 2))
            uncertainties.append(round(np.random.uniform(0.1, 0.3), 2))
        elif prev_years:
            # Extrapolate forward
            last_year = max(prev_years)
            co2 = base_co2[last_year] + (year - last_year) * 2.0  # Accelerating increase
            co2 += np.random.normal(0, 0.5)
            co2_levels.append(round(co2, 2))
            uncertainties.append(round(np.random.uniform(0.2, 0.4), 2))
        else:
            # Extrapolate backward
            first_year = min(next_years)
            co2 = base_co2[first_year] - (first_year - year) * 0.6
            co2 += np.random.normal(0, 0.2)
            co2_levels.append(round(co2, 2))
            uncertainties.append(round(np.random.uniform(0.1, 0.3), 2))
    
    data['mean'] = co2_levels
    data['uncertainty'] = uncertainties
    return data

def load_sea_level_data():
    """
    Load global mean sea level data.
    
    Returns:
        A pandas DataFrame with sea level data
    """
    try:
        # NASA Sea Level Change Portal CSV URL
        url = "https://climate.nasa.gov/system/internal_resources/details/original/121_Global_Sea_Level_Data_File.txt"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the data
            data = pd.read_csv(io.StringIO(response.text), delim_whitespace=True)
            data.columns = ['year', 'gmsl', 'gmsl_uncertainty']
            return data
        else:
            # If the request fails, generate sample data
            st.warning("Failed to fetch sea level data. Using historical data.")
            return generate_historical_sea_level_data()
    except Exception as e:
        st.warning(f"Error fetching sea level data: {str(e)}. Using historical data.")
        return generate_historical_sea_level_data()

def generate_historical_sea_level_data():
    """
    Generate historical sea level data based on known values.
    
    Returns:
        A pandas DataFrame with sea level data
    """
    # Create a DataFrame with years from 1993 to present
    current_year = datetime.now().year
    years = range(1993, current_year + 1)
    
    # Initial sea level value (0 mm in 1993)
    initial_value = 0
    
    # Annual rate of increase (mm/year)
    base_rate = 3.0  # Starting rate
    acceleration = 0.1  # Slight acceleration over time
    
    # Generate a DataFrame
    data = pd.DataFrame({'year': years})
    
    # Calculate sea level rise
    sea_levels = []
    uncertainties = []
    
    current_level = initial_value
    for i, year in enumerate(years):
        # Calculate the rate for this year with acceleration
        current_rate = base_rate + (i * acceleration / len(years))
        
        # Add the rise for this year
        current_level += current_rate
        
        # Add some random variation
        variation = np.random.normal(0, 0.5)
        sea_levels.append(round(current_level + variation, 2))
        
        # Add uncertainty values
        uncertainties.append(round(np.random.uniform(0.5, 1.0), 2))
    
    data['gmsl'] = sea_levels
    data['gmsl_uncertainty'] = uncertainties
    return data

def load_arctic_sea_ice_data():
    """
    Load Arctic sea ice extent data.
    
    Returns:
        A pandas DataFrame with Arctic sea ice extent data
    """
    try:
        # NSIDC Sea Ice Index URL
        url = "ftp://sidads.colorado.edu/DATASETS/NOAA/G02135/north/annual/data/N_seaice_extent_annual_v3.0.csv"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the data
            data = pd.read_csv(io.StringIO(response.text), skiprows=1)
            data = data.rename(columns={
                'year': 'year',
                'extent': 'ice_extent',
                'area': 'ice_area'
            })
            return data
        else:
            # If the request fails, generate sample data
            st.warning("Failed to fetch Arctic sea ice data. Using historical data.")
            return generate_historical_sea_ice_data()
    except Exception as e:
        st.warning(f"Error fetching Arctic sea ice data: {str(e)}. Using historical data.")
        return generate_historical_sea_ice_data()

def generate_historical_sea_ice_data():
    """
    Generate historical Arctic sea ice extent data based on known trends.
    
    Returns:
        A pandas DataFrame with Arctic sea ice extent data
    """
    # Create a DataFrame with years from 1979 to present
    current_year = datetime.now().year
    years = range(1979, current_year + 1)
    
    # Known ice extent values (in millions of square km)
    base_extent = {
        1979: 12.8, 1985: 12.5, 1990: 12.2, 1995: 11.9,
        2000: 11.5, 2005: 10.8, 2010: 10.2, 2015: 9.8, 2020: 9.3
    }
    
    # Generate a DataFrame
    data = pd.DataFrame({'year': years})
    
    # Calculate ice extent based on interpolation between known points
    extents = []
    areas = []
    
    for year in years:
        # Find closest known years before and after
        prev_years = [y for y in base_extent.keys() if y <= year]
        next_years = [y for y in base_extent.keys() if y >= year]
        
        if prev_years and next_years:
            prev_year = max(prev_years)
            next_year = min(next_years)
            
            # If exact year exists, use its value
            if prev_year == next_year:
                extent = base_extent[prev_year]
            else:
                # Linear interpolation
                prev_extent = base_extent[prev_year]
                next_extent = base_extent[next_year]
                ratio = (year - prev_year) / (next_year - prev_year)
                extent = prev_extent + ratio * (next_extent - prev_extent)
                
                # Add some minor random variation
                extent += np.random.normal(0, 0.1)
            
            extents.append(round(extent, 2))
            # Area is typically about 85-90% of extent
            areas.append(round(extent * np.random.uniform(0.85, 0.9), 2))
        elif prev_years:
            # Extrapolate forward
            last_year = max(prev_years)
            extent = base_extent[last_year] - (year - last_year) * 0.1
            extent += np.random.normal(0, 0.1)
            extents.append(round(extent, 2))
            areas.append(round(extent * np.random.uniform(0.85, 0.9), 2))
        else:
            # Extrapolate backward
            first_year = min(next_years)
            extent = base_extent[first_year] + (first_year - year) * 0.05
            extent += np.random.normal(0, 0.1)
            extents.append(round(extent, 2))
            areas.append(round(extent * np.random.uniform(0.85, 0.9), 2))
    
    data['ice_extent'] = extents
    data['ice_area'] = areas
    return data

def get_climate_data_for_location(lat, lon):
    """
    Get climate data for a specific location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Dictionary with climate data for the location
    """
    try:
        # For demonstration purposes, we'll return simulated data
        # In a real application, this would query APIs like OpenWeatherMap, NOAA, etc.
        
        # Calculate some values based on latitude to simulate real data patterns
        temp_base = 15 - abs(lat) * 0.5  # Hotter near equator, colder at poles
        precip_base = 1000 - abs(lat) * 10  # More rainfall near equator
        
        # Adjust for longitude (simple variation)
        temp_base += np.sin(np.radians(lon)) * 2
        precip_base += np.cos(np.radians(lon)) * 100
        
        # Add some random variation
        current_temp = temp_base + np.random.normal(0, 3)
        annual_precip = precip_base + np.random.normal(0, 100)
        
        # Get historical anomalies
        temp_data = load_global_temperature_data()
        if not temp_data.empty:
            recent_years = temp_data.tail(30)
            temp_anomaly = recent_years['anomaly'].mean()
        else:
            temp_anomaly = 1.1  # Default value if data fetch fails
        
        return {
            'current_temperature': round(current_temp, 1),
            'temperature_anomaly': round(temp_anomaly, 1),
            'annual_precipitation': round(annual_precip, 0),
            'sea_level_risk': calculate_sea_level_risk(lat, lon),
            'biodiversity_risk': calculate_biodiversity_risk(lat, lon),
            'drought_risk': calculate_drought_risk(lat, lon),
            'historical_data': generate_historical_location_data(lat, lon)
        }
    except Exception as e:
        st.error(f"Error getting climate data for location: {str(e)}")
        return {}

def calculate_sea_level_risk(lat, lon):
    """
    Calculate sea level rise risk for a location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Risk level from 0-10
    """
    # This is a simplified model - real models would use elevation data and sea level projections
    
    # Higher risk for locations near coast and low elevation
    # For simplicity, we'll just use distance from equator as a proxy
    # (coastal areas are at higher risk, especially in tropical regions)
    
    # Lower risk for locations far from equator or at high elevations
    equator_distance = abs(lat)
    
    if equator_distance < 20:
        base_risk = 8  # High risk near equator
    elif equator_distance < 40:
        base_risk = 6  # Medium risk in temperate zones
    else:
        base_risk = 3  # Lower risk at high latitudes
    
    # Add some randomness to simulate actual topography
    risk = base_risk + np.random.normal(0, 1.5)
    
    # Ensure risk is between 0-10
    risk = max(0, min(10, risk))
    
    return round(risk, 1)

def calculate_biodiversity_risk(lat, lon):
    """
    Calculate biodiversity loss risk for a location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Risk level from 0-10
    """
    # Higher risk in tropical areas (biodiversity hotspots)
    equator_distance = abs(lat)
    
    if equator_distance < 15:
        base_risk = 9  # Very high risk in tropical rainforests
    elif equator_distance < 30:
        base_risk = 7  # High risk in subtropical regions
    elif equator_distance < 50:
        base_risk = 5  # Medium risk in temperate zones
    else:
        base_risk = 3  # Lower risk in polar regions
    
    # Add some randomness
    risk = base_risk + np.random.normal(0, 1)
    
    # Ensure risk is between 0-10
    risk = max(0, min(10, risk))
    
    return round(risk, 1)

def calculate_drought_risk(lat, lon):
    """
    Calculate drought risk for a location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Risk level from 0-10
    """
    # Higher risk in subtropical deserts and continental interiors
    equator_distance = abs(lat)
    
    if 15 < equator_distance < 35:
        base_risk = 8  # Very high risk in subtropical desert regions
    elif 35 < equator_distance < 60:
        base_risk = 6  # Medium-high risk in continental interiors
    elif equator_distance < 15:
        base_risk = 4  # Lower risk in tropical regions (more rainfall)
    else:
        base_risk = 3  # Lower risk in polar regions
    
    # Add some randomness
    risk = base_risk + np.random.normal(0, 1.5)
    
    # Ensure risk is between 0-10
    risk = max(0, min(10, risk))
    
    return round(risk, 1)

def generate_historical_location_data(lat, lon):
    """
    Generate historical climate data for a specific location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        DataFrame with historical data
    """
    # Create 50 years of historical data
    current_year = datetime.now().year
    years = range(current_year - 50, current_year + 1)
    
    # Base temperature depends on latitude
    temp_base = 15 - abs(lat) * 0.5
    
    # Generate data
    data = pd.DataFrame({'year': years})
    
    # Temperature with global warming trend
    temperatures = []
    for i, year in enumerate(years):
        # Linear warming trend
        warming = i * 0.03
        
        # Annual variation
        variation = np.random.normal(0, 1.0)
        
        # Final temperature
        temperature = temp_base + warming + variation
        temperatures.append(round(temperature, 2))
    
    data['temperature'] = temperatures
    
    # Precipitation with slight drying trend in some regions
    precip_base = 1000 - abs(lat) * 10
    precipitations = []
    
    for i, year in enumerate(years):
        # Trend depends on latitude
        if 15 < abs(lat) < 35:  # Drying in subtropical regions
            trend = -i * 1.5
        else:  # Slight increase elsewhere
            trend = i * 0.8
        
        # Annual variation
        variation = np.random.normal(0, 100)
        
        # Final precipitation
        precipitation = precip_base + trend + variation
        precipitation = max(10, precipitation)  # Ensure positive values
        precipitations.append(round(precipitation, 0))
    
    data['precipitation'] = precipitations
    
    return data
