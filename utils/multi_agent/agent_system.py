"""
Multi-Agent Climate Simulation System for GAIA-∞ Climate Intelligence Platform.

This module provides an agent-based modeling framework for simulating complex climate
policy interactions, stakeholder behaviors, and their impacts on climate outcomes.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx
from collections import defaultdict
import random
import json

class ClimateAgent:
    """Base class for climate agents in the multi-agent system."""
    
    def __init__(self, agent_id, agent_type, initial_state=None):
        self.id = agent_id
        self.type = agent_type
        self.state = initial_state or {}
        self.knowledge = {}
        self.goals = []
        self.connections = []
        self.memory = []
        self.policies = {}
        
    def update_state(self, new_state):
        """Update agent's state."""
        self.state.update(new_state)
        
    def add_knowledge(self, key, value):
        """Add to agent's knowledge base."""
        self.knowledge[key] = value
        
    def add_goal(self, goal, priority=1.0):
        """Add a goal with priority."""
        self.goals.append({
            'description': goal,
            'priority': priority,
            'status': 'active'
        })
        
    def connect_to(self, agent_id, connection_type, strength=1.0):
        """Connect to another agent."""
        self.connections.append({
            'agent_id': agent_id,
            'type': connection_type,
            'strength': strength
        })
        
    def remember(self, event):
        """Add an event to agent's memory."""
        self.memory.append({
            'event': event,
            'timestamp': len(self.memory)
        })
        
    def add_policy(self, policy_name, policy_function, activation_threshold=0.5):
        """Add a policy decision function."""
        self.policies[policy_name] = {
            'function': policy_function,
            'threshold': activation_threshold
        }
        
    def decide(self, environment_state):
        """Make a decision based on policies, goals, and environment."""
        # Find active policies
        actions = []
        for policy_name, policy in self.policies.items():
            activation = policy['function'](self.state, environment_state)
            if activation >= policy['threshold']:
                actions.append({
                    'policy': policy_name,
                    'activation': activation
                })
        
        # Sort by activation level
        actions.sort(key=lambda x: x['activation'], reverse=True)
        return actions
    
    def act(self, action, environment):
        """Execute an action in the environment."""
        result = environment.process_action(self.id, action)
        self.remember({
            'action': action,
            'result': result
        })
        return result
    
    def serialize(self):
        """Convert agent to serializable format."""
        return {
            'id': self.id,
            'type': self.type,
            'state': self.state,
            'goals': self.goals,
            'connections': self.connections
        }


class PolicyMakerAgent(ClimateAgent):
    """Agent representing government or policy-making entity."""
    
    def __init__(self, agent_id, region, policy_priorities=None, initial_state=None):
        super().__init__(agent_id, 'policy_maker', initial_state)
        self.region = region
        self.policy_priorities = policy_priorities or {
            'economic_growth': 0.7,
            'environmental_protection': 0.4,
            'social_welfare': 0.6,
            'technological_innovation': 0.5
        }
        self.implemented_policies = []
        
        # Add default policies
        self.add_policy('carbon_tax', self._evaluate_carbon_tax, 0.6)
        self.add_policy('renewable_subsidy', self._evaluate_renewable_subsidy, 0.5)
        self.add_policy('efficiency_standards', self._evaluate_efficiency_standards, 0.4)
        
    def _evaluate_carbon_tax(self, agent_state, environment_state):
        """Evaluate whether to implement carbon tax."""
        # Example decision logic based on environmental concern and economic impact
        environmental_concern = environment_state.get('global_temperature_anomaly', 0) / 2.0
        economic_strength = agent_state.get('economic_index', 0.5)
        
        # Higher activation when environment concern is high and economy is strong
        activation = (environmental_concern * self.policy_priorities['environmental_protection'] +
                     economic_strength * (1 - self.policy_priorities['economic_growth']))
        
        return min(1.0, max(0.0, activation))
    
    def _evaluate_renewable_subsidy(self, agent_state, environment_state):
        """Evaluate whether to implement renewable energy subsidies."""
        technology_readiness = environment_state.get('renewable_technology_index', 0.5)
        fossil_fuel_dependence = agent_state.get('fossil_fuel_dependence', 0.7)
        
        # Higher activation with high tech readiness and high fossil dependence
        activation = (technology_readiness * self.policy_priorities['technological_innovation'] +
                     fossil_fuel_dependence * self.policy_priorities['environmental_protection'])
        
        return min(1.0, max(0.0, activation / 2.0))
    
    def _evaluate_efficiency_standards(self, agent_state, environment_state):
        """Evaluate whether to implement efficiency standards."""
        public_support = agent_state.get('public_support', 0.5)
        industry_resistance = agent_state.get('industry_resistance', 0.5)
        
        # Higher activation with high public support and low industry resistance
        activation = (public_support * self.policy_priorities['social_welfare'] -
                     industry_resistance * (1 - self.policy_priorities['economic_growth']))
        
        return min(1.0, max(0.0, activation))
    
    def implement_policy(self, policy_name, policy_strength, environment):
        """Implement a specific policy."""
        policy = {
            'name': policy_name,
            'strength': policy_strength,
            'implemented_at': environment.current_time,
            'region': self.region
        }
        
        self.implemented_policies.append(policy)
        result = environment.register_policy(self.id, policy)
        
        self.remember({
            'action': f"Implemented {policy_name}",
            'policy': policy,
            'result': result
        })
        
        return result


class IndustryAgent(ClimateAgent):
    """Agent representing industrial sector or corporation."""
    
    def __init__(self, agent_id, industry_type, region, initial_state=None):
        super().__init__(agent_id, 'industry', initial_state)
        self.industry_type = industry_type
        self.region = region
        self.emissions = initial_state.get('emissions', 100.0)
        self.profit_motive = initial_state.get('profit_motive', 0.8)
        self.innovation_capacity = initial_state.get('innovation_capacity', 0.5)
        self.market_share = initial_state.get('market_share', 0.1)
        
        # Add default policies
        self.add_policy('reduce_emissions', self._evaluate_emission_reduction, 0.4)
        self.add_policy('invest_clean_tech', self._evaluate_clean_tech_investment, 0.3)
        self.add_policy('business_as_usual', self._evaluate_business_as_usual, 0.7)
        
    def _evaluate_emission_reduction(self, agent_state, environment_state):
        """Evaluate whether to reduce emissions."""
        carbon_price = environment_state.get('carbon_price', 0.0)
        regulatory_pressure = environment_state.get('regulatory_pressure', 0.2)
        consumer_pressure = environment_state.get('consumer_green_preference', 0.3)
        
        # Higher activation with high carbon price and pressure
        activation = (carbon_price * 2.0 +
                      regulatory_pressure +
                      consumer_pressure -
                      self.profit_motive * 0.5)
        
        return min(1.0, max(0.0, activation / 3.0))
    
    def _evaluate_clean_tech_investment(self, agent_state, environment_state):
        """Evaluate whether to invest in clean technology."""
        tech_cost = environment_state.get('clean_tech_cost', 0.8)
        subsidy_level = environment_state.get('clean_tech_subsidy', 0.2)
        market_trend = environment_state.get('green_market_trend', 0.4)
        
        # Higher activation with low tech cost, high subsidies and positive market trends
        activation = (self.innovation_capacity +
                      subsidy_level +
                      market_trend -
                      tech_cost)
        
        return min(1.0, max(0.0, activation / 3.0))
    
    def _evaluate_business_as_usual(self, agent_state, environment_state):
        """Evaluate whether to continue business as usual."""
        carbon_price = environment_state.get('carbon_price', 0.0)
        regulatory_pressure = environment_state.get('regulatory_pressure', 0.2)
        
        # Higher activation with low carbon price and regulation
        activation = (self.profit_motive * 1.2 -
                     carbon_price * 2.0 -
                     regulatory_pressure)
        
        return min(1.0, max(0.0, activation / 2.0))
    
    def update_emissions(self, change_factor, environment):
        """Update emissions based on actions."""
        old_emissions = self.emissions
        self.emissions *= change_factor
        
        result = environment.update_agent_emissions(self.id, old_emissions, self.emissions)
        
        self.remember({
            'action': f"Updated emissions by factor {change_factor:.2f}",
            'old_emissions': old_emissions,
            'new_emissions': self.emissions,
            'result': result
        })
        
        return result


class ConsumerAgent(ClimateAgent):
    """Agent representing consumer or public behavior."""
    
    def __init__(self, agent_id, region, demographic=None, initial_state=None):
        super().__init__(agent_id, 'consumer', initial_state)
        self.region = region
        self.demographic = demographic or 'general'
        self.environmental_concern = initial_state.get('environmental_concern', 0.5)
        self.economic_sensitivity = initial_state.get('economic_sensitivity', 0.7)
        self.consumption_level = initial_state.get('consumption_level', 1.0)
        
        # Add default policies
        self.add_policy('reduce_consumption', self._evaluate_consumption_reduction, 0.4)
        self.add_policy('choose_green_products', self._evaluate_green_products, 0.3)
        self.add_policy('pressure_for_policy', self._evaluate_policy_pressure, 0.2)
        
    def _evaluate_consumption_reduction(self, agent_state, environment_state):
        """Evaluate whether to reduce consumption."""
        economic_conditions = environment_state.get('economic_index', 0.5)
        climate_events = environment_state.get('extreme_events_index', 0.2)
        
        # Higher activation with poor economy or high climate impacts
        activation = (self.environmental_concern +
                      climate_events -
                      economic_conditions * self.economic_sensitivity)
        
        return min(1.0, max(0.0, activation / 2.0))
    
    def _evaluate_green_products(self, agent_state, environment_state):
        """Evaluate whether to choose green products."""
        price_premium = environment_state.get('green_price_premium', 0.3)
        product_availability = environment_state.get('green_product_availability', 0.5)
        
        # Higher activation with low price premium and high availability
        activation = (self.environmental_concern +
                      product_availability -
                      price_premium * self.economic_sensitivity)
        
        return min(1.0, max(0.0, activation / 2.0))
    
    def _evaluate_policy_pressure(self, agent_state, environment_state):
        """Evaluate whether to pressure for policy change."""
        climate_events = environment_state.get('extreme_events_index', 0.2)
        political_opportunity = environment_state.get('political_receptiveness', 0.3)
        
        # Higher activation with extreme events and political opening
        activation = (self.environmental_concern * 1.5 +
                      climate_events +
                      political_opportunity -
                      0.5)
        
        return min(1.0, max(0.0, activation / 3.0))
    
    def update_consumption(self, change_factor, environment):
        """Update consumption level based on decisions."""
        old_consumption = self.consumption_level
        self.consumption_level *= change_factor
        
        result = environment.update_agent_consumption(self.id, old_consumption, self.consumption_level)
        
        self.remember({
            'action': f"Updated consumption by factor {change_factor:.2f}",
            'old_consumption': old_consumption,
            'new_consumption': self.consumption_level,
            'result': result
        })
        
        return result


class ClimateMultiAgentSystem:
    """
    Multi-agent system for climate policy and behavior simulation.
    """
    
    def __init__(self):
        self.agents = {}
        self.environment = ClimateEnvironment()
        self.time = 0
        self.graph = nx.DiGraph()
        self.history = []
        self.global_policies = []
        
    def add_agent(self, agent):
        """Add an agent to the system."""
        self.agents[agent.id] = agent
        self.graph.add_node(agent.id, agent_type=agent.type)
        return agent.id
    
    def connect_agents(self, agent1_id, agent2_id, connection_type, strength=1.0):
        """Create a connection between two agents."""
        if agent1_id in self.agents and agent2_id in self.agents:
            self.agents[agent1_id].connect_to(agent2_id, connection_type, strength)
            self.graph.add_edge(agent1_id, agent2_id, type=connection_type, strength=strength)
            return True
        return False
    
    def create_region_network(self, region, n_policy=1, n_industry=3, n_consumer=5):
        """Create a network of agents for a specific region."""
        agents = []
        
        # Create policy maker
        for i in range(n_policy):
            agent_id = f"policy_{region}_{i}"
            agent = PolicyMakerAgent(agent_id, region)
            self.add_agent(agent)
            agents.append(agent_id)
        
        # Create industries
        industry_types = ['energy', 'manufacturing', 'transportation', 'agriculture', 'services']
        for i in range(n_industry):
            agent_id = f"industry_{region}_{i}"
            industry_type = industry_types[i % len(industry_types)]
            agent = IndustryAgent(agent_id, industry_type, region)
            self.add_agent(agent)
            agents.append(agent_id)
            
            # Connect to policy makers
            for p_id in agents[:n_policy]:
                self.connect_agents(p_id, agent_id, 'regulates', 0.8)
                self.connect_agents(agent_id, p_id, 'influences', 0.6)
        
        # Create consumers
        demographics = ['general', 'low_income', 'middle_income', 'high_income', 'youth']
        for i in range(n_consumer):
            agent_id = f"consumer_{region}_{i}"
            demographic = demographics[i % len(demographics)]
            agent = ConsumerAgent(agent_id, region, demographic)
            self.add_agent(agent)
            agents.append(agent_id)
            
            # Connect to policy makers
            for p_id in agents[:n_policy]:
                self.connect_agents(agent_id, p_id, 'votes', 0.4)
                self.connect_agents(p_id, agent_id, 'influences', 0.3)
            
            # Connect to industries
            for ind_id in agents[n_policy:n_policy+n_industry]:
                self.connect_agents(agent_id, ind_id, 'buys_from', 0.5)
                self.connect_agents(ind_id, agent_id, 'sells_to', 0.5)
        
        return agents
    
    def run_simulation(self, steps=20):
        """Run the multi-agent simulation for a number of steps."""
        results = []
        
        for step in range(steps):
            self.time = step
            self.environment.current_time = step
            
            # Update environment state
            self.environment.update_state()
            env_state = self.environment.get_state()
            
            # Record current state
            state_record = {
                'time': step,
                'environment': env_state,
                'agents': {},
                'emissions': self.environment.global_emissions,
                'temperature': self.environment.global_temperature,
                'policies': len(self.environment.active_policies)
            }
            
            # Let each agent decide and act
            for agent_id, agent in self.agents.items():
                # Get agent decisions
                decisions = agent.decide(env_state)
                
                # Take top decision
                if decisions:
                    top_decision = decisions[0]
                    # Execute appropriate action based on agent type
                    if agent.type == 'policy_maker':
                        if top_decision['policy'] == 'carbon_tax':
                            agent.implement_policy('carbon_tax', top_decision['activation'], self.environment)
                        elif top_decision['policy'] == 'renewable_subsidy':
                            agent.implement_policy('renewable_subsidy', top_decision['activation'], self.environment)
                    
                    elif agent.type == 'industry':
                        if top_decision['policy'] == 'reduce_emissions':
                            factor = max(0.8, 1.0 - top_decision['activation'] * 0.4)
                            agent.update_emissions(factor, self.environment)
                        elif top_decision['policy'] == 'business_as_usual':
                            # Slight increase in emissions
                            factor = 1.0 + (top_decision['activation'] * 0.1)
                            agent.update_emissions(factor, self.environment)
                    
                    elif agent.type == 'consumer':
                        if top_decision['policy'] == 'reduce_consumption':
                            factor = max(0.9, 1.0 - top_decision['activation'] * 0.2)
                            agent.update_consumption(factor, self.environment)
                
                # Record agent state
                state_record['agents'][agent_id] = {
                    'type': agent.type,
                    'state': agent.state.copy(),
                    'decisions': decisions
                }
            
            # Calculate feedbacks
            self.environment.calculate_feedbacks()
            
            # Save state record
            results.append(state_record)
            self.history.append(state_record)
        
        return results
    
    def get_stats(self):
        """Get summary statistics from the simulation."""
        if not self.history:
            return None
            
        first_state = self.history[0]
        last_state = self.history[-1]
        
        stats = {
            'simulation_length': len(self.history),
            'num_agents': len(self.agents),
            'agent_types': {
                'policy_maker': sum(1 for a in self.agents.values() if a.type == 'policy_maker'),
                'industry': sum(1 for a in self.agents.values() if a.type == 'industry'),
                'consumer': sum(1 for a in self.agents.values() if a.type == 'consumer')
            },
            'emissions': {
                'start': first_state['emissions'],
                'end': last_state['emissions'],
                'change': last_state['emissions'] - first_state['emissions'],
                'percent_change': ((last_state['emissions'] - first_state['emissions']) / 
                                  first_state['emissions'] * 100) if first_state['emissions'] else 0
            },
            'temperature': {
                'start': first_state['temperature'],
                'end': last_state['temperature'],
                'change': last_state['temperature'] - first_state['temperature']
            },
            'policies': {
                'total_implemented': sum(state['policies'] for state in self.history),
                'final_active': last_state['policies']
            }
        }
        
        return stats
    
    def visualize_network(self):
        """Visualize the agent network."""
        if not self.graph.nodes():
            return None
        
        # Create position layout
        pos = nx.spring_layout(self.graph)
        
        # Create a Plotly figure
        fig = go.Figure()
        
        # Define node colors by type
        color_map = {
            'policy_maker': 'red',
            'industry': 'blue',
            'consumer': 'green'
        }
        
        # Add nodes
        for node_type in color_map:
            node_x = []
            node_y = []
            node_text = []
            
            for node in self.graph.nodes():
                if self.graph.nodes[node].get('agent_type') == node_type:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(f"{node}<br>Type: {node_type}")
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                marker=dict(
                    size=15,
                    color=color_map[node_type],
                    line_width=2
                ),
                text=node_text,
                name=node_type.replace('_', ' ').title()
            ))
        
        # Add edges
        edge_x = []
        edge_y = []
        edge_text = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            edge_type = self.graph.edges[edge].get('type', 'unknown')
            strength = self.graph.edges[edge].get('strength', 0)
            edge_text.append(f"Type: {edge_type}<br>Strength: {strength:.2f}")
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title='Multi-Agent Climate Network',
            titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template='plotly_white'
        )
        
        return fig
    
    def plot_emissions_trajectory(self):
        """Plot the emissions trajectory from the simulation."""
        if not self.history:
            return None
            
        # Extract data
        times = [state['time'] for state in self.history]
        emissions = [state['emissions'] for state in self.history]
        temperatures = [state['temperature'] for state in self.history]
        
        # Create figure
        fig = go.Figure()
        
        # Add emissions trace
        fig.add_trace(go.Scatter(
            x=times,
            y=emissions,
            name='Global Emissions',
            line=dict(color='red', width=3)
        ))
        
        # Create secondary y-axis for temperature
        fig.add_trace(go.Scatter(
            x=times,
            y=temperatures,
            name='Global Temperature',
            line=dict(color='orange', width=3),
            yaxis='y2'
        ))
        
        # Add events for policy implementations
        policy_times = []
        policy_names = []
        
        for state in self.history:
            if state['policies'] > (policy_times and self.history[state['time']-1]['policies'] or 0):
                policy_times.append(state['time'])
                policy_names.append(f"New policies implemented")
        
        for t, name in zip(policy_times, policy_names):
            fig.add_vline(
                x=t,
                line_dash="dash",
                line_width=1,
                line_color="green",
                annotation_text=name,
                annotation_position="top right"
            )
        
        # Update layout
        fig.update_layout(
            title='Emissions and Temperature Trajectory',
            xaxis_title='Simulation Time',
            yaxis_title='Global Emissions (GtCO₂e)',
            template='plotly_white',
            hovermode='x unified',
            yaxis2=dict(
                title='Global Temperature (°C)',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        
        return fig


class ClimateEnvironment:
    """Environment for the climate multi-agent system."""
    
    def __init__(self):
        self.current_time = 0
        self.global_emissions = 50.0  # GtCO2e
        self.global_temperature = 1.1  # °C above pre-industrial
        self.state = {
            'carbon_price': 0.0,
            'regulatory_pressure': 0.2,
            'consumer_green_preference': 0.3,
            'clean_tech_cost': 0.8,
            'clean_tech_subsidy': 0.2,
            'green_market_trend': 0.4,
            'economic_index': 0.6,
            'extreme_events_index': 0.2,
            'green_price_premium': 0.3,
            'green_product_availability': 0.5,
            'political_receptiveness': 0.4,
            'global_temperature_anomaly': 1.1,
            'renewable_technology_index': 0.6
        }
        self.active_policies = []
        self.agent_emissions = defaultdict(float)
        self.agent_consumption = defaultdict(float)
        
    def update_state(self):
        """Update the environment state based on current conditions."""
        # Update extreme events based on temperature
        self.state['extreme_events_index'] = min(1.0, 0.1 + self.global_temperature * 0.1)
        
        # Update global temperature anomaly
        self.state['global_temperature_anomaly'] = self.global_temperature
        
        # Update economic index (simplified model)
        damage_from_climate = self.global_temperature * 0.05
        self.state['economic_index'] = max(0.1, min(1.0, self.state['economic_index'] - damage_from_climate + 0.02))
        
        # Update carbon price based on active policies
        carbon_tax_policies = [p for p in self.active_policies if p['name'] == 'carbon_tax']
        self.state['carbon_price'] = sum(p['strength'] for p in carbon_tax_policies) / 5.0
        
        # Update clean tech subsidies
        subsidy_policies = [p for p in self.active_policies if p['name'] == 'renewable_subsidy']
        self.state['clean_tech_subsidy'] = sum(p['strength'] for p in subsidy_policies) / 5.0
        
        # Update clean tech cost (decreases over time and with subsidies)
        self.state['clean_tech_cost'] = max(0.2, self.state['clean_tech_cost'] * 
                                         (0.98 - self.state['clean_tech_subsidy'] * 0.1))
        
        # Update green market trends
        self.state['green_market_trend'] = min(1.0, self.state['green_market_trend'] + 
                                            (self.state['consumer_green_preference'] - 0.5) * 0.05)
        
        # Update regulatory pressure
        active_policy_count = len(self.active_policies)
        self.state['regulatory_pressure'] = min(1.0, 0.1 + active_policy_count * 0.05)
        
    def process_action(self, agent_id, action):
        """Process an agent action and return the result."""
        # Placeholder for action processing
        return {
            'success': True,
            'message': f"Action processed",
            'action': action
        }
    
    def register_policy(self, agent_id, policy):
        """Register a new policy in the environment."""
        policy['registered_at'] = self.current_time
        self.active_policies.append(policy)
        
        return {
            'success': True,
            'message': f"Policy {policy['name']} registered",
            'policy_id': len(self.active_policies) - 1
        }
    
    def update_agent_emissions(self, agent_id, old_emissions, new_emissions):
        """Update agent emissions and recalculate global emissions."""
        self.agent_emissions[agent_id] = new_emissions
        
        # Recalculate global emissions
        self.global_emissions = sum(self.agent_emissions.values()) or 50.0  # Fallback if no agents
        
        return {
            'success': True,
            'message': f"Emissions updated from {old_emissions:.1f} to {new_emissions:.1f}",
            'global_emissions': self.global_emissions
        }
    
    def update_agent_consumption(self, agent_id, old_consumption, new_consumption):
        """Update agent consumption and recalculate related metrics."""
        self.agent_consumption[agent_id] = new_consumption
        
        # Recalculate average consumption preferences
        if self.agent_consumption:
            avg_consumption = sum(self.agent_consumption.values()) / len(self.agent_consumption)
            # Update consumer green preference based on consumption
            self.state['consumer_green_preference'] = min(1.0, max(0.1, 
                self.state['consumer_green_preference'] + (1.0 - avg_consumption) * 0.05))
        
        return {
            'success': True,
            'message': f"Consumption updated from {old_consumption:.1f} to {new_consumption:.1f}"
        }
    
    def calculate_feedbacks(self):
        """Calculate climate feedbacks and update global temperature."""
        # Simplified temperature model based on emissions
        # Warming of ~0.5°C per 1000 GtCO2 cumulative emissions
        temperature_change = self.global_emissions * 0.0005
        
        # Climate inertia - temperature changes slowly
        self.global_temperature += temperature_change * 0.2
        
        # Update state
        self.state['global_temperature_anomaly'] = self.global_temperature
        
        return {
            'temperature_change': temperature_change,
            'global_temperature': self.global_temperature
        }
    
    def get_state(self):
        """Get the current environment state."""
        return self.state.copy()