from models import BiodiversityIndex, Species, SpeciesObservation, Alert, db
from datetime import datetime, timedelta
import logging
from sqlalchemy import func

class BiodiversityService:
    """Service for biodiversity monitoring and health assessment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_biodiversity_indices(self):
        """Get all biodiversity index data"""
        try:
            indices = BiodiversityIndex.query.order_by(BiodiversityIndex.assessment_date.desc()).all()
            
            indices_data = []
            for index in indices:
                index_data = {
                    'id': index.id,
                    'region_name': index.region_name,
                    'latitude': index.latitude,
                    'longitude': index.longitude,
                    'species_count': index.species_count,
                    'endemic_species': index.endemic_species,
                    'threatened_species': index.threatened_species,
                    'biodiversity_score': index.biodiversity_score,
                    'ecosystem_health': index.ecosystem_health,
                    'assessment_date': index.assessment_date.isoformat(),
                    'notes': index.notes
                }
                indices_data.append(index_data)
            
            return indices_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving biodiversity indices: {str(e)}")
            raise
    
    def calculate_sustainability_metrics(self):
        """Calculate overall sustainability metrics for the platform dashboard"""
        try:
            # Get recent data (last 30 days)
            recent_date = datetime.utcnow() - timedelta(days=30)
            
            # Species diversity metrics
            total_species = Species.query.count()
            threatened_species = Species.query.filter(
                Species.threat_level.in_(['high', 'critical'])
            ).count()
            
            # Recent observations
            recent_observations = SpeciesObservation.query.filter(
                SpeciesObservation.observation_date >= recent_date
            ).count()
            
            # Biodiversity health average
            avg_biodiversity = db.session.query(
                func.avg(BiodiversityIndex.biodiversity_score)
            ).scalar()
            
            # Active alerts by severity
            alert_counts = db.session.query(
                Alert.severity,
                func.count(Alert.id)
            ).filter(
                Alert.is_active == True
            ).group_by(Alert.severity).all()
            
            alert_summary = {severity: count for severity, count in alert_counts}
            
            # Calculate overall sustainability score
            sustainability_score = self._calculate_overall_sustainability_score(
                total_species, threatened_species, avg_biodiversity, alert_summary
            )
            
            metrics = {
                'total_species': total_species,
                'threatened_species': threatened_species,
                'threat_percentage': round((threatened_species / total_species * 100) if total_species > 0 else 0, 1),
                'recent_observations': recent_observations,
                'avg_biodiversity_score': round(avg_biodiversity, 2) if avg_biodiversity else 0,
                'active_alerts': alert_summary,
                'total_active_alerts': sum(alert_summary.values()),
                'sustainability_score': sustainability_score,
                'sustainability_trend': self._calculate_sustainability_trend(),
                'ecosystem_health_distribution': self._get_ecosystem_health_distribution()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating sustainability metrics: {str(e)}")
            raise
    
    def _calculate_overall_sustainability_score(self, total_species, threatened_species, avg_biodiversity, alerts):
        """Calculate an overall sustainability score (0-100)"""
        try:
            score = 100
            
            # Deduct points for threatened species
            if total_species > 0:
                threat_percentage = (threatened_species / total_species) * 100
                score -= min(threat_percentage * 0.8, 40)  # Max 40 points deduction
            
            # Factor in biodiversity score
            if avg_biodiversity:
                biodiversity_factor = (100 - avg_biodiversity) * 0.3
                score -= min(biodiversity_factor, 30)  # Max 30 points deduction
            
            # Deduct points for alerts
            critical_alerts = alerts.get('critical', 0)
            high_alerts = alerts.get('high', 0)
            medium_alerts = alerts.get('medium', 0)
            
            alert_penalty = (critical_alerts * 5) + (high_alerts * 3) + (medium_alerts * 1)
            score -= min(alert_penalty, 30)  # Max 30 points deduction
            
            return max(0, round(score, 2))
            
        except Exception as e:
            self.logger.error(f"Error calculating sustainability score: {str(e)}")
            return 50  # Default middle score
    
    def _calculate_sustainability_trend(self):
        """Calculate sustainability trend over time"""
        try:
            # Compare current month with previous month
            current_date = datetime.utcnow()
            current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            
            # Count threatened species observations for trend analysis
            current_threatened = SpeciesObservation.query.join(Species).filter(
                SpeciesObservation.observation_date >= current_month_start,
                Species.threat_level.in_(['high', 'critical'])
            ).count()
            
            previous_threatened = SpeciesObservation.query.join(Species).filter(
                SpeciesObservation.observation_date >= previous_month_start,
                SpeciesObservation.observation_date < current_month_start,
                Species.threat_level.in_(['high', 'critical'])
            ).count()
            
            if previous_threatened > 0:
                trend_percentage = ((current_threatened - previous_threatened) / previous_threatened) * 100
                
                if trend_percentage > 10:
                    return {'status': 'declining', 'percentage': round(abs(trend_percentage), 1)}
                elif trend_percentage < -10:
                    return {'status': 'improving', 'percentage': round(abs(trend_percentage), 1)}
                else:
                    return {'status': 'stable', 'percentage': round(abs(trend_percentage), 1)}
            else:
                return {'status': 'stable', 'percentage': 0}
                
        except Exception as e:
            self.logger.error(f"Error calculating sustainability trend: {str(e)}")
            return {'status': 'unknown', 'percentage': 0}
    
    def _get_ecosystem_health_distribution(self):
        """Get distribution of ecosystem health across regions"""
        try:
            health_distribution = db.session.query(
                BiodiversityIndex.ecosystem_health,
                func.count(BiodiversityIndex.id)
            ).group_by(BiodiversityIndex.ecosystem_health).all()
            
            distribution = {}
            for health, count in health_distribution:
                distribution[health] = count
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Error getting ecosystem health distribution: {str(e)}")
            return {}
    
    def check_biodiversity_alerts(self):
        """Check for biodiversity risks and create alerts"""
        try:
            alerts_created = []
            
            # Check for regions with low biodiversity scores
            low_biodiversity_regions = BiodiversityIndex.query.filter(
                BiodiversityIndex.biodiversity_score < 40
            ).all()
            
            for region in low_biodiversity_regions:
                alert_data = {
                    'alert_type': 'biodiversity_risk',
                    'severity': 'critical' if region.biodiversity_score < 25 else 'high',
                    'title': f'Biodiversity Risk: {region.region_name}',
                    'description': f'Low biodiversity score ({region.biodiversity_score}) detected in {region.region_name}',
                    'location': region.region_name,
                    'latitude': region.latitude,
                    'longitude': region.longitude
                }
                
                # Check if alert already exists
                existing_alert = Alert.query.filter(
                    Alert.alert_type == 'biodiversity_risk',
                    Alert.location == region.region_name,
                    Alert.is_active == True
                ).first()
                
                if not existing_alert:
                    new_alert = Alert(**alert_data)
                    db.session.add(new_alert)
                    alerts_created.append(alert_data)
            
            # Check for high numbers of threatened species in regions
            regions_with_threats = BiodiversityIndex.query.filter(
                BiodiversityIndex.threatened_species > 5
            ).all()
            
            for region in regions_with_threats:
                threat_ratio = region.threatened_species / max(region.species_count, 1)
                
                if threat_ratio > 0.3:  # More than 30% of species are threatened
                    alert_data = {
                        'alert_type': 'species_threat',
                        'severity': 'critical' if threat_ratio > 0.5 else 'high',
                        'title': f'Species Threat Alert: {region.region_name}',
                        'description': f'{region.threatened_species} threatened species ({threat_ratio*100:.1f}%) in {region.region_name}',
                        'location': region.region_name,
                        'latitude': region.latitude,
                        'longitude': region.longitude
                    }
                    
                    existing_alert = Alert.query.filter(
                        Alert.alert_type == 'species_threat',
                        Alert.location == region.region_name,
                        Alert.is_active == True
                    ).first()
                    
                    if not existing_alert:
                        new_alert = Alert(**alert_data)
                        db.session.add(new_alert)
                        alerts_created.append(alert_data)
            
            db.session.commit()
            return alerts_created
            
        except Exception as e:
            self.logger.error(f"Error checking biodiversity alerts: {str(e)}")
            db.session.rollback()
            raise
