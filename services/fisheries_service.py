from models import FisheriesData, Species, Alert, db
from datetime import datetime, timedelta
import logging
from sqlalchemy import func

class FisheriesService:
    """Service for handling fisheries data and sustainability analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_catch_data(self, start_date=None, end_date=None):
        """Get fisheries catch data for specified date range"""
        try:
            query = FisheriesData.query.join(Species)
            
            # Apply date filters
            if start_date:
                start_date_obj = datetime.fromisoformat(start_date)
                query = query.filter(FisheriesData.catch_date >= start_date_obj)
            
            if end_date:
                end_date_obj = datetime.fromisoformat(end_date)
                query = query.filter(FisheriesData.catch_date <= end_date_obj)
            else:
                # Default to last 30 days if no end date specified
                if not start_date:
                    recent_date = datetime.utcnow() - timedelta(days=30)
                    query = query.filter(FisheriesData.catch_date >= recent_date)
            
            catch_data = query.all()
            
            # Format data for visualization
            formatted_data = {
                'catch_trends': [],
                'species_breakdown': {},
                'sustainability_scores': [],
                'geographic_distribution': []
            }
            
            for catch in catch_data:
                # Catch trends data
                trend_point = {
                    'date': catch.catch_date.isoformat(),
                    'amount': catch.catch_amount,
                    'species': catch.species.common_name,
                    'scientific_name': catch.species.scientific_name,
                    'fishing_area': catch.fishing_area,
                    'sustainability_score': catch.sustainability_score
                }
                formatted_data['catch_trends'].append(trend_point)
                
                # Species breakdown
                species_name = catch.species.common_name
                if species_name not in formatted_data['species_breakdown']:
                    formatted_data['species_breakdown'][species_name] = {
                        'total_catch': 0,
                        'catch_events': 0,
                        'avg_sustainability': 0,
                        'conservation_status': catch.species.conservation_status
                    }
                
                formatted_data['species_breakdown'][species_name]['total_catch'] += catch.catch_amount
                formatted_data['species_breakdown'][species_name]['catch_events'] += 1
                
                # Geographic distribution
                if catch.latitude and catch.longitude:
                    geo_point = {
                        'lat': catch.latitude,
                        'lng': catch.longitude,
                        'catch_amount': catch.catch_amount,
                        'species': catch.species.common_name,
                        'fishing_area': catch.fishing_area,
                        'date': catch.catch_date.isoformat()
                    }
                    formatted_data['geographic_distribution'].append(geo_point)
                
                # Sustainability scores
                if catch.sustainability_score:
                    sustainability_point = {
                        'date': catch.catch_date.isoformat(),
                        'score': catch.sustainability_score,
                        'species': catch.species.common_name,
                        'fishing_area': catch.fishing_area
                    }
                    formatted_data['sustainability_scores'].append(sustainability_point)
            
            # Calculate average sustainability scores for species breakdown
            for species_name, data in formatted_data['species_breakdown'].items():
                if data['catch_events'] > 0:
                    sustainability_sum = sum([
                        catch.sustainability_score for catch in catch_data 
                        if catch.species.common_name == species_name and catch.sustainability_score
                    ])
                    data['avg_sustainability'] = round(sustainability_sum / data['catch_events'], 2)
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving catch data: {str(e)}")
            raise
    
    def check_overfishing_alerts(self):
        """Check for overfishing conditions and create alerts"""
        try:
            # Get catch data for the last 30 days
            recent_date = datetime.utcnow() - timedelta(days=30)
            
            # Aggregate catch data by species and area
            catch_summary = db.session.query(
                Species.id,
                Species.common_name,
                Species.scientific_name,
                FisheriesData.fishing_area,
                func.sum(FisheriesData.catch_amount).label('total_catch'),
                func.avg(FisheriesData.quota_limit).label('avg_quota'),
                func.avg(FisheriesData.sustainability_score).label('avg_sustainability')
            ).join(FisheriesData).filter(
                FisheriesData.catch_date >= recent_date
            ).group_by(
                Species.id, FisheriesData.fishing_area
            ).all()
            
            alerts_created = []
            
            for summary in catch_summary:
                # Check for quota violations
                if summary.avg_quota and summary.total_catch > summary.avg_quota * 1.2:  # 20% over quota
                    alert_data = {
                        'alert_type': 'overfishing',
                        'severity': 'high' if summary.total_catch > summary.avg_quota * 1.5 else 'medium',
                        'title': f'Overfishing Alert: {summary.common_name}',
                        'description': f'Catch amount ({summary.total_catch:.1f} tons) exceeds quota limit in {summary.fishing_area}',
                        'location': summary.fishing_area
                    }
                    
                    # Create alert if it doesn't exist
                    existing_alert = Alert.query.filter(
                        Alert.alert_type == 'overfishing',
                        Alert.location == summary.fishing_area,
                        Alert.title.contains(summary.common_name),
                        Alert.is_active == True
                    ).first()
                    
                    if not existing_alert:
                        new_alert = Alert(**alert_data)
                        db.session.add(new_alert)
                        alerts_created.append(alert_data)
                
                # Check for low sustainability scores
                if summary.avg_sustainability and summary.avg_sustainability < 40:
                    alert_data = {
                        'alert_type': 'sustainability_risk',
                        'severity': 'critical' if summary.avg_sustainability < 25 else 'high',
                        'title': f'Sustainability Risk: {summary.common_name}',
                        'description': f'Low sustainability score ({summary.avg_sustainability:.1f}) in {summary.fishing_area}',
                        'location': summary.fishing_area
                    }
                    
                    existing_alert = Alert.query.filter(
                        Alert.alert_type == 'sustainability_risk',
                        Alert.location == summary.fishing_area,
                        Alert.title.contains(summary.common_name),
                        Alert.is_active == True
                    ).first()
                    
                    if not existing_alert:
                        new_alert = Alert(**alert_data)
                        db.session.add(new_alert)
                        alerts_created.append(alert_data)
            
            db.session.commit()
            return alerts_created
            
        except Exception as e:
            self.logger.error(f"Error checking overfishing alerts: {str(e)}")
            db.session.rollback()
            raise
    
    def get_fishing_pressure_analysis(self):
        """Analyze fishing pressure across different regions and species"""
        try:
            # Get data for the last 90 days
            recent_date = datetime.utcnow() - timedelta(days=90)
            
            pressure_analysis = db.session.query(
                FisheriesData.fishing_area,
                func.count(FisheriesData.id).label('fishing_events'),
                func.sum(FisheriesData.catch_amount).label('total_catch'),
                func.avg(FisheriesData.sustainability_score).label('avg_sustainability'),
                func.count(func.distinct(FisheriesData.species_id)).label('species_diversity')
            ).filter(
                FisheriesData.catch_date >= recent_date
            ).group_by(
                FisheriesData.fishing_area
            ).all()
            
            analysis_results = []
            for analysis in pressure_analysis:
                # Calculate pressure score (higher values indicate more pressure)
                pressure_score = 0
                
                # Factor in fishing frequency (more events = higher pressure)
                if analysis.fishing_events > 50:
                    pressure_score += 30
                elif analysis.fishing_events > 25:
                    pressure_score += 20
                elif analysis.fishing_events > 10:
                    pressure_score += 10
                
                # Factor in total catch volume
                if analysis.total_catch > 1000:
                    pressure_score += 40
                elif analysis.total_catch > 500:
                    pressure_score += 25
                elif analysis.total_catch > 100:
                    pressure_score += 15
                
                # Factor in sustainability (lower sustainability = higher pressure)
                if analysis.avg_sustainability:
                    if analysis.avg_sustainability < 30:
                        pressure_score += 30
                    elif analysis.avg_sustainability < 50:
                        pressure_score += 20
                    elif analysis.avg_sustainability < 70:
                        pressure_score += 10
                
                # Determine pressure level
                if pressure_score >= 80:
                    pressure_level = 'critical'
                elif pressure_score >= 60:
                    pressure_level = 'high'
                elif pressure_score >= 40:
                    pressure_level = 'medium'
                else:
                    pressure_level = 'low'
                
                result = {
                    'fishing_area': analysis.fishing_area,
                    'fishing_events': analysis.fishing_events,
                    'total_catch': float(analysis.total_catch) if analysis.total_catch else 0,
                    'avg_sustainability': float(analysis.avg_sustainability) if analysis.avg_sustainability else 0,
                    'species_diversity': analysis.species_diversity,
                    'pressure_score': pressure_score,
                    'pressure_level': pressure_level
                }
                analysis_results.append(result)
            
            return sorted(analysis_results, key=lambda x: x['pressure_score'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error analyzing fishing pressure: {str(e)}")
            raise
