# services/biodiversity_service.py
from app import db, BiodiversityIndex, Species, SpeciesObservation
from datetime import datetime, timedelta
from sqlalchemy import func

class BiodiversityService:
    def get_biodiversity_indices(self):
        """Get all biodiversity index data"""
        indices = BiodiversityIndex.query\
                                  .order_by(BiodiversityIndex.assessment_date.desc())\
                                  .all()
        
        return [{
            'id': index.id,
            'region_name': index.region_name,
            'latitude': index.latitude,
            'longitude': index.longitude,
            'species_count': index.species_count,
            'endemic_species': index.endemic_species,
            'threatened_species': index.threatened_species,
            'biodiversity_score': index.biodiversity_score,
            'ecosystem_health': index.ecosystem_health,
            'assessment_date': index.assessment_date.isoformat() if index.assessment_date else None,
            'notes': index.notes
        } for index in indices]
    
    def calculate_sustainability_metrics(self):
        """Calculate overall sustainability metrics for dashboard"""
        # Total species count
        total_species = Species.query.count()
        
        # Threatened species count
        threatened_species = Species.query.filter(
            Species.threat_level.in_(['high', 'critical'])
        ).count()
        
        # Recent observations count (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_observations = SpeciesObservation.query.filter(
            SpeciesObservation.observation_date >= recent_date
        ).count()
        
        # Average biodiversity score
        avg_biodiversity = db.session.query(func.avg(BiodiversityIndex.biodiversity_score))\
                                    .filter(BiodiversityIndex.biodiversity_score.isnot(None))\
                                    .scalar() or 0
        
        # Ecosystem health distribution
        health_counts = db.session.query(
            BiodiversityIndex.ecosystem_health,
            func.count(BiodiversityIndex.id).label('count')
        ).group_by(BiodiversityIndex.ecosystem_health).all()
        
        health_distribution = {health: count for health, count in health_counts}
        
        # Conservation status distribution
        status_counts = db.session.query(
            Species.conservation_status,
            func.count(Species.id).label('count')
        ).group_by(Species.conservation_status).all()
        
        conservation_distribution = {status: count for status, count in status_counts}
        
        return {
            'total_species': total_species,
            'threatened_species': threatened_species,
            'recent_observations': recent_observations,
            'avg_biodiversity_score': round(avg_biodiversity, 1),
            'threat_percentage': round((threatened_species / total_species * 100) if total_species > 0 else 0, 1),
            'ecosystem_health_distribution': health_distribution,
            'conservation_status_distribution': conservation_distribution
        }
    
    def get_regional_trends(self):
        """Get biodiversity trends by region"""
        # Get the most recent assessment for each region
        latest_assessments = db.session.query(
            BiodiversityIndex.region_name,
            func.max(BiodiversityIndex.assessment_date).label('latest_date')
        ).group_by(BiodiversityIndex.region_name).subquery()
        
        current_data = db.session.query(BiodiversityIndex)\
                                .join(latest_assessments,
                                     (BiodiversityIndex.region_name == latest_assessments.c.region_name) &
                                     (BiodiversityIndex.assessment_date == latest_assessments.c.latest_date))\
                                .all()
        
        return [{
            'region': assessment.region_name,
            'biodiversity_score': assessment.biodiversity_score,
            'species_count': assessment.species_count,
            'ecosystem_health': assessment.ecosystem_health,
            'threatened_species': assessment.threatened_species,
            'assessment_date': assessment.assessment_date.isoformat() if assessment.assessment_date else None
        } for assessment in current_data]
    
    def get_species_threat_analysis(self):
        """Get threat level analysis for species"""
        threat_counts = db.session.query(
            Species.threat_level,
            func.count(Species.id).label('count')
        ).group_by(Species.threat_level).all()
        
        threat_data = []
        for threat_level, count in threat_counts:
            threat_data.append({
                'threat_level': threat_level or 'unknown',
                'count': count
            })
        
        return threat_data