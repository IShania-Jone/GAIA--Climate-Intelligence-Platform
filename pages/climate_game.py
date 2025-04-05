"""
Gamified Climate Learning Experience for GAIA-∞ Climate Intelligence Platform.

This page provides interactive games and challenges to learn about climate change.
"""

import streamlit as st
import json
import random
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.gamification.climate_game import ClimateGame

# Page configuration
st.set_page_config(
    page_title="GAIA-∞ | Climate Game",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize climate game
game = ClimateGame()

# Initialize session state
if 'user_progress' not in st.session_state:
    st.session_state.user_progress = {
        "challenges_completed": 0,
        "datasets_viewed": 3,
        "total_points": 125,
        "consecutive_logins": 1,
        "footprint_calculated": False,
        "datasets_explored": 2,
        "carbon_reduction_plans": 0,
        "years_analyzed": 0,
        "simulations_compared": 0,
        "insights_shared": 0,
        "renewable_percentage": 0,
        "biodiversity_preserved": False,
        "policies_created": 0,
        "simulation_years": 0
    }
    
if 'current_challenge' not in st.session_state:
    # Get a random daily challenge
    st.session_state.current_challenge = game.get_daily_challenge()
    
if 'achievements_shown' not in st.session_state:
    st.session_state.achievements_shown = False
    
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "dashboard"

# Custom CSS
st.markdown("""
<style>
    /* Game interface styling */
    .game-header {
        background: linear-gradient(90deg, #00a3e0, #004b85);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .game-header h1 {
        margin: 0;
        padding: 0;
        font-size: 2.5rem;
    }
    
    .game-header p {
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    .challenge-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #00a3e0;
    }
    
    .daily-challenge {
        border-left: 5px solid #FFD700;
        background-color: #FFFAED;
    }
    
    .achievement {
        display: flex;
        align-items: center;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    
    .achievement:hover {
        transform: translateY(-3px);
    }
    
    .achievement-icon {
        font-size: 2rem;
        margin-right: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
    }
    
    .achievement-content {
        flex: 1;
    }
    
    .achievement-title {
        font-weight: bold;
        margin: 0;
        color: #333;
    }
    
    .achievement-description {
        color: #666;
        margin: 5px 0 0 0;
    }
    
    .achievement-points {
        background-color: #00a3e0;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    
    .achievement-secret {
        background-color: #FF6B6B;
    }
    
    .progress-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    
    .progress-bar-container {
        height: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #00a3e0, #004b85);
        border-radius: 5px;
    }
    
    .tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }
    
    .tab {
        padding: 10px 20px;
        margin: 0 10px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
        background-color: #f0f0f0;
    }
    
    .tab.active {
        background-color: #00a3e0;
        color: white;
    }
    
    /* Level badge */
    .level-badge {
        display: inline-block;
        padding: 10px 15px;
        border-radius: 20px;
        background: linear-gradient(90deg, #00a3e0, #004b85);
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-right: 15px;
    }
    
    /* Points display */
    .points-display {
        display: inline-block;
        padding: 10px 15px;
        border-radius: 20px;
        background-color: #f0f0f0;
        color: #333;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Game header
st.markdown("""
<div class="game-header">
    <h1>GAIA-∞ Climate Challenge</h1>
    <p>Learn about climate change through engaging challenges and earn achievements</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tabs = ["Dashboard", "Challenges", "Achievements", "Leaderboard"]
col_tabs = st.columns(len(tabs))

for i, tab in enumerate(tabs):
    if col_tabs[i].button(
        tab, 
        key=f"tab_{tab.lower()}", 
        use_container_width=True,
        type="primary" if st.session_state.current_tab == tab.lower() else "secondary"
    ):
        st.session_state.current_tab = tab.lower()
        st.rerun()

# Get progress data
progress_data = game.get_progress_bar_data(st.session_state.user_progress)

if st.session_state.current_tab == "dashboard":
    # User progress overview
    st.markdown("### Your Climate Action Progress")
    
    # Display level and points
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">CURRENT LEVEL</div>
            <div style="font-size: 3rem; font-weight: bold; color: #00a3e0;">{progress_data["level"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Progress to next level
        st.markdown("**Progress to Next Level**")
        
        st.markdown(f"""
        <div class="progress-label">
            <span>{progress_data["points"]} points</span>
            <span>{progress_data["next_level_points"] if progress_data["next_level_points"] else "MAX"} points</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {progress_data["level_progress"] * 100}%;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"Complete challenges to earn points and level up!")
    
    # Daily challenge
    st.markdown("### 🔆 Daily Challenge")
    
    daily_challenge = st.session_state.current_challenge
    
    st.markdown(f"""
    <div class="challenge-card daily-challenge">
        <h3>{daily_challenge["title"]}</h3>
        <p>{daily_challenge["description"]}</p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
            <div>
                <span style="background-color: #FFD700; color: #000; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">+{daily_challenge["points"]} POINTS</span>
                <span style="background-color: #f0f0f0; color: #333; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; margin-left: 5px;">{daily_challenge["difficulty"].upper()}</span>
            </div>
            <div>Expires in 24 hours</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Complete challenge button
    if st.button("Complete Daily Challenge"):
        # Simulate challenge completion
        st.session_state.user_progress["challenges_completed"] += 1
        st.session_state.user_progress["total_points"] += daily_challenge["points"]
        
        # Update the specific progress metric based on challenge
        if "datasets_explored" in daily_challenge["completion_criteria"]:
            st.session_state.user_progress["datasets_explored"] += 1
            
        # Get a new challenge for tomorrow
        st.session_state.current_challenge = game.get_daily_challenge()
        
        st.success(f"Challenge completed! You earned {daily_challenge['points']} points.")
        st.rerun()
    
    # Stats overview
    st.markdown("### Your Climate Action Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="progress-card">
            <h4>Challenges Completed</h4>
            <div style="font-size: 2.5rem; font-weight: bold; color: #00a3e0; text-align: center; margin: 15px 0;">
                {}
            </div>
        </div>
        """.format(st.session_state.user_progress["challenges_completed"]), unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="progress-card">
            <h4>Climate Datasets Explored</h4>
            <div style="font-size: 2.5rem; font-weight: bold; color: #00a3e0; text-align: center; margin: 15px 0;">
                {}
            </div>
        </div>
        """.format(st.session_state.user_progress["datasets_explored"]), unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="progress-card">
            <h4>Consecutive Days Active</h4>
            <div style="font-size: 2.5rem; font-weight: bold; color: #00a3e0; text-align: center; margin: 15px 0;">
                {}
            </div>
        </div>
        """.format(st.session_state.user_progress["consecutive_logins"]), unsafe_allow_html=True)
        
    # Recent achievements
    st.markdown("### Recent Achievements")
    
    earned_achievements = game.get_user_achievements(st.session_state.user_progress)
    
    if not earned_achievements:
        st.info("Complete challenges to earn achievements!")
    else:
        # Show the most recent 3 achievements
        for achievement in earned_achievements[:3]:
            st.markdown(f"""
            <div class="achievement">
                <div class="achievement-icon">{achievement["icon"]}</div>
                <div class="achievement-content">
                    <h4 class="achievement-title">{achievement["title"]}</h4>
                    <p class="achievement-description">{achievement["description"]}</p>
                </div>
                <div class="achievement-points">+{achievement["points"]} PTS</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"**View all {len(earned_achievements)} achievements in the Achievements tab**")

elif st.session_state.current_tab == "challenges":
    st.markdown("### Climate Challenges")
    
    # Challenge filtering
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All Categories", "exploration", "simulation", "personal_action", "analysis", "social"]
        )
    with col2:
        difficulty_filter = st.selectbox(
            "Filter by Difficulty",
            ["All Difficulties", "beginner", "intermediate", "advanced"]
        )
        
    # Get challenges based on filters
    category = None if category_filter == "All Categories" else category_filter
    difficulty = None if difficulty_filter == "All Difficulties" else difficulty_filter
    
    challenges = game.get_available_challenges(
        user_profile=st.session_state.user_progress,
        category=category,
        difficulty=difficulty,
        limit=10
    )
    
    # Display challenges
    for challenge in challenges:
        # Check if challenge is completed
        is_completed = game.check_challenge_completion(challenge["id"], st.session_state.user_progress)
        
        st.markdown(f"""
        <div class="challenge-card" style="opacity: {'0.7' if is_completed else '1'}; border-left-color: {'#4CAF50' if is_completed else '#00a3e0'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{challenge["title"]} {"✓" if is_completed else ""}</h3>
                <div>
                    <span style="background-color: #00a3e0; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">+{challenge["points"]} POINTS</span>
                    <span style="background-color: #f0f0f0; color: #333; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; margin-left: 5px;">{challenge["difficulty"].upper()}</span>
                </div>
            </div>
            <p>{challenge["description"]}</p>
            <div style="margin-top: 15px;">
                <button style="background-color: {'#4CAF50' if is_completed else '#00a3e0'}; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer;">
                    {"Completed" if is_completed else "Start Challenge"}
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Complete challenge simulation (for demo purposes)
    if st.button("Simulate Challenge Completion"):
        # Choose a random incomplete challenge
        incomplete_challenges = [c for c in challenges if not game.check_challenge_completion(c["id"], st.session_state.user_progress)]
        
        if incomplete_challenges:
            challenge = random.choice(incomplete_challenges)
            
            # Update progress based on challenge type
            for key, value in challenge["completion_criteria"].items():
                if key in st.session_state.user_progress:
                    st.session_state.user_progress[key] = value
            
            # Update general progress
            st.session_state.user_progress["challenges_completed"] += 1
            st.session_state.user_progress["total_points"] += challenge["points"]
            
            st.success(f"Challenge '{challenge['title']}' completed! You earned {challenge['points']} points.")
            st.rerun()
        else:
            st.warning("All displayed challenges are already completed. Try changing the filters.")

elif st.session_state.current_tab == "achievements":
    st.markdown("### Your Achievements")
    
    # Get all achievements and user's earned achievements
    all_achievements = game.achievements
    earned_achievements = game.get_user_achievements(st.session_state.user_progress)
    
    # Calculate total achievements and earned percentage
    total_visible = len([a for a in all_achievements if not a["secret"]])
    earned_visible = len([a for a in earned_achievements if not a["secret"]])
    earned_percentage = earned_visible / total_visible * 100 if total_visible > 0 else 0
    
    # Display progress
    st.markdown(f"""
    <div class="progress-card">
        <h4>Achievement Progress</h4>
        <div class="progress-label">
            <span>{earned_visible} of {total_visible} unlocked</span>
            <span>{earned_percentage:.1f}%</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {earned_percentage}%;"></div>
        </div>
        <p style="margin-top: 10px; color: #666;">Plus {len([a for a in earned_achievements if a["secret"]])} secret achievements discovered!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display earned achievements
    st.markdown("#### Earned Achievements")
    
    if not earned_achievements:
        st.info("Complete challenges to earn achievements!")
    else:
        for achievement in earned_achievements:
            st.markdown(f"""
            <div class="achievement">
                <div class="achievement-icon">{achievement["icon"]}</div>
                <div class="achievement-content">
                    <h4 class="achievement-title">{achievement["title"]}</h4>
                    <p class="achievement-description">{achievement["description"]}</p>
                </div>
                <div class="achievement-points {'achievement-secret' if achievement['secret'] else ''}">+{achievement["points"]} PTS</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Display locked non-secret achievements
    st.markdown("#### Locked Achievements")
    
    locked_achievements = [a for a in all_achievements if not a["secret"] and a["id"] not in [ea["id"] for ea in earned_achievements]]
    
    if not locked_achievements:
        st.success("You've unlocked all regular achievements! There may still be secret ones to discover...")
    else:
        for achievement in locked_achievements:
            st.markdown(f"""
            <div class="achievement" style="opacity: 0.6;">
                <div class="achievement-icon" style="filter: grayscale(100%);">{achievement["icon"]}</div>
                <div class="achievement-content">
                    <h4 class="achievement-title">{achievement["title"]}</h4>
                    <p class="achievement-description">{achievement["description"]}</p>
                </div>
                <div class="achievement-points">+{achievement["points"]} PTS</div>
            </div>
            """, unsafe_allow_html=True)
            
    # Secret achievements hint
    st.markdown("#### Secret Achievements")
    st.markdown("There are several secret achievements to discover. Keep exploring the platform and taking climate action to find them!")

elif st.session_state.current_tab == "leaderboard":
    st.markdown("### Global Climate Action Leaderboard")
    
    # Simulated leaderboard data (in production, would be from database)
    leaderboard_data = [
        {"rank": 1, "username": "EcoChampion", "level": 8, "points": 8250, "challenges": 42, "joined": "2023-05-12"},
        {"rank": 2, "username": "ClimateHero99", "level": 7, "points": 7120, "challenges": 36, "joined": "2023-06-03"},
        {"rank": 3, "username": "EarthGuardian", "level": 7, "points": 6580, "challenges": 33, "joined": "2023-04-18"},
        {"rank": 4, "username": "GreenTech", "level": 6, "points": 5920, "challenges": 31, "joined": "2023-07-22"},
        {"rank": 5, "username": "OceanDefender", "level": 6, "points": 5750, "challenges": 29, "joined": "2023-08-05"},
        {"rank": 6, "username": "RenewableWizard", "level": 5, "points": 4980, "challenges": 26, "joined": "2023-09-14"},
        {"rank": 7, "username": "FutureSaver", "level": 5, "points": 4620, "challenges": 24, "joined": "2023-10-30"},
        {"rank": 8, "username": "BioDiversity", "level": 4, "points": 3840, "challenges": 20, "joined": "2024-01-07"},
        {"rank": 9, "username": "CarbonCutter", "level": 4, "points": 3510, "challenges": 18, "joined": "2024-02-12"},
        {"rank": 10, "username": "SolarPowered", "level": 3, "points": 2780, "challenges": 15, "joined": "2024-03-03"},
    ]
    
    # Add current user
    current_user_rank = random.randint(11, 50)
    current_user = {
        "rank": current_user_rank, 
        "username": "You", 
        "level": progress_data["level"], 
        "points": progress_data["points"], 
        "challenges": st.session_state.user_progress["challenges_completed"], 
        "joined": "2024-04-01"
    }
    
    # Display leaderboard
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 2px solid #ddd;">
                    <th style="padding: 8px; text-align: center;">Rank</th>
                    <th style="padding: 8px; text-align: left;">Username</th>
                    <th style="padding: 8px; text-align: center;">Level</th>
                    <th style="padding: 8px; text-align: right;">Points</th>
                    <th style="padding: 8px; text-align: right;">Challenges</th>
                    <th style="padding: 8px; text-align: right;">Joined</th>
                </tr>
            </thead>
            <tbody>
    """, unsafe_allow_html=True)
    
    for user in leaderboard_data:
        st.markdown(f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 12px; text-align: center; font-weight: bold;">{user["rank"]}</td>
            <td style="padding: 12px; text-align: left;">{user["username"]}</td>
            <td style="padding: 12px; text-align: center; background-color: rgba(0, 163, 224, 0.1); border-radius: 5px;">{user["level"]}</td>
            <td style="padding: 12px; text-align: right; font-weight: bold;">{user["points"]}</td>
            <td style="padding: 12px; text-align: right;">{user["challenges"]}</td>
            <td style="padding: 12px; text-align: right; color: #666;">{user["joined"]}</td>
        </tr>
        """, unsafe_allow_html=True)
    
    # Add separator and current user
    st.markdown("""
        <tr style="border-bottom: 1px solid #ddd; height: 20px; background-color: rgba(0, 0, 0, 0.03);">
            <td colspan="6" style="text-align: center; color: #666;">...</td>
        </tr>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <tr style="border-bottom: 1px solid #ddd; background-color: rgba(0, 163, 224, 0.05);">
            <td style="padding: 12px; text-align: center; font-weight: bold;">{current_user["rank"]}</td>
            <td style="padding: 12px; text-align: left; font-weight: bold;">{current_user["username"]}</td>
            <td style="padding: 12px; text-align: center; background-color: rgba(0, 163, 224, 0.2); border-radius: 5px; font-weight: bold;">{current_user["level"]}</td>
            <td style="padding: 12px; text-align: right; font-weight: bold;">{current_user["points"]}</td>
            <td style="padding: 12px; text-align: right;">{current_user["challenges"]}</td>
            <td style="padding: 12px; text-align: right; color: #666;">{current_user["joined"]}</td>
        </tr>
    """, unsafe_allow_html=True)
    
    st.markdown("""
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Leaderboard charts
    st.markdown("### Leaderboard Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create points distribution chart
        points_data = [user["points"] for user in leaderboard_data + [current_user]]
        user_labels = [user["username"] for user in leaderboard_data + [current_user]]
        
        fig = px.bar(
            x=user_labels, 
            y=points_data,
            labels={"x": "User", "y": "Points"},
            title="Top Users by Points",
            color=points_data,
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Create level distribution chart
        level_counts = {}
        for user in leaderboard_data + [current_user]:
            level = user["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
            
        levels = list(level_counts.keys())
        counts = list(level_counts.values())
        
        fig = px.pie(
            values=counts,
            names=levels,
            title="Leaderboard Level Distribution",
            color=levels,
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Info about the gamification system
with st.expander("About Climate Game"):
    st.markdown("""
    ### How the Climate Game Works
    
    The GAIA-∞ Climate Game is designed to make learning about climate change engaging and interactive. 
    The game has several components:
    
    **Challenges**: Complete tasks related to climate science, data exploration, and climate action. Each challenge 
    awards points based on difficulty.
    
    **Achievements**: Unlock badges and rewards for reaching milestones and accomplishing specific goals.
    
    **Levels**: Progress through levels as you earn points, unlocking new content and features.
    
    **Leaderboard**: Compare your progress with other users around the world.
    
    **Daily Challenges**: New challenges are provided each day to encourage regular engagement.
    
    All game activities are designed to increase your understanding of climate science, encourage data literacy,
    and promote real-world climate action.
    """)
    
    # Demo notice
    st.info("This is a demonstration version of the Climate Game. In the production version, challenges would connect to real platform activities and actions.")
    
    # Simulation options for demo
    st.markdown("### Simulation Controls (Demo Only)")
    
    if st.button("Level Up (Demo)"):
        st.session_state.user_progress["total_points"] += 200
        st.success("You gained 200 points and leveled up!")
        st.rerun()
        
    if st.button("Unlock Random Achievement (Demo)"):
        # Find an unearned, non-secret achievement
        unlocked_ids = [a["id"] for a in game.get_user_achievements(st.session_state.user_progress)]
        locked = [a for a in game.achievements if a["id"] not in unlocked_ids and not a["secret"]]
        
        if locked:
            achievement = random.choice(locked)
            for key, value in achievement["criteria"].items():
                st.session_state.user_progress[key] = value
                
            # Update points
            st.session_state.user_progress["total_points"] += achievement["points"]
            
            st.success(f"You unlocked the '{achievement['title']}' achievement!")
            st.rerun()
        else:
            st.warning("All standard achievements are already unlocked!")