"""
Real-time global climate data heatmap module for GAIA-∞.

This module generates interactive heatmaps of global climate data,
including temperature anomalies, precipitation, and extreme events.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import ee
import folium
from datetime import datetime, timedelta
from folium import plugins
import geemap.foliumap as geemap
from .climate_data_source import ClimateDataSource

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlobalHeatmapGenerator:
    """
    Generator for real-time global climate data heatmaps.
    """
    
    def __init__(self, earth_engine_initialized=False):
        """
        Initialize the heatmap generator.
        
        Args:
            earth_engine_initialized: Boolean indicating if Earth Engine is initialized
        """
        self.data_source = ClimateDataSource()
        self.earth_engine_initialized = earth_engine_initialized
        self.last_update = None
        self.cached_heatmaps = {}
        
    def get_temperature_heatmap(self, map_obj=None, days_ago=7):
        """
        Generate a global temperature anomaly heatmap.
        
        Args:
            map_obj: Optional folium Map object to add layer to
            days_ago: Days before today to start data collection
            
        Returns:
            Folium map object with temperature heatmap layer
        """
        if not map_obj:
            map_obj = folium.Map(location=[0, 0], zoom_start=2, tiles="CartoDB Positron")
            
        if not self.earth_engine_initialized:
            # If Earth Engine is not available, use database records
            df = self._get_temperature_from_database(days_ago)
            
            if df is not None and not df.empty:
                # Create a heatmap using folium HeatMap plugin
                heat_data = [[row['latitude'], row['longitude'], row['value']] 
                           for _, row in df.iterrows() if pd.notna(row['latitude']) and pd.notna(row['longitude'])]
                
                if heat_data:
                    plugins.HeatMap(
                        heat_data,
                        radius=15,
                        blur=10,
                        gradient={
                            0.2: 'blue',
                            0.4: 'green',
                            0.6: 'yellow',
                            0.8: 'orange',
                            1.0: 'red'
                        }
                    ).add_to(map_obj)
                    
                    # Add a timestamp to the map
                    folium.LayerControl().add_to(map_obj)
                    title_html = f'<h3 style="text-align:center;">Global Temperature Anomaly ({datetime.now().strftime("%Y-%m-%d")})</h3>'
                    map_obj.get_root().html.add_child(folium.Element(title_html))
            else:
                # Add info message if no data
                title_html = '<h3 style="text-align:center;">Temperature data unavailable</h3>'
                map_obj.get_root().html.add_child(folium.Element(title_html))
                
            return map_obj
                
        try:
            # Use Earth Engine for the heatmap if available
            # Get recent MODIS Land Surface Temperature
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Use Earth Engine to get MODIS Land Surface Temperature
            lst = ee.ImageCollection('MODIS/006/MOD11A1') \
                .filterDate(start_date, end_date) \
                .select('LST_Day_1km') \
                .mean()
            
            # Convert to Celsius and create anomaly
            lst_celsius = lst.multiply(0.02).subtract(273.15)
            
            # Get the long-term average (example using a fixed value)
            # In a real application, this would be calculated from historical data
            long_term_avg = 14.0  # Global average in Celsius
            anomaly = lst_celsius.subtract(long_term_avg)
            
            # Add the layer to the map
            vis_params = {
                'min': -10,
                'max': 10,
                'palette': ['blue', 'purple', 'cyan', 'green', 'yellow', 'orange', 'red']
            }
            
            # Convert to a geemap object if it's a folium map
            if not isinstance(map_obj, geemap.Map):
                # Extract center and zoom
                center = list(map_obj.location)
                zoom = map_obj.options['zoom_start']
                
                # Create a new geemap Map
                new_map = geemap.Map(location=center, zoom_start=zoom)
                
                # Add the temperature layer
                new_map.add_ee_layer(anomaly, vis_params, 'Temperature Anomaly')
                
                # Update timestamp
                self.last_update = datetime.now()
                
                return new_map
            else:
                # If it's already a geemap object, just add the layer
                map_obj.add_ee_layer(anomaly, vis_params, 'Temperature Anomaly')
                
                # Update timestamp
                self.last_update = datetime.now()
                
                return map_obj
                
        except Exception as e:
            logger.error(f"Error generating temperature heatmap: {str(e)}")
            
            # Add error message to map
            title_html = f'<h3 style="text-align:center;">Error generating temperature heatmap</h3>'
            map_obj.get_root().html.add_child(folium.Element(title_html))
            
            return map_obj
            
    def get_precipitation_heatmap(self, map_obj=None, days_ago=7):
        """
        Generate a global precipitation heatmap.
        
        Args:
            map_obj: Optional folium Map object to add layer to
            days_ago: Days before today to start data collection
            
        Returns:
            Folium map object with precipitation heatmap layer
        """
        if not map_obj:
            map_obj = folium.Map(
    location=[0, 0],
    zoom_start=2,
    tiles="CartoDB Positron"  # Capitalization matters!
)
            
        if not self.earth_engine_initialized:
            # Add message when Earth Engine is not available
            title_html = '<h3 style="text-align:center;">Precipitation heatmap requires Earth Engine access</h3>'
            map_obj.get_root().html.add_child(folium.Element(title_html))
            return map_obj
            
        try:
            # Use Earth Engine for the heatmap
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get GPM precipitation data
            precipitation = ee.ImageCollection('NASA/GPM_L3/IMERG_V06') \
                .filterDate(start_date, end_date) \
                .select('precipitationCal') \
                .mean()
            
            # Add the layer to the map
            vis_params = {
                'min': 0,
                'max': 10,
                'palette': ['white', 'blue', 'purple', 'red']
            }
            
            # Convert to a geemap object if it's a folium map
            if not isinstance(map_obj, geemap.Map):
                # Extract center and zoom
                center = list(map_obj.location)
                zoom = map_obj.options['zoom_start']
                
                # Create a new geemap Map
                new_map = geemap.Map(location=center, zoom_start=zoom)
                
                # Add the precipitation layer
                new_map.add_ee_layer(precipitation, vis_params, 'Precipitation')
                
                # Update timestamp
                self.last_update = datetime.now()
                
                return new_map
            else:
                # If it's already a geemap object, just add the layer
                map_obj.add_ee_layer(precipitation, vis_params, 'Precipitation')
                
                # Update timestamp
                self.last_update = datetime.now()
                
                return map_obj
                
        except Exception as e:
            logger.error(f"Error generating precipitation heatmap: {str(e)}")
            
            # Add error message to map
            title_html = f'<h3 style="text-align:center;">Error generating precipitation heatmap</h3>'
            map_obj.get_root().html.add_child(folium.Element(title_html))
            
            return map_obj
    
    def get_extreme_events_map(self, map_obj=None):
        """
        Generate a map of extreme climate events.
        
        Args:
            map_obj: Optional folium Map object to add layer to
            
        Returns:
            Folium map object with extreme events markers
        """
        if not map_obj:
            map_obj = folium.Map(
    location=[0, 0],
    zoom_start=2,
    tiles="CartoDB Positron"  # Capital 'P'
)
            
        try:
            # Get extreme events from database
            extreme_events = self.data_source.get_extreme_events()
            
            if extreme_events:
                # Add each event as a marker
                for event in extreme_events:
                    # Choose icon and color based on event type
                    icon_map = {
                        'drought': 'tint-slash',
                        'flood': 'water',
                        'wildfire': 'fire',
                        'extreme_weather': 'cloud-bolt',
                        'sea_level': 'water-rise'
                    }
                    
                    color_map = {
                        'drought': 'orange',
                        'flood': 'blue',
                        'wildfire': 'red',
                        'extreme_weather': 'purple',
                        'sea_level': 'darkblue'
                    }
                    
                    icon_name = icon_map.get(event['alert_type'], 'exclamation')
                    color = color_map.get(event['alert_type'], 'gray')
                    
                    # Create a popup with event information
                    popup_html = f"""
                    <div style="width:250px;">
                        <h4>{event['title']}</h4>
                        <p><strong>Type:</strong> {event['alert_type'].replace('_', ' ').title()}</p>
                        <p><strong>Severity:</strong> {event['severity']}/5</p>
                        <p><strong>Region:</strong> {event['region']}</p>
                        <p>{event['description']}</p>
                        <p><small>Issued: {event['issued_at']}</small></p>
                    </div>
                    """
                    
                    folium.Marker(
                        location=[event['latitude'], event['longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(color=color, icon=icon_name, prefix='fa')
                    ).add_to(map_obj)
                
                # Add a legend
                legend_html = """
                <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.3);">
                    <h4>Event Types</h4>
                    <div><i class="fa fa-tint-slash" style="color: orange;"></i> Drought</div>
                    <div><i class="fa fa-water" style="color: blue;"></i> Flood</div>
                    <div><i class="fa fa-fire" style="color: red;"></i> Wildfire</div>
                    <div><i class="fa fa-cloud-bolt" style="color: purple;"></i> Extreme Weather</div>
                    <div><i class="fa fa-water-rise" style="color: darkblue;"></i> Sea Level</div>
                </div>
                """
                map_obj.get_root().html.add_child(folium.Element(legend_html))
            
            # Add a timestamp to the map
            title_html = f'<h3 style="text-align:center;">Extreme Climate Events ({datetime.now().strftime("%Y-%m-%d")})</h3>'
            map_obj.get_root().html.add_child(folium.Element(title_html))
            
            return map_obj
            
        except Exception as e:
            logger.error(f"Error generating extreme events map: {str(e)}")
            
            # Add error message to map
            title_html = f'<h3 style="text-align:center;">Error loading extreme events</h3>'
            map_obj.get_root().html.add_child(folium.Element(title_html))
            
            return map_obj
    
    def get_combined_climate_map(self, center_lat=0, center_lon=0, zoom=2):
        """
        Create a combined climate map with multiple layers.
        
        Args:
            center_lat: Center latitude for the map
            center_lon: Center longitude for the map
            zoom: Initial zoom level
            
        Returns:
            Map object with multiple climate layers
        """
        try:
            if self.earth_engine_initialized:
                # Create a geemap Map
                m = geemap.Map(location=[center_lat, center_lon], zoom_start=zoom)
                
                # Add temperature layer
                self.get_temperature_heatmap(m)
                
                # Add precipitation layer
                self.get_precipitation_heatmap(m)
                
                # Add extreme events layer
                self._add_extreme_events_to_geemap(m)
                
                # Add layer control
                m.add_layer_control()
                
                return m
            else:
                # Create a folium Map
                m = folium.Map(    location=[center_lat, center_lon],    zoom_start=zoom,    tiles="CartoDB Positron")
                
                # Add temperature layer using database
                self.get_temperature_heatmap(m)
                
                # Add extreme events layer
                self.get_extreme_events_map(m)
                
                # Add layer control
                folium.LayerControl().add_to(m)
                
                return m
                
        except Exception as e:
            logger.error(f"Error generating combined climate map: {str(e)}")
            
            # Return a basic map with error message
            m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB Positron")
            
            title_html = f'<h3 style="text-align:center;">Error generating climate map: {str(e)}</h3>'
            m.get_root().html.add_child(folium.Element(title_html))
            
            return m
    
    def _get_temperature_from_database(self, days_ago=7):
        """
        Get temperature data from database.
        
        Args:
            days_ago: Number of days ago to get data for
            
        Returns:
            Pandas DataFrame with temperature data
        """
        try:
            # Use the data source to get temperature data
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            return self.data_source.get_temperature_data(start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting temperature data from database: {str(e)}")
            return None
    
    def _add_extreme_events_to_geemap(self, map_obj):
        """
        Add extreme events to a geemap Map.
        
        Args:
            map_obj: geemap Map object
            
        Returns:
            None (modifies map_obj in place)
        """
        try:
            # Get extreme events
            extreme_events = self.data_source.get_extreme_events()
            
            if not extreme_events:
                return
                
            # Create a GeoJSON FeatureCollection for the events
            features = []
            
            for event in extreme_events:
                # Create a GeoJSON feature
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [event['longitude'], event['latitude']]
                    },
                    'properties': {
                        'title': event['title'],
                        'type': event['alert_type'],
                        'severity': event['severity'],
                        'region': event['region'],
                        'description': event['description']
                    }
                }
                
                features.append(feature)
            
            # Create a GeoJSON layer
            geojson_layer = folium.GeoJson(
                {
                    'type': 'FeatureCollection',
                    'features': features
                },
                name='Extreme Events',
                popup=folium.GeoJsonPopup(
                    fields=['title', 'type', 'severity', 'region', 'description'],
                    aliases=['Title', 'Type', 'Severity', 'Region', 'Description'],
                    localize=True,
                    style="max-width: 250px;"
                )
            )
            
            # Add the layer to the map
            geojson_layer.add_to(map_obj)
            
        except Exception as e:
            logger.error(f"Error adding extreme events to geemap: {str(e)}")
            
    def get_heatmap_stats(self):
        """
        Get statistics about the current heatmap.
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = {
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "data_sources": ["MODIS Land Surface Temperature", "NASA GPM Precipitation", "Database events"],
                "coverage": "Global",
                "resolution": "1km (temperature), 10km (precipitation)"
            }
            
            # Add some statistics based on current extreme events
            extreme_events = self.data_source.get_extreme_events()
            
            if extreme_events:
                event_types = {}
                regions = {}
                total_severity = 0
                
                for event in extreme_events:
                    event_type = event['alert_type']
                    region = event['region']
                    severity = event['severity']
                    
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                    regions[region] = regions.get(region, 0) + 1
                    total_severity += severity
                
                avg_severity = total_severity / len(extreme_events)
                most_affected_region = max(regions.items(), key=lambda x: x[1])[0]
                most_common_event = max(event_types.items(), key=lambda x: x[1])[0]
                
                stats.update({
                    "active_events": len(extreme_events),
                    "average_severity": round(avg_severity, 1),
                    "most_affected_region": most_affected_region,
                    "most_common_event_type": most_common_event.replace('_', ' ').title()
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting heatmap stats: {str(e)}")
            return {
                "error": str(e),
                "last_update": None
            }