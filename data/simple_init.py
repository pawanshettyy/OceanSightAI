import logging
from datetime import datetime, timedelta

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
        
        # Add a few sample species
        species_data = [
            {
                'scientific_name': 'Thunnus thynnus',
                'common_name': 'Atlantic Bluefin Tuna',
                'species_type': 'fish',
                'conservation_status': 'critically endangered',
                'habitat': 'Open ocean',
                'threat_level': 'critical'
            },
            {
                'scientific_name': 'Chelonia mydas',
                'common_name': 'Green Sea Turtle',
                'species_type': 'reptile',
                'conservation_status': 'endangered',
                'habitat': 'Coastal waters',
                'threat_level': 'high'
            }
        ]
        
        for species_info in species_data:
            species = Species(**species_info)
            db.session.add(species)
        
        # Add sample ocean data
        ocean_point = OceanData(
            latitude=25.7617,
            longitude=-80.1918,
            temperature=24.5,
            salinity=36.2,
            ph_level=8.1,
            location_name='Florida Keys'
        )
        db.session.add(ocean_point)
        
        db.session.commit()
        logger.info("Simple sample data initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing simple data: {str(e)}")
        db.session.rollback()
        raise