from app import db
from models import Species, OceanData, BiodiversityIndex, Alert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def initialize_simple_data():
    """Initialize the database with simple marine biodiversity data"""
    try:
        # Check if data already exists
        if Species.query.first() is not None:
            logger.info("Sample data already exists, skipping initialization")
            return
        
        logger.info("Initializing simple marine biodiversity data...")
        
        # Create simple species data
        species1 = Species()
        species1.scientific_name = 'Thunnus thynnus'
        species1.common_name = 'Atlantic Bluefin Tuna'
        species1.species_type = 'fish'
        species1.conservation_status = 'critically endangered'
        species1.habitat = 'Open ocean'
        species1.population_trend = 'decreasing'
        species1.threat_level = 'critical'
        species1.description = 'Large tuna species severely threatened by overfishing'
        db.session.add(species1)
        
        species2 = Species()
        species2.scientific_name = 'Carcharodon carcharias'
        species2.common_name = 'Great White Shark'
        species2.species_type = 'fish'
        species2.conservation_status = 'vulnerable'
        species2.habitat = 'Coastal waters'
        species2.population_trend = 'decreasing'
        species2.threat_level = 'medium'
        species2.description = 'Apex predator important for marine ecosystem balance'
        db.session.add(species2)
        
        species3 = Species()
        species3.scientific_name = 'Chelonia mydas'
        species3.common_name = 'Green Sea Turtle'
        species3.species_type = 'reptile'
        species3.conservation_status = 'endangered'
        species3.habitat = 'Coastal waters'
        species3.population_trend = 'increasing'
        species3.threat_level = 'high'
        species3.description = 'Large sea turtle recovering from near extinction'
        db.session.add(species3)
        
        # Create simple ocean data
        ocean1 = OceanData()
        ocean1.latitude = 42.0
        ocean1.longitude = -70.0
        ocean1.temperature = 15.5
        ocean1.salinity = 35.0
        ocean1.ph_level = 8.1
        ocean1.timestamp = datetime.utcnow() - timedelta(hours=1)
        ocean1.location_name = 'North Atlantic'
        db.session.add(ocean1)
        
        ocean2 = OceanData()
        ocean2.latitude = 25.0
        ocean2.longitude = -80.0
        ocean2.temperature = 26.2
        ocean2.salinity = 36.0
        ocean2.ph_level = 8.0
        ocean2.timestamp = datetime.utcnow() - timedelta(hours=2)
        ocean2.location_name = 'Caribbean'
        db.session.add(ocean2)
        
        # Create simple biodiversity index
        bio1 = BiodiversityIndex()
        bio1.region_name = 'Caribbean Marine Ecosystem'
        bio1.latitude = 18.0
        bio1.longitude = -78.0
        bio1.species_count = 125
        bio1.endemic_species = 23
        bio1.threatened_species = 34
        bio1.biodiversity_score = 72.5
        bio1.ecosystem_health = 'good'
        bio1.assessment_date = datetime.utcnow() - timedelta(days=7)
        db.session.add(bio1)
        
        # Create simple alert
        alert1 = Alert()
        alert1.alert_type = 'overfishing'
        alert1.severity = 'high'
        alert1.title = 'Overfishing Alert: Atlantic Bluefin Tuna'
        alert1.description = 'Catch quotas exceeded in North Atlantic region'
        alert1.location = 'North Atlantic'
        alert1.latitude = 42.0
        alert1.longitude = -65.0
        alert1.is_active = True
        alert1.created_at = datetime.utcnow() - timedelta(hours=6)
        db.session.add(alert1)
        
        db.session.commit()
        logger.info("Simple sample data initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing simple data: {str(e)}")
        db.session.rollback()
        raise