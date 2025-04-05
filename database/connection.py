"""
Database connection module for GAIA-∞ Climate Intelligence Platform.
"""

import os
import logging
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database connection string from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Try to construct DATABASE_URL from individual environment variables
    PGUSER = os.environ.get("PGUSER")
    PGPASSWORD = os.environ.get("PGPASSWORD")
    PGHOST = os.environ.get("PGHOST")
    PGPORT = os.environ.get("PGPORT")
    PGDATABASE = os.environ.get("PGDATABASE")
    
    if all([PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE]):
        # Construct the PostgreSQL connection URL
        DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
        logger.info("Constructed DATABASE_URL from individual PostgreSQL environment variables")
    else:
        logger.warning("Database environment variables not found. Using default SQLite database.")
        DATABASE_URL = "sqlite:///gaia_climate_platform.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Create a base class for declarative models
Base = declarative_base()
Base.metadata.bind = engine

def get_db_session():
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session object
    """
    return Session()

def close_db_session(session):
    """
    Close a database session.
    
    Args:
        session: SQLAlchemy session object
    """
    session.close()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        # Import all models to ensure they're registered with the Base
        from database.models import ClimateData, User, UserPreference, SavedLocation, Alert, SimulationResult, EarthEngineImage
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables exist
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        required_tables = ['climate_data', 'users', 'user_preferences', 'saved_locations', 'alerts']
        
        missing_tables = [table for table in required_tables if table not in table_names]
        if missing_tables:
            logger.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
            
        logger.info(f"Database tables verified: {', '.join(table_names)}")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

def check_connection():
    """
    Check if the database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Try to execute a simple query
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()  # Actually fetch the result to complete the query
            connection.commit()  # Commit any pending transaction
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False