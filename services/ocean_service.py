from models import OceanData, db
from datetime import datetime, timedelta
import logging

class OceanService:
    """Service for handling oceanographic data operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_ocean_data_for_region(self, lat_min=None, lat_max=None, lng_min=None, lng_max=None):
        """Get ocean data for a specific geographic region"""
        try:
            query = OceanData.query
            
            # Apply geographic filters if provided
            if lat_min is not None:
                query = query.filter(OceanData.latitude >= lat_min)
            if lat_max is not None:
                query = query.filter(OceanData.latitude <= lat_max)
            if lng_min is not None:
                query = query.filter(OceanData.longitude >= lng_min)
            if lng_max is not None:
                query = query.filter(OceanData.longitude <= lng_max)
            
            # Get recent data (last 7 days)
            recent_date = datetime.utcnow() - timedelta(days=7)
            query = query.filter(OceanData.timestamp >= recent_date)
            
            ocean_data = query.all()
            
            # Format data for frontend visualization
            formatted_data = {
                'temperature_data': [],
                'salinity_data': [],
                'current_data': [],
                'ph_data': []
            }
            
            for data in ocean_data:
                point = {
                    'lat': data.latitude,
                    'lng': data.longitude,
                    'value': data.temperature,
                    'timestamp': data.timestamp.isoformat(),
                    'location': data.location_name
                }
                formatted_data['temperature_data'].append(point)
                
                if data.salinity:
                    point_salinity = point.copy()
                    point_salinity['value'] = data.salinity
                    formatted_data['salinity_data'].append(point_salinity)
                
                if data.current_speed and data.current_direction:
                    current_point = {
                        'lat': data.latitude,
                        'lng': data.longitude,
                        'speed': data.current_speed,
                        'direction': data.current_direction,
                        'timestamp': data.timestamp.isoformat()
                    }
                    formatted_data['current_data'].append(current_point)
                
                if data.ph_level:
                    point_ph = point.copy()
                    point_ph['value'] = data.ph_level
                    formatted_data['ph_data'].append(point_ph)
            
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving ocean data: {str(e)}")
            raise
    
    def get_temperature_anomalies(self, threshold_temp=25.0):
        """Identify temperature anomalies that might indicate climate change impacts"""
        try:
            # Get data from the last 30 days
            recent_date = datetime.utcnow() - timedelta(days=30)
            
            anomalies = OceanData.query.filter(
                OceanData.timestamp >= recent_date,
                OceanData.temperature > threshold_temp
            ).all()
            
            anomaly_data = []
            for anomaly in anomalies:
                anomaly_data.append({
                    'latitude': anomaly.latitude,
                    'longitude': anomaly.longitude,
                    'temperature': anomaly.temperature,
                    'location': anomaly.location_name,
                    'timestamp': anomaly.timestamp.isoformat(),
                    'severity': 'high' if anomaly.temperature > 28 else 'medium'
                })
            
            return anomaly_data
            
        except Exception as e:
            self.logger.error(f"Error identifying temperature anomalies: {str(e)}")
            raise
    
    def calculate_ocean_health_score(self, region_data):
        """Calculate a health score for ocean regions based on multiple parameters"""
        try:
            if not region_data:
                return 0
            
            # Scoring criteria (simplified for demo)
            temp_score = 0
            ph_score = 0
            oxygen_score = 0
            
            for data in region_data:
                # Temperature scoring (ideal range 20-25°C)
                if 20 <= data.temperature <= 25:
                    temp_score += 100
                elif 18 <= data.temperature < 20 or 25 < data.temperature <= 27:
                    temp_score += 75
                elif 15 <= data.temperature < 18 or 27 < data.temperature <= 30:
                    temp_score += 50
                else:
                    temp_score += 25
                
                # pH scoring (ideal range 8.0-8.3)
                if data.ph_level:
                    if 8.0 <= data.ph_level <= 8.3:
                        ph_score += 100
                    elif 7.8 <= data.ph_level < 8.0 or 8.3 < data.ph_level <= 8.5:
                        ph_score += 75
                    else:
                        ph_score += 50
                
                # Oxygen scoring (higher is better, threshold at 5 mg/L)
                if data.oxygen_level:
                    if data.oxygen_level >= 6:
                        oxygen_score += 100
                    elif data.oxygen_level >= 5:
                        oxygen_score += 75
                    elif data.oxygen_level >= 3:
                        oxygen_score += 50
                    else:
                        oxygen_score += 25
            
            # Calculate weighted average
            total_points = len(region_data)
            if total_points > 0:
                avg_temp_score = temp_score / total_points
                avg_ph_score = ph_score / total_points if ph_score > 0 else avg_temp_score
                avg_oxygen_score = oxygen_score / total_points if oxygen_score > 0 else avg_temp_score
                
                # Weighted average (temperature 40%, pH 30%, oxygen 30%)
                health_score = (avg_temp_score * 0.4 + avg_ph_score * 0.3 + avg_oxygen_score * 0.3)
                return round(health_score, 2)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error calculating ocean health score: {str(e)}")
            return 0
