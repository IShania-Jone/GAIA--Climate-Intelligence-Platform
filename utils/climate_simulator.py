import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Basic Climate Model Parameters
DEFAULT_PARAMS = {
    'initial_temperature': 14.0,  # Global mean temperature in degrees Celsius
    'co2_sensitivity': 5.35,      # Radiative forcing parameter for CO2
    'climate_sensitivity': 0.8,   # Climate sensitivity parameter (°C per W/m²)
    'ocean_heat_capacity': 14.0,  # Effective ocean heat capacity
    'baseline_co2': 280,          # Pre-industrial CO2 concentration (ppm)
    'current_co2': 417,           # Current CO2 concentration (ppm)
}

# Define CO2 emission scenarios
EMISSION_SCENARIOS = {
    'business_as_usual': {
        'name': 'Business as Usual (RCP 8.5)',
        'description': 'Continued high emissions with no mitigation efforts',
        'annual_increase': 2.5,  # Annual CO2 increase in ppm
    },
    'moderate_mitigation': {
        'name': 'Moderate Mitigation (RCP 4.5)',
        'description': 'Some emission reductions with partial policy implementation',
        'annual_increase': 1.2,  # Annual CO2 increase in ppm
    },
    'strong_mitigation': {
        'name': 'Strong Mitigation (RCP 2.6)',
        'description': 'Aggressive emission reductions aligned with Paris Agreement',
        'annual_increase': 0.5,  # Annual CO2 increase in ppm
    },
    'net_zero': {
        'name': 'Net Zero by 2050',
        'description': 'Rapid transition to carbon neutrality',
        'annual_increase': 1.0,  # Initial increase, decreasing over time
        'net_zero_year': 2050,   # Year when emissions reach net zero
    },
    'negative_emissions': {
        'name': 'Negative Emissions by 2070',
        'description': 'Carbon capture deployment leading to negative emissions',
        'annual_increase': 0.8,  # Initial increase, becoming negative later
        'negative_year': 2070,   # Year when emissions become negative
    }
}

def run_climate_simulation(scenario, years=80, params=None):
    """
    Run a basic climate simulation based on the chosen emission scenario.
    
    Args:
        scenario: The emission scenario key from EMISSION_SCENARIOS
        years: Number of years to simulate
        params: Optional custom parameters
        
    Returns:
        DataFrame with simulation results
    """
    # Use default parameters if none provided
    if params is None:
        params = DEFAULT_PARAMS.copy()
    
    # Get scenario details
    if scenario not in EMISSION_SCENARIOS:
        scenario = 'business_as_usual'  # Default fallback
    
    scenario_details = EMISSION_SCENARIOS[scenario]
    
    # Initialize results DataFrame
    current_year = datetime.now().year
    simulation_years = range(current_year, current_year + years)
    results = pd.DataFrame({'year': simulation_years})
    
    # Calculate CO2 concentrations based on scenario
    co2_concentrations = []
    co2_level = params['current_co2']
    
    for i, year in enumerate(simulation_years):
        # Calculate annual increase based on scenario
        if scenario == 'net_zero':
            # Linear decrease to net zero
            if year < scenario_details['net_zero_year']:
                years_to_net_zero = scenario_details['net_zero_year'] - current_year
                annual_increase = scenario_details['annual_increase'] * (1 - (i / years_to_net_zero))
            else:
                annual_increase = 0  # Net zero emissions
        
        elif scenario == 'negative_emissions':
            # Transition to negative emissions
            if year < scenario_details['negative_year']:
                years_to_negative = scenario_details['negative_year'] - current_year
                annual_increase = scenario_details['annual_increase'] * (1 - (1.5 * i / years_to_negative))
            else:
                # Negative emissions (-0.5 ppm per year)
                annual_increase = -0.5
        
        else:
            # Standard scenario with constant annual increase
            annual_increase = scenario_details['annual_increase']
        
        # Update CO2 level and add to list
        co2_level += annual_increase
        co2_concentrations.append(round(co2_level, 1))
    
    results['co2'] = co2_concentrations
    
    # Calculate temperature change using a simple energy balance model
    temperatures = []
    temp = params['initial_temperature']
    
    for co2 in co2_concentrations:
        # Calculate radiative forcing from CO2
        forcing = params['co2_sensitivity'] * np.log(co2 / params['baseline_co2'])
        
        # Calculate temperature change based on forcing and climate sensitivity
        temp_change = forcing * params['climate_sensitivity'] / params['ocean_heat_capacity']
        
        # Update temperature with a lag effect from ocean heat capacity
        temp = temp + temp_change
        temperatures.append(round(temp, 2))
    
    results['temperature'] = temperatures
    
    # Calculate sea level rise (simplified model)
    # Thermal expansion + ice melt contributions
    sea_levels = []
    initial_sea_level = 0  # Starting at 0 for relative change
    
    for i, temp in enumerate(temperatures):
        # Simplified model: sea level rises with temperature, with accelerating pace
        # Thermal expansion component
        thermal_component = 0.3 * (temp - params['initial_temperature'])
        
        # Ice melt component (accelerates with time and temperature)
        year_factor = i / 10  # Acceleration factor
        temp_anomaly = temp - params['initial_temperature']
        ice_melt_component = 0.1 * year_factor * temp_anomaly * temp_anomaly
        
        # Total sea level rise in cm
        sea_level = initial_sea_level + thermal_component + ice_melt_component
        sea_levels.append(round(sea_level, 1))
    
    results['sea_level_rise'] = sea_levels
    
    # Calculate additional impacts
    
    # Arctic sea ice extent (simplified model)
    ice_extent = []
    current_ice = 10.5  # Current Arctic sea ice extent in million square km
    
    for temp in temperatures:
        # Simplified model: ice decreases with temperature
        temp_anomaly = temp - params['initial_temperature']
        new_ice = current_ice - (temp_anomaly * 0.8)  # Simplified relationship
        
        # Ensure non-negative values and account for diminishing returns
        new_ice = max(0, new_ice)
        ice_extent.append(round(new_ice, 2))
    
    results['arctic_ice'] = ice_extent
    
    # Add extreme weather index (0-100 scale)
    extreme_weather = []
    
    for temp in temperatures:
        temp_anomaly = temp - params['initial_temperature']
        # Higher temperatures lead to more extreme weather
        weather_index = 20 + (temp_anomaly * 15)  # Base value + temperature effect
        weather_index = min(100, max(0, weather_index))  # Ensure within 0-100 range
        extreme_weather.append(round(weather_index, 1))
    
    results['extreme_weather_index'] = extreme_weather
    
    return results

def run_advanced_climate_simulation(scenario, years=80, params=None):
    """
    Run a more advanced climate simulation using a system of differential equations.
    
    Args:
        scenario: The emission scenario key from EMISSION_SCENARIOS
        years: Number of years to simulate
        params: Optional custom parameters
        
    Returns:
        DataFrame with simulation results
    """
    # Use default parameters if none provided
    if params is None:
        params = {
            'initial_temperature': 14.0,  # Global mean temperature in °C
            'ocean_heat_capacity': 14.0,  # Heat capacity parameter
            'climate_sensitivity': 3.0,    # Climate sensitivity (°C per doubling of CO2)
            'co2_forcing_coefficient': 5.35,  # Radiative forcing coefficient
            'baseline_co2': 280,          # Pre-industrial CO2 (ppm)
            'current_co2': 417,           # Current CO2 concentration (ppm)
            'ocean_mixing_rate': 0.002,   # Rate of heat transfer to deep ocean
            'deep_ocean_temperature': 6.0, # Deep ocean temperature (°C)
            'ice_albedo_feedback': 0.01,  # Ice-albedo feedback factor
            'carbon_cycle_feedback': 0.01, # Carbon cycle feedback factor
        }
    
    # Get scenario details
    if scenario not in EMISSION_SCENARIOS:
        scenario = 'business_as_usual'  # Default fallback
    
    scenario_details = EMISSION_SCENARIOS[scenario]
    
    # Initialize time array
    current_year = datetime.now().year
    simulation_years = list(range(current_year, current_year + years + 1))
    t = np.linspace(0, years, years + 1)
    
    # Generate CO2 scenario
    co2_levels = [params['current_co2']]
    
    for i in range(1, years + 1):
        # Calculate annual increase based on scenario
        if scenario == 'net_zero':
            # Linear decrease to net zero
            year = current_year + i
            if year < scenario_details['net_zero_year']:
                years_to_net_zero = scenario_details['net_zero_year'] - current_year
                annual_increase = scenario_details['annual_increase'] * (1 - (i / years_to_net_zero))
            else:
                annual_increase = 0  # Net zero emissions
        
        elif scenario == 'negative_emissions':
            # Transition to negative emissions
            year = current_year + i
            if year < scenario_details['negative_year']:
                years_to_negative = scenario_details['negative_year'] - current_year
                annual_increase = scenario_details['annual_increase'] * (1 - (1.5 * i / years_to_negative))
            else:
                # Negative emissions (-0.5 ppm per year)
                annual_increase = -0.5
        
        else:
            # Standard scenario with constant annual increase
            annual_increase = scenario_details['annual_increase']
        
        # Add carbon cycle feedback (higher temperatures release more CO2)
        def climate_system(y, t, co2_levels, params):
             T_s = y[0]  # Surface temperature
             T_d = y[1]  # Deep ocean temperature

             try:
                 idx = int(np.floor(t))
                 if idx >= len(co2_levels):
                     co2 = co2_levels[-1]
                 elif idx < 0:
                     co2 = co2_levels[0]
                 else:
                     co2 = co2_levels[idx]
             except:
                 co2 = co2_levels[0]

             # Radiative forcing due to CO2
             forcing = params['co2_forcing_coefficient'] * np.log(co2 / params['baseline_co2'])

             # Temperature tendency equations
             dT_s = (forcing - (T_s - T_d) / params['ocean_heat_capacity']) \
           - params['ice_albedo_feedback'] * max(0, T_s - params['initial_temperature'])

             dT_d = (T_s - T_d) * params['ocean_mixing_rate']

             return [dT_s, dT_d]

        
        # Update CO2 level
        co2 = co2_levels[-1] + annual_increase
        co2_levels.append(co2)
    
    # Define the climate system model
    def climate_system(y, t, co2_levels, params):
        # Unpack variables
        T_s = y[0]  # Surface temperature
        T_d = y[1]  # Deep ocean temperature
        
        # Get CO2 level for current time
        # Ensure t is properly converted to an integer index and handle edge cases
        try:
            idx = int(np.floor(t))  # Use floor to safely convert float time to integer index
            if idx >= len(co2_levels):
                co2 = co2_levels[-1]  # Use last value if beyond the range
            elif idx < 0:
                co2 = co2_levels[0]  # Use first value if negative (shouldn't happen)
            else:
                co2 = co2_levels[idx]
        except (ValueError, TypeError) as e:
            # Fallback in case of conversion error
            print(f"Warning: Error converting time value ({t}) to index: {e}")
            co2 = co2_levels[0]  # Use first value as fallback
        
        # Calculate radiative forcing from CO2
        forcing = params['co2_forcing_coefficient'] * np.log(co2 / params['baseline_co2'])
        
        # Ice-albedo feedback (reduces with less ice)
        temp_anomaly = T_s - params['initial_temperature']
        ice_feedback = params['ice_albedo_feedback'] * temp_anomaly
        
        # Total forcing including feedbacks
        total_forcing = forcing + ice_feedback
        
        # Temperature differential equations
        dTs_dt = (total_forcing - (params['ocean_mixing_rate'] * (T_s - T_d))) / params['ocean_heat_capacity']
        dTd_dt = params['ocean_mixing_rate'] * (T_s - T_d) / (5 * params['ocean_heat_capacity'])
        
        return [dTs_dt, dTd_dt]
    
    # Initial conditions
    y0 = [params['initial_temperature'], params['deep_ocean_temperature']]
    
    # Solve the ODE system
    y = odeint(climate_system, y0, t, args=(co2_levels, params))
    
    # Create results DataFrame
    results = pd.DataFrame({
        'year': simulation_years,
        'co2': co2_levels,
        'temperature': y[:, 0],
        'deep_ocean_temperature': y[:, 1]
    })
    
    # Calculate sea level rise (more detailed model)
    sea_levels = []
    
    for i, row in results.iterrows():
        temp_anomaly = row['temperature'] - params['initial_temperature']
        year_index = i
        
        # Thermal expansion component
        thermal_component = 0.3 * temp_anomaly
        
        # Ice melt component (accelerates with time and temperature)
        # Higher temperature anomalies cause accelerating ice melt
        ice_melt_rate = 0.05 * (year_index / 10) * (temp_anomaly ** 1.5)
        if temp_anomaly > 1.5:  # Threshold for accelerated Greenland/Antarctica melt
            ice_melt_rate += 0.1 * ((temp_anomaly - 1.5) ** 2)
        
        # Total sea level rise in cm
        if i == 0:
            sea_level = 0  # Start at 0
        else:
            sea_level = sea_levels[-1] + thermal_component + ice_melt_rate
        
        sea_levels.append(round(sea_level, 1))
    
    results['sea_level_rise'] = sea_levels
    
    # Calculate Arctic sea ice extent (more detailed model)
    ice_extent = []
    current_ice = 10.5  # Current Arctic sea ice extent in million square km
    
    for i, row in results.iterrows():
        temp_anomaly = row['temperature'] - params['initial_temperature']
        
        # Non-linear ice response to warming
        if temp_anomaly < 1.0:
            ice_loss = temp_anomaly * 0.7  # Slower initial loss
        elif temp_anomaly < 2.0:
            ice_loss = 0.7 + (temp_anomaly - 1.0) * 1.2  # Accelerating loss
        else:
            ice_loss = 0.7 + 1.2 + (temp_anomaly - 2.0) * 1.8  # Rapid loss at high temperatures
        
        # Calculate remaining ice
        remaining_ice = current_ice - ice_loss
        
        # Ensure non-negative values and apply diminishing returns for last ice
        remaining_ice = max(0, remaining_ice)
        if remaining_ice < 1.0:
            remaining_ice *= 0.8  # Last ice more resilient (multiyear ice)
        
        ice_extent.append(round(remaining_ice, 2))
    
    results['arctic_ice'] = ice_extent
    
    # Calculate extreme weather index (0-100 scale)
    extreme_weather = []
    
    for i, row in results.iterrows():
        temp_anomaly = row['temperature'] - params['initial_temperature']
        
        # Higher temperatures lead to more extreme weather
        # Non-linear relationship with accelerating extremes
        if temp_anomaly < 1.0:
            weather_index = 20 + (temp_anomaly * 10)  # Moderate increase
        elif temp_anomaly < 2.0:
            weather_index = 30 + (temp_anomaly - 1.0) * 20  # Faster increase
        else:
            weather_index = 50 + (temp_anomaly - 2.0) * 25  # Rapid increase
        
        # Ensure within 0-100 range
        weather_index = min(100, max(0, weather_index))
        extreme_weather.append(round(weather_index, 1))
    
    results['extreme_weather_index'] = extreme_weather
    
    # Round numeric columns for readability
    results['temperature'] = results['temperature'].round(2)
    results['deep_ocean_temperature'] = results['deep_ocean_temperature'].round(2)
    
    return results

def generate_climate_risk_map(simulation_results, year_index=30):
    """
    Generate climate risk data for global mapping.
    
    Args:
        simulation_results: Results from a climate simulation
        year_index: Index of the year to use for risk assessment
        
    Returns:
        DataFrame with risk data for global grid
    """
    # Create a grid of lat/lon points for global map
    lats = np.arange(-85, 86, 10)
    lons = np.arange(-180, 181, 20)
    
    # Get temperature from simulation for the selected year
    if year_index >= len(simulation_results):
        year_index = len(simulation_results) - 1
    
    temp_anomaly = simulation_results.iloc[year_index]['temperature'] - DEFAULT_PARAMS['initial_temperature']
    sea_level_rise = simulation_results.iloc[year_index]['sea_level_rise']
    
    # Create empty lists to store grid data
    grid_data = []
    
    for lat in lats:
        for lon in lons:
            # Skip points in Antarctica
            if lat < -60 and -180 <= lon <= 180:
                continue
                
            # Base risk depends on global temperature rise
            base_risk = temp_anomaly * 2
            
            # Adjust risk based on latitude (higher risk near equator for heat, near poles for ice melt)
            if abs(lat) < 30:
                # Tropical regions - higher heat stress
                risk_factor = base_risk * 1.3
            elif abs(lat) > 60:
                # Polar regions - higher risk from ice melt/permafrost
                risk_factor = base_risk * 1.5
            else:
                # Mid-latitudes
                risk_factor = base_risk * 1.0
            
            # Sea level rise risk higher for coastal locations
            # For simplicity, we'll use a random factor to simulate coastal proximity
            coastal = np.random.random() < 0.3  # 30% chance of being "coastal"
            if coastal:
                sea_level_risk = sea_level_rise * 0.1
            else:
                sea_level_risk = 0
            
            # Drought risk higher in certain latitude bands (subtropical regions)
            if 10 <= abs(lat) <= 40:
                drought_risk = base_risk * 1.2
            else:
                drought_risk = base_risk * 0.7
            
            # Calculate total risk
            total_risk = risk_factor + sea_level_risk + drought_risk
            
            # Add some random variation to simulate local conditions
            total_risk += np.random.normal(0, 0.5)
            
            # Ensure risk is between 0-10
            total_risk = max(0, min(10, total_risk))
            
            # Add to grid data
            grid_data.append({
                'lat': lat,
                'lon': lon,
                'risk': round(total_risk, 1),
                'temperature_risk': round(risk_factor, 1),
                'sea_level_risk': round(sea_level_risk, 1),
                'drought_risk': round(drought_risk, 1)
            })
    
    return pd.DataFrame(grid_data)

def generate_intervention_simulation(base_scenario='business_as_usual', intervention_year=2030):
    """
    Generate a simulation with an intervention at a specific year.
    
    Args:
        base_scenario: Starting scenario
        intervention_year: Year when intervention occurs
        
    Returns:
        DataFrame with simulation results
    """
    # Get current year
    current_year = datetime.now().year
    
    # Years before intervention
    years_before = intervention_year - current_year
    if years_before < 0:
        years_before = 0
    
    # Run base scenario until intervention year
    if years_before > 0:
        base_results = run_advanced_climate_simulation(base_scenario, years=years_before)
    else:
        base_results = pd.DataFrame()
    
    # Get the state at intervention year
    if not base_results.empty:
        # Get the last row of base results
        last_state = base_results.iloc[-1]
        
        # Set new initial conditions
        intervention_params = DEFAULT_PARAMS.copy()
        intervention_params['initial_temperature'] = last_state['temperature']
        intervention_params['current_co2'] = last_state['co2']
    else:
        intervention_params = DEFAULT_PARAMS.copy()
    
    # Run strong mitigation scenario after intervention
    future_years = 80 - years_before
    future_results = run_advanced_climate_simulation('strong_mitigation', years=future_years, 
                                                 params=intervention_params)
    
    # Combine results
    if not base_results.empty:
        # Drop the last row of base_results to avoid duplication
        combined_results = pd.concat([base_results, future_results])
    else:
        combined_results = future_results
    
    # Add a column to mark the intervention point
    combined_results['intervention'] = False
    combined_results.loc[combined_results['year'] == intervention_year, 'intervention'] = True
    
    return combined_results

def compare_intervention_strategies():
    """
    Compare different intervention timing strategies.
    
    Returns:
        Dictionary with simulation results for different intervention times
    """
    current_year = datetime.now().year
    
    # Define intervention years
    early_year = current_year + 5
    medium_year = current_year + 15
    late_year = current_year + 25
    
    # Run simulations
    early_results = generate_intervention_simulation('business_as_usual', early_year)
    medium_results = generate_intervention_simulation('business_as_usual', medium_year)
    late_results = generate_intervention_simulation('business_as_usual', late_year)
    no_intervention = run_advanced_climate_simulation('business_as_usual', years=80)
    
    return {
        'early': early_results,
        'medium': medium_results,
        'late': late_results,
        'none': no_intervention
    }
