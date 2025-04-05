"""
Gamified learning experience for climate change education in GAIA-∞.

This module provides game mechanics, challenges, and rewards to make
learning about climate change engaging and interactive.
"""

import random
import logging
import json
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClimateGame:
    """
    Gamified learning experience for climate change education.
    """
    
    def __init__(self):
        """Initialize the climate game system."""
        self.challenges = self._load_challenges()
        self.achievements = self._load_achievements()
        
    def _load_challenges(self):
        """Load challenges from data source."""
        # Default challenges
        default_challenges = [
            {
                "id": "ch_001",
                "title": "Climate Explorer",
                "description": "Explore 5 different climate datasets on the Earth Twin map",
                "difficulty": "beginner",
                "points": 50,
                "category": "exploration",
                "completion_criteria": {"datasets_explored": 5}
            },
            {
                "id": "ch_002",
                "title": "Policy Architect",
                "description": "Design a climate policy that reduces emissions by 30% in your simulation",
                "difficulty": "intermediate",
                "points": 100,
                "category": "simulation",
                "completion_criteria": {"emissions_reduction": 30}
            },
            {
                "id": "ch_003",
                "title": "Carbon Detective",
                "description": "Calculate your carbon footprint and identify 3 ways to reduce it",
                "difficulty": "beginner",
                "points": 75,
                "category": "personal_action",
                "completion_criteria": {"carbon_reduction_plans": 3}
            },
            {
                "id": "ch_004",
                "title": "Climate Historian",
                "description": "Analyze 100 years of temperature data and identify key patterns",
                "difficulty": "intermediate",
                "points": 125,
                "category": "analysis",
                "completion_criteria": {"years_analyzed": 100}
            },
            {
                "id": "ch_005",
                "title": "Future Forecaster",
                "description": "Run 3 different climate simulations and compare their outcomes",
                "difficulty": "advanced",
                "points": 150,
                "category": "simulation",
                "completion_criteria": {"simulations_compared": 3}
            },
            {
                "id": "ch_006",
                "title": "Ecosystem Guardian",
                "description": "Create a policy that preserves biodiversity in your simulation",
                "difficulty": "advanced",
                "points": 200,
                "category": "simulation",
                "completion_criteria": {"biodiversity_preserved": True}
            },
            {
                "id": "ch_007",
                "title": "Climate Communicator",
                "description": "Share 3 climate insights with the community",
                "difficulty": "intermediate",
                "points": 100,
                "category": "social",
                "completion_criteria": {"insights_shared": 3}
            },
            {
                "id": "ch_008",
                "title": "Energy Innovator",
                "description": "Achieve 80% renewable energy in your simulation scenario",
                "difficulty": "advanced",
                "points": 175,
                "category": "simulation",
                "completion_criteria": {"renewable_percentage": 80}
            }
        ]
        
        try:
            # TODO: In production, load from database
            return default_challenges
        except Exception as e:
            logger.warning(f"Could not load challenges: {str(e)}. Using defaults.")
            return default_challenges
            
    def _load_achievements(self):
        """Load achievements from data source."""
        # Default achievements
        default_achievements = [
            {
                "id": "ach_001",
                "title": "Climate Novice",
                "description": "Complete your first challenge",
                "icon": "🌱",
                "points": 25,
                "secret": False,
                "criteria": {"challenges_completed": 1}
            },
            {
                "id": "ach_002",
                "title": "Carbon Conscious",
                "description": "Calculate your carbon footprint",
                "icon": "👣",
                "points": 50,
                "secret": False,
                "criteria": {"footprint_calculated": True}
            },
            {
                "id": "ach_003",
                "title": "Data Explorer",
                "description": "View 10 different climate datasets",
                "icon": "🔍",
                "points": 75,
                "secret": False,
                "criteria": {"datasets_viewed": 10}
            },
            {
                "id": "ach_004",
                "title": "Policy Maker",
                "description": "Create 5 different climate policies in simulations",
                "icon": "📜",
                "points": 100,
                "secret": False,
                "criteria": {"policies_created": 5}
            },
            {
                "id": "ach_005",
                "title": "Climate Master",
                "description": "Earn 1000 points through completed challenges",
                "icon": "🏆",
                "points": 250,
                "secret": False,
                "criteria": {"total_points": 1000}
            },
            {
                "id": "ach_006",
                "title": "Time Traveler",
                "description": "Run a simulation that projects 100+ years into the future",
                "icon": "⏳",
                "points": 125,
                "secret": True,
                "criteria": {"simulation_years": 100}
            },
            {
                "id": "ach_007",
                "title": "Earth Guardian",
                "description": "Login for 30 consecutive days",
                "icon": "🛡️",
                "points": 150,
                "secret": True,
                "criteria": {"consecutive_logins": 30}
            }
        ]
        
        try:
            # TODO: In production, load from database
            return default_achievements
        except Exception as e:
            logger.warning(f"Could not load achievements: {str(e)}. Using defaults.")
            return default_achievements
    
    def get_available_challenges(self, user_profile=None, category=None, difficulty=None, limit=5):
        """
        Get available challenges for a user.
        
        Args:
            user_profile: User profile dictionary
            category: Optional category to filter by
            difficulty: Optional difficulty level to filter by
            limit: Maximum number of challenges to return
            
        Returns:
            List of challenge dictionaries
        """
        # Apply filters
        filtered_challenges = self.challenges
        
        if category:
            filtered_challenges = [c for c in filtered_challenges if c['category'] == category]
            
        if difficulty:
            filtered_challenges = [c for c in filtered_challenges if c['difficulty'] == difficulty]
        
        # Sort by difficulty (beginners get easier challenges first)
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        sorted_challenges = sorted(filtered_challenges, key=lambda c: difficulty_order.get(c['difficulty'], 99))
        
        # Return the specified number of challenges
        return sorted_challenges[:limit]
    
    def check_challenge_completion(self, challenge_id, user_progress):
        """
        Check if a user has completed a specific challenge.
        
        Args:
            challenge_id: ID of the challenge to check
            user_progress: Dictionary containing user's progress
            
        Returns:
            Boolean indicating whether the challenge is completed
        """
        # Find the challenge
        challenge = next((c for c in self.challenges if c['id'] == challenge_id), None)
        if not challenge:
            logger.warning(f"Challenge ID {challenge_id} not found")
            return False
            
        # Check completion criteria
        criteria = challenge['completion_criteria']
        for key, required_value in criteria.items():
            if key not in user_progress:
                return False
            
            user_value = user_progress[key]
            
            # Different comparison based on type
            if isinstance(required_value, bool):
                if not user_value:
                    return False
            elif isinstance(required_value, (int, float)):
                if user_value < required_value:
                    return False
            else:
                if user_value != required_value:
                    return False
                    
        return True
    
    def get_user_achievements(self, user_progress):
        """
        Get achievements that a user has earned.
        
        Args:
            user_progress: Dictionary containing user's progress
            
        Returns:
            List of earned achievement dictionaries
        """
        earned_achievements = []
        
        for achievement in self.achievements:
            criteria = achievement['criteria']
            criteria_met = True
            
            for key, required_value in criteria.items():
                if key not in user_progress:
                    criteria_met = False
                    break
                
                user_value = user_progress[key]
                
                # Different comparison based on type
                if isinstance(required_value, bool):
                    if not user_value:
                        criteria_met = False
                        break
                elif isinstance(required_value, (int, float)):
                    if user_value < required_value:
                        criteria_met = False
                        break
                else:
                    if user_value != required_value:
                        criteria_met = False
                        break
            
            if criteria_met:
                earned_achievements.append(achievement)
                
        return earned_achievements
    
    def get_progress_bar_data(self, user_progress):
        """
        Get data for displaying progress bars.
        
        Args:
            user_progress: Dictionary containing user's progress
            
        Returns:
            Dictionary with progress bar data
        """
        # Calculate total challenges completed
        if 'challenges_completed' in user_progress:
            challenges_completed = user_progress['challenges_completed']
        else:
            challenges_completed = 0
            
        # Calculate level
        if 'total_points' in user_progress:
            points = user_progress['total_points']
        else:
            points = 0
            
        # Define level thresholds
        level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
        
        # Calculate current level
        level = 0
        for i, threshold in enumerate(level_thresholds):
            if points >= threshold:
                level = i
        
        # Calculate progress to next level
        if level < len(level_thresholds) - 1:
            next_level_points = level_thresholds[level + 1]
            current_level_points = level_thresholds[level]
            points_needed = next_level_points - current_level_points
            level_progress = (points - current_level_points) / points_needed
        else:
            # Max level reached
            level_progress = 1.0
            
        return {
            "level": level,
            "points": points,
            "challenges_completed": challenges_completed,
            "level_progress": level_progress,
            "next_level_points": next_level_points if level < len(level_thresholds) - 1 else None
        }
    
    def get_daily_challenge(self, seed=None):
        """
        Get a random daily challenge.
        
        Args:
            seed: Optional seed for random selection
            
        Returns:
            Dictionary with daily challenge
        """
        # Use seed based on date if not provided
        if seed is None:
            today = datetime.now().strftime("%Y%m%d")
            seed = int(today)
            
        # Set random seed for reproducible daily challenge
        random.seed(seed)
        
        # Select a random challenge
        challenge = random.choice(self.challenges)
        
        # Add daily bonus points
        daily_challenge = challenge.copy()
        daily_challenge["points"] = int(daily_challenge["points"] * 1.5)  # 50% bonus
        daily_challenge["daily_challenge"] = True
        daily_challenge["expires"] = (datetime.now() + timedelta(days=1)).isoformat()
        
        return daily_challenge