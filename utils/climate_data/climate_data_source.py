"""
Climate data source module for GAIA-∞.

This module provides access to various climate data sources,
including the local database, Earth Engine, and external APIs.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import database operations
from database.operations import get_climate_data, get_active_alerts
from database.models import ClimateData, Alert

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateDataSource:
    """
    Source for climate data from various sources.
    """
    
    def __init__(self):
        """Initialize the climate data source."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 3600  # Cache time-to-live in seconds (1 hour)
        
    def get_temperature_data(self, start_date=None, end_date=None, is_prediction=False, with_location=True):
        """
        Get temperature data from the database.
        
        Args:
            start_date: Optional start date string (YYYY-MM-DD)
            end_date: Optional end date string (YYYY-MM-DD)
            is_prediction: Whether to get prediction data
            with_location: Whether to include only records with location data
            
        Returns:
            Pandas DataFrame with temperature data
        """
        try:
            # Convert string dates to datetime if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                
            # Check cache first
            cache_key = f"temp_{start_date}_{end_date}_{is_prediction}_{with_location}"
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    return self.cache[cache_key]
            
            # Get data from database
            records = get_climate_data(
                data_type="temperature",
                start_date=start_datetime,
                end_date=end_datetime,
                is_prediction=is_prediction
            )
            
            if not records:
                logger.warning("No temperature data found in database")
                return pd.DataFrame()
                
            # Convert records to DataFrame
            data = []
            for record in records:
                # Extract latitude and longitude from meta_data if available
                latitude = record.latitude
                longitude = record.longitude
                
                # Skip if we need location data but it's not available
                if with_location and (latitude is None or longitude is None):
                    continue
                    
                data.append({
                    'id': record.id,
                    'timestamp': record.timestamp,
                    'value': record.value,
                    'latitude': latitude,
                    'longitude': longitude,
                    'source': record.source,
                    'is_prediction': record.is_prediction
                })
                
            df = pd.DataFrame(data)
            
            # Cache the result
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting temperature data: {str(e)}")
            return pd.DataFrame()
            
    def get_co2_data(self, start_date=None, end_date=None, is_prediction=False):
        """
        Get CO2 concentration data from the database.
        
        Args:
            start_date: Optional start date string (YYYY-MM-DD)
            end_date: Optional end date string (YYYY-MM-DD)
            is_prediction: Whether to get prediction data
            
        Returns:
            Pandas DataFrame with CO2 data
        """
        try:
            # Convert string dates to datetime if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                
            # Check cache first
            cache_key = f"co2_{start_date}_{end_date}_{is_prediction}"
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    return self.cache[cache_key]
            
            # Get data from database
            records = get_climate_data(
                data_type="co2",
                start_date=start_datetime,
                end_date=end_datetime,
                is_prediction=is_prediction
            )
            
            if not records:
                logger.warning("No CO2 data found in database")
                return pd.DataFrame()
                
            # Convert records to DataFrame
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'timestamp': record.timestamp,
                    'value': record.value,
                    'source': record.source,
                    'is_prediction': record.is_prediction
                })
                
            df = pd.DataFrame(data)
            
            # Cache the result
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting CO2 data: {str(e)}")
            return pd.DataFrame()
            
    def get_sea_level_data(self, start_date=None, end_date=None, is_prediction=False):
        """
        Get sea level data from the database.
        
        Args:
            start_date: Optional start date string (YYYY-MM-DD)
            end_date: Optional end date string (YYYY-MM-DD)
            is_prediction: Whether to get prediction data
            
        Returns:
            Pandas DataFrame with sea level data
        """
        try:
            # Convert string dates to datetime if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                
            # Check cache first
            cache_key = f"sea_level_{start_date}_{end_date}_{is_prediction}"
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    return self.cache[cache_key]
            
            # Get data from database
            records = get_climate_data(
                data_type="sea_level",
                start_date=start_datetime,
                end_date=end_datetime,
                is_prediction=is_prediction
            )
            
            if not records:
                logger.warning("No sea level data found in database")
                return pd.DataFrame()
                
            # Convert records to DataFrame
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'timestamp': record.timestamp,
                    'value': record.value,
                    'source': record.source,
                    'is_prediction': record.is_prediction
                })
                
            df = pd.DataFrame(data)
            
            # Cache the result
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting sea level data: {str(e)}")
            return pd.DataFrame()
            
    def get_ice_extent_data(self, start_date=None, end_date=None, is_prediction=False):
        """
        Get sea ice extent data from the database.
        
        Args:
            start_date: Optional start date string (YYYY-MM-DD)
            end_date: Optional end date string (YYYY-MM-DD)
            is_prediction: Whether to get prediction data
            
        Returns:
            Pandas DataFrame with ice extent data
        """
        try:
            # Convert string dates to datetime if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                
            # Check cache first
            cache_key = f"ice_{start_date}_{end_date}_{is_prediction}"
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    return self.cache[cache_key]
            
            # Get data from database
            records = get_climate_data(
                data_type="ice_extent",
                start_date=start_datetime,
                end_date=end_datetime,
                is_prediction=is_prediction
            )
            
            if not records:
                logger.warning("No ice extent data found in database")
                return pd.DataFrame()
                
            # Convert records to DataFrame
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'timestamp': record.timestamp,
                    'value': record.value,
                    'source': record.source,
                    'is_prediction': record.is_prediction
                })
                
            df = pd.DataFrame(data)
            
            # Cache the result
            self.cache[cache_key] = df
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting ice extent data: {str(e)}")
            return pd.DataFrame()
            
    def get_extreme_events(self, region=None, event_type=None, min_severity=None):
        """
        Get active extreme climate events.
        
        Args:
            region: Optional region filter
            event_type: Optional event type filter
            min_severity: Optional minimum severity filter
            
        Returns:
            List of dictionaries with extreme events
        """
        try:
            # Check cache first
            cache_key = f"events_{region}_{event_type}_{min_severity}"
            if cache_key in self.cache and cache_key in self.cache_expiry:
                if datetime.now() < self.cache_expiry[cache_key]:
                    return self.cache[cache_key]
            
            # Get active alerts from database
            alerts = get_active_alerts(alert_type=event_type, region=region, min_severity=min_severity)
            
            if not alerts:
                logger.info("No active extreme events found")
                return []
                
            # Convert alerts to list of dictionaries
            events = []
            for alert in alerts:
                events.append({
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'region': alert.region,
                    'latitude': alert.latitude,
                    'longitude': alert.longitude,
                    'title': alert.title,
                    'description': alert.description,
                    'issued_at': alert.issued_at.isoformat() if alert.issued_at else None,
                    'expires_at': alert.expires_at.isoformat() if alert.expires_at else None,
                    'source': alert.source
                })
                
            # Cache the result
            self.cache[cache_key] = events
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting extreme events: {str(e)}")
            return []
            
    def get_aggregated_climate_stats(self):
        """
        Get aggregated climate statistics.
        
        Returns:
            Dictionary with climate statistics
        """
        try:
            # Get the latest values
            latest_temp = self._get_latest_value("temperature", is_prediction=False)
            latest_co2 = self._get_latest_value("co2", is_prediction=False)
            latest_sea_level = self._get_latest_value("sea_level", is_prediction=False)
            latest_ice = self._get_latest_value("ice_extent", is_prediction=False)
            
            # Get the latest predictions
            predicted_temp = self._get_latest_value("temperature", is_prediction=True)
            predicted_co2 = self._get_latest_value("co2", is_prediction=True)
            predicted_sea_level = self._get_latest_value("sea_level", is_prediction=True)
            predicted_ice = self._get_latest_value("ice_extent", is_prediction=True)
            
            # Get active events count
            active_events = len(self.get_extreme_events())
            
            # Get data trends (comparing with 1 year ago)
            temp_trend = self._calculate_trend("temperature")
            co2_trend = self._calculate_trend("co2")
            sea_level_trend = self._calculate_trend("sea_level")
            ice_trend = self._calculate_trend("ice_extent")
            
            return {
                "current": {
                    "temperature": latest_temp,
                    "co2": latest_co2,
                    "sea_level": latest_sea_level,
                    "ice_extent": latest_ice
                },
                "predicted": {
                    "temperature": predicted_temp,
                    "co2": predicted_co2,
                    "sea_level": predicted_sea_level,
                    "ice_extent": predicted_ice
                },
                "trends": {
                    "temperature": temp_trend,
                    "co2": co2_trend,
                    "sea_level": sea_level_trend,
                    "ice_extent": ice_trend
                },
                "active_events": active_events,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting aggregated climate stats: {str(e)}")
            return {"error": str(e)}
            
    def _get_latest_value(self, data_type, is_prediction=False):
        """
        Get the latest value for a climate data type.
        
        Args:
            data_type: Type of climate data
            is_prediction: Whether to get prediction or historical data
            
        Returns:
            Latest value or None if not found
        """
        try:
            # Get records from database
            records = get_climate_data(data_type=data_type, is_prediction=is_prediction, limit=1)
            
            if not records:
                return None
                
            # Return the value
            return records[0].value
            
        except Exception as e:
            logger.error(f"Error getting latest {data_type} value: {str(e)}")
            return None
            
    def _calculate_trend(self, data_type):
        """
        Calculate trend for a climate data type.
        
        Args:
            data_type: Type of climate data
            
        Returns:
            Dictionary with trend information
        """
        try:
            # Get current value
            current = self._get_latest_value(data_type)
            
            if current is None:
                return None
                
            # Get value from 1 year ago
            one_year_ago = datetime.now() - timedelta(days=365)
            records = get_climate_data(
                data_type=data_type,
                end_date=one_year_ago,
                is_prediction=False,
                limit=1
            )
            
            if not records:
                return None
                
            previous = records[0].value
            
            # Calculate change
            absolute_change = current - previous
            if previous != 0:
                percentage_change = (absolute_change / previous) * 100
            else:
                percentage_change = 0
                
            # Determine direction
            if absolute_change > 0:
                direction = "increasing"
            elif absolute_change < 0:
                direction = "decreasing"
            else:
                direction = "stable"
                
            return {
                "current": current,
                "previous": previous,
                "absolute_change": absolute_change,
                "percentage_change": percentage_change,
                "direction": direction
            }
            
        except Exception as e:
            logger.error(f"Error calculating {data_type} trend: {str(e)}")
            return None