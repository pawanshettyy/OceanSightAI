from app import db
from models import OceanData, Species, FisheriesData, BiodiversityIndex, Alert, SpeciesObservation
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

def initialize_sample_data():
    """Initialize the database with sample marine biodiversity data"""
    try:
        # Check if data already exists
        if Species.query.first() is not None:
            logger.info("Sample data already exists, skipping initialization")
            return
        
        logger.info("Initializing sample marine biodiversity data...")
        
        # Initialize data in order of dependencies
        create_species_data()
        create_ocean_data()
        create_biodiversity_indices()
        create_species_observations()
        create_fisheries_data()
        create_alerts()
        
        db.session.commit()
        logger.info("Sample data initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {str(e)}")
        db.session.rollback()
        raise

def create_species_data():
    """Create sample species data"""
    species_data = [
        {
            'scientific_name': 'Thunnus thynnus',
            'common_name': 'Atlantic Bluefin Tuna',
            'species_type': 'fish',
            'conservation_status': 'critically endangered',
            'habitat': 'Open ocean, temperate and subtropical waters',
            'depth_range': '0-1000m',
            'geographic_range': 'North Atlantic Ocean',
            'population_trend': 'decreasing',
            'threat_level': 'critical',
            'description': 'Large, fast-swimming tuna species highly valued for commercial fishing. Severely overfished populations.'
        },
        {
            'scientific_name': 'Eubalaena glacialis',
            'common_name': 'North Atlantic Right Whale',
            'species_type': 'mammal',
            'conservation_status': 'critically endangered',
            'habitat': 'Coastal and shelf waters',
            'depth_range': '0-200m',
            'geographic_range': 'North Atlantic Ocean',
            'population_trend': 'decreasing',
            'threat_level': 'critical',
            'description': 'One of the most endangered large whales. Threatened by ship strikes and fishing gear entanglement.'
        },
        {
            'scientific_name': 'Carcharodon carcharias',
            'common_name': 'Great White Shark',
            'species_type': 'fish',
            'conservation_status': 'vulnerable',
            'habitat': 'Coastal surface waters',
            'depth_range': '0-1200m',
            'geographic_range': 'Global distribution in temperate waters',
            'population_trend': 'decreasing',
            'threat_level': 'medium',
            'description': 'Apex predator critical for marine ecosystem balance. Declining due to overfishing and bycatch.'
        },
        {
            'scientific_name': 'Chelonia mydas',
            'common_name': 'Green Sea Turtle',
            'species_type': 'reptile',
            'conservation_status': 'endangered',
            'habitat': 'Coastal waters, seagrass beds',
            'depth_range': '0-100m',
            'geographic_range': 'Tropical and subtropical oceans worldwide',
            'population_trend': 'increasing',
            'threat_level': 'high',
            'description': 'Large sea turtle recovering from near extinction. Threatened by plastic pollution and coastal development.'
        },
        {
            'scientific_name': 'Gadus morhua',
            'common_name': 'Atlantic Cod',
            'species_type': 'fish',
            'conservation_status': 'vulnerable',
            'habitat': 'Continental shelf waters',
            'depth_range': '0-600m',
            'geographic_range': 'North Atlantic Ocean',
            'population_trend': 'stable',
            'threat_level': 'medium',
            'description': 'Important commercial fish species. Populations recovering from historical overfishing.'
        },
        {
            'scientific_name': 'Physeter macrocephalus',
            'common_name': 'Sperm Whale',
            'species_type': 'mammal',
            'conservation_status': 'vulnerable',
            'habitat': 'Deep ocean waters',
            'depth_range': '0-3000m',
            'geographic_range': 'Global distribution in deep waters',
            'population_trend': 'stable',
            'threat_level': 'medium',
            'description': 'Largest toothed whale, deep-diving species. Threatened by ship noise and plastic pollution.'
        },
        {
            'scientific_name': 'Acropora palmata',
            'common_name': 'Elkhorn Coral',
            'species_type': 'coral',
            'conservation_status': 'critically endangered',
            'habitat': 'Shallow tropical reef environments',
            'depth_range': '1-20m',
            'geographic_range': 'Caribbean Sea, Western Atlantic',
            'population_trend': 'decreasing',
            'threat_level': 'critical',
            'description': 'Important reef-building coral. Severely threatened by ocean acidification and warming.'
        },
        {
            'scientific_name': 'Hippocampus erectus',
            'common_name': 'Lined Seahorse',
            'species_type': 'fish',
            'conservation_status': 'vulnerable',
            'habitat': 'Seagrass beds, coral reefs',
            'depth_range': '0-73m',
            'geographic_range': 'Western Atlantic Ocean',
            'population_trend': 'decreasing',
            'threat_level': 'medium',
            'description': 'Small marine fish threatened by habitat destruction and collection for traditional medicine.'
        },
        {
            'scientific_name': 'Caretta caretta',
            'common_name': 'Loggerhead Sea Turtle',
            'species_type': 'reptile',
            'conservation_status': 'vulnerable',
            'habitat': 'Open ocean, coastal waters',
            'depth_range': '0-200m',
            'geographic_range': 'Global distribution in temperate and tropical waters',
            'population_trend': 'stable',
            'threat_level': 'medium',
            'description': 'Long-lived sea turtle species. Threatened by bycatch in fishing operations.'
        },
        {
            'scientific_name': 'Salmo salar',
            'common_name': 'Atlantic Salmon',
            'species_type': 'fish',
            'conservation_status': 'vulnerable',
            'habitat': 'Rivers, coastal waters',
            'depth_range': '0-210m',
            'geographic_range': 'North Atlantic Ocean and rivers',
            'population_trend': 'decreasing',
            'threat_level': 'high',
            'description': 'Anadromous fish species. Wild populations threatened by habitat loss and aquaculture impacts.'
        },
        {
            'scientific_name': 'Mytilus edulis',
            'common_name': 'Blue Mussel',
            'species_type': 'invertebrate',
            'conservation_status': 'least concern',
            'habitat': 'Intertidal rocky shores',
            'depth_range': '0-10m',
            'geographic_range': 'North Atlantic and North Pacific coasts',
            'population_trend': 'stable',
            'threat_level': 'low',
            'description': 'Important filter-feeding mollusk that helps maintain water quality in coastal ecosystems.'
        },
        {
            'scientific_name': 'Laminaria hyperborea',
            'common_name': 'Cuvie Kelp',
            'species_type': 'algae',
            'conservation_status': 'least concern',
            'habitat': 'Rocky subtidal zones',
            'depth_range': '5-30m',
            'geographic_range': 'Northeast Atlantic Ocean',
            'population_trend': 'stable',
            'threat_level': 'low',
            'description': 'Large brown algae forming underwater forests. Important habitat for marine biodiversity.'
        }
    ]
    
    for species_info in species_data:
        species = Species(**species_info)
        db.session.add(species)
    
    logger.info(f"Created {len(species_data)} species records")

def create_ocean_data():
    """Create sample oceanographic data"""
    # Define key marine regions with realistic coordinates and parameters
    regions = [
        {'name': 'Gulf of Maine', 'lat': 43.5, 'lng': -69.0, 'temp_base': 12, 'salinity_base': 32.5, 'ph_base': 8.0},
        {'name': 'Sargasso Sea', 'lat': 32.0, 'lng': -64.0, 'temp_base': 22, 'salinity_base': 36.5, 'ph_base': 8.1},
        {'name': 'North Sea', 'lat': 56.0, 'lng': 3.0, 'temp_base': 10, 'salinity_base': 35.0, 'ph_base': 8.0},
        {'name': 'Caribbean Sea', 'lat': 15.0, 'lng': -75.0, 'temp_base': 27, 'salinity_base': 36.0, 'ph_base': 8.2},
        {'name': 'Mediterranean Sea', 'lat': 40.0, 'lng': 18.0, 'temp_base': 20, 'salinity_base': 38.5, 'ph_base': 8.1},
        {'name': 'Bering Sea', 'lat': 58.0, 'lng': -175.0, 'temp_base': 4, 'salinity_base': 33.0, 'ph_base': 7.9},
        {'name': 'Great Barrier Reef', 'lat': -18.0, 'lng': 147.0, 'temp_base': 25, 'salinity_base': 35.5, 'ph_base': 8.0},
        {'name': 'Norwegian Sea', 'lat': 66.0, 'lng': 2.0, 'temp_base': 6, 'salinity_base': 34.8, 'ph_base': 8.0}
    ]
    
    # Generate data for the last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)
    
    for region in regions:
        for day in range(30):
            for measurement in range(random.randint(2, 6)):  # 2-6 measurements per day per region
                timestamp = start_date + timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                
                # Add some realistic variation to coordinates
                lat_variation = random.uniform(-2.0, 2.0)
                lng_variation = random.uniform(-2.0, 2.0)
                
                # Add seasonal and random variation to parameters
                temp_variation = random.uniform(-3.0, 3.0)
                salinity_variation = random.uniform(-1.0, 1.0)
                ph_variation = random.uniform(-0.3, 0.3)
                
                ocean_point = OceanData(
                    latitude=region['lat'] + lat_variation,
                    longitude=region['lng'] + lng_variation,
                    temperature=max(0, region['temp_base'] + temp_variation),
                    salinity=max(0, region['salinity_base'] + salinity_variation),
                    ph_level=max(6.5, min(8.5, region['ph_base'] + ph_variation)),
                    oxygen_level=random.uniform(4.0, 8.5),  # mg/L
                    current_speed=random.uniform(0.1, 2.5),  # m/s
                    current_direction=random.uniform(0, 360),  # degrees
                    depth=random.uniform(10, 2000),  # meters
                    timestamp=timestamp,
                    location_name=region['name']
                )
                db.session.add(ocean_point)
    
    logger.info("Created oceanographic data for 8 regions over 30 days")

def create_biodiversity_indices():
    """Create biodiversity index data for different regions"""
    regions_data = [
        {
            'region_name': 'Caribbean Marine Ecosystem',
            'latitude': 18.0,
            'longitude': -78.0,
            'species_count': 125,
            'endemic_species': 23,
            'threatened_species': 34,
            'biodiversity_score': 72.5,
            'ecosystem_health': 'good',
            'notes': 'High coral diversity but declining due to bleaching events'
        },
        {
            'region_name': 'North Atlantic Continental Shelf',
            'latitude': 42.0,
            'longitude': -65.0,
            'species_count': 89,
            'endemic_species': 5,
            'threatened_species': 18,
            'biodiversity_score': 68.3,
            'ecosystem_health': 'fair',
            'notes': 'Recovering from historical overfishing, showing signs of improvement'
        },
        {
            'region_name': 'Mediterranean Deep Sea',
            'latitude': 38.5,
            'longitude': 15.0,
            'species_count': 156,
            'endemic_species': 45,
            'threatened_species': 28,
            'biodiversity_score': 75.8,
            'ecosystem_health': 'good',
            'notes': 'High endemic diversity but threatened by pollution and warming'
        },
        {
            'region_name': 'Arctic Marine Region',
            'latitude': 75.0,
            'longitude': -100.0,
            'species_count': 67,
            'endemic_species': 12,
            'threatened_species': 15,
            'biodiversity_score': 58.2,
            'ecosystem_health': 'fair',
            'notes': 'Rapidly changing ecosystem due to climate change and ice loss'
        },
        {
            'region_name': 'Pacific Northwest Coast',
            'latitude': 48.5,
            'longitude': -125.0,
            'species_count': 198,
            'endemic_species': 32,
            'threatened_species': 42,
            'biodiversity_score': 81.4,
            'ecosystem_health': 'excellent',
            'notes': 'Diverse kelp forest ecosystem with strong conservation measures'
        },
        {
            'region_name': 'Great Barrier Reef System',
            'latitude': -16.0,
            'longitude': 145.5,
            'species_count': 234,
            'endemic_species': 67,
            'threatened_species': 56,
            'biodiversity_score': 65.1,
            'ecosystem_health': 'poor',
            'notes': 'Severe coral bleaching and acidification impacts on biodiversity'
        }
    ]
    
    for region_data in regions_data:
        assessment_dates = []
        for i in range(3):  # Create 3 assessments per region over time
            assessment_date = datetime.utcnow() - timedelta(days=random.randint(30, 365))
            assessment_dates.append(assessment_date)
        
        assessment_dates.sort()
        
        for i, assessment_date in enumerate(assessment_dates):
            # Add some temporal variation
            score_variation = random.uniform(-5.0, 5.0) if i > 0 else 0
            species_variation = random.randint(-10, 10) if i > 0 else 0
            
            biodiversity_index = BiodiversityIndex(
                region_name=region_data['region_name'],
                latitude=region_data['latitude'],
                longitude=region_data['longitude'],
                species_count=max(0, region_data['species_count'] + species_variation),
                endemic_species=region_data['endemic_species'],
                threatened_species=region_data['threatened_species'],
                biodiversity_score=max(0, min(100, region_data['biodiversity_score'] + score_variation)),
                ecosystem_health=region_data['ecosystem_health'],
                assessment_date=assessment_date,
                notes=region_data['notes']
            )
            db.session.add(biodiversity_index)
    
    logger.info("Created biodiversity indices for 6 marine regions")

def create_species_observations():
    """Create species observation records"""
    # Get all species from database
    species_list = Species.query.all()
    if not species_list:
        logger.warning("No species found for creating observations")
        return
    
    # Define observation locations based on species habitats
    observation_locations = [
        {'lat': 25.7, 'lng': -80.2, 'location': 'Florida Keys'},
        {'lat': 42.0, 'lng': -70.0, 'location': 'Stellwagen Bank'},
        {'lat': 37.8, 'lng': -122.5, 'location': 'Gulf of the Farallones'},
        {'lat': -25.3, 'lng': 153.1, 'location': 'Great Barrier Reef'},
        {'lat': 60.0, 'lng': 5.0, 'location': 'Norwegian Fjords'},
        {'lat': 45.5, 'lng': -62.0, 'location': 'Bay of Fundy'},
        {'lat': 55.0, 'lng': 2.0, 'location': 'North Sea'},
        {'lat': 18.0, 'lng': -77.0, 'location': 'Caribbean Sea'}
    ]
    
    # Generate observations over the past 60 days
    start_date = datetime.utcnow() - timedelta(days=60)
    
    for species in species_list:
        # Create 3-15 observations per species
        num_observations = random.randint(3, 15)
        
        for _ in range(num_observations):
            location = random.choice(observation_locations)
            observation_date = start_date + timedelta(days=random.randint(0, 60))
            
            # Vary location slightly
            lat_variation = random.uniform(-0.5, 0.5)
            lng_variation = random.uniform(-0.5, 0.5)
            
            # Confidence based on species type and observation method
            base_confidence = 85 if species.species_type in ['fish', 'mammal'] else 75
            confidence_variation = random.uniform(-15, 10)
            confidence = max(50, min(95, base_confidence + confidence_variation))
            
            observation = SpeciesObservation(
                species_id=species.id,
                latitude=location['lat'] + lat_variation,
                longitude=location['lng'] + lng_variation,
                observation_count=random.randint(1, 12),
                confidence_level=confidence,
                observation_method=random.choice(['visual', 'camera', 'sonar', 'acoustic']),
                observer_type=random.choice(['researcher', 'citizen', 'ai_system']),
                observation_date=observation_date,
                notes=f"Observation in {location['location']} area"
            )
            db.session.add(observation)
    
    logger.info(f"Created species observations for {len(species_list)} species")

def create_fisheries_data():
    """Create fisheries catch data"""
    # Get commercial fish species
    commercial_species = Species.query.filter(Species.species_type == 'fish').all()
    if not commercial_species:
        logger.warning("No fish species found for creating fisheries data")
        return
    
    fishing_areas = [
        {'area': 'Grand Banks', 'lat': 45.0, 'lng': -50.0},
        {'area': 'Georges Bank', 'lat': 41.0, 'lng': -67.5},
        {'area': 'North Sea', 'lat': 56.0, 'lng': 3.0},
        {'area': 'Barents Sea', 'lat': 74.0, 'lng': 40.0},
        {'area': 'Bering Sea', 'lat': 58.0, 'lng': -175.0},
        {'area': 'Gulf of Mexico', 'lat': 26.0, 'lng': -90.0}
    ]
    
    vessel_types = ['trawler', 'longliner', 'purse_seiner', 'gillnetter']
    fishing_methods = ['bottom_trawl', 'pelagic_trawl', 'longline', 'purse_seine', 'gillnet']
    
    # Generate fishing data for the past 90 days
    start_date = datetime.utcnow() - timedelta(days=90)
    
    for species in commercial_species:
        # Create 5-20 fishing records per species
        num_records = random.randint(5, 20)
        
        for _ in range(num_records):
            area = random.choice(fishing_areas)
            catch_date = start_date + timedelta(days=random.randint(0, 90))
            
            # Catch amount varies by species size and commercial value
            if 'tuna' in species.common_name.lower():
                base_catch = random.uniform(50, 500)  # High-value species
                quota_limit = base_catch * random.uniform(1.2, 2.0)
            elif 'cod' in species.common_name.lower():
                base_catch = random.uniform(100, 800)
                quota_limit = base_catch * random.uniform(1.1, 1.8)
            else:
                base_catch = random.uniform(20, 300)
                quota_limit = base_catch * random.uniform(1.3, 2.5)
            
            # Sustainability score based on species threat level
            if species.threat_level == 'critical':
                sustainability_base = random.uniform(15, 35)
            elif species.threat_level == 'high':
                sustainability_base = random.uniform(25, 50)
            elif species.threat_level == 'medium':
                sustainability_base = random.uniform(40, 70)
            else:
                sustainability_base = random.uniform(60, 85)
            
            fisheries_record = FisheriesData(
                species_id=species.id,
                catch_amount=base_catch,
                fishing_area=area['area'],
                latitude=area['lat'] + random.uniform(-2.0, 2.0),
                longitude=area['lng'] + random.uniform(-2.0, 2.0),
                fishing_method=random.choice(fishing_methods),
                vessel_type=random.choice(vessel_types),
                catch_date=catch_date,
                quota_limit=quota_limit,
                sustainability_score=sustainability_base
            )
            db.session.add(fisheries_record)
    
    logger.info(f"Created fisheries data for {len(commercial_species)} fish species")

def create_alerts():
    """Create environmental and conservation alerts"""
    alert_data = [
        {
            'alert_type': 'overfishing',
            'severity': 'high',
            'title': 'Quota Exceeded: Atlantic Bluefin Tuna',
            'description': 'Catch quotas for Atlantic Bluefin Tuna have been exceeded by 25% in the Grand Banks region',
            'location': 'Grand Banks',
            'latitude': 45.0,
            'longitude': -50.0,
            'created_at': datetime.utcnow() - timedelta(days=2)
        },
        {
            'alert_type': 'temperature_anomaly',
            'severity': 'critical',
            'title': 'Extreme Temperature Rise in Caribbean',
            'description': 'Sea surface temperatures 3.2C above normal, triggering coral bleaching risk',
            'location': 'Caribbean Sea',
            'latitude': 18.0,
            'longitude': -78.0,
            'created_at': datetime.utcnow() - timedelta(days=1)
        },
        {
            'alert_type': 'biodiversity_risk',
            'severity': 'high',
            'title': 'Declining Biodiversity: Great Barrier Reef',
            'description': 'Biodiversity index has dropped to 65.1, indicating ecosystem stress',
            'location': 'Great Barrier Reef',
            'latitude': -16.0,
            'longitude': 145.5,
            'created_at': datetime.utcnow() - timedelta(days=3)
        },
        {
            'alert_type': 'species_threat',
            'severity': 'critical',
            'title': 'North Atlantic Right Whale Population Crisis',
            'description': 'Only 340 individuals remaining, ship strikes reported in migration corridor',
            'location': 'North Atlantic',
            'latitude': 42.0,
            'longitude': -65.0,
            'created_at': datetime.utcnow() - timedelta(hours=6)
        },
        {
            'alert_type': 'sustainability_risk',
            'severity': 'medium',
            'title': 'Low Sustainability Score: North Sea Fishing',
            'description': 'Average sustainability score of 42% detected in North Sea commercial fishing',
            'location': 'North Sea',
            'latitude': 56.0,
            'longitude': 3.0,
            'created_at': datetime.utcnow() - timedelta(days=5)
        },
        {
            'alert_type': 'ocean_acidification',
            'severity': 'high',
            'title': 'pH Levels Dropping in Arctic Waters',
            'description': 'Ocean pH has decreased to 7.8, threatening calcifying organisms',
            'location': 'Arctic Ocean',
            'latitude': 75.0,
            'longitude': -100.0,
            'created_at': datetime.utcnow() - timedelta(days=1)
        }
    ]
    
    for alert_info in alert_data:
        alert = Alert(**alert_info, is_active=True)
        db.session.add(alert)
    
    # Add some resolved alerts from the past
    resolved_alerts = [
        {
            'alert_type': 'overfishing',
            'severity': 'medium',
            'title': 'Cod Overfishing Alert Resolved',
            'description': 'Fishing pressure reduced, quota compliance restored in Barents Sea',
            'location': 'Barents Sea',
            'latitude': 74.0,
            'longitude': 40.0,
            'created_at': datetime.utcnow() - timedelta(days=15),
            'resolved_at': datetime.utcnow() - timedelta(days=7),
            'is_active': False
        }
    ]
    
    for alert_info in resolved_alerts:
        alert = Alert(**alert_info)
        db.session.add(alert)
    
    logger.info(f"Created {len(alert_data) + len(resolved_alerts)} environmental alerts")

if __name__ == '__main__':
    # This allows running the initialization script directly
    from app import app
    with app.app_context():
        initialize_sample_data()
