"""
Carbon Credits Tracking System for GAIA-∞ Climate Intelligence Platform.

This module provides a decentralized carbon credit tracking and verification system,
enabling transparent monitoring, trading, and retirement of carbon credits.
"""

import numpy as np
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict

class CarbonCreditRegistry:
    """
    Carbon credit registry for tracking issuance, ownership, and retirement of credits.
    """
    
    def __init__(self):
        self.projects = {}
        self.credits = {}
        self.transactions = []
        self.entities = {}
        self.verification_records = {}
        self.methodologies = self._initialize_methodologies()
        self.last_sync = datetime.now()
    
    def _initialize_methodologies(self):
        """Initialize supported carbon credit methodologies."""
        return {
            'afforestation': {
                'name': 'Afforestation/Reforestation',
                'code': 'ARR',
                'description': 'Conversion of non-forest land to forest through planting or natural regeneration',
                'verification_requirements': ['growth_monitoring', 'satellite_imagery', 'soil_carbon_sampling'],
                'minimum_duration_years': 30,
                'typical_credit_rate': 5.0  # tCO2e per hectare per year
            },
            'avoided_deforestation': {
                'name': 'Avoided Deforestation',
                'code': 'REDD+',
                'description': 'Reducing emissions from deforestation and forest degradation',
                'verification_requirements': ['satellite_monitoring', 'ground_surveys', 'biodiversity_assessment'],
                'minimum_duration_years': 20,
                'typical_credit_rate': 10.0  # tCO2e per hectare per year
            },
            'renewable_energy': {
                'name': 'Renewable Energy',
                'code': 'RE',
                'description': 'Clean energy generation displacing fossil fuels',
                'verification_requirements': ['energy_metering', 'grid_connection_data', 'emission_factor_verification'],
                'minimum_duration_years': 10,
                'typical_credit_rate': 0.7  # tCO2e per MWh
            },
            'energy_efficiency': {
                'name': 'Energy Efficiency',
                'code': 'EE',
                'description': 'Reducing energy consumption through efficiency improvements',
                'verification_requirements': ['energy_monitoring', 'baseline_assessment', 'technology_verification'],
                'minimum_duration_years': 7,
                'typical_credit_rate': 0.4  # tCO2e per MWh saved
            },
            'methane_capture': {
                'name': 'Methane Capture',
                'code': 'MC',
                'description': 'Capturing and utilizing or destroying methane emissions',
                'verification_requirements': ['flow_metering', 'gas_composition_analysis', 'destruction_efficiency'],
                'minimum_duration_years': 10,
                'typical_credit_rate': 21.0  # CO2e multiplier for methane
            },
            'soil_carbon': {
                'name': 'Soil Carbon Sequestration',
                'code': 'SCS',
                'description': 'Agricultural practices that increase soil carbon storage',
                'verification_requirements': ['soil_sampling', 'practice_documentation', 'remote_sensing'],
                'minimum_duration_years': 20,
                'typical_credit_rate': 2.0  # tCO2e per hectare per year
            }
        }
    
    def register_entity(self, entity_id, name, entity_type, contact_info=None, metadata=None):
        """
        Register a new entity in the carbon credit system.
        
        Args:
            entity_id: Unique identifier for the entity
            name: Entity name
            entity_type: Type of entity (project_developer, verifier, buyer, etc.)
            contact_info: Optional contact information
            metadata: Optional additional metadata
            
        Returns:
            Success flag and message
        """
        if entity_id in self.entities:
            return False, f"Entity with ID {entity_id} already exists"
        
        self.entities[entity_id] = {
            'id': entity_id,
            'name': name,
            'type': entity_type,
            'contact_info': contact_info or {},
            'metadata': metadata or {},
            'credit_balance': 0,
            'registered_at': datetime.now().isoformat(),
            'projects': [],
            'transactions': []
        }
        
        return True, f"Entity {name} registered successfully with ID {entity_id}"
    
    def register_project(self, project_data):
        """
        Register a new carbon credit project.
        
        Args:
            project_data: Dictionary with project details
                - id: Unique project identifier
                - name: Project name
                - developer_id: ID of project developer
                - methodology: Carbon credit methodology
                - location: Geographic location (lat, lon)
                - area_hectares: Area covered by project
                - start_date: Project start date
                - end_date: Project end date
                - estimated_annual_credits: Estimated annual credits
                - description: Project description
                - additional_attributes: Any additional attributes
                
        Returns:
            Success flag and message
        """
        project_id = project_data.get('id', str(uuid.uuid4()))
        
        if project_id in self.projects:
            return False, f"Project with ID {project_id} already exists"
        
        # Validate required fields
        required_fields = ['name', 'developer_id', 'methodology', 'location', 'start_date', 'end_date']
        for field in required_fields:
            if field not in project_data:
                return False, f"Missing required field: {field}"
        
        # Validate developer exists
        developer_id = project_data['developer_id']
        if developer_id not in self.entities:
            return False, f"Developer with ID {developer_id} does not exist"
            
        # Validate methodology exists
        methodology = project_data['methodology']
        if methodology not in self.methodologies:
            return False, f"Methodology {methodology} is not supported"
            
        # Add registration timestamp and status
        project_data['registered_at'] = datetime.now().isoformat()
        project_data['status'] = 'registered'
        project_data['verification_status'] = 'pending'
        project_data['credits_issued'] = 0
        project_data['credits_retired'] = 0
        
        # Add ID if not provided
        project_data['id'] = project_id
        
        # Register the project
        self.projects[project_id] = project_data
        
        # Update entity's project list
        if developer_id in self.entities:
            self.entities[developer_id]['projects'].append(project_id)
        
        return True, f"Project {project_data['name']} registered successfully with ID {project_id}"
    
    def verify_project(self, project_id, verifier_id, verification_data):
        """
        Record verification of a carbon credit project.
        
        Args:
            project_id: ID of project being verified
            verifier_id: ID of the verifying entity
            verification_data: Dictionary with verification details
                - date: Verification date
                - findings: Verification findings
                - approved: Approval status (boolean)
                - methodology_compliance: Compliance with methodology
                - monitoring_data: Monitoring data used for verification
                - estimated_credits: Verified credit estimation
                
        Returns:
            Success flag and message
        """
        if project_id not in self.projects:
            return False, f"Project with ID {project_id} does not exist"
            
        if verifier_id not in self.entities:
            return False, f"Verifier with ID {verifier_id} does not exist"
            
        if self.entities[verifier_id]['type'] != 'verifier':
            return False, f"Entity {verifier_id} is not a registered verifier"
            
        # Create verification record
        verification_id = str(uuid.uuid4())
        verification_record = {
            'id': verification_id,
            'project_id': project_id,
            'verifier_id': verifier_id,
            'timestamp': datetime.now().isoformat(),
            'approved': verification_data.get('approved', False),
            'findings': verification_data.get('findings', ''),
            'methodology_compliance': verification_data.get('methodology_compliance', {}),
            'monitoring_data': verification_data.get('monitoring_data', {}),
            'estimated_credits': verification_data.get('estimated_credits', 0)
        }
        
        # Store verification record
        self.verification_records[verification_id] = verification_record
        
        # Update project status based on verification
        if verification_record['approved']:
            self.projects[project_id]['verification_status'] = 'verified'
            self.projects[project_id]['last_verification'] = verification_id
        else:
            self.projects[project_id]['verification_status'] = 'failed'
        
        return True, f"Project verification recorded: {'Approved' if verification_record['approved'] else 'Not approved'}"
    
    def issue_credits(self, project_id, amount, issuance_data=None):
        """
        Issue carbon credits for a verified project.
        
        Args:
            project_id: ID of the project
            amount: Amount of credits to issue
            issuance_data: Additional data related to issuance
                
        Returns:
            Success flag, message, and credit IDs
        """
        if project_id not in self.projects:
            return False, "Project does not exist", []
            
        project = self.projects[project_id]
        
        if project['verification_status'] != 'verified':
            return False, "Project must be verified before credits can be issued", []
            
        # Generate unique credit IDs
        credit_ids = []
        for _ in range(amount):
            credit_id = str(uuid.uuid4())
            credit_ids.append(credit_id)
            
            # Create credit record
            self.credits[credit_id] = {
                'id': credit_id,
                'project_id': project_id,
                'issued_at': datetime.now().isoformat(),
                'vintage': datetime.now().year,
                'current_owner': project['developer_id'],
                'status': 'active',
                'retirement_data': None,
                'metadata': issuance_data or {}
            }
            
        # Update project credit counter
        project['credits_issued'] += amount
        
        # Update developer's balance
        developer_id = project['developer_id']
        if developer_id in self.entities:
            self.entities[developer_id]['credit_balance'] += amount
        
        return True, f"Successfully issued {amount} credits for project {project_id}", credit_ids
    
    def transfer_credits(self, from_entity_id, to_entity_id, amount, price=None, transaction_type='sale', metadata=None):
        """
        Transfer carbon credits between entities.
        
        Args:
            from_entity_id: ID of the entity transferring credits
            to_entity_id: ID of the entity receiving credits
            amount: Number of credits to transfer
            price: Optional price per credit
            transaction_type: Type of transaction
            metadata: Additional transaction metadata
                
        Returns:
            Success flag and message
        """
        if from_entity_id not in self.entities:
            return False, f"Sending entity {from_entity_id} does not exist"
            
        if to_entity_id not in self.entities:
            return False, f"Receiving entity {to_entity_id} does not exist"
            
        sender = self.entities[from_entity_id]
        receiver = self.entities[to_entity_id]
        
        if sender['credit_balance'] < amount:
            return False, f"Insufficient credit balance: {sender['credit_balance']} < {amount}"
            
        # Find credits to transfer (oldest first)
        transferable_credits = []
        for credit_id, credit in self.credits.items():
            if credit['current_owner'] == from_entity_id and credit['status'] == 'active':
                transferable_credits.append(credit_id)
                if len(transferable_credits) == amount:
                    break
        
        if len(transferable_credits) < amount:
            return False, "Could not find enough active credits to transfer"
            
        # Create transaction record
        transaction_id = str(uuid.uuid4())
        transaction = {
            'id': transaction_id,
            'timestamp': datetime.now().isoformat(),
            'from_entity_id': from_entity_id,
            'to_entity_id': to_entity_id,
            'amount': amount,
            'price_per_credit': price,
            'transaction_type': transaction_type,
            'credit_ids': transferable_credits[:amount],
            'metadata': metadata or {}
        }
        
        # Record transaction
        self.transactions.append(transaction)
        
        # Update entity transaction lists
        sender['transactions'].append(transaction_id)
        receiver['transactions'].append(transaction_id)
        
        # Update credit ownership
        for credit_id in transferable_credits[:amount]:
            self.credits[credit_id]['current_owner'] = to_entity_id
        
        # Update credit balances
        sender['credit_balance'] -= amount
        receiver['credit_balance'] += amount
        
        return True, f"Successfully transferred {amount} credits from {from_entity_id} to {to_entity_id}"
    
    def retire_credits(self, entity_id, amount, retirement_purpose, beneficiary=None, metadata=None):
        """
        Retire carbon credits (permanently remove from circulation).
        
        Args:
            entity_id: ID of the entity retiring credits
            amount: Number of credits to retire
            retirement_purpose: Purpose of retirement
            beneficiary: Optional beneficiary of retirement
            metadata: Additional retirement metadata
                
        Returns:
            Success flag and message
        """
        if entity_id not in self.entities:
            return False, f"Entity {entity_id} does not exist"
            
        entity = self.entities[entity_id]
        
        if entity['credit_balance'] < amount:
            return False, f"Insufficient credit balance: {entity['credit_balance']} < {amount}"
            
        # Find credits to retire (oldest first)
        retirable_credits = []
        for credit_id, credit in self.credits.items():
            if credit['current_owner'] == entity_id and credit['status'] == 'active':
                retirable_credits.append(credit_id)
                if len(retirable_credits) == amount:
                    break
        
        if len(retirable_credits) < amount:
            return False, "Could not find enough active credits to retire"
            
        # Create retirement record
        retirement_data = {
            'timestamp': datetime.now().isoformat(),
            'entity_id': entity_id,
            'purpose': retirement_purpose,
            'beneficiary': beneficiary,
            'metadata': metadata or {}
        }
        
        # Create transaction record for retirement
        transaction_id = str(uuid.uuid4())
        transaction = {
            'id': transaction_id,
            'timestamp': datetime.now().isoformat(),
            'from_entity_id': entity_id,
            'to_entity_id': None,
            'amount': amount,
            'transaction_type': 'retirement',
            'credit_ids': retirable_credits[:amount],
            'retirement_data': retirement_data
        }
        
        # Record transaction
        self.transactions.append(transaction)
        entity['transactions'].append(transaction_id)
        
        # Update credit status
        for credit_id in retirable_credits[:amount]:
            credit = self.credits[credit_id]
            credit['status'] = 'retired'
            credit['retirement_data'] = retirement_data
            
            # Update project's retired credit counter
            project_id = credit['project_id']
            if project_id in self.projects:
                self.projects[project_id]['credits_retired'] += 1
        
        # Update credit balance
        entity['credit_balance'] -= amount
        
        return True, f"Successfully retired {amount} credits"
    
    def get_entity_balance(self, entity_id):
        """Get the current credit balance for an entity."""
        if entity_id not in self.entities:
            return 0
        return self.entities[entity_id]['credit_balance']
    
    def get_entity_credits(self, entity_id):
        """Get details of all credits owned by an entity."""
        if entity_id not in self.entities:
            return []
            
        entity_credits = []
        for credit_id, credit in self.credits.items():
            if credit['current_owner'] == entity_id and credit['status'] == 'active':
                credit_details = credit.copy()
                # Add project information to each credit
                if credit['project_id'] in self.projects:
                    project = self.projects[credit['project_id']]
                    credit_details['project_name'] = project['name']
                    credit_details['methodology'] = project['methodology']
                    credit_details['location'] = project['location']
                
                entity_credits.append(credit_details)
                
        return entity_credits
    
    def get_entity_transactions(self, entity_id):
        """Get all transactions involving an entity."""
        if entity_id not in self.entities:
            return []
            
        entity_transactions = []
        transaction_ids = self.entities[entity_id]['transactions']
        
        for transaction in self.transactions:
            if transaction['id'] in transaction_ids:
                entity_transactions.append(transaction)
                
        return entity_transactions
    
    def get_project_details(self, project_id):
        """Get detailed information about a project."""
        if project_id not in self.projects:
            return None
            
        project = self.projects[project_id].copy()
        
        # Add verification details
        if 'last_verification' in project and project['last_verification'] in self.verification_records:
            project['verification_details'] = self.verification_records[project['last_verification']]
            
        # Add credit issuance statistics
        project_credits = [c for c_id, c in self.credits.items() if c['project_id'] == project_id]
        
        project['credit_vintage_distribution'] = defaultdict(int)
        for credit in project_credits:
            project['credit_vintage_distribution'][credit['vintage']] += 1
            
        # Convert defaultdict to regular dict for serialization
        project['credit_vintage_distribution'] = dict(project['credit_vintage_distribution'])
        
        return project
    
    def get_market_statistics(self):
        """Get market-wide statistics for carbon credits."""
        if not self.credits:
            return {
                'total_credits_issued': 0,
                'total_credits_retired': 0,
                'total_credits_active': 0,
                'total_projects': len(self.projects),
                'total_entities': len(self.entities),
                'entity_types': {},
                'methodology_distribution': {},
                'price_history': [],
                'retirement_purposes': {}
            }
        
        # Count credit status
        total_issued = len(self.credits)
        total_retired = sum(1 for c in self.credits.values() if c['status'] == 'retired')
        total_active = total_issued - total_retired
        
        # Count entity types
        entity_types = defaultdict(int)
        for entity in self.entities.values():
            entity_types[entity['type']] += 1
            
        # Count methodology distribution
        methodology_distribution = defaultdict(int)
        for project in self.projects.values():
            methodology_distribution[project['methodology']] += project['credits_issued']
            
        # Get price history
        price_history = []
        for transaction in self.transactions:
            if transaction['transaction_type'] == 'sale' and transaction['price_per_credit'] is not None:
                price_history.append({
                    'timestamp': transaction['timestamp'],
                    'price': transaction['price_per_credit'],
                    'amount': transaction['amount']
                })
                
        # Count retirement purposes
        retirement_purposes = defaultdict(int)
        for transaction in self.transactions:
            if transaction['transaction_type'] == 'retirement' and 'retirement_data' in transaction:
                purpose = transaction['retirement_data'].get('purpose', 'unknown')
                retirement_purposes[purpose] += transaction['amount']
        
        return {
            'total_credits_issued': total_issued,
            'total_credits_retired': total_retired,
            'total_credits_active': total_active,
            'total_projects': len(self.projects),
            'total_entities': len(self.entities),
            'entity_types': dict(entity_types),
            'methodology_distribution': dict(methodology_distribution),
            'price_history': price_history,
            'retirement_purposes': dict(retirement_purposes)
        }
    
    def visualize_credit_flow(self):
        """Create a Sankey diagram of carbon credit flows between entities."""
        if not self.transactions:
            # Create an empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No Carbon Credit Transactions Available",
                annotations=[dict(
                    text="No transaction data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
            
        # Create lists for Sankey diagram
        label_dict = {}  # Map entity IDs to indices
        label_list = []  # List of entity names
        source_list = []  # Source indices for links
        target_list = []  # Target indices for links
        value_list = []   # Values for links
        link_labels = []  # Labels for links
        
        # Add entities to labels
        for entity_id, entity in self.entities.items():
            label_dict[entity_id] = len(label_list)
            label_list.append(entity['name'])
            
        # Add a node for retirements
        retirement_index = len(label_list)
        label_list.append("Retired")
        
        # Add links from transactions
        for transaction in self.transactions:
            source = label_dict.get(transaction['from_entity_id'])
            if source is None:
                continue
                
            if transaction['transaction_type'] == 'retirement':
                target = retirement_index
                link_color = 'rgba(169, 169, 169, 0.5)'  # Gray for retirement
            else:
                target = label_dict.get(transaction['to_entity_id'])
                if target is None:
                    continue
                link_color = 'rgba(44, 160, 44, 0.5)'  # Green for transfers
                
            source_list.append(source)
            target_list.append(target)
            value_list.append(transaction['amount'])
            
            # Create link label
            timestamp = datetime.fromisoformat(transaction['timestamp']).strftime('%Y-%m-%d')
            link_labels.append(f"{transaction['amount']} credits on {timestamp}")
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=label_list
            ),
            link=dict(
                source=source_list,
                target=target_list,
                value=value_list,
                label=link_labels
            )
        )])
        
        fig.update_layout(
            title_text="Carbon Credit Flow Between Entities",
            font_size=10
        )
        
        return fig
    
    def visualize_price_history(self):
        """Create a line chart of carbon credit price history."""
        # Get price history data
        price_history = []
        for transaction in self.transactions:
            if transaction['transaction_type'] == 'sale' and transaction['price_per_credit'] is not None:
                price_history.append({
                    'timestamp': datetime.fromisoformat(transaction['timestamp']),
                    'price': transaction['price_per_credit'],
                    'amount': transaction['amount']
                })
                
        if not price_history:
            # Create an empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No Carbon Credit Price History Available",
                annotations=[dict(
                    text="No price data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
            
        # Sort by timestamp
        price_history.sort(key=lambda x: x['timestamp'])
        
        # Create figure
        fig = go.Figure()
        
        # Add price trace
        fig.add_trace(go.Scatter(
            x=[p['timestamp'] for p in price_history],
            y=[p['price'] for p in price_history],
            mode='lines+markers',
            name='Credit Price',
            marker=dict(
                size=[min(20, 5 + p['amount'] / 10) for p in price_history],
                sizemode='area',
                sizeref=2.*max([p['amount'] for p in price_history])/(40.**2),
                sizemin=4
            ),
            hovertemplate='%{x}<br>Price: $%{y:.2f}<br>Volume: %{text}',
            text=[f"{p['amount']} credits" for p in price_history]
        ))
        
        # Update layout
        fig.update_layout(
            title="Carbon Credit Price History",
            xaxis_title="Date",
            yaxis_title="Price per Credit (USD)",
            hovermode="closest",
            template="plotly_white"
        )
        
        return fig
    
    def visualize_methodology_distribution(self):
        """Create a pie chart of carbon credits by methodology."""
        # Count methodology distribution
        methodology_distribution = defaultdict(int)
        for project in self.projects.values():
            methodology_distribution[project['methodology']] += project['credits_issued']
            
        if not methodology_distribution:
            # Create an empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No Carbon Credit Methodology Data Available",
                annotations=[dict(
                    text="No methodology data available",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )]
            )
            return fig
        
        # Get methodology names
        labels = []
        values = []
        
        for methodology_code, count in methodology_distribution.items():
            methodology_name = self.methodologies.get(methodology_code, {}).get('name', methodology_code)
            labels.append(methodology_name)
            values.append(count)
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            hoverinfo='label+percent+value',
            textinfo='percent',
            insidetextorientation='radial'
        )])
        
        fig.update_layout(
            title="Carbon Credits by Methodology",
            template="plotly_white"
        )
        
        return fig
    
    def export_data(self):
        """Export all registry data in serializable format."""
        return {
            'projects': self.projects,
            'credits': self.credits,
            'transactions': self.transactions,
            'entities': self.entities,
            'verification_records': self.verification_records,
            'methodologies': self.methodologies,
            'last_sync': self.last_sync.isoformat(),
            'export_timestamp': datetime.now().isoformat()
        }
    
    def import_data(self, data):
        """Import registry data from exported format."""
        if not isinstance(data, dict):
            return False, "Invalid data format"
            
        required_keys = ['projects', 'credits', 'transactions', 'entities']
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"
        
        # Import data
        self.projects = data['projects']
        self.credits = data['credits']
        self.transactions = data['transactions']
        self.entities = data['entities']
        
        if 'verification_records' in data:
            self.verification_records = data['verification_records']
        
        if 'methodologies' in data:
            self.methodologies = data['methodologies']
            
        if 'last_sync' in data:
            try:
                self.last_sync = datetime.fromisoformat(data['last_sync'])
            except (ValueError, TypeError):
                self.last_sync = datetime.now()
        
        return True, "Data imported successfully"