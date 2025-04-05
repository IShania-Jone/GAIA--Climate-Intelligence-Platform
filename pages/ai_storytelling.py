"""
AI Storytelling Page for GAIA-∞ Climate Intelligence Platform.

This page allows users to generate engaging climate stories using AI.
"""

import streamlit as st
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta

from utils.ai_storytelling.storyteller import ClimateStoryteller

# Page configuration
st.set_page_config(
    page_title="GAIA-∞ | AI Climate Storytelling",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storytelling
if 'stories' not in st.session_state:
    st.session_state.stories = []
    
if 'template_parameters' not in st.session_state:
    st.session_state.template_parameters = {}
    
if 'regions' not in st.session_state:
    st.session_state.regions = []

# Initialize the storyteller
storyteller = ClimateStoryteller()

# Check if Anthropic API key is available
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
api_available = anthropic_api_key is not None

# Page header with custom styling
st.markdown("""
<style>
    .storytelling-header {
        text-align: center;
        padding: 20px 0;
        border-radius: 10px;
        margin-bottom: 20px;
        background: linear-gradient(90deg, rgba(0,163,224,0.2) 0%, rgba(0,75,133,0.2) 100%);
    }
    
    .storytelling-header h1 {
        color: #00a3e0;
        margin-bottom: 5px;
    }
    
    .storytelling-header p {
        color: #555;
        font-size: 1.1rem;
    }
    
    .story-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
        border-left: 4px solid #00a3e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .story-title {
        color: #00a3e0;
        margin-bottom: 10px;
    }
    
    .story-meta {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    
    .story-content {
        line-height: 1.6;
        margin-bottom: 15px;
    }
    
    .story-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 10px;
    }
    
    .story-tag {
        background-color: rgba(0,163,224,0.1);
        color: #00a3e0;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    
    .api-warning {
        padding: 15px;
        border-radius: 5px;
        background-color: rgba(255,193,7,0.1);
        border-left: 4px solid #ffc107;
        margin-bottom: 20px;
    }
    
    .story-generator {
        padding: 25px;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 30px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="storytelling-header">
    <h1>AI Climate Storytelling</h1>
    <p>Generate compelling narratives about climate change using advanced AI</p>
</div>
""", unsafe_allow_html=True)

# Check if API key is available
if not api_available:
    st.markdown("""
    <div class="api-warning">
        <h3>⚠️ API Key Required</h3>
        <p>To generate AI-powered climate stories, please provide an Anthropic API key in the Settings page.</p>
        <p>Without an API key, you can still see the story templates but won't be able to generate new content.</p>
    </div>
    """, unsafe_allow_html=True)

# Main content layout
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("### Generate a Climate Story")
    st.markdown("Use our AI storyteller to generate engaging narratives about climate change impacts and solutions.")
    
    # Get available templates
    templates = storyteller.get_available_templates()
    
    # Story template selection
    template_options = {}
    for key, template in templates.items():
        template_options[template["title"]] = key
        
    selected_template_title = st.selectbox(
        "Select a story template", 
        list(template_options.keys())
    )
    
    selected_template_key = template_options[selected_template_title]
    selected_template = templates[selected_template_key]
    
    # Display template information
    st.markdown(f"**Required parameters:** {', '.join(selected_template['required_parameters'])}")
    st.markdown(f"**Themes:** {', '.join(selected_template['themes'])}")
    
    # Initialize parameters for the selected template
    parameters = {}
    
    # Input fields for required parameters
    for param in selected_template["required_parameters"]:
        # Special handling for common parameters
        if param == "region":
            regions = storyteller.get_region_suggestions()
            parameters[param] = st.selectbox(f"Select {param}", regions)
        elif param == "year":
            current_year = datetime.now().year
            parameters[param] = st.slider(f"Select {param}", current_year, current_year + 100, current_year + 30)
        elif param == "climate_event":
            event_options = ["drought", "flood", "wildfire", "hurricane", "heat wave", "sea level rise"]
            parameters[param] = st.selectbox(f"Select {param}", event_options)
        elif param == "adaptation_strategy":
            strategy_options = ["urban design", "sustainable agriculture", "renewable energy", "coastal protection", "water conservation"]
            parameters[param] = st.selectbox(f"Select {param}", strategy_options)
        else:
            parameters[param] = st.text_input(f"Enter {param}")
    
    # Story length
    max_tokens = st.slider("Story length", 500, 2000, 1000, 100)
    
    # Generate button
    generate_button = st.button("Generate Story", disabled=not api_available)
    
    if generate_button:
        with st.spinner("Generating your climate story with AI..."):
            story = storyteller.generate_story(
                selected_template_key,
                parameters,
                max_tokens=max_tokens
            )
            
            if "error" in story:
                st.error(f"Error generating story: {story['error']}")
            elif "status" in story and story["status"] == "API key required":
                st.warning(story["message"])
            else:
                # Add to session state
                st.session_state.stories.append(story)
                # Display success message
                st.success("Story generated successfully!")

with col2:
    st.markdown("### Your Climate Stories")
    
    if not st.session_state.stories:
        if api_available:
            st.info("Generate your first climate story using the form on the left.")
        else:
            # Example story to demonstrate the format
            example_story = {
                "title": "Tomorrow's Earth: Pathways to the Future",
                "content": "In 2050, coastal cities around the world have adapted to rising sea levels through innovative floating architecture and natural barrier restoration. This story would explore how these adaptations have changed urban life and created new opportunities for sustainable living.",
                "themes": ["future_projections", "adaptation", "innovation"],
                "created_at": datetime.now().isoformat(),
                "parameters": {"year": 2050, "region": "Coastal Cities", "adaptation_strategy": "floating architecture"}
            }
            
            st.markdown("""
            <div class="story-card">
                <h3 class="story-title">{}</h3>
                <p class="story-meta">Example Story Format</p>
                <div class="story-content">{}</div>
                <div class="story-tags">
                    {}
                </div>
            </div>
            """.format(
                example_story["title"],
                example_story["content"],
                "".join([f'<span class="story-tag">{theme}</span>' for theme in example_story["themes"]])
            ), unsafe_allow_html=True)
            
            st.markdown("*This is an example of how stories will appear once generated with a valid API key.*")
    else:
        # Display generated stories
        for story in reversed(st.session_state.stories):
            st.markdown("""
            <div class="story-card">
                <h3 class="story-title">{}</h3>
                <p class="story-meta">Generated on {} • Based on parameters: {}</p>
                <div class="story-content">{}</div>
                <div class="story-tags">
                    {}
                </div>
            </div>
            """.format(
                story["title"],
                datetime.fromisoformat(story["created_at"]).strftime("%Y-%m-%d %H:%M"),
                ", ".join([f"{k}={v}" for k, v in story["parameters"].items()]),
                story["content"].replace("\n", "<br>"),
                "".join([f'<span class="story-tag">{theme}</span>' for theme in story["themes"]])
            ), unsafe_allow_html=True)

# Information about the AI storytelling feature
st.markdown("### About AI Climate Storytelling")

st.markdown("""
Climate change data can often feel abstract and disconnected from our everyday lives. 
The AI Climate Storytelling feature transforms complex climate science into engaging 
personal narratives that help us understand the human impact of climate change.

This feature uses the Claude-3.5-Sonnet AI model to generate scientifically accurate 
climate stories based on real data and projections. These stories can help:

- Make climate impacts more relatable and tangible
- Explore possible future scenarios based on different climate trajectories
- Connect global climate patterns to local experiences
- Inspire action through emotional, personal storytelling

All stories are generated based on the latest climate science and data from the GAIA-∞ platform.
""")

# Technical details in an expandable section
with st.expander("Technical Details"):
    st.markdown("""
    The AI Storytelling module uses Anthropic's Claude API to generate narratives based on carefully crafted prompts
    that combine climate science data with storytelling frameworks. 
    
    The system:
    
    1. Maintains a database of story templates for different climate scenarios
    2. Incorporates real climate data from the GAIA-∞ database
    3. Uses prompt engineering to ensure scientifically accurate content
    4. Provides customization options for different regions, timeframes, and scenarios
    
    The generated stories maintain scientific integrity while making climate concepts more accessible through narrative.
    """)
    
    # Display Claude API status
    st.markdown(f"**Claude API Status:** {'Connected' if api_available else 'Not Connected'}")
    st.markdown(f"**Available Templates:** {len(templates)}")
    st.markdown(f"**Stories Generated:** {len(st.session_state.stories)}")