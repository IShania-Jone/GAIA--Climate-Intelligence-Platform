"""
Advanced Climate Simulation Engine for GAIA-∞ Climate Intelligence Platform.

This module provides a sophisticated climate simulation engine using coupled
differential equations to model climate system dynamics and predict future
climate states under different scenarios.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

class AdvancedClimateSimulator:
    """
    Advanced climate simulation engine for GAIA-∞.
    Uses coupled differential equations to model climate system dynamics.
    """
    
    def __init__(self):
        self.parameters = {
            'carbon_sensitivity': 3.0,  # Climate sensitivity to CO2 doubling (°C)
            'ocean_heat_capacity': 14.0,  # Ocean heat capacity (W yr m^-2 K^-1)
            'carbon_cycle_feedback': 0.15,  # Carbon cycle feedback parameter
            'aerosol_forcing': -1.1,  # Aerosol forcing (W/m^2)
            'ocean_carbon_uptake': 0.7,  # Fraction of emissions absorbed by ocean
            'land_carbon_uptake': 0.3,  # Fraction of emissions absorbed by land
            'permafrost_feedback': 0.1,  # Permafrost feedback factor
            'albedo_feedback': 0.3,  # Ice-albedo feedback factor
        }
        
        # Initial conditions for state variables
        self.initial_state = {
            'temperature': 1.1,  # Current temperature anomaly (°C)
            'co2_concentration': 417.0,  # Current CO2 concentration (ppm)
            'ocean_heat': 10.0,  # Ocean heat content (10^22 J)
            'sea_level': 0.0,  # Sea level rise (m)
            'ice_extent': 10.5,  # Arctic sea ice extent (million km^2)
        }
        
    def set_parameters(self, new_parameters):
        """Update simulation parameters."""
        self.parameters.update(new_parameters)
        
    def set_initial_state(self, new_state):
        """Update initial conditions."""
        self.initial_state.update(new_state)
    
    def climate_system_dynamics(self, t, y, emissions_scenario):
        """
        Define the system of differential equations that govern climate dynamics.
        
        Args:
            t: Time variable
            y: State vector [temperature, co2, ocean_heat, sea_level, ice_extent]
            emissions_scenario: Function that returns emissions at time t
            
        Returns:
            Derivatives of state variables
        """
        temp, co2, ocean_heat, sea_level, ice_extent = y
        
        # Get current emissions from scenario
        emissions = emissions_scenario(t)
        
        # Carbon cycle
        # CO2 concentration change depends on emissions and uptake by oceans/land
        co2_derivative = (
            emissions * 0.1267 -  # Convert GtC to ppm
            (co2 - 280) * 0.02 +  # Natural carbon sinks
            temp * self.parameters['carbon_cycle_feedback'] +  # Temperature feedback
            (10.5 - ice_extent) * self.parameters['permafrost_feedback']  # Permafrost melting
        )
        
        # Temperature change
        # Based on radiative forcing from CO2 and feedbacks
        forcing = 5.35 * np.log(co2 / 280) + self.parameters['aerosol_forcing']
        temp_derivative = (
            forcing / self.parameters['ocean_heat_capacity'] -
            0.1 * temp  # Thermal radiation to space
        )
        
        # Ocean heat content
        ocean_heat_derivative = 0.9 * forcing - 0.05 * ocean_heat
        
        # Sea level (thermal expansion + ice melt)
        sea_level_derivative = 0.0003 * temp + 0.00001 * ocean_heat
        
        # Arctic sea ice extent
        ice_extent_derivative = -0.1 * temp * self.parameters['albedo_feedback']
        
        return [temp_derivative, co2_derivative, ocean_heat_derivative, 
                sea_level_derivative, ice_extent_derivative]
    
    def create_emissions_scenario(self, scenario_type):
        """
        Create an emissions scenario function.
        
        Args:
            scenario_type: One of 'business_as_usual', 'moderate_mitigation', 'strong_mitigation'
            
        Returns:
            Emissions function that takes time as input
        """
        # Current annual emissions in GtC
        current_emissions = 10.0
        
        if scenario_type == 'business_as_usual':
            # Increasing emissions
            return lambda t: current_emissions * (1 + 0.02 * t)
        
        elif scenario_type == 'moderate_mitigation':
            # Emissions peak and gradually decline
            return lambda t: current_emissions * (1 + 0.01 * t - 0.001 * t**2) if t < 30 else current_emissions * 0.7
        
        elif scenario_type == 'strong_mitigation':
            # Rapid emissions reduction
            return lambda t: current_emissions * np.exp(-0.05 * t)
        
        else:
            # Default: constant emissions
            return lambda t: current_emissions
    
    def run_simulation(self, years=80, scenario='moderate_mitigation', time_step=0.1):
        """
        Run the climate simulation.
        
        Args:
            years: Number of years to simulate
            scenario: Emissions scenario
            time_step: Time step for integration
            
        Returns:
            DataFrame with simulation results
        """
        # Create emissions scenario
        emissions_scenario = self.create_emissions_scenario(scenario)
        
        # Define time span
        t_span = (0, years)
        t_eval = np.arange(0, years + time_step, time_step)
        
        # Initial conditions
        y0 = [
            self.initial_state['temperature'],
            self.initial_state['co2_concentration'],
            self.initial_state['ocean_heat'],
            self.initial_state['sea_level'],
            self.initial_state['ice_extent']
        ]
        
        # Solve the system of differential equations
        solution = solve_ivp(
            fun=lambda t, y: self.climate_system_dynamics(t, y, emissions_scenario),
            t_span=t_span,
            y0=y0,
            t_eval=t_eval,
            method='RK45'
        )
        
        # Extract results
        results = pd.DataFrame({
            'year': [datetime.now().year + t for t in solution.t],
            'temperature': solution.y[0],
            'co2': solution.y[1],
            'ocean_heat': solution.y[2],
            'sea_level': solution.y[3] * 100,  # Convert to cm
            'ice_extent': np.maximum(0, solution.y[4])  # Ensure non-negative
        })
        
        # Add uncertainty estimates
        temp_uncertainty = 0.01 * np.sqrt(solution.t + 1)
        results['temperature_lower'] = results['temperature'] - 1.96 * temp_uncertainty
        results['temperature_upper'] = results['temperature'] + 1.96 * temp_uncertainty
        
        return results
    
    def visualize_simulation(self, results, variable='temperature'):
        """
        Create an interactive visualization of simulation results.
        
        Args:
            results: DataFrame with simulation results
            variable: Climate variable to visualize
            
        Returns:
            Plotly figure object
        """
        # Variable configurations
        var_config = {
            'temperature': {
                'title': 'Global Temperature Anomaly',
                'y_label': 'Temperature (°C)',
                'color': '#FF5733'
            },
            'co2': {
                'title': 'Atmospheric CO₂ Concentration',
                'y_label': 'CO₂ (ppm)',
                'color': '#4CAF50'
            },
            'sea_level': {
                'title': 'Sea Level Rise',
                'y_label': 'Sea Level Rise (cm)',
                'color': '#2196F3'
            },
            'ice_extent': {
                'title': 'Arctic Sea Ice Extent',
                'y_label': 'Ice Extent (million km²)',
                'color': '#9C27B0'
            }
        }
        
        config = var_config.get(variable, {
            'title': variable.replace('_', ' ').title(),
            'y_label': variable,
            'color': '#00a3e0'
        })
        
        # Create figure
        fig = go.Figure()
        
        # Add main trace
        fig.add_trace(go.Scatter(
            x=results['year'],
            y=results[variable],
            mode='lines',
            name=config['y_label'],
            line=dict(color=config['color'], width=3)
        ))
        
        # Add uncertainty range if available
        if f"{variable}_lower" in results.columns and f"{variable}_upper" in results.columns:
            fig.add_trace(go.Scatter(
                x=results['year'].tolist() + results['year'].tolist()[::-1],
                y=results[f"{variable}_upper"].tolist() + results[f"{variable}_lower"].tolist()[::-1],
                fill='toself',
                fillcolor=f"rgba{tuple(int(config['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}",
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))
        
        # Update layout
        fig.update_layout(
            title=config['title'],
            xaxis_title='Year',
            yaxis_title=config['y_label'],
            template='plotly_white',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        return fig

    def analyze_tipping_points(self, results):
        """
        Analyze simulation results for climate tipping points.
        
        Args:
            results: DataFrame with simulation results
            
        Returns:
            Dictionary with tipping point analysis
        """
        tipping_points = {}
        
        # Analyze temperature for 1.5°C and 2.0°C thresholds
        if 'temperature' in results:
            # Find when temperature crosses 1.5°C
            temp_1_5 = results[results['temperature'] >= 1.5]
            if not temp_1_5.empty:
                tipping_points['1.5C_threshold_year'] = int(temp_1_5.iloc[0]['year'])
                tipping_points['1.5C_threshold_risk'] = 'Moderate'
            
            # Find when temperature crosses 2.0°C
            temp_2_0 = results[results['temperature'] >= 2.0]
            if not temp_2_0.empty:
                tipping_points['2.0C_threshold_year'] = int(temp_2_0.iloc[0]['year'])
                tipping_points['2.0C_threshold_risk'] = 'High'
            
            # Find when temperature crosses 3.0°C
            temp_3_0 = results[results['temperature'] >= 3.0]
            if not temp_3_0.empty:
                tipping_points['3.0C_threshold_year'] = int(temp_3_0.iloc[0]['year'])
                tipping_points['3.0C_threshold_risk'] = 'Severe'
        
        # Analyze Arctic sea ice for ice-free summers
        if 'ice_extent' in results:
            # Ice-free summer threshold is around 1 million km²
            ice_free = results[results['ice_extent'] <= 1.0]
            if not ice_free.empty:
                tipping_points['ice_free_summer_year'] = int(ice_free.iloc[0]['year'])
                tipping_points['ice_free_impact'] = 'Major ecosystem disruption, albedo feedback acceleration'
        
        # Analyze permafrost and methane releases
        if 'temperature' in results:
            # Permafrost starts significant methane release around 2.5°C warming
            temp_permafrost = results[results['temperature'] >= 2.5]
            if not temp_permafrost.empty:
                tipping_points['permafrost_methane_year'] = int(temp_permafrost.iloc[0]['year'])
                tipping_points['permafrost_impact'] = 'Accelerated warming due to methane release'
        
        return tipping_points