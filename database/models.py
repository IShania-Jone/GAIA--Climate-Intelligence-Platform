"""
Database models for the GAIA-∞ Climate Intelligence Platform.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    """User model for storing user data"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default='user')
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserPreference(Base):
    """User preferences model"""
    __tablename__ = 'user_preferences'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    theme = Column(String(20), default='light')
    default_map_view = Column(String(50), default='earth')
    temperature_unit = Column(String(10), default='celsius')
    notification_enabled = Column(Boolean, default=True)
    advanced_mode = Column(Boolean, default=False)
    custom_settings = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference {self.id}>"

class SavedLocation(Base):
    """Saved locations model"""
    __tablename__ = 'saved_locations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_locations")
    
    def __repr__(self):
        return f"<SavedLocation {self.name}>"

class ClimateData(Base):
    """Climate data model for storing climate measurements and predictions"""
    __tablename__ = 'climate_data'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    data_type = Column(String(50), nullable=False)  # temperature, co2, sea_level, ice_extent
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    source = Column(String(100))
    is_prediction = Column(Boolean, default=False)
    prediction_model = Column(String(100))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<ClimateData {self.data_type} @ {self.timestamp}>"

class Alert(Base):
    """Environmental alerts model"""
    __tablename__ = 'alerts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # drought, flood, wildfire, extreme_weather
    severity = Column(Integer, nullable=False)  # 1-5, with 5 being most severe
    region = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    source = Column(String(100))
    
    def __repr__(self):
        return f"<Alert {self.alert_type} in {self.region}>"

class SimulationResult(Base):
    """Model for storing climate simulation results"""
    __tablename__ = 'simulation_results'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    scenario = Column(String(50), nullable=False)
    parameters = Column(JSON)
    results = Column(JSON)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text)
    
    def __repr__(self):
        return f"<SimulationResult {self.name}>"

class EarthEngineImage(Base):
    """Model for storing Earth Engine image references and metadata"""
    __tablename__ = 'earth_engine_images'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    image_properties = Column(JSON)
    visualization_params = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<EarthEngineImage {self.display_name}>"