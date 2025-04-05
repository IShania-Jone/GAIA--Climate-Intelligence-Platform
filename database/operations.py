"""
Database operations module for GAIA-∞ Climate Intelligence Platform.

This module provides functions for interacting with the database,
including storing and retrieving climate data, alerts, simulation results, etc.
"""

import logging
import numpy as np
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from database.connection import get_db_session, close_db_session, init_db
from database.models import (
    User, UserPreference, SavedLocation, ClimateData, 
    Alert, SimulationResult, EarthEngineImage
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user(username, email, password_hash, role='user'):
    """Create a new user in the database."""
    session = get_db_session()
    try:
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            logger.warning(f"User with username '{username}' or email '{email}' already exists")
            return False

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=datetime.utcnow()
        )

        session.add(user)
        session.commit()
        logger.info(f"User '{username}' created successfully")
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return False
    finally:
        close_db_session(session)

def store_climate_data(data_type, timestamp, value, source=None, 
                      latitude=None, longitude=None, is_prediction=False, 
                      prediction_model=None, meta_data=None):
    """Store climate data in the database."""
    session = get_db_session()
    try:
        # Convert numpy types to Python native types
        if isinstance(value, (np.number, float)):
            value = float(value)
        if isinstance(latitude, (np.number, float)):
            latitude = float(latitude)
        if isinstance(longitude, (np.number, float)):
            longitude = float(longitude)

        climate_data = ClimateData(
            data_type=data_type,
            timestamp=timestamp,
            value=value,
            latitude=latitude,
            longitude=longitude,
            source=source,
            is_prediction=is_prediction,
            prediction_model=prediction_model,
            meta_data=meta_data,
            created_at=datetime.utcnow()
        )

        session.add(climate_data)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error storing climate data: {str(e)}")
        return False
    finally:
        close_db_session(session)

def get_climate_data(data_type=None, start_date=None, end_date=None, 
                    is_prediction=None, limit=1000):
    """Get climate data from the database."""
    if not init_db():
        logger.error("Database not properly initialized")
        return []

    session = get_db_session()
    try:
        query = session.query(ClimateData)

        if data_type:
            query = query.filter(ClimateData.data_type == data_type)
        if start_date:
            query = query.filter(ClimateData.timestamp >= start_date)
        if end_date:
            query = query.filter(ClimateData.timestamp <= end_date)
        if is_prediction is not None:
            query = query.filter(ClimateData.is_prediction == is_prediction)

        return query.order_by(ClimateData.timestamp).limit(limit).all()

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving climate data: {str(e)}")
        return []
    finally:
        close_db_session(session)

def create_alert(alert_type, severity, region, latitude, longitude, 
                title, description=None, expires_at=None, source=None):
    """Create a new environmental alert."""
    session = get_db_session()
    try:
        if isinstance(severity, np.number):
            severity = int(severity)
        if isinstance(latitude, (np.number, float)):
            latitude = float(latitude)
        if isinstance(longitude, (np.number, float)):
            longitude = float(longitude)

        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            region=region,
            latitude=latitude,
            longitude=longitude,
            title=title,
            description=description,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True,
            source=source
        )

        session.add(alert)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating alert: {str(e)}")
        return False
    finally:
        close_db_session(session)

def get_active_alerts(alert_type=None, region=None, min_severity=None):
    """Get active alerts from the database."""
    session = get_db_session()
    try:
        query = session.query(Alert).filter(Alert.is_active == True)

        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if region:
            query = query.filter(Alert.region == region)
        if min_severity:
            query = query.filter(Alert.severity >= min_severity)

        return query.order_by(Alert.severity.desc(), Alert.issued_at.desc()).all()

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        return []
    finally:
        close_db_session(session)

def store_simulation_result(name, scenario, parameters, results, description=None, created_by=None):
    """Store a climate simulation result."""
    session = get_db_session()
    try:
        parameters = _convert_numpy_to_python_types(parameters) if parameters else None
        results = _convert_numpy_to_python_types(results) if results else None
        if isinstance(created_by, np.number):
            created_by = int(created_by)

        simulation = SimulationResult(
            name=name,
            scenario=scenario,
            parameters=parameters,
            results=results,
            created_by=created_by,
            created_at=datetime.utcnow(),
            description=description
        )

        session.add(simulation)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error storing simulation result: {str(e)}")
        return False
    finally:
        close_db_session(session)

def _convert_numpy_to_python_types(obj):
    """Convert numpy types to Python native types in a nested structure."""
    if isinstance(obj, dict):
        return {k: _convert_numpy_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_to_python_types(item) for item in obj]
    elif isinstance(obj, np.number):
        return int(obj) if isinstance(obj, (np.int32, np.int64)) else float(obj)
    elif isinstance(obj, np.ndarray):
        return _convert_numpy_to_python_types(obj.tolist())
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

def get_simulation_results(scenario=None, created_by=None):
    """Get simulation results from the database."""
    session = get_db_session()
    try:
        query = session.query(SimulationResult)

        if scenario:
            query = query.filter(SimulationResult.scenario == scenario)
        if created_by:
            query = query.filter(SimulationResult.created_by == created_by)

        return query.order_by(SimulationResult.created_at.desc()).all()

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving simulation results: {str(e)}")
        return []
    finally:
        close_db_session(session)

def store_earth_engine_image(dataset_id, display_name, description=None, 
                           date=None, image_properties=None, visualization_params=None):
    """Store Earth Engine image metadata."""
    session = get_db_session()
    try:
        image_properties = _convert_numpy_to_python_types(image_properties) if image_properties else None
        visualization_params = _convert_numpy_to_python_types(visualization_params) if visualization_params else None

        image = EarthEngineImage(
            dataset_id=dataset_id,
            display_name=display_name,
            description=description,
            date=date,
            image_properties=image_properties,
            visualization_params=visualization_params,
            created_at=datetime.utcnow()
        )

        session.add(image)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error storing Earth Engine image: {str(e)}")
        return False
    finally:
        close_db_session(session)

def get_earth_engine_images():
    """Get Earth Engine image metadata from the database."""
    session = get_db_session()
    try:
        return session.query(EarthEngineImage).order_by(EarthEngineImage.display_name).all()

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving Earth Engine images: {str(e)}")
        return []
    finally:
        close_db_session(session)

def save_user_location(user_id, name, latitude, longitude, description=None):
    """Save a location for a user."""
    session = get_db_session()
    try:
        if isinstance(user_id, np.number):
            user_id = int(user_id)
        if isinstance(latitude, (np.number, float)):
            latitude = float(latitude)
        if isinstance(longitude, (np.number, float)):
            longitude = float(longitude)

        location = SavedLocation(
            user_id=user_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
            description=description,
            created_at=datetime.utcnow()
        )

        session.add(location)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving user location: {str(e)}")
        return False
    finally:
        close_db_session(session)

def get_user_saved_locations(user_id):
    """Get saved locations for a user."""
    session = get_db_session()
    try:
        return session.query(SavedLocation).filter(SavedLocation.user_id == user_id).all()

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user saved locations: {str(e)}")
        return []
    finally:
        close_db_session(session)

def update_user_preferences(user_id, theme=None, default_map_view=None, 
                          temperature_unit=None, notification_enabled=None, 
                          advanced_mode=None, custom_settings=None):
    """Update user preferences."""
    session = get_db_session()
    try:
        preferences = session.query(UserPreference).filter(UserPreference.user_id == user_id).first()

        if not preferences:
            preferences = UserPreference(user_id=user_id)
            session.add(preferences)

        if theme is not None:
            preferences.theme = theme
        if default_map_view is not None:
            preferences.default_map_view = default_map_view
        if temperature_unit is not None:
            preferences.temperature_unit = temperature_unit
        if notification_enabled is not None:
            preferences.notification_enabled = notification_enabled
        if advanced_mode is not None:
            preferences.advanced_mode = advanced_mode
        if custom_settings is not None:
            preferences.custom_settings = custom_settings

        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating user preferences: {str(e)}")
        return False
    finally:
        close_db_session(session)