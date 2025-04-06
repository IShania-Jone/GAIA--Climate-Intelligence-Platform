import ee
import os
import json
import streamlit as st
import folium
from folium import plugins
import geemap.foliumap as geemap
from datetime import datetime, timedelta,timezone

def initialize_earth_engine():
    """
    Initialize the Earth Engine API. This function tries to authenticate with Earth Engine
    using Service Account credentials if available, or uses non-interactive authentication for cloud environments.
    """
    # Check if we already have authenticated in this session
    if 'ee_initialized' in st.session_state and st.session_state.ee_initialized:
        return True
        
    try:
        # Try to initialize Earth Engine (works if already authenticated)
        ee.Authenticate()
        ee.Initialize(project='gaia-455911')
        st.session_state.ee_initialized = True
        return True
    except Exception as e:
        # If the initialization fails, try to authenticate
        try:
            # Try using environment variables first
            service_account = os.getenv("EARTH_ENGINE_SERVICE_ACCOUNT")
            private_key = os.getenv("EARTH_ENGINE_PRIVATE_KEY")
            
            if service_account and private_key:
                try:
                    private_key = private_key.replace('\\n', '\n')  # Fix newline characters
                    credentials = ee.ServiceAccountCredentials(service_account, key_data=private_key)
                    ee.Initialize(credentials)
                    st.session_state.ee_initialized = True
                    st.session_state.earth_engine_service_account = service_account
                    return True
                except Exception as cred_error:
                    st.error(f"Error initializing Earth Engine with credentials: {str(cred_error)}")
                    return False
            else:
                st.warning("Earth Engine credentials not found in environment variables")
                return False
            
            # If credentials fail, try using session state
            service_account = None
            private_key = None
            
            # Check session state first (from UI input)
            if 'earth_engine_service_account' in st.session_state:
                service_account = st.session_state.earth_engine_service_account
            if 'earth_engine_private_key' in st.session_state:
                private_key = st.session_state.earth_engine_private_key
                
            # If not in session state, check environment variables
            if not service_account:
                service_account = os.getenv("EARTH_ENGINE_SERVICE_ACCOUNT", None)
            if not private_key:
                private_key = os.getenv("EARTH_ENGINE_PRIVATE_KEY", None)
            
            if service_account and private_key:
                credentials = ee.ServiceAccountCredentials(service_account, private_key)
                ee.Initialize(credentials)
                st.session_state.ee_initialized = True
                return True
            else:
                # In a cloud/deployed environment, we can't use interactive authentication
                # So we'll use a fallback mechanism to show demo content
                st.session_state.ee_initialized = False
                st.warning("Google Earth Engine authentication is pending. For full functionality, please provide Earth Engine credentials.")
                st.info("Currently running in demonstration mode with limited Earth visualization capabilities.")
                return False
        except Exception as auth_error:
            st.error(f"Earth Engine authentication issue: {str(auth_error)}")
            st.info("Using demonstration mode with sample data. For full functionality, please provide Earth Engine credentials.")
            st.session_state.ee_initialized = False
            return False

def get_earth_engine_map(center_lat=0.0, center_lon=0.0, zoom=2):
    """
    Create and return a geemap Map object centered at the specified coordinates.
    
    Args:
        center_lat: Latitude for the center of the map (float)
        center_lon: Longitude for the center of the map (float)
        zoom: Initial zoom level (int)
    
    Returns:
        A geemap Map object
    """
    try:
        # Ensure we're working with the right types
        center_lat_float = float(center_lat)
        center_lon_float = float(center_lon)
        zoom_int = int(zoom)
        
        # Create a geemap Map object
        m = geemap.Map(location=[center_lat_float, center_lon_float], zoom=zoom_int)
        
        # Add Earth Engine dataset layers
        add_default_basemaps(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating Earth Engine map: {str(e)}")
        # Return a simple folium map as fallback
        m = folium.Map(location=[float(center_lat), float(center_lon)], zoom=int(zoom))
        return m

def add_default_basemaps(m):
    """
    Add default Earth Engine layers to the map.
    
    Args:
        m: A geemap Map object
    """
    try:
        # Add MODIS land surface temperature
        ee.Authenticate()
        ee.Initialize(project='gaia-455911')
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=30)  
        ee_start = ee.Date(start.isoformat() + 'Z')
        ee_end = ee.Date(end.isoformat() + 'Z')
        lst = (
            ee.ImageCollection('MODIS/006/MOD11A1')
            .filter(ee.Filter.date(ee_start, ee_end))
            .select('LST_Day_1km')
            .mean()
        )

        
        # Scale to Celsius
        lst = lst.multiply(0.02).subtract(273.15)
        
        # Add the layer to the map
        m.add_layer(
            lst,
            {
                'min': -20,
                'max': 40,
                'palette': ['blue', 'purple', 'cyan', 'green', 'yellow', 'red']
            },
            'Land Surface Temperature'
        )
        
        # Add MODIS vegetation indices
        ee.Initialize(project='gaia-455911')
        now = datetime.now(timezone.utc)
        two_months_ago = now - timedelta(days=60)  # Approximate 2 months
        start = ee.Date(two_months_ago.isoformat())
        end = ee.Date(now.isoformat())
        ndvi = ee.ImageCollection('MODIS/006/MOD13A2') \
           .filter(ee.Filter.date(start, end)) \
           .select('NDVI') \
            .mean()
        
        m.add_layer(
            ndvi,
            {
                'min': -2000,
                'max': 10000,
                'palette': ['brown', 'yellow', 'green', 'darkgreen']
            },
            'Vegetation Index (NDVI)'
        )
        
        # Add precipitation data
        ee.Authenticate()
        ee.Initialize(project='gaia-455911')


        end = datetime.now(timezone.utc)
        start = end - timedelta(weeks=1)
        ee_start = ee.Date(start.isoformat() + 'Z')
        ee_end = ee.Date(end.isoformat() + 'Z')
        date_filter = ee.Filter.date(ee_start, ee_end)
        precipitation = (
            ee.ImageCollection('NASA/GPM_L3/IMERG_V06')
            .filter(date_filter)
            .select('precipitationCal')
            .mean()
        )
        m.add_layer(
            precipitation,
            {
                'min': 0,
                'max': 10,
                'palette': ['white', 'blue', 'purple', 'red']
            },
            'Precipitation'
        )
        
        # Add sea surface temperature
        ee.Initialize(project='gaia-455911')

        now = datetime.now(timezone.utc)
        one_month_ago = now - timedelta(days=30)  # Approximate 1 month
        start = ee.Date(one_month_ago.isoformat())
        end = ee.Date(now.isoformat())
        sst = ee.ImageCollection('NASA/OCEANDATA/MODIS-Terra/L3SMI') \
            .filter(ee.Filter.date(start, end)) \
            .select('sst') \
            .mean()
        
        m.add_layer(
            sst,
            {
                'min': -4,
                'max': 30,
                'palette': ['blue', 'cyan', 'green', 'yellow', 'red']
            },
            'Sea Surface Temperature'
        )
        
        # Add layer control
        m.add_layer_control()
        
    except Exception as e:
        print(f"Error adding Earth Engine layers: {str(e)}")
        # Continue without adding these layers

def get_available_datasets():
    """
    Return a list of available Earth Engine datasets with descriptions.
    
    Returns:
        A list of dictionaries with dataset information
    """
    return [
        {
            "id": "MODIS/006/MOD11A1",
            "name": "Land Surface Temperature",
            "description": "MODIS Land Surface Temperature daily global 1km",
            "band": "LST_Day_1km",
            "visualization": {
                "min": -20,
                "max": 40,
                "palette": ['blue', 'purple', 'cyan', 'green', 'yellow', 'red']
            }
        },
        {
            "id": "MODIS/006/MOD13A2",
            "name": "Vegetation Index (NDVI)",
            "description": "MODIS Vegetation Index (NDVI) 16-day global 1km",
            "band": "NDVI",
            "visualization": {
                "min": -2000,
                "max": 10000,
                "palette": ['brown', 'yellow', 'green', 'darkgreen']
            }
        },
        {
            "id": "NASA/GPM_L3/IMERG_V06",
            "name": "Precipitation",
            "description": "Global Precipitation Measurement (GPM) 30-minute 0.1 degree",
            "band": "precipitationCal",
            "visualization": {
                "min": 0,
                "max": 10,
                "palette": ['white', 'blue', 'purple', 'red']
            }
        },
        {
            "id": "NASA/OCEANDATA/MODIS-Terra/L3SMI",
            "name": "Sea Surface Temperature",
            "description": "MODIS Terra Ocean Color SMI",
            "band": "sst",
            "visualization": {
                "min": -4,
                "max": 30,
                "palette": ['blue', 'cyan', 'green', 'yellow', 'red']
            }
        },
        {
            "id": "COPERNICUS/S5P/NRTI/L3_CO",
            "name": "Carbon Monoxide",
            "description": "Sentinel-5P Carbon Monoxide",
            "band": "CO_column_number_density",
            "visualization": {
                "min": 0,
                "max": 0.05,
                "palette": ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
            }
        }
    ]

def get_dataset_by_id(dataset_id):
    """
    Get dataset information by ID.
    
    Args:
        dataset_id: The Earth Engine dataset ID
        
    Returns:
        Dictionary with dataset information or None if not found
    """
    for dataset in get_available_datasets():
        if dataset["id"] == dataset_id:
            return dataset
    return None

def add_dataset_to_map(m, dataset_id):
    """
    Add a specific Earth Engine dataset to a map.
    
    Args:
        m: A geemap Map object
        dataset_id: The Earth Engine dataset ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dataset = get_dataset_by_id(dataset_id)
        if not dataset:
            return False
            
        # Get the dataset as an image collection
        collection = ee.ImageCollection(dataset["id"])
        
        # Filter to recent data
        ee.Initialize(project='gaia-455911')
        now = datetime.now(timezone.utc)
        one_month_ago = now - timedelta(days=30)  
        start = ee.Date(one_month_ago.isoformat())
        end = ee.Date(now.isoformat())
        recent_data = collection.filter(
             ee.Filter.date(start, end)
        ).select(dataset["band"]).mean()
        
        # Add the layer to the map
        m.add_layer(
            recent_data,
            dataset["visualization"],
            dataset["name"]
        )
        
        return True
    except Exception as e:
        print(f"Error adding dataset {dataset_id}: {str(e)}")
        return False
