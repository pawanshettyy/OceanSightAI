import logging
import logging
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def initialize_simple_data():
    """Initialize the database with simple marine biodiversity data"""
    try:
        from app import Species, OceanData, BiodiversityIndex, Alert, db
        # Check if data already exists
        if Species.query.first() is not None:
            logger.info("Sample data already exists, skipping initialization")
            return
        logger.info("Initializing simple marine biodiversity data...")
        # ...existing code for adding species, ocean data, biodiversity indices, alerts...
        db.session.commit()
        logger.info("Simple sample data initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing simple data: {str(e)}")
        db.session.rollback()
        raise