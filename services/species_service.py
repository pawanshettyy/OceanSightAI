# services/species_service.py
from app import db, Species, SpeciesObservation
from datetime import datetime
import random

class SpeciesService:
    def get_all_species_data(self):
        """Get all species data for visualization"""
        species_list = Species.query.all()
        
        species_data = []
        for species in species_list:
            # Get recent observations for this species
            recent_observations = SpeciesObservation.query.filter_by(
                species_id=species.id
            ).order_by(SpeciesObservation.observation_date.desc()).limit(10).all()
            
            observations_data = [{
                'latitude': obs.latitude,
                'longitude': obs.longitude,
                'count': obs.observation_count,
                'date': obs.observation_date.isoformat(),
                'confidence': obs.confidence_level
            } for obs in recent_observations]
            
            species_data.append({
                'id': species.id,
                'scientific_name': species.scientific_name,
                'common_name': species.common_name,
                'species_type': species.species_type,
                'conservation_status': species.conservation_status,
                'threat_level': species.threat_level,
                'habitat': species.habitat,
                'description': species.description,
                'observations': observations_data
            })
        
        return species_data
    
    def mock_species_identification(self):
        """Mock species identification when OpenAI API is not available"""
        mock_species = [
            {
                'scientific_name': 'Chelonia mydas',
                'common_name': 'Green Sea Turtle',
                'species_type': 'reptile',
                'conservation_status': 'endangered',
                'threat_level': 'high',
                'confidence': 85,
                'habitat': 'Coastal waters and seagrass beds',
                'description': 'Large sea turtle with heart-shaped shell'
            },
            {
                'scientific_name': 'Carcharodon carcharias',
                'common_name': 'Great White Shark',
                'species_type': 'fish',
                'conservation_status': 'vulnerable',
                'threat_level': 'medium',
                'confidence': 78,
                'habitat': 'Coastal surface waters',
                'description': 'Large predatory shark with distinctive white underside'
            },
            {
                'scientific_name': 'Thunnus thynnus',
                'common_name': 'Atlantic Bluefin Tuna',
                'species_type': 'fish',
                'conservation_status': 'critically endangered',
                'threat_level': 'critical',
                'confidence': 92,
                'habitat': 'Open ocean waters',
                'description': 'Large, fast-swimming tuna highly valued commercially'
            }
        ]
        
        # Return a random mock identification
        identified_species = random.choice(mock_species)
        identified_species['identified'] = True
        return identified_species
    
    def find_or_create_species(self, species_data):
        """Find existing species or create new one"""
        existing_species = Species.query.filter_by(
            scientific_name=species_data['scientific_name']
        ).first()
        
        if existing_species:
            return existing_species.id
        
        # Create new species
        new_species = Species(
            scientific_name=species_data['scientific_name'],
            common_name=species_data.get('common_name', ''),
            species_type=species_data.get('species_type', 'unknown'),
            conservation_status=species_data.get('conservation_status', 'unknown'),
            threat_level=species_data.get('threat_level', 'unknown'),
            habitat=species_data.get('habitat', ''),
            description=species_data.get('description', '')
        )
        
        db.session.add(new_species)
        db.session.commit()
        return new_species.id