"""
This module initializes the database with climate data and models
for the GAIA-∞ Climate Intelligence Platform.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import os

from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db_session, close_db_session, init_db
# Import models
from database.models import ClimateData, Alert, SimulationResult, EarthEngineImage, User
from database.operations import (
    store_climate_data, create_alert, store_simulation_result, 
    store_earth_engine_image, create_user
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database schema and populate with initial data."""
    try:
        # Create tables
        init_db()
        logger.info("Database tables created successfully")
        
        # Create initial data
        create_initial_users()
        create_initial_climate_data()
        create_initial_alerts()
        create_initial_simulation_results()
        create_initial_earth_engine_data()
        
        logger.info("Database initialized successfully with initial data")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def create_initial_users():
    """Create initial users for the system."""
    try:
        # Create admin user
        admin_created = create_user(
            username="admin",
            email="admin@gaia-infinity.ai",
            password_hash="$2b$12$QqHSJBQ5S6gD8XK5BFVlp.l2mzKqm8LBx4QYcYBoTvMC8U9VPY/jK",  # hashed "admin123"
            role="admin"
        )
        
        # Create demo user
        demo_created = create_user(
            username="demo",
            email="demo@gaia-infinity.ai",
            password_hash="$2b$12$m3O9UrQNI6C/zKSuXa.kXOnj5TwEAf.Zz5BO4.KY8lPZtC4w9kd7y",  # hashed "demo123"
            role="user"
        )
        
        if admin_created and demo_created:
            logger.info("Initial users created successfully")
        else:
            logger.warning("Some initial users could not be created")
            
    except Exception as e:
        logger.error(f"Error creating initial users: {str(e)}")

def create_initial_climate_data():
    """Create initial climate data for the system."""
    try:
        # Generate historical temperature data
        current_year = datetime.now().year
        start_year = 1880
        
        # Temperature anomaly data (based on NASA GISS data pattern)
        years = list(range(start_year, current_year + 1))
        base_anomaly = np.linspace(-0.2, 0.3, 100)  # 1880-1979
        accelerated_anomaly = np.linspace(0.3, 1.1, current_year - 1979)  # 1980-present
        
        temperature_anomalies = np.concatenate([base_anomaly[:100], accelerated_anomaly])
        noise = np.random.normal(0, 0.1, len(years))
        temperature_anomalies = temperature_anomalies + noise
        
        # Store temperature data
        for i, year in enumerate(years):
            store_climate_data(
                data_type="temperature",
                timestamp=datetime(year, 7, 1),
                value=temperature_anomalies[i],
                source="GAIA-∞ Initial Data",
                is_prediction=False,
                meta_data={"type": "global_average"}
            )
        
        # Generate CO2 concentration data (based on Mauna Loa pattern)
        if start_year < 1960:
            # Pre-1960 data is more sparse
            co2_years = list(range(1960, current_year + 1))
            base_co2 = 315  # ppm in 1960
        else:
            co2_years = years
            base_co2 = 290  # estimated for 1880
            
        for i, year in enumerate(co2_years):
            # CO2 increase accelerates over time
            if year < 1980:
                co2_increase = 0.85  # ppm per year
            elif year < 2000:
                co2_increase = 1.5  # ppm per year
            else:
                co2_increase = 2.3  # ppm per year
                
            year_idx = year - co2_years[0]
            co2_value = base_co2 + sum([co2_increase for _ in range(year_idx)])
            
            # Add seasonal variation and noise
            months = list(range(1, 13))
            for month in months:
                # CO2 has seasonal cycle, highest in May, lowest in October
                seasonal_factor = 2.0 * np.sin(2 * np.pi * (month - 1) / 12)
                monthly_co2 = co2_value + seasonal_factor + np.random.normal(0, 0.3)
                
                store_climate_data(
                    data_type="co2",
                    timestamp=datetime(year, month, 15),
                    value=monthly_co2,
                    source="GAIA-∞ Initial Data",
                    is_prediction=False,
                    meta_data={"location": "global_average"}
                )
        
        # Generate sea level data (based on satellite altimetry pattern)
        # Sea level data starts from 1993 (satellite era)
        sea_level_years = list(range(1993, current_year + 1))
        base_sea_level = 0  # mm in 1993 (relative)
        sea_level_rate = 3.3  # mm per year
        
        for i, year in enumerate(sea_level_years):
            sea_level = base_sea_level + (i * sea_level_rate) + np.random.normal(0, 1)
            
            store_climate_data(
                data_type="sea_level",
                timestamp=datetime(year, 6, 30),
                value=sea_level,
                source="GAIA-∞ Initial Data",
                is_prediction=False,
                meta_data={"type": "global_average"}
            )
        
        # Generate Arctic sea ice data
        ice_years = list(range(1979, current_year + 1))  # Satellite data starts 1979
        base_ice_extent = 12.5  # million sq km in 1979
        
        for i, year in enumerate(ice_years):
            # Ice loss accelerates over time
            if year < 2000:
                ice_loss_rate = 0.05  # million sq km per year
            elif year < 2010:
                ice_loss_rate = 0.1  # million sq km per year
            else:
                ice_loss_rate = 0.15  # million sq km per year
            
            ice_extent = base_ice_extent - (i * ice_loss_rate) + np.random.normal(0, 0.2)
            ice_extent = max(ice_extent, 3.0)  # Ensure physical reasonability
            
            store_climate_data(
                data_type="ice_extent",
                timestamp=datetime(year, 9, 15),  # September minimum
                value=ice_extent,
                source="GAIA-∞ Initial Data",
                is_prediction=False,
                meta_data={"type": "arctic_september_minimum"}
            )
            
        # Generate some future predictions
        future_years = list(range(current_year + 1, current_year + 31))
        last_temp = temperature_anomalies[-1]
        last_co2 = co2_value
        last_sea_level = base_sea_level + ((len(sea_level_years) - 1) * sea_level_rate)
        last_ice = ice_extent
        
        # Business as usual scenario
        for i, year in enumerate(future_years):
            # Temperature (accelerating)
            future_temp = last_temp + (0.03 * (i + 1)) + np.random.normal(0, 0.05)
            
            store_climate_data(
                data_type="temperature",
                timestamp=datetime(year, 7, 1),
                value=future_temp,
                source="GAIA-∞ Prediction",
                is_prediction=True,
                prediction_model="Business as Usual",
                meta_data={"type": "global_average"}
            )
            
            # CO2 (continuing increase)
            future_co2 = last_co2 + (2.5 * (i + 1)) + np.random.normal(0, 1)
            
            store_climate_data(
                data_type="co2",
                timestamp=datetime(year, 7, 1),
                value=future_co2,
                source="GAIA-∞ Prediction",
                is_prediction=True,
                prediction_model="Business as Usual",
                meta_data={"type": "global_average"}
            )
            
            # Sea level (accelerating)
            future_sea_level = last_sea_level + (3.5 * (i + 1)) + np.random.normal(0, 1)
            
            store_climate_data(
                data_type="sea_level",
                timestamp=datetime(year, 6, 30),
                value=future_sea_level,
                source="GAIA-∞ Prediction",
                is_prediction=True,
                prediction_model="Business as Usual",
                meta_data={"type": "global_average"}
            )
            
            # Ice extent (declining)
            future_ice = max(0, last_ice - (0.15 * (i + 1)) + np.random.normal(0, 0.1))
            
            store_climate_data(
                data_type="ice_extent",
                timestamp=datetime(year, 9, 15),
                value=future_ice,
                source="GAIA-∞ Prediction",
                is_prediction=True,
                prediction_model="Business as Usual",
                meta_data={"type": "arctic_september_minimum"}
            )
        
        logger.info("Initial climate data created successfully")
            
    except Exception as e:
        logger.error(f"Error creating initial climate data: {str(e)}")

def create_initial_alerts():
    """Create initial environmental alerts for the system."""
    try:
        # Create some current alerts
        current_date = datetime.now()
        expiry_date = current_date + timedelta(days=7)
        
        # Alert 1: Extreme heat
        create_alert(
            alert_type="extreme_weather",
            severity=4,  # High
            region="South Asia",
            latitude=28.7041,
            longitude=77.1025,
            title="Extreme Heat Wave: Northern India",
            description="Temperatures exceeding 45°C (113°F) expected to affect over 100 million people across northern India for the next 5-7 days. Heat wave conditions expected to impact agriculture, increase water demand, and pose significant health risks.",
            expires_at=expiry_date,
            source="GAIA-∞ Climate Intelligence"
        )
        
        # Alert 2: Drought
        create_alert(
            alert_type="drought",
            severity=3,  # Medium-high
            region="Western United States",
            latitude=36.7783,
            longitude=-119.4179,
            title="Severe Drought Conditions: Western US",
            description="Persistent drought conditions worsening across Western states, with over 75% of the region experiencing moderate to severe drought. Water reservoirs at critical levels and increasing wildfire risk.",
            expires_at=current_date + timedelta(days=90),  # Longer term alert
            source="GAIA-∞ Climate Intelligence"
        )
        
        # Alert 3: Flooding
        create_alert(
            alert_type="flood",
            severity=5,  # Critical
            region="Southeast Asia",
            latitude=14.0583,
            longitude=108.2772,
            title="Monsoon Flooding: Vietnam and Cambodia",
            description="Heavy monsoon rainfall causing severe flooding across multiple provinces. Over 100,000 people displaced and critical infrastructure damaged. Additional rainfall expected to worsen conditions over the next 72 hours.",
            expires_at=current_date + timedelta(days=5),
            source="GAIA-∞ Climate Intelligence"
        )
        
        # Alert 4: Sea level
        create_alert(
            alert_type="sea_level",
            severity=3,  # Medium-high
            region="Pacific Islands",
            latitude=-17.7134,
            longitude=178.0650,
            title="King Tide Coastal Flooding: Fiji",
            description="Exceptionally high 'king tides' combined with rising sea levels causing significant coastal flooding in low-lying communities. Infrastructure damage and saltwater contamination of freshwater resources reported.",
            expires_at=current_date + timedelta(days=3),
            source="GAIA-∞ Climate Intelligence"
        )
        
        # Alert 5: Wildfire
        create_alert(
            alert_type="wildfire",
            severity=4,  # High
            region="Mediterranean",
            latitude=38.7223,
            longitude=9.1393,
            title="Extreme Fire Danger: Portugal and Spain",
            description="Combination of drought conditions, high temperatures, and strong winds creating extreme fire danger across the Iberian Peninsula. Multiple active fires already reported with rapid spread potential.",
            expires_at=current_date + timedelta(days=10),
            source="GAIA-∞ Climate Intelligence"
        )
        
        logger.info("Initial alerts created successfully")
            
    except Exception as e:
        logger.error(f"Error creating initial alerts: {str(e)}")

def create_initial_simulation_results():
    """Create initial simulation results for the system."""
    try:
        # Create simulation results for different scenarios
        current_year = datetime.now().year
        projection_years = list(range(current_year, current_year + 81))
        
        # Business as usual scenario
        bau_scenario = {
            "temperature": [1.1 + (0.035 * i + 0.0003 * i**2) for i in range(len(projection_years))],
            "co2": [417 + (2.5 * i) for i in range(len(projection_years))],
            "sea_level": [0 + (3.5 * i + 0.015 * i**2) for i in range(len(projection_years))],
            "arctic_ice": [max(0, 10.5 - (0.15 * i)) for i in range(len(projection_years))]
        }
        
        store_simulation_result(
            name="Business as Usual Projection",
            scenario="business_as_usual",
            parameters={
                "start_year": current_year,
                "end_year": current_year + 80,
                "description": "Continued high emissions with no mitigation efforts"
            },
            results={
                "years": projection_years,
                "data": bau_scenario
            },
            description="Simulation of climate impacts under current emissions trajectory with no additional mitigation policies."
        )
        
        # Moderate mitigation scenario
        mod_scenario = {
            "temperature": [1.1 + (0.025 * i + 0.0001 * i**2) for i in range(len(projection_years))],
            "co2": [417 + (1.8 * i) for i in range(len(projection_years))],
            "sea_level": [0 + (3.2 * i + 0.01 * i**2) for i in range(len(projection_years))],
            "arctic_ice": [max(0, 10.5 - (0.1 * i)) for i in range(len(projection_years))]
        }
        
        store_simulation_result(
            name="Moderate Mitigation Projection",
            scenario="moderate_mitigation",
            parameters={
                "start_year": current_year,
                "end_year": current_year + 80,
                "description": "Partial implementation of Paris Agreement commitments"
            },
            results={
                "years": projection_years,
                "data": mod_scenario
            },
            description="Simulation of climate impacts with moderate emission reductions consistent with partial implementation of current policies."
        )
        
        # Strong mitigation scenario
        strong_scenario = {
            "temperature": [1.1 + (0.015 * i) for i in range(len(projection_years))],
            "co2": [417 + min(0.8 * i, 40) for i in range(len(projection_years))],
            "sea_level": [0 + (2.8 * i) for i in range(len(projection_years))],
            "arctic_ice": [max(5, 10.5 - (0.05 * i)) for i in range(len(projection_years))]
        }
        
        store_simulation_result(
            name="Strong Mitigation Projection",
            scenario="strong_mitigation",
            parameters={
                "start_year": current_year,
                "end_year": current_year + 80,
                "description": "Ambitious emission reductions aligned with 1.5°C pathway"
            },
            results={
                "years": projection_years,
                "data": strong_scenario
            },
            description="Simulation of climate impacts with strong emission reductions aligned with the Paris Agreement 1.5°C goal."
        )
        
        # Net zero scenario
        net_zero_scenario = {
            "temperature": [1.1 + (0.01 * min(i, 30)) for i in range(len(projection_years))],
            "co2": [417 + 0.5 * min(i, 30) - max(0, 0.5 * (i - 30)) for i in range(len(projection_years))],
            "sea_level": [0 + (2.5 * i) for i in range(len(projection_years))],
            "arctic_ice": [max(8, 10.5 - (0.03 * min(i, 30))) for i in range(len(projection_years))]
        }
        
        store_simulation_result(
            name="Net Zero by 2050 Projection",
            scenario="net_zero",
            parameters={
                "start_year": current_year,
                "end_year": current_year + 80,
                "description": "Global net zero emissions by 2050 with negative emissions after"
            },
            results={
                "years": projection_years,
                "data": net_zero_scenario
            },
            description="Simulation of climate impacts with rapid transition to net zero emissions by 2050, followed by negative emissions."
        )
        
        logger.info("Initial simulation results created successfully")
            
    except Exception as e:
        logger.error(f"Error creating initial simulation results: {str(e)}")

def create_initial_earth_engine_data():
    """Create initial Earth Engine dataset references."""
    try:
        # Add key Earth Engine datasets
        
        # Dataset 1: Land Surface Temperature
        store_earth_engine_image(
            dataset_id="MODIS/006/MOD11A1",
            display_name="Land Surface Temperature",
            description="MODIS Land Surface Temperature daily global 1km resolution dataset showing Earth's skin temperature.",
            image_properties={"band": "LST_Day_1km"},
            visualization_params={
                "min": -20,
                "max": 40,
                "palette": ["blue", "purple", "cyan", "green", "yellow", "red"]
            }
        )
        
        # Dataset 2: Vegetation Index
        store_earth_engine_image(
            dataset_id="MODIS/006/MOD13A2",
            display_name="Vegetation Index (NDVI)",
            description="MODIS Normalized Difference Vegetation Index (NDVI) showing vegetation health and density.",
            image_properties={"band": "NDVI"},
            visualization_params={
                "min": -2000,
                "max": 10000,
                "palette": ["brown", "yellow", "green", "darkgreen"]
            }
        )
        
        # Dataset 3: Precipitation
        store_earth_engine_image(
            dataset_id="NASA/GPM_L3/IMERG_V06",
            display_name="Global Precipitation",
            description="NASA Global Precipitation Measurement dataset showing precipitation rates.",
            image_properties={"band": "precipitationCal"},
            visualization_params={
                "min": 0,
                "max": 10,
                "palette": ["white", "blue", "purple", "red"]
            }
        )
        
        # Dataset 4: Sea Surface Temperature
        store_earth_engine_image(
            dataset_id="NASA/OCEANDATA/MODIS-Terra/L3SMI",
            display_name="Sea Surface Temperature",
            description="MODIS Terra Ocean Color dataset showing sea surface temperature.",
            image_properties={"band": "sst"},
            visualization_params={
                "min": -4,
                "max": 30,
                "palette": ["blue", "cyan", "green", "yellow", "red"]
            }
        )
        
        # Dataset 5: Carbon Monoxide
        store_earth_engine_image(
            dataset_id="COPERNICUS/S5P/NRTI/L3_CO",
            display_name="Carbon Monoxide",
            description="Sentinel-5P Carbon Monoxide concentration in the atmosphere, indicator of air quality and pollution.",
            image_properties={"band": "CO_column_number_density"},
            visualization_params={
                "min": 0,
                "max": 0.05,
                "palette": ["black", "blue", "purple", "cyan", "green", "yellow", "red"]
            }
        )
        
        logger.info("Initial Earth Engine data created successfully")
            
    except Exception as e:
        logger.error(f"Error creating initial Earth Engine data: {str(e)}")

if __name__ == "__main__":
    initialize_database()