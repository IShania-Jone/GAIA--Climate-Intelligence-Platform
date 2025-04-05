import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils.climate_simulator import (
    run_climate_simulation,
    run_advanced_climate_simulation,
    EMISSION_SCENARIOS,
    DEFAULT_PARAMS,
    generate_intervention_simulation,
    compare_intervention_strategies,
    generate_climate_risk_map
)
from utils.visualization import (
    plot_simulation_results,
    plot_comparative_simulations,
    create_climate_risk_map
)
# Page config must be the first Streamlit command
st.set_page_config(
    page_title="GAIA-∞ | Climate Simulations",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Page title
st.title("🔮 Climate Simulations")
st.markdown("""
Explore potential climate futures through interactive simulations. This page allows you to
run different climate scenarios, compare intervention strategies, and visualize projected impacts.
""")

# Sidebar options
st.sidebar.header("Simulation Options")

simulation_type = st.sidebar.radio(
    "Simulation Type",
    ["Basic Climate Projections", "Comparative Scenarios", "Intervention Analysis", "Custom Parameters"]
)

# Default values for years to simulate
years_to_simulate = st.sidebar.slider(
    "Years to Simulate",
    min_value=10,
    max_value=100,
    value=80,
    step=10
)

# Main simulation interface
if simulation_type == "Basic Climate Projections":
    st.subheader("Climate Projection Simulator")
    
    # Select emission scenario
    scenario_options = list(EMISSION_SCENARIOS.keys())
    selected_scenario = st.selectbox(
        "Select Emission Scenario",
        options=scenario_options,
        format_func=lambda x: EMISSION_SCENARIOS[x]['name']
    )
    
    # Display scenario description
    st.info(EMISSION_SCENARIOS[selected_scenario]['description'])
    
    # Run simulation button
    if st.button("Run Simulation"):
        with st.spinner("Running climate simulation..."):
            # Run the advanced climate simulation
            simulation_results = run_advanced_climate_simulation(
                selected_scenario, 
                years=years_to_simulate
            )
            
            # Store results in session state for reuse
            st.session_state.simulation_results = simulation_results
        
        st.success("Simulation complete!")
    
    # Check if we have simulation results to display
    if 'simulation_results' in st.session_state:
        simulation_results = st.session_state.simulation_results
        
        # Display simulation results
        plot_simulation_results(simulation_results, title=f"Climate Projection: {EMISSION_SCENARIOS[selected_scenario]['name']}")
        
        # Display key insights
        st.subheader("Key Insights")
        
        # Find important years/thresholds
        try:
            # When temperature exceeds 1.5°C above pre-industrial
            preindustrial_temp = DEFAULT_PARAMS['initial_temperature'] - 0.8  # Approximate pre-industrial temperature
            paris_threshold = preindustrial_temp + 1.5
            exceed_paris = None
            for i, row in simulation_results.iterrows():
                if row['temperature'] > paris_threshold:
                    exceed_paris = row['year']
                    break
            
            # When temperature exceeds 2.0°C above pre-industrial
            two_degree_threshold = preindustrial_temp + 2.0
            exceed_two_degrees = None
            for i, row in simulation_results.iterrows():
                if row['temperature'] > two_degree_threshold:
                    exceed_two_degrees = row['year']
                    break
            
            # When Arctic becomes nearly ice-free in summer (< 1 million sq km)
            ice_free_year = None
            for i, row in simulation_results.iterrows():
                if row['arctic_ice'] < 1.0:
                    ice_free_year = row['year']
                    break
            
            # Display insights
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if exceed_paris:
                    st.metric("1.5°C Threshold Reached", f"{exceed_paris}")
                else:
                    st.metric("1.5°C Threshold Reached", "Not in simulation period")
            
            with col2:
                if exceed_two_degrees:
                    st.metric("2.0°C Threshold Reached", f"{exceed_two_degrees}")
                else:
                    st.metric("2.0°C Threshold Reached", "Not in simulation period")
            
            with col3:
                if ice_free_year:
                    st.metric("Ice-free Arctic Summer", f"{ice_free_year}")
                else:
                    st.metric("Ice-free Arctic Summer", "Not in simulation period")
            
            # Calculate end-of-century values
            end_year = min(simulation_results['year'].max(), 2100)
            end_row = simulation_results[simulation_results['year'] == end_year].iloc[0]
            
            st.subheader(f"Projected Values in {end_year}")
            
            end_col1, end_col2, end_col3, end_col4 = st.columns(4)
            
            with end_col1:
                st.metric("Temperature", f"{end_row['temperature']:.2f}°C")
            
            with end_col2:
                st.metric("CO₂ Concentration", f"{end_row['co2']:.1f} ppm")
            
            with end_col3:
                st.metric("Sea Level Rise", f"{end_row['sea_level_rise']:.1f} cm")
            
            with end_col4:
                st.metric("Arctic Sea Ice", f"{end_row['arctic_ice']:.1f} million km²")
        
        except Exception as e:
            st.error(f"Error analyzing simulation results: {str(e)}")
        
        # Generate and display risk map
        st.subheader("Climate Risk Map")
        st.markdown(f"Projected climate risks for year **{datetime.now().year + 30}** under the **{selected_scenario.replace('_', ' ').title()}** scenario")
        
        # Generate risk data
        risk_data = generate_climate_risk_map(simulation_results, year_index=30)
        
        # Create and display the map
        risk_map = create_climate_risk_map(risk_data)
        st.components.v1.html(risk_map._repr_html_(), height=500)
        
        # Add download options
        st.subheader("Download Results")
        
        # Convert DataFrame to CSV
        csv = simulation_results.to_csv(index=False)
        st.download_button(
            label="Download Simulation Data (CSV)",
            data=csv,
            file_name=f"climate_simulation_{selected_scenario}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif simulation_type == "Comparative Scenarios":
    st.subheader("Comparative Climate Scenarios")
    
    # Select scenarios to compare
    available_scenarios = list(EMISSION_SCENARIOS.keys())
    selected_scenarios = st.multiselect(
        "Select Scenarios to Compare",
        options=available_scenarios,
        default=["business_as_usual", "strong_mitigation"],
        format_func=lambda x: EMISSION_SCENARIOS[x]['name']
    )
    
    # Select metric to compare
    comparison_metric = st.selectbox(
        "Select Metric to Compare",
        options=["temperature", "co2", "sea_level_rise", "arctic_ice", "extreme_weather_index"],
        format_func=lambda x: {
            "temperature": "Global Temperature (°C)",
            "co2": "CO₂ Concentration (ppm)",
            "sea_level_rise": "Sea Level Rise (cm)",
            "arctic_ice": "Arctic Sea Ice Extent (million km²)",
            "extreme_weather_index": "Extreme Weather Index (0-100)"
        }[x]
    )
    
    if len(selected_scenarios) > 0:
        # Run comparison button
        if st.button("Run Comparison"):
            with st.spinner("Running comparative simulations..."):
                # Run simulations for each selected scenario
                scenario_results = {}
                
                for scenario in selected_scenarios:
                    scenario_results[scenario] = run_advanced_climate_simulation(
                        scenario, 
                        years=years_to_simulate
                    )
                
                # Store results in session state
                st.session_state.scenario_results = scenario_results
            
            st.success("Comparison complete!")
        
        # Check if we have results to display
        if 'scenario_results' in st.session_state:
            scenario_results = st.session_state.scenario_results
            
            # Filter to only include selected scenarios
            filtered_results = {k: v for k, v in scenario_results.items() if k in selected_scenarios}
            
            if filtered_results:
                # Plot comparative results
                plot_comparative_simulations(
                    filtered_results, 
                    metric=comparison_metric,
                    title=f"Scenario Comparison: {comparison_metric.replace('_', ' ').title()}"
                )
                
                # Show key differences table
                st.subheader("Key Differences Between Scenarios")
                
                # Create a DataFrame for comparison
                comparison_data = []
                
                for scenario, results in filtered_results.items():
                    # Get values at specific years
                    current_year = datetime.now().year
                    mid_century = min(results['year'].max(), 2050)
                    end_century = min(results['year'].max(), 2100)
                    
                    mid_idx = results[results['year'] == mid_century].index[0] if mid_century in results['year'].values else -1
                    end_idx = results[results['year'] == end_century].index[0] if end_century in results['year'].values else -1
                    
                    # Add to comparison data
                    comparison_data.append({
                        'Scenario': EMISSION_SCENARIOS[scenario]['name'],
                        'Temperature 2050 (°C)': f"{results.iloc[mid_idx]['temperature']:.2f}" if mid_idx >= 0 else "N/A",
                        'Temperature 2100 (°C)': f"{results.iloc[end_idx]['temperature']:.2f}" if end_idx >= 0 else "N/A",
                        'Sea Level 2050 (cm)': f"{results.iloc[mid_idx]['sea_level_rise']:.1f}" if mid_idx >= 0 else "N/A",
                        'Sea Level 2100 (cm)': f"{results.iloc[end_idx]['sea_level_rise']:.1f}" if end_idx >= 0 else "N/A",
                        'Arctic Ice 2050 (M km²)': f"{results.iloc[mid_idx]['arctic_ice']:.1f}" if mid_idx >= 0 else "N/A",
                        'Arctic Ice 2100 (M km²)': f"{results.iloc[end_idx]['arctic_ice']:.1f}" if end_idx >= 0 else "N/A",
                        'CO₂ 2050 (ppm)': f"{results.iloc[mid_idx]['co2']:.0f}" if mid_idx >= 0 else "N/A",
                        'CO₂ 2100 (ppm)': f"{results.iloc[end_idx]['co2']:.0f}" if end_idx >= 0 else "N/A"
                    })
                
                # Display comparison table
                st.table(pd.DataFrame(comparison_data))
                
                # Add comparison insights
                st.subheader("Comparative Insights")
                
                # Temperature difference
                if len(filtered_results) > 1:
                    scenarios = list(filtered_results.keys())
                    if "business_as_usual" in scenarios and "strong_mitigation" in scenarios:
                        bau = filtered_results["business_as_usual"]
                        mit = filtered_results["strong_mitigation"]
                        
                        # Find common years
                        max_year = min(bau['year'].max(), mit['year'].max())
                        bau_max = bau[bau['year'] == max_year].iloc[0]
                        mit_max = mit[mit['year'] == max_year].iloc[0]
                        
                        temp_diff = bau_max['temperature'] - mit_max['temperature']
                        sea_diff = bau_max['sea_level_rise'] - mit_max['sea_level_rise']
                        
                        st.markdown(f"""
                        By {max_year}, the difference between 'Business as Usual' and 'Strong Mitigation' scenarios is:
                        
                        - **{temp_diff:.2f}°C** in global temperature
                        - **{sea_diff:.1f} cm** in sea level rise
                        
                        This highlights the significant impact that mitigation actions can have on future climate outcomes.
                        """)
            else:
                st.warning("No simulation results available for the selected scenarios.")
    else:
        st.warning("Please select at least one scenario to simulate.")

elif simulation_type == "Intervention Analysis":
    st.subheader("Climate Intervention Analysis")
    
    st.markdown("""
    This simulation explores the impact of implementing climate interventions at different points in time.
    It simulates starting with a business-as-usual pathway and then transitioning to strong mitigation
    measures at different years.
    """)
    
    # Let user select the intervention year
    current_year = datetime.now().year
    intervention_year = st.slider(
        "Select Intervention Year",
        min_value=current_year,
        max_value=current_year + 30,
        value=current_year + 10,
        step=5
    )
    
    # Run intervention simulation button
    if st.button("Run Intervention Analysis"):
        with st.spinner("Running intervention analysis..."):
            intervention_results = generate_intervention_simulation(
                base_scenario='business_as_usual',
                intervention_year=intervention_year
            )
            
            # Store results in session state
            st.session_state.intervention_results = intervention_results
        
        st.success("Intervention analysis complete!")
    
    # Check if we have results to display
    if 'intervention_results' in st.session_state:
        intervention_results = st.session_state.intervention_results
        
        # Plot intervention results
        st.subheader("Intervention Results")
        plot_simulation_results(intervention_results, title=f"Climate Intervention in {intervention_year}")
        
        # Mark the intervention point
        intervention_row = intervention_results[intervention_results['intervention'] == True]
        
        if not intervention_row.empty:
            # Display intervention metrics
            st.subheader(f"Intervention Point: {intervention_year}")
            
            int_col1, int_col2, int_col3, int_col4 = st.columns(4)
            
            with int_col1:
                st.metric("Temperature at Intervention", f"{intervention_row['temperature'].values[0]:.2f}°C")
            
            with int_col2:
                st.metric("CO₂ at Intervention", f"{intervention_row['co2'].values[0]:.1f} ppm")
            
            with int_col3:
                st.metric("Sea Level at Intervention", f"{intervention_row['sea_level_rise'].values[0]:.1f} cm")
            
            with int_col4:
                st.metric("Arctic Ice at Intervention", f"{intervention_row['arctic_ice'].values[0]:.1f} million km²")
        
        # Compare with other intervention timings
        st.subheader("Comparative Intervention Timing Analysis")
        st.markdown("""
        How does changing the timing of intervention affect long-term climate outcomes?
        This analysis compares early, medium, and late interventions against no intervention.
        """)
        
        # Run comparative intervention analysis
        if st.button("Compare Different Intervention Timings"):
            with st.spinner("Running comparative intervention analysis..."):
                # Run simulations for different intervention times
                intervention_comparisons = compare_intervention_strategies()
                
                # Store in session state
                st.session_state.intervention_comparisons = intervention_comparisons
            
            st.success("Comparison complete!")
        
        # Check if we have comparison results
        if 'intervention_comparisons' in st.session_state:
            comparisons = st.session_state.intervention_comparisons
            
            # Create tabs for different metrics
            tab1, tab2, tab3 = st.tabs(["Temperature", "Sea Level Rise", "Arctic Sea Ice"])
            
            with tab1:
                plot_comparative_simulations(
                    comparisons,
                    metric="temperature",
                    title="Temperature Outcomes with Different Intervention Timings"
                )
            
            with tab2:
                plot_comparative_simulations(
                    comparisons,
                    metric="sea_level_rise",
                    title="Sea Level Rise with Different Intervention Timings"
                )
            
            with tab3:
                plot_comparative_simulations(
                    comparisons,
                    metric="arctic_ice",
                    title="Arctic Sea Ice with Different Intervention Timings"
                )
            
            # Key insights from comparison
            st.subheader("Key Insights on Intervention Timing")
            
            # Extract data for 2100 or max year
            max_year = min([comp['year'].max() for comp in comparisons.values()])
            
            data_2100 = {}
            for key, results in comparisons.items():
                row = results[results['year'] == max_year].iloc[0]
                data_2100[key] = {
                    'temperature': row['temperature'],
                    'sea_level': row['sea_level_rise'],
                    'arctic_ice': row['arctic_ice']
                }
            
            # Calculate differences
            if 'early' in data_2100 and 'late' in data_2100:
                temp_diff = data_2100['late']['temperature'] - data_2100['early']['temperature']
                sea_diff = data_2100['late']['sea_level'] - data_2100['early']['sea_level']
                
                st.markdown(f"""
                **Delaying Climate Action Has Significant Consequences:**
                
                By the year {max_year}, the difference between early intervention and late intervention is:
                
                - **{temp_diff:.2f}°C** additional warming
                - **{sea_diff:.1f} cm** additional sea level rise
                
                This demonstrates the importance of early action on climate change, as delays lead to
                significantly more warming and irreversible impacts.
                """)

elif simulation_type == "Custom Parameters":
    st.subheader("Custom Climate Simulation")
    
    st.markdown("""
    Advanced mode: Customize the climate model parameters to create your own scenarios.
    This allows you to explore the sensitivity of the climate system to different factors.
    """)
    
    # Create parameter inputs
    st.subheader("Model Parameters")
    
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        custom_params = {}
        custom_params['initial_temperature'] = st.slider(
            "Initial Global Temperature (°C)",
            min_value=13.0,
            max_value=15.0,
            value=DEFAULT_PARAMS['initial_temperature'],
            step=0.1
        )
        
        custom_params['climate_sensitivity'] = st.slider(
            "Climate Sensitivity (°C per doubling of CO₂)",
            min_value=1.5,
            max_value=4.5,
            value=3.0,
            step=0.1,
            help="How much warming results from doubling CO₂ concentration"
        )
        
        custom_params['ocean_heat_capacity'] = st.slider(
            "Ocean Heat Capacity",
            min_value=10.0,
            max_value=20.0,
            value=DEFAULT_PARAMS['ocean_heat_capacity'],
            step=0.5,
            help="Higher values lead to slower warming as oceans absorb more heat"
        )
    
    with param_col2:
        custom_params['baseline_co2'] = st.slider(
            "Pre-industrial CO₂ (ppm)",
            min_value=260,
            max_value=300,
            value=DEFAULT_PARAMS['baseline_co2'],
            step=5
        )
        
        custom_params['current_co2'] = st.slider(
            "Current CO₂ (ppm)",
            min_value=400,
            max_value=430,
            value=DEFAULT_PARAMS['current_co2'],
            step=1
        )
        
        custom_params['co2_forcing_coefficient'] = st.slider(
            "CO₂ Forcing Coefficient",
            min_value=4.0,
            max_value=6.0,
            value=5.35,
            step=0.05,
            help="Radiative forcing parameter for CO₂"
        )
    
    # Select emission scenario
    scenario_options = list(EMISSION_SCENARIOS.keys())
    selected_scenario = st.selectbox(
        "Select Emission Scenario",
        options=scenario_options,
        format_func=lambda x: EMISSION_SCENARIOS[x]['name']
    )
    
    # Run custom simulation button
    if st.button("Run Custom Simulation"):
        with st.spinner("Running custom climate simulation..."):
            # Run the advanced climate simulation with custom parameters
            custom_results = run_advanced_climate_simulation(
                selected_scenario, 
                years=years_to_simulate,
                params=custom_params
            )
            
            # Store results in session state
            st.session_state.custom_results = custom_results
        
        st.success("Custom simulation complete!")
    
    # Check if we have results to display
    if 'custom_results' in st.session_state:
        custom_results = st.session_state.custom_results
        
        # Display simulation results
        plot_simulation_results(custom_results, title=f"Custom Climate Projection: {EMISSION_SCENARIOS[selected_scenario]['name']}")
        
        # Parameter sensitivity analysis
        st.subheader("Parameter Sensitivity")
        
        if st.button("Run Parameter Sensitivity Analysis"):
            with st.spinner("Running sensitivity analysis..."):
                # Run multiple simulations with different parameter values
                sensitivity_results = {}
                
                # Vary climate sensitivity
                for sensitivity in [2.0, 3.0, 4.0]:
                    params = custom_params.copy()
                    params['climate_sensitivity'] = sensitivity
                    sensitivity_results[f"Climate Sensitivity {sensitivity}°C"] = run_advanced_climate_simulation(
                        selected_scenario, 
                        years=years_to_simulate,
                        params=params
                    )
                
                # Store in session state
                st.session_state.sensitivity_results = sensitivity_results
            
            st.success("Sensitivity analysis complete!")
        
        # Display sensitivity results if available
        if 'sensitivity_results' in st.session_state:
            sensitivity_results = st.session_state.sensitivity_results
            
            # Plot comparative results
            plot_comparative_simulations(
                sensitivity_results, 
                metric="temperature",
                title="Temperature Sensitivity to Climate Sensitivity Parameter"
            )
            
            st.markdown("""
            **About Climate Sensitivity:**
            
            Climate sensitivity is one of the most important parameters in climate science. It represents
            how much warming results from doubling the CO₂ concentration in the atmosphere.
            
            The IPCC's likely range for climate sensitivity is 2.5°C to 4°C per doubling of CO₂.
            This analysis shows how different values within this range affect temperature projections.
            """)

# Information section
st.markdown("---")
st.subheader("About Climate Simulations")
st.markdown("""
**How These Simulations Work:**

These climate simulations use a simplified Earth system model that includes:

1. **Carbon cycle**: How CO₂ emissions accumulate in the atmosphere
2. **Energy balance**: How greenhouse gases trap heat in the Earth system
3. **Ocean heat absorption**: How oceans delay warming through heat uptake
4. **Ice-albedo feedback**: How melting ice accelerates warming
5. **Climate sensitivity**: How temperature responds to greenhouse gas forcing

While these models are simplified compared to full Earth System Models (ESMs) used by
climate scientists, they capture the essential dynamics and provide reasonable projections
of future climate trajectories under different scenarios.

**Limitations:**

- Simplified representation of complex Earth systems
- Regional variations not explicitly modeled
- Uncertainty in parameters like climate sensitivity
- Limited representation of tipping points and feedbacks

For definitive climate projections, please refer to the comprehensive reports by the
Intergovernmental Panel on Climate Change (IPCC).
""")

# Footer
st.markdown("---")
st.caption("""
GAIA-∞ Climate Simulation Module | Climate modeling powered by simplified Earth system models
For research purposes only; not for policy decisions without expert consultation.
""")
