"""
AI-powered climate storytelling module for GAIA-∞.

This module uses advanced AI to generate compelling narratives about climate 
change based on real data, helping users understand complex climate issues 
through engaging, personalized stories.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateStoryteller:
    """
    AI-powered climate storytelling engine.
    Generates compelling narratives about climate change based on real data.
    """
    
    def __init__(self, anthropic_api_key=None):
        """
        Initialize the climate storyteller with API keys.
        
        Args:
            anthropic_api_key: API key for Anthropic's Claude API
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.story_templates = self._load_story_templates()
        
    def _load_story_templates(self):
        """Load story templates from disk or use default templates."""
        # Default templates in case file doesn't exist
        default_templates = {
            "personal_impact": {
                "title": "Climate Change and You: A Personal Story",
                "themes": ["local_impacts", "personal_choices", "future_generations"],
                "prompt_template": "Tell a personal story about how climate change impacts {region} and how individual choices can make a difference."
            },
            "global_perspective": {
                "title": "Our Changing Planet: A Global View",
                "themes": ["global_systems", "interconnectedness", "tipping_points"],
                "prompt_template": "Create a narrative that explains how {climate_event} in {region} connects to global climate systems and affects other parts of the world."
            },
            "future_scenarios": {
                "title": "Tomorrow's Earth: Pathways to the Future",
                "themes": ["future_projections", "adaptation", "innovation"],
                "prompt_template": "Craft a story set in {year} that explores how {region} has adapted to climate change through {adaptation_strategy}."
            },
        }
        
        try:
            # TODO: In a production environment, load from a database or file
            return default_templates
        except Exception as e:
            logger.warning(f"Could not load story templates: {str(e)}. Using defaults.")
            return default_templates
            
    def generate_story(self, template_key, parameters=None, max_tokens=1000):
        """
        Generate a climate story based on selected template and parameters.
        
        Args:
            template_key: Key for the story template to use
            parameters: Dictionary of parameters to fill in the template
            max_tokens: Maximum length of the story
            
        Returns:
            Dictionary containing the generated story and metadata
        """
        parameters = parameters or {}
        
        # Get the template
        if template_key not in self.story_templates:
            logger.error(f"Story template '{template_key}' not found")
            return {"error": f"Story template '{template_key}' not found"}
            
        template = self.story_templates[template_key]
        
        # If we have Anthropic API access, use it to generate the story
        if self.anthropic_api_key:
            try:
                # Import here to avoid dependency issues if not installed
                import anthropic
                from anthropic import Anthropic
                
                client = Anthropic(
                    api_key=self.anthropic_api_key,
                )
                
                # Fill in the prompt template with parameters
                prompt = template["prompt_template"]
                for key, value in parameters.items():
                    prompt = prompt.replace(f"{{{key}}}", str(value))
                
                # The newest Anthropic model is "claude-3-5-sonnet-20241022", not "claude-3-sonnet-20240229". 
                # claude-3-5-sonnet-20241022 was released after your knowledge cutoff.
                # Always prefer using claude-3-5-sonnet-20241022 as it is the latest model.
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    messages=[
                        {
                            "role": "user", 
                            "content": f"You are an expert climate science communicator. {prompt} Make the story vivid, emotional, and scientifically accurate. Include specific details about climate impacts and solutions. Format the response as an engaging narrative with a clear beginning, middle, and end."
                        }
                    ]
                )
                
                story_text = response.content[0].text
                
            except Exception as e:
                logger.error(f"Error generating story with Anthropic API: {str(e)}")
                story_text = self._generate_fallback_story(template, parameters)
        else:
            # If no API key, generate a prompt that would be used
            prompt_text = template["prompt_template"]
            for key, value in parameters.items():
                prompt_text = prompt_text.replace(f"{{{key}}}", str(value))
                
            return {
                "title": template["title"],
                "status": "API key required",
                "prompt": prompt_text,
                "message": "To generate AI-powered climate stories, please provide an Anthropic API key in the settings.",
                "themes": template["themes"]
            }
            
        # Return the story and metadata
        return {
            "title": template["title"],
            "content": story_text,
            "themes": template["themes"],
            "created_at": datetime.now().isoformat(),
            "parameters": parameters
        }
        
    def _generate_fallback_story(self, template, parameters):
        """Generate a simple fallback story when API is unavailable."""
        # This should not be used in production, only when API fails unexpectedly
        title = template["title"]
        prompt = template["prompt_template"]
        for key, value in parameters.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
            
        return f"[Story based on: {prompt}]\n\nPlease enable the AI storytelling feature by providing an API key in settings."
        
    def get_available_templates(self):
        """Get list of available story templates."""
        return {
            key: {
                "title": template["title"],
                "themes": template["themes"],
                "required_parameters": self._extract_template_parameters(template["prompt_template"])
            }
            for key, template in self.story_templates.items()
        }
        
    def _extract_template_parameters(self, prompt_template):
        """Extract required parameters from a prompt template."""
        import re
        # Find all {parameter} patterns in the template
        parameters = re.findall(r'\{([^{}]+)\}', prompt_template)
        return parameters
        
    def get_region_suggestions(self, query=None):
        """Get suggested regions for storytelling."""
        # Basic suggestions - in production this would use a more sophisticated system
        regions = [
            "Arctic", "Amazon Rainforest", "Pacific Islands", "Coastal Cities", 
            "The Sahel", "Great Barrier Reef", "The Alps", "California", 
            "Bangladesh", "Mediterranean Region", "Tokyo", "London", "New York", 
            "Shanghai", "Sydney", "Cape Town", "Jakarta", "Venice"
        ]
        
        if query:
            # Filter regions that match the query
            filtered = [r for r in regions if query.lower() in r.lower()]
            return filtered[:5]  # Return top 5 matches
        
        return regions