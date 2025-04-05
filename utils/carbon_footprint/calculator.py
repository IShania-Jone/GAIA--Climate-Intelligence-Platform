"""
Carbon Footprint Calculator for GAIA-∞ Climate Intelligence Platform.

This module provides comprehensive carbon footprint calculation capabilities
for individuals, organizations, products, and events.
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

class CarbonFootprintCalculator:
    """
    Carbon footprint calculator for evaluating emissions from various activities.
    """
    
    def __init__(self):
        # Emission factors for different activities
        self.electricity_factors = self._load_electricity_factors()
        self.transportation_factors = self._load_transportation_factors()
        self.food_factors = self._load_food_factors()
        self.product_factors = self._load_product_factors()
        self.building_factors = self._load_building_factors()
    
    def _load_electricity_factors(self):
        """Load emission factors for electricity by region/source."""
        return {
            # Electricity emission factors by country (kg CO2e per kWh)
            'country': {
                'global_average': 0.475,
                'usa': 0.417,
                'china': 0.555,
                'india': 0.708,
                'eu_average': 0.275,
                'uk': 0.233,
                'france': 0.056,  # Low due to nuclear
                'germany': 0.338,
                'australia': 0.660,
                'canada': 0.120,
                'brazil': 0.074,  # Low due to hydro
                'south_africa': 0.869
            },
            # Emission factors by source (kg CO2e per kWh)
            'source': {
                'coal': 0.920,
                'natural_gas': 0.490,
                'oil': 0.650,
                'nuclear': 0.012,
                'solar': 0.045,
                'wind': 0.011,
                'hydro': 0.024,
                'geothermal': 0.038,
                'biomass': 0.230
            }
        }
    
    def _load_transportation_factors(self):
        """Load emission factors for transportation."""
        return {
            # Passenger transport (kg CO2e per passenger-km)
            'passenger': {
                'car_petrol': 0.192,
                'car_diesel': 0.171,
                'car_hybrid': 0.106,
                'car_electric': {
                    'global_average': 0.081,  # Depends on electricity mix
                    'usa': 0.071,
                    'eu_average': 0.047
                },
                'motorcycle': 0.103,
                'bus': 0.105,
                'train_local': 0.041,
                'train_high_speed': 0.006,
                'subway': 0.027,
                'ferry': 0.115,
                'airplane_short_haul': 0.156,
                'airplane_medium_haul': 0.138,
                'airplane_long_haul': 0.110,
                'bicycle': 0.005,
                'walking': 0.000
            },
            # Freight transport (kg CO2e per tonne-km)
            'freight': {
                'truck_large': 0.092,
                'truck_medium': 0.135,
                'train': 0.028,
                'ship_container': 0.008,
                'ship_bulk': 0.005,
                'airplane_freight': 0.800
            }
        }
    
    def _load_food_factors(self):
        """Load emission factors for food production."""
        return {
            # Food emission factors (kg CO2e per kg food)
            'beef': 60.0,
            'lamb': 24.0,
            'pork': 7.0,
            'chicken': 6.0,
            'fish_farmed': 5.0,
            'fish_wild': 3.0,
            'eggs': 4.5,
            'milk': 1.9,
            'cheese': 13.5,
            'rice': 4.0,
            'wheat': 1.4,
            'corn': 1.0,
            'potatoes': 0.3,
            'vegetables_average': 0.5,
            'fruits_average': 0.4,
            'legumes': 0.9,
            'tofu': 2.0,
            'nuts': 1.5,
            'chocolate': 19.0,
            'coffee': 17.0
        }
    
    def _load_product_factors(self):
        """Load emission factors for products."""
        return {
            # Product emission factors (kg CO2e per unit or kg)
            'electronics': {
                'smartphone': 70.0,  # per device
                'laptop': 300.0,     # per device
                'desktop_computer': 500.0,  # per device
                'tv_lcd': 300.0,    # per device
                'tablet': 100.0     # per device
            },
            'clothing': {
                'cotton_shirt': 7.0,  # per item
                'jeans': 25.0,       # per item
                'synthetic_shirt': 5.5,  # per item
                'wool_sweater': 20.0,    # per item
                'shoes_leather': 15.0    # per pair
            },
            'materials': {
                'paper': 1.1,       # per kg
                'plastic': 3.5,     # per kg
                'aluminum': 8.0,    # per kg
                'steel': 1.9,       # per kg
                'glass': 0.85,      # per kg
                'concrete': 0.11,   # per kg
                'timber': 0.45      # per kg
            }
        }
    
    def _load_building_factors(self):
        """Load emission factors for buildings."""
        return {
            # Building emission factors
            'heating': {
                'natural_gas': 0.198,  # kg CO2e per kWh
                'heating_oil': 0.266,  # kg CO2e per kWh
                'propane': 0.215,      # kg CO2e per kWh
                'biomass': 0.029,      # kg CO2e per kWh
                'district_heating': 0.072  # kg CO2e per kWh
            },
            'cooling': {
                'electricity_based': 'use_electricity_factors'  # Use electricity factors
            },
            'water': {
                'supply': 0.344,        # kg CO2e per cubic meter
                'treatment': 0.708      # kg CO2e per cubic meter
            },
            'construction': {
                'residential_per_sqm': 500.0,  # kg CO2e per square meter
                'commercial_per_sqm': 800.0,   # kg CO2e per square meter
                'industrial_per_sqm': 1200.0   # kg CO2e per square meter
            }
        }
    
    def calculate_electricity_emissions(self, kwh, location='global_average', source=None):
        """
        Calculate emissions from electricity consumption.
        
        Args:
            kwh: Electricity consumption in kilowatt-hours
            location: Country or region
            source: Energy source if known (overrides location factor)
            
        Returns:
            Emissions in kg CO2e
        """
        if source and source in self.electricity_factors['source']:
            # Use source-specific factor
            factor = self.electricity_factors['source'][source]
        elif location in self.electricity_factors['country']:
            # Use location-specific factor
            factor = self.electricity_factors['country'][location]
        else:
            # Use global average
            factor = self.electricity_factors['country']['global_average']
            
        return kwh * factor
    
    def calculate_transportation_emissions(self, distance, mode, passengers=1, weight=None, location='global_average'):
        """
        Calculate emissions from transportation.
        
        Args:
            distance: Distance traveled in kilometers
            mode: Transportation mode
            passengers: Number of passengers (for passenger transport)
            weight: Weight in tonnes (for freight transport)
            location: Location for electric vehicles
            
        Returns:
            Emissions in kg CO2e
        """
        if mode in self.transportation_factors['passenger']:
            # Passenger transport
            if mode == 'car_electric' and isinstance(self.transportation_factors['passenger'][mode], dict):
                # Electric car depends on electricity mix
                if location in self.transportation_factors['passenger'][mode]:
                    factor = self.transportation_factors['passenger'][mode][location]
                else:
                    factor = self.transportation_factors['passenger'][mode]['global_average']
            else:
                factor = self.transportation_factors['passenger'][mode]
                
            # Calculate total emissions and divide by passengers for shared transport
            return distance * factor * (1 / passengers)
            
        elif mode in self.transportation_factors['freight'] and weight is not None:
            # Freight transport
            factor = self.transportation_factors['freight'][mode]
            return distance * weight * factor
            
        else:
            # Unknown mode
            return 0
    
    def calculate_food_emissions(self, food_consumption):
        """
        Calculate emissions from food consumption.
        
        Args:
            food_consumption: Dictionary mapping food types to amounts in kg
            
        Returns:
            Dictionary with emissions per food type and total
        """
        emissions = {}
        total = 0
        
        for food_type, amount in food_consumption.items():
            if food_type in self.food_factors:
                food_emission = amount * self.food_factors[food_type]
                emissions[food_type] = food_emission
                total += food_emission
                
        emissions['total'] = total
        return emissions
    
    def calculate_product_emissions(self, product_data):
        """
        Calculate emissions from products.
        
        Args:
            product_data: Dictionary with product categories, types, and quantities
            
        Returns:
            Dictionary with emissions per category and total
        """
        emissions = {'total': 0}
        
        for category, products in product_data.items():
            if category in self.product_factors:
                category_emissions = 0
                
                for product_type, quantity in products.items():
                    if product_type in self.product_factors[category]:
                        product_emission = quantity * self.product_factors[category][product_type]
                        category_emissions += product_emission
                
                emissions[category] = category_emissions
                emissions['total'] += category_emissions
                
        return emissions
    
    def calculate_building_emissions(self, building_data):
        """
        Calculate emissions from buildings.
        
        Args:
            building_data: Dictionary with building parameters
                - area: Building area in square meters
                - type: Building type (residential, commercial, industrial)
                - heating_type: Type of heating
                - heating_energy: Heating energy in kWh
                - electricity: Electricity consumption in kWh
                - water_supply: Water supply in cubic meters
                - water_treatment: Water treatment in cubic meters
                - location: Location for electricity emissions
                
        Returns:
            Dictionary with building emissions by category and total
        """
        emissions = {}
        total = 0
        
        # Construction emissions (one-time, usually amortized over building life)
        if 'area' in building_data and 'type' in building_data:
            building_type = building_data['type']
            area = building_data['area']
            
            if building_type + '_per_sqm' in self.building_factors['construction']:
                construction_factor = self.building_factors['construction'][building_type + '_per_sqm']
                construction_emissions = area * construction_factor
                
                # Typically amortized over 50 years
                emissions['construction'] = construction_emissions / 50
                total += emissions['construction']
        
        # Heating emissions
        if 'heating_type' in building_data and 'heating_energy' in building_data:
            heating_type = building_data['heating_type']
            heating_energy = building_data['heating_energy']
            
            if heating_type in self.building_factors['heating']:
                heating_factor = self.building_factors['heating'][heating_type]
                emissions['heating'] = heating_energy * heating_factor
                total += emissions['heating']
        
        # Electricity emissions (for appliances, lighting, cooling)
        if 'electricity' in building_data:
            electricity = building_data['electricity']
            location = building_data.get('location', 'global_average')
            
            emissions['electricity'] = self.calculate_electricity_emissions(electricity, location)
            total += emissions['electricity']
        
        # Water-related emissions
        if 'water_supply' in building_data:
            water_supply = building_data['water_supply']
            emissions['water_supply'] = water_supply * self.building_factors['water']['supply']
            total += emissions['water_supply']
            
        if 'water_treatment' in building_data:
            water_treatment = building_data['water_treatment']
            emissions['water_treatment'] = water_treatment * self.building_factors['water']['treatment']
            total += emissions['water_treatment']
        
        emissions['total'] = total
        return emissions
    
    def calculate_individual_footprint(self, individual_data):
        """
        Calculate the carbon footprint for an individual.
        
        Args:
            individual_data: Dictionary with individual consumption data
                - electricity: Electricity consumption in kWh
                - electricity_location: Location for electricity
                - transportation: List of transportation activities
                    - mode: Transportation mode
                    - distance: Distance in km
                    - passengers: Number of passengers
                - food: Dictionary of food consumption in kg
                - products: Dictionary of product purchases
                - home: Building data for home
                
        Returns:
            Dictionary with carbon footprint by category and total
        """
        footprint = {'categories': {}}
        total = 0
        
        # Electricity emissions
        if 'electricity' in individual_data:
            electricity = individual_data['electricity']
            location = individual_data.get('electricity_location', 'global_average')
            
            footprint['categories']['electricity'] = self.calculate_electricity_emissions(electricity, location)
            total += footprint['categories']['electricity']
        
        # Transportation emissions
        if 'transportation' in individual_data:
            transportation_emissions = 0
            
            for activity in individual_data['transportation']:
                mode = activity.get('mode')
                distance = activity.get('distance', 0)
                passengers = activity.get('passengers', 1)
                location = activity.get('location', 'global_average')
                
                transportation_emissions += self.calculate_transportation_emissions(
                    distance, mode, passengers, location=location
                )
                
            footprint['categories']['transportation'] = transportation_emissions
            total += transportation_emissions
        
        # Food emissions
        if 'food' in individual_data:
            food_results = self.calculate_food_emissions(individual_data['food'])
            footprint['categories']['food'] = food_results['total']
            footprint['food_detail'] = {k: v for k, v in food_results.items() if k != 'total'}
            total += food_results['total']
        
        # Product emissions
        if 'products' in individual_data:
            product_results = self.calculate_product_emissions(individual_data['products'])
            footprint['categories']['products'] = product_results['total']
            footprint['product_detail'] = {k: v for k, v in product_results.items() if k != 'total'}
            total += product_results['total']
        
        # Home emissions
        if 'home' in individual_data:
            home_results = self.calculate_building_emissions(individual_data['home'])
            footprint['categories']['home'] = home_results['total']
            footprint['home_detail'] = {k: v for k, v in home_results.items() if k != 'total'}
            total += home_results['total']
        
        footprint['total'] = total
        
        # Convert to tonnes for easier reading
        footprint['total_tonnes'] = total / 1000
        
        return footprint
    
    def calculate_organization_footprint(self, organization_data):
        """
        Calculate the carbon footprint for an organization.
        
        Args:
            organization_data: Dictionary with organization consumption data
                - electricity: Electricity consumption in kWh
                - electricity_location: Location for electricity
                - transportation: Transportation activities
                    - employee_commute: List of commute patterns
                    - business_travel: List of business trips
                    - fleet: List of company fleet activities
                    - shipping: List of shipping activities
                - buildings: List of building data
                - products: Product manufacturing data
                - waste: Waste generation data
                
        Returns:
            Dictionary with carbon footprint by category and total
        """
        footprint = {'categories': {}, 'scopes': {}}
        total = 0
        
        # Scope 1: Direct emissions
        scope1 = 0
        
        # Fleet emissions (Scope 1)
        if 'transportation' in organization_data and 'fleet' in organization_data['transportation']:
            fleet_emissions = 0
            
            for activity in organization_data['transportation']['fleet']:
                mode = activity.get('mode')
                distance = activity.get('distance', 0)
                passengers = activity.get('passengers', 1)
                weight = activity.get('weight')
                
                fleet_emissions += self.calculate_transportation_emissions(
                    distance, mode, passengers, weight
                )
                
            footprint['categories']['fleet'] = fleet_emissions
            scope1 += fleet_emissions
            total += fleet_emissions
        
        # Building direct emissions (Scope 1)
        building_direct_emissions = 0
        if 'buildings' in organization_data:
            for building in organization_data['buildings']:
                # Heating emissions if using fuels directly
                if 'heating_type' in building and 'heating_energy' in building:
                    heating_type = building['heating_type']
                    if heating_type in ['natural_gas', 'heating_oil', 'propane']:
                        heating_energy = building['heating_energy']
                        heating_factor = self.building_factors['heating'][heating_type]
                        building_direct_emissions += heating_energy * heating_factor
            
            footprint['categories']['building_direct'] = building_direct_emissions
            scope1 += building_direct_emissions
            total += building_direct_emissions
        
        # Scope 2: Indirect emissions from purchased energy
        scope2 = 0
        
        # Electricity emissions (Scope 2)
        if 'electricity' in organization_data:
            electricity = organization_data['electricity']
            location = organization_data.get('electricity_location', 'global_average')
            
            electricity_emissions = self.calculate_electricity_emissions(electricity, location)
            footprint['categories']['electricity'] = electricity_emissions
            scope2 += electricity_emissions
            total += electricity_emissions
        
        # Building electricity (Scope 2)
        building_indirect_emissions = 0
        if 'buildings' in organization_data:
            for building in organization_data['buildings']:
                if 'electricity' in building:
                    electricity = building['electricity']
                    location = building.get('location', 'global_average')
                    building_indirect_emissions += self.calculate_electricity_emissions(electricity, location)
            
            if 'electricity' not in organization_data:  # Avoid double counting
                footprint['categories']['building_electricity'] = building_indirect_emissions
                scope2 += building_indirect_emissions
                total += building_indirect_emissions
        
        # Scope 3: Other indirect emissions
        scope3 = 0
        
        # Employee commute (Scope 3)
        if 'transportation' in organization_data and 'employee_commute' in organization_data['transportation']:
            commute_emissions = 0
            
            for commute in organization_data['transportation']['employee_commute']:
                mode = commute.get('mode')
                distance = commute.get('distance', 0)
                days_per_year = commute.get('days_per_year', 220)  # Default working days
                employees = commute.get('employees', 1)
                passengers = commute.get('passengers', 1)
                location = commute.get('location', 'global_average')
                
                emissions_per_day = self.calculate_transportation_emissions(
                    distance * 2,  # Round trip
                    mode,
                    passengers,
                    location=location
                )
                
                commute_emissions += emissions_per_day * days_per_year * employees
                
            footprint['categories']['employee_commute'] = commute_emissions
            scope3 += commute_emissions
            total += commute_emissions
        
        # Business travel (Scope 3)
        if 'transportation' in organization_data and 'business_travel' in organization_data['transportation']:
            travel_emissions = 0
            
            for trip in organization_data['transportation']['business_travel']:
                mode = trip.get('mode')
                distance = trip.get('distance', 0)
                passengers = trip.get('passengers', 1)
                location = trip.get('location', 'global_average')
                
                travel_emissions += self.calculate_transportation_emissions(
                    distance,
                    mode,
                    passengers,
                    location=location
                )
                
            footprint['categories']['business_travel'] = travel_emissions
            scope3 += travel_emissions
            total += travel_emissions
        
        # Shipping (Scope 3)
        if 'transportation' in organization_data and 'shipping' in organization_data['transportation']:
            shipping_emissions = 0
            
            for shipment in organization_data['transportation']['shipping']:
                mode = shipment.get('mode')
                distance = shipment.get('distance', 0)
                weight = shipment.get('weight')
                
                shipping_emissions += self.calculate_transportation_emissions(
                    distance,
                    mode,
                    weight=weight
                )
                
            footprint['categories']['shipping'] = shipping_emissions
            scope3 += shipping_emissions
            total += shipping_emissions
        
        # Product emissions (Scope 3)
        if 'products' in organization_data:
            product_results = self.calculate_product_emissions(organization_data['products'])
            footprint['categories']['products'] = product_results['total']
            footprint['product_detail'] = {k: v for k, v in product_results.items() if k != 'total'}
            scope3 += product_results['total']
            total += product_results['total']
        
        # Waste emissions (Scope 3)
        if 'waste' in organization_data:
            waste_emissions = 0
            
            for waste_type, amount in organization_data['waste'].items():
                # Simplified waste factors (kg CO2e per kg waste)
                waste_factors = {
                    'landfill': 0.580,
                    'recycling': 0.040,
                    'composting': 0.010,
                    'incineration': 0.210
                }
                
                if waste_type in waste_factors:
                    waste_emissions += amount * waste_factors[waste_type]
                    
            footprint['categories']['waste'] = waste_emissions
            scope3 += waste_emissions
            total += waste_emissions
        
        # Set scope totals
        footprint['scopes'] = {
            'scope1': scope1,
            'scope2': scope2,
            'scope3': scope3
        }
        
        footprint['total'] = total
        
        # Convert to tonnes for easier reading
        footprint['total_tonnes'] = total / 1000
        
        return footprint
    
    def visualize_footprint(self, footprint_data, title="Carbon Footprint Breakdown"):
        """
        Create a visualization of carbon footprint data.
        
        Args:
            footprint_data: Result from one of the footprint calculation methods
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if 'categories' not in footprint_data:
            # Create an empty figure with a message
            fig = go.Figure()
            fig.update_layout(
                title="No Carbon Footprint Data Available",
                annotations=[dict(
                    text="No footprint data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
        
        # Prepare data for visualization
        categories = []
        values = []
        
        # Extract categories and values
        for category, value in footprint_data['categories'].items():
            categories.append(category.replace('_', ' ').title())
            values.append(value)
        
        # Create color scale
        colors = px.colors.sequential.Viridis[:len(categories)]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            insidetextorientation='radial'
        )])
        
        fig.update_layout(
            title=f"{title}<br>Total: {footprint_data['total_tonnes']:.2f} tonnes CO₂e",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            template="plotly_white"
        )
        
        return fig
    
    def visualize_organization_scopes(self, footprint_data):
        """
        Create a visualization of organizational carbon footprint by scope.
        
        Args:
            footprint_data: Result from calculate_organization_footprint
            
        Returns:
            Plotly figure
        """
        if 'scopes' not in footprint_data:
            # Create an empty figure with a message
            fig = go.Figure()
            fig.update_layout(
                title="No Scope Data Available",
                annotations=[dict(
                    text="No scope data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
        
        # Prepare data for visualization
        scopes = []
        values = []
        
        # Extract scopes and values
        for scope, value in footprint_data['scopes'].items():
            scopes.append(scope.upper())
            values.append(value)
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=scopes,
            y=values,
            marker_color=['#3366CC', '#DC3912', '#FF9900'],
            text=[f"{v/1000:.2f} tonnes" for v in values],
            textposition='auto',
        )])
        
        fig.update_layout(
            title=f"Carbon Footprint by Scope<br>Total: {footprint_data['total_tonnes']:.2f} tonnes CO₂e",
            xaxis_title="Emission Scope",
            yaxis_title="Emissions (kg CO₂e)",
            template="plotly_white"
        )
        
        return fig
    
    def compare_to_average(self, individual_footprint, country='global'):
        """
        Compare an individual's footprint to average footprints.
        
        Args:
            individual_footprint: Result from calculate_individual_footprint
            country: Country to compare against
            
        Returns:
            Dictionary with comparison data
        """
        if 'total_tonnes' not in individual_footprint:
            return {
                'status': 'error',
                'message': 'Invalid footprint data'
            }
            
        # Average annual footprints in tonnes CO2e per capita
        averages = {
            'global': 4.7,
            'usa': 15.5,
            'canada': 15.5,
            'australia': 15.4,
            'russia': 11.5,
            'japan': 8.7,
            'china': 7.4,
            'uk': 5.5,
            'france': 4.6,
            'italy': 5.4,
            'brazil': 2.3,
            'india': 1.9,
            'sustainable': 2.0  # Science-based target for limiting warming to 1.5°C
        }
        
        # Get relevant average
        if country in averages:
            reference = averages[country]
        else:
            reference = averages['global']
            country = 'global'
            
        # Calculate percentage difference
        individual = individual_footprint['total_tonnes']
        percentage_diff = ((individual - reference) / reference) * 100
        
        # Determine sustainability rating
        if individual <= averages['sustainable']:
            rating = 'Sustainable'
            description = 'Your footprint is within sustainable limits'
        elif individual <= reference * 0.5:
            rating = 'Excellent'
            description = f'Your footprint is less than half the {country} average'
        elif individual <= reference * 0.8:
            rating = 'Very Good'
            description = f'Your footprint is significantly below the {country} average'
        elif individual <= reference * 1.0:
            rating = 'Good'
            description = f'Your footprint is below the {country} average'
        elif individual <= reference * 1.2:
            rating = 'Fair'
            description = f'Your footprint is slightly above the {country} average'
        elif individual <= reference * 1.5:
            rating = 'Poor'
            description = f'Your footprint is significantly above the {country} average'
        else:
            rating = 'Very Poor'
            description = f'Your footprint is more than 50% above the {country} average'
            
        return {
            'individual_tonnes': individual,
            'reference_tonnes': reference,
            'reference_type': f'{country} average',
            'difference_tonnes': individual - reference,
            'percentage_difference': percentage_diff,
            'rating': rating,
            'description': description,
            'sustainable_target': averages['sustainable'],
            'sustainable_difference': individual - averages['sustainable']
        }
        
    def recommend_reductions(self, footprint_data):
        """
        Provide recommendations for reducing carbon footprint.
        
        Args:
            footprint_data: Result from a footprint calculation
            
        Returns:
            List of recommendations with potential savings
        """
        if 'categories' not in footprint_data:
            return []
            
        recommendations = []
        
        # Identify top emission categories
        categories = footprint_data['categories']
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        # General recommendations based on top categories
        for category, emissions in sorted_categories[:3]:
            if category == 'electricity':
                recommendations.extend([
                    {
                        'category': 'electricity',
                        'action': 'Switch to renewable energy provider',
                        'potential_savings': 0.85 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'Low'
                    },
                    {
                        'category': 'electricity',
                        'action': 'Replace lighting with LED bulbs',
                        'potential_savings': 0.05 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'Low-Medium'
                    },
                    {
                        'category': 'electricity',
                        'action': 'Install smart thermostats and energy monitors',
                        'potential_savings': 0.15 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Medium'
                    }
                ])
                
            elif category == 'transportation':
                recommendations.extend([
                    {
                        'category': 'transportation',
                        'action': 'Replace car trips under 2km with walking or cycling',
                        'potential_savings': 0.05 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'None'
                    },
                    {
                        'category': 'transportation',
                        'action': 'Use public transportation instead of driving',
                        'potential_savings': 0.3 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Low'
                    },
                    {
                        'category': 'transportation',
                        'action': 'Switch to an electric or hybrid vehicle',
                        'potential_savings': 0.6 * emissions,
                        'difficulty': 'Hard',
                        'cost': 'High'
                    },
                    {
                        'category': 'transportation',
                        'action': 'Reduce air travel and choose direct flights',
                        'potential_savings': 0.2 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'None'
                    }
                ])
                
            elif category == 'food':
                recommendations.extend([
                    {
                        'category': 'food',
                        'action': 'Reduce beef consumption by 50%',
                        'potential_savings': 0.3 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'None'
                    },
                    {
                        'category': 'food',
                        'action': 'Adopt a plant-based diet one day per week',
                        'potential_savings': 0.15 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'None'
                    },
                    {
                        'category': 'food',
                        'action': 'Reduce food waste by 50%',
                        'potential_savings': 0.1 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'Negative (saves money)'
                    },
                    {
                        'category': 'food',
                        'action': 'Buy local and seasonal produce',
                        'potential_savings': 0.05 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Low'
                    }
                ])
                
            elif category == 'home' or category == 'building_direct' or category == 'building_electricity':
                recommendations.extend([
                    {
                        'category': 'home',
                        'action': 'Improve insulation and seal air leaks',
                        'potential_savings': 0.2 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Medium-High'
                    },
                    {
                        'category': 'home',
                        'action': 'Install a heat pump instead of gas heating',
                        'potential_savings': 0.5 * emissions,
                        'difficulty': 'Hard',
                        'cost': 'High'
                    },
                    {
                        'category': 'home',
                        'action': 'Install solar panels',
                        'potential_savings': 0.4 * emissions,
                        'difficulty': 'Hard',
                        'cost': 'High'
                    },
                    {
                        'category': 'home',
                        'action': 'Reduce heating by 1-2°C and cooling by 1-2°C',
                        'potential_savings': 0.1 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'None'
                    }
                ])
                
            elif category == 'products':
                recommendations.extend([
                    {
                        'category': 'products',
                        'action': 'Extend product lifetimes by repairing instead of replacing',
                        'potential_savings': 0.2 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Negative (saves money)'
                    },
                    {
                        'category': 'products',
                        'action': 'Buy second-hand products when possible',
                        'potential_savings': 0.3 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'Negative (saves money)'
                    },
                    {
                        'category': 'products',
                        'action': 'Invest in high-quality, durable products',
                        'potential_savings': 0.15 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Medium'
                    }
                ])
                
            elif category == 'waste':
                recommendations.extend([
                    {
                        'category': 'waste',
                        'action': 'Implement comprehensive recycling',
                        'potential_savings': 0.3 * emissions,
                        'difficulty': 'Easy',
                        'cost': 'None'
                    },
                    {
                        'category': 'waste',
                        'action': 'Compost organic waste',
                        'potential_savings': 0.2 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'Low'
                    },
                    {
                        'category': 'waste',
                        'action': 'Reduce packaging waste with bulk buying',
                        'potential_savings': 0.1 * emissions,
                        'difficulty': 'Medium',
                        'cost': 'None'
                    }
                ])
        
        # Sort recommendations by potential savings
        recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
        
        # Format savings as kg CO2e
        for recommendation in recommendations:
            recommendation['potential_savings_kg'] = recommendation['potential_savings']
            
        return recommendations
    
    def visualize_reduction_potential(self, recommendations):
        """
        Create a visualization of emission reduction recommendations.
        
        Args:
            recommendations: Result from recommend_reductions
            
        Returns:
            Plotly figure
        """
        if not recommendations:
            # Create an empty figure with a message
            fig = go.Figure()
            fig.update_layout(
                title="No Reduction Recommendations Available",
                annotations=[dict(
                    text="No recommendation data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
        
        # Prepare data for visualization
        actions = []
        savings = []
        categories = []
        difficulties = []
        costs = []
        
        # Use a maximum of top 10 recommendations for clarity
        for recommendation in recommendations[:10]:
            actions.append(recommendation['action'])
            savings.append(recommendation['potential_savings_kg'])
            categories.append(recommendation['category'])
            difficulties.append(recommendation['difficulty'])
            costs.append(recommendation['cost'])
        
        # Create color mapping for categories
        category_colors = {
            'electricity': '#3366CC',
            'transportation': '#DC3912',
            'food': '#FF9900',
            'home': '#109618',
            'products': '#990099',
            'waste': '#0099C6'
        }
        
        colors = [category_colors.get(cat, '#BBBBBB') for cat in categories]
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=actions,
            x=savings,
            orientation='h',
            marker_color=colors,
            text=[f"{s:.1f} kg CO₂e" for s in savings],
            textposition='auto',
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Potential Savings: %{x:.1f} kg CO₂e<br>" +
                "Category: %{customdata[0]}<br>" +
                "Difficulty: %{customdata[1]}<br>" +
                "Cost: %{customdata[2]}"
            ),
            customdata=list(zip(categories, difficulties, costs))
        ))
        
        # Update layout
        fig.update_layout(
            title="Top Emission Reduction Opportunities",
            xaxis_title="Potential Savings (kg CO₂e)",
            yaxis_title="Recommended Action",
            template="plotly_white",
            height=500 + len(actions) * 30  # Adjust height based on number of actions
        )
        
        # Sort bars by savings
        fig.update_layout(
            yaxis={'categoryorder': 'array', 'categoryarray': actions[::-1]}
        )
        
        return fig