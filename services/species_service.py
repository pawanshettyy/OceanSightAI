from models import Species, SpeciesObservation, db
from datetime import datetime, timedelta
import logging
import random

class SpeciesService:
    """Service for handling species identification and management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_all_species_data(self):
        """Get all species data with recent observations"""
        try:
            species_list = Species.query.all()
            
            species_data = []
            for species in species_list:
                # Get recent observations (last 30 days)
                recent_date = datetime.utcnow() - timedelta(days=30)
                recent_observations = SpeciesObservation.query.filter(
                    SpeciesObservation.species_id == species.id,
                    SpeciesObservation.observation_date >= recent_date
                ).count()
                
                species_info = {
                    'id': species.id,
                    'scientific_name': species.scientific_name,
                    'common_name': species.common_name,
                    'species_type': species.species_type,
                    'conservation_status': species.conservation_status,
                    'habitat': species.habitat,
                    'population_trend': species.population_trend,
                    'threat_level': species.threat_level,
                    'recent_observations': recent_observations,
                    'description': species.description
                }
                species_data.append(species_info)
            
            return species_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving species data: {str(e)}")
            raise
    
    def mock_species_identification(self):
        """Mock species identification for demo purposes"""
        try:
            # Get a random species from database for mock identification
            species_count = Species.query.count()
            if species_count > 0:
                random_species = Species.query.offset(random.randint(0, species_count - 1)).first()
                
                if random_species:
                    # Mock confidence level
                    confidence = random.uniform(75, 95)
                    
                    result = {
                        'identified': True,
                        'species_id': random_species.id,
                        'scientific_name': random_species.scientific_name,
                        'common_name': random_species.common_name,
                        'confidence': round(confidence, 2),
                        'conservation_status': random_species.conservation_status,
                        'threat_level': random_species.threat_level,
                        'description': random_species.description,
                        'recommendations': self._get_conservation_recommendations(random_species)
                    }
                else:
                    return {
                        'identified': False,
                        'error': 'No species data available in database'
                    }
                
                return result
            else:
                return {
                    'identified': False,
                    'error': 'No species data available in database'
                }
                
        except Exception as e:
            self.logger.error(f"Error in species identification: {str(e)}")
            return {
                'identified': False,
                'error': 'Species identification service unavailable'
            }
    
    def _get_conservation_recommendations(self, species):
        """Get conservation recommendations based on species threat level"""
        recommendations = {
            'low': [
                'Continue monitoring population trends',
                'Maintain habitat protection measures',
                'Support sustainable fishing practices'
            ],
            'medium': [
                'Implement targeted conservation measures',
                'Increase monitoring frequency',
                'Establish marine protected areas in key habitats',
                'Reduce fishing pressure in breeding areas'
            ],
            'high': [
                'Urgent conservation action required',
                'Implement immediate fishing restrictions',
                'Establish breeding programs if applicable',
                'Create marine reserves in critical habitats',
                'International cooperation needed'
            ],
            'critical': [
                'Emergency conservation measures required',
                'Complete fishing moratorium needed',
                'Immediate habitat restoration',
                'Captive breeding programs',
                'International protection status required'
            ]
        }
        
        return recommendations.get(species.threat_level, recommendations['low'])
    
    def get_species_by_region(self, lat_min, lat_max, lng_min, lng_max):
        """Get species observations within a geographic region"""
        try:
            observations = SpeciesObservation.query.filter(
                SpeciesObservation.latitude >= lat_min,
                SpeciesObservation.latitude <= lat_max,
                SpeciesObservation.longitude >= lng_min,
                SpeciesObservation.longitude <= lng_max
            ).all()
            
            region_species = []
            for obs in observations:
                species = obs.species
                region_species.append({
                    'observation_id': obs.id,
                    'species_id': species.id,
                    'scientific_name': species.scientific_name,
                    'common_name': species.common_name,
                    'latitude': obs.latitude,
                    'longitude': obs.longitude,
                    'observation_count': obs.observation_count,
                    'confidence_level': obs.confidence_level,
                    'observation_date': obs.observation_date.isoformat(),
                    'conservation_status': species.conservation_status,
                    'threat_level': species.threat_level
                })
            
            return region_species
            
        except Exception as e:
            self.logger.error(f"Error retrieving species by region: {str(e)}")
            raise
    
    def get_threatened_species_summary(self):
        """Get summary of threatened species"""
        try:
            threatened_species = Species.query.filter(
                Species.threat_level.in_(['high', 'critical'])
            ).all()
            
            summary = {
                'total_threatened': len(threatened_species),
                'critical': len([s for s in threatened_species if s.threat_level == 'critical']),
                'high_risk': len([s for s in threatened_species if s.threat_level == 'high']),
                'species_list': []
            }
            
            for species in threatened_species:
                summary['species_list'].append({
                    'id': species.id,
                    'scientific_name': species.scientific_name,
                    'common_name': species.common_name,
                    'threat_level': species.threat_level,
                    'conservation_status': species.conservation_status,
                    'population_trend': species.population_trend
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting threatened species summary: {str(e)}")
            raise
    
    def find_or_create_species(self, species_data):
        """Find existing species or create new one based on scientific name"""
        try:
            # Try to find existing species by scientific name
            existing_species = Species.query.filter_by(
                scientific_name=species_data['scientific_name']
            ).first()
            
            if existing_species:
                # Update existing species with new data if provided
                existing_species.common_name = species_data.get('common_name', existing_species.common_name)
                existing_species.species_type = species_data.get('species_type', existing_species.species_type)
                existing_species.conservation_status = species_data.get('conservation_status', existing_species.conservation_status)
                existing_species.threat_level = species_data.get('threat_level', existing_species.threat_level)
                existing_species.habitat = species_data.get('habitat', existing_species.habitat)
                existing_species.description = species_data.get('description', existing_species.description)
                
                db.session.commit()
                return existing_species.id
            else:
                # Create new species
                new_species = Species()
                new_species.scientific_name = species_data['scientific_name']
                new_species.common_name = species_data.get('common_name', '')
                new_species.species_type = species_data.get('species_type', 'unknown')
                new_species.conservation_status = species_data.get('conservation_status', 'unknown')
                new_species.threat_level = species_data.get('threat_level', 'unknown')
                new_species.habitat = species_data.get('habitat', '')
                new_species.population_trend = 'unknown'
                new_species.description = species_data.get('description', '')
                
                db.session.add(new_species)
                db.session.commit()
                
                return new_species.id
                
        except Exception as e:
            self.logger.error(f"Error finding or creating species: {str(e)}")
            db.session.rollback()
            raise
