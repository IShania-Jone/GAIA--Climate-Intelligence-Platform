"""
Climate intervention simulation module for GAIA-∞.

This module simulates the effects of various climate interventions
and policy decisions on future climate trajectories.
"""

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Import the quantum prediction module for baseline scenarios
from utils.quantum_prediction import QuantumClimatePredictor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateInterventionSimulator:
    """
    Simulator for climate interventions and policy effects.
    
    This class provides methods to model the effects of various climate
    interventions and policy decisions on future climate trajectories.
    """
    
    def __init__(self):
        """Initialize the climate intervention simulator."""
        self.predictor = QuantumClimatePredictor()
        self.intervention_effects = self._load_intervention_effects()
        
    def _load_intervention_effects(self):
        """
        Load the effects of various interventions.
        
        Returns:
            Dictionary mapping intervention types to their effects
        """
        # In a production system, these would be loaded from a database
        # with scientifically validated models
        return {
            "renewable_energy": {
                "description": "Transition to renewable energy sources",
                "parameters": {
                    "implementation_speed": 0.5,  # 0 to 1, with 1 being fastest
                    "coverage": 0.8,  # 0 to 1, fraction of energy production covered
                    "efficiency": 0.9,  # 0 to 1, efficiency compared to ideal
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.1,  # immediate reduction
                        "annual_effect": -0.02,  # annual additional reduction
                        "saturation_level": 0.7,  # maximum reduction possible
                        "delay_years": 2  # years before effect begins
                    },
                    "temperature": {
                        "factor_type": "trend_reduction",
                        "immediate_effect": 0,  # immediate change
                        "annual_effect": -0.002,  # annual reduction in trend
                        "saturation_level": 0.6,  # maximum reduction possible
                        "delay_years": 10  # years before effect begins
                    }
                }
            },
            "reforestation": {
                "description": "Large-scale reforestation and forest protection",
                "parameters": {
                    "implementation_speed": 0.3,
                    "coverage": 0.6,
                    "ecosystem_diversity": 0.8
                },
                "effects": {
                    "co2": {
                        "factor_type": "carbon_sequestration",
                        "immediate_effect": -0.02,
                        "annual_effect": -0.01,
                        "saturation_level": 0.3,
                        "delay_years": 5
                    },
                    "temperature": {
                        "factor_type": "trend_reduction",
                        "immediate_effect": 0,
                        "annual_effect": -0.001,
                        "saturation_level": 0.2,
                        "delay_years": 15
                    }
                }
            },
            "industrial_efficiency": {
                "description": "Improved industrial efficiency and processes",
                "parameters": {
                    "implementation_speed": 0.6,
                    "coverage": 0.7,
                    "technology_level": 0.8
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.05,
                        "annual_effect": -0.01,
                        "saturation_level": 0.5,
                        "delay_years": 1
                    }
                }
            },
            "carbon_pricing": {
                "description": "Carbon pricing and markets",
                "parameters": {
                    "price_level": 0.5,  # 0 to 1, with 1 being highest
                    "coverage": 0.6,
                    "enforcement": 0.7
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.03,
                        "annual_effect": -0.01,
                        "saturation_level": 0.4,
                        "delay_years": 3
                    }
                }
            },
            "transportation_electrification": {
                "description": "Electrification of transportation",
                "parameters": {
                    "implementation_speed": 0.4,
                    "coverage": 0.8,
                    "grid_carbon_intensity": 0.6  # 0 is fully clean, 1 is current mix
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.02,
                        "annual_effect": -0.015,
                        "saturation_level": 0.6,
                        "delay_years": 4
                    }
                }
            },
            "building_efficiency": {
                "description": "Building efficiency improvements",
                "parameters": {
                    "implementation_speed": 0.3,
                    "coverage": 0.7,
                    "retrofit_depth": 0.6  # 0 is minimal, 1 is deep retrofit
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.01,
                        "annual_effect": -0.008,
                        "saturation_level": 0.4,
                        "delay_years": 2
                    }
                }
            },
            "agricultural_practices": {
                "description": "Sustainable agricultural practices",
                "parameters": {
                    "implementation_speed": 0.3,
                    "coverage": 0.6,
                    "intensity": 0.7
                },
                "effects": {
                    "co2": {
                        "factor_type": "emission_reduction",
                        "immediate_effect": -0.01,
                        "annual_effect": -0.005,
                        "saturation_level": 0.3,
                        "delay_years": 5
                    }
                }
            },
            "direct_air_capture": {
                "description": "Direct air capture of CO2",
                "parameters": {
                    "implementation_speed": 0.2,
                    "scale": 0.3,
                    "efficiency": 0.7
                },
                "effects": {
                    "co2": {
                        "factor_type": "carbon_removal",
                        "immediate_effect": 0,
                        "annual_effect": -0.01,
                        "saturation_level": 0.2,
                        "delay_years": 10
                    }
                }
            }
        }
        
    def simulate_intervention(self, intervention_type, custom_parameters=None,
                           years_to_simulate=30, baseline_scenario="moderate"):
        """
        Simulate the effect of a climate intervention.
        
        Args:
            intervention_type: Type of intervention to simulate
            custom_parameters: Optional custom parameters for the intervention
            years_to_simulate: Number of years to simulate
            baseline_scenario: Baseline climate scenario
            
        Returns:
            DataFrame with intervention simulation results
        """
        if intervention_type not in self.intervention_effects:
            logger.error(f"Unsupported intervention type: {intervention_type}")
            return None
            
        # Get the intervention details
        intervention = self.intervention_effects[intervention_type]
        
        # Update parameters with custom ones if provided
        parameters = intervention["parameters"].copy()
        if custom_parameters:
            parameters.update(custom_parameters)
            
        # Get effects for this intervention
        effects = intervention["effects"]
        
        # Generate baseline predictions for each affected climate variable
        baselines = {}
        for variable in effects:
            baselines[variable] = self.predictor.generate_prediction(
                variable, None, years_to_simulate, baseline_scenario
            )
            
        # Apply intervention effects to each variable
        results = {}
        for variable, effect in effects.items():
            # Get the baseline prediction
            baseline = baselines[variable]
            
            # Apply the intervention effect
            intervention_result = self._apply_intervention_effect(
                baseline, effect, parameters, years_to_simulate
            )
            
            # Store the result
            results[variable] = intervention_result
            
        # Return the most significant result (usually CO2 or temperature)
        primary_variable = "temperature" if "temperature" in results else "co2"
        return results[primary_variable]
        
    def _apply_intervention_effect(self, baseline, effect, parameters, years):
        """
        Apply an intervention effect to a baseline prediction.
        
        Args:
            baseline: DataFrame with baseline prediction
            effect: Dictionary with effect parameters
            parameters: Dictionary with intervention parameters
            years: Number of years to simulate
            
        Returns:
            DataFrame with modified prediction
        """
        # Extract effect parameters
        factor_type = effect["factor_type"]
        immediate_effect = effect["immediate_effect"]
        annual_effect = effect["annual_effect"]
        saturation_level = effect["saturation_level"]
        delay_years = effect["delay_years"]
        
        # Extract relevant intervention parameters
        implementation_speed = parameters.get("implementation_speed", 0.5)
        coverage = parameters.get("coverage", 0.7)
        
        # Create a copy of the baseline
        result = baseline.copy()
        
        # Calculate the implementation curve
        # (sigmoid function to model gradual implementation)
        years_array = np.array(range(years + 1))
        midpoint = delay_years + 5.0 / implementation_speed
        steepness = implementation_speed * 0.5
        implementation_curve = 1.0 / (1.0 + np.exp(-steepness * (years_array - midpoint)))
        
        # Scale by coverage
        implementation_curve *= coverage
        
        # Apply effect based on factor type
        if factor_type == "emission_reduction" or factor_type == "carbon_sequestration" or factor_type == "carbon_removal":
            # These affect the rate of change (trend)
            
            # First, apply immediate effect after delay
            for i, year in enumerate(result["year"]):
                year_index = year - result["year"].min()
                
                if year_index >= delay_years:
                    # Calculate total effect at this time point
                    time_since_delay = year_index - delay_years
                    cumulative_effect = (immediate_effect + 
                                       annual_effect * time_since_delay) * implementation_curve[year_index]
                    
                    # Ensure we don't exceed saturation level
                    if abs(cumulative_effect) > saturation_level:
                        cumulative_effect = -saturation_level if cumulative_effect < 0 else saturation_level
                    
                    # Apply to the baseline trend
                    baseline_value = baseline.loc[i, "value"]
                    result.loc[i, "value"] = baseline_value * (1 + cumulative_effect)
                    
                    # Update uncertainty bounds
                    uncertainty = result.loc[i, "uncertainty"]
                    result.loc[i, "lower_bound"] = result.loc[i, "value"] - 1.96 * uncertainty
                    result.loc[i, "upper_bound"] = result.loc[i, "value"] + 1.96 * uncertainty
                    
        elif factor_type == "trend_reduction":
            # This affects the trend itself
            
            # Calculate baseline trend
            baseline_trend = (baseline.iloc[-1]["value"] - baseline.iloc[0]["value"]) / len(baseline)
            
            # Apply modified trend after delay
            for i, year in enumerate(result["year"]):
                year_index = year - result["year"].min()
                
                if year_index >= delay_years:
                    # Calculate effect on trend at this time point
                    time_since_delay = year_index - delay_years
                    trend_effect = (immediate_effect + 
                                  annual_effect * time_since_delay) * implementation_curve[year_index]
                    
                    # Ensure we don't exceed saturation level
                    if abs(trend_effect) > saturation_level:
                        trend_effect = -saturation_level if trend_effect < 0 else saturation_level
                    
                    # Apply modified trend
                    modified_trend = baseline_trend * (1 + trend_effect)
                    time_since_delay = time_since_delay if time_since_delay > 0 else 0
                    
                    first_affected_value = baseline.loc[baseline["year"] == (baseline["year"].min() + delay_years), "value"].iloc[0]
                    result.loc[i, "value"] = first_affected_value + modified_trend * time_since_delay
                    
                    # Update uncertainty bounds
                    uncertainty = result.loc[i, "uncertainty"]
                    result.loc[i, "lower_bound"] = result.loc[i, "value"] - 1.96 * uncertainty
                    result.loc[i, "upper_bound"] = result.loc[i, "value"] + 1.96 * uncertainty
        
        # Add intervention metadata
        result["intervention"] = True
        
        return result
        
    def simulate_policy_package(self, interventions, years_to_simulate=30, 
                           baseline_scenario="moderate"):
        """
        Simulate a package of policy interventions.
        
        Args:
            interventions: List of dictionaries with intervention details
            years_to_simulate: Number of years to simulate
            baseline_scenario: Baseline climate scenario
            
        Returns:
            Dictionary with simulation results for each climate variable
        """
        if not interventions:
            logger.error("No interventions provided")
            return None
            
        # Generate baseline predictions for climate variables
        variables = set()
        for intervention in interventions:
            intervention_type = intervention["type"]
            if intervention_type in self.intervention_effects:
                variables.update(self.intervention_effects[intervention_type]["effects"].keys())
        
        baselines = {}
        for variable in variables:
            baselines[variable] = self.predictor.generate_prediction(
                variable, None, years_to_simulate, baseline_scenario
            )
            
        # Apply each intervention sequentially
        # Note: This is a simplification; in reality, interactions between interventions would be complex
        results = baselines.copy()
        
        for intervention in interventions:
            intervention_type = intervention["type"]
            parameters = intervention.get("parameters", None)
            
            if intervention_type not in self.intervention_effects:
                continue
                
            # Get effects for this intervention
            intervention_effects = self.intervention_effects[intervention_type]["effects"]
            
            # Apply to each affected variable
            for variable, effect in intervention_effects.items():
                # Use the current result as the new baseline
                current_baseline = results[variable]
                
                # Apply the intervention effect
                intervention_result = self._apply_intervention_effect(
                    current_baseline, effect, 
                    parameters or self.intervention_effects[intervention_type]["parameters"],
                    years_to_simulate
                )
                
                # Update the result
                results[variable] = intervention_result
                
        # Add the intervention package ID to each result
        package_id = "policy_package_" + datetime.now().strftime("%Y%m%d%H%M%S")
        for variable in results:
            results[variable]["package_id"] = package_id
            
        return results
        
    def get_available_interventions(self):
        """
        Get list of available interventions.
        
        Returns:
            Dictionary with intervention types and descriptions
        """
        return {
            key: {
                "description": info["description"],
                "parameter_defaults": info["parameters"],
                "affected_variables": list(info["effects"].keys())
            }
            for key, info in self.intervention_effects.items()
        }
        
    def create_intervention_comparison_chart(self, variable, interventions, years_to_simulate=30):
        """
        Create a comparison chart for multiple interventions.
        
        Args:
            variable: Climate variable to compare (temperature, co2, etc.)
            interventions: List of intervention types to compare
            years_to_simulate: Number of years to simulate
            
        Returns:
            Plotly figure object
        """
        # Generate baseline
        baseline = self.predictor.generate_prediction(
            variable, None, years_to_simulate, "moderate"
        )
        
        # Simulate each intervention
        results = {}
        results["baseline"] = baseline
        
        for intervention_type in interventions:
            if intervention_type in self.intervention_effects:
                result = self.simulate_intervention(
                    intervention_type, None, years_to_simulate, "moderate"
                )
                if variable in self.intervention_effects[intervention_type]["effects"]:
                    results[intervention_type] = result
        
        # Create figure
        fig = go.Figure()
        
        # Add baseline
        fig.add_trace(go.Scatter(
            x=baseline["year"],
            y=baseline["value"],
            mode="lines",
            name="Baseline (No Intervention)",
            line=dict(color="red", width=3)
        ))
        
        # Add uncertainty band for baseline
        fig.add_trace(go.Scatter(
            x=baseline["year"].tolist() + baseline["year"].tolist()[::-1],
            y=baseline["upper_bound"].tolist() + baseline["lower_bound"].tolist()[::-1],
            fill="toself",
            fillcolor="rgba(255, 0, 0, 0.1)",
            line=dict(color="rgba(255, 0, 0, 0.2)"),
            showlegend=False
        ))
        
        # Add each intervention
        colors = ["green", "blue", "purple", "orange", "cyan", "magenta", "yellow"]
        for i, (intervention_type, result) in enumerate(results.items()):
            if intervention_type == "baseline":
                continue
                
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=result["year"],
                y=result["value"],
                mode="lines",
                name=self.intervention_effects[intervention_type]["description"],
                line=dict(color=color, width=2)
            ))
            
            # Add uncertainty band
            fig.add_trace(go.Scatter(
                x=result["year"].tolist() + result["year"].tolist()[::-1],
                y=result["upper_bound"].tolist() + result["lower_bound"].tolist()[::-1],
                fill="toself",
                fillcolor=f"rgba({','.join(map(str, px.colors.hex_to_rgb(px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)])))},.1)",
                line=dict(color=f"rgba({','.join(map(str, px.colors.hex_to_rgb(px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)])))},.2)"),
                showlegend=False
            ))
        
        # Add labels and title
        variable_labels = {
            "temperature": "Global Temperature Anomaly (°C)",
            "sea_level": "Sea Level Rise (mm)",
            "co2": "CO₂ Concentration (ppm)",
            "ice_extent": "Arctic Sea Ice Extent (million km²)",
            "extreme_events": "Number of Extreme Weather Events"
        }
        
        fig.update_layout(
            title=f"Impact of Climate Interventions on {variable_labels.get(variable, variable.title())}",
            xaxis_title="Year",
            yaxis_title=variable_labels.get(variable, variable.title()),
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add annotations for key points
        current_year = datetime.now().year
        fig.add_vline(x=current_year, line_dash="dash", line_width=1, line_color="gray")
        fig.add_annotation(
            x=current_year, y=fig.data[0]["y"][0],
            text="Present Day",
            showarrow=False,
            yshift=10
        )
        
        return fig
        
    def calculate_intervention_effectiveness(self, variable, intervention_type, 
                                       custom_parameters=None, years_to_simulate=30):
        """
        Calculate the effectiveness of an intervention.
        
        Args:
            variable: Climate variable to analyze
            intervention_type: Type of intervention
            custom_parameters: Optional custom parameters
            years_to_simulate: Number of years to simulate
            
        Returns:
            Dictionary with effectiveness metrics
        """
        # Generate baseline
        baseline = self.predictor.generate_prediction(
            variable, None, years_to_simulate, "moderate"
        )
        
        # Simulate intervention
        result = self.simulate_intervention(
            intervention_type, custom_parameters, years_to_simulate, "moderate"
        )
        
        # Calculate metrics
        baseline_end = baseline.iloc[-1]["value"]
        intervention_end = result.iloc[-1]["value"]
        
        absolute_difference = intervention_end - baseline_end
        relative_difference = absolute_difference / abs(baseline_end) * 100
        
        # Calculate time gained/lost (if applicable)
        time_equivalent = "N/A"
        
        if variable in ["temperature", "co2", "sea_level"]:
            # For these variables, calculate how many years the intervention
            # delays reaching a certain threshold
            
            # Find the year in the baseline when the value exceeds the intervention end value
            equivalent_years = baseline[baseline["value"] >= intervention_end]
            
            if not equivalent_years.empty:
                equivalent_year = equivalent_years.iloc[0]["year"]
                final_year = result.iloc[-1]["year"]
                time_gained = final_year - equivalent_year
                time_equivalent = f"{time_gained} years"
        
        return {
            "variable": variable,
            "intervention": intervention_type,
            "baseline_end_value": baseline_end,
            "intervention_end_value": intervention_end,
            "absolute_difference": absolute_difference,
            "relative_difference": relative_difference,
            "time_equivalent": time_equivalent,
            "cost_effectiveness": self._estimate_cost_effectiveness(intervention_type, relative_difference),
            "years_simulated": years_to_simulate,
            "parameters": custom_parameters or self.intervention_effects[intervention_type]["parameters"]
        }
        
    def _estimate_cost_effectiveness(self, intervention_type, impact_percentage):
        """
        Estimate cost-effectiveness of an intervention.
        
        Args:
            intervention_type: Type of intervention
            impact_percentage: Percentage impact of the intervention
            
        Returns:
            Cost-effectiveness rating (1-10)
        """
        # This is a simplified model - in reality would be much more complex
        # and based on economic models
        
        # Rough cost estimates for each intervention type (1-10 scale)
        cost_estimates = {
            "renewable_energy": 7,  # High initial investment
            "reforestation": 3,  # Lower cost
            "industrial_efficiency": 5,  # Medium cost
            "carbon_pricing": 2,  # Low direct cost (high indirect)
            "transportation_electrification": 8,  # High cost
            "building_efficiency": 6,  # Medium-high cost
            "agricultural_practices": 4,  # Medium-low cost
            "direct_air_capture": 9  # Very high cost
        }
        
        cost = cost_estimates.get(intervention_type, 5)
        
        # Normalize impact to a 0-10 scale
        # Assuming 20% impact is very good (10)
        normalized_impact = min(10, abs(impact_percentage) / 2)
        
        # Calculate cost-effectiveness (impact per unit cost)
        cost_effectiveness = normalized_impact / cost * 10
        
        return min(10, cost_effectiveness)