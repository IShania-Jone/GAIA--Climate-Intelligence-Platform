import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.quantum_prediction import QuantumClimatePredictor
from utils.climate_interventions import ClimateInterventionSimulator

# Page config
st.set_page_config(
    page_title="GAIA-∞ | Quantum Insights",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page title
st.title("⚛️ Quantum Climate Insights")
st.markdown("""
This revolutionary module leverages quantum-inspired algorithms to analyze climate data, predict future scenarios, 
and generate optimized intervention strategies. The platform combines cutting-edge AI with quantum computing 
principles to provide unprecedented climate intelligence.
""")

# Initialize our predictors
predictor = QuantumClimatePredictor()
intervention_simulator = ClimateInterventionSimulator()

# Sidebar options
with st.sidebar:
    st.header("Quantum Insights")
    
    insight_type = st.radio(
        "Analysis Type",
        ["Quantum Predictions", "Intervention Strategies"]
    )
    
    if insight_type == "Quantum Predictions":
        scenario = st.selectbox(
            "Climate Scenario",
            ["low_emissions", "moderate", "high_emissions"],
            format_func=lambda x: {
                "low_emissions": "Low Emissions",
                "moderate": "Moderate Emissions",
                "high_emissions": "High Emissions"
            }.get(x, x.title()),
            index=1
        )
        
        climate_variable = st.selectbox(
            "Climate Variable",
            ["temperature", "co2", "sea_level", "ice_extent"],
            format_func=lambda x: {
                "temperature": "Global Temperature",
                "co2": "CO₂ Concentration",
                "sea_level": "Sea Level Rise",
                "ice_extent": "Arctic Sea Ice Extent"
            }.get(x, x.title())
        )
        
        years = st.slider(
            "Prediction Horizon (Years)",
            min_value=10,
            max_value=80,
            value=50,
            step=5
        )
        
    elif insight_type == "Intervention Strategies":
        available_interventions = intervention_simulator.get_available_interventions()
        
        intervention_type = st.selectbox(
            "Intervention Type",
            options=list(available_interventions.keys()),
            format_func=lambda x: available_interventions[x]["description"]
        )
        
        intervention_years = st.slider(
            "Years to Simulate",
            min_value=10,
            max_value=80,
            value=30,
            step=5
        )
        
        # Parameter controls
        st.subheader("Intervention Parameters")
        if intervention_type in available_interventions:
            default_parameters = available_interventions[intervention_type]["parameter_defaults"]
            custom_parameters = {}
            
            for param_name, default_value in default_parameters.items():
                # Format the parameter name for display
                display_name = param_name.replace("_", " ").title()
                
                # Create a slider for the parameter
                value = st.slider(
                    display_name,
                    min_value=0.0,
                    max_value=1.0,
                    value=float(default_value),
                    step=0.1,
                    format="%.1f"
                )
                
                custom_parameters[param_name] = value

# Main content based on selected insight type
if insight_type == "Quantum Predictions":
    st.header("Quantum-Enhanced Climate Predictions")
    
    st.markdown(f"""
    <div style="background-color: rgba(0, 163, 224, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="margin-top:0;">How Quantum Algorithms Work</h3>
        <p>The GAIA-∞ quantum prediction system simulates quantum superposition and entanglement to explore multiple
        climate futures simultaneously. Unlike traditional models, our quantum-inspired algorithm considers complex
        interdependencies between climate variables and incorporates uncertainty principles to deliver more robust projections.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Run the prediction
    generate_button = st.button("Generate Quantum Prediction", type="primary")
    
    if generate_button:
        with st.spinner("Running quantum-enhanced prediction algorithm..."):
            # Generate the prediction
            predictions = predictor.generate_prediction(
                climate_variable=climate_variable,
                years_to_predict=years,
                scenario=scenario
            )
            
            if predictions is not None:
                # Create visualization
                fig = go.Figure()
                
                # Add the prediction line
                fig.add_trace(go.Scatter(
                    x=predictions["year"],
                    y=predictions["value"],
                    mode="lines",
                    name="Quantum Prediction",
                    line=dict(color="#9C27B0", width=3)
                ))
                
                # Add uncertainty range
                fig.add_trace(go.Scatter(
                    x=predictions["year"].tolist() + predictions["year"].tolist()[::-1],
                    y=predictions["upper_bound"].tolist() + predictions["lower_bound"].tolist()[::-1],
                    fill="toself",
                    fillcolor="rgba(156, 39, 176, 0.2)",
                    line=dict(color="rgba(156, 39, 176, 0.2)"),
                    showlegend=False
                ))
                
                # Configure layout
                variable_labels = {
                    "temperature": "Global Temperature Anomaly (°C)",
                    "sea_level": "Sea Level Rise (mm)",
                    "co2": "CO₂ Concentration (ppm)",
                    "ice_extent": "Arctic Sea Ice Extent (million km²)"
                }
                
                scenario_labels = {
                    "low_emissions": "Low Emissions Scenario",
                    "moderate": "Moderate Emissions Scenario",
                    "high_emissions": "High Emissions Scenario"
                }
                
                fig.update_layout(
                    title=f"{variable_labels.get(climate_variable, climate_variable.title())} Prediction ({scenario_labels.get(scenario, scenario.title())})",
                    xaxis_title="Year",
                    yaxis_title=variable_labels.get(climate_variable, climate_variable.title()),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    height=500
                )
                
                # Add present day line
                current_year = datetime.now().year
                fig.add_vline(x=current_year, line_dash="dash", line_width=1, line_color="gray")
                fig.add_annotation(
                    x=current_year, y=predictions["value"].iloc[0],
                    text="Present Day",
                    showarrow=False,
                    yshift=10
                )
                
                # Display the plot
                st.plotly_chart(fig, use_container_width=True)
                
                # Display metrics
                metrics = predictor.get_metrics(climate_variable, scenario)
                
                if metrics:
                    st.subheader("Key Insights")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Total Change",
                            f"{metrics['total_change']:.2f}" + (" °C" if climate_variable == "temperature" else ""),
                            f"{metrics['annual_rate']:.3f} per year"
                        )
                        
                    with col2:
                        st.metric(
                            f"Value in {current_year + years}",
                            f"{metrics['end_value']:.2f}" + (" °C" if climate_variable == "temperature" else ""),
                            f"{metrics['total_change']:.2f} from present"
                        )
                        
                    with col3:
                        if climate_variable == "temperature" and "paris_threshold_year" in metrics:
                            st.metric(
                                "1.5°C Threshold Year",
                                metrics["paris_threshold_year"]
                            )
                        elif climate_variable == "ice_extent" and "ice_free_summer_year" in metrics:
                            st.metric(
                                "Ice-Free Summer Year",
                                metrics["ice_free_summer_year"]
                            )
                
                # Add comparison button
                if st.button("Compare with Classical Methods"):
                    with st.spinner("Generating comparison chart..."):
                        # Generate a matplotlib figure
                        fig_mpl = predictor.generate_comparison_chart(
                            climate_variable,
                            years_to_predict=years
                        )
                        
                        # Display the matplotlib figure
                        st.pyplot(fig_mpl)
                        
                        st.markdown("""
                        The comparison shows how quantum-enhanced algorithms provide more precise predictions
                        with narrower confidence intervals compared to traditional classical methods.
                        This precision allows for better planning and policy development.
                        """)
            else:
                st.error("Failed to generate quantum predictions. Please try again with different parameters.")

elif insight_type == "Intervention Strategies":
    st.header("Climate Intervention Simulator")
    
    st.markdown(f"""
    <div style="background-color: rgba(0, 163, 224, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="margin-top:0;">Quantum-Enhanced Intervention Analysis</h3>
        <p>The GAIA-∞ platform uses quantum-inspired algorithms to model the complex effects of climate interventions.
        This gives policymakers a powerful tool to evaluate different strategies and optimize their climate action plans
        with greater precision than traditional models.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulate button
    simulate_button = st.button("Simulate Intervention", type="primary")
    
    if simulate_button:
        with st.spinner(f"Simulating the effects of {available_interventions[intervention_type]['description']}..."):
            # Get the necessary variables from the sidebar
            custom_parameters = {}
            for param_name, default_value in available_interventions[intervention_type]["parameter_defaults"].items():
                param_key = param_name.replace("_", " ").title()
                value_from_session = st.session_state.get(f"{param_key}_key")
                custom_parameters[param_name] = value_from_session if value_from_session is not None else default_value
            
            # Simulate the intervention
            intervention_results = intervention_simulator.simulate_intervention(
                intervention_type,
                custom_parameters,
                intervention_years,
                "moderate"  # Default to moderate scenario
            )
            
            if intervention_results is not None:
                # Calculate effectiveness metrics
                affected_variables = available_interventions[intervention_type]["affected_variables"]
                primary_variable = affected_variables[0] if affected_variables else "temperature"
                
                effectiveness_metrics = intervention_simulator.calculate_intervention_effectiveness(
                    primary_variable,
                    intervention_type,
                    custom_parameters,
                    intervention_years
                )
                
                # Display results
                st.subheader("Intervention Results")
                
                # Create visualization
                fig = go.Figure()
                
                # Add the intervention line
                fig.add_trace(go.Scatter(
                    x=intervention_results["year"],
                    y=intervention_results["value"],
                    mode="lines",
                    name="With Intervention",
                    line=dict(color="green", width=3)
                ))
                
                # Add uncertainty range for intervention
                fig.add_trace(go.Scatter(
                    x=intervention_results["year"].tolist() + intervention_results["year"].tolist()[::-1],
                    y=intervention_results["upper_bound"].tolist() + intervention_results["lower_bound"].tolist()[::-1],
                    fill="toself",
                    fillcolor="rgba(0, 128, 0, 0.2)",
                    line=dict(color="rgba(0, 128, 0, 0.2)"),
                    showlegend=False
                ))
                
                # Add the baseline line (using metrics)
                if effectiveness_metrics:
                    baseline_end = effectiveness_metrics["baseline_end_value"]
                    intervention_end = effectiveness_metrics["intervention_end_value"]
                    baseline_start = baseline_end - effectiveness_metrics["absolute_difference"]
                    
                    # Create evenly spaced points for the baseline
                    years = intervention_results["year"].tolist()
                    baseline_values = [baseline_start + (baseline_end - baseline_start) * i / (len(years) - 1) for i in range(len(years))]
                    
                    fig.add_trace(go.Scatter(
                        x=years,
                        y=baseline_values,
                        mode="lines",
                        name="No Intervention (Baseline)",
                        line=dict(color="red", width=3, dash="dash")
                    ))
                
                # Configure layout
                variable_labels = {
                    "temperature": "Global Temperature Anomaly (°C)",
                    "sea_level": "Sea Level Rise (mm)",
                    "co2": "CO₂ Concentration (ppm)",
                    "ice_extent": "Arctic Sea Ice Extent (million km²)"
                }
                
                fig.update_layout(
                    title=f"Impact of {available_interventions[intervention_type]['description']} on {variable_labels.get(primary_variable, primary_variable.title())}",
                    xaxis_title="Year",
                    yaxis_title=variable_labels.get(primary_variable, primary_variable.title()),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    height=500
                )
                
                # Add vertical line for present day
                current_year = datetime.now().year
                fig.add_vline(x=current_year, line_dash="dash", line_width=1, line_color="gray")
                fig.add_annotation(
                    x=current_year, y=intervention_results["value"].iloc[0],
                    text="Present Day",
                    showarrow=False,
                    yshift=10
                )
                
                # Display the plot
                st.plotly_chart(fig, use_container_width=True)
                
                # Display effectiveness metrics
                if effectiveness_metrics:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Format the change value
                        abs_diff = effectiveness_metrics["absolute_difference"]
                        abs_diff_formatted = f"{abs_diff:.2f}"
                        if primary_variable == "temperature":
                            abs_diff_formatted = f"{abs_diff:+.2f}°C"
                        elif primary_variable == "co2":
                            abs_diff_formatted = f"{abs_diff:+.2f} ppm"
                        elif primary_variable == "sea_level":
                            abs_diff_formatted = f"{abs_diff:+.2f} mm"
                        elif primary_variable == "ice_extent":
                            abs_diff_formatted = f"{abs_diff:+.2f} million km²"
                        
                        rel_diff = effectiveness_metrics["relative_difference"]
                        
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <h3 style="margin-top:0;">Impact Assessment</h3>
                            <p><strong>Absolute Change:</strong> {abs_diff_formatted} by {current_year + intervention_years}</p>
                            <p><strong>Relative Change:</strong> {rel_diff:+.2f}% compared to baseline</p>
                            <p><strong>Time Equivalent:</strong> {effectiveness_metrics['time_equivalent']} gained/delayed</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Cost-effectiveness analysis
                        cost_effectiveness = effectiveness_metrics["cost_effectiveness"]
                        
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <h3 style="margin-top:0;">Cost-Effectiveness Analysis</h3>
                            <div style="margin: 15px 0;">
                                <div style="margin-bottom: 10px;">Effectiveness Rating: {cost_effectiveness:.1f}/10</div>
                                <div style="background-color: #f0f0f0; height: 10px; border-radius: 5px; overflow: hidden;">
                                    <div style="background-color: {'green' if cost_effectiveness > 7 else ('orange' if cost_effectiveness > 4 else 'red')}; width: {cost_effectiveness * 10}%; height: 100%;"></div>
                                </div>
                            </div>
                            <p>{'Highly' if cost_effectiveness > 7 else ('Moderately' if cost_effectiveness > 4 else 'Less')} cost-effective compared to other interventions.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Compare multiple interventions
                st.subheader("Compare Multiple Interventions")
                
                # Let user select interventions to compare
                compare_interventions = st.multiselect(
                    "Select interventions to compare",
                    options=list(available_interventions.keys()),
                    format_func=lambda x: available_interventions[x]["description"],
                    default=[intervention_type]
                )
                
                if st.button("Generate Comparison") and compare_interventions:
                    with st.spinner("Generating intervention comparison..."):
                        # Create a comparison chart
                        fig = intervention_simulator.create_intervention_comparison_chart(
                            primary_variable,
                            compare_interventions,
                            years_to_simulate=intervention_years
                        )
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("""
                        This comparison helps policymakers understand the relative effectiveness of different
                        intervention strategies and choose the optimal approach for climate action.
                        """)
            else:
                st.error("Failed to simulate intervention. Please try again with different parameters.")

# Footer with additional information
st.markdown("---")
st.markdown("""
**About Quantum-Enhanced Climate Intelligence**

The GAIA-∞ platform's quantum-inspired algorithms provide several key advantages:

- **Improved accuracy**: Reduced uncertainty in climate projections compared to classical models.
- **Better complexity handling**: More accurate modeling of complex interactions between climate variables.
- **Efficient simulation**: Faster computation of multiple climate scenarios and intervention pathways.
- **Enhanced optimization**: More effective identification of optimal intervention strategies.

*Note: These quantum-inspired algorithms implement mathematical approaches developed for quantum systems that
provide advantages over traditional methods while running on classical hardware.*
""")

# Add information about what's "quantum" about it
with st.expander("How Quantum-Inspired Algorithms Work"):
    st.markdown("""
    ### Quantum-Inspired Climate Modeling Techniques
    
    The GAIA-∞ platform uses several techniques from quantum computing theory:
    
    **Tensor Networks**: Inspired by quantum entanglement, these mathematical structures efficiently represent
    high-dimensional climate data with reduced computational requirements.
    
    **Quantum-Inspired Sampling**: Our algorithms implement sampling techniques that mirror quantum superposition,
    enabling exploration of multiple climate scenarios simultaneously.
    
    **Uncertainty Principles**: Similar to Heisenberg's uncertainty principle in quantum mechanics, our models
    incorporate fundamental uncertainty relationships between climate variables.
    
    **Quantum Neural Networks**: Neural network architectures inspired by quantum circuit designs provide enhanced
    pattern recognition in climate time series data.
    
    While these methods don't require a quantum computer, they implement mathematical approaches that significantly
    outperform traditional modeling techniques.
    """)